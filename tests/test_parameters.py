"""Функции библиотеки проверяют свои числа и списки слов так же, как ядро"""

import pytest

from ruts import (
    CohesionStats,
    DiversityStats,
    LexicalStats,
    MorphStats,
    PhonStats,
    StyleStats,
    WordsExtractor,
)
from ruts.cohesion_stats import find_connectors
from ruts.corpus import compare_corpora, corpus_features, function_words_profile, keyness, kwic
from ruts.corpus.compare import sentence_rhythm, split_windows, text_features
from ruts.datasets import FreqDict
from ruts.exceptions import ParameterError, SourceTypeError
from ruts.lexical_stats import calc_surprisal
from ruts.phon_stats import (
    calc_alliteration,
    calc_assonance,
    calc_consonant_clusters,
    calc_cv_entropy,
    calc_hiatus,
)
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
    is_stopword,
)
from ruts.syllables import count_syllables, stress_type, syllabify
from ruts.utils import find_phrases
from ruts.visualizers import highlight

TEXT = "Кот спит на окне. Собака ест на полу, и кот на нее смотрит."
WORDS = ["кот", "спит", "на", "окне", "собака", "ест", "на", "полу"]

INTEGERS = {
    "StyleStats(top_n)": lambda: StyleStats(TEXT, top_n=1.5),
    "calc_academic_nausea(top_n)": lambda: calc_academic_nausea(WORDS, top_n=2.0),
    "calc_zipf_naturalness(top_n)": lambda: calc_zipf_naturalness(WORDS, top_n=True),
    "PhonStats(window_len)": lambda: PhonStats(TEXT, window_len=2.5),
    "calc_alliteration(window_len)": lambda: calc_alliteration(WORDS, window_len=3.0),
    "calc_assonance(window_len)": lambda: calc_assonance(WORDS, window_len=True),
    "kwic(window)": lambda: kwic(TEXT, "кот", window=1.5),
    "split_windows(window)": lambda: split_windows(TEXT, 1.5),
    "split_windows(window=True)": lambda: split_windows(TEXT, True),
    "split_windows(min_words)": lambda: split_windows(TEXT, 10, min_words=2.0),
    "corpus_features(window)": lambda: corpus_features([TEXT], window=2.5),
    "compare_corpora(n_bootstrap)": lambda: compare_corpora([TEXT], [TEXT], n_bootstrap=1.5),
    "find_connectors(pos)": lambda: find_connectors(["но", "не"], pos=["CCONJ"]),
}

NOT_STRINGS = [1, 2]
WORD_LISTS = {
    "function_words_profile": lambda: function_words_profile(NOT_STRINGS),
    "calc_classic_nausea": lambda: calc_classic_nausea(NOT_STRINGS),
    "calc_academic_nausea": lambda: calc_academic_nausea(NOT_STRINGS),
    "calc_water": lambda: calc_water(NOT_STRINGS),
    "calc_water(stopwords)": lambda: calc_water(WORDS, stopwords=NOT_STRINGS),
    "calc_spam(iterator)": lambda: calc_spam(iter(WORDS)),
    "calc_zipf_naturalness": lambda: calc_zipf_naturalness(NOT_STRINGS),
    "calc_keyword_density(keywords)": lambda: calc_keyword_density(WORDS, NOT_STRINGS),
    "calc_verbal_nouns": lambda: calc_verbal_nouns(NOT_STRINGS),
    "expand_phrases": lambda: expand_phrases(NOT_STRINGS, []),
    "calc_phrase_density(phrases)": lambda: calc_phrase_density(WORDS, "в связи с"),
    "calc_parentheticals": lambda: calc_parentheticals(NOT_STRINGS),
    "calc_consonant_clusters": lambda: calc_consonant_clusters(NOT_STRINGS),
    "calc_hiatus": lambda: calc_hiatus(NOT_STRINGS),
    "calc_cv_entropy": lambda: calc_cv_entropy(NOT_STRINGS),
    "calc_alliteration": lambda: calc_alliteration(NOT_STRINGS),
    "calc_assonance": lambda: calc_assonance("кот"),
    "calc_surprisal": lambda: calc_surprisal(NOT_STRINGS, None),
    "find_phrases": lambda: find_phrases(NOT_STRINGS, []),
    "StyleStats(stopwords)": lambda: StyleStats(TEXT, stopwords=NOT_STRINGS),
    "StyleStats(cliches)": lambda: StyleStats(TEXT, cliches="в связи с"),
    "corpus_features": lambda: corpus_features(NOT_STRINGS),
    "compare_corpora": lambda: compare_corpora([TEXT], NOT_STRINGS),
    "DiversityStats(words_extractor)": lambda: DiversityStats(TEXT, words_extractor="x"),
    "PhonStats(words_extractor)": lambda: PhonStats(TEXT, words_extractor="x"),
    "StyleStats(words_extractor)": lambda: StyleStats(TEXT, words_extractor="x"),
    "MorphStats(words_extractor)": lambda: MorphStats(TEXT, words_extractor="x"),
    "LexicalStats(words_extractor)": lambda: LexicalStats(TEXT, words_extractor="x"),
    "CohesionStats(sents_extractor)": lambda: CohesionStats(TEXT, sents_extractor="x"),
    "CohesionStats(words_extractor)": lambda: CohesionStats(TEXT, words_extractor="x"),
    "LexicalStats(freq_dict)": lambda: LexicalStats(TEXT, freq_dict="x"),
    "calc_surprisal(freq_dict)": lambda: calc_surprisal(WORDS, "x"),
    "text_features": lambda: text_features(None),
    "split_windows": lambda: split_windows(WORDS),
    "sentence_rhythm": lambda: sentence_rhythm("текст"),
    "sentence_rhythm(elements)": lambda: sentence_rhythm(["4", "8"]),
    "kwic(keyword)": lambda: kwic(TEXT, 5),
    "syllabify": lambda: syllabify(None),
    "count_syllables": lambda: count_syllables(["кот"]),
    "stress_type": lambda: stress_type(5),
    "is_stopword": lambda: is_stopword(None),
    "find_connectors": lambda: find_connectors("но не"),
    "find_connectors(pos)": lambda: find_connectors(["но", "не"], pos="CC"),
    "CohesionStats(connectors)": lambda: CohesionStats(TEXT, connectors=["потому что"]),
    "CohesionStats(connector)": lambda: CohesionStats(TEXT, connectors={"потому что": "causal"}),
    "compare_corpora(features)": lambda: compare_corpora([TEXT], [TEXT], features=1),
    "corpus_features(features)": lambda: corpus_features([TEXT], features="text_features"),
    "WordsExtractor(stopwords)": lambda: WordsExtractor(stopwords=NOT_STRINGS),
    "highlight(stopwords)": lambda: highlight(TEXT, stopwords=NOT_STRINGS),
    "highlight(cliches)": lambda: highlight(TEXT, cliches="в связи с"),
}


@pytest.mark.parametrize("call", INTEGERS.values(), ids=INTEGERS)
def test_integers(call):
    with pytest.raises(ParameterError):
        call()


@pytest.mark.parametrize("call", WORD_LISTS.values(), ids=WORD_LISTS)
def test_word_lists(call):
    with pytest.raises(SourceTypeError):
        call()


def test_sets_of_words():
    """Стоп-слова, ключевые слова и штампы - наборы, порядок не важен"""
    assert calc_water(WORDS, stopwords={"на"}) == calc_water(WORDS, stopwords=["на"])
    assert calc_keyword_density(WORDS, {"кот"}) == calc_keyword_density(WORDS, ["кот"])
    assert calc_phrase_density(WORDS, {"на окне"}) == calc_phrase_density(WORDS, ["на окне"])
    assert StyleStats(TEXT, stopwords={"на"}).water == StyleStats(TEXT, stopwords=["на"]).water
    assert (
        StyleStats(TEXT, cliches={"на окне"}).cliches
        == StyleStats(TEXT, cliches=["на окне"]).cliches
    )
    layers = ["stopwords", "cliches"]
    assert (
        highlight(TEXT, layers=layers, stopwords={"на"}, cliches={"на окне"}).highlights
        == highlight(TEXT, layers=layers, stopwords=["на"], cliches=["на окне"]).highlights
    )


def test_compare_corpora_checks_before_the_features():
    calls = []

    def features(text):
        calls.append(text)
        return {"chars": float(len(text))}

    with pytest.raises(ParameterError):
        compare_corpora([TEXT], [TEXT], features=features, n_bootstrap=1.5)
    with pytest.raises(ParameterError):
        compare_corpora([TEXT], [TEXT], window=2.5, features=features)
    with pytest.raises(ParameterError):
        compare_corpora([TEXT], [TEXT], features=features, seed=-1)
    with pytest.raises(ParameterError):
        compare_corpora([TEXT], [TEXT], features=features, labels=("diff", "B"))
    with pytest.raises(SourceTypeError):
        compare_corpora([TEXT], NOT_STRINGS, features=features)
    assert calls == []


def test_cohesion_checks_the_connectors_before_parsing():
    # Текст разбирается долго, а неверный словарь отвергается сразу
    with pytest.raises(SourceTypeError):
        CohesionStats("кот спит " * 200_000, connectors=["потому что"])


def test_keyness_checks_before_the_dictionary(tmp_path):
    """Неверные параметры и цель отвергаются до чтения частотного словаря"""
    freq_dict = FreqDict(data_dir=tmp_path)
    with pytest.raises(ParameterError):
        keyness(["кот"], freq_dict, measure="x")
    with pytest.raises(SourceTypeError):
        keyness("кот спит", freq_dict)
    with pytest.raises(SourceTypeError):
        keyness({"кот": 1.5}, freq_dict)
