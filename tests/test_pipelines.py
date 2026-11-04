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
    load_pipeline,
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


def test_rumorph_sees_anyseg_sentences():
    """rumorph разбирает слова в контексте предложений anySeg: абзац без точки - свое предложение"""
    text = "Что нового\n\nДверь открылась. Мы вошли."
    doc = load_nlp()(text)
    assert MorphStats(doc).pos == MorphStats(text).pos
    assert (doc[0].text, doc[0].pos_) == ("Что", "PRON")


def test_imperative_labels():
    """Совместность и переходность глагола Doc - по разбору с его признаками, как у строки"""
    text = "Извините меня. Садитесь, прошу вас. Посмотрите сюда."
    stats = MorphStats(load_nlp()(text)).get_stats("involvement", "transitivity")
    assert stats == MorphStats(text).get_stats("involvement", "transitivity")
    assert stats["involvement"]["Ex"] == 3


def test_load_pipeline_options(tmp_path):
    nlp = load_pipeline(exclude="ner")
    assert nlp.pipe_names == [
        "anyseg_sentencizer",
        "rumorph",
        "tok2vec",
        "parser",
        "attribute_ruler",
    ]
    nlp.to_disk(tmp_path)
    assert load_pipeline(tmp_path).pipe_names == nlp.pipe_names
    assert isinstance(load_pipeline(tmp_path).tokenizer, Tokenizer)
    parsed = load_pipeline(disable=["parser"])
    parsed.enable_pipe("parser")
    text = "Что нового\n\nБыстрый импорт. Меньше ошибок\n\nСписок изменений"
    assert BasicStats(parsed(text)).n_sents == BasicStats(text).n_sents == 4
