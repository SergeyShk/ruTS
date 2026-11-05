import unicodedata

import pytest
import spacy

import ruts.utils
import ruts.verse_stats
from ruts import CohesionStats, MorphStats, StyleStats, WordsExtractor
from ruts.exceptions import SourceTypeError
from ruts.morph_stats import word_to_ud
from ruts.style_stats import is_water_word
from ruts.utils import (
    add_dash_rules,
    analyze_sentence,
    analyze_sents,
    analyze_text,
    analyze_words,
    find_phrases,
    is_verbal_noun,
    iter_text_sents,
    iter_text_words,
    iter_tokens,
    lemmatize,
    normalize_yo,
    parse_all,
    parse_word,
    strip_marks,
    word_form,
)


def test_parse_yo_pronoun():
    """У «её» без контекста - разборы притяжательного и личного местоимения"""
    assert [(a.lemma, a.pos) for a in parse_all("Её")][:2] == [("её", "DET"), ("она", "PRON")]
    assert lemmatize("её", "PRON") == lemmatize("ее", "PRON") == "она"
    assert lemmatize("её", "DET") == "её"


@pytest.mark.parametrize(
    ("word", "lemma", "pos"),
    [
        ("нем", "он", "PRON"),
        ("Нем", "он", "PRON"),
        ("есть", "быть", "VERB"),
        ("ниже", "низкий", "ADJ"),
        ("Мартова", "мартов", "PROPN"),
        ("мартова", "мартовый", "ADJ"),
        ("Кринжово", "кринжовый", "ADJ"),
    ],
)
def test_parse_word(word, lemma, pos):
    """Первый разбор ruMorph: часть речи UD, регистр слова учитывается"""
    analysis = parse_word(word)
    assert (analysis.lemma, analysis.pos) == (lemma, pos)


def test_parse_without_invisible_characters():
    """Слово с управляющим или служебным символом разбирается без него, пустая строка - как знак"""
    assert parse_word("это\x7f").lemma == parse_word("это\u200b").lemma == "это"
    assert parse_word("").pos == parse_word(" ").pos == "PUNCT"
    assert lemmatize("знаю\x7f", "VERB") == "знать"


def test_parse_word_cached():
    parse_all.cache_clear()
    assert parse_word("рублей").lemma == "рубль"
    assert parse_word("рублей").pos == "NOUN"
    assert parse_all.cache_info().hits == 1
    assert parse_all.cache_info().misses == 1


def test_analyze_sentence():
    """Омоним разбирается по соседним словам, знаки препинания в вывод не входят"""
    pairs = analyze_sentence("Мы стали ждать, а нож сделан из стали.")
    assert [word for word, _ in pairs] == [
        "Мы",
        "стали",
        "ждать",
        "а",
        "нож",
        "сделан",
        "из",
        "стали",
    ]
    assert [(pairs[1][1].lemma, pairs[1][1].pos), (pairs[-1][1].lemma, pairs[-1][1].pos)] == [
        ("стать", "VERB"),
        ("сталь", "NOUN"),
    ]
    # Токен без разборов модели (с ZWNJ внутри) разбирается, как в parse_all
    word, analysis = analyze_sentence("Большой до\u200cм.")[1]
    assert (word, analysis.lemma) == ("до\u200cм", "дом")


def test_analyze_text():
    text = "Мост сделан из стали.\n\nМы стали ждать, т.е. сидеть."
    pairs = analyze_text(text)
    assert [word for word, _ in pairs] == list(WordsExtractor().extract(text))
    # Слова spaCy получают разборы в контексте в предложениях, где совпали со словами строки
    doc = spacy.blank("ru")(text)
    words = [(token.idx, token.text) for token in doc if not (token.is_punct or token.is_space)]
    found = analyze_words(words, text)
    assert found[:4] == [analysis for _, analysis in pairs[:4]]
    assert found[4:] == [None] * 5


def test_analyze_sents_shared():
    """Классы статистик одного текста разбирают его один раз"""
    text = "Мост сделан из стали. Мы стали ждать."
    ruts.utils._analyze_sents.cache_clear()
    MorphStats(text).get_stats()
    CohesionStats(text).get_stats()
    assert ruts.utils._analyze_sents.cache_info().misses == 1
    assert ruts.utils._analyze_sents.cache_info().hits == 1


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
        (17, 19, "т"),
        (19, 21, "е"),
        (23, 28, "зверь"),
    ]
    assert list(iter_text_words("")) == []


def test_iter_text_sents_blank_lines():
    """Пустая строка завершает предложение, позиции - по исходной строке со знаками"""
    text = "Итоги без точки\n \n\nВсё на ме\u0301сте. Идём дальше\n\n***\n\n"
    sents = list(iter_text_sents(text))
    assert [sent for _, _, sent in sents] == [
        "Итоги без точки",
        "Всё на ме\u0301сте.",
        "Идём дальше",
        "***",
    ]
    assert all(text[start:stop] == sent for start, stop, sent in sents)
    assert list(iter_text_sents(" \n\n ")) == []


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("-Нет -сказал он.", ["-", "Нет", "-", "сказал", "он", "."]),
        ("он —сказал", ["он", "—", "сказал"]),
        ("смеяться—говорил он—над", ["смеяться", "—", "говорил", "он", "—", "над"]),
        ("Нет- сказал", ["Нет", "-", "сказал"]),
        ("--Нет --сказал", ["--", "Нет", "--", "сказал"]),
        ("во-первых кто-то рок-н-ролл", ["во-первых", "кто-то", "рок-н-ролл"]),
        ("-5 1990—1995", ["-", "5", "1990", "—", "1995"]),
        ("Г—в и N—ский", ["Г", "—", "в", "и", "N", "—", "ский"]),
        ("Нет-сказал", ["Нет-сказал"]),
        ("Он сказа\u0301л—и ушёл", ["Он", "сказал", "—", "и", "ушёл"]),
        ("Да\u0301- сказал", ["Да", "-", "сказал"]),
        (
            unicodedata.normalize("NFD", "мой—её"),
            ["мой", "—", "её"],
        ),
    ],
)
def test_iter_tokens(text, expected):
    tokens = list(iter_tokens(text))
    assert [token for _, _, token in tokens] == expected
    assert all(strip_marks(text[start:stop]) == token for start, stop, token in tokens)


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
        "Да\u0301- нет",
        "Да\u0301,-нет",
        "Он—«Нет»",
        "он—(тихо)—сказал",
    ):
        tokens = [strip_marks(token.text) for token in nlp(text)]
        assert tokens == [token for _, _, token in iter_tokens(text)]
    assert [token.text for token in nlp("во-первых")] == ["во", "-", "первых"]


def test_add_dash_rules_other_tokenizer():
    import spacy

    nlp = spacy.blank("ru")
    tokenizer = nlp.tokenizer = lambda text: spacy.tokens.Doc(nlp.vocab, words=text.split())
    add_dash_rules(nlp)
    assert nlp.tokenizer is tokenizer


def test_iter_text_words_dialogue():
    assert list(iter_text_words("он —сказал")) == [(0, 2, "он"), (4, 10, "сказал")]


def test_abbreviation_with_period():
    """Сокращение с точкой (токен UD) - та же лемма, что без нее"""
    assert parse_word("т.").lemma == parse_word("т").lemma == "так"
    assert lemmatize("руб.", "NOUN") == lemmatize("руб", "NOUN") == "рубль"


def test_lone_surrogate():
    """Одиночный суррогат (из JSON) не мешает сегментации, позиции - по исходной строке"""
    text = "Привет \ud83d мир. Ещё."
    assert [word for *_, word in iter_tokens(text)] == ["Привет", "\ud83d", "мир", ".", "Ещё", "."]
    assert list(iter_text_sents(text)) == [(0, 13, "Привет \ud83d мир."), (14, 18, "Ещё.")]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Моро\u0301з и со\u00adлнце", "Мороз и солнце"),
        ("чуде\u0300сный, ѐлка, Ѝгорь", "чудесный, елка, Игорь"),
        ("ёлка и йод", "ёлка и йод"),
        ("Е\u0308\u0301лка и\u0306од", "Ёлка йод"),
        ("Ó\u00adблако, Ниже\u0301", "Облако, Ниже"),
        ("Он сказа\u0301л: où, Café", "Он сказал: où, Café"),
        ("чтó, Домá, бóльшую; ó!", "что, Дома, большую; ó!"),
        ("г\u0301ород", "город"),
    ],
)
def test_strip_marks(text, expected):
    assert strip_marks(text) == expected


def test_iter_tokens_soft_hyphen():
    """Токен из одного мягкого переноса - не токен"""
    assert [token for _, _, token in iter_tokens("кот \u00ad спит")] == ["кот", "спит"]


def test_marks_in_parse_and_folding():
    """Знаки ударения не мешают разбору и сравнению слов"""
    assert parse_word("Моро\u0301з").lemma == "мороз"
    assert lemmatize("сказа\u0301л", "VERB") == "сказать"
    assert normalize_yo("Ёлка\u0301") == "елка"
    assert find_phrases(["в", "свя\u0301зи", "с"], ["в связи с"]) == [(0, 3)]


@pytest.mark.parametrize(
    "func",
    [
        strip_marks,
        iter_text_words,
        iter_text_sents,
        ruts.verse_stats.split_stanzas,
        ruts.verse_stats.accentuate,
    ],
)
@pytest.mark.parametrize("value", [None, 5, ["текст"]])
def test_text_must_be_a_string(func, value):
    with pytest.raises(SourceTypeError, match=r"^Ожидается строка текста, а не "):
        func(value)


def test_set_sent_starts_reexport():
    """Предложения Doc по началам сегментатора - функция ядра из ruts.utils"""
    import anyts.utils

    from ruts.utils import set_sent_starts

    assert set_sent_starts is anyts.utils.set_sent_starts


def test_abbreviation_dot():
    """Сокращение с точкой внутри предложения и без нее в конце - одно слово, разбор по токену с точкой"""
    text = "Цена 5 руб. за кг, итого 10 руб."
    assert WordsExtractor().extract(text) == ("Цена", "5", "руб", "за", "кг", "итого", "10", "руб")
    assert [analysis.lemma for word, analysis in analyze_text(text) if word == "руб"] == [
        "рубль"
    ] * 2
    assert [word for _, _, word in iter_tokens(text)][2] == "руб."
    assert (word_form("руб."), word_form("т.е."), word_form("...")) == ("руб", "т.е.", "...")
    # Без точки - другое слово: точка остается, разбор по слову тот же, что по токену
    assert [word_form(token) for token in ("им.", "в.", "с.", "А.")] == ["им.", "в.", "с.", "А."]
    text = "В XIX в. театр им. Пушкина стоял на берегу. Театр им. Горького построен в XX в."
    assert StyleStats(text).water == 0


def test_word_helpers_type_errors():
    """Не строка у помощников по слову и разбора в контексте - SourceTypeError ruTS"""
    for func, value in (
        (parse_word, 1),
        (lemmatize, None),
        (analyze_sentence, 1),
        (analyze_sents, "Кот."),
        (parse_all, ["кот"]),
        (lemmatize, ["кот"]),
        (normalize_yo, ["кот"]),
        (is_water_word, ["кот"]),
        (word_to_ud, ["кот"]),
        (analyze_sents, [["Кот спит."]]),
    ):
        with pytest.raises(SourceTypeError):
            func(value)
    assert analyze_sents(["Кот спит."]) == analyze_sents(("Кот спит.",))
