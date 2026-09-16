from collections import Counter
from math import inf, isnan, log

import pytest

from ruts.constants import G2_CRITICAL_VALUES, KEYNESS_MEASURES
from ruts.corpus import Keyword, keyness
from ruts.corpus.keyness import (
    MEASURES,
    calc_bic,
    calc_chi2,
    calc_diff,
    calc_ell,
    calc_log_likelihood,
    calc_log_ratio,
    calc_odds_ratio,
    calc_p_value,
)
from ruts.datasets import FreqDict
from ruts.datasets.freq2011 import CORPUS_SIZE
from tests.datasets.test_freq2011 import write_dict

target = ["кот", "сидел", "на", "окне", "и", "смотрел", "на", "птиц", "кот", "уснул"]
reference = ["собака", "лежала", "на", "полу", "и", "спала", "собака", "ела"]


@pytest.fixture(scope="module")
def freq_dict(tmp_path_factory):
    path = tmp_path_factory.mktemp("dicts")
    write_dict(path)
    return FreqDict(data_dir=path)


def test_measures():
    assert set(MEASURES) == set(KEYNESS_MEASURES)
    assert calc_log_likelihood(10, 5, 1000, 2000) == pytest.approx(
        2 * (10 * log(2) + 5 * log(0.5))
    )
    assert calc_log_likelihood(5, 10, 2000, 1000) == pytest.approx(
        -calc_log_likelihood(10, 5, 1000, 2000)
    )
    assert calc_log_likelihood(0, 0, 1000, 2000) == 0
    assert calc_log_likelihood(10, 0, 1000, 2000) == pytest.approx(2 * 10 * log(3))
    assert calc_chi2(10, 5, 1000, 2000) == pytest.approx(6.105527638190955)
    assert calc_chi2(5, 10, 2000, 1000) == pytest.approx(-6.105527638190955)
    assert calc_chi2(1, 2, 1000, 2000) == 0
    assert calc_chi2(0, 0, 1000, 2000) == 0
    assert calc_diff(10, 5, 1000, 2000) == pytest.approx(300)
    assert calc_diff(10, 0, 1000, 2000) == pytest.approx((0.01 - 0.00025) / 0.00025 * 100)
    assert calc_log_ratio(10, 5, 1000, 2000) == 2
    assert calc_log_ratio(0, 5, 1000, 2000) == pytest.approx(-2.321928094887362)
    assert calc_bic(10, 5, 1000, 2000) == pytest.approx(
        calc_log_likelihood(10, 5, 1000, 2000) - log(3000)
    )
    assert calc_bic(5, 10, 2000, 1000) == pytest.approx(-calc_bic(10, 5, 1000, 2000))
    assert calc_ell(10, 5, 1000, 2000) == pytest.approx(
        calc_log_likelihood(10, 5, 1000, 2000) / (3000 * log(5))
    )
    assert isnan(calc_ell(1, 0, 1000, 2000))
    assert calc_odds_ratio(10, 5, 1000, 2000) == pytest.approx((10 / 990) / (5 / 1995))
    assert calc_odds_ratio(10, 10, 10, 20) == inf
    assert calc_odds_ratio(10, 20, 20, 20) == inf
    assert calc_p_value(3.84) == pytest.approx(0.05, abs=0.001)
    for p, critical in G2_CRITICAL_VALUES.items():
        assert calc_p_value(critical) == pytest.approx(p, rel=0.01)
        assert calc_p_value(-critical) == pytest.approx(p, rel=0.01)


def test_keyness():
    keywords = keyness(target, reference)
    assert [keyword.word for keyword in keywords] == [
        "кот",
        "окне",
        "птиц",
        "сидел",
        "смотрел",
        "уснул",
        "на",
    ]
    assert keywords[0] == Keyword(
        "кот",
        2,
        0,
        200000.0,
        0.0,
        calc_log_likelihood(2, 0, 10, 8),
        calc_p_value(calc_log_likelihood(2, 0, 10, 8)),
        calc_log_ratio(2, 0, 10, 8),
        calc_log_likelihood(2, 0, 10, 8),
    )
    assert keywords[-1].freq_reference == 1
    assert keywords[-1].ipm_reference == 125000.0
    assert keyness(Counter(target), Counter(reference)) == keywords
    assert keyness(target, reference, top_n=2) == keywords[:2]
    assert [keyword.word for keyword in keyness(target, reference, min_freq=2)] == ["кот", "на"]
    assert all(keyword.g2 > 0 for keyword in keywords)


def test_keyness_negative():
    keywords = keyness(target, reference, positive=False)
    assert [keyword.word for keyword in keywords] == [
        "собака",
        "ела",
        "лежала",
        "полу",
        "спала",
        "и",
    ]
    assert all(keyword.g2 < 0 and keyword.score < 0 for keyword in keywords)
    assert keywords[-1].freq_target == 1
    assert keywords[-1].log_ratio == pytest.approx(-0.32192809488736235)


def test_keyness_measures():
    for measure in KEYNESS_MEASURES:
        keywords = keyness(target, reference, measure=measure)
        cat = next(keyword for keyword in keywords if keyword.word == "кот")
        assert cat.score == MEASURES[measure](2, 0, 10, 8) or isnan(cat.score)
        if measure != "ell":
            assert keywords[0].word == "кот"
    keywords = keyness(target, reference, measure="ell")
    assert keywords[0].word == "на"
    assert all(isnan(keyword.score) for keyword in keywords[1:])
    assert [keyword.word for keyword in keyness(target, reference, measure="odds_ratio")[:1]] == [
        "кот"
    ]


def test_keyness_freq_dict(freq_dict):
    keywords = keyness(["Кот", "кот", "птица", "фелинолог"], freq_dict)
    assert [keyword.word for keyword in keywords] == ["фелинолог", "кот", "птица"]
    cat = keywords[1]
    assert cat.freq_reference == pytest.approx(40.3 * CORPUS_SIZE / 1e6)
    assert cat.ipm_reference == pytest.approx(40.3)
    assert cat.ipm_target == 500000.0
    assert cat.g2 == pytest.approx(calc_log_likelihood(2, 40.3 * 92, 4, CORPUS_SIZE))
    assert keywords[0].freq_reference == 0
    assert keywords[0].log_ratio == pytest.approx(calc_log_ratio(1, 0, 4, CORPUS_SIZE))
    negative = keyness(["кот"], freq_dict, positive=False, min_freq=1000)
    assert [keyword.word for keyword in negative][:2] == ["и", "на"]
    assert keyness({"ещё": 2, "Ещё": 1}, freq_dict)[0].freq_target == 3
    assert keyness(["ещё"], freq_dict)[0].ipm_reference == pytest.approx(2409.4)


def test_keyness_errors():
    with pytest.raises(ValueError):
        keyness(target, reference, measure="mi")
    with pytest.raises(ValueError):
        keyness([], reference)
    with pytest.raises(ValueError):
        keyness(target, {})
