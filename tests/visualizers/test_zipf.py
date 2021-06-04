from typing import Counter

import matplotlib.pyplot as plt
import pytest
from matplotlib.lines import Line2D

from ruts.visualizers import zipf, zipf_theory


@pytest.fixture(scope="module")
def tokens():
    return Counter({"а": 100, "б": 75, "в": 50, "г": 25})


def test_zipf_theory():
    plt.cla()
    plot = zipf_theory(10, 5, 1.0)[0]
    assert isinstance(plot, Line2D)
    assert plot._label == "Теоретический закон"
    assert plot.get_linewidth() == 2
    assert plot.get_color() == "r"


def test_zipf_type_error():
    with pytest.raises(TypeError):
        zipf(1)


def test_zipf(tokens):
    plt.cla()
    plot = zipf(tokens)
    assert isinstance(plot, Line2D)
    assert plot._label == "Экспериментальный закон"
    assert plot.axes.title.get_text() == "Закон Ципфа"
    assert plot.axes.title.get_position() == (0.5, 1.0)


def test_zipf_num_words(tokens):
    plt.cla()
    plot = zipf(tokens, num_words=2)
    assert len(plot.get_data()[0]) == 2


def test_zipf_log(tokens):
    plt.cla()
    plot = zipf(tokens, log=False)
    assert plot.axes.get_xscale() == "linear"
    assert plot.axes.get_yscale() == "linear"


def test_zipf_num_labels(tokens):
    plt.cla()
    plot = zipf(tokens, num_labels=1)
    assert plot.axes.get_children()[1].get_text() == " а"
    assert plot.axes.get_children()[1].get_position() == (1, 100)


def test_zipf_show_theory(tokens):
    plt.cla()
    plot = zipf(tokens, show_theory=True)[0]
    assert plot.axes.get_children()[0]._label == "Экспериментальный закон"
    assert plot.axes.get_children()[1]._label == "Теоретический закон"


def test_zipf_with_theory(tokens):
    plt.cla()
    plot = zipf(tokens, show_theory=True)
    assert len(plot) == 1
    assert all(isinstance(p, Line2D) for p in plot)
