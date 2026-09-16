from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from ..diversity_stats import calc_frequency_spectrum, fit_heaps, vocabulary_growth


def heaps_plot(words: Sequence[str], ax: Axes | None = None) -> Axes:
    """
    Построение графика закона Хипса - роста словаря с длиной текста

    Описание:
        Размер словаря V после каждого слова текста (vocabulary_growth) и кривая
        подгонки V(N) = K · N^β (fit_heaps) с параметрами в легенде

    Аргументы:
        words (list[str]): Слова текста по порядку
        ax (Axes): Оси для графика; если не заданы, создается новая фигура

    Вывод:
        Axes: Оси с графиком

    Исключения:
        ValueError: Если слов меньше двух
    """
    if len(words) < 2:
        raise ValueError("Для кривой роста словаря нужно не меньше двух слов")
    if ax is None:
        _, ax = plt.subplots()
    lengths = np.arange(1, len(words) + 1)
    ax.plot(lengths, vocabulary_growth(words), label="Рост словаря")
    fit = fit_heaps(words)
    ax.plot(
        lengths,
        fit.k * lengths**fit.beta,
        linestyle="--",
        color="r",
        label=f"K·N^β: K={fit.k:.2f}, β={fit.beta:.2f}",
    )
    ax.set_xlabel("Длина текста, слов")
    ax.set_ylabel("Размер словаря")
    ax.set_title("Закон Хипса")
    ax.grid()
    ax.legend()
    return ax


def frequency_spectrum_plot(words: Sequence[str], ax: Axes | None = None) -> Axes:
    """
    Построение спектра частот - числа лексем по частоте

    Описание:
        Число лексем V_m, встретившихся ровно m раз (calc_frequency_spectrum),
        в логарифмических координатах, как plot.spc в zipfR; левый край - гапаксы

    Аргументы:
        words (list[str]): Слова текста
        ax (Axes): Оси для графика; если не заданы, создается новая фигура

    Вывод:
        Axes: Оси с графиком

    Исключения:
        ValueError: Если слов нет
    """
    if not words:
        raise ValueError("В источнике данных отсутствуют слова")
    if ax is None:
        _, ax = plt.subplots()
    spectrum = calc_frequency_spectrum(words)
    frequencies = sorted(spectrum)
    ax.loglog(frequencies, [spectrum[m] for m in frequencies], marker="o", linestyle="")
    ax.set_xlabel("Частота лексемы m")
    ax.set_ylabel("Число лексем V(m)")
    ax.set_title("Спектр частот")
    ax.grid()
    return ax
