import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes

from ruts import WordsExtractor
from ruts.corpus import delta, mendenhall_curve
from ruts.visualizers import dendrogram_plot, mds_plot, mendenhall_plot, pca_plot

matplotlib.use("Agg")

texts = {
    "А": "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне.",
    "Б": "Собака лежала на полу и дремала. Потом собака ела и снова дремала на полу.",
    "В": "Завтра кот снова будет сидеть на окне и смотреть на птиц, а собака будет дремать.",
}
extractor = WordsExtractor(lowercase=True)
corpus = {name: extractor.extract(text) for name, text in texts.items()}
distances = delta(corpus, n_mfw=10)


def test_dendrogram_plot():
    ax = dendrogram_plot(distances)
    assert isinstance(ax, Axes)
    assert sorted(label.get_text() for label in ax.get_yticklabels()) == ["А", "Б", "В"]
    assert ax.get_xlabel() == "Расстояние"
    assert len(ax.collections) >= 2
    _, given = plt.subplots()
    assert dendrogram_plot(distances, method="average", ax=given) is given
    plt.close("all")
    with pytest.raises(ValueError):
        dendrogram_plot(distances.iloc[:1, :1])
    with pytest.raises(ValueError):
        dendrogram_plot(distances.iloc[:2, :3])
    with pytest.raises(ValueError):
        dendrogram_plot(distances.replace(0.0, np.nan))
    assert len(plt.get_fignums()) == 0


def test_pca_plot():
    ax = pca_plot(corpus, n_mfw=10)
    assert isinstance(ax, Axes)
    assert [text.get_text() for text in ax.texts] == ["А", "Б", "В"]
    offsets = ax.collections[0].get_offsets()
    assert offsets.shape == (3, 2)
    assert np.allclose(offsets.mean(axis=0), 0, atol=1e-9)
    assert ax.get_xlabel().startswith("Компонента 1 (")
    assert ax.get_ylabel().startswith("Компонента 2 (")
    with pytest.raises(ValueError):
        pca_plot({name: corpus[name] for name in ("А", "Б")}, n_mfw=10)
    ax = pca_plot(corpus, n_mfw=1)
    assert ax.get_xlabel() == "Компонента 1 (100.0%)"
    assert np.allclose(ax.collections[0].get_offsets()[:, 1], 0)
    with pytest.raises(ValueError):
        pca_plot({"А": corpus["А"]})
    plt.close("all")


def test_mds_plot():
    ax = mds_plot(distances)
    assert isinstance(ax, Axes)
    assert [text.get_text() for text in ax.texts] == ["А", "Б", "В"]
    offsets = np.asarray(ax.collections[0].get_offsets())
    assert offsets.shape == (3, 2)
    assert np.allclose(offsets.mean(axis=0), 0, atol=1e-9)
    recovered = np.linalg.norm(offsets[0] - offsets[1])
    assert recovered <= distances.loc["А", "Б"] + 1e-9
    assert ax.get_title() == "Многомерное шкалирование"
    with pytest.raises(ValueError):
        mds_plot(distances.iloc[:1, :1])
    with pytest.raises(ValueError):
        mds_plot(distances.replace(0.0, np.inf))
    plt.close("all")


def test_mds_plot_exact():
    exact = distances.copy()
    exact.loc[:, :] = [[0, 3, 4], [3, 0, 5], [4, 5, 0]]
    offsets = np.asarray(mds_plot(exact).collections[0].get_offsets())
    for i, j, expected in ((0, 1, 3), (0, 2, 4), (1, 2, 5)):
        assert np.linalg.norm(offsets[i] - offsets[j]) == pytest.approx(expected)
    plt.close("all")


def test_mendenhall_plot():
    ax = mendenhall_plot(corpus)
    assert isinstance(ax, Axes)
    assert [line.get_label() for line in ax.get_lines()] == ["А", "Б", "В"]
    curve = mendenhall_curve(corpus["А"])
    assert list(ax.get_lines()[0].get_xdata()) == list(curve)
    assert list(ax.get_lines()[0].get_ydata()) == list(curve.values())
    assert ax.get_legend() is not None
    with pytest.raises(ValueError):
        mendenhall_plot({})
    plt.close("all")
    with pytest.raises(ValueError):
        mendenhall_plot({"А": []})
    assert len(plt.get_fignums()) == 0
