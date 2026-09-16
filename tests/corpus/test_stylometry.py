from math import isclose, log2, sqrt

import numpy as np
import pytest
import spacy
from scipy.spatial.distance import jensenshannon

from ruts import CharNgramsExtractor, WordsExtractor
from ruts.constants import DELTA_VARIANTS, FUNCTION_UD_POS
from ruts.corpus import (
    ZetaScore,
    delta,
    frequency_table,
    function_words_profile,
    kilgarriff_chi2,
    mendenhall_curve,
    mendenhall_distance,
    z_scores,
    zeta,
)

texts = {
    "А": "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне.",
    "Б": "Собака лежала на полу и дремала. Потом собака ела и снова дремала на полу.",
    "В": "Завтра кот снова будет сидеть на окне и смотреть на птиц, а собака будет дремать.",
}
extractor = WordsExtractor(lowercase=True)
corpus = {name: extractor.extract(text) for name, text in texts.items()}


def test_frequency_table():
    table = frequency_table(corpus, n_mfw=5)
    assert list(table.index) == ["А", "Б", "В"]
    assert list(table.columns) == ["на", "и", "собака", "кот", "окне"]
    assert table.loc["А", "на"] == pytest.approx(3 / 15)
    assert table.loc["Б", "кот"] == 0
    assert frequency_table(corpus, n_mfw=None).shape == (3, 23)
    assert list(frequency_table(corpus, n_mfw=None, culling=1.0).columns) == ["на", "и"]
    assert list(frequency_table(corpus, n_mfw=None, culling=0.5).columns)[:4] == [
        "на",
        "и",
        "собака",
        "кот",
    ]
    assert frequency_table({"А": ["а"]}, n_mfw=None).loc["А", "а"] == 1


def test_z_scores():
    scores = z_scores(frequency_table(corpus, n_mfw=5))
    assert scores["кот"].tolist() == pytest.approx([1.0, -1.0, 0.0])
    column = frequency_table(corpus, n_mfw=5)["на"]
    assert scores["на"].tolist() == pytest.approx(
        ((column - column.mean()) / column.std(ddof=1)).tolist()
    )
    constant = z_scores(frequency_table({"А": ["а", "б"], "Б": ["а", "в"]}, n_mfw=None))
    assert constant["а"].tolist() == [0.0, 0.0]
    assert constant["б"].tolist() == pytest.approx([sqrt(2) / 2, -sqrt(2) / 2])


def test_delta():
    scores = z_scores(frequency_table(corpus, n_mfw=5))
    difference = (scores.loc["А"] - scores.loc["Б"]).abs()
    distances = delta(corpus, n_mfw=5)
    assert list(distances.index) == list(distances.columns) == ["А", "Б", "В"]
    assert np.allclose(distances, distances.T)
    assert np.diag(distances).tolist() == [0.0, 0.0, 0.0]
    assert distances.loc["А", "Б"] == pytest.approx(difference.sum() / 5)
    assert delta(corpus, n_mfw=5, variant="quadratic").loc["А", "Б"] == pytest.approx(
        sqrt((difference**2).sum()) / 5
    )
    weights = [(5 - rank + 2) / 5 for rank in range(1, 6)]
    assert delta(corpus, n_mfw=5, variant="eder").loc["А", "Б"] == pytest.approx(
        (difference * weights).sum()
    )
    a, b = scores.loc["А"], scores.loc["Б"]
    assert delta(corpus, n_mfw=5, variant="cosine").loc["А", "Б"] == pytest.approx(
        1 - (a * b).sum() / sqrt((a**2).sum() * (b**2).sum())
    )
    assert delta(corpus, n_mfw=5).loc["А", "В"] < delta(corpus, n_mfw=5).loc["А", "Б"]
    assert set(DELTA_VARIANTS) == {"burrows", "quadratic", "eder", "cosine"}


def test_delta_char_ngrams():
    ngrams = CharNgramsExtractor(n=2, lowercase=True)
    distances = delta({name: ngrams.extract(text) for name, text in texts.items()}, n_mfw=20)
    assert distances.shape == (3, 3)
    assert distances.loc["А", "В"] < distances.loc["А", "Б"]


def test_delta_errors():
    with pytest.raises(ValueError):
        delta(corpus, variant="manhattan")
    with pytest.raises(ValueError):
        delta({"А": corpus["А"]})
    with pytest.raises(ValueError):
        frequency_table({})
    with pytest.raises(ValueError):
        frequency_table({"А": corpus["А"], "Б": []})
    with pytest.raises(ValueError):
        frequency_table(corpus, culling=2)


def test_zeta():
    scores = zeta(corpus["А"], corpus["Б"], segment_size=5)
    assert scores[0] == ZetaScore("кот", 2 / 3, 0.0, 2 / 3, log2((2 / 3) / (0.5 / 3)))
    assert [score.word for score in scores[:3]] == ["кот", "окне", "на"]
    assert scores[2] == ZetaScore("на", 1.0, 2 / 3, pytest.approx(1 / 3), pytest.approx(log2(1.5)))
    assert scores[-1].word == "собака"
    assert scores[-1].zeta == pytest.approx(-2 / 3)
    assert scores[-1].log_zeta == pytest.approx(log2((0.5 / 3) / (2 / 3)))
    assert zeta(corpus["А"], corpus["Б"], segment_size=5, top_n=2) == scores[:2]
    assert zeta(corpus["А"], corpus["Б"], segment_size=100)[0].zeta == 1.0
    assert zeta([corpus["А"], corpus["В"]], [corpus["Б"]], segment_size=5)[
        -1
    ].zeta == pytest.approx(-2 / 3)
    assert zeta([corpus["А"], []], corpus["Б"], segment_size=5) == scores


def test_zeta_errors():
    with pytest.raises(ValueError):
        zeta(corpus["А"], corpus["Б"], segment_size=0)
    with pytest.raises(ValueError):
        zeta([], corpus["Б"])
    with pytest.raises(ValueError):
        zeta(corpus["А"], [[]])


def test_kilgarriff_chi2():
    words_a = ["а"] * 6 + ["б"] * 3 + ["в"]
    words_b = ["а"] * 2 + ["б"] * 5 + ["г"] * 3
    expected = 0.0
    for count_a, count_b in ((6, 2), (3, 5)):
        joint = count_a + count_b
        expected += (count_a - joint / 2) ** 2 / (joint / 2) * 2
    assert kilgarriff_chi2(words_a, words_b, n_mfw=2) == pytest.approx(expected)
    assert kilgarriff_chi2(words_a, words_a) == 0
    assert kilgarriff_chi2(words_a, words_b) > kilgarriff_chi2(words_a, words_b, n_mfw=2)
    with pytest.raises(ValueError):
        kilgarriff_chi2([], words_b)


def test_mendenhall():
    curve = mendenhall_curve(corpus["А"])
    assert list(curve) == [1, 2, 3, 4, 5, 7]
    assert curve[3] == pytest.approx(2 / 15)
    assert isclose(sum(curve.values()), 1.0)
    curve_b = mendenhall_curve(corpus["Б"])
    lengths = sorted(set(curve) | set(curve_b))
    assert mendenhall_distance(corpus["А"], corpus["Б"]) == pytest.approx(
        jensenshannon(
            [curve.get(length, 0) for length in lengths],
            [curve_b.get(length, 0) for length in lengths],
            base=2,
        )
    )
    assert mendenhall_distance(corpus["А"], corpus["А"]) == 0
    assert mendenhall_distance(["а"], ["бб"]) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        mendenhall_curve([])


def test_function_words_profile():
    profile = function_words_profile(corpus["А"])
    assert list(profile) == list(FUNCTION_UD_POS)
    assert profile["ADP"] == pytest.approx(3 / 15)
    assert profile["CCONJ"] == pytest.approx(2 / 15)
    assert profile["PRON"] == 0
    profile = function_words_profile(["Он", "не", "знал", ",", "что", "это", "тот"])
    assert profile["PRON"] == pytest.approx(1 / 7)
    assert profile["PART"] == pytest.approx(2 / 7)
    assert profile["SCONJ"] == pytest.approx(1 / 7)
    assert profile["DET"] == pytest.approx(1 / 7)
    doc = spacy.blank("ru")(texts["А"])
    assert function_words_profile(doc) == function_words_profile(corpus["А"])
    with pytest.raises(ValueError):
        function_words_profile([])


def test_function_words_profile_tagged():
    pytest.importorskip("ru_core_news_sm")
    doc = spacy.load("ru_core_news_sm")("Он сказал, что кот спал, а пёс во-первых ел.")
    profile = function_words_profile(doc)
    assert profile["PRON"] == pytest.approx(1 / 9)
    assert profile["SCONJ"] == pytest.approx(1 / 9)
    assert profile["CCONJ"] == pytest.approx(2 / 9)
    assert profile["ADP"] == 0
