from math import isnan

import pytest

from ruts import BasicStats
from ruts.basic_stats import count_punctuations, punctuation_profile
from ruts.constants import BASIC_STATS_DESC, PUNCTUATION_TYPES


@pytest.fixture(scope="module")
def bs():
    text = "Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие черты: полнота\
        значений словарного состава языка или какого-либо его сегмента; тематический, или идеографический способ\
        упорядочения значений слов. Отличительной особенностью тезаурусов по сравнению с формальными онтологиями\
        является выход в сферу лексических значений, установление связей не только между значениями и выражающими их\
        словами, а также между самими значениями (регистрация различных семантических отношений внутри словаря)."
    return BasicStats(text, normalize=True)


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


def test_c_punctuations(bs):
    assert bs.c_punctuations == {
        "comma": 4,
        "period": 2,
        "question": 0,
        "exclamation": 0,
        "ellipsis": 0,
        "colon": 1,
        "semicolon": 1,
        "dash": 0,
        "hyphen": 2,
        "angle_quotes": 0,
        "straight_quotes": 0,
        "parentheses": 2,
        "other": 0,
    }
    assert sum(bs.c_punctuations.values()) == bs.n_punctuations
    assert list(bs.c_punctuations) == list(PUNCTUATION_TYPES)


def test_count_punctuations():
    text = (
        'Кот — «зверь»... Пёс, конечно, - друг; а „кот“ (тот, что жив) – нет! Так ли? "Да". № 5…'
    )
    counts = count_punctuations(text)
    assert counts == {
        "comma": 3,
        "period": 1,
        "question": 1,
        "exclamation": 1,
        "ellipsis": 2,
        "colon": 0,
        "semicolon": 1,
        "dash": 2,
        "hyphen": 1,
        "angle_quotes": 2,
        "straight_quotes": 4,
        "parentheses": 2,
        "other": 1,
    }
    assert count_punctuations("Привет.... Пока....... Да") == {
        **dict.fromkeys(PUNCTUATION_TYPES, 0),
        "ellipsis": 2,
    }
    assert count_punctuations("") == dict.fromkeys(PUNCTUATION_TYPES, 0)


def test_punctuation_profile():
    profile = punctuation_profile("Ёж, ещё ёж — и еще еж!")
    assert profile["comma"] == pytest.approx(1 / 6 * 1000)
    assert profile["dash"] == pytest.approx(1 / 6 * 1000)
    assert profile["exclamation"] == pytest.approx(1 / 6 * 1000)
    assert profile["period"] == 0
    assert profile["yo_share"] == pytest.approx(3 / 7)
    assert punctuation_profile("Ёж, ёж", n_words=4)["comma"] == 250
    assert isnan(punctuation_profile("Кот и пёс")["yo_share"]) is False
    assert isnan(punctuation_profile("Кот и дом")["yo_share"])
    assert all(isnan(value) for value in punctuation_profile("...").values())


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


def test_count_words_by_syllables(bs):
    assert bs.count_words_by_syllables(4) == bs.n_complex_words
    assert bs.count_words_by_syllables(5) == 17


def test_count_words_by_letters(bs):
    assert bs.count_words_by_letters(6) == bs.n_long_words
    assert bs.count_words_by_letters(7) == 35


def test_custom_factors():
    text = "Существуют три вида лжи: ложь, наглая ложь и статистика"
    bs = BasicStats(text, complex_syl_factor=5, long_word_letter_factor=7)
    assert bs.n_complex_words == 0
    assert bs.n_simple_words == 9
    assert bs.n_long_words == 2


def test_multichar_punctuation():
    bs = BasicStats("Ура!!! Ура?! Ура... Слово – слово… и №1")
    assert bs.n_words == 7
    assert bs.n_punctuations == 11


def test_get_stats(bs):
    stats = bs.get_stats()
    assert isinstance(stats, dict)
    for key in BASIC_STATS_DESC:
        assert stats[key] == getattr(bs, key)


def test_print_stats(capsys, bs):
    bs.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == 14
