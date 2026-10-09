import math

import pytest
import spacy

from ruts import (
    BasicStats,
    CohesionStats,
    DiversityStats,
    LexicalStats,
    MorphStats,
    PhonStats,
    StyleStats,
    WordsExtractor,
)
from ruts.corpus import keyness, kwic
from ruts.datasets import FreqDict
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
