from .constants import DIVERSITY_STATS_DESC
from .extractors import WordsExtractor
from .utils import safe_divide
from collections import Counter
from itertools import permutations
from math import sqrt, log10
from nltk import FreqDist
from scipy.special import comb
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
        https://ru.wikipedia.org/wiki/Мера_разнообразия
        https://en.wikipedia.org/wiki/Diversity_index
        https://core.ac.uk/download/pdf/82620241.pdf

    Пример использования:
        >>> from ruts import DiversityStats
        >>> text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
        >>> ds = DiversityStats(text)
        >>> ds.get_stats()
        {'ttr': 0.7333333333333333,
        'rttr': 2.840187787218772,
        'cttr': 2.008316044185609,
        'httr': 0.8854692840710253,
        'sttr': 0.2500605793160845,
        'mttr': 0.0973825075623254,
        'dttr': 10.268784661968104,
        'mattr': 0.7333333333333333,
        'msttr': 0.7333333333333333,
        'mtld': 15.0,
        'mamtld': 11.875,
        'hdd': -1,
        'simpson_index': 21.0,
        'hapax_index': 431.2334616537499}

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        words_extractor (WordsExtractor): Инструмент для извлечения слов

    Атрибуты:
        ttr (float): Метрика Type-Token Ratio (TTR)
        rttr (float): Метрика Root Type-Token Ratio (RTTR)
        cttr (float): Метрика Corrected Type-Token Ratio (CTTR)
        httr (float): Метрика Herdan Type-Token Ratio (HTTR)
        sttr (float): Метрика Summer Type-Token Ratio (STTR)
        mttr (float): Метрика Mass Type-Token Ratio (MTTR)
        dttr (float): Метрика Dugast Type-Token Ratio (DTTR)
        mattr (float): Метрика Moving Average Type-Token Ratio (MATTR)
        msttr (float): Метрика Mean Segmental Type-Token Ratio (MSTTR)
        mtld (float): Метрика Measure of Textual Lexical Diversity (MTLD)
        mamtld (float): Метрика Moving Average Measure of Textual Lexical Diversity (MTLD)
        hdd (float): Метрика Hypergeometric Distribution D (HD-D)
        simpson_index (float): Индекс Симпсона
        hapax_index (float): Гапакс-индекс

    Методы:
        get_stats: Получение вычисленных метрик лексического разнообразия текста
        print_stats: Отображение вычисленных метрик лексического разнообразия текста с описанием на экран

    Исключения:
        TypeError: Если передаваемое значение не является строкой или объектом Doc
        ValueError: Если в источнике данных отсутствуют слова
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
                words_extractor = WordsExtractor(text, lowercase=True)
            self.words = words_extractor.extract()
        else:
            raise TypeError("Некорректный источник данных")
        if not self.words:
            raise ValueError("В источнике данных отсутствуют слова")

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

    @property
    def msttr(self):
        return calc_msttr(self.words, 50)

    @property
    def mtld(self):
        return calc_mtld(self.words, 10)

    @property
    def mamtld(self):
        return calc_mamtld(self.words, 10)

    @property
    def hdd(self):
        return calc_hdd(self.words, 42)

    @property
    def simpson_index(self):
        return calc_simpson_index(self.words)

    @property
    def hapax_index(self):
        return calc_hapax_index(self.words)

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
            'mattr': self.mattr,
            'msttr': self.msttr,
            'mtld': self.mtld,
            'mamtld': self.mamtld,
            'hdd': self.hdd,
            'simpson_index': self.simpson_index,
            'hapax_index': self.hapax_index
        }

    def print_stats(self):
        """Отображение вычисленных метрик лексического разнообразия текста с описанием на экран"""
        print(f"{'Метрика':^60}|{'Значение':^10}")
        print("-" * 70)
        for stat, value in DIVERSITY_STATS_DESC.items():
            print(f"{value:60}|{self.get_stats().get(stat):^10.2f}")


def calc_ttr(text: List[str]) -> float:
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
    return safe_divide(n_lexemes, n_words)

def calc_rttr(text: List[str]) -> float:
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
    return safe_divide(n_lexemes, sqrt(n_words))

def calc_cttr(text: List[str]) -> float:
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
    return safe_divide(n_lexemes, sqrt(2 * n_words))

def calc_httr(text: List[str]) -> float:
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
    return safe_divide(log10(n_lexemes), log10(n_words))

def calc_sttr(text: List[str]) -> float:
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
    if n_words == 1 or n_lexemes == 1:
        return 0
    else:
        return safe_divide(log10(log10(n_lexemes)), log10(log10(n_words)))

def calc_mttr(text: List[str]) -> float:
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
    return safe_divide((log10(n_words) - log10(n_lexemes)), log10(n_words)**2)

def calc_dttr(text: List[str]) -> float:
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
    return safe_divide(log10(n_words)**2, (log10(n_words) - log10(n_lexemes)))

def calc_mattr(
    text: List[str],
    window_len: int = 50
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
        window_ttr = 0
        window_count = 0
        for n in range(n_words):
            window = text[n: (n + window_len)]
            if len(window) < window_len:
                break
            window_count += 1
            window_ttr += len(set(window)) / float(window_len)
        mattr = safe_divide(window_ttr, window_count)
    return mattr

def calc_msttr(
    text: List[str],
    segment_len: int = 50
) -> float:
    """
    Вычисление метрики Mean Segmental Type-Token Ratio (MSTTR)

    Описание:
        Модификация метрики TTR с использованием сегментирования (1944, Johnson)

    Аргументы:
        text (list[str]): Список слов
        segment_len (int): Размер сегмента

    Вывод:
        float: Значение метрики
    """
    n_words = len(text)
    if n_words < (segment_len + 1):
        msttr = calc_ttr(text)
    else:
        segment_ttr = 0
        segment_count = 0
        seed = 0
        for _ in range(int(n_words / segment_len)):
            segment = text[seed: (seed + segment_len)]
            segment_count += 1
            seed += segment_len
            segment_ttr += safe_divide(len(set(segment)), len(segment))
        msttr = safe_divide(segment_ttr, segment_count)
    return msttr

def calc_mtld(
    text: List[str],
    min_len: int = 10
) -> float:
    """
    Вычисление метрики Measure of Textual Lexical Diversity (MTLD)

    Описание:
        Модификация метрики MSTTR (2005, McCarthy)
        В данном алгоритме исходный текст делится на сегменты со значением TTR равным 0.72
        Значение метрики вычисляется путем деления количества слов на количество получившихся сегментов
        Доработанная версия алгоритма предполагает два прохода по тексту - в прямом
        и обратном порядке, и дальнейшее усреднее значения метрики (2010, McCarthy & Jarvis)

    Аргументы:
        text (list[str]): Список слов
        min_len (int): Минимальный размер сегмента

    Вывод:
        float: Значение метрики
    """
    def calc_mtld_base(text):
        """Подсчет базовой метрики MTLD"""
        factor = 0
        factor_len = 0
        start = 0
        for n in range(len(text)):
            factor_text = text[start: n + 1]
            if n + 1 == len(text):
                factor += (1 - calc_ttr(factor_text)) / (1 - 0.72)
                factor_len += len(factor_text)
            else:
                if calc_ttr(factor_text) < 0.72 and len(factor_text) >= min_len:
                    factor += 1
                    factor_len += len(factor_text)
                    start = n + 1
                else:
                    continue
        mtld_base = safe_divide(factor_len, factor)
        return mtld_base

    mltd_forward = calc_mtld_base(text)
    mltd_backward = calc_mtld_base(list(reversed(text)))
    mtld = (mltd_forward + mltd_backward) / 2
    return mtld

def calc_mamtld(
    text: List[str],
    min_len: int = 10
) -> float:
    """
    Вычисление метрики Moving Average Measure of Textual Lexical Diversity (MAMTLD)

    Описание:
        Модификация метрики MTLD с использованием скользящей средней

    Аргументы:
        text (list[str]): Список слов
        min_len (int): Минимальный размер сегмента

    Вывод:
        float: Значение метрики
    """
    def calc_mamtld_base(text):
        """Подсчет базовой метрики MAMTLD"""
        factor = 0
        factor_len = 0
        for n in range(len(text)):
            sub_text = text[n:]
            breaker = False
            for m in range(len(sub_text)):
                if not breaker:
                    factor_text = sub_text[: m + 1]
                    if calc_ttr(factor_text) < 0.72 and len(factor_text) >= min_len:
                        factor += 1
                        factor_len += len(factor_text)
                        breaker = True
                    else:
                        continue
        mamtld_base = safe_divide(factor_len, factor, 1)
        return mamtld_base

    mamtld_forward = calc_mamtld_base(text)
    mamtld_backward = calc_mamtld_base(list(reversed(text)))
    mamtld = (mamtld_forward + mamtld_backward) / 2
    return mamtld

def calc_hdd(
    text: List[str],
    sample_size: int = 42
) -> float:
    """
    Вычисление метрики Hypergeometric Distribution D (HD-D)

    Описание:
        Наиболее достоверная реализация алгоритма VocD (2010, McCarthy & Jarvis)
        В основе алгоритм лежит метод случайного отбора из текста сегментов длиной от 32 до 50 слов и
        вычисления для них TTR с последующим усреднением

    Аргументы:
        text (list[str]): Список слов
        sample_size (int): Длина сегмента

    Вывод:
        float: Значение метрики
    """
    def hyper(successes, sample_size, population_size, freq):
        """
            Вероятность появления слова по крайней мере в одном сегменте, каждый из которых
            сформирован на основе гипергеометрического распределения
        """
        try:
            prob = 1.0 - (float((comb(freq, successes) * comb((population_size - freq),(sample_size - successes)))) /\
                    float(comb(population_size, sample_size)))
            prob = prob * (1 / sample_size)
        except ZeroDivisionError:
            prob = 0
        return prob

    n_words = len(text)
    if n_words < 50:
        return -1
    hdd = 0.0
    lexemes = list(set(text))
    freqs = Counter(text)
    for lexeme in lexemes:
        prob = hyper(0, sample_size, n_words, freqs[lexeme])
        hdd += prob
    return hdd

def calc_simpson_index(text: List[str]) -> float:
    """
    Вычисление индекса Симпсона

    Описание:
        Индекс широко применяется в биологии для описания вероятности принадлежности любых двух особей,
        случайно отобранных из неопределенно большого сообщества, к разным видам
        С определенными допущениями применим и для описания лексического разнообразия текста

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение индекса
    """
    n_words = len(text)
    den = n_words * (n_words - 1)
    perms = permutations(text, 2)
    counter = 0
    for perm in perms:
        if perm[0] == perm[1]:
            counter += 1
    simpson_index = safe_divide(den, counter)
    return simpson_index

def calc_hapax_index(text: List[str]) -> float:
    """
    Вычисление Гапакс-индекса

    Описание:
        Гапакс - слово, встретившееся в тексте только один раз
        Гапаксы того или иного автора нередко используют для атрибуции ему некоторого другого произведения,
        где встречаются такие слова

    Ссылки:
        https://ru.wikipedia.org/wiki/Гапакс
        https://en.wikipedia.org/wiki/Hapax_legomenon

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение индекса
    """
    n_words = len(text)
    n_lexemes = len(set(text))
    num = 100 * log10(n_words)
    freqs = FreqDist(text)
    hapaxes = len(freqs.hapaxes())
    den = 1 - (safe_divide(hapaxes, n_lexemes))
    hapax_index = safe_divide(num, den)
    return hapax_index