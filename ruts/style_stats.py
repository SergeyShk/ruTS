from collections import Counter
from collections.abc import Collection, Iterable, Sequence
from functools import lru_cache
from math import isnan, nan, sqrt

import anyts
from anyts.readability_stats import scale_level
from anyts.utils import check_integer, check_words, iter_doc_words, safe_divide
from spacy.tokens import Doc

from .constants import (
    COMPOUND_PREPOSITIONS,
    NAUSEA_TOP_N,
    OFFICIALESE_CLICHES,
    PARENTHETICALS,
    STOPWORD_GRAMMEMES,
    STOPWORD_POS,
    STYLE_NORMS,
    STYLE_STATS_DESC,
)
from .exceptions import ParameterError, SourceError, SourceTypeError, UnknownStatError
from .extractors import WordsExtractor
from .utils import find_phrases, get_morph_analyzer, is_verbal_noun, normalize_yo, parse_word


def check_params(top_n: int) -> None:
    """
    Проверка параметров SEO-метрик

    Аргументы:
        top_n (int): Количество самых частых слов

    Исключения:
        ParameterError: Если количество самых частых слов меньше единицы
    """
    check_integer(top_n, "number of the most frequent words")
    if top_n < 1:
        raise ParameterError("Количество самых частых слов должно быть больше 0")


class StyleStats:
    """
    Класс для вычисления SEO-метрик стиля и качества текста

    Описание:
        SEO-метрики повторяют показатели сервисов Advego и Text.ru: тошнота, водность,
        заспамленность, естественность распределения слов по закону Ципфа и плотность
        ключевых слов. Точные формулы сервисов не опубликованы, поэтому реализованы
        общепринятые определения, они описаны в докстрингах функций; прочтение метрик
        по нормам сервисов (describe) - по полосам STYLE_NORMS
        Лексические маркеры канцелярита: отглагольные существительные, производные
        предлоги, вводные слова, штампы - по спискам из constants
        Слова по умолчанию извлекаются в нижнем регистре без лемматизации; для расчета
        SEO-метрик по леммам передайте WordsExtractor(use_lexemes=True, lowercase=True)
        Из Doc слова берутся без знаков препинания, дефисные слова (во-первых), которые
        spaCy режет на части, склеиваются (iter_doc_words)
        Маркеры канцелярита считаются по словоформам без фильтрации (forms)
        независимо от переданного экстрактора

    Пример использования:
        >>> from ruts import StyleStats
        >>> text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
        >>> ss = StyleStats(text)
        >>> ss.get_stats()
        {'classic_nausea': 1.7320508075688772,
        'academic_nausea': 93.33333333333333,
        'water': 46.666666666666664,
        'spam': 26.666666666666668,
        'zipf_naturalness': 33.333333333333336,
        'verbal_nouns': 0.0,
        'compound_prepositions': 0.0,
        'parentheticals': 0.0,
        'cliches': 0.0}
        >>> ss.keyword_density("когда", "нет а")
        {'когда': 20.0, 'нет а': 13.333333333333334}
        >>> StyleStats("В целях повышения качества в кратчайшие сроки, как правило, проводится проверка").get_stats()
        {'classic_nausea': 1.4142135623730951,
        'academic_nausea': 100.0,
        'water': 27.272727272727273,
        'spam': 9.090909090909092,
        'zipf_naturalness': 100.0,
        'verbal_nouns': 16.666666666666664,
        'compound_prepositions': 9.090909090909092,
        'parentheticals': 9.090909090909092,
        'cliches': 9.090909090909092}

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        words_extractor (WordsExtractor): Инструмент для извлечения слов;
            если задан, применяется и к тексту Doc
        stopwords (list[str]): Список стоп-слов для водности; если не задан, стоп-слова
            определяются по части речи с помощью pymorphy3
        top_n (int): Количество самых частых слов для академической тошноты и естественности по Ципфу
        cliches (list[str]): Список штампов; если не задан, используется OFFICIALESE_CLICHES

    Атрибуты:
        words (tuple[str]): Кортеж извлеченных слов
        forms (tuple[str]): Кортеж словоформ в нижнем регистре без фильтрации
        classic_nausea (float): Классическая тошнота
        academic_nausea (float): Академическая тошнота в процентах
        water (float): Водность в процентах
        spam (float): Заспамленность в процентах
        zipf_naturalness (float): Естественность по Ципфу в процентах
        verbal_nouns (float): Доля отглагольных существительных среди существительных в процентах
        compound_prepositions (float): Производных предлогов на 100 слов
        parentheticals (float): Вводных слов на 100 слов
        cliches (float): Штампов на 100 слов

    Методы:
        keyword_density: Плотность ключевых слов и фраз
        describe: Прочтение метрики стиля по нормам SEO-сервисов
        get_stats: Получение вычисленных метрик стиля текста
        print_stats: Отображение вычисленных метрик стиля текста с описанием на экран

    Исключения:
        SourceTypeError: Если передаваемое значение не является строкой или объектом Doc
        SourceError: Если в источнике данных отсутствуют слова
        ParameterError: Если количество самых частых слов не положительно
    """

    def __init__(
        self,
        source: str | Doc,
        words_extractor: WordsExtractor | None = None,
        stopwords: Collection[str] | None = None,
        top_n: int = NAUSEA_TOP_N,
        cliches: Collection[str] | None = None,
    ):
        if words_extractor is not None and not isinstance(words_extractor, anyts.WordsExtractor):
            raise SourceTypeError("Экстрактор слов должен быть WordsExtractor")
        check_params(top_n)
        if stopwords is not None:
            check_words(stopwords, "stopwords", ordered=False)
        if cliches is not None:
            check_words(cliches, "clichés", ordered=False)
        if isinstance(source, Doc) and words_extractor is not None:
            # Экстрактор слов применяется к тексту Doc, как в классах ядра
            source = source.text
        if isinstance(source, Doc):
            self.words = tuple(
                text.lower() for _, _, text in iter_doc_words(source, join_hyphens=True)
            )
            self.forms = self.words
        elif isinstance(source, str):
            if not words_extractor:
                words_extractor = WordsExtractor(lowercase=True)
                self.words = words_extractor.extract(source)
                self.forms = self.words
            else:
                self.words = words_extractor.extract(source)
                self.forms = WordsExtractor(lowercase=True).extract(source)
        else:
            raise SourceTypeError("Некорректный источник данных")
        if not self.words:
            raise SourceError("В источнике данных отсутствуют слова")
        self.stopwords = tuple(stopwords) if stopwords is not None else None
        self.top_n = top_n
        self.cliches_list = tuple(cliches) if cliches is not None else OFFICIALESE_CLICHES

    @property
    def classic_nausea(self) -> float:
        return calc_classic_nausea(self.words)

    @property
    def academic_nausea(self) -> float:
        return calc_academic_nausea(self.words, self.top_n)

    @property
    def water(self) -> float:
        return calc_water(self.words, self.stopwords)

    @property
    def spam(self) -> float:
        return calc_spam(self.words)

    @property
    def zipf_naturalness(self) -> float:
        return calc_zipf_naturalness(self.words, self.top_n)

    @property
    def verbal_nouns(self) -> float:
        return calc_verbal_nouns(self.forms)

    @property
    def compound_prepositions(self) -> float:
        return calc_phrase_density(self.forms, COMPOUND_PREPOSITIONS)

    @property
    def parentheticals(self) -> float:
        return calc_parentheticals(self.forms)

    @property
    def cliches(self) -> float:
        return calc_phrase_density(self.forms, self.cliches_list)

    def keyword_density(self, *keywords: str) -> dict[str, float]:
        """
        Вычисление плотности ключевых слов и фраз

        Аргументы:
            keywords (tuple[str]): Ключевые слова или фразы из нескольких слов через пробел

        Вывод:
            dict[str, float]: Плотность каждого ключевого слова в процентах
        """
        return calc_keyword_density(self.words, keywords)

    def describe(self, stat: str) -> str | None:
        """
        Прочтение метрики стиля по нормам SEO-сервисов

        Описание:
            Полоса нормы метрики из STYLE_NORMS: тошнота - по Advego, водность
            и заспамленность - по Text.ru, естественность по Ципфу - по pr-cy и megaindex
            Метрика без нормы (маркеры канцелярита) и неопределенное значение (nan)
            дают None
            Нормы - ориентиры сервисов для текстов сайтов в несколько сотен слов,
            к коротким текстам и художественной прозе они неприменимы

        Аргументы:
            stat (str): Название метрики

        Вывод:
            str | None: Полоса нормы; None для метрики без нормы или неопределенного значения

        Исключения:
            UnknownStatError: Если метрики нет в справочнике метрик стиля

        Пример использования:
            >>> from ruts import StyleStats
            >>> ss = StyleStats("Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать")
            >>> ss.describe("water"), ss.describe("spam")
            ('высокая водность по Text.ru', 'естественный текст по Text.ru')
            >>> ss.describe("cliches") is None
            True
        """
        if not isinstance(stat, str) or stat not in STYLE_STATS_DESC:
            raise UnknownStatError(
                f"{stat} отсутствует в справочнике метрик стиля, "
                f"доступны: {', '.join(STYLE_STATS_DESC)}"
            )
        if stat not in STYLE_NORMS:
            return None
        value = getattr(self, stat)
        return None if isnan(value) else scale_level(value, STYLE_NORMS[stat])

    def get_stats(self) -> dict[str, float]:
        """
        Получение вычисленных метрик стиля текста

        Вывод:
            dict[str, float]: Справочник вычисленных метрик стиля текста
        """
        return {stat: getattr(self, stat) for stat in STYLE_STATS_DESC}

    def print_stats(self):
        """Отображение вычисленных метрик стиля текста с описанием на экран"""
        print(f"{'Метрика':^50}|{'Значение':^10}")
        print("-" * 60)
        stats = self.get_stats()
        for stat, value in STYLE_STATS_DESC.items():
            print(f"{value:50}|{stats[stat]:^10.2f}")


@lru_cache(maxsize=65536)
def is_stopword(word: str) -> bool:
    """
    Проверка, является ли слово стоп-словом по части речи

    Описание:
        Стоп-словами считаются союзы, частицы, предлоги, местоимения-существительные,
        междометия, предикативы (нет, надо, можно), местоименные прилагательные
        (этот, такой, который, весь), вводные слова (конечно, например), указательные
        (там, тогда) и вопросительные (где, почему) наречия по разметке pymorphy3
        Разбор словоформы кэшируется в parse_word, результат проверки - здесь

    Аргументы:
        word (str): Слово

    Вывод:
        bool: Результат проверки
    """
    if not isinstance(word, str):
        raise SourceTypeError(f"Слово должно быть строкой, а не {type(word).__name__}")
    tag = parse_word(word).tag
    return tag.POS in STOPWORD_POS or bool(STOPWORD_GRAMMEMES & tag.grammemes)


def calc_classic_nausea(text: Sequence[str]) -> float:
    """
    Вычисление классической тошноты

    Описание:
        Квадратный корень из количества вхождений самого частого слова (Advego)
        Характеризует навязчивость одного слова без учета длины текста, поэтому
        растет вместе с текстом
        Норма Advego - не больше 7, на практике 1-5; полосы - STYLE_NORMS

    Ссылки:
        https://advego.com/text/seo/

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение тошноты
    """
    check_words(text)
    if not text:
        return 0.0
    return sqrt(max(Counter(text).values()))


def calc_academic_nausea(text: Sequence[str], top_n: int = NAUSEA_TOP_N) -> float:
    """
    Вычисление академической тошноты

    Описание:
        Доля вхождений самых частых слов в тексте в процентах (Advego)
        Точная формула Advego не опубликована, реализовано как суммарная частота
        top_n самых частых слов, деленная на количество слов
        Норма Advego - 5-15%; полосы - STYLE_NORMS

    Ссылки:
        https://advego.com/text/seo/

    Аргументы:
        text (list[str]): Список слов
        top_n (int): Количество самых частых слов

    Вывод:
        float: Значение тошноты в процентах
    """
    check_words(text)
    check_params(top_n)
    top_freqs = sum(freq for _, freq in Counter(text).most_common(top_n))
    return safe_divide(100 * top_freqs, len(text))


def calc_water(text: Sequence[str], stopwords: Collection[str] | None = None) -> float:
    """
    Вычисление водности

    Описание:
        Доля незначимых слов в тексте в процентах (Text.ru)
        Незначимыми считаются стоп-слова: союзы, частицы, предлоги, местоимения, междометия,
        предикативы, вводные слова, указательные и вопросительные наречия по разметке
        pymorphy3 (функция is_stopword) или слова из переданного списка стоп-слов
        Нормы Text.ru: до 15% - естественное содержание, 15-30% - избыточное, больше 30% - высокое;
        полосы - STYLE_NORMS
        «Вода» Advego - другой показатель с нормой 55-75%, здесь не реализован

    Ссылки:
        https://text.ru/seo

    Аргументы:
        text (list[str]): Список слов
        stopwords (list[str]): Список стоп-слов; если не задан, используется разметка pymorphy3

    Вывод:
        float: Значение водности в процентах
    """
    check_words(text)
    if stopwords is not None:
        check_words(stopwords, "stopwords", ordered=False)
    if stopwords is not None:
        stopwords_set = {word.lower() for word in stopwords}
        n_stopwords = sum(1 for word in text if word.lower() in stopwords_set)
    else:
        n_stopwords = sum(1 for word in text if is_stopword(word))
    return safe_divide(100 * n_stopwords, len(text))


def calc_spam(text: Sequence[str]) -> float:
    """
    Вычисление заспамленности

    Описание:
        Доля повторов слов в тексте в процентах (Text.ru): каждое вхождение слова,
        кроме первого, считается повтором, то есть заспамленность равна 100 · (1 - TTR)
        Для расчета по леммам извлекайте слова с лемматизацией
        Нормы Text.ru: до 30% - естественное содержание, 30-60% - SEO-оптимизированный текст,
        больше 60% - заспамленный текст; полосы - STYLE_NORMS

    Ссылки:
        https://text.ru/seo

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение заспамленности в процентах
    """
    check_words(text)
    n_words = len(text)
    return safe_divide(100 * (n_words - len(set(text))), n_words)


def calc_zipf_naturalness(text: Sequence[str], top_n: int = NAUSEA_TOP_N) -> float:
    """
    Вычисление естественности текста по закону Ципфа

    Описание:
        Согласие частот самых частых слов с идеальным распределением f_r = f_1 / r,
        где f_1 - частота самого частого слова, r - ранг слова (pr-cy, megaindex)
        Считается как 100 · (1 - среднее относительное отклонение частот от идеальных)
        по рангам от 2 до min(top_n, V, f_1): ранг 1 совпадает с идеалом по построению,
        а при рангах больше f_1 идеальная частота меньше единицы и отклонение
        гапаксов растет без ограничения
        Отрицательные значения обрезаются до 0; норма сервисов - не меньше 50%,
        полосы - STYLE_NORMS
        Не определена, если рангов для сравнения нет: все слова - гапаксы,
        одна лексема или top_n меньше 2

    Ссылки:
        https://en.wikipedia.org/wiki/Zipf's_law

    Аргументы:
        text (list[str]): Список слов
        top_n (int): Количество самых частых слов

    Вывод:
        float: Значение естественности в процентах, nan если рангов для сравнения нет
    """
    check_words(text)
    check_params(top_n)
    frequencies = sorted(Counter(text).values(), reverse=True)
    if not frequencies:
        return nan
    top_freq = frequencies[0]
    n_ranks = min(top_n, len(frequencies), top_freq)
    if n_ranks < 2:
        return nan
    deviation = sum(
        abs(freq - top_freq / rank) / (top_freq / rank)
        for rank, freq in enumerate(frequencies[1:n_ranks], start=2)
    ) / (n_ranks - 1)
    return max(0.0, 100 * (1 - deviation))


def calc_keyword_density(text: Sequence[str], keywords: Collection[str]) -> dict[str, float]:
    """
    Вычисление плотности ключевых слов

    Описание:
        Частота каждого ключевого слова на 100 слов текста (Text.ru, Тургенев)
        Ключевая фраза из нескольких слов через пробел ищется как последовательность слов,
        вхождения фраз могут пересекаться
        Слова сравниваются без учета регистра, для сравнения по леммам извлекайте
        слова с лемматизацией и передавайте леммы

    Ссылки:
        https://text.ru/seo

    Аргументы:
        text (list[str]): Список слов
        keywords (list[str]): Ключевые слова или фразы

    Вывод:
        dict[str, float]: Плотность каждого ключевого слова в процентах
    """
    check_words(text)
    check_words(keywords, "keywords", ordered=False)
    n_words = len(text)
    lowered = [word.lower() for word in text]
    density = {}
    for keyword in keywords:
        parts = keyword.lower().split()
        size = len(parts)
        if not size:
            density[keyword] = 0.0
            continue
        count = sum(1 for i in range(n_words - size + 1) if lowered[i : i + size] == parts)
        density[keyword] = safe_divide(100 * count, n_words)
    return density


def is_parenthetical(word: str) -> bool:
    """
    Проверка, является ли слово вводным по разметке pymorphy3 (граммема Prnt)

    Аргументы:
        word (str): Слово

    Вывод:
        bool: Результат проверки
    """
    return "Prnt" in parse_word(word).tag.grammemes


def calc_verbal_nouns(text: Sequence[str]) -> float:
    """
    Вычисление доли отглагольных существительных

    Описание:
        Доля существительных (по первому разбору pymorphy3), лемма которых
        оканчивается на суффикс из VERBAL_NOUN_SUFFIXES (is_verbal_noun), в процентах
        от всех существительных; nan для текста без существительных

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Доля в процентах
    """
    check_words(text)
    nouns = [parse for parse in map(parse_word, text) if parse.tag.POS == "NOUN"]
    verbal = sum(1 for parse in nouns if is_verbal_noun(parse.normal_form))
    return safe_divide(verbal, len(nouns), nan) * 100


def calc_phrase_density(text: Sequence[str], phrases: Iterable[str]) -> float:
    """
    Вычисление плотности словосочетаний из списка

    Описание:
        Число вхождений словосочетаний (find_phrases) на 100 слов; используется для
        производных предлогов (COMPOUND_PREPOSITIONS) и штампов (OFFICIALESE_CLICHES).
        Словосочетание, начинающееся с инфинитива, находится в любой форме глагола
        (expand_phrases)

    Аргументы:
        text (list[str]): Список слов
        phrases (list[str]): Словосочетания через пробел

    Вывод:
        float: Вхождений на 100 слов
    """
    check_words(text)
    check_words(phrases, "phrases", ordered=False)
    return safe_divide(len(find_phrases(text, expand_phrases(text, phrases))), len(text)) * 100


def expand_phrases(text: Sequence[str], phrases: Iterable[str]) -> dict[str, str]:
    """
    Дополнение словосочетаний формами их глаголов из текста

    Описание:
        Словосочетание с инфинитивом в начале (или после «не») дополняется
        вариантами с формами этого глагола из текста, включая причастия
        и деепричастия: довел до сведения, доведено до сведения

    Аргументы:
        text (list[str]): Список слов
        phrases (list[str]): Словосочетания через пробел

    Вывод:
        dict[str, str]: Словосочетания и их варианты со словосочетанием из списка

    Пример использования:
        >>> from ruts.style_stats import expand_phrases
        >>> expand_phrases(["он", "довел", "до", "сведения"], ["довести до сведения"])
        {'довести до сведения': 'довести до сведения', 'довел до сведения': 'довести до сведения'}
    """
    check_words(text)
    check_words(phrases, "phrases", ordered=False)
    phrases = tuple(phrases)
    words = {normalize_yo(word) for word in text}
    expanded = {phrase: phrase for phrase in phrases}
    for phrase in phrases:
        parts = normalize_yo(phrase).split()
        head = 1 if len(parts) > 1 and parts[0] == "не" else 0
        if len(parts) <= head:
            continue
        for form in sorted(_verb_forms(parts[head]) & words):
            expanded.setdefault(" ".join([*parts[:head], form, *parts[head + 1 :]]), phrase)
    return expanded


@lru_cache(maxsize=4096)
def _verb_forms(word: str) -> frozenset[str]:
    """Формы глагола по всем лексемам pymorphy3, где слово - инфинитив, иначе пустое множество"""
    return frozenset(
        normalize_yo(form.word)
        for parse in get_morph_analyzer().parse(word)
        if parse.tag.POS == "INFN" and normalize_yo(parse.normal_form) == word
        for form in parse.lexeme
    )


def calc_parentheticals(text: Sequence[str]) -> float:
    """
    Вычисление плотности вводных слов

    Описание:
        Вводные словосочетания из PARENTHETICALS (таким образом, как правило) плюс
        одиночные вводные слова по граммеме Prnt pymorphy3 (конечно, например, впрочем)
        вне найденных словосочетаний, на 100 слов

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Вводных слов на 100 слов
    """
    check_words(text)
    spans = find_phrases(text, PARENTHETICALS)
    covered = {position for start, end in spans for position in range(start, end)}
    singles = sum(
        1
        for position, word in enumerate(text)
        if position not in covered and is_parenthetical(word)
    )
    return safe_divide(len(spans) + singles, len(text)) * 100
