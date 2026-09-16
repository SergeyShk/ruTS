from collections import Counter
from collections.abc import Sequence
from math import log, log2, nan, sqrt
from typing import NamedTuple

from ..constants import COLLOCATION_MEASURES


class Collocation(NamedTuple):
    """
    Коллокация - пара слов с мерой ассоциации

    Атрибуты:
        left (str): Левое слово
        right (str): Правое слово, встречается в окне после левого
        freq_left (int): Частота левого слова
        freq_right (int): Частота правого слова
        freq_pair (int): Частота совместной встречаемости
        score (float): Значение выбранной меры
    """

    left: str
    right: str
    freq_left: int
    freq_right: int
    freq_pair: int
    score: float


def collocations(
    words: Sequence[str],
    window: int = 5,
    measure: str = "logdice",
    min_freq: int = 2,
    node: str | None = None,
    top_n: int | None = None,
) -> list[Collocation]:
    """
    Поиск коллокаций в последовательности слов

    Описание:
        Пары слов считаются упорядоченными, как в NLTK: правое слово встречается
        не дальше window слов после левого, каждая пара позиций учитывается один раз;
        window = 1 дает биграммы. Для пары считается выбранная мера ассоциации
        по частотам слов, частоте пары и числу слов N; в меру частота пары делится
        на размер окна (Church и Hanks 1990, так же в NLTK), чтобы ожидаемая частота
        не зависела от окна, а Dice и минимальная чувствительность не превышали
        единицы; в freq_pair записывается частота без деления
        Слова сравниваются как есть: регистр и лемматизация - на стороне извлечения

    Ссылки:
        https://www.sketchengine.eu/wp-content/uploads/ske-statistics.pdf
        https://www.nltk.org/api/nltk.metrics.association.html

    Аргументы:
        words (list[str]): Слова текста по порядку
        window (int): Наибольшее расстояние между словами пары
        measure (str): Мера из COLLOCATION_MEASURES
        min_freq (int): Минимальная частота пары
        node (str): Слово, коллокации которого нужны (слева или справа); None - все пары
        top_n (int): Количество коллокаций; None - все

    Вывод:
        list[Collocation]: Коллокации по убыванию меры и частоты пары, при равенстве -
            по алфавиту

    Исключения:
        ValueError: Если мера неизвестна или окно меньше единицы
    """
    if measure not in COLLOCATION_MEASURES:
        raise ValueError(f"Неизвестная мера ассоциации: {measure}")
    if window < 1:
        raise ValueError("Окно должно быть не меньше единицы")
    calc = MEASURES[measure]
    n_words = len(words)
    frequencies = Counter(words)
    pairs: Counter[tuple[str, str]] = Counter()
    for index, left in enumerate(words):
        for right in words[index + 1 : index + 1 + window]:
            if node is None or node in (left, right):
                pairs[left, right] += 1
    found = [
        Collocation(
            left,
            right,
            frequencies[left],
            frequencies[right],
            freq_pair,
            calc(frequencies[left], frequencies[right], freq_pair / window, n_words),
        )
        for (left, right), freq_pair in pairs.items()
        if freq_pair >= min_freq
    ]
    found.sort(
        key=lambda collocation: (
            -collocation.score,
            -collocation.freq_pair,
            collocation.left,
            collocation.right,
        )
    )
    return found[:top_n] if top_n else found


def calc_mi(freq_a: int, freq_b: int, freq_ab: float, n: int) -> float:
    """
    Вычисление взаимной информации MI

    Описание:
        log2(f_ab · N / (f_a · f_b)); завышает редкие пары

    Аргументы:
        freq_a (int): Частота первого слова
        freq_b (int): Частота второго слова
        freq_ab (float): Частота пары
        n (int): Число слов в тексте

    Вывод:
        float: MI, nan при нулевой частоте пары
    """
    if not freq_ab:
        return nan
    return log2(freq_ab * n / (freq_a * freq_b))


def calc_mi3(freq_a: int, freq_b: int, freq_ab: float, n: int) -> float:
    """
    Вычисление кубической взаимной информации MI³

    Описание:
        log2(f_ab³ · N / (f_a · f_b)); в отличие от MI, отдает предпочтение
        частым парам

    Аргументы:
        freq_a (int): Частота первого слова
        freq_b (int): Частота второго слова
        freq_ab (float): Частота пары
        n (int): Число слов в тексте

    Вывод:
        float: MI³, nan при нулевой частоте пары
    """
    if not freq_ab:
        return nan
    return log2(freq_ab**3 * n / (freq_a * freq_b))


def calc_t_score(freq_a: int, freq_b: int, freq_ab: float, n: int) -> float:
    """
    Вычисление t-критерия

    Описание:
        (f_ab − f_a · f_b / N) / sqrt(f_ab); отдает предпочтение частым парам

    Аргументы:
        freq_a (int): Частота первого слова
        freq_b (int): Частота второго слова
        freq_ab (float): Частота пары
        n (int): Число слов в тексте

    Вывод:
        float: t-критерий, nan при нулевой частоте пары
    """
    if not freq_ab:
        return nan
    return (freq_ab - freq_a * freq_b / n) / sqrt(freq_ab)


def calc_dice(freq_a: int, freq_b: int, freq_ab: float, n: int) -> float:
    """
    Вычисление коэффициента Дайса

    Описание:
        2 · f_ab / (f_a + f_b); не зависит от размера текста

    Аргументы:
        freq_a (int): Частота первого слова
        freq_b (int): Частота второго слова
        freq_ab (float): Частота пары
        n (int): Число слов в тексте (не используется)

    Вывод:
        float: Коэффициент Дайса
    """
    return 2 * freq_ab / (freq_a + freq_b)


def calc_logdice(freq_a: int, freq_b: int, freq_ab: float, n: int) -> float:
    """
    Вычисление logDice

    Описание:
        14 + log2(2 · f_ab / (f_a + f_b)) по Rychlý (2008); не зависит от размера
        текста, максимум 14, значения ниже нуля - слабая связь

    Ссылки:
        https://www.sketchengine.eu/glossary/logdice/

    Аргументы:
        freq_a (int): Частота первого слова
        freq_b (int): Частота второго слова
        freq_ab (float): Частота пары
        n (int): Число слов в тексте (не используется)

    Вывод:
        float: logDice, nan при нулевой частоте пары
    """
    if not freq_ab:
        return nan
    return 14 + log2(2 * freq_ab / (freq_a + freq_b))


def calc_log_likelihood(freq_a: int, freq_b: int, freq_ab: float, n: int) -> float:
    """
    Вычисление логарифма правдоподобия G² пары слов

    Описание:
        По таблице сопряженности 2×2 (Dunning 1993): наблюдаемые частоты f_ab,
        f_a − f_ab, f_b − f_ab, N − f_a − f_b + f_ab против ожидаемых при независимости,
        G² = 2 · Σ O · ln(O / E)

    Аргументы:
        freq_a (int): Частота первого слова
        freq_b (int): Частота второго слова
        freq_ab (float): Частота пары
        n (int): Число слов в тексте

    Вывод:
        float: G²
    """
    observed = (freq_ab, freq_a - freq_ab, freq_b - freq_ab, n - freq_a - freq_b + freq_ab)
    expected = (
        freq_a * freq_b / n,
        freq_a * (n - freq_b) / n,
        (n - freq_a) * freq_b / n,
        (n - freq_a) * (n - freq_b) / n,
    )
    return 2 * sum(o * log(o / e) for o, e in zip(observed, expected, strict=True) if o > 0)


def calc_npmi(freq_a: int, freq_b: int, freq_ab: float, n: int) -> float:
    """
    Вычисление нормированной взаимной информации NPMI

    Описание:
        MI / (−log2(f_ab / N)) по Bouma (2009); лежит в пределах от −1 до 1,
        единица - слова встречаются только вместе

    Аргументы:
        freq_a (int): Частота первого слова
        freq_b (int): Частота второго слова
        freq_ab (float): Частота пары
        n (int): Число слов в тексте

    Вывод:
        float: NPMI, nan при нулевой частоте пары или паре, равной тексту
    """
    if not freq_ab or freq_ab == n:
        return nan
    return calc_mi(freq_a, freq_b, freq_ab, n) / -log2(freq_ab / n)


def calc_min_sensitivity(freq_a: int, freq_b: int, freq_ab: float, n: int) -> float:
    """
    Вычисление минимальной чувствительности

    Описание:
        min(f_ab / f_a, f_ab / f_b) по Pedersen (1998); лежит в пределах от 0 до 1

    Аргументы:
        freq_a (int): Частота первого слова
        freq_b (int): Частота второго слова
        freq_ab (float): Частота пары
        n (int): Число слов в тексте (не используется)

    Вывод:
        float: Минимальная чувствительность
    """
    return min(freq_ab / freq_a, freq_ab / freq_b)


MEASURES = {
    "mi": calc_mi,
    "mi3": calc_mi3,
    "t_score": calc_t_score,
    "dice": calc_dice,
    "logdice": calc_logdice,
    "log_likelihood": calc_log_likelihood,
    "npmi": calc_npmi,
    "min_sensitivity": calc_min_sensitivity,
}
