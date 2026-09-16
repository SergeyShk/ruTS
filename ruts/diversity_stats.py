from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from functools import partial
from math import inf, log, log2, nan, sqrt
from typing import NamedTuple

import numpy as np
from nltk import FreqDist
from scipy.optimize import curve_fit
from scipy.special import comb
from scipy.stats import t as student_t
from spacy.tokens import Doc

from .constants import (
    BRUNET_W_EXPONENT,
    DIVERSITY_LOG_BASE,
    DIVERSITY_STATS_DESC,
    HDD_SAMPLE_SIZE,
    MATTR_WINDOW_LEN,
    MTLD_MIN_LEN,
    MTLD_TTR_THRESHOLD,
)
from .extractors import WordsExtractor
from .utils import iter_doc_words, safe_divide

Calculator = Callable[[Sequence[str]], float]


class WindowStats(NamedTuple):
    """
    Результат оконного расчета метрики

    Атрибуты:
        mean (float): Среднее значение метрики по окнам
        std (float): Выборочное стандартное отклонение по окнам
        lower (float): Нижняя граница доверительного интервала среднего
        upper (float): Верхняя граница доверительного интервала среднего
        n_windows (int): Количество окон с определенным значением метрики
    """

    mean: float
    std: float
    lower: float
    upper: float
    n_windows: int


class DiversityStats:
    """
    Класс для вычисления основных метрик лексического разнообразия текста

    Описание:
        Лексическое разнообразие - это количественная характеристика текста,
        отражающая степень богатства словаря при построении текста заданной длины
        Соглашения, принятые в библиотеке (совпадают с koRpus и lexical-diversity Кайла):
            логарифмические меры Summer, Maas и Dugast считаются по основанию 10,
            LexicalRichness, textcomplexity и zipfR используют натуральный логарифм
            окно MATTR и MSTTR равно 50 словам, quanteda и koRpus используют 100
            порог TTR для MTLD равен 0.72, минимальная длина фактора - 10 слов;
            фактор закрывается при TTR не больше порога (включительно), в lexical-diversity
            и TAALED сравнение строгое, поэтому значения расходятся на факторах,
            где TTR попадает ровно в 0.72
            размер выборки HD-D равен 42 словам
        Все соглашения вынесены в параметры класса

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
        >>> ds.ttr
        0.7333333333333333
        >>> ds.yule_k
        444.44444444444446
        >>> ds.windowed("ttr", window_len=5)
        WindowStats(mean=0.9333333333333332, std=0.11547005383792512, lower=0.6464898180167025, upper=1.220176848649964, n_windows=3)

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        words_extractor (WordsExtractor): Инструмент для извлечения слов
        window_len (int): Размер окна для MATTR и сегмента для MSTTR
        mtld_threshold (float): Порог TTR для MTLD, MA-MTLD и MTLD-W
        mtld_min_len (int): Минимальная длина фактора для MTLD, MA-MTLD и MTLD-W
        hdd_sample_size (int): Размер выборки для HD-D
        log_base (float): Основание логарифма для метрик Summer, Maas и Dugast

    Атрибуты:
        words (tuple[str]): Кортеж извлеченных слов
        frequency_spectrum (dict[int, int]): Спектр частот - количество лексем с заданной частотой
        ttr (float): Метрика Type-Token Ratio (TTR)
        rttr (float): Метрика Root Type-Token Ratio (RTTR)
        cttr (float): Метрика Corrected Type-Token Ratio (CTTR)
        httr (float): Метрика Herdan Type-Token Ratio (HTTR)
        sttr (float): Метрика Summer Type-Token Ratio (STTR)
        mttr (float): Метрика Maas Type-Token Ratio (MTTR)
        dttr (float): Метрика Dugast Type-Token Ratio (DTTR)
        mattr (float): Метрика Moving Average Type-Token Ratio (MATTR)
        msttr (float): Метрика Mean Segmental Type-Token Ratio (MSTTR)
        mtld (float): Метрика Measure of Textual Lexical Diversity (MTLD)
        mamtld (float): Метрика Moving Average Measure of Textual Lexical Diversity (MA-MTLD)
        mtldw (float): Метрика MTLD со скользящим окном и заворотом текста (MTLD-W)
        hdd (float): Метрика Hypergeometric Distribution D (HD-D)
        simpson_index (float): Индекс Симпсона (D)
        inverse_simpson_index (float): Обратный индекс Симпсона (1/D)
        gini_simpson_index (float): Индекс Джини-Симпсона (1-D)
        hapax_index (float): Гапакс-индекс, он же Honoré's R
        honore_r (float): Псевдоним для гапакс-индекса
        yule_k (float): Характеристика Юла (Yule's K)
        yule_i (float): Обратная характеристика Юла (Yule's I)
        herdan_vm (float): Мера Хердана (Herdan's Vm)
        sichel_s (float): Мера Сишела (Sichel's S)
        michea_m (float): Мера Мишеа (Michéa's M)
        brunet_w (float): Мера Брюне (Brunet's W)
        dugast_k (float): Мера Дюга (Dugast's k)
        baayen_p (float): Мера Баайена (Baayen's P)
        hapax_ratio (float): Доля гапаксов среди лексем
        alpha2 (float): Показатель α₂
        entropy (float): Энтропия Шеннона в битах
        evenness (float): Выравненность - отношение энтропии к максимальной
        perplexity (float): Перплексия
        zipf_alpha (float): Наклон закона Ципфа
        heaps_beta (float): Показатель закона Хипса

    Методы:
        windowed: Оконный расчет метрики со средним и доверительным интервалом
        get_stats: Получение вычисленных метрик лексического разнообразия текста
        print_stats: Отображение вычисленных метрик лексического разнообразия текста с описанием на экран

    Исключения:
        TypeError: Если передаваемое значение не является строкой или объектом Doc
        ValueError: Если в источнике данных отсутствуют слова
        ValueError: Если параметры метрик заданы некорректно
    """

    def __init__(
        self,
        source: str | Doc,
        words_extractor: WordsExtractor | None = None,
        window_len: int = MATTR_WINDOW_LEN,
        mtld_threshold: float = MTLD_TTR_THRESHOLD,
        mtld_min_len: int = MTLD_MIN_LEN,
        hdd_sample_size: int = HDD_SAMPLE_SIZE,
        log_base: float = DIVERSITY_LOG_BASE,
    ):
        if isinstance(source, Doc):
            text = source.text
            self.words = tuple(word.lower() for _, _, word in iter_doc_words(source))
        elif isinstance(source, str):
            text = source
            if not words_extractor:
                words_extractor = WordsExtractor(lowercase=True)
            self.words = words_extractor.extract(text)
        else:
            raise TypeError("Некорректный источник данных")
        if not self.words:
            raise ValueError("В источнике данных отсутствуют слова")
        if window_len < 1:
            raise ValueError("Размер окна должен быть больше 0")
        if not 0 < mtld_threshold < 1:
            raise ValueError("Порог TTR для MTLD должен лежать в интервале (0, 1)")
        if mtld_min_len < 0:
            raise ValueError("Минимальная длина фактора MTLD не может быть отрицательной")
        if hdd_sample_size < 1:
            raise ValueError("Размер выборки HD-D должен быть больше 0")
        if log_base <= 1:
            raise ValueError("Основание логарифма должно быть больше 1")
        self.window_len = window_len
        self.mtld_threshold = mtld_threshold
        self.mtld_min_len = mtld_min_len
        self.hdd_sample_size = hdd_sample_size
        self.log_base = log_base
        self._calculators: dict[str, Calculator] = {
            "ttr": calc_ttr,
            "rttr": calc_rttr,
            "cttr": calc_cttr,
            "httr": calc_httr,
            "sttr": partial(calc_sttr, base=log_base),
            "mttr": partial(calc_mttr, base=log_base),
            "dttr": partial(calc_dttr, base=log_base),
            "mattr": partial(calc_mattr, window_len=window_len),
            "msttr": partial(calc_msttr, segment_len=window_len),
            "mtld": partial(calc_mtld, min_len=mtld_min_len, threshold=mtld_threshold),
            "mamtld": partial(calc_mamtld, min_len=mtld_min_len, threshold=mtld_threshold),
            "mtldw": partial(calc_mtldw, min_len=mtld_min_len, threshold=mtld_threshold),
            "hdd": partial(calc_hdd, sample_size=hdd_sample_size),
            "simpson_index": calc_simpson_index,
            "inverse_simpson_index": calc_inverse_simpson_index,
            "gini_simpson_index": calc_gini_simpson_index,
            "hapax_index": calc_hapax_index,
            "yule_k": calc_yule_k,
            "yule_i": calc_yule_i,
            "herdan_vm": calc_herdan_vm,
            "sichel_s": calc_sichel_s,
            "michea_m": calc_michea_m,
            "brunet_w": calc_brunet_w,
            "dugast_k": partial(calc_dugast_k, base=log_base),
            "baayen_p": calc_baayen_p,
            "hapax_ratio": calc_hapax_ratio,
            "alpha2": calc_alpha2,
            "entropy": calc_entropy,
            "evenness": calc_evenness,
            "perplexity": calc_perplexity,
            "zipf_alpha": calc_zipf_alpha,
            "heaps_beta": calc_heaps_beta,
        }

    def _calc(self, stat: str) -> float:
        return self._calculators[stat](self.words)

    @property
    def frequency_spectrum(self) -> dict[int, int]:
        return calc_frequency_spectrum(self.words)

    @property
    def ttr(self) -> float:
        return self._calc("ttr")

    @property
    def rttr(self) -> float:
        return self._calc("rttr")

    @property
    def cttr(self) -> float:
        return self._calc("cttr")

    @property
    def httr(self) -> float:
        return self._calc("httr")

    @property
    def sttr(self) -> float:
        return self._calc("sttr")

    @property
    def mttr(self) -> float:
        return self._calc("mttr")

    @property
    def dttr(self) -> float:
        return self._calc("dttr")

    @property
    def mattr(self) -> float:
        return self._calc("mattr")

    @property
    def msttr(self) -> float:
        return self._calc("msttr")

    @property
    def mtld(self) -> float:
        return self._calc("mtld")

    @property
    def mamtld(self) -> float:
        return self._calc("mamtld")

    @property
    def mtldw(self) -> float:
        return self._calc("mtldw")

    @property
    def hdd(self) -> float:
        return self._calc("hdd")

    @property
    def simpson_index(self) -> float:
        return self._calc("simpson_index")

    @property
    def inverse_simpson_index(self) -> float:
        return self._calc("inverse_simpson_index")

    @property
    def gini_simpson_index(self) -> float:
        return self._calc("gini_simpson_index")

    @property
    def hapax_index(self) -> float:
        return self._calc("hapax_index")

    @property
    def honore_r(self) -> float:
        return self._calc("hapax_index")

    @property
    def yule_k(self) -> float:
        return self._calc("yule_k")

    @property
    def yule_i(self) -> float:
        return self._calc("yule_i")

    @property
    def herdan_vm(self) -> float:
        return self._calc("herdan_vm")

    @property
    def sichel_s(self) -> float:
        return self._calc("sichel_s")

    @property
    def michea_m(self) -> float:
        return self._calc("michea_m")

    @property
    def brunet_w(self) -> float:
        return self._calc("brunet_w")

    @property
    def dugast_k(self) -> float:
        return self._calc("dugast_k")

    @property
    def baayen_p(self) -> float:
        return self._calc("baayen_p")

    @property
    def hapax_ratio(self) -> float:
        return self._calc("hapax_ratio")

    @property
    def alpha2(self) -> float:
        return self._calc("alpha2")

    @property
    def entropy(self) -> float:
        return self._calc("entropy")

    @property
    def evenness(self) -> float:
        return self._calc("evenness")

    @property
    def perplexity(self) -> float:
        return self._calc("perplexity")

    @property
    def zipf_alpha(self) -> float:
        return self._calc("zipf_alpha")

    @property
    def heaps_beta(self) -> float:
        return self._calc("heaps_beta")

    def windowed(
        self,
        stat: str,
        window_len: int = 100,
        step: int | None = None,
        confidence: float = 0.95,
    ) -> WindowStats:
        """
        Оконный расчет метрики: значение по последовательным окнам текста,
        среднее и доверительный интервал среднего

        Описание:
            Стандартный способ сравнения текстов разной длины: метрика считается
            по окнам одинаковой длины, разброс по окнам дает доверительный интервал
            STTR Кубата и Милички - это оконный расчет TTR с окном 1000 слов
            Окна с неопределенной метрикой (nan) не учитываются, бесконечное значение
            хотя бы в одном окне дает бесконечное среднее без интервала

        Аргументы:
            stat (str): Название метрики из get_stats
            window_len (int): Размер окна
            step (int): Шаг окна, по умолчанию равен размеру окна (окна не пересекаются)
            confidence (float): Уровень доверия

        Вывод:
            WindowStats: Среднее, стандартное отклонение, границы интервала и число окон

        Исключения:
            ValueError: Если указана неизвестная метрика
        """
        if stat not in self._calculators:
            raise ValueError(
                f"Неизвестная метрика: {stat}. Доступные метрики: {tuple(self._calculators)}"
            )
        return calc_windowed(self.words, self._calculators[stat], window_len, step, confidence)

    def get_stats(self) -> dict[str, float]:
        """
        Получение вычисленных метрик лексического разнообразия текста

        Вывод:
            dict[str, float]: Справочник вычисленных метрик лексического разнообразия текста
        """
        return {stat: self._calc(stat) for stat in DIVERSITY_STATS_DESC}

    def print_stats(self):
        """Отображение вычисленных метрик лексического разнообразия текста с описанием на экран"""
        print(f"{'Метрика':^75}|{'Значение':^10}")
        print("-" * 85)
        stats = self.get_stats()
        for stat, value in DIVERSITY_STATS_DESC.items():
            print(f"{value:75}|{stats.get(stat):^10.2f}")


def calc_frequency_spectrum(text: Sequence[str]) -> dict[int, int]:
    """
    Вычисление спектра частот

    Описание:
        Спектр частот - количество лексем V_i, встретившихся в тексте ровно i раз
        Основа для мер Юла, Хердана, Сишела, Мишеа, Баайена и LNRE-моделей zipfR

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        dict[int, int]: Справочник количества лексем по частоте
    """
    return dict(sorted(Counter(Counter(text).values()).items()))


def calc_ttr(text: Sequence[str]) -> float:
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


def calc_rttr(text: Sequence[str]) -> float:
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


def calc_cttr(text: Sequence[str]) -> float:
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


def calc_httr(text: Sequence[str]) -> float:
    """
    Вычисление метрики Herdan Type-Token Ratio (HTTR)

    Описание:
        Модификация метрики TTR с использованием логарифмической функции (1960, Herdan)
        Отношение логарифмов не зависит от основания

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение метрики
    """
    n_words = len(text)
    n_lexemes = len(set(text))
    return safe_divide(log(n_lexemes), log(n_words))


def calc_sttr(text: Sequence[str], base: float = DIVERSITY_LOG_BASE) -> float:
    """
    Вычисление метрики Summer Type-Token Ratio (STTR)

    Описание:
        Модификация метрики TTR с использованием логарифмической функции (1966, Summer)
        Значение зависит от основания логарифма: по умолчанию 10, как в koRpus
        и lexical-diversity, в LexicalRichness и textcomplexity - натуральный

    Аргументы:
        text (list[str]): Список слов
        base (float): Основание логарифма

    Вывод:
        float: Значение метрики
    """
    n_words = len(text)
    n_lexemes = len(set(text))
    if n_words == 1 or n_lexemes == 1:
        return 0
    return safe_divide(log(log(n_lexemes, base), base), log(log(n_words, base), base))


def calc_mttr(text: Sequence[str], base: float = DIVERSITY_LOG_BASE) -> float:
    """
    Вычисление метрики Maas Type-Token Ratio (MTTR)

    Описание:
        Модификация метрики TTR с использованием логарифмической функции (1972, Maas)
        Наиболее стабильная метрика в отношении длины текста
        Значение зависит от основания логарифма: по умолчанию 10, как в koRpus
        и lexical-diversity, в LexicalRichness и textcomplexity - натуральный

    Аргументы:
        text (list[str]): Список слов
        base (float): Основание логарифма

    Вывод:
        float: Значение метрики
    """
    n_words = len(text)
    n_lexemes = len(set(text))
    log_words = log(n_words, base)
    return safe_divide(log_words - log(n_lexemes, base), log_words**2)


def calc_dttr(text: Sequence[str], base: float = DIVERSITY_LOG_BASE) -> float:
    """
    Вычисление метрики Dugast Type-Token Ratio (DTTR)

    Описание:
        Модификация метрики TTR с использованием логарифмической функции (1978, Dugast),
        она же Dugast's U, обратная величина метрики Maas
        Значение зависит от основания логарифма: по умолчанию 10, как в koRpus
        и lexical-diversity, в LexicalRichness и textcomplexity - натуральный

    Аргументы:
        text (list[str]): Список слов
        base (float): Основание логарифма

    Вывод:
        float: Значение метрики
    """
    n_words = len(text)
    n_lexemes = len(set(text))
    log_words = log(n_words, base)
    return safe_divide(log_words**2, log_words - log(n_lexemes, base))


def calc_mattr(text: Sequence[str], window_len: int = MATTR_WINDOW_LEN) -> float:
    """
    Вычисление метрики Moving Average Type-Token Ratio (MATTR)

    Описание:
        Модификация метрики TTR с использованием скользящей средней (2010, Covington & McFall)
        Окно по умолчанию 50 слов, как в lexical-diversity, TAALED и textacy,
        quanteda и koRpus используют 100
        Для текстов короче окна возвращается TTR всего текста

    Аргументы:
        text (list[str]): Список слов
        window_len (int): Размер окна

    Вывод:
        float: Значение метрики
    """
    n_words = len(text)
    if n_words < (window_len + 1):
        return calc_ttr(text)
    counts = Counter(text[:window_len])
    window_ttr = len(counts) / window_len
    for n in range(window_len, n_words):
        counts[text[n]] += 1
        outgoing = text[n - window_len]
        counts[outgoing] -= 1
        if not counts[outgoing]:
            del counts[outgoing]
        window_ttr += len(counts) / window_len
    return window_ttr / (n_words - window_len + 1)


def calc_msttr(text: Sequence[str], segment_len: int = MATTR_WINDOW_LEN) -> float:
    """
    Вычисление метрики Mean Segmental Type-Token Ratio (MSTTR)

    Описание:
        Модификация метрики TTR с использованием сегментирования (1944, Johnson)
        Сегмент по умолчанию 50 слов, как в lexical-diversity, TAALED и textacy,
        quanteda и koRpus используют 100
        Для текстов короче сегмента возвращается TTR всего текста, неполный
        последний сегмент отбрасывается

    Аргументы:
        text (list[str]): Список слов
        segment_len (int): Размер сегмента

    Вывод:
        float: Значение метрики
    """
    n_words = len(text)
    if n_words < (segment_len + 1):
        return calc_ttr(text)
    segments = [text[start : start + segment_len] for start in range(0, n_words, segment_len)]
    segments = [segment for segment in segments if len(segment) == segment_len]
    return sum(calc_ttr(segment) for segment in segments) / len(segments)


def _count_mtld_factors(text: Sequence[str], threshold: float, min_len: int) -> float:
    """Подсчет количества факторов MTLD за один проход по тексту"""
    factors = 0.0
    counts: Counter[str] = Counter()
    factor_len = 0
    for word in text:
        counts[word] += 1
        factor_len += 1
        if len(counts) / factor_len <= threshold and factor_len >= min_len:
            factors += 1
            counts.clear()
            factor_len = 0
    if factor_len:
        ttr = len(counts) / factor_len
        factors += min(1.0, (1 - ttr) / (1 - threshold))
    return factors


def calc_mtld(
    text: Sequence[str], min_len: int = MTLD_MIN_LEN, threshold: float = MTLD_TTR_THRESHOLD
) -> float:
    """
    Вычисление метрики Measure of Textual Lexical Diversity (MTLD)

    Описание:
        Модификация метрики MSTTR (2005, McCarthy)
        Текст делится на факторы - отрезки, на которых TTR опускается до порога 0.72
        включительно (TTR <= 0.72, у McCarthy и Jarvis фактор закрывается, когда TTR
        «достигает» 0.720); в lexical-diversity Кайла и TAALED сравнение строгое,
        поэтому на факторах, где TTR попадает ровно в порог (18/25, 36/50), значения расходятся
        Значение метрики равно отношению количества слов к количеству факторов
        Незавершенный фактор в конце текста учитывается частично, пропорционально
        тому, насколько его TTR приблизился к порогу
        Итоговое значение - среднее двух проходов по тексту, в прямом
        и обратном порядке (2010, McCarthy & Jarvis)
        Минимальная длина фактора взята из lexical-diversity Кайла и нестандартна:
        koRpus применяет ее только к MA-MTLD, LexicalRichness и textcomplexity не применяют
        Если ни один фактор не завершен и TTR не опускается ниже 1, возвращается бесконечность

    Аргументы:
        text (list[str]): Список слов
        min_len (int): Минимальная длина фактора
        threshold (float): Порог TTR для завершения фактора

    Вывод:
        float: Значение метрики
    """
    n_words = len(text)
    forward = safe_divide(n_words, _count_mtld_factors(text, threshold, min_len), inf)
    backward = safe_divide(n_words, _count_mtld_factors(text[::-1], threshold, min_len), inf)
    return (forward + backward) / 2


def _mtld_factor_lengths(
    text: Sequence[str], threshold: float, min_len: int, wrap: bool
) -> list[int]:
    """Длины первых факторов MTLD, начинающихся с каждой позиции текста"""
    n_words = len(text)
    source = tuple(text) + tuple(text) if wrap else tuple(text)
    lengths = []
    for start in range(n_words):
        types: set[str] = set()
        end = start + n_words if wrap else n_words
        for pos in range(start, end):
            types.add(source[pos])
            factor_len = pos - start + 1
            if len(types) / factor_len <= threshold and factor_len >= min_len:
                lengths.append(factor_len)
                break
    return lengths


def calc_mamtld(
    text: Sequence[str], min_len: int = MTLD_MIN_LEN, threshold: float = MTLD_TTR_THRESHOLD
) -> float:
    """
    Вычисление метрики Moving Average Measure of Textual Lexical Diversity (MA-MTLD)

    Описание:
        Модификация метрики MTLD с использованием скользящего окна (koRpus MTLD-MA):
        фактор начинается с каждой позиции текста, значение метрики - средняя длина
        завершенных факторов по двум проходам, в прямом и обратном порядке
        Фактор закрывается при TTR не больше порога включительно, как в calc_mtld
        Факторы, не завершенные до конца текста, не учитываются; если не завершен
        ни один фактор, возвращается nan

    Аргументы:
        text (list[str]): Список слов
        min_len (int): Минимальная длина фактора
        threshold (float): Порог TTR для завершения фактора

    Вывод:
        float: Значение метрики, nan если ни один фактор не завершен
    """
    lengths = _mtld_factor_lengths(text, threshold, min_len, wrap=False)
    lengths += _mtld_factor_lengths(text[::-1], threshold, min_len, wrap=False)
    return safe_divide(sum(lengths), len(lengths), nan)


def calc_mtldw(
    text: Sequence[str], min_len: int = MTLD_MIN_LEN, threshold: float = MTLD_TTR_THRESHOLD
) -> float:
    """
    Вычисление метрики MTLD со скользящим окном и заворотом текста (MTLD-W)

    Описание:
        Модификация метрики MA-MTLD (lexical-diversity mtld_ma_wrap, TAALED): фактор
        начинается с каждой позиции текста, а факторы, не завершенные до конца текста,
        продолжаются с его начала, поэтому все факторы получают равный вес
        Фактор закрывается при TTR не больше порога включительно, как в calc_mtld,
        в lexical-diversity сравнение строгое
        Нестабильна на текстах короче 100 слов
        Если TTR не опускается до порога даже на всем тексте, возвращается nan

    Аргументы:
        text (list[str]): Список слов
        min_len (int): Минимальная длина фактора
        threshold (float): Порог TTR для завершения фактора

    Вывод:
        float: Значение метрики, nan если ни один фактор не завершен
    """
    lengths = _mtld_factor_lengths(text, threshold, min_len, wrap=True)
    return safe_divide(sum(lengths), len(lengths), nan)


def calc_hdd(text: Sequence[str], sample_size: int = HDD_SAMPLE_SIZE) -> float:
    """
    Вычисление метрики Hypergeometric Distribution D (HD-D)

    Описание:
        Наиболее достоверная реализация алгоритма VocD (2010, McCarthy & Jarvis)
        В основе алгоритма лежит метод случайного отбора из текста сегментов длиной от 32 до 50 слов и
        вычисления для них TTR с последующим усреднением
        Размер выборки по умолчанию 42 слова, в литературе встречаются значения от 35 до 50
        Метрика не определена для текстов короче 50 слов и для текстов короче размера выборки

    Аргументы:
        text (list[str]): Список слов
        sample_size (int): Длина сегмента

    Вывод:
        float: Значение метрики, для текстов короче 50 слов или размера выборки - nan
    """

    def hyper(successes, sample_size, population_size, freq):
        """
        Вероятность появления слова по крайней мере в одном сегменте, каждый из которых
        сформирован на основе гипергеометрического распределения
        """
        try:
            prob = 1.0 - (
                float(
                    comb(freq, successes)
                    * comb((population_size - freq), (sample_size - successes))
                )
                / float(comb(population_size, sample_size))
            )
            prob = prob * (1 / sample_size)
        except ZeroDivisionError:
            prob = 0
        return prob

    n_words = len(text)
    if n_words < 50 or n_words < sample_size:
        return nan
    hdd = 0.0
    lexemes = list(set(text))
    freqs = Counter(text)
    for lexeme in lexemes:
        prob = hyper(0, sample_size, n_words, freqs[lexeme])
        hdd += prob
    return hdd


def calc_simpson_index(text: Sequence[str]) -> float:
    """
    Вычисление индекса Симпсона (D)

    Описание:
        Индекс широко применяется в биологии для описания вероятности принадлежности любых двух особей,
        случайно отобранных из неопределенно большого сообщества, к разным видам
        С определенными допущениями применим и для описания лексического разнообразия текста
        Вычисляется в классической форме без возвращения (D = Σ n·(n-1) / N·(N-1)),
        как в quanteda, LexicalRichness и zipfR
        Чем ниже показатель, тем богаче словарь текста
        Обратная величина (1/D) и индекс Джини-Симпсона (1-D) вычисляются отдельными функциями
        Для текстов короче двух слов индекс не определен, как в zipfR и quanteda

    Ссылки:
        https://en.wikipedia.org/wiki/Diversity_index#Simpson_index

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение индекса, для текстов короче двух слов - nan
    """
    n_words = len(text)
    if n_words < 2:
        return nan
    num = sum(freq * (freq - 1) for freq in Counter(text).values())
    return num / (n_words * (n_words - 1))


def calc_inverse_simpson_index(text: Sequence[str]) -> float:
    """
    Вычисление обратного индекса Симпсона (1/D)

    Описание:
        Обратная величина индекса Симпсона, число Хилла второго порядка
        Чем выше показатель, тем богаче словарь текста
        Если все слова текста уникальны, индекс Симпсона равен 0, а обратный индекс - бесконечности

    Ссылки:
        https://en.wikipedia.org/wiki/Diversity_index#Inverse_Simpson_index

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение индекса, для текстов короче двух слов - nan
    """
    return safe_divide(1, calc_simpson_index(text), inf)


def calc_gini_simpson_index(text: Sequence[str]) -> float:
    """
    Вычисление индекса Джини-Симпсона (1-D)

    Описание:
        Вероятность того, что два случайно выбранных слова текста окажутся разными
        Чем выше показатель, тем богаче словарь текста

    Ссылки:
        https://en.wikipedia.org/wiki/Diversity_index#Gini–Simpson_index

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение индекса, для текстов короче двух слов - nan
    """
    return 1 - calc_simpson_index(text)


def calc_hapax_index(text: Sequence[str]) -> float:
    """
    Вычисление Гапакс-индекса (Honoré's R)

    Описание:
        Гапакс - слово, встретившееся в тексте только один раз
        Гапаксы того или иного автора нередко используют для атрибуции ему некоторого другого произведения,
        где встречаются такие слова
        Метрика совпадает с мерой Оноре (1979): R = 100 · ln N / (1 - V1/V),
        где N - количество слов, V - количество лексем, V1 - количество гапаксов
        Используется натуральный логарифм, как в zipfR и textcomplexity
        Если все слова текста являются гапаксами, значение индекса равно бесконечности
        Для текстов короче двух слов индекс не определен, как в zipfR
        Доступна под псевдонимом calc_honore_r

    Ссылки:
        https://ru.wikipedia.org/wiki/Гапакс
        https://en.wikipedia.org/wiki/Hapax_legomenon

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение индекса, для текстов короче двух слов - nan
    """
    n_words = len(text)
    if n_words < 2:
        return nan
    n_lexemes = len(set(text))
    num = 100 * log(n_words)
    freqs = FreqDist(text)
    hapaxes = len(freqs.hapaxes())
    den = 1 - (safe_divide(hapaxes, n_lexemes))
    return safe_divide(num, den, inf)


calc_honore_r = calc_hapax_index


def calc_yule_k(text: Sequence[str]) -> float:
    """
    Вычисление характеристики Юла (Yule's K)

    Описание:
        K = 10⁴ · (Σ i²·V_i - N) / N², где V_i - количество лексем с частотой i (1944, Yule)
        Одна из немногих мер, теоретически не зависящих от длины текста
        (Tweedie & Baayen, 1998), на практике сходится с ростом текста
        Чем ниже показатель, тем богаче словарь текста
        Пропорциональна индексу Симпсона: K ≈ 10⁴ · D

    Ссылки:
        https://link.springer.com/content/pdf/10.1007/s10579-005-8622-8.pdf

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение характеристики, для текстов короче двух слов - nan
    """
    n_words = len(text)
    if n_words < 2:
        return nan
    spectrum = calc_frequency_spectrum(text)
    sum_squares = sum(freq**2 * count for freq, count in spectrum.items())
    return 1e4 * (sum_squares - n_words) / n_words**2


def calc_yule_i(text: Sequence[str]) -> float:
    """
    Вычисление обратной характеристики Юла (Yule's I)

    Описание:
        I = V² / (Σ i²·V_i - V), где V - количество лексем, V_i - количество лексем с частотой i
        Обратная величина к характеристике K, чем выше показатель, тем богаче словарь текста
        Если все слова текста уникальны, значение равно бесконечности

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение характеристики, для текстов короче двух слов - nan
    """
    if len(text) < 2:
        return nan
    n_lexemes = len(set(text))
    spectrum = calc_frequency_spectrum(text)
    sum_squares = sum(freq**2 * count for freq, count in spectrum.items())
    return safe_divide(n_lexemes**2, sum_squares - n_lexemes, inf)


def calc_herdan_vm(text: Sequence[str]) -> float:
    """
    Вычисление меры Хердана (Herdan's Vm)

    Описание:
        Vm = sqrt(Σ V_i · (i/N)² - 1/V), где N - количество слов, V - количество лексем,
        V_i - количество лексем с частотой i (1955, Herdan)
        Теоретически не зависит от длины текста, чем ниже показатель, тем богаче словарь

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение меры, для текстов короче двух слов - nan
    """
    n_words = len(text)
    if n_words < 2:
        return nan
    n_lexemes = len(set(text))
    spectrum = calc_frequency_spectrum(text)
    sum_probs = sum(count * (freq / n_words) ** 2 for freq, count in spectrum.items())
    return sqrt(max(sum_probs - 1 / n_lexemes, 0))


def calc_sichel_s(text: Sequence[str]) -> float:
    """
    Вычисление меры Сишела (Sichel's S)

    Описание:
        S = V2 / V - доля дислегоменов, лексем с частотой 2, среди всех лексем (1975, Sichel)
        Стабильна на текстах разной длины

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение меры
    """
    spectrum = calc_frequency_spectrum(text)
    return safe_divide(spectrum.get(2, 0), len(set(text)))


def calc_michea_m(text: Sequence[str]) -> float:
    """
    Вычисление меры Мишеа (Michéa's M)

    Описание:
        M = V / V2 - обратная величина к мере Сишела (1969, Michéa)
        Если в тексте нет дислегоменов, значение равно бесконечности

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение меры
    """
    spectrum = calc_frequency_spectrum(text)
    return safe_divide(len(set(text)), spectrum.get(2, 0), inf)


def calc_brunet_w(text: Sequence[str], a: float = BRUNET_W_EXPONENT) -> float:
    """
    Вычисление меры Брюне (Brunet's W)

    Описание:
        W = N ^ (V ^ -a), где N - количество слов, V - количество лексем, a = 0.172 (1978, Brunet)
        Значения для текстов обычно лежат в пределах 10-20, чем ниже показатель, тем богаче словарь

    Аргументы:
        text (list[str]): Список слов
        a (float): Показатель степени

    Вывод:
        float: Значение меры
    """
    n_words = len(text)
    n_lexemes = len(set(text))
    if not n_words:
        return nan
    return float(n_words ** (n_lexemes**-a))


def calc_dugast_k(text: Sequence[str], base: float = DIVERSITY_LOG_BASE) -> float:
    """
    Вычисление меры Дюга (Dugast's k)

    Описание:
        k = log V / log log N, где N - количество слов, V - количество лексем (1979, Dugast)
        Значение зависит от основания логарифма: по умолчанию 10, как для метрик
        Summer, Maas и Dugast's U, в textcomplexity - натуральный
        Не определена, если log N не больше 1, то есть для текстов не длиннее основания логарифма

    Аргументы:
        text (list[str]): Список слов
        base (float): Основание логарифма

    Вывод:
        float: Значение меры, для коротких текстов - nan
    """
    n_words = len(text)
    n_lexemes = len(set(text))
    if not n_words or log(n_words, base) <= 1:
        return nan
    return log(n_lexemes, base) / log(log(n_words, base), base)


def calc_baayen_p(text: Sequence[str]) -> float:
    """
    Вычисление меры Баайена (Baayen's P)

    Описание:
        P = V1 / N - доля гапаксов среди всех слов текста (1991, Baayen)
        Равна наклону кривой роста словаря в конце текста: вероятность того,
        что следующее слово окажется новым

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение меры
    """
    spectrum = calc_frequency_spectrum(text)
    return safe_divide(spectrum.get(1, 0), len(text))


def calc_hapax_ratio(text: Sequence[str]) -> float:
    """
    Вычисление доли гапаксов

    Описание:
        V1 / V - доля гапаксов среди всех лексем текста

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение доли
    """
    spectrum = calc_frequency_spectrum(text)
    return safe_divide(spectrum.get(1, 0), len(set(text)))


def calc_alpha2(text: Sequence[str]) -> float:
    """
    Вычисление показателя α₂

    Описание:
        α₂ = 1 - 2·V2 / V1, где V1 - количество гапаксов, V2 - количество дислегоменов
        Оценка параметра Ципфа-Мандельброта по нижней части спектра частот (Evert, 2004)
        Не определен, если в тексте нет гапаксов

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение показателя, nan если в тексте нет гапаксов
    """
    spectrum = calc_frequency_spectrum(text)
    hapaxes = spectrum.get(1, 0)
    if not hapaxes:
        return nan
    return 1 - 2 * spectrum.get(2, 0) / hapaxes


def calc_entropy(text: Sequence[str]) -> float:
    """
    Вычисление энтропии Шеннона

    Описание:
        H = -Σ p_k · log₂ p_k, где p_k - относительная частота лексемы
        Измеряется в битах, чем выше показатель, тем богаче словарь текста
        Число Хилла первого порядка равно 2^H (перплексия), нулевого - V,
        второго - обратный индекс Симпсона

    Ссылки:
        https://en.wikipedia.org/wiki/Diversity_index#Shannon_index

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение энтропии
    """
    n_words = len(text)
    if not n_words:
        return nan
    return -sum(freq / n_words * log2(freq / n_words) for freq in Counter(text).values())


def calc_evenness(text: Sequence[str]) -> float:
    """
    Вычисление выравненности

    Описание:
        H / log₂ V - отношение энтропии Шеннона к ее максимуму при данном количестве лексем
        (выравненность Пиелу), лежит в пределах от 0 до 1
        Не определена для текстов из одной лексемы

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение выравненности, nan для текстов из одной лексемы
    """
    n_lexemes = len(set(text))
    if n_lexemes < 2:
        return nan
    return calc_entropy(text) / log2(n_lexemes)


def calc_perplexity(text: Sequence[str]) -> float:
    """
    Вычисление перплексии

    Описание:
        2^H, где H - энтропия Шеннона в битах; число Хилла первого порядка,
        эффективное количество лексем текста

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение перплексии
    """
    return float(2 ** calc_entropy(text))


def calc_zipf_alpha(text: Sequence[str]) -> float:
    """
    Вычисление наклона закона Ципфа

    Описание:
        Показатель α в законе f(r) ∝ r^(-α), где r - ранг лексемы по частоте
        Оценивается линейной регрессией логарифма частоты по логарифму ранга
        Оценка по рангам методом наименьших квадратов смещена, для точной оценки
        используют метод максимального правдоподобия (например, библиотека powerlaw)
        Для естественных текстов α близка к 1

    Ссылки:
        https://en.wikipedia.org/wiki/Zipf's_law

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение показателя, nan для текстов из одной лексемы
    """
    frequencies = sorted(Counter(text).values(), reverse=True)
    if len(frequencies) < 2:
        return nan
    ranks = np.arange(1, len(frequencies) + 1)
    slope = np.polyfit(np.log(ranks), np.log(frequencies), 1)[0]
    return float(-slope)


class ZipfMandelbrot(NamedTuple):
    """
    Параметры закона Ципфа-Мандельброта f(r) = C / (r + q)^s

    Атрибуты:
        c (float): Масштаб C
        q (float): Сдвиг ранга q
        s (float): Показатель s
        r2 (float): Коэффициент детерминации подгонки в логарифмических координатах
    """

    c: float
    q: float
    s: float
    r2: float


def fit_zipf_mandelbrot(text: Sequence[str] | Mapping[str, int]) -> ZipfMandelbrot:
    """
    Подгонка закона Ципфа-Мандельброта к распределению частот

    Описание:
        Закон f(r) = C / (r + q)^s, где r - ранг лексемы по частоте; при q = 0
        сводится к закону Ципфа со показателем s. Параметры подбираются методом
        наименьших квадратов в логарифмических координатах
        (scipy.optimize.curve_fit) с начальным приближением C = f(1), q = 1, s = 1
        и ограничениями q ≥ 0, s ≥ 0; сдвиг q описывает выполаживание кривой
        на самых частых словах

    Ссылки:
        https://en.wikipedia.org/wiki/Zipf–Mandelbrot_law

    Аргументы:
        text (list[str]|Counter): Список слов или справочник частот

    Вывод:
        ZipfMandelbrot: Параметры закона, nan для текстов из менее чем трех лексем
            или если подгонка не сошлась
    """
    frequencies = np.array(sorted(Counter(text).values(), reverse=True), dtype=float)
    if len(frequencies) < 3:
        return ZipfMandelbrot(nan, nan, nan, nan)
    ranks = np.arange(1, len(frequencies) + 1, dtype=float)
    log_frequencies = np.log(frequencies)

    def model(rank: np.ndarray, log_c: float, q: float, s: float) -> np.ndarray:
        return log_c - s * np.log(rank + q)

    try:
        (log_c, q, s), _ = curve_fit(
            model,
            ranks,
            log_frequencies,
            p0=(log_frequencies[0], 1.0, 1.0),
            bounds=([-np.inf, 0.0, 0.0], [np.inf, np.inf, np.inf]),
        )
    except (RuntimeError, ValueError):
        return ZipfMandelbrot(nan, nan, nan, nan)
    residual = float(((log_frequencies - model(ranks, log_c, q, s)) ** 2).sum())
    total = float(((log_frequencies - log_frequencies.mean()) ** 2).sum())
    r2 = 1 - residual / total if total else nan
    return ZipfMandelbrot(float(np.exp(log_c)), float(q), float(s), r2)


class HeapsFit(NamedTuple):
    """
    Параметры закона Хипса V(N) = K · N^β

    Атрибуты:
        k (float): Коэффициент K
        beta (float): Показатель β
        r2 (float): Коэффициент детерминации подгонки в логарифмических координатах
    """

    k: float
    beta: float
    r2: float


def fit_heaps(text: Sequence[str]) -> HeapsFit:
    """
    Подгонка закона Хипса к кривой роста словаря

    Описание:
        Закон V(N) = K · N^β, где V - размер словаря после N слов текста; параметры
        подбираются линейной регрессией логарифма размера словаря по логарифму
        длины текста вдоль кривой роста, как в calc_heaps_beta, который дает
        только показатель β. Зависит от порядка слов

    Ссылки:
        https://en.wikipedia.org/wiki/Heaps'_law

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        HeapsFit: Параметры закона, nan для текстов короче двух слов
    """
    n_words = len(text)
    if n_words < 2:
        return HeapsFit(nan, nan, nan)
    growth = np.log(vocabulary_growth(text))
    lengths = np.log(np.arange(1, n_words + 1))
    slope, intercept = np.polyfit(lengths, growth, 1)
    residual = float(((growth - (intercept + slope * lengths)) ** 2).sum())
    total = float(((growth - growth.mean()) ** 2).sum())
    r2 = 1 - residual / total if total else nan
    return HeapsFit(float(np.exp(intercept)), float(slope), r2)


def vocabulary_growth(text: Sequence[str]) -> list[int]:
    """
    Вычисление кривой роста словаря

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        list[int]: Размер словаря после каждого слова текста
    """
    seen: set[str] = set()
    growth = []
    for word in text:
        seen.add(word)
        growth.append(len(seen))
    return growth


def calc_heaps_beta(text: Sequence[str]) -> float:
    """
    Вычисление показателя закона Хипса

    Описание:
        Показатель β в законе V(N) = K · N^β, описывающем рост словаря V
        с ростом длины текста N
        Оценивается линейной регрессией логарифма размера словаря по логарифму
        длины текста вдоль кривой роста словаря; зависит от порядка слов
        и требует от нескольких сотен слов
        Для естественных текстов β лежит в пределах 0.4-0.6

    Ссылки:
        https://en.wikipedia.org/wiki/Heaps'_law

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение показателя, nan для текстов короче двух слов
    """
    return fit_heaps(text).beta


def calc_windowed(
    text: Sequence[str],
    func: Calculator,
    window_len: int = 100,
    step: int | None = None,
    confidence: float = 0.95,
) -> WindowStats:
    """
    Оконный расчет метрики

    Описание:
        Метрика вычисляется по последовательным окнам текста одинаковой длины,
        по значениям окон считаются среднее, выборочное стандартное отклонение
        и доверительный интервал среднего по распределению Стьюдента
        Стандартный способ сравнения текстов разной длины (textcomplexity bootstrap,
        характеристические кривые koRpus); STTR Кубата и Милички - оконный расчет TTR
        с окном 1000 слов и 95% доверительным интервалом
        Для текстов короче окна метрика считается по всему тексту как по единственному окну
        Окна, в которых метрика не определена (nan), не учитываются
        Если хотя бы в одном окне метрика бесконечна, среднее равно бесконечности,
        а стандартное отклонение и доверительный интервал не определены

    Аргументы:
        text (list[str]): Список слов
        func (callable): Функция вычисления метрики по списку слов
        window_len (int): Размер окна
        step (int): Шаг окна, по умолчанию равен размеру окна (окна не пересекаются)
        confidence (float): Уровень доверия

    Вывод:
        WindowStats: Среднее, стандартное отклонение, границы интервала и число окон

    Исключения:
        ValueError: Если размер окна, шаг или уровень доверия заданы некорректно
    """
    if window_len < 1:
        raise ValueError("Размер окна должен быть больше 0")
    if step is None:
        step = window_len
    if step < 1:
        raise ValueError("Шаг окна должен быть больше 0")
    if not 0 < confidence < 1:
        raise ValueError("Уровень доверия должен лежать в интервале (0, 1)")
    n_words = len(text)
    if n_words <= window_len:
        windows = [text]
    else:
        windows = [
            text[start : start + window_len] for start in range(0, n_words - window_len + 1, step)
        ]
    values = np.array([func(window) for window in windows], dtype=float)
    values = values[~np.isnan(values)]
    n_windows = int(values.size)
    if not n_windows:
        return WindowStats(nan, nan, nan, nan, 0)
    with np.errstate(invalid="ignore"):
        mean = float(values.mean())
    if n_windows < 2 or not np.isfinite(mean):
        return WindowStats(mean, nan, nan, nan, n_windows)
    std = float(values.std(ddof=1))
    half_width = float(student_t.ppf((1 + confidence) / 2, n_windows - 1)) * std / sqrt(n_windows)
    return WindowStats(mean, std, mean - half_width, mean + half_width, n_windows)
