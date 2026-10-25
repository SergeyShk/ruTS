import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes

from ruts import WordsExtractor
from ruts.corpus import delta, mendenhall_curve, rolling_delta, zeta, zeta_segments
from ruts.visualizers import (
    delta_histogram_plot,
    dendrogram_plot,
    mds_plot,
    mendenhall_plot,
    pca_plot,
    rolling_delta_plot,
    zeta_scatter_plot,
)

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
    # Длины без слов - нули, кривая не перескакивает через них
    curve = mendenhall_curve(corpus["А"])
    lengths = range(min(curve), max(curve) + 1)
    assert list(ax.get_lines()[0].get_xdata()) == list(lengths)
    assert list(ax.get_lines()[0].get_ydata()) == [curve.get(length, 0.0) for length in lengths]
    assert ax.get_legend() is not None
    with pytest.raises(ValueError):
        mendenhall_plot({})
    plt.close("all")
    with pytest.raises(ValueError):
        mendenhall_plot({"А": []})
    assert len(plt.get_fignums()) == 0


def test_rolling_delta_plot():
    reference = {"Кот": corpus["А"], "Собака": corpus["Б"]}
    ax = rolling_delta_plot(rolling_delta(reference, corpus["В"], window=6, step=3, n_mfw=10))
    assert isinstance(ax, Axes)
    assert (ax.get_title(), ax.get_xlabel(), ax.get_ylabel()) == (
        "Скользящая дельта",
        "Середина окна",
        "Расстояние",
    )
    assert [line.get_label() for line in ax.get_lines()] == ["Кот", "Собака"]
    plt.close("all")


def test_zeta_scatter_plot():
    scores = zeta(corpus["А"], corpus["Б"], segment_size=4)
    preferred = [score.word for score in scores if score.zeta > 0]
    avoided = [score.word for score in scores if score.zeta < 0]
    ax = zeta_scatter_plot(zeta_segments(corpus, preferred, avoided, segment_size=4))
    assert isinstance(ax, Axes)
    assert (ax.get_title(), ax.get_xlabel(), ax.get_ylabel()) == (
        "Маркеры Zeta в сегментах",
        "Доля избегаемых слов",
        "Доля предпочитаемых слов",
    )
    plt.close("all")


def test_delta_histogram_plot():
    texts = {**corpus, "Г": corpus["А"][::-1], "Д": corpus["Б"][::-1]}
    authors = {"А": "кот", "В": "кот", "Г": "кот", "Б": "собака", "Д": "собака"}
    ax = delta_histogram_plot(delta(texts, n_mfw=10), authors, bins=5)
    assert isinstance(ax, Axes)
    assert (ax.get_title(), ax.get_xlabel(), ax.get_ylabel()) == (
        "Расстояния внутри и между авторами",
        "Расстояние",
        "Плотность",
    )
    legend = [text.get_text() for text in ax.get_legend().get_texts()]
    assert [label.strip("\u200b ") for label in legend] == ["Один автор", "Разные авторы"]
    plt.close("all")
