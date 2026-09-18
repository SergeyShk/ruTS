from functools import partial

import matplotlib
import matplotlib.pyplot as plt
import pytest
from matplotlib.axes import Axes

from ruts.diversity_stats import calc_simpson_index
from ruts.exceptions import ParameterError, SourceTypeError
from ruts.visualizers import fingerprinting

matplotlib.use("Agg")


@pytest.fixture(scope="module")
def texts():
    return [["мама", "мыла", "раму"], ["шла", "Саша", "по", "Шоссе"]]


def test_fingerprinting_type_error(texts):
    with pytest.raises(TypeError):
        fingerprinting(1)
    with pytest.raises(SourceTypeError):
        fingerprinting(["мама мыла раму", ["шла", "Саша"]])
    with pytest.raises(SourceTypeError):
        fingerprinting("мама мыла раму")
    with pytest.raises(SourceTypeError):
        fingerprinting(texts, metric=42)
    for segment_len in (0, -1):
        with pytest.raises(ParameterError):
            fingerprinting(texts, segment_len=segment_len)
    assert plt.get_fignums() == []


def test_fingerprinting(texts):
    ax = fingerprinting(texts, x_size=600, y_size=500)
    assert isinstance(ax, Axes)
    assert len(ax.figure.axes) == 2
    assert ax.get_title() == "Литературная дактилоскопия"
    assert ax.figure.axes[1].get_label() == "<colorbar>"
    assert ax.get_xlim() == (-600.0, 600.0)
    assert ax.get_ylim() == (-500.0, 500.0)
    assert len(ax.patches) == 2
    plt.close("all")


def test_fingerprinting_ax(texts):
    _, given = plt.subplots()
    ax = fingerprinting(texts, ax=given)
    assert ax is given
    assert len(ax.figure.axes) == 2
    plt.close("all")


def test_fingerprinting_metric(texts):
    ax = fingerprinting(texts, metric=calc_simpson_index)
    assert isinstance(ax, Axes)
    plt.close("all")


def test_fingerprinting_callable_metric(texts):
    # любой вызываемый объект, а не только функция: partial, метод, класс
    by_length = partial(lambda segment, scale: scale * len(segment), scale=0.1)
    colors = [patch.get_facecolor() for patch in fingerprinting(texts, metric=by_length).patches]
    plt.close("all")
    ttr_colors = [patch.get_facecolor() for patch in fingerprinting(texts).patches]
    plt.close("all")
    assert len(set(ttr_colors)) == 1
    assert len(set(colors)) == 2
