"""Ошибки корпусных функций - по-русски: латиница в сообщении - только имена параметров,
типов и значений"""

import pickle
import re

import pandas as pd
import pytest
import spacy

from ruts import corpus
from ruts.corpus import FrequencyReference
from ruts.exceptions import RutsError

WORDS = ["кот", "спит", "кот"]
UNITS = {"a": ["кот"], "b": ["пес"]}
TEN = ["кот"] * 10
# Латиница сообщений: имена параметров, типов и значений, N-граммы и p-значения
NAMES = {
    "words", "target", "reference", "samples", "corpora", "preferred", "avoided", "window",
    "step", "top_n", "n", "n_mfw", "segment_size", "n_bootstrap", "seed", "culling",
    "positive", "min_freq", "size", "missing", "key", "keep", "fold", "width", "values_a",
    "p_values", "left", "right", "str", "int", "NoneType", "Doc", "DataFrame", "Generator",
    "numpy", "FrequencyReference", "WordsExtractor", "x", "up", "corpus", "list",
    "N", "p", "side", "node", "texts", "a", "source",
}  # fmt: skip
CALLS = [
    lambda: corpus.kwic("Кот спит.", "..."),
    lambda: corpus.kwic("Кот спит.", 5),
    lambda: corpus.kwic("Кот спит.", "кот", window=-1),
    lambda: corpus.format_kwic("кот"),
    lambda: corpus.format_kwic([], width=0),
    lambda: corpus.collocations([]),
    lambda: corpus.collocations(WORDS, measure="x"),
    lambda: corpus.collocations(WORDS, node="кот", side="up"),
    lambda: corpus.collocations(spacy.blank("ru")("Кот спит")),
    lambda: corpus.dispersion([], 10),
    lambda: corpus.dispersion(WORDS, 10),
    lambda: corpus.dispersion(WORDS, [1, 1]),
    lambda: corpus.keyness([], WORDS),
    lambda: corpus.keyness(WORDS, WORDS, "x"),
    lambda: corpus.keyness(WORDS, WORDS, top_n=0),
    lambda: corpus.keyness([["кот"]], [["кот", "пес"]], n=2),
    lambda: corpus.keyness(WORDS, FrequencyReference({"кот": 1.0}, -1.0)),
    lambda: corpus.check_keyness_params(positive="да"),
    lambda: corpus.frequency_table({}),
    lambda: corpus.frequency_table(UNITS, culling=1),
    lambda: corpus.delta(UNITS),
    lambda: corpus.delta(UNITS, variant="x"),
    lambda: corpus.delta_profiles(UNITS, UNITS),
    lambda: corpus.rolling_delta({"A": TEN}, TEN, 5, 1),
    lambda: corpus.rolling_delta({"A": TEN, "B": TEN}, TEN[:3], 5, 1),
    lambda: corpus.zeta([], WORDS),
    lambda: corpus.zeta(WORDS, WORDS, segment_size=0),
    lambda: corpus.zeta_segments({}, ["кот"], ["пес"]),
    lambda: corpus.zeta_segments({"c": WORDS}, [], ["пес"]),
    lambda: corpus.kilgarriff_chi2([], WORDS),
    lambda: corpus.mendenhall_curve([]),
    lambda: corpus.compare_features(pd.DataFrame({"a": [1.0]}), [1]),
    lambda: corpus.check_comparison_params(("A", "A")),
    lambda: corpus.bootstrap_median_diff([1.0], [1.0], rng=5),
    lambda: corpus.holm_correction([2.0]),
    lambda: corpus.calc_cohen_d("кот", [1.0]),
    lambda: corpus.corpus_features("Кот спит"),
    lambda: corpus.compare_corpora("Кот спит", ["Пес лает"]),
    lambda: corpus.function_words_profile([1]),
]


@pytest.mark.parametrize("call", CALLS)
def test_corpus_errors_in_russian(call):
    with pytest.raises(RutsError) as raised:
        call()
    message = str(raised.value).strip("'")
    assert re.search("[а-яё]", message, re.IGNORECASE), message
    assert set(re.findall(r"[A-Za-z_]+", message)) <= NAMES, message


@pytest.mark.parametrize("name", ["delta", "collocations", "format_kwic", "compare_features"])
def test_wrappers_pickle(name):
    """Обертка функции ядра - объект ruTS по своему пути: pickle (процессы) ее находит"""
    function = getattr(corpus, name)
    assert pickle.loads(pickle.dumps(function)) is function


def test_partial_messages():
    """Словарь части ключей дополняется русскими сообщениями: верный вызов работает,
    заданный ключ берется из словаря"""
    messages = {"association_measure": "Мера {measure} неизвестна"}
    assert corpus.collocations(WORDS * 3, messages=messages)
    assert corpus.holm_correction([0.1, 0.2], messages=messages).tolist() == [0.2, 0.2]
    with pytest.raises(RutsError, match=r"^Мера x неизвестна$"):
        corpus.collocations(WORDS, measure="x", messages=messages)
