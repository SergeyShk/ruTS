import pytest
import spacy

from ruts import ReadabilityStats
from ruts.constants import (
    BASIC_STATS_DESC,
    DIVERSITY_STATS_DESC,
    MORPHOLOGY_STATS_DESC,
    PUNCTUATIONS,
    READABILITY_STATS_DESC,
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

    yield spacy_nlp

    spacy_nlp.remove_pipe("basic")
    spacy_nlp.remove_pipe("morph")
    spacy_nlp.remove_pipe("readability")
    spacy_nlp.remove_pipe("diversity")


@pytest.fixture(scope="module")
def spacy_doc(spacy_nlp):
    return spacy_nlp(text)


def test_components_names(spacy_nlp):
    assert spacy_nlp.has_pipe("basic") is True
    assert spacy_nlp.has_pipe("morph") is True
    assert spacy_nlp.has_pipe("readability") is True
    assert spacy_nlp.has_pipe("diversity") is True


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


def test_components_filter_punctuation(spacy_doc):
    n_tokens = sum(1 for token in spacy_doc if not token.is_punct and not token.is_space)
    assert n_tokens < len(spacy_doc)
    assert spacy_doc._.basic.n_words == n_tokens
    assert len(spacy_doc._.diversity.words) == n_tokens
    assert len(spacy_doc._.morph.words) == n_tokens
    assert not any(word in PUNCTUATIONS for word in spacy_doc._.diversity.words)
