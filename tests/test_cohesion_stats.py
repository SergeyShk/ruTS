import random
from math import isnan

import pytest
import spacy

from ruts import CohesionStats, WordsExtractor
from ruts.cohesion_stats import (
    Connector,
    Overlap,
    WordInfo,
    calc_overlap,
    calc_overlaps,
    calc_proportional_overlap,
    calc_repetition,
    count_given,
    dice,
    dominant,
    find_connectors,
    is_content_word,
    is_pronoun,
    load_connectors,
    token_info,
    word_info,
)
from ruts.constants import COHESION_STATS_DESC, CONNECTOR_CLASSES, CONNECTOR_TYPES
from ruts.utils import lemmatize

text = (
    "Кот сидел на окне. Он смотрел на птиц. Птицы улетели, и кот уснул. "
    "Завтра он снова будет сидеть на этом окне."
)


@pytest.fixture(scope="module")
def cs():
    return CohesionStats(text)


@pytest.fixture(scope="module")
def nlp():
    pytest.importorskip("ru_core_news_sm")
    return spacy.load("ru_core_news_sm")


def test_init_value_error():
    with pytest.raises(ValueError):
        CohesionStats("... !!! ...")


@pytest.mark.parametrize("source", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(source):
    with pytest.raises(TypeError):
        CohesionStats(source)


def test_init_doc(cs):
    nlp = spacy.blank("ru")
    nlp.add_pipe("sentencizer")
    doc_cs = CohesionStats(nlp(text))
    assert doc_cs.words == cs.words
    assert doc_cs.lemmas == cs.lemmas
    assert doc_cs.get_stats() == cs.get_stats()


def test_init_doc_model(nlp):
    doc = nlp("Мы стали ждать поезда. Нож сделан из стали. Эта сталь очень прочна.")
    cs = CohesionStats(doc)
    assert cs.lemmas == (
        ("мы", "стать", "ждать", "поезд"),
        ("нож", "сделать", "из", "сталь"),
        ("этот", "сталь", "очень", "прочный"),
    )
    assert cs.n_nouns == 4
    assert cs.n_pronouns == 2
    assert cs.n_demonstratives == 1
    assert cs.n_content_words == 9
    assert cs.n_given == 1
    assert cs.noun_overlap_adjacent == pytest.approx(1 / 2)
    assert cs.argument_overlap_all == pytest.approx(1 / 3)
    assert cs.tense_repetition == 1
    assert cs.aspect_repetition == 1
    assert CohesionStats(doc.text).noun_overlap_adjacent == 0


def test_word_info():
    assert word_info("кота") == WordInfo("кот", True, False, False, True, True, None, None)
    assert word_info("он") == WordInfo("он", False, True, False, True, False, None, None)
    assert word_info("этот") == WordInfo("этот", False, True, True, False, False, None, None)
    assert word_info("это") == WordInfo("это", False, True, True, False, False, None, None)
    assert word_info("столько") == WordInfo("столько", False, True, True, False, False, None, None)
    assert word_info("читал") == WordInfo(
        "читать", False, False, False, False, True, "past", "impf"
    )
    assert word_info("на") == WordInfo("на", False, False, False, False, False, None, None)


def test_token_info(nlp):
    doc = nlp("Иван читает эту книгу.")
    assert token_info(doc[0]) == WordInfo("иван", True, False, False, True, True, None, None)
    assert token_info(doc[1]) == WordInfo(
        "читать", False, False, False, False, True, "Pres", "Imp"
    )
    assert token_info(doc[2]) == WordInfo("этот", False, True, True, False, False, None, None)
    assert token_info(doc[4]) == WordInfo(".", False, False, False, False, False, None, None)


def test_init_doc_without_lemmatizer(nlp):
    tagger_nlp = spacy.load("ru_core_news_sm", exclude=["lemmatizer", "ner"])
    text = "Мы стали ждать поезда. Нож сделан из стали. Эта сталь очень прочна."
    doc = tagger_nlp(text)
    assert not doc.has_annotation("LEMMA")
    cs = CohesionStats(doc)
    assert cs.lemmas[1] == ("нож", "сделать", "из", "сталь")
    assert cs.noun_overlap_adjacent == pytest.approx(1 / 2)
    assert cs.get_stats() == pytest.approx(CohesionStats(nlp(text)).get_stats(), nan_ok=True)


def test_lemmatize():
    assert lemmatize("стали", "NOUN") == "сталь"
    assert lemmatize("стали", "VERB") == "стать"
    assert lemmatize("стали") == "стать"
    assert lemmatize("стали", "ADP") == "стать"
    assert lemmatize("Москву", "PROPN") == "москва"
    assert lemmatize("лучше", "ADV") == "хороший"


def test_demonstratives():
    cs = CohesionStats("Это кот. Столько котов!")
    assert cs.n_pronouns == 2
    assert cs.n_demonstratives == 2
    assert cs.p_demonstratives <= cs.p_pronouns


def test_init_extractors():
    cs = CohesionStats(text, words_extractor=WordsExtractor(stopwords=["на", "и"]))
    assert cs.n_words == 17
    assert cs.words[0] == ("Кот", "сидел", "окне")
    assert cs.noun_overlap_adjacent == pytest.approx(1 / 3)


def test_words_and_lemmas(cs):
    assert cs.n_sents == 4
    assert cs.n_words == 21
    assert cs.words[2] == ("Птицы", "улетели", "и", "кот", "уснул")
    assert cs.lemmas[2] == ("птица", "улететь", "и", "кот", "уснуть")


def test_counts(cs):
    assert cs.n_nouns == 6
    assert cs.n_pronouns == 3
    assert cs.n_demonstratives == 1
    assert cs.n_content_words == 14
    assert cs.n_given == 4


def test_overlap(cs):
    assert cs.noun_overlap_adjacent == pytest.approx(1 / 3)
    assert cs.noun_overlap_all == pytest.approx(3 / 6)
    assert cs.argument_overlap_adjacent == pytest.approx(1 / 3)
    assert cs.argument_overlap_all == pytest.approx(4 / 6)
    assert cs.content_overlap_adjacent == pytest.approx(1 / 3)
    assert cs.content_overlap_all == pytest.approx(3 / 6)
    assert cs.content_overlap_prop_adjacent == pytest.approx((0 + 1 / 3 + 0) / 3)
    assert cs.content_overlap_prop_all == pytest.approx((2 / 7 + 1 / 2 + 1 / 3) / 6)


def test_givenness(cs):
    assert cs.p_pronouns == pytest.approx(3 / 21)
    assert cs.pronoun_noun_ratio == pytest.approx(3 / 6)
    assert cs.p_demonstratives == pytest.approx(1 / 21)
    assert cs.p_given == pytest.approx(4 / 14)


def test_temporal(cs):
    assert cs.tense_repetition == pytest.approx(2 / 3)
    assert cs.aspect_repetition == pytest.approx(1 / 3)
    assert cs.temporal_cohesion == pytest.approx(1 / 2)


def test_single_sentence():
    cs = CohesionStats("Кот сидел на окне и смотрел на кота.")
    assert cs.n_sents == 1
    for stat in (
        "noun_overlap_adjacent",
        "noun_overlap_all",
        "argument_overlap_all",
        "content_overlap_prop_adjacent",
        "tense_repetition",
        "aspect_repetition",
        "temporal_cohesion",
    ):
        assert isnan(getattr(cs, stat))
    assert cs.p_pronouns == 0
    assert cs.pronoun_noun_ratio == 0
    assert cs.p_given == pytest.approx(1 / 5)


def test_no_nouns_no_verbs():
    cs = CohesionStats("Я не ты. Ты не я.")
    assert cs.n_nouns == 0
    assert cs.n_content_words == 0
    assert isnan(cs.pronoun_noun_ratio)
    assert isnan(cs.p_given)
    assert cs.noun_overlap_adjacent == 0
    assert cs.argument_overlap_adjacent == 1
    assert cs.content_overlap_adjacent == 0
    assert isnan(cs.tense_repetition)
    assert isnan(cs.temporal_cohesion)


def test_temporal_skips_sentences_without_verbs():
    cs = CohesionStats("Кот сидел. Кот лежал. Тишина. Кот проснётся. Кот уснул.")
    assert cs.tense_repetition == pytest.approx(1 / 2)
    assert cs.aspect_repetition == pytest.approx(1)
    assert cs.temporal_cohesion == pytest.approx(3 / 4)


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("он", True),
        ("его", True),
        ("себя", True),
        ("кто", True),
        ("этот", True),
        ("который", True),
        ("мой", True),
        ("весь", True),
        ("кот", False),
        ("там", False),
        ("и", False),
    ],
)
def test_is_pronoun(word, expected):
    assert is_pronoun(word) is expected


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("кот", True),
        ("сидел", True),
        ("сидеть", True),
        ("сидящий", True),
        ("сидя", True),
        ("красивый", True),
        ("красив", True),
        ("быстрее", True),
        ("быстро", True),
        ("на", False),
        ("и", False),
        ("он", False),
        ("этот", False),
        ("там", False),
        ("конечно", False),
        ("почему", False),
        ("три", False),
        ("2020", False),
    ],
)
def test_is_content_word(word, expected):
    assert is_content_word(word) is expected


def test_calc_overlap():
    sets = [{"a", "b"}, {"b", "c"}, {"d"}, {"a"}]
    assert calc_overlap(sets) == pytest.approx(1 / 3)
    assert calc_overlap(sets, adjacent=False) == pytest.approx(2 / 6)
    assert calc_overlap([{"a"}, set()]) == 0
    assert calc_overlap([["a", "a"], ["a"]]) == 1
    assert isnan(calc_overlap([{"a"}]))
    assert isnan(calc_overlap([]))


def test_calc_proportional_overlap():
    sets = [{"a", "b"}, {"b", "c"}, {"b"}, set()]
    assert calc_proportional_overlap(sets) == pytest.approx((1 / 2 + 2 / 3 + 0) / 3)
    assert calc_proportional_overlap(sets, adjacent=False) == pytest.approx(
        (1 / 2 + 2 / 3 + 0 + 2 / 3 + 0 + 0) / 6
    )
    assert calc_proportional_overlap([["a", "a"], ["a"]]) == 1
    assert isnan(calc_proportional_overlap([{"a"}]))


def test_dice():
    assert dice(frozenset("ab"), frozenset("bc")) == pytest.approx(1 / 2)
    assert dice(frozenset("ab"), frozenset()) == 0
    assert dice(frozenset(), frozenset()) == 0


@pytest.mark.parametrize(
    "sets",
    [
        [{"a", "b"}, {"b", "c"}, {"d"}, {"a"}],
        [{"a", "b"}, {"b", "c"}, {"b"}, set()],
        [set(), {"a"}, set(), {"a", "b"}, {"b"}],
        [{"a"}, {"a"}],
    ],
)
def test_calc_overlaps(sets):
    overlap = calc_overlaps(sets)
    assert isinstance(overlap, Overlap)
    assert overlap == pytest.approx(
        (
            calc_overlap(sets),
            calc_overlap(sets, adjacent=False),
            calc_proportional_overlap(sets),
            calc_proportional_overlap(sets, adjacent=False),
        )
    )


def test_calc_overlaps_random():
    rng = random.Random(7)
    sets = [
        {rng.randrange(40) for _ in range(rng.randrange(6))} for _ in range(rng.randrange(2, 300))
    ]
    sets = [{str(element) for element in elements} for elements in sets]
    assert calc_overlaps(sets) == pytest.approx(
        (
            calc_overlap(sets),
            calc_overlap(sets, adjacent=False),
            calc_proportional_overlap(sets),
            calc_proportional_overlap(sets, adjacent=False),
        )
    )
    long_sets = [{"a"} if i % 2 else {"b"} for i in range(5000)]
    assert calc_overlaps(long_sets).all == pytest.approx(2 * (2500 * 2499 / 2) / (5000 * 4999 / 2))


def test_calc_overlaps_short():
    assert all(isnan(value) for value in calc_overlaps([{"a"}]))
    assert all(isnan(value) for value in calc_overlaps([]))


def test_count_given():
    assert count_given([["a", "b"], ["b", "c", "a"], ["c"]]) == 3
    assert count_given([["a", "a"]]) == 1
    assert count_given([]) == 0


def test_dominant():
    assert dominant(["past", "pres", "past"]) == "past"
    assert dominant(["pres", "past"]) == "pres"
    assert dominant([]) is None


def test_calc_repetition():
    assert calc_repetition([["past"], ["past", "pres"], ["pres"]]) == pytest.approx(1 / 2)
    assert calc_repetition([["past"], [], ["past"]]) is not None
    assert isnan(calc_repetition([["past"], [], ["past"]]))
    assert isnan(calc_repetition([["past"]]))


def test_get_stats(cs):
    stats = cs.get_stats()
    assert list(stats) == list(COHESION_STATS_DESC)
    for key in COHESION_STATS_DESC:
        assert stats[key] == getattr(cs, key)


def test_print_stats(cs, capsys):
    cs.print_stats()
    captured = capsys.readouterr().out
    for value in COHESION_STATS_DESC.values():
        assert value in captured


connectors_text = (
    "Кот сидел на окне, потому что ждал птиц. Однако птицы улетели, и всё же кот не ушёл. "
    "Затем, иными словами, он уснул. Если бы птицы вернулись, кот проснулся бы."
)
# 29 слов: потому что (причинный, первичный), однако (противительный, первичный),
# и всё же (уступительный, первичный), затем (временной, первичный),
# иными словами (переформулирующий, вторичный), если бы (условный, первичный)


def test_connectors_dictionary():
    connectors = load_connectors()
    assert len(connectors) == 318
    assert all(
        cls in CONNECTOR_CLASSES and kind in CONNECTOR_TYPES for cls, kind in connectors.values()
    )
    assert connectors["потому что"] == ("causal", "primary")
    assert connectors["иными словами"] == ("reformulative", "secondary")
    assert all(connector == connector.strip().lower() for connector in connectors)


def test_connectors():
    cs = CohesionStats(connectors_text)
    assert cs.n_words == 29
    assert [connector.text for connector in cs.connector_spans] == [
        "потому что",
        "однако",
        "и всё же",
        "затем",
        "иными словами",
        "если бы",
    ]
    assert cs.connector_spans[0] == Connector(0, 4, 6, "потому что", "causal", "primary")
    assert cs.connector_spans[2] == Connector(1, 3, 6, "и всё же", "concessive", "primary")
    assert cs.n_connectors == 6
    assert cs.c_connectors["и всё же"] == 1
    assert cs.connectors == pytest.approx(6 / 29 * 1000)
    for cls in ("causal", "adversative", "concessive", "temporal", "reformulative", "conditional"):
        assert getattr(cs, f"connectors_{cls}") == pytest.approx(1 / 29 * 1000)
    assert cs.connectors_additive == 0
    assert cs.connectors_primary == pytest.approx(5 / 29 * 1000)
    assert cs.connectors_secondary == pytest.approx(1 / 29 * 1000)


def test_connectors_doc(nlp):
    doc = nlp(connectors_text)
    assert CohesionStats(doc).connector_spans == CohesionStats(connectors_text).connector_spans


def test_find_connectors():
    assert find_connectors(["Иными", "словами", "и", "всё", "же", "кот"], sent_index=3) == [
        Connector(3, 0, 2, "иными словами", "reformulative", "secondary"),
        Connector(3, 2, 5, "и всё же", "concessive", "primary"),
    ]
    assert find_connectors(["И", "все", "же"]) == [
        Connector(0, 0, 3, "и всё же", "concessive", "primary")
    ]
    assert find_connectors(["кот", "спит"]) == []
    assert find_connectors([]) == []


def test_find_connectors_custom():
    custom = {"кот": ("additive", "secondary"), "и всё же": ("adversative", "primary")}
    assert find_connectors(["кот", "и", "всё", "же"], custom) == [
        Connector(0, 0, 1, "кот", "additive", "secondary"),
        Connector(0, 1, 4, "и всё же", "adversative", "primary"),
    ]
    cs = CohesionStats(connectors_text, connectors=custom)
    assert cs.n_connectors == 4
    assert cs.connectors_additive == pytest.approx(3 / 29 * 1000)
    assert CohesionStats(connectors_text, connectors={}).n_connectors == 0
    with pytest.raises(ValueError):
        find_connectors(["кот"], {"кот": ("noun", "primary")})
    with pytest.raises(ValueError):
        find_connectors(["кот"], {"кот": ("causal", "tertiary")})


def test_connectors_single_sentence_words(cs):
    assert cs.connector_spans == (Connector(2, 2, 3, "и", "additive", "primary"),)
    assert cs.connectors_additive == pytest.approx(1 / 21 * 1000)
