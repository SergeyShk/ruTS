import pytest
import spacy

from ruts.constants import (
    BASIC_STATS_DESC,
    DIVERSITY_STATS_DESC,
    MORPHOLOGY_STATS_DESC,
    READABILITY_STATS_DESC,
)

text = "Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие черты: полнота значений\
    словарного состава языка или какого-либо его сегмента; тематический, или идеографический способ упорядочения\
    значений слов. Отличительной особенностью тезаурусов по сравнению с формальными онтологиями является выход в сферу\
    лексических значений, установление связей не только между значениями и выражающими их словами, а также между самими\
    значениями (регистрация различных семантических отношений внутри словаря)."


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
    spacy_doc = spacy_nlp(text)
    return spacy_doc


def test_components_names(spacy_nlp):
    assert spacy_nlp.has_pipe("basic") is True
    assert spacy_nlp.has_pipe("morph") is True
    assert spacy_nlp.has_pipe("readability") is True
    assert spacy_nlp.has_pipe("diversity") is True


def test_component_basic(spacy_doc):
    for key in BASIC_STATS_DESC.keys():
        assert hasattr(spacy_doc._.basic, key)


def test_component_morph(spacy_doc):
    for key in MORPHOLOGY_STATS_DESC.keys():
        assert hasattr(spacy_doc._.morph, key)


def test_component_readability(spacy_doc):
    for key in READABILITY_STATS_DESC.keys():
        assert hasattr(spacy_doc._.readability, key)


def test_component_diversity(spacy_doc):
    for key in DIVERSITY_STATS_DESC.keys():
        assert hasattr(spacy_doc._.diversity, key)
