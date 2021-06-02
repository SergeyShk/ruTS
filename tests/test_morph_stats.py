from collections import Counter

import pytest

from ruts import MorphStats
from ruts.constants import MORPHOLOGY_STATS_DESC


@pytest.fixture(scope="module")
def ms():
    text = "Постарайтесь получить то, что любите, иначе придется полюбить то, что получили"
    ms_ = MorphStats(text)
    return ms_


def test_init_value_error():
    text = "+ _"
    with pytest.raises(ValueError):
        MorphStats(text)


@pytest.mark.parametrize("text", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(text):
    with pytest.raises(TypeError):
        MorphStats(text)


def test_pos(ms):
    assert ms.pos == (
        "VERB",
        "INFN",
        "CONJ",
        "CONJ",
        "VERB",
        "ADVB",
        "VERB",
        "INFN",
        "CONJ",
        "CONJ",
        "VERB",
    )


def test_animacy(ms):
    assert ms.animacy == (
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )


def test_aspect(ms):
    assert ms.aspect == (
        "perf",
        "perf",
        None,
        None,
        "impf",
        None,
        "perf",
        "perf",
        None,
        None,
        "perf",
    )


def test_case(ms):
    assert ms.case == (None, None, None, None, None, None, None, None, None, None, None)


def test_gender(ms):
    assert ms.gender == (
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )


def test_involvement(ms):
    assert ms.involvement == (
        "excl",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )


def test_mood(ms):
    assert ms.mood == (
        "impr",
        None,
        None,
        None,
        "indc",
        None,
        "indc",
        None,
        None,
        None,
        "indc",
    )


def test_number(ms):
    assert ms.number == (
        "plur",
        None,
        None,
        None,
        "plur",
        None,
        "sing",
        None,
        None,
        None,
        "plur",
    )


def test_person(ms):
    assert ms.person == (
        None,
        None,
        None,
        None,
        "2per",
        None,
        "3per",
        None,
        None,
        None,
        None,
    )


def test_tense(ms):
    assert ms.tense == (
        None,
        None,
        None,
        None,
        "pres",
        None,
        "futr",
        None,
        None,
        None,
        "past",
    )


def test_transitivity(ms):
    assert ms.transitivity == (
        "intr",
        "tran",
        None,
        None,
        "tran",
        None,
        "intr",
        "tran",
        None,
        None,
        "tran",
    )


def test_voice(ms):
    assert ms.voice == (
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )


def test_get_stats(ms):
    stats = ms.get_stats()
    assert isinstance(stats, dict)
    for key in MORPHOLOGY_STATS_DESC.keys():
        assert stats[key] == Counter(getattr(ms, key))


def test_get_stats_args(ms):
    stats = ms.get_stats("pos", "tense")
    assert set(stats.keys()) == set(["pos", "tense"])


def test_get_stats_filter_none(ms):
    stats = ms.get_stats(filter_none=True)
    assert all([None not in v.keys() for v in stats.values()])


def test_explain_text(ms):
    explain = ms.explain_text()
    assert isinstance(explain, tuple)
    assert list(zip(*explain))[0] == ms.words


def test_explain_text_args(ms):
    explain = ms.explain_text("pos", "tense")
    assert all([set(v.keys()) == set(["pos", "tense"]) for v in tuple(zip(*explain))[1]])


def test_explain_text_filter_none(ms):
    explain = ms.explain_text(filter_none=True)
    assert all([None not in v.values() for v in tuple(zip(*explain))[1]])


def test_print_stats(capsys, ms):
    ms.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == 29


def test_print_stats_args(capsys, ms):
    ms.print_stats("pos", "tense")
    captured = capsys.readouterr()
    assert captured.out.count("|") == 8


def test_check_stat_key_error(ms):
    with pytest.raises(KeyError):
        ms.get_stats("foo", "tense")
