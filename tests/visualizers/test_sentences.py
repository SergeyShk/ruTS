import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
import spacy
from matplotlib.axes import Axes

from ruts.visualizers import sentence_lengths, sentence_lengths_plot

matplotlib.use("Agg")

text = "Кот сидел на окне. Он смотрел на птиц, а птицы улетели. Кот уснул. Завтра он снова будет сидеть на окне."


def test_sentence_lengths():
    assert sentence_lengths(text) == [4, 7, 2, 7]
    assert sentence_lengths(spacy.blank("ru")(text)) == [4, 7, 2, 7]
    nlp = spacy.blank("ru")
    nlp.add_pipe("sentencizer")
    assert sentence_lengths(nlp(text)) == [4, 7, 2, 7]
    assert sentence_lengths([3, 5, 2]) == [3, 5, 2]
    assert sentence_lengths(np.array([3, 5, 2])) == [3, 5, 2]
    assert sentence_lengths(pd.Series([3, 5, 2])) == [3, 5, 2]
    assert sentence_lengths((np.int64(3), np.int32(5))) == [3, 5]
    assert sentence_lengths(iter([3, 5])) == [3, 5]
    assert sentence_lengths("") == []
    with pytest.raises(TypeError):
        sentence_lengths(["кот", "спал"])
    with pytest.raises(TypeError):
        sentence_lengths([3.5, 2])
    with pytest.raises(TypeError):
        sentence_lengths(42)


def test_sentence_lengths_plot():
    ax = sentence_lengths_plot(text, window=2)
    assert isinstance(ax, Axes)
    series, average = ax.get_lines()
    assert list(series.get_ydata()) == [4, 7, 2, 7]
    assert list(average.get_ydata()) == [5.5, 4.5, 4.5]
    assert list(average.get_xdata()) == [1.5, 2.5, 3.5]
    assert average.get_label() == "Скользящее среднее (2)"
    assert len(ax.child_axes) == 1
    assert ax.child_axes[0].get_title() == "Распределение"
    assert ax.get_ylim()[1] == pytest.approx(7 * 1.7)
    assert ax.get_title() == "Длины предложений"
    ax = sentence_lengths_plot([3, 5, 2], window=10, inset=False)
    assert len(ax.get_lines()) == 1
    assert not ax.child_axes
    _, given = plt.subplots()
    assert sentence_lengths_plot([3, 5, 2], ax=given) is given
    with pytest.raises(ValueError):
        sentence_lengths_plot("")
    with pytest.raises(ValueError):
        sentence_lengths_plot(text, window=0)
    plt.close("all")
