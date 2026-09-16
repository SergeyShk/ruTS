from math import inf, log2, nan

import matplotlib
import matplotlib.pyplot as plt
import pytest
from matplotlib.axes import Axes

from ruts.corpus import Collocation, Keyword, collocations, keyness
from ruts.visualizers import collocation_network, dispersion_plot, keyness_plot

matplotlib.use("Agg")

words = ["кот", "сидел", "на", "окне", "кот", "сидел", "на", "полу", "кот", "спал", "на", "окне"]
target = ["кот", "сидел", "на", "окне", "и", "смотрел", "на", "птиц", "кот", "уснул"]
reference = ["собака", "лежала", "на", "полу", "и", "спала", "собака", "ела"]


def test_dispersion_plot():
    ax = dispersion_plot(words, ["кот", "окне", "собака"])
    assert isinstance(ax, Axes)
    assert [label.get_text() for label in ax.get_yticklabels()] == ["кот", "окне", "собака"]
    positions = [list(collection.get_positions()) for collection in ax.collections]
    assert positions == [[0, 4, 8], [3, 11], []]
    assert ax.get_xlim() == (0.0, 12.0)
    assert ax.get_ylim()[0] > ax.get_ylim()[1]
    assert ax.get_title() == "Лексическая дисперсия"
    _, given = plt.subplots()
    assert dispersion_plot(words, ["кот"], ax=given) is given
    with pytest.raises(ValueError):
        dispersion_plot([], ["кот"])
    with pytest.raises(ValueError):
        dispersion_plot(words, [])
    plt.close("all")


def test_keyness_plot():
    positive = keyness(target, reference)
    negative = keyness(target, reference, positive=False)
    ax = keyness_plot(positive, negative, top_n=3, labels=("кот", "собака"))
    assert isinstance(ax, Axes)
    labels = [label.get_text() for label in ax.get_yticklabels()]
    assert labels[:3] == [keyword.word for keyword in positive[:3]]
    assert labels[3:] == [keyword.word for keyword in negative[:3]][::-1]
    widths = [patch.get_width() for patch in ax.patches]
    assert widths[:3] == [keyword.score for keyword in positive[:3]]
    assert widths[3:] == [keyword.score for keyword in negative[:3]][::-1]
    assert all(width < 0 for width in widths[3:])
    assert [text.get_text() for text in ax.get_legend().get_texts()] == ["кот", "собака"]
    assert ax.get_title() == "Ключевые слова"
    assert ax.get_xlabel() == "|score|"
    ax = keyness_plot(positive)
    assert len(ax.patches) == len(positive)
    assert [text.get_text() for text in ax.get_legend().get_texts()] == ["целевой корпус"]
    undefined = [Keyword("а", 1, 0, 1.0, 0.0, 1.0, 0.5, 1.0, nan)]
    infinite = [Keyword("б", 1, 0, 1.0, 0.0, 1.0, 0.5, 1.0, inf)]
    assert len(keyness_plot(positive + undefined + infinite).patches) == len(positive)
    with pytest.raises(ValueError):
        keyness_plot([])
    with pytest.raises(ValueError):
        keyness_plot(undefined)
    with pytest.raises(ValueError):
        keyness_plot(positive, field="word")
    plt.close("all")


def test_keyness_plot_sides():
    positive = keyness(target, reference, measure="odds_ratio")
    negative = keyness(target, reference, measure="odds_ratio", positive=False)
    ax = keyness_plot(positive, negative, top_n=2, log=True)
    widths = [patch.get_width() for patch in ax.patches]
    assert widths[:2] == [pytest.approx(abs(log2(keyword.score))) for keyword in positive[:2]]
    assert (
        widths[2:] == [pytest.approx(-abs(log2(keyword.score))) for keyword in negative[:2]][::-1]
    )
    assert ax.get_xlabel() == "|log2(score)|"
    ax = keyness_plot(positive, negative, top_n=2, field="log_ratio")
    widths = [patch.get_width() for patch in ax.patches]
    assert widths[:2] == [abs(keyword.log_ratio) for keyword in positive[:2]]
    assert all(width < 0 for width in widths[2:])
    weak = [Keyword("а", 1, 0, 1.0, 0.0, 1.0, 0.5, 1.0, -2.0)]
    assert keyness_plot(weak, weak).patches[0].get_width() == 2.0
    assert keyness_plot(weak, weak).patches[1].get_width() == -2.0
    plt.close("all")


def test_collocation_network():
    found = collocations(words, window=2)
    graph = collocation_network(found, top_n=3)
    assert graph.engine == "neato"
    assert graph.source.count("--") == 3
    assert '"кот" [fontsize=24]' in graph.source
    assert '"сидел" [fontsize=10]' in graph.source
    assert "label=13.00 penwidth=4.00" in graph.source
    assert graph.source.count("penwidth=0.50") == 2
    assert collocation_network(found).source.count("--") == len(found)
    single = collocation_network([Collocation("а", "б", 1, 1, 1, nan)])
    assert "label=0.00 penwidth=2.25" in single.source
    assert '"а" [fontsize=17]' in single.source
    with pytest.raises(ValueError):
        collocation_network([])
