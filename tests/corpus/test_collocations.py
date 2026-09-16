from math import isnan, log2, sqrt

import pytest
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder

from ruts.constants import COLLOCATION_MEASURES
from ruts.corpus import Collocation, collocations
from ruts.corpus.collocations import (
    MEASURES,
    calc_dice,
    calc_log_likelihood,
    calc_logdice,
    calc_mi,
    calc_mi3,
    calc_min_sensitivity,
    calc_npmi,
    calc_t_score,
)

words = ["кот", "сидел", "на", "окне", "кот", "сидел", "на", "полу", "кот", "спал", "на", "окне"]
text = (
    "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне. "
    "Завтра кот снова будет сидеть на окне и смотреть на птиц."
).lower()
tokens = [word.strip(".,") for word in text.split()]


def test_measures():
    assert set(MEASURES) == set(COLLOCATION_MEASURES)
    assert calc_mi(3, 3, 3, 12) == log2(4)
    assert calc_mi3(3, 3, 3, 12) == log2(27 * 12 / 9)
    assert calc_t_score(3, 3, 3, 12) == pytest.approx((3 - 9 / 12) / sqrt(3))
    assert calc_dice(3, 2, 2, 12) == 0.8
    assert calc_logdice(3, 3, 3, 12) == 14
    assert calc_logdice(3, 2, 2, 12) == pytest.approx(14 + log2(0.8))
    assert calc_npmi(3, 3, 3, 12) == pytest.approx(2 / 2)
    assert calc_npmi(3, 3, 1, 12) == pytest.approx(log2(12 / 9) / log2(12))
    assert calc_min_sensitivity(3, 2, 2, 12) == pytest.approx(2 / 3)
    assert calc_log_likelihood(3, 3, 3, 12) == pytest.approx(
        BigramAssocMeasures.likelihood_ratio(3, (3, 3), 12), rel=1e-6
    )
    for calc in (calc_mi, calc_mi3, calc_t_score, calc_logdice, calc_npmi):
        assert isnan(calc(3, 3, 0, 12))
    assert isnan(calc_npmi(12, 12, 12, 12))
    assert calc_log_likelihood(12, 12, 12, 12) == 0


def test_collocations():
    found = collocations(words, window=2)
    assert found[0] == Collocation("кот", "на", 3, 3, 3, 13.0)
    assert [(c.left, c.right) for c in found[1:4]] == [
        ("кот", "сидел"),
        ("на", "окне"),
        ("сидел", "на"),
    ]
    assert found[1].score == pytest.approx(calc_logdice(3, 2, 1, 12))
    assert all(c.freq_pair >= 2 for c in found)
    assert collocations(words, window=2, top_n=1) == found[:1]
    assert collocations(words, window=1) == [
        Collocation("кот", "сидел", 3, 2, 2, calc_logdice(3, 2, 2, 12)),
        Collocation("на", "окне", 3, 2, 2, calc_logdice(3, 2, 2, 12)),
        Collocation("сидел", "на", 2, 3, 2, calc_logdice(2, 3, 2, 12)),
    ]
    assert collocations(words, window=1, measure="t_score", node="кот") == [
        Collocation("кот", "сидел", 3, 2, 2, calc_t_score(3, 2, 2, 12))
    ]
    assert [(c.left, c.right) for c in collocations(words, window=1, node="на", min_freq=1)] == [
        ("на", "окне"),
        ("сидел", "на"),
        ("на", "полу"),
        ("спал", "на"),
    ]
    assert collocations(["кот"], window=3) == []


@pytest.mark.parametrize("window", [1, 2, 5])
def test_collocations_nltk(window):
    finder = BigramCollocationFinder.from_words(tokens, window_size=window + 1)
    found = {
        (c.left, c.right): c
        for c in collocations(tokens, window=window, measure="log_likelihood", min_freq=1)
    }
    assert {pair: c.freq_pair for pair, c in found.items()} == dict(finder.ngram_fd)
    for (left, right), score in finder.score_ngrams(BigramAssocMeasures.likelihood_ratio):
        assert found[left, right].score == pytest.approx(score, rel=1e-6)
    mi = {
        (c.left, c.right): c.score
        for c in collocations(tokens, window=window, measure="mi", min_freq=1)
    }
    for (left, right), score in finder.score_ngrams(BigramAssocMeasures.pmi):
        assert mi[left, right] == pytest.approx(score)
    t_score = {
        (c.left, c.right): c.score
        for c in collocations(tokens, window=window, measure="t_score", min_freq=1)
    }
    for (left, right), score in finder.score_ngrams(BigramAssocMeasures.student_t):
        assert t_score[left, right] == pytest.approx(score)


def test_collocations_measures():
    for measure in COLLOCATION_MEASURES:
        found = collocations(words, window=2, measure=measure)
        assert found[0].score == MEASURES[measure](3, 3, 1.5, 12)
        scores = [c.score for c in found]
        assert scores == sorted(scores, reverse=True)


def test_collocations_errors():
    with pytest.raises(ValueError):
        collocations(words, measure="pmi")
    with pytest.raises(ValueError):
        collocations(words, window=0)
