import pytest

from ruts import DiversityStats
from ruts.constants import DIVERSITY_STATS_DESC
from ruts.diversity_stats import calc_hdd, calc_mattr, calc_msttr, calc_ttr


@pytest.fixture(scope="module")
def ds():
    text = "Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие черты: полнота\
        значений словарного состава языка или какого-либо его сегмента; тематический, или идеографический способ\
        упорядочения значений слов. Отличительной особенностью тезаурусов по сравнению с формальными онтологиями\
        является выход в сферу лексических значений, установление связей не только между значениями и выражающими их\
        словами, а также между самими значениями (регистрация различных семантических отношений внутри словаря)."
    ds_ = DiversityStats(text)
    return ds_


def test_init_value_error():
    text = "+ _"
    with pytest.raises(ValueError):
        DiversityStats(text)


@pytest.mark.parametrize("text", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(text):
    with pytest.raises(TypeError):
        DiversityStats(text)


def test_ttr(ds):
    assert ds.ttr == pytest.approx(0.9180327868852459, rel=0.01)


def test_rttr(ds):
    assert ds.rttr == pytest.approx(7.170065276242175, rel=0.05)


def test_cttr(ds):
    assert ds.cttr == pytest.approx(5.070001778381037, rel=0.05)


def test_httr(ds):
    assert ds.httr == pytest.approx(0.9791961085978588, rel=0.01)


def test_sttr(ds):
    assert ds.sttr == pytest.approx(0.9637280435448702, rel=0.01)


def test_mttr(ds):
    assert ds.mttr == pytest.approx(0.011652687920277623, rel=0.005)


def test_dttr(ds):
    assert ds.dttr == pytest.approx(85.81710990988037, rel=0.1)


def test_mattr(ds):
    assert ds.mattr == pytest.approx(0.9133333333333336, rel=0.01)


def test_mattr_n_words():
    text = ["социалистическая", "революция"]
    assert calc_mattr(text, 50) == calc_ttr(text)


def test_msttr(ds):
    assert ds.msttr == pytest.approx(0.94, rel=0.01)


def test_msttr_n_words():
    text = ["социалистическая", "революция"]
    assert calc_msttr(text, 50) == calc_ttr(text)


def test_mtld(ds):
    assert ds.mtld == pytest.approx(208.3760000000001, rel=1)


def test_mamtld(ds):
    assert ds.mamtld == pytest.approx(1.0, rel=0.01)


def test_hdd(ds):
    assert ds.hdd == pytest.approx(0.9403815874780037, rel=0.01)


def test_hdd_n_words():
    text = ["социалистическая", "революция"]
    assert calc_hdd(text) == -1


def test_hdd_zero_division_error(ds):
    text = ds.words
    assert calc_hdd(text, 0) == 0.0


def test_simpson_index(ds):
    assert ds.simpson_index == pytest.approx(305.0, rel=1)


def test_hapax_index(ds):
    assert ds.hapax_index == pytest.approx(2499.4617690150753, rel=1)


def test_get_stats(ds):
    stats = ds.get_stats()
    assert isinstance(stats, dict)
    for key in DIVERSITY_STATS_DESC.keys():
        assert stats[key] == getattr(ds, key)


def test_print_stats(capsys, ds):
    ds.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == 15
