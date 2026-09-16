import matplotlib
import matplotlib.pyplot as plt
import pytest
from matplotlib.axes import Axes

from ruts.diversity_stats import calc_simpson_index
from ruts.visualizers import fingerprinting

matplotlib.use("Agg")


@pytest.fixture(scope="module")
def texts():
    return [["мама", "мыла", "раму"], ["шла", "Саша", "по", "Шоссе"]]


def test_fingerprinting_type_error():
    with pytest.raises(TypeError):
        fingerprinting(1)


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
