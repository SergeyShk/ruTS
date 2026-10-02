"""Графики ядра подписываются по-русски, заданные подписи ложатся поверх русских"""

from collections import Counter

import matplotlib
import matplotlib.pyplot as plt
import pytest

from ruts.corpus.keyness import Keyword
from ruts.exceptions import ParameterError
from ruts.visualizers import heaps_plot, keyness_plot, sentence_lengths_plot, zipf

matplotlib.use("Agg")

WORDS = ["мама", "мыла", "раму", "мама", "мыла", "мама"]
COUNTER = Counter(WORDS)
STRONG = [Keyword("кот", 3, 0, 1.0, 0.0, 1.0, 0.5, 1.0, 2.0)]
WEAK = [Keyword("пёс", 1, 3, 1.0, 0.0, 1.0, 0.5, 1.0, -2.0)]


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


def test_russian_labels_by_default():
    ax = zipf(COUNTER)
    assert (ax.get_title(), ax.get_xlabel()) == ("Закон Ципфа", "Ранк слова")
    assert sentence_lengths_plot([3, 5, 4]).get_title() == "Длины предложений"


def test_labels_over_the_russian_ones():
    ax = zipf(COUNTER, labels={"title": "Ципф"})
    assert (ax.get_title(), ax.get_xlabel()) == ("Ципф", "Ранк слова")
    # labels можно передать и позиционно
    assert heaps_plot(WORDS, None, {"title": "Хипс"}).get_title() == "Хипс"
    with pytest.raises(ParameterError):
        zipf(COUNTER, labels={"unknown": "x"})
    with pytest.raises(ParameterError):
        zipf(COUNTER, labels="Ципф")


def test_keyness_legend():
    legend = keyness_plot(STRONG, WEAK).get_legend()
    assert [text.get_text() for text in legend.get_texts()] == [
        "целевой корпус",
        "эталонный корпус",
    ]
    legend = keyness_plot(STRONG, WEAK, labels=("свой", "чужой")).get_legend()
    assert [text.get_text() for text in legend.get_texts()] == ["свой", "чужой"]
    assert keyness_plot(STRONG, labels={"title": "Ключи"}).get_title() == "Ключи"
    with pytest.raises(ParameterError):
        keyness_plot(STRONG, WEAK, labels=("свой",))
