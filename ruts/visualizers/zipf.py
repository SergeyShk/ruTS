from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from scipy import special

from ..diversity_stats import fit_zipf_mandelbrot


def zipf(
    counter: Counter[str],
    num_words: int | None = None,
    num_labels: int = 10,
    log: bool = True,
    show_theory: bool = False,
    alpha: float = 1.5,
    show_fit: bool = False,
    ax: Axes | None = None,
) -> Axes:
    """
    Построение графика Закона Ципфа (Zipf's law) на основе справочника частотности слов

    Описание:
        Частоты слов по рангам; show_theory добавляет теоретическую кривую закона
        Ципфа с показателем alpha (zipf_theory), show_fit - кривую подгонки закона
        Ципфа-Мандельброта f(r) = C / (r + q)^s по частотам справочника
        (fit_zipf_mandelbrot)

    Аргументы:
        counter (Counter): Справочник частотности слов
        num_words (int): Количество самых частотных слов
        num_labels (int): Количество слов, отображаемых на графике
        log (bool): Использовать логарифмическую шкалу
        show_theory (bool): Отображать график теоретического Закона Ципфа
        alpha (float): Коэффициент α теоретического Закона Ципфа
        show_fit (bool): Отображать кривую подгонки закона Ципфа-Мандельброта
        ax (Axes): Оси для графика; если не заданы, создается новая фигура

    Вывод:
        Axes: Оси с графиком Закона Ципфа

    Исключения:
        TypeError: Если передаваемое значение не является объектом Counter
    """
    if not isinstance(counter, Counter):
        raise TypeError("Справочник частотности слов должен быть объектом Counter")
    if ax is None:
        _, ax = plt.subplots()
    top_frequency = counter.most_common(1)[0][1]
    if num_words:
        frequencies_by_token = dict(counter.most_common(num_words))
    else:
        frequencies_by_token = dict(counter)
        num_words = len(counter)
    counts = np.array(tuple(frequencies_by_token.values()))
    tokens = np.array(tuple(frequencies_by_token.keys()))
    ranks = np.arange(1, counts.size + 1)
    indices = counts.argsort()[::-1][:]
    frequencies = counts[indices]
    plot = ax.loglog if log else ax.plot
    plot(ranks, frequencies, marker=".", label="Экспериментальный закон")
    if num_labels > 0:
        for n in list(np.logspace(-0.5, np.log10(len(counts) - 1), num_labels).astype(int)):
            ax.text(
                ranks[n],
                frequencies[n],
                " " + tokens[indices[n]],
                verticalalignment="bottom",
                horizontalalignment="left",
            )
    ax.set_title("Закон Ципфа")
    ax.set_xlabel("Ранк слова")
    ax.set_ylabel("Частота слова")
    ax.grid()
    if show_theory:
        zipf_theory(top_frequency, num_words, alpha, ax=ax)
    if show_fit:
        fit = fit_zipf_mandelbrot(counter)
        if not np.isnan(fit.s):
            ax.plot(
                ranks,
                fit.c / (ranks + fit.q) ** fit.s,
                linewidth=2,
                color="g",
                linestyle="--",
                label=f"Ципф-Мандельброт: q={fit.q:.2f}, s={fit.s:.2f}",
            )
    if show_theory or show_fit:
        ax.legend()
    return ax


def zipf_theory(size: int, num_ranks: int, alpha: float = 1.5, ax: Axes | None = None) -> Axes:
    """
    Построение теоретического графика Закона Ципфа (Zipf's law) по заданным параметрам

    Аргументы:
        size (int): Количество слов
        num_ranks (int): Количество ранков слов
        alpha (float): Коэффициент α
        ax (Axes): Оси для графика; если не заданы, создается новая фигура

    Вывод:
        Axes: Оси с графиком теоретического Закона Ципфа
    """
    if ax is None:
        _, ax = plt.subplots()
    x = np.arange(1, num_ranks + 1)
    y = x ** (-alpha) / special.zetac(alpha)
    ax.plot(x, y / max(y) * size, linewidth=2, color="r", label="Теоретический закон")
    return ax
