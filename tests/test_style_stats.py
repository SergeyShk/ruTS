from math import isnan

import pytest
import spacy

from ruts import StyleStats, WordsExtractor
from ruts.constants import STYLE_STATS_DESC
from ruts.style_stats import (
    calc_academic_nausea,
    calc_classic_nausea,
    calc_keyword_density,
    calc_parentheticals,
    calc_phrase_density,
    calc_spam,
    calc_verbal_nouns,
    calc_water,
    calc_zipf_naturalness,
    is_parenthetical,
    is_stopword,
)

text = "Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие черты: полнота\
        значений словарного состава языка или какого-либо его сегмента; тематический, или идеографический способ\
        упорядочения значений слов. Отличительной особенностью тезаурусов по сравнению с формальными онтологиями\
        является выход в сферу лексических значений, установление связей не только между значениями и выражающими их\
        словами, а также между самими значениями (регистрация различных семантических отношений внутри словаря)."
# 15 слов, 11 лексем, спектр частот {1: 8, 2: 2, 3: 1}
riddle = (
    "ног", "нет", "а", "хожу", "рта", "нет", "а", "скажу",
    "когда", "спать", "когда", "вставать", "когда", "работу", "начинать",
)  # fmt: skip


@pytest.fixture(scope="module")
def ss():
    return StyleStats(text)


def test_init_value_error():
    with pytest.raises(ValueError):
        StyleStats("+ _")
    with pytest.raises(ValueError):
        StyleStats(text, top_n=0)


@pytest.mark.parametrize("source", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(source):
    with pytest.raises(TypeError):
        StyleStats(source)


def test_init_doc():
    riddle_text = (
        "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    )
    doc = spacy.blank("ru")(riddle_text)
    assert StyleStats(doc).words == riddle
    assert StyleStats(doc).get_stats() == StyleStats(riddle_text).get_stats()


def test_init_lexemes():
    ss = StyleStats(text, words_extractor=WordsExtractor(use_lexemes=True, lowercase=True))
    assert ss.classic_nausea == pytest.approx(5**0.5)
    assert ss.spam > StyleStats(text).spam


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("и", True),
        ("не", True),
        ("в", True),
        ("он", True),
        ("этот", True),
        ("который", True),
        ("конечно", True),
        ("там", True),
        ("где", True),
        ("почему", True),
        ("нет", True),
        ("надо", True),
        ("ох", True),
        ("мама", False),
        ("быстро", False),
        ("читать", False),
        ("100", False),
    ],
)
def test_is_stopword(word, expected):
    assert is_stopword(word) is expected


def test_classic_nausea(ss):
    assert calc_classic_nausea(riddle) == pytest.approx(3**0.5)
    assert ss.classic_nausea == pytest.approx(3**0.5)
    assert calc_classic_nausea([]) == 0.0


def test_academic_nausea(ss):
    assert calc_academic_nausea(riddle, 1) == pytest.approx(100 * 3 / 15)
    assert calc_academic_nausea(riddle, 3) == pytest.approx(100 * 7 / 15)
    assert calc_academic_nausea(riddle, 100) == 100.0
    assert ss.academic_nausea == pytest.approx(100 * 15 / 61)
    assert StyleStats(text, top_n=3).academic_nausea == pytest.approx(
        calc_academic_nausea(ss.words, 3)
    )


def test_water(ss):
    # стоп-слова: нет (предикатив) x2, а (союз) x2, когда (союз) x3
    assert calc_water(riddle) == pytest.approx(100 * 7 / 15)
    assert calc_water(riddle, stopwords=["нет", "а"]) == pytest.approx(100 * 4 / 15)
    assert calc_water(riddle, stopwords=["НЕТ"]) == pytest.approx(100 * 2 / 15)
    assert calc_water(riddle, stopwords=[]) == 0.0
    assert ss.water == pytest.approx(100 * 18 / 61)
    assert StyleStats(text, stopwords=["и", "или"]).water == pytest.approx(100 * 3 / 61)


def test_spam(ss):
    assert calc_spam(riddle) == pytest.approx(100 * 4 / 15)
    assert calc_spam(["а", "б", "в"]) == 0.0
    assert calc_spam(["а", "а", "а"]) == pytest.approx(200 / 3)
    assert ss.spam == pytest.approx(100 * 5 / 61)


def test_zipf_naturalness(ss):
    # частоты 2, 2 на рангах 2 и 3 при идеальных 1.5 и 1: отклонения 1/3 и 1, ранг 1 не учитывается
    assert calc_zipf_naturalness(riddle) == pytest.approx(100 * (1 - (1 / 3 + 1) / 2))
    assert calc_zipf_naturalness(["а"] * 12 + ["б"] * 6 + ["в"] * 4 + ["г"] * 3) == 100.0
    assert calc_zipf_naturalness(["а"] * 6 + ["б"] * 6 + ["в"] * 6 + ["г"] * 6) == 0.0
    # равномерные частоты дают 0 независимо от их величины
    assert calc_zipf_naturalness(["а", "б", "в", "г"] * 2) == 0.0
    assert calc_zipf_naturalness(["а", "б", "в"] * 3) == 0.0
    # нет рангов для сравнения: одни гапаксы, одна лексема, top_n меньше 2
    assert isnan(calc_zipf_naturalness(["а", "б", "в"]))
    assert isnan(calc_zipf_naturalness(["а", "а", "а"]))
    assert isnan(calc_zipf_naturalness(riddle, top_n=1))
    assert isnan(calc_zipf_naturalness([]))
    assert ss.zipf_naturalness == pytest.approx(100 / 3)
    assert isnan(StyleStats(text, top_n=1).zipf_naturalness)


def test_keyword_density(ss):
    assert calc_keyword_density(riddle, ["когда", "нет а", "КОГДА спать", "ноги", ""]) == {
        "когда": pytest.approx(20.0),
        "нет а": pytest.approx(100 * 2 / 15),
        "КОГДА спать": pytest.approx(100 / 15),
        "ноги": 0.0,
        "": 0.0,
    }
    assert ss.keyword_density("значений", "лексических значений") == {
        "значений": pytest.approx(100 * 3 / 61),
        "лексических значений": pytest.approx(100 / 61),
    }
    assert ss.keyword_density() == {}


officialese = (
    "В целях повышения качества обслуживания, как правило, в кратчайшие сроки "
    "проводится проверка. Конечно, за счёт этого имеет место рост издержек."
)


@pytest.fixture(scope="module")
def os():
    return StyleStats(officialese)


def test_verbal_nouns(os):
    assert os.verbal_nouns == pytest.approx(2 / 11 * 100)
    assert calc_verbal_nouns(["повышение", "качества", "производство", "кот"]) == 50
    assert isnan(calc_verbal_nouns(["и", "в"]))


def test_compound_prepositions(os):
    assert len(os.words) == 20
    assert os.compound_prepositions == pytest.approx(2 / 20 * 100)
    assert calc_phrase_density(["в", "целях", "и", "путем"], ["в целях", "путём"]) == 50


def test_parentheticals(os):
    assert os.parentheticals == pytest.approx(2 / 20 * 100)
    assert calc_parentheticals(["как", "правило", "конечно", "кот"]) == 50
    assert calc_parentheticals(["кот"]) == 0


def test_cliches(os):
    assert os.cliches == pytest.approx(2 / 20 * 100)
    assert StyleStats(officialese, cliches=["имеет место"]).cliches == pytest.approx(1 / 20 * 100)
    assert StyleStats(officialese, cliches=[]).cliches == 0
    assert StyleStats("кот дом", cliches=["", " ", "имеет место"]).cliches == 0


def test_officialese_extractor_independent(os):
    lexemes = StyleStats(
        officialese, words_extractor=WordsExtractor(use_lexemes=True, lowercase=True)
    )
    filtered = StyleStats(
        officialese, words_extractor=WordsExtractor(stopwords=["в", "с", "за"], lowercase=True)
    )
    for stats in (lexemes, filtered):
        assert stats.forms == os.forms
        assert stats.words != os.words
        for key in ("verbal_nouns", "compound_prepositions", "parentheticals", "cliches"):
            assert getattr(stats, key) == pytest.approx(getattr(os, key))


@pytest.mark.parametrize(
    ("word", "expected"),
    [("конечно", True), ("например", True), ("впрочем", True), ("кот", False), ("и", False)],
)
def test_is_parenthetical(word, expected):
    assert is_parenthetical(word) is expected


def test_officialese_doc(os):
    nlp = spacy.blank("ru")
    doc_os = StyleStats(nlp(officialese))
    assert doc_os.get_stats() == os.get_stats()


def test_get_stats(ss):
    stats = ss.get_stats()
    assert isinstance(stats, dict)
    assert list(stats) == list(STYLE_STATS_DESC)
    for key in STYLE_STATS_DESC:
        assert stats[key] == getattr(ss, key)


def test_print_stats(capsys, ss):
    ss.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == len(STYLE_STATS_DESC) + 1
