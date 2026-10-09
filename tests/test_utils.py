import unicodedata

import pytest

from ruts.utils import (
    add_dash_rules,
    find_phrases,
    is_verbal_noun,
    iter_text_words,
    iter_tokens,
    lemmatize,
    normalize_yo,
    parse_all,
    parse_word,
)


def test_parse_yo_pronoun():
    """pymorphy3 не дает у «её» личного местоимения, и оно разбирается как «ее»"""
    assert [parse.normal_form for parse in parse_all("Её")][:2] == ["она", "её"]
    assert parse_word("её").tag.POS == "NPRO"
    assert lemmatize("её", "PRON") == lemmatize("ее", "PRON") == "она"
    assert lemmatize("её", "DET") == "её"


def test_parse_word_cached():
    parse_word.cache_clear()
    assert parse_word("рублей").normal_form == "рубль"
    assert parse_word("рублей").tag.POS == "NOUN"
    assert parse_word.cache_info().hits == 1
    assert parse_word.cache_info().misses == 1


@pytest.mark.parametrize(
    ("lemma", "expected"),
    [
        ("повышение", True),
        ("Участие", True),
        ("реализация", True),
        ("производство", True),
        ("руководство", True),
        ("содействие", True),
        ("житьё", True),
        ("здание", True),
        ("качество", False),
        ("правительство", False),
        ("кот", False),
        ("проверка", False),
        ("ние", True),
        ("", False),
    ],
)
def test_is_verbal_noun(lemma, expected):
    assert is_verbal_noun(lemma) is expected


def test_normalize_yo():
    assert normalize_yo("Учёт") == "учет"
    assert normalize_yo("путем") == "путем"


def test_find_phrases():
    words = ["В", "целях", "повышения", "в", "связи", "с", "этим", "путём", "проверки", "в"]
    phrases = ["в целях", "в связи с", "путем", "в связи", "в"]
    assert find_phrases(words, phrases) == [(0, 2), (3, 6), (7, 8), (9, 10)]
    assert find_phrases(words, []) == []
    assert find_phrases(words, ["", "  "]) == []
    assert find_phrases(["кот", "дом"], ["дом", ""]) == [(1, 2)]
    assert find_phrases([], phrases) == []
    assert find_phrases(["связи", "с"], ["в связи с"]) == []
    assert find_phrases(["в", "связи"], ["в связи с", "в"]) == [(0, 1)]


def test_iter_text_words():
    assert list(iter_text_words("Во-первых, кот - т.е. «зверь»!")) == [
        (0, 9, "Во-первых"),
        (11, 14, "кот"),
        (17, 18, "т"),
        (19, 20, "е"),
        (23, 28, "зверь"),
    ]
    assert list(iter_text_words("")) == []


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("-Нет -сказал он.", ["-", "Нет", "-", "сказал", "он", "."]),
        ("он —сказал", ["он", "—", "сказал"]),
        ("смеяться—говорил он—над", ["смеяться", "—", "говорил", "он", "—", "над"]),
        ("Нет- сказал", ["Нет", "-", "сказал"]),
        ("--Нет --сказал", ["--", "Нет", "--", "сказал"]),
        ("во-первых кто-то рок-н-ролл", ["во-первых", "кто-то", "рок-н-ролл"]),
        ("-5 1990—1995", ["-", "5", "1990—1995"]),
        ("Г—в и N—ский", ["Г—в", "и", "N—ский"]),
        ("Нет-сказал", ["Нет-сказал"]),
        ("Он сказа́л—и ушёл", ["Он", "сказа́л", "—", "и", "ушёл"]),
        ("Да́- сказал", ["Да́", "-", "сказал"]),
        (
            unicodedata.normalize("NFD", "мой—её"),
            [unicodedata.normalize("NFD", "мой"), "—", unicodedata.normalize("NFD", "её")],
        ),
    ],
)
def test_iter_tokens(text, expected):
    tokens = list(iter_tokens(text))
    assert [token for _, _, token in tokens] == expected
    assert all(text[start:stop] == token for start, stop, token in tokens)


def test_add_dash_rules():
    import spacy

    nlp = spacy.blank("ru")
    add_dash_rules(nlp)
    add_dash_rules(nlp)
    for text in (
        "-Нет -сказал он.",
        "Нет- сказал",
        "Нет,-сказал",
        "сказал:—Нет",
        "«-Нет»",
        "да--сказал",
        "Да́- нет",
        "Да́,-нет",
        "Он—«Нет»",
        "он—(тихо)—сказал",
    ):
        assert [token.text for token in nlp(text)] == [token for _, _, token in iter_tokens(text)]
    assert [token.text for token in nlp("во-первых")] == ["во", "-", "первых"]


def test_add_dash_rules_other_tokenizer():
    import spacy

    nlp = spacy.blank("ru")
    tokenizer = nlp.tokenizer = lambda text: spacy.tokens.Doc(nlp.vocab, words=text.split())
    add_dash_rules(nlp)
    assert nlp.tokenizer is tokenizer


def test_iter_text_words_dialogue():
    assert list(iter_text_words("он —сказал")) == [(0, 2, "он"), (4, 10, "сказал")]
