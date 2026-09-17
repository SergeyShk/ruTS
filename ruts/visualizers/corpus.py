from collections import Counter
from collections.abc import Sequence
from math import isfinite, isnan, log2, nan

import matplotlib.pyplot as plt
from graphviz import Graph
from matplotlib.axes import Axes
from matplotlib.patches import Patch

from ..corpus.collocations import Collocation
from ..corpus.keyness import Keyword


def dispersion_plot(words: Sequence[str], targets: Sequence[str], ax: Axes | None = None) -> Axes:
    """
    Построение графика лексической дисперсии

    Описание:
        Строка на каждое слово из targets, штрих на позиции каждого его вхождения
        в текст (NLTK dispersion_plot, quanteda textplot_xray); слова сравниваются
        как есть - регистр и лемматизация на стороне экстрактора

    Аргументы:
        words (list[str]): Слова текста по порядку
        targets (list[str]): Слова, вхождения которых нужно показать
        ax (Axes): Оси для графика; если не заданы, создается новая фигура

    Вывод:
        Axes: Оси с графиком дисперсии

    Исключения:
        ValueError: Если слов или целевых слов нет
    """
    if not words or not targets:
        raise ValueError("В источнике данных отсутствуют слова")
    positions = [
        [index for index, word in enumerate(words) if word == target] for target in targets
    ]
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 0.4 * len(targets) + 1.5))
    ax.eventplot(
        positions,
        lineoffsets=range(len(targets)),
        linelengths=0.8,
        linewidths=0.8,
        colors="tab:blue",
    )
    ax.set_yticks(range(len(targets)), labels=list(targets))
    ax.invert_yaxis()
    ax.set_xlim(0, len(words))
    ax.set_xlabel("Позиция слова в тексте")
    ax.set_title("Лексическая дисперсия")
    return ax


def keyness_plot(
    positive: Sequence[Keyword],
    negative: Sequence[Keyword] = (),
    top_n: int = 20,
    labels: tuple[str, str] = ("целевой корпус", "эталонный корпус"),
    field: str = "score",
    log: bool = False,
    ax: Axes | None = None,
) -> Axes:
    """
    Построение диаграммы ключевых слов

    Описание:
        Расходящиеся горизонтальные столбцы (quanteda textplot_keyness): слова
        из positive вправо, из negative - влево, длина столбца - модуль значения
        поля field (score, g2, log_ratio), так что сторона задается списком, а не
        знаком меры; по top_n слов с каждой стороны, слова с неопределенным
        или бесконечным значением пропускаются. Для отношения шансов
        (score от 0 до бесконечности, единица - шансы равны) задайте log=True:
        откладывается модуль log2 значения, симметричный относительно единицы

    Аргументы:
        positive (list[Keyword]): Положительные ключевые слова (keyness)
        negative (list[Keyword]): Отрицательные ключевые слова (keyness с positive=False)
        top_n (int): Количество слов с каждой стороны
        labels (tuple[str, str]): Подписи легенды для целевого и эталонного корпусов
        field (str): Поле Keyword, значения которого откладываются
        log (bool): Откладывать log2 значения - для отношения шансов
        ax (Axes): Оси для графика; если не заданы, создается новая фигура

    Вывод:
        Axes: Оси с диаграммой

    Исключения:
        ValueError: Если ключевых слов нет, поле неизвестно или top_n меньше единицы
    """
    if field not in Keyword._fields[1:]:
        raise ValueError(f"Неизвестное поле ключевого слова: {field}")
    if top_n < 1:
        raise ValueError("Количество слов должно быть больше 0")
    top = _bars(positive, field, log, 1)[:top_n]
    bottom = _bars(negative, field, log, -1)[:top_n]
    keywords = top + bottom[::-1]
    if not keywords:
        raw = list(positive) + list(negative)
        raise ValueError(
            "В источнике данных отсутствуют слова" if not raw else "Мера не определена"
        )
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 0.3 * len(keywords) + 1.5))
    rows = range(len(keywords))
    colors = ["tab:blue"] * len(top) + ["tab:red"] * len(bottom)
    ax.barh(rows, [value for _, value in keywords], color=colors)
    ax.set_yticks(rows, labels=[keyword.word for keyword, _ in keywords])
    ax.invert_yaxis()
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel(f"|log2({field})|" if log else f"|{field}|")
    ax.set_title("Ключевые слова")
    handles = []
    legend_labels = []
    if top:
        handles.append(Patch(color="tab:blue"))
        legend_labels.append(labels[0])
    if bottom:
        handles.append(Patch(color="tab:red"))
        legend_labels.append(labels[1])
    ax.legend(handles, legend_labels)
    return ax


def _bars(
    keywords: Sequence[Keyword], field: str, log: bool, sign: int
) -> list[tuple[Keyword, float]]:
    bars = []
    for keyword in keywords:
        value = float(getattr(keyword, field))
        if log:
            value = log2(value) if value > 0 else nan
        if isfinite(value):
            bars.append((keyword, sign * abs(value)))
    return bars


def collocation_network(collocations: Sequence[Collocation], top_n: int | None = None) -> Graph:
    """
    Построение сети коллокаций

    Описание:
        Неориентированный граф (quanteda textplot_network): узлы - слова,
        размер шрифта по частоте слова, ребра - пары с толщиной по значению
        меры и подписью; раскладка neato

    Аргументы:
        collocations (list[Collocation]): Коллокации (collocations)
        top_n (int): Количество пар с начала списка; None - все

    Вывод:
        Graph: Граф graphviz

    Исключения:
        ValueError: Если коллокаций нет или top_n меньше единицы
    """
    if top_n is not None and top_n < 1:
        raise ValueError("Количество пар должно быть больше 0")
    pairs = list(collocations)[:top_n] if top_n else list(collocations)
    if not pairs:
        raise ValueError("В источнике данных отсутствуют коллокации")
    frequencies: Counter[str] = Counter()
    for pair in pairs:
        frequencies[pair.left] = max(frequencies[pair.left], pair.freq_left)
        frequencies[pair.right] = max(frequencies[pair.right], pair.freq_right)
    scores = [pair.score for pair in pairs if not isnan(pair.score)]
    min_score, max_score = (min(scores), max(scores)) if scores else (0.0, 0.0)
    min_freq, max_freq = min(frequencies.values()), max(frequencies.values())
    graph = Graph("collocations", engine="neato")
    graph.attr("graph", overlap="false", splines="true")
    graph.attr("node", shape="plaintext", margin="0", fontname="Helvetica")
    graph.attr("edge", color="gray50", fontsize="9", fontname="Helvetica")
    for word, frequency in frequencies.items():
        graph.node(word, fontsize=f"{_scale(frequency, min_freq, max_freq, 10, 24):.0f}")
    for pair in pairs:
        score = 0.0 if isnan(pair.score) else pair.score
        graph.edge(
            pair.left,
            pair.right,
            label=f"{score:.2f}",
            penwidth=f"{_scale(score, min_score, max_score, 0.5, 4):.2f}",
        )
    return graph


def _scale(value: float, low: float, high: float, out_low: float, out_high: float) -> float:
    if high <= low:
        return (out_low + out_high) / 2
    return out_low + (value - low) / (high - low) * (out_high - out_low)
