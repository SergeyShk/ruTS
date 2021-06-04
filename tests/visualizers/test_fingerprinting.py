import matplotlib.pyplot as plt
import pytest
from matplotlib.figure import Figure

from ruts.diversity_stats import calc_simpson_index
from ruts.visualizers import fingerprinting


@pytest.fixture(scope="module")
def texts():
    return [["мама", "мыла", "раму"], ["шла", "Саша", "по", "Шоссе"]]


def test_fingerprinting_type_error():
    with pytest.raises(TypeError):
        fingerprinting(1)


def test_fingerprinting(texts):
    plt.cla()
    plot = fingerprinting(texts, x_size=600, y_size=500)
    assert isinstance(plot, Figure)
    assert len(plot.axes) == 2
    assert plot.axes[0].title.get_text() == "Литературная дактилоскопия"
    assert plot.axes[0].title.get_position() == (0.5, 1.0)
    assert plot.axes[1]._label == "<colorbar>"
    assert plot.axes[0].get_xlim() == (-600.0, 600.0)
    assert plot.axes[0].get_ylim() == (-500.0, 500.0)


def test_fingerprinting_is_return(texts):
    plt.cla()
    plot = fingerprinting(texts, is_return=False)
    assert plot is None


def test_fingerprinting_metric(texts):
    plt.cla()
    plot = fingerprinting(texts, metric=calc_simpson_index)
    assert isinstance(plot, Figure)
