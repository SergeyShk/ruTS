from collections import Counter
from collections.abc import Sequence
from math import log2, nan, sqrt
from typing import NamedTuple

import numpy as np


class Dispersion(NamedTuple):
    """
    Дисперсия слова по частям текста

    Атрибуты:
        word (str): Слово
        freq (int): Частота слова
        dp (float): Отклонение пропорций DP Гриса: 0 - равномерно, 1 - в одной части
        dp_norm (float): DP, нормированное на наибольшее возможное значение
        juilland_d (float): D Жюйана: 1 - равномерно, 0 - в одной части
        carroll_d2 (float): D2 Кэрролла: 1 - равномерно, 0 - в одной части
        rosengren_s (float): S Розенгрена: 1 - равномерно, стремится к 0 при скоплении
        kl_divergence (float): Дивергенция Кульбака-Лейблера в битах: 0 - равномерно
    """

    word: str
    freq: int
    dp: float
    dp_norm: float
    juilland_d: float
    carroll_d2: float
    rosengren_s: float
    kl_divergence: float


def dispersion(
    words: Sequence[str],
    parts: int | Sequence[int] = 10,
    word: str | None = None,
    min_freq: int = 1,
) -> list[Dispersion]:
    """
    Вычисление дисперсии слов по частям текста

    Описание:
        Текст делится на части: parts - число частей примерно равного размера
        или размеры частей по порядку (предложения, абзацы, главы), в сумме равные
        числу слов. Для каждого слова считаются частоты по частям и меры дисперсии
        по Gries (2008, 2020): DP и нормированное DP, D Жюйана, D2 Кэрролла,
        S Розенгрена и дивергенция Кульбака-Лейблера; Gries рекомендует DP
        Слова сравниваются как есть: регистр и лемматизация - на стороне извлечения

    Ссылки:
        https://www.stgries.info/research/2020_STG_Dispersion_PHCL.pdf
        https://www.stgries.info/research/2008_STG_Dispersion_IJCL.pdf

    Аргументы:
        words (list[str]): Слова текста по порядку
        parts (int|list[int]): Число частей или размеры частей
        word (str): Слово, дисперсия которого нужна; None - все слова
        min_freq (int): Минимальная частота слова

    Вывод:
        list[Dispersion]: Дисперсия слов по убыванию частоты; для слова, которого
            нет в тексте, - нулевая частота и nan

    Исключения:
        ValueError: Если частей меньше двух или больше слов, или размеры частей
            не совпадают с текстом
    """
    sizes = _sizes(len(words), parts)
    total = Counter(words)
    targets = [word] if word is not None else [w for w, f in total.most_common() if f >= min_freq]
    vocabulary = {target: index for index, target in enumerate(targets)}
    ids = np.fromiter((vocabulary.get(w, -1) for w in words), dtype=np.int64, count=len(words))
    part_ids = np.repeat(np.arange(len(sizes), dtype=np.int64), sizes)
    known = ids >= 0
    cells, counts = np.unique(ids[known] * len(sizes) + part_ids[known], return_counts=True)
    measures = _cell_measures(
        cells // len(sizes),
        cells % len(sizes),
        counts.astype(float),
        len(targets),
        np.asarray(sizes, dtype=float),
    )
    return [
        Dispersion(target, int(total[target]), *(float(column[index]) for column in measures))
        for index, target in enumerate(targets)
    ]


def _sizes(n_words: int, parts: int | Sequence[int]) -> list[int]:
    if isinstance(parts, int):
        if not 2 <= parts <= n_words:
            raise ValueError("Частей должно быть не меньше двух и не больше числа слов")
        return [len(part) for part in np.array_split(np.arange(n_words), parts)]
    sizes = [int(size) for size in parts]
    if len(sizes) < 2 or sum(sizes) != n_words or min(sizes) < 1:
        raise ValueError("Размеры частей должны быть положительными и в сумме давать число слов")
    return sizes


def _cell_measures(
    rows: np.ndarray, cols: np.ndarray, values: np.ndarray, n_words: int, sizes: np.ndarray
) -> tuple[np.ndarray, ...]:
    """
    Меры дисперсии для всех слов по ненулевым ячейкам матрицы «слово × часть»

    Описание:
        Векторный расчет тех же мер, что calc_dp, calc_dp_norm, calc_juilland_d,
        calc_carroll_d2, calc_rosengren_s и calc_kl_divergence, по разреженному
        представлению: rows и cols - номера слова и части ненулевой ячейки, values -
        частота в ней; память линейна по числу ячеек, а не слов на части. Нулевые
        ячейки дают в DP слагаемое s_i, в энтропии, дивергенции и S Розенгрена ноль,
        среднее и дисперсия для D Жюйана считаются по суммам и суммам квадратов;
        слова с нулевой частотой дают nan

    Аргументы:
        rows (ndarray): Номера слов ненулевых ячеек
        cols (ndarray): Номера частей ненулевых ячеек
        values (ndarray): Частоты в ячейках
        n_words (int): Число слов
        sizes (ndarray): Размеры частей

    Вывод:
        tuple[ndarray, ...]: Массивы DP, DP_norm, D, D2, S и дивергенции по словам
    """
    shares = sizes / sizes.sum()
    n_parts = len(sizes)
    cell_shares = shares[cols]

    def by_word(weights: np.ndarray) -> np.ndarray:
        return np.bincount(rows, weights=weights, minlength=n_words)

    totals = by_word(values)
    proportions = values / totals[rows]
    dp = 0.5 * (1 + by_word(np.abs(proportions - cell_shares) - cell_shares))
    dp_norm = dp / (1 - shares.min())
    relative = values / sizes[cols]
    mean = by_word(relative) / n_parts
    variance = np.maximum(by_word(relative**2) / n_parts - mean**2, 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        juilland = 1 - np.sqrt(variance) / mean / sqrt(n_parts - 1)
        probabilities = relative / (mean * n_parts)[rows]
        carroll = -by_word(probabilities * np.log2(probabilities)) / log2(n_parts)
        rosengren = by_word(np.sqrt(cell_shares * values)) ** 2 / totals
        kl = by_word(proportions * np.log2(proportions / cell_shares))
    empty = totals == 0
    return tuple(
        np.where(empty, nan, measure)
        for measure in (dp, dp_norm, juilland, carroll, rosengren, kl)
    )


def _proportions(
    frequencies: Sequence[int], sizes: Sequence[int]
) -> tuple[np.ndarray, np.ndarray]:
    counts = np.asarray(frequencies, dtype=float)
    shares = np.asarray(sizes, dtype=float)
    shares = shares / shares.sum()
    return counts, shares


def calc_dp(frequencies: Sequence[int], sizes: Sequence[int]) -> float:
    """
    Вычисление отклонения пропорций DP

    Описание:
        По Gries (2008): 0.5 · Σ |v_i / f − s_i|, где v_i - частота слова в части i,
        f - частота слова, s_i - доля части в тексте; 0 - слово распределено
        пропорционально размерам частей, стремится к 1 - сосредоточено в одной части

    Аргументы:
        frequencies (list[int]): Частоты слова по частям
        sizes (list[int]): Размеры частей

    Вывод:
        float: DP, nan для слова с нулевой частотой
    """
    counts, shares = _proportions(frequencies, sizes)
    total = counts.sum()
    if not total:
        return nan
    return float(0.5 * np.abs(counts / total - shares).sum())


def calc_dp_norm(frequencies: Sequence[int], sizes: Sequence[int]) -> float:
    """
    Вычисление нормированного отклонения пропорций DP_norm

    Описание:
        По Lijffijt и Gries (2012): DP / (1 − min(s_i)), чтобы наибольшее значение
        равнялось единице при любом делении на части

    Аргументы:
        frequencies (list[int]): Частоты слова по частям
        sizes (list[int]): Размеры частей

    Вывод:
        float: DP_norm, nan для слова с нулевой частотой
    """
    _, shares = _proportions(frequencies, sizes)
    return calc_dp(frequencies, sizes) / (1 - float(shares.min()))


def calc_juilland_d(frequencies: Sequence[int], sizes: Sequence[int]) -> float:
    """
    Вычисление D Жюйана

    Описание:
        По Juilland и Chang-Rodríguez (1964) в записи Gries (2008): 1 − V / sqrt(n − 1),
        где V - коэффициент вариации (отношение стандартного отклонения к среднему)
        относительных частот слова по частям v_i / n_i, n - число частей;
        1 - равномерно, 0 - в одной части

    Аргументы:
        frequencies (list[int]): Частоты слова по частям
        sizes (list[int]): Размеры частей

    Вывод:
        float: D, nan для слова с нулевой частотой
    """
    counts, _ = _proportions(frequencies, sizes)
    if not counts.sum():
        return nan
    relative = counts / np.asarray(sizes, dtype=float)
    variation = relative.std() / relative.mean()
    return float(1 - variation / sqrt(len(sizes) - 1))


def calc_carroll_d2(frequencies: Sequence[int], sizes: Sequence[int]) -> float:
    """
    Вычисление D2 Кэрролла

    Описание:
        По Carroll (1970): энтропия распределения относительных частот слова
        по частям p_i = v_i / n_i, деленная на log2 числа частей;
        1 - равномерно, 0 - в одной части

    Аргументы:
        frequencies (list[int]): Частоты слова по частям
        sizes (list[int]): Размеры частей

    Вывод:
        float: D2, nan для слова с нулевой частотой
    """
    counts, _ = _proportions(frequencies, sizes)
    if not counts.sum():
        return nan
    relative = counts / np.asarray(sizes, dtype=float)
    probabilities = relative[relative > 0] / relative.sum()
    entropy = -float((probabilities * np.log2(probabilities)).sum())
    return entropy / log2(len(sizes))


def calc_rosengren_s(frequencies: Sequence[int], sizes: Sequence[int]) -> float:
    """
    Вычисление S Розенгрена

    Описание:
        По Rosengren (1971) в записи Gries (2008): (Σ sqrt(s_i · v_i))² / f;
        1 - слово распределено пропорционально размерам частей, стремится к 1/n
        при сосредоточении в одной из n равных частей

    Аргументы:
        frequencies (list[int]): Частоты слова по частям
        sizes (list[int]): Размеры частей

    Вывод:
        float: S, nan для слова с нулевой частотой
    """
    counts, shares = _proportions(frequencies, sizes)
    total = counts.sum()
    if not total:
        return nan
    return float(np.sqrt(shares * counts).sum() ** 2 / total)


def calc_kl_divergence(frequencies: Sequence[int], sizes: Sequence[int]) -> float:
    """
    Вычисление дивергенции Кульбака-Лейблера распределения слова по частям

    Описание:
        По Gries (2020): Σ (v_i / f) · log2((v_i / f) / s_i) - расхождение долей
        вхождений слова по частям с долями частей в тексте; 0 - пропорционально,
        растет при сосредоточении слова в малых частях

    Аргументы:
        frequencies (list[int]): Частоты слова по частям
        sizes (list[int]): Размеры частей

    Вывод:
        float: Дивергенция в битах, nan для слова с нулевой частотой
    """
    counts, shares = _proportions(frequencies, sizes)
    total = counts.sum()
    if not total:
        return nan
    mask = counts > 0
    observed = counts[mask] / total
    return float((observed * np.log2(observed / shares[mask])).sum())
