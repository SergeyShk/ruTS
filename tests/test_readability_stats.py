import pytest

from ruts import ReadabilityStats
from ruts.constants import READABILITY_STATS_DESC


@pytest.fixture(scope="module")
def rs():
    text = "Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие черты: полнота\
        значений словарного состава языка или какого-либо его сегмента; тематический, или идеографический способ\
        упорядочения значений слов. Отличительной особенностью тезаурусов по сравнению с формальными онтологиями\
        является выход в сферу лексических значений, установление связей не только между значениями и выражающими их\
        словами, а также между самими значениями (регистрация различных семантических отношений внутри словаря)."
    rs_ = ReadabilityStats(text)
    return rs_


def test_init_value_error():
    text = "+ _"
    with pytest.raises(ValueError):
        ReadabilityStats(text)


@pytest.mark.parametrize("text", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(text):
    with pytest.raises(TypeError):
        ReadabilityStats(text)


def test_flesch_kincaid_grade(rs):
    assert rs.flesch_kincaid_grade == pytest.approx(22.050081967213114, rel=0.1)


def test_flesch_reading_easy(rs):
    assert rs.flesch_reading_easy == pytest.approx(-27.893688524590175, rel=0.1)


def test_coleman_liau_index(rs):
    assert rs.coleman_liau_index == pytest.approx(23.900823770491805, rel=0.1)


def test_smog_index(rs):
    assert rs.smog_index == pytest.approx(30.676655057318946, rel=0.1)


def test_automated_readability_index(rs):
    assert rs.automated_readability_index == pytest.approx(23.900823770491805, rel=0.1)


def test_lix(rs):
    assert rs.lix == pytest.approx(97.71311475409836, rel=0.1)


def test_get_stats(rs):
    stats = rs.get_stats()
    assert isinstance(stats, dict)
    for key in READABILITY_STATS_DESC.keys():
        assert stats[key] == getattr(rs, key)


def test_print_stats(capsys, rs):
    rs.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == 7
