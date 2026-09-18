from collections.abc import Iterable, Sequence
from numbers import Integral

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from razdel import sentenize
from spacy.tokens import Doc

from ..exceptions import ParameterError, SourceError, SourceTypeError
from ..utils import iter_doc_words, iter_text_words


def sentence_lengths_plot(
    source: str | Doc | Iterable[int],
    window: int = 10,
    inset: bool = True,
    ax: Axes | None = None,
) -> Axes:
    """
    Построение кривой длин предложений

    Описание:
        Длина каждого предложения в словах по порядку текста, скользящее среднее
        по окну из window предложений и врезка с гистограммой длин - ритм текста;
        предложения и слова строки извлекаются razdel (слова относятся
        к предложению по позиции), объекта Doc - по границам предложений,
        готовый список длин используется как есть

    Аргументы:
        source (str|Doc|Iterable[int]): Текст, объект Doc или длины предложений
            (список, массив numpy, Series)
        window (int): Окно скользящего среднего в предложениях
        inset (bool): Показывать врезку с гистограммой
        ax (Axes): Оси для графика; если не заданы, создается новая фигура

    Вывод:
        Axes: Оси с графиком

    Исключения:
        SourceTypeError: Если источник данных некорректен
        ParameterError: Если окно меньше единицы
        SourceError: Если предложений нет
    """
    if window < 1:
        raise ParameterError("Окно должно быть не меньше единицы")
    lengths = sentence_lengths(source)
    if not lengths:
        raise SourceError("В источнике данных отсутствуют предложения")
    if ax is None:
        _, ax = plt.subplots(figsize=(9, 4))
    numbers = np.arange(1, len(lengths) + 1)
    ax.plot(numbers, lengths, marker=".", linewidth=1, color="tab:blue", label="Длина предложения")
    if len(lengths) >= window:
        average = np.convolve(lengths, np.ones(window) / window, mode="valid")
        ax.plot(
            numbers[window - 1 :] - (window - 1) / 2,
            average,
            linewidth=2,
            color="tab:red",
            label=f"Скользящее среднее ({window})",
        )
    ax.set_xlabel("Номер предложения")
    ax.set_ylabel("Слов в предложении")
    ax.set_title("Длины предложений")
    ax.legend(loc="upper left")
    if inset:
        ax.set_ylim(top=max(lengths) * 1.7)
        histogram = ax.inset_axes((0.7, 0.62, 0.28, 0.33))
        histogram.hist(lengths, bins="auto", color="tab:gray")
        histogram.set_title("Распределение", fontsize=8)
        histogram.tick_params(labelsize=7)
    return ax


def count_words_by_spans(starts: Sequence[int], spans: Sequence[tuple[int, int]]) -> list[int]:
    """
    Число слов в каждом отрезке текста по позициям слов и границам отрезков

    Аргументы:
        starts (list[int]): Позиции первых символов слов по порядку
        spans (list[tuple[int, int]]): Границы отрезков по порядку - начало и позиция
            за концом

    Вывод:
        list[int]: Число слов в каждом отрезке; отрезки без слов пропускаются
    """
    lengths = []
    index = 0
    for start, stop in spans:
        count = 0
        while index < len(starts) and starts[index] < stop:
            count += starts[index] >= start
            index += 1
        lengths.append(count)
    return [length for length in lengths if length]


def sentence_lengths(source: str | Doc | Iterable[int]) -> list[int]:
    """
    Извлечение длин предложений в словах

    Аргументы:
        source (str|Doc|Iterable[int]): Текст, объект Doc или готовые длины -
            любая последовательность целых чисел, в том числе массив numpy и Series

    Вывод:
        list[int]: Длины предложений по порядку; предложения без слов пропускаются

    Исключения:
        SourceTypeError: Если источник данных некорректен
    """
    if isinstance(source, str):
        starts = [start for start, _, _ in iter_text_words(source)]
        spans = [(sent.start, sent.stop) for sent in sentenize(source)]
        return count_words_by_spans(starts, spans)
    if isinstance(source, Doc):
        if source.has_annotation("SENT_START"):
            lengths = [sum(1 for _ in iter_doc_words(sent)) for sent in source.sents]
            return [length for length in lengths if length]
        return sentence_lengths(source.text)
    if isinstance(source, Iterable):
        lengths = list(source)
        if all(isinstance(length, Integral) for length in lengths):
            return [int(length) for length in lengths]
    raise SourceTypeError("Некорректный источник данных")
