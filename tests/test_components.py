import pytest
import spacy

from ruts import DiversityStats, PhonStats, ReadabilityStats, StyleStats, SyntaxStats
from ruts.constants import (
    BASIC_STATS_DESC,
    DIVERSITY_STATS_DESC,
    MORPHOLOGY_STATS_DESC,
    PHON_STATS_DESC,
    PUNCTUATIONS,
    READABILITY_STATS_DESC,
    STYLE_STATS_DESC,
    SYNTAX_STATS_DESC,
)

text = (
    "Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие черты: полнота значений\
    словарного состава языка или какого-либо его сегмента; тематический, или идеографический способ упорядочения\
    значений слов. Отличительной особенностью тезаурусов по сравнению с формальными онтологиями является выход в сферу\
    лексических значений, установление связей не только между значениями и выражающими их словами, а также между самими\
    значениями (регистрация различных семантических отношений внутри словаря)."
)


@pytest.fixture(scope="module")
def spacy_nlp():
    spacy_nlp = spacy.blank("ru")
    spacy_nlp.add_pipe("sentencizer")
    spacy_nlp.add_pipe("basic", last=True)
    spacy_nlp.add_pipe("morph", last=True)
    spacy_nlp.add_pipe("readability", last=True)
    spacy_nlp.add_pipe("diversity", last=True)
    spacy_nlp.add_pipe("style", last=True)
    spacy_nlp.add_pipe("phon", last=True)

    yield spacy_nlp

    spacy_nlp.remove_pipe("basic")
    spacy_nlp.remove_pipe("morph")
    spacy_nlp.remove_pipe("readability")
    spacy_nlp.remove_pipe("diversity")
    spacy_nlp.remove_pipe("style")
    spacy_nlp.remove_pipe("phon")


@pytest.fixture(scope="module")
def spacy_doc(spacy_nlp):
    return spacy_nlp(text)


def test_components_names(spacy_nlp):
    assert spacy_nlp.has_pipe("basic") is True
    assert spacy_nlp.has_pipe("morph") is True
    assert spacy_nlp.has_pipe("readability") is True
    assert spacy_nlp.has_pipe("diversity") is True
    assert spacy_nlp.has_pipe("style") is True
    assert spacy_nlp.has_pipe("phon") is True


def test_component_basic(spacy_doc):
    for key in BASIC_STATS_DESC:
        assert hasattr(spacy_doc._.basic, key)


def test_component_morph(spacy_doc):
    for key in MORPHOLOGY_STATS_DESC:
        assert hasattr(spacy_doc._.morph, key)


def test_component_readability(spacy_doc):
    for key in READABILITY_STATS_DESC:
        assert hasattr(spacy_doc._.readability, key)


def test_component_diversity(spacy_doc):
    for key in DIVERSITY_STATS_DESC:
        assert hasattr(spacy_doc._.diversity, key)


def test_component_readability_preset(spacy_doc):
    nlp = spacy.blank("ru")
    nlp.add_pipe("sentencizer")
    nlp.add_pipe("readability", name="readability_fiction", config={"preset": "fiction"})
    doc = nlp(text)
    assert doc._.readability_fiction.preset == "fiction"
    assert (
        doc._.readability_fiction.flesch_kincaid_grade
        != spacy_doc._.readability.flesch_kincaid_grade
    )
    assert doc._.readability_fiction.flesch_kincaid_grade == pytest.approx(
        ReadabilityStats(doc, preset="fiction").flesch_kincaid_grade
    )


def test_component_style(spacy_doc):
    for key in STYLE_STATS_DESC:
        assert hasattr(spacy_doc._.style, key)
    assert spacy_doc._.style.get_stats() == StyleStats(spacy_doc).get_stats()


def test_component_phon(spacy_doc):
    for key in PHON_STATS_DESC:
        assert hasattr(spacy_doc._.phon, key)
    assert spacy_doc._.phon.get_stats() == PhonStats(spacy_doc).get_stats()


def test_component_phon_params(spacy_doc):
    nlp = spacy.blank("ru")
    nlp.add_pipe("phon", name="phon_custom", config={"window_len": 5})
    doc = nlp(text)
    assert doc._.phon_custom.window_len == 5
    assert doc._.phon_custom.alliteration == pytest.approx(
        PhonStats(doc, window_len=5).alliteration
    )
    assert doc._.phon_custom.alliteration != pytest.approx(spacy_doc._.phon.alliteration)


def test_component_style_params(spacy_doc):
    nlp = spacy.blank("ru")
    nlp.add_pipe("style", name="style_custom", config={"stopwords": ["и", "или"], "top_n": 3})
    doc = nlp(text)
    custom = doc._.style_custom
    assert custom.stopwords == ("и", "или")
    assert custom.water == pytest.approx(StyleStats(doc, stopwords=["и", "или"]).water)
    assert custom.water != spacy_doc._.style.water
    assert custom.academic_nausea == pytest.approx(StyleStats(doc, top_n=3).academic_nausea)


def test_component_diversity_params(spacy_doc):
    nlp = spacy.blank("ru")
    nlp.add_pipe("sentencizer")
    nlp.add_pipe(
        "diversity",
        name="diversity_custom",
        config={"window_len": 20, "mtld_threshold": 0.9, "log_base": 2.718281828459045},
    )
    doc = nlp(text)
    custom = doc._.diversity_custom
    assert (custom.window_len, custom.mtld_threshold, custom.log_base) == (
        20,
        0.9,
        2.718281828459045,
    )
    assert custom.mattr != spacy_doc._.diversity.mattr
    assert custom.mattr == pytest.approx(DiversityStats(doc, window_len=20).mattr)
    assert custom.mttr == pytest.approx(DiversityStats(doc, log_base=2.718281828459045).mttr)


def test_components_filter_punctuation(spacy_doc):
    n_tokens = sum(1 for token in spacy_doc if not token.is_punct and not token.is_space)
    assert n_tokens < len(spacy_doc)
    assert spacy_doc._.basic.n_words == n_tokens
    assert len(spacy_doc._.diversity.words) == n_tokens
    assert len(spacy_doc._.morph.words) == n_tokens
    assert not any(word in PUNCTUATIONS for word in spacy_doc._.diversity.words)


@pytest.fixture(scope="module")
def parsed_nlp():
    pytest.importorskip("ru_core_news_sm")
    parsed_nlp = spacy.load("ru_core_news_sm")
    parsed_nlp.add_pipe("syntax", last=True)

    yield parsed_nlp

    parsed_nlp.remove_pipe("syntax")


def test_component_syntax(parsed_nlp):
    doc = parsed_nlp(text)
    assert parsed_nlp.has_pipe("syntax") is True
    for key in SYNTAX_STATS_DESC:
        assert hasattr(doc._.syntax, key)
    assert doc._.syntax.get_stats() == SyntaxStats(doc).get_stats()


def test_component_syntax_requires_parser():
    nlp = spacy.blank("ru")
    nlp.add_pipe("sentencizer")
    nlp.add_pipe("syntax", last=True)
    with pytest.raises(ValueError):
        nlp(text)
