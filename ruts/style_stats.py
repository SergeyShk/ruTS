from collections import Counter
from collections.abc import Sequence
from functools import lru_cache
from math import sqrt

from spacy.tokens import Doc

from .constants import NAUSEA_TOP_N, STOPWORD_GRAMMEMES, STOPWORD_POS, STYLE_STATS_DESC
from .extractors import WordsExtractor
from .utils import get_morph_analyzer, safe_divide


class StyleStats:
    """
    Класс для вычисления SEO-метрик стиля и качества текста

    Описание:
        Метрики повторяют показатели сервисов Advego и Text.ru: тошнота, водность,
        заспамленность, естественность распределения слов по закону Ципфа и плотность
        ключевых слов. Точные формулы сервисов не опубликованы, поэтому реализованы
        общепринятые определения, они описаны в докстрингах функций
        Слова по умолчанию извлекаются в нижнем регистре без лемматизации; для расчета
        по леммам передайте WordsExtractor(use_lexemes=True, lowercase=True)

    Пример использования:
        >>> from ruts import StyleStats
        >>> text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
        >>> ss = StyleStats(text)
        >>> ss.get_stats()
        {'classic_nausea': 1.7320508075688772,
        'academic_nausea': 93.33333333333333,
        'water': 33.333333333333336,
        'spam': 26.666666666666668,
        'zipf_naturalness': 55.55555555555556}
        >>> ss.keyword_density("когда", "нет а")
        {'когда': 20.0, 'нет а': 13.333333333333334}

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        words_extractor (WordsExtractor): Инструмент для извлечения слов
        stopwords (list[str]): Список стоп-слов для водности; если не задан, стоп-слова
            определяются по части речи с помощью pymorphy3
        top_n (int): Количество самых частых слов для академической тошноты и естественности по Ципфу

    Атрибуты:
        words (tuple[str]): Кортеж извлеченных слов
        classic_nausea (float): Классическая тошнота
        academic_nausea (float): Академическая тошнота в процентах
        water (float): Водность в процентах
        spam (float): Заспамленность в процентах
        zipf_naturalness (float): Естественность по Ципфу в процентах

    Методы:
        keyword_density: Плотность ключевых слов и фраз
        get_stats: Получение вычисленных метрик стиля текста
        print_stats: Отображение вычисленных метрик стиля текста с описанием на экран

    Исключения:
        TypeError: Если передаваемое значение не является строкой или объектом Doc
        ValueError: Если в источнике данных отсутствуют слова
        ValueError: Если количество самых частых слов не положительно
    """

    def __init__(
        self,
        source: str | Doc,
        words_extractor: WordsExtractor | None = None,
        stopwords: Sequence[str] | None = None,
        top_n: int = NAUSEA_TOP_N,
    ):
        if isinstance(source, Doc):
            text = source.text
            self.words = tuple(
                word.lower_ for word in source if not word.is_punct and not word.is_space
            )
        elif isinstance(source, str):
            text = source
            if not words_extractor:
                words_extractor = WordsExtractor(lowercase=True)
            self.words = words_extractor.extract(text)
        else:
            raise TypeError("Некорректный источник данных")
        if not self.words:
            raise ValueError("В источнике данных отсутствуют слова")
        if top_n < 1:
            raise ValueError("Количество самых частых слов должно быть больше 0")
        self.stopwords = tuple(stopwords) if stopwords is not None else None
        self.top_n = top_n

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

    def keyword_density(self, *keywords: str) -> dict[str, float]:
        """
        Вычисление плотности ключевых слов и фраз

        Аргументы:
            keywords (tuple[str]): Ключевые слова или фразы из нескольких слов через пробел

        Вывод:
            dict[str, float]: Плотность каждого ключевого слова в процентах
        """
        return calc_keyword_density(self.words, keywords)

    def get_stats(self) -> dict[str, float]:
        """
        Получение вычисленных метрик стиля текста

        Вывод:
            dict[str, float]: Справочник вычисленных метрик стиля текста
        """
        return {stat: getattr(self, stat) for stat in STYLE_STATS_DESC}

    def print_stats(self):
        """Отображение вычисленных метрик стиля текста с описанием на экран"""
        print(f"{'Метрика':^35}|{'Значение':^10}")
        print("-" * 45)
        stats = self.get_stats()
        for stat, value in STYLE_STATS_DESC.items():
            print(f"{value:35}|{stats.get(stat):^10.2f}")


@lru_cache(maxsize=65536)
def is_stopword(word: str) -> bool:
    """
    Проверка, является ли слово стоп-словом по части речи

    Описание:
        Стоп-словами считаются союзы, частицы, предлоги, местоимения-существительные,
        междометия, местоименные прилагательные (этот, такой, который, весь), вводные
        слова (конечно, например) и указательные наречия (там, тогда) по разметке pymorphy3
        Результаты разбора кэшируются

    Аргументы:
        word (str): Слово

    Вывод:
        bool: Результат проверки
    """
    tag = get_morph_analyzer().parse(word)[0].tag
    return tag.POS in STOPWORD_POS or bool(STOPWORD_GRAMMEMES & tag.grammemes)


def calc_classic_nausea(text: Sequence[str]) -> float:
    """
    Вычисление классической тошноты

    Описание:
        Квадратный корень из количества вхождений самого частого слова (Advego)
        Характеризует навязчивость одного слова без учета длины текста, поэтому
        растет вместе с текстом
        Норма Advego - не больше 7, на практике 1-5

    Ссылки:
        https://advego.com/text/seo/

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение тошноты
    """
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
        Норма Advego - 5-15%

    Ссылки:
        https://advego.com/text/seo/

    Аргументы:
        text (list[str]): Список слов
        top_n (int): Количество самых частых слов

    Вывод:
        float: Значение тошноты в процентах
    """
    top_freqs = sum(freq for _, freq in Counter(text).most_common(top_n))
    return safe_divide(100 * top_freqs, len(text))


def calc_water(text: Sequence[str], stopwords: Sequence[str] | None = None) -> float:
    """
    Вычисление водности

    Описание:
        Доля незначимых слов в тексте в процентах (Advego, Text.ru)
        Незначимыми считаются стоп-слова: союзы, частицы, предлоги, местоимения, междометия,
        вводные слова и указательные наречия по разметке pymorphy3 (функция is_stopword)
        или слова из переданного списка стоп-слов
        Нормы Text.ru: до 15% - естественное содержание, 15-30% - избыточное, больше 30% - высокое

    Ссылки:
        https://text.ru/seo
        https://advego.com/text/seo/

    Аргументы:
        text (list[str]): Список слов
        stopwords (list[str]): Список стоп-слов; если не задан, используется разметка pymorphy3

    Вывод:
        float: Значение водности в процентах
    """
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
        больше 60% - заспамленный текст

    Ссылки:
        https://text.ru/seo

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение заспамленности в процентах
    """
    n_words = len(text)
    return safe_divide(100 * (n_words - len(set(text))), n_words)


def calc_zipf_naturalness(text: Sequence[str], top_n: int = NAUSEA_TOP_N) -> float:
    """
    Вычисление естественности текста по закону Ципфа

    Описание:
        Согласие частот самых частых слов с идеальным распределением f_r = f_1 / r,
        где f_1 - частота самого частого слова, r - ранг слова (pr-cy, megaindex)
        Считается как 100 · (1 - среднее относительное отклонение частот от идеальных)
        по рангам от 1 до min(top_n, V, f_1): при рангах больше f_1 идеальная частота
        меньше единицы и отклонение хапаксов растет без ограничения
        Отрицательные значения обрезаются до 0; норма сервисов - не меньше 50%

    Ссылки:
        https://en.wikipedia.org/wiki/Zipf's_law

    Аргументы:
        text (list[str]): Список слов
        top_n (int): Количество самых частых слов

    Вывод:
        float: Значение естественности в процентах
    """
    frequencies = sorted(Counter(text).values(), reverse=True)
    if not frequencies:
        return 0.0
    top_freq = frequencies[0]
    n_ranks = min(top_n, len(frequencies), top_freq)
    deviation = (
        sum(
            abs(freq - top_freq / rank) / (top_freq / rank)
            for rank, freq in enumerate(frequencies[:n_ranks], start=1)
        )
        / n_ranks
    )
    return max(0.0, 100 * (1 - deviation))


def calc_keyword_density(text: Sequence[str], keywords: Sequence[str]) -> dict[str, float]:
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
