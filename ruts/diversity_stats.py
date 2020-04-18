from .constants import DIVERSITY_STATS_DESC
from .extractors import WordsExtractor
from math import sqrt, log10
from spacy.tokens import Doc
from typing import Dict, List, Union

class DiversityStats(object):
    """
    Класс для вычисления основных метрик лексического разнообразия текста

    Описание:
        Лексическое разнообразие - это количественная характеристика текста, 
        отражающая степень богатства словаря при построении текста заданной длины

    Ссылки:
        https://ru.wikipedia.org/wiki/Коэффициент_лексического_разнообразия
        https://en.wikipedia.org/wiki/Lexical_diversity
        https://core.ac.uk/download/pdf/82620241.pdf

    Пример использования:
        >>> from ruts import ReadabilityStats
        >>> text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
        >>> rs = ReadabilityStats(text)
        >>> rs.get_stats()
        {'automated_readability_index': 0.2941666666666656,
        'coleman_liau_index': 0.2941666666666656,
        'flesch_kincaid_grade': 3.4133333333333304,
        'flesch_reading_easy': 83.16166666666666,
        'lix': 48.333333333333336,
        'smog_index': 0.05}

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        words_extractor (WordsExtractor): Инструмент для извлечения слов

    Атрибуты:
        ttr (float): Метрика Type-Token Ratio
        rttr (float): Метрика Root Type-Token Ratio
        cttr (float): Метрика Corrected Type-Token Ratio
        httr (float): Метрика Herdan Type-Token Ratio
        sttr (float): Метрика Summer Type-Token Ratio
        mttr (float): Метрика Mass Type-Token Ratio
        dttr (float): Метрика Dugast Type-Token Ratio
        mattr (float): Метрика Moving Average Type-Token Ratio

    Методы:
        get_stats: Получение вычисленных метрик лексического разнообразия текста
        print_stats: Отображение вычисленных метрик лексического разнообразия текста с описанием на экран

    Исключения:
        TypeError: Если передаваемое значение не является строкой или объектом Doc
        ValueError: Если анализируемый текст является пустой строкой
    """

    def __init__(
        self,
        source: Union[str, Doc],
        words_extractor: WordsExtractor = None
    ):
        if isinstance(source, Doc):
            text = source.text
            self.words = tuple(word.text for word in source)
        elif isinstance(source, str):
            text = source
            if not words_extractor:
                words_extractor = WordsExtractor(text)
            self.words = words_extractor.extract()
        else:
            raise TypeError("Некорректный источник данных")
        if not text:
            raise ValueError("Анализируемый текст пуст")

    @property
    def ttr(self):
        return calc_ttr(self.words)

    @property
    def rttr(self):
        return calc_rttr(self.words)

    @property
    def cttr(self):
        return calc_cttr(self.words)

    @property
    def httr(self):
        return calc_httr(self.words)

    @property
    def sttr(self):
        return calc_sttr(self.words)

    @property
    def mttr(self):
        return calc_mttr(self.words)

    @property
    def dttr(self):
        return calc_dttr(self.words)

    @property
    def mattr(self):
        return calc_mattr(self.words, 50)

    def get_stats(self) -> Dict[str, float]:
        """
        Получение вычисленных метрик лексического разнообразия текста

        Вывод:
            dict[str, float]: Справочник вычисленных метрик лексического разнообразия текста
        """
        return {
            'ttr': self.ttr,
            'rttr': self.rttr,
            'cttr': self.cttr,
            'httr': self.httr,
            'sttr': self.sttr,
            'mttr': self.mttr,
            'dttr': self.dttr,
            'mattr': self.mattr
        }

    def print_stats(self):
        """Отображение вычисленных метрик лексического разнообразия текста с описанием на экран"""
        print(f"{'Метрика':^40}|{'Значение':^10}")
        print("-" * 50)
        for stat, value in DIVERSITY_STATS_DESC.items():
            print(f"{value:40}|{self.get_stats().get(stat):^10.2f}")


def calc_ttr(
    text: List[str]
) -> float:
    """
    Вычисление метрики Type-Token Ratio (TTR)

    Описание:
        Самый простой и самый критикуемый способ вычисления лексического разнообразия, 
        не принимающий во внимание влияние эффекта длины текста

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение метрики
    """
    n_words = len(text)
    n_lexemes = len(set(text))
    return n_lexemes / n_words

def calc_rttr(
    text: List[str]
) -> float:
    """
    Вычисление метрики Root Type-Token Ratio (RTTR)

    Описание:
        Модификация метрики TTR (1960, Giraud)

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение метрики
    """
    n_words = len(text)
    n_lexemes = len(set(text))
    return n_lexemes / sqrt(n_words)

def calc_cttr(
    text: List[str]
) -> float:
    """
    Вычисление метрики Corrected Type-Token Ratio (CTTR)

    Описание:
        Модификация метрики TTR (1964, Carrol)

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение метрики
    """
    n_words = len(text)
    n_lexemes = len(set(text))
    return n_lexemes / sqrt(2 * n_words)

def calc_httr(
    text: List[str]
) -> float:
    """
    Вычисление метрики Herdan Type-Token Ratio (HTTR)

    Описание:
        Модификация метрики TTR с использованием логарифмической функции (1960, Herdan)

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение метрики
    """
    n_words = len(text)
    n_lexemes = len(set(text))
    return log10(n_lexemes) / log10(n_words)

def calc_sttr(
    text: List[str]
) -> float:
    """
    Вычисление метрики Summer Type-Token Ratio (STTR)

    Описание:
        Модификация метрики TTR с использованием логарифмической функции (1966, Summer)

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение метрики
    """
    n_words = len(text)
    n_lexemes = len(set(text))
    return log10(log10(n_lexemes)) / log10(log10(n_words))

def calc_mttr(
    text: List[str]
) -> float:
    """
    Вычисление метрики Mass Type-Token Ratio (MTTR)

    Описание:
        Модификация метрики TTR с использованием логарифмической функции (1966, Mass)
        Наиболее стабильная метрика в отношении длины текста

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение метрики
    """
    n_words = len(text)
    n_lexemes = len(set(text))
    return (log10(n_words) - log10(n_lexemes)) / log10(n_words)**2

def calc_dttr(
    text: List[str]
) -> float:
    """
    Вычисление метрики Dugast Type-Token Ratio (DTTR)

    Описание:
        Модификация метрики TTR с использованием логарифмической функции (1978, Dugast)

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение метрики
    """
    n_words = len(text)
    n_lexemes = len(set(text))
    return log10(n_words)**2 / (log10(n_words) - log10(n_lexemes))

def calc_mattr(
    text: List[str],
    window_len: int
) -> float:
    """
    Вычисление метрики Moving Average Type-Token Ratio (MATTR)

    Описание:
        Модификация метрики TTR с использованием скользящей средней (2010, Covington & McFall)

    Аргументы:
        text (list[str]): Список слов
        window_len (int): Размер окна

    Вывод:
        float: Значение метрики
    """
    n_words = len(text)
    if n_words < (window_len + 1):
        mattr = calc_ttr(text)
    else:
        segment_ttr = 0
        segment_count = 0
        for n in range(n_words):
            segment = text[n: (n + window_len)]
            if len(segment) < window_len:
                break
            segment_count += 1
            segment_ttr += len(set(segment)) / float(window_len)
        mattr = segment_ttr / segment_count
    return mattr