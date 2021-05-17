from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Dict

import pandas as pd
from graphviz import Digraph

from ruts import SentsExtractor, WordsExtractor


class Direction(Enum):
    Forward = 1
    Backward = 2


@dataclass
class FreqNode:
    freq: int
    children: Dict[str, "FreqNode"]


class TreeDrawer:
    def __init__(
        self, keyword, fwd_tree, bwd_tree, max_font_size=30, min_font_size=12, font_interp=None
    ):
        self.max_font_size = max_font_size
        self.min_font_size = min_font_size
        self.keyword = keyword
        self.fwd_tree = fwd_tree
        self.bwd_tree = bwd_tree
        self.max_freq = max(
            [t.freq for t in fwd_tree.children.values()]
            + [t.freq for t in bwd_tree.children.values()]
        )
        self.font_interp = None
        self.graph = Digraph(keyword, format="png")
        self.graph.attr("graph", rankdir="LR")
        self.graph.attr("node", shape="plaintext", margin="0")

    def interpolate_fontsize(self, freq):
        lower = self.min_font_size
        upper = self.max_font_size
        t = freq / self.max_freq

        def quad(t):
            return t ** (1.0 / 3)

        font_interp = quad if self.font_interp is None else self.font_interp
        return int(font_interp(t) * (upper - lower) + lower)

    def draw_subtree(self, tree, direction, root, suffix, depth):
        if depth > 0:
            fontsize = self.interpolate_fontsize(tree.freq)
            self.graph.node(root + suffix, label=root, fontsize=str(fontsize))
        for word, subtree in tree.children.items():
            new_suffix = "{}-{}".format(suffix, word)
            self.draw_subtree(subtree, direction, word, new_suffix, depth + 1)
            src = root if depth == 0 else root + suffix
            dst = word + new_suffix
            if direction == Direction.Forward:
                self.graph.edge(src, dst)
            else:
                self.graph.edge(dst, src)

    def draw(self):
        self.graph.node(self.keyword, label=self.keyword, fontsize=str(self.max_font_size))
        self.draw_subtree(self.bwd_tree, Direction.Backward, self.keyword, "-bwd", 0)
        self.draw_subtree(self.fwd_tree, Direction.Forward, self.keyword, "-fwd", 0)
        return self.graph


class WordTree(object):
    def __init__(
        self,
        texts,
        keyword,
        max_n=5,
        max_per_n=8,
        sents_extractor: SentsExtractor = None,
        words_extractor: WordsExtractor = None,
    ):
        self.texts = texts
        self.keyword = keyword
        self.max_n = max_n
        self.max_per_n = max_per_n
        if not sents_extractor:
            self.sents_extractor = SentsExtractor()
        else:
            self.sents_extractor = sents_extractor
        if not words_extractor:
            self.words_extractor = WordsExtractor()
        else:
            self.words_extractor = words_extractor
        self.ngrams = []
        self.frequencies = []

    def search(self):
        frequencies_dict = defaultdict(int)
        for text in texts:
            for sent in self.sents_extractor.extract(text):
                print(sent)
                tokens = self.words_extractor.extract(sent)
                print(tokens)
                for n in range(2, self.max_n + 1):
                    for i in range(0, len(tokens) - n + 1):
                        ngram = tokens[i : i + n]
                        if ngram[0] == self.keyword or ngram[-1] == self.keyword:
                            frequencies_dict[tuple(ngram)] += 1
        for ngram, freq in frequencies_dict.items():
            self.ngrams.append(ngram)
            self.frequencies.append(freq)

    @staticmethod
    def build_tree(ngrams, frequencies):
        tree = FreqNode(freq=0, children={})
        for ngram, freq in zip(ngrams, frequencies):
            subtree = tree
            for gram in ngram:
                if gram not in subtree.children:
                    subtree.children[gram] = FreqNode(children={}, freq=freq)
                subtree = subtree.children[gram]
            subtree.freq = freq
        return tree

    def build_trees(self):
        forward_ngrams, forward_frequencies = [], []
        backward_ngrams, backward_frequencies = [], []
        for ngram, freq in zip(self.ngrams, self.frequencies):
            forward = ngram[0] == self.keyword
            backward = ngram[-1] == self.keyword
            if forward:
                forward_ngrams.append(ngram[1:])
                forward_frequencies.append(freq)
            if backward:
                backward_ngrams.append(reversed(ngram[:-1]))
                backward_frequencies.append(freq)
        forward_tree = self.build_tree(forward_ngrams, forward_frequencies)
        backward_tree = self.build_tree(backward_ngrams, backward_frequencies)
        return forward_tree, backward_tree

    def draw(self, **kwargs):
        df = pd.DataFrame(
            [
                {
                    "ngram": ngram,
                    "n": len(ngram),
                    "forward": ngram[0] == self.keyword,
                    "freq": freq,
                }
                for ngram, freq in zip(self.ngrams, self.frequencies)
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
        # return fwd_tree, bwd_tree
        # self.forward_tree, self.backward_tree = self.build_both_trees()
        # return


def wordtree(texts, keyword, max_n=5, max_per_n=8, words_extractor=None, **kwargs):
    # ngrams, frequencies = search(texts, keyword, max_n=max_n, tokenizer=tokenizer)
    # return draw(keyword, ngrams, frequencies, **kwargs)
    wt = WordTree(
        texts, keyword, max_n=max_n, max_per_n=max_per_n, words_extractor=words_extractor
    )
    wt.search()
    if not wt.ngrams:
        raise ValueError("Ключевое слово не найдено")
    return wt.draw()


if __name__ == "__main__":
    import tempfile

    from ruts.datasets import StalinWorks

    sw = StalinWorks()
    # texts = list(itertools.chain(*[SentsExtractor(text).extract() for text in sw.get_texts(limit=50)]))
    texts = [text for text in sw.get_texts(limit=50)]
    # wt = WordTree(texts, "масса", max_n=5, max_per_n=8)
    # wt.search()
    # print(wt.build_trees())
    g = wordtree(texts, "масса", max_n=5)
    g.view(tempfile.mktemp(".gv"))
