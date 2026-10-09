import math
import re
import unicodedata

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
import spacy
from spacy.tokens import Doc

from ruts import (
    BasicStats,
    CharNgramsExtractor,
    CohesionStats,
    DiversityStats,
    LexicalStats,
    MorphStats,
    PhonStats,
    ReadabilityStats,
    SentsExtractor,
    StyleStats,
    WordsExtractor,
)
from ruts.basic_stats import punctuation_profile
from ruts.corpus import collocations, dispersion, keyness, kwic
from ruts.datasets import FreqDict
from ruts.utils import iter_text_sents, strip_doc_marks, strip_marks
from ruts.visualizers import dispersion_plot, wordtree
from tests.datasets.test_freq2011 import write_dict

PLAIN = (
    "Мороз и солнце; день чудесный! Ещё ты дремлешь, друг прелестный. Пора, красавица, "
    "проснись: открой сомкнуты негой взоры навстречу северной Авроры, звездою севера явись!"
)
MARKED = (
    "Моро́з и со­лнце; день чуде́сный! Ещё ты дре́млешь, друг "
    "преле́стный. Пора́, краса̀вица, проснись: откро́й сомкну́ты "
    "не́гой взо́ры навстре­чу се́верной Авро́ры, звездо́ю "
    "се́вера яви́сь!"
)


def same(a: dict, b: dict) -> bool:
    """Равенство статистик, где nan равен nan"""

    def equal(x, y):
        return x == y or (isinstance(x, float) and math.isnan(x) and math.isnan(y))

    return a.keys() == b.keys() and all(equal(a[key], b[key]) for key in a)


@pytest.fixture(scope="module")
def freq_dict(tmp_path_factory):
    path = tmp_path_factory.mktemp("dicts")
    write_dict(path)
    return FreqDict(data_dir=path)


def test_words():
    assert WordsExtractor().extract(MARKED) == WordsExtractor().extract(PLAIN)
    marked, plain = BasicStats(MARKED), BasicStats(PLAIN)
    assert (marked.n_words, marked.n_syllables, marked.n_letters) == (
        plain.n_words,
        plain.n_syllables,
        plain.n_letters,
    )


@pytest.mark.parametrize("stats", [DiversityStats, MorphStats, StyleStats, PhonStats])
def test_stats(stats):
    """Текст со знаками ударения и мягкими переносами дает те же статистики, что без них"""
    nlp = spacy.blank("ru")
    expected = stats(PLAIN).get_stats()
    assert same(stats(MARKED).get_stats(), expected)
    assert same(stats(nlp(MARKED)).get_stats(), stats(nlp(PLAIN)).get_stats())


def test_lexical_stats(freq_dict):
    nlp = spacy.blank("ru")
    for source in (MARKED, nlp(MARKED)):
        marked = LexicalStats(source, freq_dict=freq_dict)
        plain = LexicalStats(PLAIN if isinstance(source, str) else nlp(PLAIN), freq_dict=freq_dict)
        assert marked.lemmas == plain.lemmas
        assert same(marked.get_stats(), plain.get_stats())


def test_cohesion_stats():
    assert same(CohesionStats(MARKED).get_stats(), CohesionStats(PLAIN).get_stats())


def test_kwic():
    lines = kwic(MARKED, "мороз", window=2)
    assert [line.keyword for line in lines] == ["Моро́з"]
    assert [line.keyword for line in kwic(PLAIN, "моро́з")] == ["Мороз"]
    assert [line.keyword for line in kwic(MARKED, "солнце", by_lemma=True)] == ["со­лнце"]


def test_keyness(freq_dict):
    keywords = {k.word: k.freq_target for k in keyness(["ко́т", "кот"], freq_dict)}
    assert keywords["кот"] == 2


def test_char_ngrams():
    for within_words in (False, True):
        extractor = CharNgramsExtractor(n=3, lowercase=True, within_words=within_words)
        assert extractor.extract(MARKED) == extractor.extract(PLAIN)


def test_latin_stressed_vowels():
    """Ударная гласная латиницей внутри русского слова - буква этого слова"""
    assert WordsExtractor().extract("Он чтó-то сказал, Домá") == ("Он", "что-то", "сказал", "Дома")
    assert MorphStats("чтó").get_stats() == MorphStats("что").get_stats()


SENTS = "У него уродливый нос. Серое чудище стоит. Он не найдёт. Разве можно найти?"
MARKED_SENTS = "У него́ уро́дливый но́с. Се́рое чу́дище стои́т. Он не найдё́т. Ра́зве мо́жно найти́?"


def test_sentences():
    """Хвост слова после знака («но́с.») не принимается за сокращение"""
    sents = list(iter_text_sents(MARKED_SENTS))
    assert all(MARKED_SENTS[start:stop] == sent for start, stop, sent in sents)
    assert [strip_marks(sent) for _, _, sent in sents] == list(SentsExtractor().extract(SENTS))
    assert len(SentsExtractor().extract(MARKED_SENTS)) == 4
    assert kwic(MARKED_SENTS, "нос серое") == []
    assert SentsExtractor().extract("\u00ad\u00ad") == ()


@pytest.mark.parametrize(
    "text",
    [MARKED, MARKED_SENTS, unicodedata.normalize("NFD", PLAIN)],
    ids=["marks", "sentences", "nfd"],
)
def test_basic_readability(text):
    """Знаки, мягкие переносы и NFD не меняют ни слов, ни символов, ни предложений"""
    nlp = spacy.blank("ru")
    plain = strip_marks(text)
    for marked, clean in ((text, plain), (nlp(text), nlp(plain))):
        assert same(
            BasicStats(marked, normalize=True).get_stats(),
            BasicStats(clean, normalize=True).get_stats(),
        )
        assert same(ReadabilityStats(marked).get_stats(), ReadabilityStats(clean).get_stats())
    assert same(CohesionStats(text).get_stats(), CohesionStats(plain).get_stats())
    assert punctuation_profile(text) == pytest.approx(punctuation_profile(plain), nan_ok=True)


@pytest.mark.parametrize("stats", [DiversityStats, MorphStats, StyleStats, PhonStats])
def test_nfd(stats):
    """Й и ё из двух символов разбираются как одна буква"""
    assert same(stats(unicodedata.normalize("NFD", PLAIN)).get_stats(), stats(PLAIN).get_stats())


def test_custom_tokenizer():
    extractor = WordsExtractor(tokenizer=re.compile(r"\W+"))
    assert extractor.extract("Моро́з и со­лнце") == ("Мороз", "и", "солнце")


PLAIN_WORDS = ["глаза", "смотрели", "на", "глаза", "и", "глаза", "смотрели"]
MARKED_WORDS = ["гла́за", "смо́трели", "на", "гла́за", "и", "гла\u00adза", "смотрели"]


@pytest.mark.parametrize("node", ["глаза", "гла́за"])
@pytest.mark.parametrize(
    "words",
    [
        PLAIN_WORDS,
        MARKED_WORDS,
        tuple(MARKED_WORDS),
        np.array(MARKED_WORDS),
        pd.Series(MARKED_WORDS),
    ],
    ids=["plain", "marked", "tuple", "array", "series"],
)
def test_core_queries(node, words):
    """Слова и слово запроса со знаками и без находятся одинаково"""
    assert collocations(words, node=node, min_freq=1) == collocations(
        PLAIN_WORDS, node="глаза", min_freq=1
    )
    assert dispersion(words, parts=2, word=node)[0].freq == 3
    assert wordtree([words], node).source == wordtree([PLAIN_WORDS], "глаза").source
    ax = dispersion_plot(words, [node])
    assert ax.get_yticklabels()[0].get_text() == "глаза"
    plt.close("all")


def test_kwic_case_sensitive():
    text = "Стои́т моро́з. Моро́з и солнце. Мороз крепчал. Домá стоят."
    for source in (text, spacy.blank("ru")(text)):
        assert len(kwic(source, "Мороз", ignore_case=False)) == 2
        assert len(kwic(source, "Дома", ignore_case=False)) == 1
        assert len(kwic(source, "мороз", ignore_case=False)) == 1


def test_strip_doc_marks():
    nlp = spacy.blank("ru")
    doc = Doc(
        nlp.vocab,
        words=["Моро́з", "­", "и", "солнце", ".", "День", "."],
        spaces=[True, True, True, False, True, False, False],
        sent_starts=[True, False, False, False, False, True, False],
    )
    clean = strip_doc_marks(doc)
    assert [token.text for token in clean] == ["Мороз", "и", "солнце", ".", "День", "."]
    assert clean.text == "Мороз и солнце. День."
    assert [sent.text for sent in clean.sents] == ["Мороз и солнце.", "День."]
    plain = nlp("Мороз и солнце")
    assert strip_doc_marks(plain) is plain
    leading = Doc(nlp.vocab, words=["\u00ad", "Мороз"], spaces=[True, False])
    assert strip_doc_marks(leading).text == "Мороз"
