from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any

import pandas as pd
from graphviz import Digraph, nohtml

from ..exceptions import ParameterError, SourceError, SourceTypeError
from ..utils import check_sequence


class Direction(Enum):
    Forward = 1
    Backward = 2


@dataclass
class FreqNode:
    freq: int
    children: dict[str, "FreqNode"]


class TreeDrawer:
    """
    Класс для отображения дерева слов

    Аргументы:
        keyword (str): Ключевое слово, по которому ищется контекст
        fwd_tree (FreqNode): Поддерево после ключевого слова
        bwd_tree (FreqNode): Поддерево до ключевого слова
        max_font_size (int): Максимальный размер шрифта
        min_font_size (int): Минимальный размер шрифта
        font_interp (Callable): Функция интерполяции шрифта

    Атрибуты:
        max_freq (int): Максимальная частота встречаемости
        graph (Digraph): Двунаправленный граф

    Методы:
        interpolate_fontsize: Вычисление размера шрифта для узла дерева
        draw_subtree: Отображение поддерева слов
        draw: Отображение дерева слов в виде двунаправленного графа
    """

    def __init__(
        self,
        keyword: str,
        fwd_tree: FreqNode,
        bwd_tree: FreqNode,
        max_font_size: int = 30,
        min_font_size: int = 12,
        font_interp: Callable[[float], float] | None = None,
    ) -> None:
        self.keyword = keyword
        self.fwd_tree = fwd_tree
        self.bwd_tree = bwd_tree
        self.max_font_size = max_font_size
        self.min_font_size = min_font_size
        self.font_interp = font_interp
        self.max_freq = max(
            [t.freq for t in fwd_tree.children.values()]
            + [t.freq for t in bwd_tree.children.values()]
        )
        self.graph = Digraph(nohtml(keyword), format="png")
        self.graph.attr("graph", rankdir="LR")
        self.graph.attr("node", shape="plaintext", margin="0")

    def interpolate_fontsize(self, freq: int) -> int:
        """
        Вычисление размера шрифта для узла дерева

        Аргументы:
            freq (int): Частота встречаемости n-грамы

        Вывод:
            fontsize (int): Размер шрифта
        """
        lower = self.min_font_size
        upper = self.max_font_size
        t = freq / self.max_freq

        def quad(t: float) -> float:
            return float(t ** (1.0 / 3))

        font_interp = quad if self.font_interp is None else self.font_interp
        return int(font_interp(t) * (upper - lower) + lower)

    def draw_subtree(
        self, tree: FreqNode, direction: Direction, root: str, suffix: str, depth: int
    ) -> None:
        """
        Отображение поддерева слов

        Аргументы:
            tree (FreqNode): Поддерево слов
            direction (Direction): Направление поддерева
            root (str): Корневое слово
            suffix (str): Суффикс поддерева слов
            depth (int): Глубина поддерева слов
        """
        if depth > 0:
            fontsize = self.interpolate_fontsize(tree.freq)
            self.graph.node(nohtml(root + suffix), label=nohtml(root), fontsize=str(fontsize))
        for word, subtree in tree.children.items():
            new_suffix = f"{suffix}-{word}"
            self.draw_subtree(subtree, direction, word, new_suffix, depth + 1)
            src = root if depth == 0 else root + suffix
            dst = word + new_suffix
            if direction == Direction.Forward:
                self.graph.edge(nohtml(src), nohtml(dst))
            else:
                self.graph.edge(nohtml(dst), nohtml(src))

    def draw(self) -> Digraph:
        """
        Отображение дерева слов в виде двунаправленного графа

        Вывод:
            plot (Digraph): Дерево слов
        """
        self.graph.node(
            nohtml(self.keyword), label=nohtml(self.keyword), fontsize=str(self.max_font_size)
        )
        self.draw_subtree(self.bwd_tree, Direction.Backward, self.keyword, "-bwd", 0)
        self.draw_subtree(self.fwd_tree, Direction.Forward, self.keyword, "-fwd", 0)
        return self.graph


class WordTree:
    """
    Класс для построения дерева слов

    Аргументы:
        texts (list[list[str]]): Список списков слов
        keyword (str): Ключевое слово, по которому ищется контекст
        max_n (int): Максимальный размер контекста
        max_per_n (int): Максимальное число примеров для каждого размера контекста

    Атрибуты:
        ngrams (list[str]): Список n-грам
        frequencies (list[int]): Список частот встречаемости n-грам

    Методы:
        search: Построение списков n-грам и их встречаемостей по ключевому слову
        build_tree: Построение поддерева слов
        build_trees: Построение поддеревьев слов до ключевого слова и после него
        draw: Отображение дерева слов в виде двунаправленного графа

    Исключения:
        SourceTypeError: Если передаваемое значение не является списком списков
    """

    def __init__(
        self,
        texts: list[list[str]],
        keyword: str,
        max_n: int = 5,
        max_per_n: int = 8,
    ):
        check_sequence(texts, "списков слов")
        if not all(isinstance(text, (list, tuple)) for text in texts):
            raise SourceTypeError("Тексты должны быть представлены в виде списка списков слов")
        if not texts:
            raise SourceError("В источнике данных отсутствуют слова")
        if max_n < 2:
            raise ParameterError("Размер контекста должен быть не меньше 2")
        if max_per_n < 1:
            raise ParameterError(
                "Число примеров для каждого размера контекста должно быть больше 0"
            )
        self.texts = texts
        self.keyword = keyword
        self.max_n = max_n
        self.max_per_n = max_per_n
        self.ngrams: list[tuple[str, ...]] = []
        self.frequencies: list[int] = []

    def search(self) -> None:
        """
        Построение списков n-грам и их встречаемостей по ключевому слову
        """
        frequencies_dict: defaultdict[tuple[str, ...], int] = defaultdict(int)
        for sent in self.texts:
            for n in range(2, self.max_n + 1):
                for i in range(0, len(sent) - n + 1):
                    ngram = sent[i : i + n]
                    if ngram[0] == self.keyword or ngram[-1] == self.keyword:
                        frequencies_dict[tuple(ngram)] += 1
        for found_ngram, freq in frequencies_dict.items():
            self.ngrams.append(found_ngram)
            self.frequencies.append(freq)

    @staticmethod
    def build_tree(ngrams: Sequence[Sequence[str]], frequencies: Sequence[int]) -> FreqNode:
        """
        Построение поддерева слов

        Аргументы:
            ngrams (Sequence[Sequence[str]]): Список n-грам
            frequencies (Sequence[int]): Список частот встречаемости n-грам

        Вывод:
            tree (FreqNode): Поддерево слов
        """
        tree = FreqNode(freq=0, children={})
        for ngram, freq in zip(ngrams, frequencies, strict=False):
            subtree = tree
            for gram in ngram:
                if gram not in subtree.children:
                    subtree.children[gram] = FreqNode(children={}, freq=freq)
                subtree = subtree.children[gram]
            subtree.freq = freq
        return tree

    def build_trees(self) -> tuple[FreqNode, FreqNode]:
        """
        Построение поддеревьев слов до ключевого слова и после него

        Вывод:
            trees (tuple[FreqNode, FreqNode]): Поддеревья слов
        """
        forward_ngrams: list[Sequence[str]] = []
        forward_frequencies: list[int] = []
        backward_ngrams: list[Sequence[str]] = []
        backward_frequencies: list[int] = []
        for ngram, freq in zip(self.ngrams, self.frequencies, strict=False):
            forward = ngram[0] == self.keyword
            backward = ngram[-1] == self.keyword
            if forward:
                forward_ngrams.append(ngram[1:])
                forward_frequencies.append(freq)
            if backward:
                backward_ngrams.append(list(reversed(ngram[:-1])))
                backward_frequencies.append(freq)
        forward_tree = self.build_tree(forward_ngrams, forward_frequencies)
        backward_tree = self.build_tree(backward_ngrams, backward_frequencies)
        return forward_tree, backward_tree

    def draw(self, **kwargs: Any) -> Digraph:
        """
        Отображение дерева слов в виде двунаправленного графа

        Вывод:
            plot (Digraph): Дерево слов
        """
        df = pd.DataFrame(
            [
                {
                    "ngram": ngram,
                    "n": len(ngram),
                    "forward": ngram[0] == self.keyword,
                    "freq": freq,
                }
                for ngram, freq in zip(self.ngrams, self.frequencies, strict=False)
            ]
        )
        filtered_df = (
            df.sort_values("freq", ascending=False)
            .groupby(["forward", "n"])
            .head(self.max_per_n)
            .reset_index()
        )
        self.ngrams = filtered_df.ngram.tolist()
        self.frequencies = filtered_df.freq.tolist()
        forward_tree, backward_tree = self.build_trees()
        td = TreeDrawer(self.keyword, forward_tree, backward_tree, **kwargs)
        return td.draw()


def wordtree(
    texts: list[list[str]], keyword: str, max_n: int = 5, max_per_n: int = 8, **kwargs: Any
) -> Digraph:
    """
    Построение дерева слов, отображающее контекст для заданного ключевого слова в тексте

    Аргументы:
        texts (list[list[str]]): Список списков слов
        keyword (str): Ключевое слово, по которому ищется контекст
        max_n (int): Максимальные размер контекста
        max_per_n (int): Максимальное число примеров для каждого размера контекста
        kwargs: Параметры отрисовки TreeDrawer - max_font_size, min_font_size, font_interp

    Вывод:
        plot (Digraph): Дерево слов

    Исключения:
        SourceTypeError: Если тексты не список списков слов
        SourceError: Если текстов нет или ключевое слово не найдено ни в одном из них
        ParameterError: Если размер контекста меньше 2 или число примеров меньше единицы
    """
    wt = WordTree(
        texts,
        keyword,
        max_n=max_n,
        max_per_n=max_per_n,
    )
    wt.search()
    if not wt.ngrams:
        raise SourceError("Ключевое слово не найдено")
    return wt.draw(**kwargs)
