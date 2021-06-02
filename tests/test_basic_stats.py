import pytest

from ruts import BasicStats
from ruts.constants import BASIC_STATS_DESC


@pytest.fixture(scope="module")
def bs():
    text = "Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие черты: полнота\
        значений словарного состава языка или какого-либо его сегмента; тематический, или идеографический способ\
        упорядочения значений слов. Отличительной особенностью тезаурусов по сравнению с формальными онтологиями\
        является выход в сферу лексических значений, установление связей не только между значениями и выражающими их\
        словами, а также между самими значениями (регистрация различных семантических отношений внутри словаря)."
    bs_ = BasicStats(text, normalize=True)
    return bs_


def test_init_value_error():
    text = "+ _"
    with pytest.raises(ValueError):
        BasicStats(text)


@pytest.mark.parametrize("text", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(text):
    with pytest.raises(TypeError):
        BasicStats(text)


def test_c_letters(bs):
    assert bs.c_letters == {
        1: 4,
        2: 3,
        3: 4,
        4: 1,
        5: 8,
        6: 6,
        7: 5,
        8: 6,
        9: 5,
        10: 5,
        11: 6,
        12: 4,
        13: 2,
        15: 1,
        18: 1,
    }


def test_c_syllables(bs):
    assert bs.c_syllables == {0: 2, 1: 8, 2: 13, 3: 14, 4: 7, 5: 11, 6: 3, 7: 3}


def test_n_chars(bs):
    assert bs.n_chars == 553


def test_n_complex_words(bs):
    assert bs.n_complex_words == 24


def test_n_letters(bs):
    assert bs.n_letters == 452


def test_n_long_words(bs):
    assert bs.n_long_words == 41


def test_n_monosyllable_words(bs):
    assert bs.n_monosyllable_words == 8


def test_n_polysyllable_words(bs):
    assert bs.n_polysyllable_words == 51


def test_n_sents(bs):
    assert bs.n_sents == 2


def test_n_simple_words(bs):
    assert bs.n_simple_words == 35


def test_n_spaces(bs):
    assert bs.n_spaces == 89


def test_n_syllables(bs):
    assert bs.n_syllables == 198


def test_n_unique_words(bs):
    assert bs.n_unique_words == 56


def test_n_words(bs):
    assert bs.n_words == 61


def test_n_punctuations(bs):
    assert bs.n_punctuations == 12


def test_p_unique_words(bs):
    assert bs.p_unique_words == pytest.approx(0.91, rel=0.1)


def test_p_long_words(bs):
    assert bs.p_long_words == pytest.approx(0.67, rel=0.1)


def test_p_complex_words(bs):
    assert bs.p_complex_words == pytest.approx(0.39, rel=0.1)


def test_p_simple_words(bs):
    assert bs.p_simple_words == pytest.approx(0.57, rel=0.1)


def test_p_monosyllable_words(bs):
    assert bs.p_monosyllable_words == pytest.approx(0.13, rel=0.1)


def test_p_polysyllable_words(bs):
    assert bs.p_polysyllable_words == pytest.approx(0.83, rel=0.1)


def test_p_letters(bs):
    assert bs.p_letters == pytest.approx(0.82, rel=0.1)


def test_p_spaces(bs):
    assert bs.p_spaces == pytest.approx(0.15, rel=0.1)


def test_p_punctuations(bs):
    assert bs.p_punctuations == pytest.approx(0.02, rel=0.1)


def test_get_stats(bs):
    stats = bs.get_stats()
    assert isinstance(stats, dict)
    for key in BASIC_STATS_DESC.keys():
        assert stats[key] == getattr(bs, key)


def test_print_stats(capsys, bs):
    bs.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == 14
