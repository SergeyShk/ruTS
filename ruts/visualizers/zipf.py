from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from ..diversity_stats import fit_zipf_mandelbrot
from ..exceptions import ParameterError, SourceError, SourceTypeError


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
        num_words (int): Количество самых частотных слов; не больше размера справочника
        num_labels (int): Количество слов, отображаемых на графике
        log (bool): Использовать логарифмическую шкалу
        show_theory (bool): Отображать график теоретического Закона Ципфа
        alpha (float): Коэффициент α теоретического Закона Ципфа
        show_fit (bool): Отображать кривую подгонки закона Ципфа-Мандельброта
        ax (Axes): Оси для графика; если не заданы, создается новая фигура

    Вывод:
        Axes: Оси с графиком Закона Ципфа

    Исключения:
        SourceTypeError: Если передаваемое значение не является объектом Counter
        SourceError: Если справочник пуст
    """
    if not isinstance(counter, Counter):
        raise SourceTypeError("Справочник частотности слов должен быть объектом Counter")
    if not counter:
        raise SourceError("В источнике данных отсутствуют слова")
    if ax is None:
        _, ax = plt.subplots()
    top_frequency = counter.most_common(1)[0][1]
    num_words = min(num_words, len(counter)) if num_words else len(counter)
    frequencies_by_token = dict(counter.most_common(num_words))
    counts = np.array(tuple(frequencies_by_token.values()))
    tokens = np.array(tuple(frequencies_by_token.keys()))
    ranks = np.arange(1, counts.size + 1)
    indices = counts.argsort()[::-1][:]
    frequencies = counts[indices]
    plot = ax.loglog if log else ax.plot
    plot(ranks, frequencies, marker=".", label="Экспериментальный закон")
    if num_labels > 0:
        positions = (
            np.logspace(-0.5, np.log10(len(counts) - 1), num_labels).astype(int)
            if len(counts) > 1
            else np.zeros(1, dtype=int)
        )
        for n in np.unique(positions):
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

    Описание:
        Частота ранга r пропорциональна r^(-α), кривая нормирована так, что частота
        первого ранга равна size

    Вывод:
        Axes: Оси с графиком теоретического Закона Ципфа

    Исключения:
        ParameterError: Если число ранков меньше единицы или показатель не больше нуля
    """
    if num_ranks < 1:
        raise ParameterError("Количество ранков должно быть больше 0")
    if alpha <= 0:
        raise ParameterError("Показатель α должен быть больше 0")
    if ax is None:
        _, ax = plt.subplots()
    x = np.arange(1, num_ranks + 1)
    ax.plot(x, size * x ** (-alpha), linewidth=2, color="r", label="Теоретический закон")
    return ax
