from typing import Counter

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from scipy import special


def zipf(
    counter: Counter,
    num_words: int = None,
    num_labels: int = 10,
    log: bool = True,
    show_theory: bool = False,
    alpha: float = 1.5,
) -> Line2D:
    """
    Построение графика Закона Ципфа (Zipf's law) на основе справочника частотности слов

    Аргументы:
        counter (Counter): Справочник частотности слов
        num_words (int): Количество самых частотных слов
        num_labels (int): Количество слов, отображаемых на графике
        log (bool): Использовать логарифмическую шкалу
        show_theory (bool): Отображать график теоретического Закону Ципфа
        alpha (float): Коэффициент α теоретического Закона Ципфа

    Вывод:
        plot (Line2D): График Закона Ципфа

    Исключения:
        TypeError: Если передаваемое значение не является объектом Counter
    """
    if not isinstance(counter, Counter):
        raise TypeError("Справочник частотности слов должен быть объектом Counter")
    top_frequency = counter.most_common(1)[0][1]
    if num_words:
        counter = dict(counter.most_common(num_words))
    else:
        num_words = len(counter)
    counts = np.array(tuple(counter.values()))
    tokens = np.array(tuple(counter.keys()))
    ranks = np.arange(1, counts.size + 1)
    indices = counts.argsort()[::-1][:]
    frequencies = counts[indices]
    if log:
        plot = plt.loglog(ranks, frequencies, marker=".", label="Экспериментальный закон")[0]
    else:
        plot = plt.plot(ranks, frequencies, marker=".", label="Экспериментальный закон")[0]
    if num_labels > 0:
        for n in list(np.logspace(-0.5, np.log10(len(counts) - 1), num_labels).astype(int)):
            plt.text(
                ranks[n],
                frequencies[n],
                " " + tokens[indices[n]],
                verticalalignment="bottom",
                horizontalalignment="left",
            )
    plt.title("Закон Ципфа")
    plt.xlabel("Ранк слова")
    plt.ylabel("Частота слова")
    plt.grid()
    if show_theory:
        plot = zipf_theory(top_frequency, num_words, alpha)
        plt.legend()
    return plot


def zipf_theory(size: int, num_ranks: int, alpha: float = 1.5) -> Line2D:
    """
    Построение теоретического графика Закона Ципфа (Zipf's law) по заданным параметрам

    Аргументы:
        size (int): Количество слов
        num_ranks (int): Количество ранков слов
        alpha (float): Коэффициент α

    Вывод:
        plot (Line2D): График теоретического Закона Ципфа
    """
    x = np.arange(1, num_ranks + 1)
    y = x ** (-alpha) / special.zetac(alpha)
    plot = plt.plot(x, y / max(y) * size, linewidth=2, color="r", label="Теоретический закон")
    return plot
