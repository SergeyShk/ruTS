from collections import Counter
from collections.abc import Mapping, Sequence
from math import inf, isnan, log, log2, nan
from typing import Any, NamedTuple

import numpy as np
from scipy.stats import chi2 as chi2_distribution

from ..constants import KEYNESS_MEASURES
from ..datasets.freq2011 import CORPUS_SIZE, FreqDict
from ..utils import normalize_yo

ZERO_ADJUSTMENT = 0.5


class Keyword(NamedTuple):
    """
    Ключевое слово - результат сравнения частот в двух корпусах

    Атрибуты:
        word (str): Слово
        freq_target (int): Частота в целевом корпусе
        freq_reference (float): Частота в эталонном корпусе (по словарю - дробная)
        ipm_target (float): Частота в целевом корпусе на миллион слов
        ipm_reference (float): Частота в эталонном корпусе на миллион слов
        g2 (float): Логарифм правдоподобия G² со знаком направления
        p_value (float): p-значение G² по распределению хи-квадрат с одной степенью свободы
        log_ratio (float): Двоичный логарифм отношения нормированных частот
        score (float): Значение выбранной меры
    """

    word: str
    freq_target: int
    freq_reference: float
    ipm_target: float
    ipm_reference: float
    g2: float
    p_value: float
    log_ratio: float
    score: float


def keyness(
    target: Sequence[str] | Mapping[str, int],
    reference: Sequence[str] | Mapping[str, float] | FreqDict,
    measure: str = "log_likelihood",
    min_freq: int = 1,
    positive: bool = True,
    top_n: int | None = None,
) -> list[Keyword]:
    """
    Поиск ключевых слов целевого корпуса относительно эталонного

    Описание:
        Слова сравниваются по частотам в двух корпусах: для каждого слова считаются
        логарифм правдоподобия G² с p-значением (значимость различия) и Log Ratio
        (размер эффекта), как рекомендуют Gabrielatos и Hardie, а также выбранная
        мера score, по которой список сортируется. Меры значимости (G², хи-квадрат,
        BIC, ELL) получают знак: отрицательный, если слово чаще в эталоне
        Эталоном может быть частотный словарь FreqDict: тогда целевые слова должны
        быть леммами, они приводятся к нижнему регистру без буквы ё, как в словаре,
        частота в эталоне - ipm, умноженная на объем корпуса словаря (92 млн)
        Нулевая частота в одном из корпусов при расчете %DIFF, Log Ratio и отношения
        шансов заменяется на 0.5 (Hardie 2014)
        Положительные ключевые слова чаще в целевом корпусе, отрицательные -
        в эталонном; min_freq - наименьшая частота слова в том корпусе, где оно чаще

    Ссылки:
        https://ucrel.lancs.ac.uk/llwizard.html
        http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf
        http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/

    Аргументы:
        target (list[str]|dict[str, int]): Слова целевого корпуса или их частоты
        reference (list[str]|dict[str, float]|FreqDict): Слова эталонного корпуса,
            их частоты или частотный словарь
        measure (str): Мера из KEYNESS_MEASURES для score и сортировки
        min_freq (int): Минимальная частота ключевого слова в своем корпусе
        positive (bool): Положительные ключевые слова (True) или отрицательные (False)
        top_n (int): Количество ключевых слов; None - все

    Вывод:
        list[Keyword]: Ключевые слова по убыванию ключевости, при равенстве -
            по убыванию частоты и по алфавиту; слова с неопределенной мерой в конце

    Исключения:
        ValueError: Если мера неизвестна или один из корпусов пуст
    """
    if measure not in KEYNESS_MEASURES:
        raise ValueError(f"Неизвестная мера ключевости: {measure}")
    if isinstance(reference, FreqDict):
        counts_target = _count(target, normalize=True)
        size_reference = float(CORPUS_SIZE)
        counts_reference: Mapping[str, float] = {
            lemma: entry.ipm * size_reference / 1e6 for lemma, entry in reference.entries.items()
        }
    else:
        counts_target = _count(target)
        counts_reference = _count(reference)
        size_reference = float(sum(counts_reference.values()))
    size_target = float(sum(counts_target.values()))
    if not size_target or not size_reference:
        raise ValueError("В источнике данных отсутствуют слова")
    calc = MEASURES[measure]
    rows = []
    words = set(counts_target) | set(counts_reference)
    for word in words:
        a = counts_target.get(word, 0)
        b = counts_reference.get(word, 0)
        ipm_target = a / size_target * 1e6
        ipm_reference = b / size_reference * 1e6
        if ipm_target == ipm_reference or (ipm_target > ipm_reference) != positive:
            continue
        if (a if positive else b) < min_freq:
            continue
        rows.append(
            (
                word,
                int(a),
                b,
                ipm_target,
                ipm_reference,
                calc_log_likelihood(a, b, size_target, size_reference),
                calc_log_ratio(a, b, size_target, size_reference),
                calc(a, b, size_target, size_reference),
            )
        )
    p_values = calc_p_value(np.array([row[5] for row in rows]))
    keywords = [
        Keyword(*row[:6], float(p_value), *row[6:])
        for row, p_value in zip(rows, p_values, strict=True)
    ]
    sign = -1 if positive else 1
    keywords.sort(
        key=lambda keyword: (
            isnan(keyword.score),
            sign * (0.0 if isnan(keyword.score) else keyword.score),
            -(keyword.freq_target if positive else keyword.freq_reference),
            keyword.word,
        )
    )
    return keywords[:top_n] if top_n else keywords


def _count(
    words: Sequence[str] | Mapping[str, float], normalize: bool = False
) -> Mapping[str, float]:
    if not normalize:
        return words if isinstance(words, Mapping) else Counter(words)
    counts: dict[str, float] = {}
    if isinstance(words, Mapping):
        for word, count in words.items():
            counts[normalize_yo(word)] = counts.get(normalize_yo(word), 0) + count
        return counts
    return Counter(normalize_yo(word) for word in words)


def _sign(a: float, b: float, c: float, d: float) -> int:
    return 1 if a / c >= b / d else -1


def _adjust(a: float, b: float) -> tuple[float, float]:
    return a or ZERO_ADJUSTMENT, b or ZERO_ADJUSTMENT


def calc_log_likelihood(a: float, b: float, c: float, d: float) -> float:
    """
    Вычисление логарифма правдоподобия G² частот слова в двух корпусах

    Описание:
        По Rayson и Garside (2000): ожидаемые частоты E1 = c·(a + b)/(c + d)
        и E2 = d·(a + b)/(c + d), G² = 2·(a·ln(a/E1) + b·ln(b/E2)); слагаемое
        с нулевой частотой равно нулю. Критические значения - G2_CRITICAL_VALUES
        (3.84 для p < 0.05, 6.63 для p < 0.01, 10.83 для p < 0.001, 15.13 для p < 0.0001)
        Знак отрицательный, если слово чаще в эталоне

    Ссылки:
        https://ucrel.lancs.ac.uk/llwizard.html

    Аргументы:
        a (float): Частота слова в целевом корпусе
        b (float): Частота слова в эталонном корпусе
        c (float): Объем целевого корпуса
        d (float): Объем эталонного корпуса

    Вывод:
        float: Значение G² со знаком
    """
    total = a + b
    if not total:
        return 0.0
    expected_a = c * total / (c + d)
    expected_b = d * total / (c + d)
    value = 2 * (_xlog(a, expected_a) + _xlog(b, expected_b))
    return _sign(a, b, c, d) * value


def _xlog(observed: float, expected: float) -> float:
    return observed * log(observed / expected) if observed else 0.0


def calc_p_value(g2: float | np.ndarray) -> Any:
    """
    Вычисление p-значения по величине G² или хи-квадрат

    Аргументы:
        g2 (float|ndarray): Значение G² или хи-квадрат (знак не учитывается)
            или массив значений

    Вывод:
        float|ndarray: p-значение по распределению хи-квадрат с одной степенью свободы
    """
    p_value = chi2_distribution.sf(np.abs(g2), 1)
    return float(p_value) if np.isscalar(g2) else p_value


def calc_chi2(a: float, b: float, c: float, d: float) -> float:
    """
    Вычисление хи-квадрат с поправкой Йейтса для частот слова в двух корпусах

    Описание:
        Таблица сопряженности 2×2: слово и остальные слова в каждом корпусе,
        χ² = N·(|a·(d − b) − b·(c − a)| − N/2)² / ((a + b)·(c − a + d − b)·c·d), N = c + d
        Знак отрицательный, если слово чаще в эталоне

    Аргументы:
        a (float): Частота слова в целевом корпусе
        b (float): Частота слова в эталонном корпусе
        c (float): Объем целевого корпуса
        d (float): Объем эталонного корпуса

    Вывод:
        float: Значение хи-квадрат со знаком
    """
    total = c + d
    rest_a = c - a
    rest_b = d - b
    denominator = (a + b) * (rest_a + rest_b) * c * d
    if not denominator:
        return 0.0
    difference = max(abs(a * rest_b - b * rest_a) - total / 2, 0.0)
    return _sign(a, b, c, d) * total * difference**2 / denominator


def calc_diff(a: float, b: float, c: float, d: float) -> float:
    """
    Вычисление разности нормированных частот %DIFF

    Описание:
        По Gabrielatos и Marchi (2011): (NF_a − NF_b) / NF_b · 100, где NF - частота
        на миллион слов; нулевая частота заменяется на 0.5

    Аргументы:
        a (float): Частота слова в целевом корпусе
        b (float): Частота слова в эталонном корпусе
        c (float): Объем целевого корпуса
        d (float): Объем эталонного корпуса

    Вывод:
        float: %DIFF
    """
    a, b = _adjust(a, b)
    return (a / c - b / d) / (b / d) * 100


def calc_log_ratio(a: float, b: float, c: float, d: float) -> float:
    """
    Вычисление Log Ratio - двоичного логарифма отношения нормированных частот

    Описание:
        По Hardie (2014): log2(NF_a / NF_b); единица - слово вдвое чаще в целевом
        корпусе; нулевая частота заменяется на 0.5

    Ссылки:
        http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/

    Аргументы:
        a (float): Частота слова в целевом корпусе
        b (float): Частота слова в эталонном корпусе
        c (float): Объем целевого корпуса
        d (float): Объем эталонного корпуса

    Вывод:
        float: Log Ratio
    """
    a, b = _adjust(a, b)
    return log2((a / c) / (b / d))


def calc_bic(a: float, b: float, c: float, d: float) -> float:
    """
    Вычисление байесовского информационного критерия для G²

    Описание:
        По Wilson (2013): BIC = G² − ln(N), N = c + d; значения выше 2 - положительное
        свидетельство различия, выше 6 - сильное, выше 10 - очень сильное
        Знак как у G²

    Аргументы:
        a (float): Частота слова в целевом корпусе
        b (float): Частота слова в эталонном корпусе
        c (float): Объем целевого корпуса
        d (float): Объем эталонного корпуса

    Вывод:
        float: BIC со знаком
    """
    g2 = calc_log_likelihood(a, b, c, d)
    return _sign(a, b, c, d) * (abs(g2) - log(c + d))


def calc_ell(a: float, b: float, c: float, d: float) -> float:
    """
    Вычисление размера эффекта для логарифма правдоподобия ELL

    Описание:
        По Johnson, Culpeper и Rayson (2007): ELL = G² / (N · ln(min(E1, E2))),
        N = c + d; лежит в пределах от 0 до 1. Знак как у G²

    Аргументы:
        a (float): Частота слова в целевом корпусе
        b (float): Частота слова в эталонном корпусе
        c (float): Объем целевого корпуса
        d (float): Объем эталонного корпуса

    Вывод:
        float: ELL со знаком, nan при минимальной ожидаемой частоте не больше единицы
    """
    total = a + b
    expected_min = min(c, d) * total / (c + d)
    if expected_min <= 1:
        return nan
    return calc_log_likelihood(a, b, c, d) / ((c + d) * log(expected_min))


def calc_odds_ratio(a: float, b: float, c: float, d: float) -> float:
    """
    Вычисление отношения шансов слова в двух корпусах

    Описание:
        (a / (c − a)) / (b / (d − b)); единица - шансы равны, нулевая частота
        заменяется на 0.5

    Аргументы:
        a (float): Частота слова в целевом корпусе
        b (float): Частота слова в эталонном корпусе
        c (float): Объем целевого корпуса
        d (float): Объем эталонного корпуса

    Вывод:
        float: Отношение шансов; inf, если слово занимает весь целевой корпус,
            0, если весь эталонный, nan, если оба
    """
    a, b = _adjust(a, b)
    if a >= c and b >= d:
        return nan
    if a >= c:
        return inf
    if b >= d:
        return 0.0
    return (a / (c - a)) / (b / (d - b))


MEASURES = {
    "log_likelihood": calc_log_likelihood,
    "chi2": calc_chi2,
    "diff": calc_diff,
    "log_ratio": calc_log_ratio,
    "bic": calc_bic,
    "ell": calc_ell,
    "odds_ratio": calc_odds_ratio,
}
