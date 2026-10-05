import re
from collections import defaultdict
from math import inf, isnan, nextafter
from pathlib import Path

import pytest
import spacy

from ruts import StyleStats, WordsExtractor
from ruts.constants import STYLE_NORMS, STYLE_STATS_DESC
from ruts.exceptions import ParameterError, SourceTypeError, UnknownStatError
from ruts.readability_stats import scale_level
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
    expand_phrases,
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
def nlp():
    pytest.importorskip("ru_core_news_sm")
    return spacy.load("ru_core_news_sm")


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


def test_describe():
    """Прочтение по полосам норм, None для метрик без нормы и неопределенных значений"""
    ss = StyleStats(" ".join(riddle))
    assert {stat: ss.describe(stat) for stat in STYLE_NORMS} == {
        "classic_nausea": "норма Advego",
        "academic_nausea": "выше нормы Advego",
        "water": "высокая водность по Text.ru",
        "spam": "естественный текст по Text.ru",
        "zipf_naturalness": "ниже нормы pr-cy и megaindex",
    }
    assert ss.describe("cliches") is None
    hapaxes = StyleStats("мама мыла раму")
    assert isnan(hapaxes.zipf_naturalness)
    assert hapaxes.describe("zipf_naturalness") is None
    assert StyleStats("слово " * 49).describe("classic_nausea") == "у верхней границы нормы Advego"
    for stat in ("flesch_reading_easy", "words", ["water"]):
        with pytest.raises(UnknownStatError):
            ss.describe(stat)


@pytest.mark.parametrize(
    ("stat", "value", "expected"),
    [
        ("classic_nausea", 7, "у верхней границы нормы Advego"),
        ("classic_nausea", nextafter(7, inf), "выше нормы Advego"),
        ("classic_nausea", 5, "норма Advego"),
        ("academic_nausea", 15, "норма Advego"),
        ("academic_nausea", 5, "норма Advego"),
        ("water", 30, "избыточная водность по Text.ru"),
        ("water", 15, "избыточная водность по Text.ru"),
        ("spam", 60, "SEO-оптимизированный текст по Text.ru"),
        ("spam", 30, "SEO-оптимизированный текст по Text.ru"),
        ("zipf_naturalness", 50, "норма pr-cy и megaindex"),
    ],
)
def test_style_norms_bounds(stat, value, expected):
    """Полоса «больше X» не включает X"""
    assert scale_level(value, STYLE_NORMS[stat]) == expected


def doc_norms(page):
    """Полосы норм из таблицы страницы: метрика - нижние границы по убыванию и подписи"""
    text = (Path(__file__).parent.parent / "docs" / "stats" / page).read_text(encoding="utf-8")
    section = text.split("{ #norms }", 1)[1].split("\n## ", 1)[0]
    rows = re.findall(
        r"^\| `(\w+)` \| `([\[(])([\d.]+)[;,] ([\d.]+|∞)([\])])` \| ([^|]+?) \|$",
        section,
        re.MULTILINE,
    )
    norms, lower = defaultdict(list), {}
    for stat, opening, low, high, closing, label in rows:
        if stat in lower:
            # полосы смыкаются, и граница входит ровно в одну из них
            assert high == lower[stat][0]
            assert (lower[stat][1], closing) in {("(", "]"), ("[", ")")}
        lower[stat] = (low, opening)
        norms[stat].append((float(low) if opening == "[" else nextafter(float(low), inf), label))
    return {stat: tuple(bands) for stat, bands in norms.items()}


def test_style_norms_follow_docs():
    """Полосы норм совпадают с таблицами документации на обоих языках"""
    assert doc_norms("style_stats.md") == STYLE_NORMS
    english = doc_norms("style_stats.en.md")
    assert {stat: [low for low, _ in bands] for stat, bands in english.items()} == {
        stat: [low for low, _ in bands] for stat, bands in STYLE_NORMS.items()
    }


def test_hyphenated_words_doc(nlp):
    source = "Во-первых, кот спит. По-видимому, он устал."
    doc = nlp(source)
    assert StyleStats(doc).words == ("во-первых", "кот", "спит", "по-видимому", "он", "устал")
    assert (
        StyleStats(doc).parentheticals
        == StyleStats(source).parentheticals
        == pytest.approx(200 / 6)
    )


@pytest.mark.parametrize("parameter", ["stopwords", "cliches"])
def test_init_string_list(parameter):
    with pytest.raises(SourceTypeError):
        StyleStats(text, **{parameter: "и в"})


def test_init_parameters_before_source():
    with pytest.raises(ParameterError):
        StyleStats("+ _", top_n=0)


def test_cliches_verb_forms():
    forms = "Он довёл до сведения коллег, это имело место, работа оставляла желать лучшего"
    assert StyleStats(forms).cliches == 25.0


def test_expand_phrases():
    words = ["меры", "приняты", "принял", "к", "сведению", "стали", "в", "свете"]
    assert expand_phrases(words, ["принять к сведению", "в свете", "стать причиной"]) == {
        "принять к сведению": "принять к сведению",
        "в свете": "в свете",
        "стать причиной": "стать причиной",
        "принял к сведению": "принять к сведению",
        "приняты к сведению": "принять к сведению",
        "стали причиной": "стать причиной",
    }
    assert expand_phrases(["принимать"], ["принимать меры", "принять меры"])["принимать меры"] == (
        "принимать меры"
    )


def test_cliches_reflexive_and_negated():
    forms = "Это принимается во внимание, мы не остались в стороне, довожу до вашего сведения"
    assert StyleStats(forms).cliches == pytest.approx(3 / 13 * 100)


def test_phrase_density_iterator():
    with pytest.raises(SourceTypeError):
        calc_phrase_density(["имеет", "место"], iter(["иметь место"]))


def test_phrase_density_all_lexemes():
    assert calc_phrase_density(["они", "стоят", "того"], ["стоить того"]) == pytest.approx(100 / 3)
