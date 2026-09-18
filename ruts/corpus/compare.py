from collections.abc import Callable, Mapping, Sequence
from itertools import pairwise
from math import floor, isnan, nan, sqrt
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

from ..basic_stats import BasicStats, punctuation_profile
from ..constants import MORPHOLOGY_STATS_DESC
from ..diversity_stats import DiversityStats
from ..exceptions import ParameterError, SourceError
from ..extractors import SentsExtractor, WordsExtractor
from ..morph_stats import MorphStats
from ..readability_stats import ReadabilityStats
from ..utils import iter_text_words
from ..visualizers.sentences import sentence_lengths

Features = Callable[[str], Mapping[str, float]]
Values = Sequence[float] | np.ndarray[Any, Any]

OPENING_MARKS = frozenset('«"„“‘([{—–-')
COMPARISON_COLUMNS = (
    "mean_a",
    "mean_b",
    "median_a",
    "median_b",
    "median_diff",
    "ci_low",
    "ci_high",
    "cohen_d",
    "cliff_delta",
    "auc",
    "u",
    "p_value",
    "p_holm",
    "n_a",
    "n_b",
)


def split_windows(text: str, window: int | None = 1000) -> list[str]:
    """
    Разбиение текста на окна по словам

    Описание:
        Число окон - отношение числа слов к размеру окна, округленное вверх
        от половины (2500 слов при окне 1000 - три окна), не меньше одного,
        части равные, как сегменты в zeta: короткие тексты не теряются, хвост
        не отбрасывается. Первое окно начинается с первого непробельного символа
        текста, граница между окнами проходит перед первым словом следующего окна
        и открывающими знаками перед ним (OPENING_MARKS: кавычки, скобки, тире),
        последнее окно длится до конца текста; пробелы по краям окон убираются,
        так что знаки препинания перед первым словом, после последнего слова окна
        и в конце текста остаются в окнах; при window=None окно - весь текст
        без пробелов по краям

    Аргументы:
        text (str): Строка текста
        window (int): Размер окна в словах; None - текст целиком

    Вывод:
        list[str]: Окна текста; пустой список для текста без слов

    Исключения:
        ParameterError: Если размер окна меньше единицы
    """
    if window is not None and window < 1:
        raise ParameterError("Размер окна должен быть больше 0")
    words = list(iter_text_words(text))
    if not words:
        return []
    n_windows = 1 if window is None else max(1, floor(len(words) / window + 0.5))
    chunks = np.array_split(np.arange(len(words)), n_windows)
    boundaries = [0]
    for chunk in chunks[1:]:
        boundary = words[chunk[0]][0]
        previous_end = words[chunk[0] - 1][1]
        while boundary > previous_end and (
            text[boundary - 1].isspace() or text[boundary - 1] in OPENING_MARKS
        ):
            boundary -= 1
        boundaries.append(boundary)
    boundaries.append(len(text))
    return [text[start:end].strip() for start, end in pairwise(boundaries)]


def text_features(text: str) -> dict[str, float]:
    """
    Вычисление признаков текста для сравнения корпусов

    Описание:
        Признаки с префиксом по источнику: basic_ - доли уникальных, длинных,
        сложных, простых, одно- и многосложных слов, букв, пробелов и знаков
        препинания, среднее число букв и слогов на слово и слов на предложение
        (BasicStats); readability_ - все формулы удобочитаемости, сводный класс
        и время чтения (ReadabilityStats); diversity_ - все меры лексического
        разнообразия (DiversityStats); morph_ - доли частей речи от числа слов
        и доли значений внутри каждого морфологического признака по полному
        словарю значений MORPHOLOGY_STATS_DESC, например morph_pos_NOUN
        и morph_case_Gen: не встретившееся значение дает 0, отсутствующий
        в окне признак целиком (нет глаголов - нет времени) - nan (MorphStats
        по pymorphy3); sents_ - средняя
        длина предложения в словах, ее стандартное отклонение, коэффициент
        вариации и автокорреляция соседних длин - ритм текста; punct_ - частоты
        знаков по типам на 1000 слов и доля буквы ё (punctuation_profile)
        Слова и предложения извлекаются по одному разу и передаются во все
        классы, базовые статистики считаются один раз (ReadabilityStats получает
        готовый BasicStats); на окно в 1000 слов уходит около 0.1 с, большая
        часть - разбор pymorphy3

    Аргументы:
        text (str): Строка текста

    Вывод:
        dict[str, float]: Признаки; неопределенные значения - nan

    Исключения:
        SourceError: Если в тексте нет слов
    """
    sents = _CachedSentsExtractor()
    words = _CachedWordsExtractor()
    basic = BasicStats(text, sents, words, normalize=True)
    features: dict[str, float] = {}
    for key in (
        "p_unique_words",
        "p_long_words",
        "p_complex_words",
        "p_simple_words",
        "p_monosyllable_words",
        "p_polysyllable_words",
        "p_letters",
        "p_spaces",
        "p_punctuations",
    ):
        features[f"basic_{key}"] = float(getattr(basic, key))
    features["basic_letters_per_word"] = basic.n_letters / basic.n_words
    features["basic_syllables_per_word"] = basic.n_syllables / basic.n_words
    features["basic_words_per_sent"] = basic.n_words / basic.n_sents if basic.n_sents else nan
    for key, score in ReadabilityStats(basic).get_stats().items():
        features[f"readability_{key}"] = float(score)
    for key, score in DiversityStats(text, words_extractor=words).get_stats().items():
        features[f"diversity_{key}"] = float(score)
    morph = MorphStats(text, words_extractor=words)
    n_words = len(morph.words)
    stats = morph.get_stats(filter_none=True)
    for category, desc in MORPHOLOGY_STATS_DESC.items():
        counts = stats.get(category, {})
        denominator = n_words if category == "pos" else sum(counts.values())
        for label in desc["values"]:
            features[f"morph_{category}_{label}"] = (
                counts.get(label, 0) / denominator if denominator else nan
            )
    features.update(sentence_rhythm(sentence_lengths(text)))
    features.update(
        (f"punct_{key}", float(value))
        for key, value in punctuation_profile(text, basic.n_words).items()
    )
    return features


class _CachedWordsExtractor(WordsExtractor):
    def __init__(self) -> None:
        super().__init__()
        self._text: str | None = None

    def extract(self, text: str) -> tuple[str, ...]:
        if text != self._text:
            self._text = text
            super().extract(text)
        return self.words


class _CachedSentsExtractor(SentsExtractor):
    def __init__(self) -> None:
        super().__init__()
        self._text: str | None = None

    def extract(self, text: str) -> tuple[str, ...]:
        if text != self._text:
            self._text = text
            super().extract(text)
        return self.sents


def sentence_rhythm(lengths: Sequence[int]) -> dict[str, float]:
    """
    Вычисление признаков ритма предложений

    Описание:
        Средняя длина предложения в словах, стандартное отклонение, коэффициент
        вариации и автокорреляция лага 1 - связь длин соседних предложений
        (Yule 1939); автокорреляция требует не меньше трех предложений

    Аргументы:
        lengths (list[int]): Длины предложений в словах

    Вывод:
        dict[str, float]: Признаки sents_mean, sents_std, sents_cv, sents_autocorr
    """
    values = np.asarray(lengths, dtype=float)
    if not len(values):
        return dict.fromkeys(("sents_mean", "sents_std", "sents_cv", "sents_autocorr"), nan)
    mean = float(values.mean())
    std = float(values.std(ddof=1)) if len(values) > 1 else nan
    centered = values - mean
    variance = float((centered**2).sum())
    autocorr = (
        float((centered[:-1] * centered[1:]).sum() / variance)
        if len(values) > 2 and variance
        else nan
    )
    return {
        "sents_mean": mean,
        "sents_std": std,
        "sents_cv": std / mean if mean and not isnan(std) else nan,
        "sents_autocorr": autocorr,
    }


def corpus_features(
    texts: Sequence[str],
    window: int | None = 1000,
    features: Features = text_features,
) -> pd.DataFrame:
    """
    Вычисление признаков окон корпуса

    Описание:
        Каждый текст режется на окна (split_windows), для каждого окна считаются
        признаки; строки - окна с индексом (номер текста, номер окна), столбцы -
        признаки. Тексты без слов пропускаются

    Аргументы:
        texts (list[str]): Тексты корпуса
        window (int): Размер окна в словах; None - тексты целиком
        features (callable): Функция признаков текста; по умолчанию text_features

    Вывод:
        DataFrame: Признаки окон

    Исключения:
        SourceError: Если в корпусе нет слов
    """
    rows = {}
    for text_index, text in enumerate(texts):
        for window_index, chunk in enumerate(split_windows(text, window)):
            rows[text_index, window_index] = dict(features(chunk))
    if not rows:
        raise SourceError("В источнике данных отсутствуют слова")
    table = pd.DataFrame.from_dict(rows, orient="index").astype(float)
    table.index = pd.MultiIndex.from_tuples(table.index, names=["text", "window"])
    return table


def compare_corpora(
    a: Sequence[str],
    b: Sequence[str],
    window: int | None = 1000,
    features: Features | None = None,
    labels: tuple[str, str] = ("A", "B"),
    n_bootstrap: int = 1000,
    seed: int | None = 0,
) -> pd.DataFrame:
    """
    Сравнение двух корпусов по всем признакам текста

    Описание:
        Тексты обоих корпусов режутся на окна одинакового размера, чтобы убрать
        зависимость признаков от длины, для каждого окна считаются признаки
        (text_features или своя функция), для каждого признака сравниваются
        два набора значений: средние и медианы, разность медиан с перцентильным
        бутстрэп-интервалом 95%, d Коэна, дельта Клиффа, AUC признака как одиночного
        классификатора (доля пар окон, где значение в A больше, чем в B, ничьи
        за половину; дельта Клиффа равна 2·AUC − 1), U-критерий Манна-Уитни
        с двусторонним p-значением и поправкой Холма на число признаков.
        Неопределенные и бесконечные значения признака отбрасываются, при менее
        чем двух значениях на стороне статистики признака - nan. Строки отсортированы
        по убыванию модуля дельты Клиффа, признаки без статистик - в конце
        Один инструмент для атрибуции авторства, сравнения жанров и переводов,
        отличия сгенерированных текстов от человеческих; для отдельных слов
        то же делает keyness

    Ссылки:
        https://doi.org/10.1037/0033-2909.114.3.494
        https://en.wikipedia.org/wiki/Mann–Whitney_U_test

    Аргументы:
        a (list[str]): Тексты первого корпуса
        b (list[str]): Тексты второго корпуса
        window (int): Размер окна в словах; None - тексты целиком
        features (callable): Функция признаков текста; None - text_features
        labels (tuple[str, str]): Имена корпусов для столбцов (mean_<a>, ...)
        n_bootstrap (int): Число выборок бутстрэпа
        seed (int): Зерно генератора случайных чисел; None - случайное

    Вывод:
        DataFrame: Признаки × статистики сравнения (COMPARISON_COLUMNS
            с именами корпусов в столбцах)

    Исключения:
        SourceError: Если один из корпусов без слов
        ParameterError: Если число выборок меньше единицы
    """
    if n_bootstrap < 1:
        raise ParameterError("Число выборок бутстрэпа должно быть больше 0")
    feature_function = features or text_features
    table_a = corpus_features(a, window, feature_function)
    table_b = corpus_features(b, window, feature_function)
    rng = np.random.default_rng(seed)
    rows = {}
    for name in table_a.columns.union(table_b.columns, sort=False):
        rows[name] = compare_values(
            _finite(table_a, name), _finite(table_b, name), n_bootstrap, rng
        )
    result = pd.DataFrame.from_dict(rows, orient="index", columns=list(COMPARISON_COLUMNS))
    result["p_holm"] = holm_correction(result["p_value"].to_numpy())
    result = result.iloc[(-result["cliff_delta"].abs()).fillna(np.inf).argsort(kind="stable")]
    result[["n_a", "n_b"]] = result[["n_a", "n_b"]].astype(int)
    label_a, label_b = labels
    return result.rename(
        columns={
            "mean_a": f"mean_{label_a}",
            "mean_b": f"mean_{label_b}",
            "median_a": f"median_{label_a}",
            "median_b": f"median_{label_b}",
            "n_a": f"n_{label_a}",
            "n_b": f"n_{label_b}",
        }
    )


def _finite(table: pd.DataFrame, name: str) -> np.ndarray:
    if name not in table:
        return np.array([])
    values = table[name].to_numpy(dtype=float)
    return np.asarray(values[np.isfinite(values)], dtype=float)


def compare_values(
    values_a: np.ndarray,
    values_b: np.ndarray,
    n_bootstrap: int = 1000,
    rng: np.random.Generator | None = None,
) -> tuple[float, ...]:
    """
    Сравнение двух наборов значений признака

    Аргументы:
        values_a (ndarray): Конечные значения в первом корпусе
        values_b (ndarray): Конечные значения во втором корпусе
        n_bootstrap (int): Число выборок бутстрэпа
        rng (Generator): Генератор случайных чисел

    Вывод:
        tuple[float, ...]: Значения в порядке COMPARISON_COLUMNS, p_holm - nan
    """
    n_a, n_b = len(values_a), len(values_b)
    if n_a < 2 or n_b < 2:
        return (*(nan,) * 13, n_a, n_b)
    u, p_value = mannwhitneyu(values_a, values_b, alternative="two-sided")
    auc = float(u) / (n_a * n_b)
    ci_low, ci_high = bootstrap_median_diff(values_a, values_b, n_bootstrap, rng)
    return (
        float(values_a.mean()),
        float(values_b.mean()),
        float(np.median(values_a)),
        float(np.median(values_b)),
        float(np.median(values_a) - np.median(values_b)),
        ci_low,
        ci_high,
        calc_cohen_d(values_a, values_b),
        2 * auc - 1,
        auc,
        float(u),
        float(p_value),
        nan,
        n_a,
        n_b,
    )


def calc_cohen_d(values_a: Values, values_b: Values) -> float:
    """
    Вычисление d Коэна - стандартизированной разности средних

    Описание:
        (mean_a − mean_b) / s, где s - объединенное стандартное отклонение
        с выборочными дисперсиями (ddof=1); по Коэну 0.2 - малый эффект,
        0.5 - средний, 0.8 - большой

    Аргументы:
        values_a (list[float]): Значения в первом корпусе
        values_b (list[float]): Значения во втором корпусе

    Вывод:
        float: d Коэна, nan при менее чем двух значениях на стороне или нулевой
            дисперсии
    """
    a = np.asarray(values_a, dtype=float)
    b = np.asarray(values_b, dtype=float)
    if len(a) < 2 or len(b) < 2:
        return nan
    pooled = ((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2)
    if not pooled:
        return nan
    return float((a.mean() - b.mean()) / sqrt(pooled))


def calc_cliff_delta(values_a: Values, values_b: Values) -> float:
    """
    Вычисление дельты Клиффа - вероятностного размера эффекта

    Описание:
        Доля пар (x из A, y из B) с x > y минус доля пар с x < y (Cliff 1993);
        от −1 до 1, 0 - распределения не различаются; |δ| < 0.147 - пренебрежимый
        эффект, < 0.33 - малый, < 0.474 - средний, иначе большой (Romano и др. 2006)

    Аргументы:
        values_a (list[float]): Значения в первом корпусе
        values_b (list[float]): Значения во втором корпусе

    Вывод:
        float: Дельта Клиффа, nan для пустого набора
    """
    a = np.asarray(values_a, dtype=float)
    b = np.asarray(values_b, dtype=float)
    if not len(a) or not len(b):
        return nan
    comparison = np.sign(a[:, None] - b[None, :])
    return float(comparison.mean())


def bootstrap_median_diff(
    values_a: Values,
    values_b: Values,
    n_bootstrap: int = 1000,
    rng: np.random.Generator | None = None,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """
    Вычисление перцентильного бутстрэп-интервала разности медиан

    Описание:
        Оба набора пересэмплируются с возвращением n_bootstrap раз, для каждой
        пары выборок считается median_a − median_b, границы интервала - перцентили
        (1 − confidence) / 2 и 1 − (1 − confidence) / 2

    Аргументы:
        values_a (list[float]): Значения в первом корпусе
        values_b (list[float]): Значения во втором корпусе
        n_bootstrap (int): Число выборок
        rng (Generator): Генератор случайных чисел; None - новый без зерна
        confidence (float): Уровень доверия

    Вывод:
        tuple[float, float]: Нижняя и верхняя границы, nan для пустого набора
    """
    a = np.asarray(values_a, dtype=float)
    b = np.asarray(values_b, dtype=float)
    if not len(a) or not len(b):
        return nan, nan
    generator = rng if rng is not None else np.random.default_rng()
    medians_a = np.median(generator.choice(a, size=(n_bootstrap, len(a))), axis=1)
    medians_b = np.median(generator.choice(b, size=(n_bootstrap, len(b))), axis=1)
    differences = medians_a - medians_b
    tail = (1 - confidence) / 2 * 100
    low, high = np.percentile(differences, [tail, 100 - tail])
    return float(low), float(high)


def holm_correction(p_values: Sequence[float]) -> np.ndarray:
    """
    Поправка Холма на множественные сравнения

    Описание:
        p-значения сортируются по возрастанию, i-е умножается на (m − i + 1),
        где m - число определенных значений, затем берется накопленный максимум
        и ограничение единицей; nan остаются nan

    Аргументы:
        p_values (list[float]): p-значения

    Вывод:
        ndarray: Скорректированные p-значения в исходном порядке
    """
    values = np.asarray(p_values, dtype=float)
    adjusted = np.full(len(values), nan)
    defined = np.flatnonzero(~np.isnan(values))
    if not len(defined):
        return adjusted
    order = defined[np.argsort(values[defined], kind="stable")]
    m = len(order)
    scaled = values[order] * (m - np.arange(m))
    adjusted[order] = np.minimum(np.maximum.accumulate(scaled), 1.0)
    return adjusted
