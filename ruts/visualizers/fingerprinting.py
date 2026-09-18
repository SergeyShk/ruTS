from collections.abc import Callable, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from ..diversity_stats import calc_ttr
from ..exceptions import ParameterError, SourceTypeError
from ..utils import check_sequence


def fingerprinting(
    texts: list[list[str]],
    segment_len: int = 10,
    metric: Callable[[Sequence[str]], float] | None = None,
    x_size: int = 800,
    y_size: int = 600,
    cmap: str = "PuOr",
    ax: Axes | None = None,
) -> Axes:
    """
    Визуализация литературной дактилоскопии (Literature Fingerprinting)

    Описание:
        Каждый текст режется на сегменты по segment_len слов со скользящим шагом
        в десятую часть сегмента, для сегмента считается метрика лексического
        разнообразия, квадраты раскрашиваются по ее значению относительно
        наибольшего конечного; сегменты с неопределенной метрикой (nan
        на слишком коротких для нее сегментах) рисуются как нулевые

    Ссылки:
        https://www.uni-konstanz.de/mmsp/pubsys/publishedFiles/KeOe07.pdf

    Аргументы:
        texts (list[list[str]]): Список списков слов
        segment_len (int): Размер сегмента
        metric (callable): Функция для подсчета метрики лексического разнообразия
        x_size (int): Ширина области для визуализации
        y_size (int): Высота области для визуализации
        cmap (str): Цветовая карта
        ax (Axes): Оси для графика; если не заданы, создается фигура 15×10

    Вывод:
        Axes: Оси с визуализацией литературной дактилоскопии

    Исключения:
        SourceTypeError: Если тексты не список списков слов или метрика не вызываемый
            объект
        ParameterError: Если размер сегмента меньше единицы
    """
    check_sequence(texts, "списков слов")
    if not all(isinstance(text, (list, tuple)) for text in texts):
        raise SourceTypeError("Тексты должны быть представлены в виде списка списков слов")
    if metric is not None and not callable(metric):
        raise SourceTypeError("Метрика должна быть вызываемым объектом")
    if segment_len < 1:
        raise ParameterError("Размер сегмента должен быть больше 0")
    metrics = {}
    metric_func = metric if metric is not None else calc_ttr
    for i, text in enumerate(texts):
        start = 0
        end = segment_len
        window_len = int(0.1 * segment_len)
        if window_len == 0:
            window_len = 1
        n_words = len(text)
        segments = []
        while end <= n_words:
            segment = text[start:end]
            metric_value = metric_func(segment)
            segments.append(metric_value)
            start += window_len
            end += window_len
        final_segment = text[start:]
        segments.append(metric_func(final_segment))
        metrics[i] = segments

    if ax is None:
        _, ax = plt.subplots(figsize=(15, 10))
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    cmaps = plt.get_cmap(cmap)
    cmap_list = [cmaps(i) for i in range(cmaps.N)]
    cx = ax.imshow(cmap_list, interpolation="nearest", cmap=cmap, visible=None)
    ax.figure.colorbar(cx, ax=ax)
    x = -x_size + 30
    y = y_size - 50
    finite = [value for segments in metrics.values() for value in segments if np.isfinite(value)]
    max_metric = max(finite) if finite else 1.0
    n_cols = 0
    n_rows = 0
    for segments in metrics.values():
        n_segments = len(segments)
        n_cols = int(n_segments / 8) if (n_segments % 8) == 0 else int(n_segments / 8) + 1
        n_rows = 8 if n_cols > 1 else n_segments
        b = np.zeros((n_rows, n_cols))
        pos = 0
        for i in range(n_rows):
            for j in range(n_cols):
                if pos <= (n_segments - 1):
                    b[i][j] = segments[pos] if np.isfinite(segments[pos]) else 0
                    pos += 1
                else:
                    b[i][j] = 0
        tam_quad = 15
        x_max = x_size - 25
        margin = 25
        x_accum = n_cols * tam_quad
        if (x + x_accum + margin) > x_max:
            y = y - ((8 * tam_quad) + margin)
            x = -x_size + 25
        for i in range(n_rows):
            for j in range(n_cols):
                if b[i][j] == 0:
                    rect = Rectangle((x, y), tam_quad, tam_quad, color="Black")
                    ax.add_patch(rect)
                else:
                    rect = Rectangle((x, y), tam_quad, tam_quad, color=cmaps(b[i][j] / max_metric))
                    ax.add_patch(rect)
                x += tam_quad
            x -= n_cols * tam_quad
            y -= tam_quad
        x += (n_cols * tam_quad) + margin
        y += n_rows * tam_quad
    ax.set_xlim(-x_size, x_size)
    ax.set_ylim(-y_size, y_size)
    ax.set_title("Литературная дактилоскопия")
    return ax
