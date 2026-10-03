from collections.abc import Callable, Mapping, Sequence

from anyts.visualizers.fingerprinting import fingerprinting as core_fingerprinting
from matplotlib.axes import Axes

from ._labels import russian_labels


def fingerprinting(
    texts: list[list[str]],
    segment_len: int = 10,
    metric: Callable[[Sequence[str]], float] | None = None,
    x_size: int = 800,
    y_size: int = 600,
    cmap: str = "PuOr",
    ax: Axes | None = None,
    labels: Mapping[str, str] | None = None,
) -> Axes:
    """
    Визуализация литературной дактилоскопии (Literature Fingerprinting)

    Описание:
        Каждый текст режется на сегменты по segment_len слов со скользящим шагом
        в десятую часть сегмента, для сегмента считается метрика лексического
        разнообразия; текст - блок квадратов, цвет - значение метрики от наименьшего
        до наибольшего конечного, неопределенные значения - светло-серые

    Ссылки:
        https://www.uni-konstanz.de/mmsp/pubsys/publishedFiles/KeOe07.pdf

    Аргументы:
        texts (list[list[str]]): Список списков слов
        segment_len (int): Размер сегмента
        metric (callable): Функция метрики лексического разнообразия; по умолчанию calc_ttr
        x_size (int): Половина ширины области визуализации
        y_size (int): Половина высоты области визуализации
        cmap (str): Цветовая карта
        ax (Axes): Оси для графика; если не заданы, создается фигура 15×10
        labels (dict[str, str]): Подписи поверх VISUALIZER_LABELS["fingerprinting"]

    Вывод:
        Axes: Оси с визуализацией литературной дактилоскопии

    Исключения:
        SourceTypeError: Если тексты не список списков слов или метрика не вызываемый
            объект
        SourceError: Если текстов нет или в тексте нет слов
        ParameterError: Если размер сегмента или размеры области некорректны
    """
    return core_fingerprinting(
        texts,
        segment_len,
        metric,
        x_size,
        y_size,
        cmap,
        ax,
        russian_labels("fingerprinting", labels),
    )
