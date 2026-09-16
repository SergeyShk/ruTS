from math import isnan, log2, sqrt

import pytest

from ruts.constants import DISPERSION_STATS_DESC
from ruts.corpus import Dispersion, dispersion
from ruts.corpus.dispersion import (
    calc_carroll_d2,
    calc_dp,
    calc_dp_norm,
    calc_juilland_d,
    calc_kl_divergence,
    calc_rosengren_s,
)

words = ["кот", "сидел", "на", "окне", "кот", "сидел", "на", "полу", "кот", "спал", "на", "окне"]
sizes = [10, 10, 10, 10, 10]


def test_measures_even():
    assert calc_dp([2, 2, 2, 2, 2], sizes) == 0
    assert calc_dp_norm([2, 2, 2, 2, 2], sizes) == 0
    assert calc_juilland_d([2, 2, 2, 2, 2], sizes) == 1
    assert calc_carroll_d2([2, 2, 2, 2, 2], sizes) == pytest.approx(1)
    assert calc_rosengren_s([2, 2, 2, 2, 2], sizes) == pytest.approx(1)
    assert calc_kl_divergence([2, 2, 2, 2, 2], sizes) == 0


def test_measures_clumped():
    assert calc_dp([10, 0, 0, 0, 0], sizes) == pytest.approx(0.8)
    assert calc_dp_norm([10, 0, 0, 0, 0], sizes) == pytest.approx(1)
    assert calc_juilland_d([10, 0, 0, 0, 0], sizes) == pytest.approx(1 - 2 / sqrt(4))
    assert calc_carroll_d2([10, 0, 0, 0, 0], sizes) == 0
    assert calc_rosengren_s([10, 0, 0, 0, 0], sizes) == pytest.approx(0.2)
    assert calc_kl_divergence([10, 0, 0, 0, 0], sizes) == pytest.approx(log2(5))


def test_measures_gries():
    frequencies = [1, 2, 3, 4, 5]
    assert calc_dp(frequencies, sizes) == pytest.approx(
        0.5 * (2 / 15 + 1 / 15 + 0 + 1 / 15 + 2 / 15)
    )
    assert calc_dp_norm(frequencies, sizes) == pytest.approx(0.25)
    assert calc_juilland_d(frequencies, sizes) == pytest.approx(1 - (sqrt(2) / 3) / 2)
    entropy = -sum(p / 15 * log2(p / 15) for p in frequencies)
    assert calc_carroll_d2(frequencies, sizes) == pytest.approx(entropy / log2(5))
    assert calc_rosengren_s(frequencies, sizes) == pytest.approx(
        sum(sqrt(0.2 * f) for f in frequencies) ** 2 / 15
    )
    assert calc_kl_divergence(frequencies, sizes) == pytest.approx(
        sum(f / 15 * log2(f / 15 / 0.2) for f in frequencies)
    )


def test_measures_unequal():
    frequencies = [3, 1]
    parts = [30, 10]
    assert calc_dp(frequencies, parts) == 0
    assert calc_dp_norm(frequencies, parts) == 0
    assert calc_juilland_d(frequencies, parts) == 1
    assert calc_carroll_d2(frequencies, parts) == pytest.approx(1)
    assert calc_rosengren_s(frequencies, parts) == pytest.approx(1)
    assert calc_kl_divergence(frequencies, parts) == 0
    assert calc_dp([0, 4], parts) == pytest.approx(0.75)
    assert calc_dp_norm([0, 4], parts) == pytest.approx(1)
    assert calc_rosengren_s([0, 4], parts) == pytest.approx(0.25)
    for calc in (
        calc_dp,
        calc_dp_norm,
        calc_juilland_d,
        calc_carroll_d2,
        calc_rosengren_s,
        calc_kl_divergence,
    ):
        assert isnan(calc([0, 0], parts))


def test_dispersion():
    result = dispersion(words, parts=3)
    assert [item.word for item in result] == ["кот", "на", "сидел", "окне", "полу", "спал"]
    assert result[0] == Dispersion("кот", 3, 0.0, 0.0, 1.0, 1.0, pytest.approx(1.0), 0.0)
    assert result[2] == Dispersion(
        "сидел",
        2,
        pytest.approx(1 / 3),
        pytest.approx(0.5),
        pytest.approx(0.5),
        pytest.approx(1 / log2(3)),
        pytest.approx(2 / 3),
        pytest.approx(log2(1.5)),
    )
    assert result[-1].dp == pytest.approx(2 / 3)
    assert dispersion(words, parts=[4, 4, 4]) == result
    assert dispersion(words, parts=3, word="окне") == [result[3]]
    assert dispersion(words, parts=3, min_freq=3) == result[:2]
    missing = dispersion(words, parts=3, word="собака")[0]
    assert missing.freq == 0 and isnan(missing.dp)
    assert set(Dispersion._fields[2:]) == set(DISPERSION_STATS_DESC)


def test_dispersion_errors():
    with pytest.raises(ValueError):
        dispersion(words, parts=1)
    with pytest.raises(ValueError):
        dispersion(words, parts=13)
    with pytest.raises(ValueError):
        dispersion(words, parts=[6, 5])
    with pytest.raises(ValueError):
        dispersion(words, parts=[12, 0])
    with pytest.raises(ValueError):
        dispersion(words, parts=[12])
