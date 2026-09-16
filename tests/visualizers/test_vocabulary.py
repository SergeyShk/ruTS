import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes

from ruts.diversity_stats import fit_heaps, vocabulary_growth
from ruts.visualizers import frequency_spectrum_plot, heaps_plot

matplotlib.use("Agg")

words = ["кот", "сидел", "на", "окне", "кот", "сидел", "на", "полу", "кот", "спал", "на", "окне"]


def test_heaps_plot():
    ax = heaps_plot(words)
    assert isinstance(ax, Axes)
    growth, fit_line = ax.get_lines()
    assert list(growth.get_ydata()) == vocabulary_growth(words)
    fit = fit_heaps(words)
    assert fit_line.get_label() == f"K·N^β: K={fit.k:.2f}, β={fit.beta:.2f}"
    assert np.allclose(fit_line.get_ydata(), fit.k * np.arange(1, 13) ** fit.beta)
    assert ax.get_title() == "Закон Хипса"
    _, given = plt.subplots()
    assert heaps_plot(words, ax=given) is given
    with pytest.raises(ValueError):
        heaps_plot(["кот"])
    plt.close("all")


def test_frequency_spectrum_plot():
    ax = frequency_spectrum_plot(words)
    assert isinstance(ax, Axes)
    line = ax.get_lines()[0]
    assert list(line.get_xdata()) == [1, 2, 3]
    assert list(line.get_ydata()) == [2, 2, 2]
    assert ax.get_xscale() == "log"
    assert ax.get_title() == "Спектр частот"
    with pytest.raises(ValueError):
        frequency_spectrum_plot([])
    plt.close("all")
