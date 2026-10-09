from collections import Counter

import pytest

from ruts.corpus import Keyword, keyness
from ruts.corpus.keyness import (
    calc_log_likelihood,
    calc_log_ratio,
    calc_p_value,
)
from ruts.datasets import FreqDict
from ruts.datasets.freq2011 import CORPUS_SIZE, FILENAME
from tests.datasets.test_freq2011 import write_dict

target = ["кот", "сидел", "на", "окне", "и", "смотрел", "на", "птиц", "кот", "уснул"]
reference = ["собака", "лежала", "на", "полу", "и", "спала", "собака", "ела"]


@pytest.fixture(scope="module")
def freq_dict(tmp_path_factory):
    path = tmp_path_factory.mktemp("dicts")
    write_dict(path)
    return FreqDict(data_dir=path)


def test_keyness():
    keywords = keyness(target, reference)
    assert [keyword.word for keyword in keywords] == [
        "кот",
        "окне",
        "птиц",
        "сидел",
        "смотрел",
        "уснул",
        "на",
    ]
    assert keywords[0] == Keyword(
        "кот",
        2,
        0,
        200000.0,
        0.0,
        calc_log_likelihood(2, 0, 10, 8),
        calc_p_value(calc_log_likelihood(2, 0, 10, 8)),
        calc_log_ratio(2, 0, 10, 8),
        calc_log_likelihood(2, 0, 10, 8),
    )
    assert keywords[-1].freq_reference == 1
    assert keywords[-1].ipm_reference == 125000.0
    assert keyness(Counter(target), Counter(reference)) == keywords
    assert keyness(target, reference, top_n=2) == keywords[:2]
    assert [keyword.word for keyword in keyness(target, reference, min_freq=2)] == ["кот", "на"]
    assert all(keyword.g2 > 0 for keyword in keywords)


def test_keyness_negative():
    keywords = keyness(target, reference, positive=False)
    assert [keyword.word for keyword in keywords] == [
        "собака",
        "ела",
        "лежала",
        "полу",
        "спала",
        "и",
    ]
    assert all(keyword.g2 < 0 and keyword.score < 0 for keyword in keywords)
    assert keywords[-1].freq_target == 1
    assert keywords[-1].log_ratio == pytest.approx(-0.32192809488736235)


def test_keyness_freq_dict(freq_dict):
    keywords = keyness(["Кот", "кот", "птица", "фелинолог"], freq_dict)
    assert [keyword.word for keyword in keywords] == ["кот", "фелинолог", "птица"]
    cat = keywords[0]
    assert cat.freq_reference == pytest.approx(40.3 * CORPUS_SIZE / 1e6)
    assert cat.ipm_reference == pytest.approx(40.3)
    assert cat.ipm_target == 500000.0
    assert cat.g2 == pytest.approx(calc_log_likelihood(2, 40.3 * 92, 4, CORPUS_SIZE))
    missing = freq_dict.min_ipm * CORPUS_SIZE / 1e6
    assert keywords[1].freq_reference == pytest.approx(missing)
    assert keywords[1].log_ratio == pytest.approx(calc_log_ratio(1, missing, 4, CORPUS_SIZE))
    negative = keyness(["кот"], freq_dict, positive=False, min_freq=1000)
    assert [keyword.word for keyword in negative][:2] == ["и", "на"]
    assert keyness({"ещё": 2, "Ещё": 1}, freq_dict)[0].freq_target == 3
    assert keyness(["ещё"], freq_dict)[0].ipm_reference == pytest.approx(2409.4)


@pytest.fixture(scope="module")
def homonym_dict(tmp_path_factory):
    path = tmp_path_factory.mktemp("dicts")
    rows = ["Lemma\tPoS\tFreq(ipm)\tR\tD\tDoc", "гора\ts\t115.5\t100\t97\t9000"]
    rows += ["горе\ts\t48.3\t100\t95\t5000", "кошка\ts\t30.0\t95\t90\t800"]
    path.joinpath(FILENAME).write_text("\n".join(rows) + "\n", encoding="utf-8")
    return FreqDict(data_dir=path)


def test_keyness_freq_dict_forms(freq_dict):
    keywords = keyness(["коты", "кота", "кошек", "2020", "cat"], freq_dict)
    assert {keyword.word: keyword.freq_target for keyword in keywords} == {"кот": 2, "кошка": 1}
    assert {keyword.word: keyword.ipm_target for keyword in keywords}["кот"] == pytest.approx(
        2 / 3 * 1e6
    )


def test_keyness_freq_dict_lemmatize(homonym_dict):
    assert [keyword.word for keyword in keyness(["горе"], homonym_dict)] == ["гора"]
    lemmas = keyness(["горе"], homonym_dict, lemmatize=False)
    assert [keyword.word for keyword in lemmas] == ["горе"]
    assert keyness(target, reference, lemmatize=False) == keyness(target, reference)


def test_keyness_freq_dict_negative(homonym_dict):
    negative = keyness({"гора": 10**7, "фелинолог": 1}, homonym_dict, positive=False)
    assert [keyword.word for keyword in negative] == ["горе", "кошка"]


def test_keyness_errors():
    with pytest.raises(ValueError):
        keyness(target, reference, measure="mi")
    with pytest.raises(ValueError):
        keyness([], reference)
    with pytest.raises(ValueError):
        keyness(target, {})
    with pytest.raises(ValueError):
        keyness(target, reference, top_n=0)
    with pytest.raises(ValueError):
        keyness(target, reference, top_n=-1)


@pytest.fixture(scope="module")
def pronoun_dict(tmp_path_factory):
    """Статьи, к которым лемматизатор слова не приводит: «его», «ее», «во»"""
    path = tmp_path_factory.mktemp("dicts")
    rows = [
        ("в", "pr", 30000.0),
        ("во", "pr", 600.0),
        ("его", "apro", 2000.0),
        ("ее", "apro", 1500.0),
        ("кот", "s", 40.3),
        ("он", "spro", 15000.0),
        ("она", "spro", 9000.0),
        ("род", "s", 300.0),
        ("родиться", "v", 200.0),
    ]
    lines = ["Lemma\tPoS\tFreq(ipm)\tR\tD\tDoc"]
    lines += [f"{lemma}\t{pos}\t{ipm}\t90\t90\t1000" for lemma, pos, ipm in rows]
    path.joinpath(FILENAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return FreqDict(data_dir=path)


@pytest.mark.parametrize("lemmatize", [True, False])
def test_keyness_freq_dict_unreachable(pronoun_dict, lemmatize):
    """Статья остается, если к ней приводится другая форма: «род» - «родиться», но «рода» - «род»"""
    negative = keyness(["кот"] * 50, pronoun_dict, positive=False, lemmatize=lemmatize)
    assert {keyword.word for keyword in negative} == {"в", "он", "она", "род", "родиться"}


def test_keyness_freq_dict_top_n(pronoun_dict):
    """top_n берется после того, как недостижимые статьи отброшены"""
    negative = keyness(["кот"] * 50, pronoun_dict, positive=False, top_n=2)
    assert [keyword.word for keyword in negative] == ["в", "он"]


def test_keyness_freq_dict_yo(pronoun_dict):
    """«Её» и «ее» - одна статья «она», как в тексте без ё"""
    assert keyness(["Её", "кот"], pronoun_dict) == keyness(["ее", "кот"], pronoun_dict)
    assert {keyword.word for keyword in keyness(["её"], pronoun_dict)} == {"она"}
