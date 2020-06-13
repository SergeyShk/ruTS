import pytest
import spacy
from ruts import (
    BasicStatsComponent,
    DiversityStatsComponent,
    MorphStatsComponent,
    ReadabilityStatsComponent
)
from ruts.constants import (
    BASIC_STATS_DESC,
    DIVERSITY_STATS_DESC,
    MORPHOLOGY_STATS_DESC,
    READABILITY_STATS_DESC
)

text = "Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие черты: полнота значений словарного состава языка или\
    какого-либо его сегмента; тематический, или идеографический способ упорядочения значений слов. Отличительной особенностью тезаурусов по сравнению\
    с формальными онтологиями является выход в сферу лексических значений, установление связей не только между значениями и выражающими их словами,\
    а также между самими значениями (регистрация различных семантических отношений внутри словаря)."

@pytest.fixture(scope='module')
def spacy_nlp():
    spacy_nlp = spacy.blank('ru')
    spacy_nlp.add_pipe(spacy_nlp.create_pipe('sentencizer'))
    bsc = BasicStatsComponent()
    spacy_nlp.add_pipe(bsc, 'basic', last=True)
    msc = MorphStatsComponent()
    spacy_nlp.add_pipe(msc, 'morph', last=True)
    rsc = ReadabilityStatsComponent()
    spacy_nlp.add_pipe(rsc, 'readability', last=True)
    dsc = DiversityStatsComponent()
    spacy_nlp.add_pipe(dsc, 'diversity', last=True)

    yield spacy_nlp

    spacy_nlp.remove_pipe('basic')
    spacy_nlp.remove_pipe('morph')
    spacy_nlp.remove_pipe('readability')
    spacy_nlp.remove_pipe('diversity')

@pytest.fixture(scope='module')
def spacy_doc(spacy_nlp):
    spacy_doc = spacy_nlp(text)
    return spacy_doc

def test_components_names(spacy_nlp):
    assert spacy_nlp.has_pipe('basic') is True
    assert spacy_nlp.has_pipe('morph') is True
    assert spacy_nlp.has_pipe('readability') is True

def test_component_basic(spacy_doc):
    for key in BASIC_STATS_DESC.keys():
        assert hasattr(spacy_doc._.bs, key)

def test_component_morph(spacy_doc):
    for key in MORPHOLOGY_STATS_DESC.keys():
        assert hasattr(spacy_doc._.ms, key)

def test_component_readability(spacy_doc):
    for key in READABILITY_STATS_DESC.keys():
        assert hasattr(spacy_doc._.rs, key)

def test_component_diversity(spacy_doc):
    for key in DIVERSITY_STATS_DESC.keys():
        assert hasattr(spacy_doc._.ds, key)