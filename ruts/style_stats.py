from __future__ import annotations

from collections.abc import Collection, Iterator, Sequence
from functools import lru_cache
from math import nan
from typing import TYPE_CHECKING

import anyts.style_stats
import pymorphy3
from anyts.constants import NAUSEA_TOP_N
from anyts.style_stats import (
    calc_classic_nausea as calc_classic_nausea,
    calc_spam as calc_spam,
)
from anyts.utils import check_words, safe_divide

from .constants import (
    COMPOUND_PREPOSITIONS,
    CORE_MESSAGES,
    OFFICIALESE_CLICHES,
    PARENTHETICALS,
    STOPWORD_GRAMMEMES,
    STOPWORD_POS,
    STYLE_NORMS,
    STYLE_STATS_DESC,
    WATER_POS,
)
from .exceptions import SourceTypeError
from .extractors import WordsExtractor
from .utils import is_verbal_noun, normalize_yo, parse_all, parse_word, strip_marks

if TYPE_CHECKING:
    from spacy.tokens import Doc


def check_params(top_n: int) -> None:
    """
    Проверка параметров SEO-метрик

    Аргументы:
        top_n (int): Количество самых частых слов

    Исключения:
        ParameterError: Если количество самых частых слов не целое число или меньше единицы
    """
    anyts.style_stats.check_params(top_n, messages=CORE_MESSAGES)


class StyleStats(anyts.style_stats.StyleStats):
    """
    Класс для вычисления SEO-метрик стиля и качества текста

    Описание:
        Расширяет StyleStats ядра anyTS крючками русского языка: стоп-слова, «вода»,
        вводные слова и существительные - по разметке pymorphy3, словосочетания
        сравниваются без буквы ё и находятся в любой форме глагола, нормы
        сервисов - STYLE_NORMS. Слова Doc - без знаков ударения, дефисные слова
        склеиваются

    Пример использования:
        >>> from ruts import StyleStats
        >>> text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
        >>> ss = StyleStats(text)
        >>> ss.get_stats()
        {'classic_nausea': 1.7320508075688772,
        'academic_nausea': 53.333333333333336,
        'water': 33.333333333333336,
        'spam': 26.666666666666668,
        'zipf_naturalness': 33.333333333333336,
        'verbal_nouns': 0.0,
        'compound_prepositions': 0.0,
        'parentheticals': 0.0,
        'cliches': 0.0}
        >>> ss.keyword_density("когда", "нет а")
        {'когда': 20.0, 'нет а': 13.333333333333334}
        >>> ss.describe("water"), ss.describe("spam")
        ('высокая водность по Text.ru', 'естественный текст по Text.ru')
        >>> StyleStats("В целях повышения качества в кратчайшие сроки, как правило, проводится проверка").markers()
        {'verbal_nouns': ('повышения',),
        'compound_prepositions': ('в целях',),
        'parentheticals': ('как правило',),
        'cliches': ('в кратчайшие сроки',)}

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        words_extractor (WordsExtractor): Инструмент для извлечения слов;
            если задан, применяется и к тексту Doc
        stopwords (list[str]): Список слов «воды» для водности; если не задан - is_water_word
        top_n (int): Количество самых частых слов для академической тошноты и естественности по Ципфу
        cliches (list[str]): Список штампов; если не задан, используется OFFICIALESE_CLICHES
        nausea_stopwords (list[str]): Список стоп-слов для академической тошноты; если
            не задан - is_stopword

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
        nausea_words: Самые частые значимые слова академической тошноты
        markers: Найденные маркеры канцелярита
        describe: Прочтение метрики стиля по нормам SEO-сервисов
        get_stats: Получение вычисленных метрик стиля текста
        to_dataframe: Получение статистик таблицей из одной строки
        print_stats: Отображение вычисленных метрик стиля текста с описанием на экран

    Исключения:
        SourceTypeError: Если источник данных не строка и не объект Doc, экстрактор
            другого типа или список не список строк
        SourceError: Если в источнике данных отсутствуют слова
        ParameterError: Если количество самых частых слов не целое число или меньше единицы
    """

    words_extractor_class = WordsExtractor
    join_hyphens = True
    compound_prepositions_list = COMPOUND_PREPOSITIONS
    parentheticals_list = PARENTHETICALS
    cliches_list = OFFICIALESE_CLICHES
    level_scales = STYLE_NORMS
    stats_desc = STYLE_STATS_DESC
    stats_headers = ("Метрика", "Значение")
    messages = CORE_MESSAGES

    def normalize(self, word: str) -> str:
        """Нижний регистр без буквы ё и знаков ударения (normalize_yo)"""
        return normalize_yo(word)

    def doc_words(self, doc: Doc) -> tuple[str, ...]:
        """Слова Doc ядра без знаков ударения"""
        return tuple(map(strip_marks, super().doc_words(doc)))

    def is_stopword(self, word: str) -> bool:
        """Стоп-слово академической тошноты по разметке pymorphy3 (is_stopword)"""
        return is_stopword(word)

    def is_water_word(self, word: str) -> bool:
        """«Вода» по разметке pymorphy3 (is_water_word)"""
        return is_water_word(word)

    def is_parenthetical(self, word: str) -> bool:
        """Вводное слово по граммеме Prnt pymorphy3 (is_parenthetical)"""
        return is_parenthetical(word)

    def expand_phrases(self, text: Sequence[str], phrases: Collection[str]) -> dict[str, str]:
        """Словосочетания с формами их глаголов из текста (expand_phrases)"""
        return expand_phrases(text, phrases)

    def nouns(self) -> list[tuple[str, str]]:
        """Существительные словоформ по первому разбору pymorphy3 с леммами"""
        return [
            (self.forms[position], parse.normal_form)
            for position, parse in _iter_nouns(self.forms)
        ]

    def is_verbal_noun(self, lemma: str) -> bool:
        """Отглагольное существительное (ruts.utils.is_verbal_noun)"""
        return is_verbal_noun(lemma)


@lru_cache(maxsize=65536)
def is_stopword(word: str) -> bool:
    """
    Проверка, является ли слово стоп-словом по части речи

    Описание:
        Стоп-словами считаются союзы, частицы, предлоги, местоимения-существительные,
        междометия, предикативы (нет, надо, можно), местоименные прилагательные
        (этот, такой, который, весь), вводные слова (конечно, например), указательные
        (там, тогда) и вопросительные (где, почему) наречия по разметке pymorphy3

    Аргументы:
        word (str): Слово

    Вывод:
        bool: Результат проверки
    """
    if not isinstance(word, str):
        raise SourceTypeError(f"Слово должно быть строкой, а не {type(word).__name__}")
    tag = parse_word(word).tag
    return tag.POS in STOPWORD_POS or bool(STOPWORD_GRAMMEMES & tag.grammemes)


@lru_cache(maxsize=65536)
def is_water_word(word: str) -> bool:
    """
    Проверка, является ли слово «водой» по части речи

    Описание:
        «Вода» - союзы (с вводными «конечно», «например», которые pymorphy3 относит
        к союзам), частицы, местоимения-существительные и междометия по разметке
        pymorphy3; предлоги, местоименные прилагательные и предикативы, в отличие
        от is_stopword, водой не считаются

    Аргументы:
        word (str): Слово

    Вывод:
        bool: Результат проверки
    """
    if not isinstance(word, str):
        raise SourceTypeError(f"Слово должно быть строкой, а не {type(word).__name__}")
    tag = parse_word(word).tag
    return tag.POS in WATER_POS


def is_parenthetical(word: str) -> bool:
    """
    Проверка, является ли слово вводным по разметке pymorphy3 (граммема Prnt)

    Аргументы:
        word (str): Слово

    Вывод:
        bool: Результат проверки
    """
    return "Prnt" in parse_word(word).tag.grammemes


def calc_academic_nausea(
    text: Sequence[str],
    top_n: int = NAUSEA_TOP_N,
    stopwords: Collection[str] | None = None,
) -> float:
    """
    Вычисление академической тошноты

    Описание:
        Суммарная частота top_n самых частых слов без стоп-слов (find_nausea_words),
        деленная на количество всех слов, в процентах (Advego); норма Advego - 5-15%,
        полосы - STYLE_NORMS

    Ссылки:
        https://advego.com/text/seo/

    Аргументы:
        text (list[str]): Список слов
        top_n (int): Количество самых частых слов
        stopwords (list[str]): Список стоп-слов; если не задан - is_stopword

    Вывод:
        float: Значение тошноты в процентах
    """
    return anyts.style_stats.calc_academic_nausea(
        text,
        top_n,
        stopwords,
        is_stopword=is_stopword,
        normalize=normalize_yo,
        messages=CORE_MESSAGES,
    )


def find_nausea_words(
    text: Sequence[str],
    top_n: int = NAUSEA_TOP_N,
    stopwords: Collection[str] | None = None,
) -> dict[str, int]:
    """
    Поиск самых частых значимых слов академической тошноты

    Описание:
        top_n самых частых слов без стоп-слов (переданного списка без учета регистра
        и буквы ё или is_stopword) с количеством вхождений, по убыванию частоты

    Аргументы:
        text (list[str]): Список слов
        top_n (int): Количество самых частых слов
        stopwords (list[str]): Список стоп-слов; если не задан - is_stopword

    Вывод:
        dict[str, int]: Количество вхождений каждого слова

    Пример использования:
        >>> from ruts.style_stats import find_nausea_words
        >>> find_nausea_words(["кот", "и", "кот", "и", "пес"], top_n=1)
        {'кот': 2}
    """
    return anyts.style_stats.find_nausea_words(
        text,
        top_n,
        stopwords,
        is_stopword=is_stopword,
        normalize=normalize_yo,
        messages=CORE_MESSAGES,
    )


def calc_water(text: Sequence[str], stopwords: Collection[str] | None = None) -> float:
    """
    Вычисление водности

    Описание:
        Доля «воды» в тексте в процентах (Text.ru): слов is_water_word или слов
        из переданного списка без учета регистра и буквы ё. Нормы Text.ru: до 15% -
        естественное содержание, 15-30% - избыточное, больше 30% - высокое;
        полосы - STYLE_NORMS. «Вода» Advego - другой показатель, здесь не реализован

    Ссылки:
        https://text.ru/seo

    Аргументы:
        text (list[str]): Список слов
        stopwords (list[str]): Список слов «воды»; если не задан - is_water_word

    Вывод:
        float: Значение водности в процентах
    """
    return anyts.style_stats.calc_water(
        text, stopwords, is_water_word=is_water_word, normalize=normalize_yo
    )


def calc_zipf_naturalness(text: Sequence[str], top_n: int = NAUSEA_TOP_N) -> float:
    """
    Вычисление естественности текста по закону Ципфа

    Описание:
        100 · (1 - среднее относительное отклонение частот от идеальных f_r = f_1 / r)
        по рангам от 2 до min(top_n, V, f_1) (pr-cy, megaindex); отрицательные
        значения обрезаются до 0, норма сервисов - не меньше 50%, полосы - STYLE_NORMS

    Ссылки:
        https://en.wikipedia.org/wiki/Zipf's_law

    Аргументы:
        text (list[str]): Список слов
        top_n (int): Количество самых частых слов

    Вывод:
        float: Значение естественности в процентах; nan, если рангов для сравнения нет
            (все слова - гапаксы, одна лексема или top_n меньше 2)
    """
    return anyts.style_stats.calc_zipf_naturalness(text, top_n, messages=CORE_MESSAGES)


def calc_keyword_density(text: Sequence[str], keywords: Collection[str]) -> dict[str, float]:
    """
    Вычисление плотности ключевых слов

    Описание:
        Частота каждого ключевого слова на 100 слов текста (Text.ru); ключевая фраза
        из нескольких слов через пробел ищется как последовательность слов, вхождения
        могут пересекаться; слова сравниваются в нижнем регистре без буквы ё
        (calc_keyword_density ядра с normalize_yo)

    Ссылки:
        https://text.ru/seo

    Аргументы:
        text (list[str]): Список слов
        keywords (list[str]): Ключевые слова или фразы

    Вывод:
        dict[str, float]: Плотность каждого ключевого слова в процентах
    """
    return anyts.style_stats.calc_keyword_density(text, keywords, normalize_yo)


def calc_verbal_nouns(text: Sequence[str]) -> float:
    """
    Вычисление доли отглагольных существительных

    Описание:
        Доля существительных (по первому разбору pymorphy3), лемма которых -
        отглагольное существительное по is_verbal_noun, в процентах от всех
        существительных

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Доля в процентах; nan для текста без существительных
    """
    check_words(text)
    nouns = list(_iter_nouns(text))
    verbal = sum(1 for _, parse in nouns if is_verbal_noun(parse.normal_form))
    return safe_divide(verbal, len(nouns), nan) * 100


def find_verbal_nouns(text: Sequence[str]) -> list[tuple[int, int]]:
    """
    Поиск отглагольных существительных

    Описание:
        Существительные, которые считает calc_verbal_nouns

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        list[tuple[int, int]]: Границы найденных слов как срезы text

    Пример использования:
        >>> from ruts.style_stats import find_verbal_nouns
        >>> find_verbal_nouns(["организация", "работы", "и", "решение", "вопросов"])
        [(0, 1), (3, 4)]
    """
    check_words(text)
    return [
        (position, position + 1)
        for position, parse in _iter_nouns(text)
        if is_verbal_noun(parse.normal_form)
    ]


def _iter_nouns(text: Sequence[str]) -> Iterator[tuple[int, pymorphy3.analyzer.Parse]]:
    """Позиции и первые разборы существительных"""
    for position, parse in enumerate(map(parse_word, text)):
        if parse.tag.POS == "NOUN":
            yield position, parse


def calc_phrase_density(text: Sequence[str], phrases: Collection[str]) -> float:
    """
    Вычисление плотности словосочетаний из списка

    Описание:
        Число вхождений словосочетаний (find_phrases) на 100 слов; словосочетание,
        начинающееся с инфинитива, находится в любой форме глагола (expand_phrases)

    Аргументы:
        text (list[str]): Список слов
        phrases (list[str]): Словосочетания через пробел

    Вывод:
        float: Вхождений на 100 слов
    """
    return anyts.style_stats.calc_phrase_density(
        text, phrases, expand=expand_phrases, normalize=normalize_yo
    )


def expand_phrases(text: Sequence[str], phrases: Collection[str]) -> dict[str, str]:
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
        for parse in parse_all(word)
        if parse.tag.POS == "INFN" and normalize_yo(parse.normal_form) == word
        for form in parse.lexeme
    )


def calc_parentheticals(text: Sequence[str]) -> float:
    """
    Вычисление плотности вводных слов

    Описание:
        Вводные словосочетания и слова find_parentheticals на 100 слов

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Вводных слов на 100 слов
    """
    return anyts.style_stats.calc_parentheticals(
        text,
        PARENTHETICALS,
        is_parenthetical=is_parenthetical,
        expand=expand_phrases,
        normalize=normalize_yo,
    )


def find_parentheticals(text: Sequence[str]) -> list[tuple[int, int]]:
    """
    Поиск вводных слов и словосочетаний

    Описание:
        Вводные словосочетания из PARENTHETICALS (таким образом, как правило) в любой
        форме глагола (expand_phrases) и одиночные вводные слова is_parenthetical
        (конечно, например, впрочем) вне найденных словосочетаний; слова сравниваются
        без буквы ё (find_parentheticals ядра)

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        list[tuple[int, int]]: Границы найденных слов и словосочетаний как срезы text,
            по порядку

    Пример использования:
        >>> from ruts.style_stats import find_parentheticals
        >>> find_parentheticals(["таким", "образом", "мы", "конечно", "правы"])
        [(0, 2), (3, 4)]
    """
    return anyts.style_stats.find_parentheticals(
        text,
        PARENTHETICALS,
        is_parenthetical=is_parenthetical,
        expand=expand_phrases,
        normalize=normalize_yo,
    )
