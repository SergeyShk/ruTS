from collections.abc import Mapping, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform

from ..corpus.stylometry import frequency_table, mendenhall_curve, z_scores
from ..exceptions import SourceError


def dendrogram_plot(distances: pd.DataFrame, method: str = "ward", ax: Axes | None = None) -> Axes:
    """
    Построение дендрограммы по матрице расстояний между текстами

    Описание:
        Иерархическая кластеризация scipy по матрице расстояний (delta); метод
        Уорда по умолчанию, как в stylo и у Evert и др. (2015), подписи листьев -
        имена текстов из индекса

    Аргументы:
        distances (DataFrame): Симметричная матрица расстояний с именами текстов
        method (str): Метод объединения кластеров scipy.cluster.hierarchy.linkage
        ax (Axes): Оси для графика; если не заданы, создается новая фигура

    Вывод:
        Axes: Оси с дендрограммой

    Исключения:
        SourceError: Если матрица не квадратная, текстов меньше двух или есть
            бесконечные расстояния
    """
    values = _distance_matrix(distances, "дендрограммы")
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 0.4 * len(distances) + 1.5))
    condensed = squareform(values, checks=False)
    dendrogram(
        linkage(condensed, method=method), labels=list(distances.index), orientation="right", ax=ax
    )
    ax.set_xlabel("Расстояние")
    ax.set_title("Кластеризация текстов")
    return ax


def pca_plot(
    corpus: Mapping[str, Sequence[str]],
    n_mfw: int | None = 100,
    culling: float = 0.0,
    ax: Axes | None = None,
) -> Axes:
    """
    Построение диаграммы главных компонент по частотам самых частых единиц

    Описание:
        Метод главных компонент по z-оценкам относительных частот (frequency_table,
        z_scores) через сингулярное разложение, как pca.visualization в stylo:
        тексты на плоскости двух первых компонент с подписями, в подписях осей -
        доля объясненной дисперсии

    Аргументы:
        corpus (dict[str, list[str]]): Единицы текстов по именам текстов
        n_mfw (int): Число самых частых единиц; None - все
        culling (float): Наименьшая доля текстов, в которых встречается единица
        ax (Axes): Оси для графика; если не заданы, создается новая фигура

    Вывод:
        Axes: Оси с диаграммой

    Исключения:
        SourceError: Если текстов меньше трех
    """
    if len(corpus) < 3:
        raise SourceError("Для главных компонент нужно не меньше трех текстов")
    scores = z_scores(frequency_table(corpus, n_mfw, culling))
    values = scores.to_numpy(dtype=float)
    left, singular, _ = np.linalg.svd(values, full_matrices=False)
    components = left[:, :2] * singular[:2]
    if components.shape[1] < 2:
        components = np.hstack([components, np.zeros((len(components), 1))])
    variance = singular**2 / (singular**2).sum() if singular.any() else np.zeros(2)
    explained = list(variance[:2]) + [0.0] * (2 - min(len(variance), 2))
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(components[:, 0], components[:, 1], color="tab:blue")
    for name, (x, y) in zip(scores.index, components, strict=True):
        ax.annotate(str(name), (x, y), xytext=(4, 4), textcoords="offset points")
    ax.axhline(0, color="gray", linewidth=0.5)
    ax.axvline(0, color="gray", linewidth=0.5)
    ax.set_xlabel(f"Компонента 1 ({explained[0]:.1%})")
    ax.set_ylabel(f"Компонента 2 ({explained[1]:.1%})")
    ax.set_title("Главные компоненты")
    return ax


def mds_plot(distances: pd.DataFrame, ax: Axes | None = None) -> Axes:
    """
    Построение диаграммы многомерного шкалирования по матрице расстояний

    Описание:
        Классическое многомерное шкалирование (Torgerson 1952): двойное
        центрирование матрицы квадратов расстояний и два главных собственных
        вектора; тексты на плоскости с подписями, расстояния между точками
        приближают расстояния матрицы (delta)

    Аргументы:
        distances (DataFrame): Симметричная матрица расстояний с именами текстов
        ax (Axes): Оси для графика; если не заданы, создается новая фигура

    Вывод:
        Axes: Оси с диаграммой

    Исключения:
        SourceError: Если матрица не квадратная, текстов меньше двух или есть
            бесконечные расстояния
    """
    squared = _distance_matrix(distances, "шкалирования") ** 2
    n_texts = len(squared)
    centering = np.eye(n_texts) - np.ones((n_texts, n_texts)) / n_texts
    gram = -0.5 * centering @ squared @ centering
    eigenvalues, eigenvectors = np.linalg.eigh(gram)
    order = np.argsort(eigenvalues)[::-1][:2]
    coordinates = eigenvectors[:, order] * np.sqrt(np.clip(eigenvalues[order], 0, None))
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(coordinates[:, 0], coordinates[:, 1], color="tab:blue")
    for name, (x, y) in zip(distances.index, coordinates, strict=True):
        ax.annotate(str(name), (x, y), xytext=(4, 4), textcoords="offset points")
    ax.axhline(0, color="gray", linewidth=0.5)
    ax.axvline(0, color="gray", linewidth=0.5)
    ax.set_xlabel("Измерение 1")
    ax.set_ylabel("Измерение 2")
    ax.set_title("Многомерное шкалирование")
    return ax


def _distance_matrix(distances: pd.DataFrame, purpose: str) -> np.ndarray:
    values = np.asarray(distances.to_numpy(dtype=float), dtype=float)
    if values.ndim != 2 or values.shape[0] != values.shape[1] or len(values) < 2:
        raise SourceError(f"Для {purpose} нужна квадратная матрица не меньше чем из двух текстов")
    if not np.isfinite(values).all():
        raise SourceError(f"Для {purpose} все расстояния должны быть конечными")
    return values


def mendenhall_plot(corpus: Mapping[str, Sequence[str]], ax: Axes | None = None) -> Axes:
    """
    Построение кривых Менденхолла нескольких текстов

    Описание:
        Доли слов по длине в символах (mendenhall_curve) для каждого текста
        на одном графике - сравнение профилей авторов

    Аргументы:
        corpus (dict[str, list[str]]): Слова текстов по именам текстов
        ax (Axes): Оси для графика; если не заданы, создается новая фигура

    Вывод:
        Axes: Оси с кривыми

    Исключения:
        SourceError: Если текстов нет
    """
    if not corpus:
        raise SourceError("В корпусе нет текстов")
    curves = {name: mendenhall_curve(words) for name, words in corpus.items()}
    if ax is None:
        _, ax = plt.subplots()
    for name, curve in curves.items():
        ax.plot(list(curve), list(curve.values()), marker=".", label=str(name))
    ax.set_xlabel("Длина слова, символов")
    ax.set_ylabel("Доля слов")
    ax.set_title("Кривые Менденхолла")
    ax.legend()
    return ax
