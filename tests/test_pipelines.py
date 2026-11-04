"""Классы и компоненты на рекомендуемом конвейере и на обычном ru_core_news_sm"""

import pytest
from anyseg.spacy import Tokenizer

from ruts import (
    BasicStats,
    CohesionStats,
    DiversityStats,
    MorphStats,
    PhonStats,
    ReadabilityStats,
    StyleStats,
    SyntaxStats,
)
from ruts.constants import SYNTAX_STATS_DESC
from tests.pipelines import load_model_nlp, load_nlp

TEXT = (
    "Мы стали ждать, т.е. сидеть у окна.\n\nНож сделан из стали! — Нет, — сказал он, — не пойду."
)
CLASSES = [BasicStats, CohesionStats, DiversityStats, MorphStats, PhonStats, StyleStats]


@pytest.fixture(scope="module", params=["anyseg", "model"])
def pipeline(request):
    return load_nlp() if request.param == "anyseg" else load_model_nlp()


@pytest.mark.parametrize("stats_class", CLASSES)
def test_stats_keys(pipeline, stats_class):
    """На обоих конвейерах классы дают те же статистики, что у строки"""
    assert set(stats_class(pipeline(TEXT)).get_stats()) == set(stats_class(TEXT).get_stats())


def test_syntax_and_readability(pipeline):
    doc = pipeline(TEXT)
    assert set(SyntaxStats(doc).get_stats()) == set(SYNTAX_STATS_DESC)
    assert SyntaxStats(doc).n_sents == BasicStats(doc).n_sents
    assert ReadabilityStats(doc).get_stats().keys() == ReadabilityStats(TEXT).get_stats().keys()


def test_anyseg_doc_as_string():
    """С токенами и предложениями anySeg и морфологией ruMorph Doc размечается, как строка"""
    doc = load_nlp()(TEXT)
    for stats_class in CLASSES:
        assert stats_class(doc).get_stats() == stats_class(TEXT).get_stats(), stats_class.__name__
    assert MorphStats(doc).tags == MorphStats(TEXT).tags
    assert CohesionStats(doc).lemmas == CohesionStats(TEXT).lemmas


def test_components_keep_anyseg_tokenizer():
    """Компоненты не меняют токенизатор anySeg: правила тире нужны только токенизатору spaCy"""
    nlp = load_nlp()
    tokenizer, config = nlp.tokenizer, nlp.config["nlp"]["tokenizer"]
    nlp.add_pipe("ruts_basic", name="basic", last=True)
    assert nlp.tokenizer is tokenizer and isinstance(nlp.tokenizer, Tokenizer)
    assert nlp.config["nlp"]["tokenizer"] == config
    doc = nlp("-Нет -сказал он.")
    assert [token.text for token in doc] == ["-", "Нет", "-", "сказал", "он", "."]
    assert doc._.basic.n_words == BasicStats("-Нет -сказал он.").n_words == 3


def test_reflexive_personal_forms():
    """Личная форма на -шься в рекомендуемом конвейере - сказуемое придаточной клаузы,
    а теггер ru_core_news_sm размечает ее инфинитивом"""
    text = "Я знаю, что ты боишься."
    assert SyntaxStats(load_nlp()(text)).subordinate_clauses_per_sent == 1.0
    model = SyntaxStats(load_model_nlp()(text))
    assert (model.subordinate_clauses_per_sent, model.infinitive_clauses_per_sent) == (0.0, 1.0)
