from collections import Counter

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes

from ruts.visualizers import zipf, zipf_theory

matplotlib.use("Agg")


@pytest.fixture(scope="module")
def tokens():
    return Counter({"а": 100, "б": 75, "в": 50, "г": 25})


def test_zipf_theory():
    ax = zipf_theory(10, 5, 1.0)
    assert isinstance(ax, Axes)
    line = ax.get_lines()[0]
    assert line.get_label() == "Теоретический закон"
    assert line.get_linewidth() == 2
    assert line.get_color() == "r"
    assert list(line.get_xdata()) == [1, 2, 3, 4, 5]
    assert list(line.get_ydata()) == pytest.approx([10, 5, 10 / 3, 2.5, 2])
    assert np.isfinite(zipf_theory(10, 5, 1.5).get_lines()[0].get_ydata()).all()
    plt.close("all")
    for num_ranks, alpha in ((0, 1.0), (5, 0.0), (5, -1.0)):
        with pytest.raises(ValueError):
            zipf_theory(10, num_ranks, alpha)
    assert plt.get_fignums() == []


def test_zipf_empty_and_overflow(tokens):
    plt.close("all")
    with pytest.raises(ValueError):
        zipf(Counter())
    assert plt.get_fignums() == []
    ax = zipf(tokens, num_words=100, num_labels=100, show_theory=True)
    assert all(len(line.get_xdata()) == 4 for line in ax.get_lines())
    assert len(ax.texts) == 4
    single = zipf(Counter({"а": 3}), num_labels=5)
    assert len(single.texts) == 1
    plt.close("all")


def test_zipf_type_error():
    with pytest.raises(TypeError):
        zipf(1)


def test_zipf(tokens):
    ax = zipf(tokens)
    assert isinstance(ax, Axes)
    line = ax.get_lines()[0]
    assert line.get_label() == "Экспериментальный закон"
    assert ax.get_title() == "Закон Ципфа"
    assert ax.get_xscale() == "log"
    assert len(ax.get_lines()) == 1
    plt.close("all")


def test_zipf_num_words(tokens):
    ax = zipf(tokens, num_words=2)
    assert len(ax.get_lines()[0].get_data()[0]) == 2
    plt.close("all")


def test_zipf_log(tokens):
    ax = zipf(tokens, log=False)
    assert ax.get_xscale() == "linear"
    assert ax.get_yscale() == "linear"
    plt.close("all")


def test_zipf_num_labels(tokens):
    ax = zipf(tokens, num_labels=1)
    assert ax.texts[0].get_text() == " а"
    assert ax.texts[0].get_position() == (1, 100)
    assert len(ax.texts) == 1
    plt.close("all")


def test_zipf_show_theory(tokens):
    ax = zipf(tokens, show_theory=True)
    labels = [line.get_label() for line in ax.get_lines()]
    assert labels == ["Экспериментальный закон", "Теоретический закон"]
    assert ax.get_legend() is not None
    plt.close("all")


def test_zipf_show_fit():
    ax = zipf(Counter({"а": 12, "б": 6, "в": 4, "г": 3}), show_fit=True, show_theory=True)
    labels = [line.get_label() for line in ax.get_lines()]
    assert labels[:2] == ["Экспериментальный закон", "Теоретический закон"]
    assert labels[2] == "Ципф-Мандельброт: q=0.00, s=1.00"
    assert ax.get_lines()[2].get_ydata()[0] == pytest.approx(12, rel=1e-3)
    assert len(zipf(Counter({"а": 2, "б": 1}), show_fit=True).get_lines()) == 1
    plt.close("all")


def test_zipf_ax(tokens):
    _, (left, right) = plt.subplots(1, 2)
    assert zipf(tokens, ax=left) is left
    assert zipf_theory(10, 5, ax=right) is right
    assert len(left.get_lines()) == 1
    assert len(right.get_lines()) == 1
    plt.close("all")
