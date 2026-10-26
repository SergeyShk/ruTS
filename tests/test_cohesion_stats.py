import unicodedata
from math import isnan

import pytest
import spacy
from anyts.utils import iter_doc_units
from spacy.tokens import Doc

from ruts import BasicStats, CohesionStats, SentsExtractor, WordsExtractor
from ruts.cohesion_stats import (
    Connector,
    WordInfo,
    connector_pos,
    find_connectors,
    is_content_word,
    is_pronoun,
    load_connectors,
    split_doc_units,
    token_info,
    unit_info,
    unit_text,
    word_info,
)
from ruts.constants import (
    COHESION_STATS_DESC,
    CONNECTOR_BLOCKED_AFTER,
    CONNECTOR_BLOCKED_AFTER_POS,
    CONNECTOR_BLOCKED_BEFORE,
    CONNECTOR_CLASSES,
    CONNECTOR_NOT_AT_START,
    CONNECTOR_ONLY_AFTER,
    CONNECTOR_SUBORDINATORS,
    CONNECTOR_TYPES,
)
from ruts.exceptions import ParameterError, SourceError
from ruts.utils import lemmatize, normalize_yo

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


def test_answer_particle_tense(nlp):
    """Ответное «нет» - частица без времени, бытийное - в настоящем, как у Doc"""
    answers = "Нет, я его видел. Нет, она придёт завтра."
    assert CohesionStats(answers).tense_repetition == 0.0
    assert CohesionStats(nlp(answers)).tense_repetition == 0.0
    assert CohesionStats("Денег нет. Хлеба нет.").tense_repetition == 1.0


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
    assert word_info("надо") == WordInfo("надо", False, False, False, False, False, None, None)
    assert word_info("прочитав").tense == "past"
    assert word_info("нет").tense == "pres"


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


def test_temporal_ignores_predicatives():
    """У «надо» нет времени, поэтому повтор времени не определен, как у Doc; у «нет» - есть"""
    cs = CohesionStats("Надо идти. Надо спать.")
    assert isnan(cs.tense_repetition)
    assert cs.aspect_repetition == 1.0
    assert CohesionStats("Тебя нет. Денег нет.").tense_repetition == 1.0


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


def test_get_stats(cs):
    stats = cs.get_stats()
    assert list(stats) == list(COHESION_STATS_DESC)
    for key in COHESION_STATS_DESC:
        assert stats[key] == pytest.approx(getattr(cs, key), nan_ok=True)


def test_print_stats(cs, capsys):
    cs.print_stats()
    captured = capsys.readouterr().out
    for value in COHESION_STATS_DESC.values():
        assert value in captured


connectors_text = (
    "Кот сидел на окне, потому что ждал птиц. Однако птицы улетели, и всё же кот не ушёл. "
    "Затем, иными словами, он уснул. Если бы птицы вернулись, кот проснулся бы. "
    "Во-первых, из-за этого он голоден."
)
# 34 слова: потому что (причинный, первичный), однако (противительный, первичный),
# и всё же (уступительный, первичный), затем (временной, первичный),
# иными словами (переформулирующий, вторичный), если бы (условный, первичный),
# во-первых (аддитивный, первичный), из-за этого (причинный, вторичный)


def test_connectors_dictionary():
    connectors = load_connectors()
    assert len(connectors) == 316
    assert all(
        cls in CONNECTOR_CLASSES and kind in CONNECTOR_TYPES for cls, kind in connectors.values()
    )
    assert connectors["потому что"] == ("causal", "primary")
    assert connectors["иными словами"] == ("reformulative", "secondary")
    assert all(connector == connector.strip().lower() for connector in connectors)


def test_connectors():
    cs = CohesionStats(connectors_text)
    assert cs.n_words == 34
    assert [connector.text for connector in cs.connector_spans] == [
        "потому что",
        "однако",
        "и всё же",
        "затем",
        "иными словами",
        "если бы",
        "во-первых",
        "из-за этого",
    ]
    assert cs.connector_spans[0] == Connector(0, 4, 6, "потому что", "causal", "primary")
    assert cs.connector_spans[2] == Connector(1, 3, 6, "и всё же", "concessive", "primary")
    assert cs.connector_spans[6] == Connector(4, 0, 1, "во-первых", "additive", "primary")
    assert cs.connector_spans[7] == Connector(4, 1, 3, "из-за этого", "causal", "secondary")
    assert cs.n_connectors == 8
    assert cs.c_connectors["и всё же"] == 1
    assert cs.connectors == pytest.approx(8 / 34 * 1000)
    assert cs.connectors_causal == pytest.approx(2 / 34 * 1000)
    assert cs.connectors_additive == pytest.approx(1 / 34 * 1000)
    for cls in ("adversative", "concessive", "temporal", "reformulative", "conditional"):
        assert getattr(cs, f"connectors_{cls}") == pytest.approx(1 / 34 * 1000)
    assert cs.connectors_primary == pytest.approx(6 / 34 * 1000)
    assert cs.connectors_secondary == pytest.approx(2 / 34 * 1000)
    # Однако, затем, во-первых открывают предложения; «если бы» начинает придаточное
    assert cs.n_inter_connectors == 3
    assert cs.connectors_inter == pytest.approx(3 / 34 * 1000)
    assert cs.connectors_intra == pytest.approx(5 / 34 * 1000)


def test_connectors_doc(nlp):
    doc = nlp(connectors_text)
    doc_cs = CohesionStats(doc)
    assert [connector.text for connector in doc_cs.connector_spans] == [
        connector.text for connector in CohesionStats(connectors_text).connector_spans
    ]
    assert doc_cs.words[4] == ("Во-первых", "из-за", "этого", "он", "голоден")
    assert doc_cs.connector_spans[6] == Connector(4, 0, 1, "во-первых", "additive", "primary")
    assert doc_cs.connector_spans[7] == Connector(4, 1, 3, "из-за этого", "causal", "secondary")
    assert doc_cs.n_words == CohesionStats(connectors_text).n_words
    assert doc_cs.n_inter_connectors == 3


def test_connectors_hyphens_and_dots(nlp):
    text = "Из-за этого мы опоздали, т.е. пришли позже. Всё-таки успели."
    expected = ["из-за этого", "т.е.", "позже", "всё-таки"]
    assert [connector.text for connector in CohesionStats(text).connector_spans] == expected
    assert [connector.text for connector in CohesionStats(nlp(text)).connector_spans] == expected
    assert find_connectors(["во", "первых"]) == [
        Connector(0, 0, 2, "во-первых", "additive", "primary")
    ]
    assert find_connectors(["т", "е"]) == [Connector(0, 0, 2, "т.е.", "reformulative", "primary")]


@pytest.mark.parametrize(
    ("text", "found", "inter"),
    [
        # Правила не читают слово через знак препинания
        ("Ну, значит, придётся подождать.", ["значит"], 0),
        ("Это, правда, было давно.", ["правда"], 0),
        ("А это, главное, не важно.", ["а", "главное"], 1),
        ("Значит бояться нечего.", [], 0),
        # «Отчего» после глагола знания - через запятую
        ("Он не знал, отчего так.", [], 0),
        ("Он устал, отчего и заснул.", ["отчего", "и"], 0),
        # Подчинительные союзы и предлоги в начале предложения, «ибо» - парцелляция
        ("Он устал. Раз ты здесь, помоги.", ["раз"], 0),
        ("Он устал. Хоть он и устал, он пошёл.", ["хоть", "и"], 0),
        ("Он устал. Едва он вошёл, все встали.", ["едва"], 0),
        ("Он устал. Несмотря на дождь, мы пошли.", ["несмотря на"], 0),
        ("Он устал. Несмотря на это, мы пошли.", ["несмотря на это"], 1),
        ("Он устал. Вопреки ожиданиям, он пришёл.", ["вопреки"], 0),
        ("Он не пришёл. Ибо болен был.", ["ибо"], 1),
        # «Раз» - не условный союз
        ("Раз вечером сказал им отец.", [], 0),
        ("Он садился отдыхать раз пять.", [], 0),
        ("Десятки раз хвалил.", [], 0),
        ("Выхожу раз другой поглядеть.", [], 0),
        # Частые ложные коннекторы
        ("Именно так он и сказал.", ["и"], 0),
        ("Пусть он придёт.", [], 0),
        ("Пускай и поздно, но пришёл.", ["пускай и", "но"], 0),
        ("Луна вышла из-за облаков.", [], 0),
        ("Он поступил иначе.", [], 0),
        ("Иди скорее домой.", [], 0),
        ("Моя правда.", [], 0),
        ("После него остался сын.", [], 0),
        ("После «Ревизора» он уехал.", [], 0),
        ("Он ушёл после.", ["после"], 0),
        # Правило части речи не читает через скобку и многоточие: в корпусах таких нет
        ("Он пришёл после (обеда) домой.", ["после"], 0),
        ("Ради бога, простите.", [], 0),
    ],
)
def test_connector_rules(nlp, text, found, inter):
    for source in (text, nlp(text)):
        cs = CohesionStats(source)
        assert [connector.text for connector in cs.connector_spans] == found
        assert cs.n_inter_connectors == inter


@pytest.mark.parametrize(
    "text", ["Это, правда, было давно.", "Что значит ещё раз?", "Он не знал, отчего так."]
)
def test_connector_rules_with_stress_marks(text):
    """Знаки ударения и буквы из двух символов (NFD) не меняют знаки препинания между словами"""
    plain = [connector.text for connector in CohesionStats(text).connector_spans]
    for marked in (text.replace("ра", "ра\u0301"), unicodedata.normalize("NFD", text)):
        assert [connector.text for connector in CohesionStats(marked).connector_spans] == plain


def test_connectors_pos(nlp):
    text = "Раз он пришёл, значит, всё хорошо. В тот раз это значит много. Словом, пусть идёт."
    assert [connector.text for connector in CohesionStats(nlp(text)).connector_spans] == [
        "раз",
        "значит",
        "словом",
    ]
    assert [connector.text for connector in CohesionStats(text).connector_spans] == [
        "раз",
        "значит",
        "словом",
    ]
    assert connector_pos("раз") == "ADV"
    assert connector_pos("Отчего") == "CCONJ"
    assert connector_pos("кот") == "NOUN"
    assert connector_pos("т.е.") == "X"
    for connector in load_connectors():
        if " " not in connector:
            words = ["кот", connector] if connector in CONNECTOR_NOT_AT_START else [connector]
            assert find_connectors(words, pos=[connector_pos(word) for word in words]), connector
    assert find_connectors(["раз", "значит"]) == [
        Connector(0, 0, 1, "раз", "conditional", "primary"),
        Connector(0, 1, 2, "значит", "causal", "primary"),
    ]
    assert find_connectors(["раз", "значит", "ждать"], pos=["NOUN", "VERB", "VERB"]) == []
    assert find_connectors(["раз", "значит"], pos=["SCONJ", None]) == [
        Connector(0, 0, 1, "раз", "conditional", "primary"),
        Connector(0, 1, 2, "значит", "causal", "primary"),
    ]
    assert find_connectors(["точнее", "т.е."], pos=["ADJ", "PUNCT"]) == [
        Connector(0, 0, 1, "точнее", "reformulative", "primary"),
        Connector(0, 1, 2, "т.е.", "reformulative", "primary"),
    ]
    assert find_connectors(["кот"], {"кот": ("additive", "secondary")}, pos=["NOUN"]) == []


def test_connector_context_rules(nlp):
    """Предлоги и омонимы коннекторов не считаются ни в строке, ни в Doc"""
    text = (
        "После обеда он уснул, а после проснулся. Пока что тихо, пока он спит. "
        "Не правда ли, он устал? Правда, ненадолго. Ещё раз прошу. "
        "Хоть бы дождь пошёл! Хоть устал, а идёт. Он едва ли придёт. Едва он вошёл, все встали. "
        "И так далее. Отчего же? Он устал, отчего и уснул. Коли хочешь, иди. Ежели устал, сядь."
    )
    expected = [
        (0, "а"),
        (0, "после"),
        (1, "пока"),
        (3, "правда"),
        (6, "хоть"),
        (6, "а"),
        (8, "едва"),
        (9, "и"),
        (11, "отчего"),
        (11, "и"),
        (12, "коли"),
        (13, "ежели"),
    ]
    for source in (text, nlp(text)):
        spans = CohesionStats(source).connector_spans
        assert [(connector.sent, connector.text) for connector in spans] == expected
    # Разметка «того», «его», «только» у pymorphy3 и spaCy расходится, итог - нет
    text = (
        "После того я уехал. После его смерти дом опустел. Накануне её отъезда шёл дождь. "
        "Едва только он вошёл, все встали. Он говорил едва слышно. Мне было всё равно."
    )
    for source in (text, nlp(text)):
        spans = CohesionStats(source).connector_spans
        assert [(connector.sent, connector.text) for connector in spans] == [
            (0, "после"),
            (3, "едва"),
        ]
    assert find_connectors(["только", "раз"]) == []
    assert find_connectors(["раз", "в", "год"]) == []
    assert find_connectors(["это", "главное"]) == []
    assert find_connectors(["уйти", "отсюда"]) == []
    assert [c.text for c in find_connectors(["и", "отсюда"])] == ["и", "отсюда"]


def test_connectors_by_place(nlp):
    """Подчинительный союз в начале предложения начинает его придаточное"""
    text = (
        "Что касается денег, их нет. Для того чтобы успеть, он бежал. Так как он устал, "
        "он сел. Потому что поздно. Как бы там ни было, мы пошли. Когда он пришёл, все встали. "
        "Однако дождь шёл. Ежели устал, сядь. Коли хочешь, иди. Пока он спал, шёл дождь. "
        "Независимо от того, придёт ли он, мы начнём."
    )
    for source in (text, nlp(text)):
        cs = CohesionStats(source)
        # Межпредложенческие: что касается, потому что, как бы там ни было, однако
        assert [connector.start for connector in cs.connector_spans] == [0] * 11
        assert cs.n_inter_connectors == 4
        assert cs.connectors_intra == pytest.approx(7 / cs.n_words * 1000)


def test_connector_rules_dictionary():
    """Ключи правил - коннекторы словаря, слова правил - в форме normalize_yo"""
    connectors = load_connectors()
    rules = (
        CONNECTOR_BLOCKED_AFTER,
        CONNECTOR_BLOCKED_BEFORE,
        CONNECTOR_ONLY_AFTER,
        CONNECTOR_BLOCKED_AFTER_POS,
    )
    for rule in rules:
        assert set(rule) <= set(connectors)
    assert set(CONNECTOR_NOT_AT_START) <= set(connectors)
    assert set(CONNECTOR_SUBORDINATORS) <= set(connectors)
    for rule in rules[:3]:
        for words in rule.values():
            assert all(word == normalize_yo(word) for word in words), words


def test_hyphenated_verb_doc(nlp):
    doc = nlp("Жили-были дед и баба. Они жили долго. Назовите-ка их, говорить-то легко.")
    cs = CohesionStats(doc)
    assert cs.words[0] == ("Жили-были", "дед", "и", "баба")
    assert cs.lemmas[0][0] == lemmatize("Жили-были", "VERB")
    assert cs.tense_repetition == 1.0
    assert cs.aspect_repetition == 0.5
    units = list(iter_doc_units(doc, join_hyphens=True))
    assert unit_info(units[0]) == WordInfo(
        lemmatize("Жили-были", "VERB"), False, False, False, False, True, "Past", "Imp"
    )
    assert unit_info(units[1]) == token_info(doc[3])
    assert (unit_info(units[7]).tense, unit_info(units[7]).aspect) == (None, "Perf")


def test_doc_without_sents(nlp):
    text = "Раз он пришёл, значит, всё хорошо. Кое-как птицы улетели, т.е. исчезли."
    doc = nlp(text)
    tagged = spacy.load("ru_core_news_sm", exclude=["parser"])(text)
    assert not tagged.has_annotation("SENT_START") and tagged.has_annotation("POS")
    cs = CohesionStats(tagged)
    assert cs.words == CohesionStats(doc).words
    assert cs.n_words == BasicStats(tagged).n_words == 11
    assert cs.lemmas == CohesionStats(doc).lemmas
    assert [connector.text for connector in cs.connector_spans] == ["раз", "значит", "т.е."]
    blank = spacy.blank("ru")(text)
    assert CohesionStats(blank).words == cs.words
    assert CohesionStats(blank).n_words == 11
    units = split_doc_units(blank, SentsExtractor(), join_hyphens=True)
    assert [[unit_text(unit) for unit in sent] for sent in units] == [
        list(sent) for sent in cs.words
    ]
    extractor = SentsExtractor(tokenizer=lambda text: ("нет такого предложения",))
    assert split_doc_units(blank, extractor) == []
    short = "Кот сидел. Пёс спал."
    with pytest.raises(SourceError):
        CohesionStats(short, sents_extractor=SentsExtractor(min_len=50))
    with pytest.raises(SourceError):
        CohesionStats(spacy.blank("ru")(short), sents_extractor=SentsExtractor(min_len=50))


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
    assert cs.n_connectors == 1
    assert cs.connectors_adversative == pytest.approx(1 / 34 * 1000)
    custom = {"если": ("conditional", "secondary"), "и всё же": ("adversative", "primary")}
    cs = CohesionStats(connectors_text, connectors=custom)
    assert cs.n_connectors == 2
    assert cs.connectors_conditional == pytest.approx(1 / 34 * 1000)
    assert CohesionStats(connectors_text, connectors={}).n_connectors == 0
    with pytest.raises(ValueError):
        find_connectors(["кот"], {"кот": ("noun", "primary")})
    with pytest.raises(ValueError):
        find_connectors(["кот"], {"кот": ("causal", "tertiary")})
    assert find_connectors(["он", "ушёл", "однако"], {"однако ": ("adversative", "primary")}) == [
        Connector(0, 2, 3, "однако ", "adversative", "primary")
    ]
    assert find_connectors(["потому", "что"], {"потому  что": ("causal", "primary")}) == [
        Connector(0, 0, 2, "потому  что", "causal", "primary")
    ]
    assert find_connectors(["кот"], {"": ("causal", "primary"), " ": ("causal", "primary")}) == []


def test_connectors_single_sentence_words(cs):
    assert cs.connector_spans == (Connector(2, 2, 3, "и", "additive", "primary"),)
    assert cs.connectors_additive == pytest.approx(1 / 21 * 1000)


def test_sents_extractor_class_of_a_subclass():
    """Свой экстрактор предложений подкласса делит и строку, и Doc без границ"""
    import re

    class Lines(SentsExtractor):
        def __init__(self):
            super().__init__(tokenizer=re.compile(r"; "))

    class LineCohesion(CohesionStats):
        sents_extractor_class = Lines

    text = "Кот спит, пёс лежит; мы ушли"
    blank = spacy.blank("ru")(text)
    counts = {
        LineCohesion(text).n_sents,
        LineCohesion(blank).n_sents,
        LineCohesion(blank, words_extractor=WordsExtractor()).n_sents,
    }
    assert counts == {2}


def test_forward_overlap(cs):
    """Доля лемм предложения, повторенных в одном из двух следующих, по всем таким предложениям"""
    # Существительные: {кот, окно} -> {птица, кот}: 1 из 2; {птица} -> {птица, кот, окно}: 1 из 1
    assert cs.noun_overlap_2_sent == pytest.approx(2 / 3)
    assert cs.argument_overlap_2_sent == pytest.approx(3 / 4)
    assert cs.n_paragraphs == 1
    assert isnan(cs.noun_overlap_para)


paragraphs = "Кот сидел на окне.\n\nКот смотрел на птиц. Птицы улетели.\n\nПтицы вернулись к коту."


def test_paragraphs(nlp):
    """Абзацы после пустой строки - у строки, Doc и Doc с экстрактором слов"""
    doc = nlp(paragraphs)
    sources = [
        CohesionStats(paragraphs),
        CohesionStats(doc),
        CohesionStats(spacy.blank("ru")(paragraphs)),
        CohesionStats(doc, words_extractor=WordsExtractor()),
    ]
    # Экстрактор, который меняет слова, не теряет абзацы: у Doc пустая строка - хвост предложения
    for extractor in (WordsExtractor(lowercase=True), WordsExtractor(use_lexemes=True)):
        sources += [
            CohesionStats(paragraphs, words_extractor=extractor),
            CohesionStats(doc, words_extractor=extractor),
        ]
    for stats in sources:
        assert stats.n_paragraphs == 3
        # {кот, окно} -> {кот, птица}: 1 из 2; {кот, птица} -> {птица, кот}: 2 из 2
        assert stats.noun_overlap_para == pytest.approx(3 / 4)


lines = "Кот сидел на окне.\nКот смотрел на птиц. Птицы улетели.\nПтицы вернулись к коту."


def test_paragraphs_are_lines(nlp):
    """Абзац - строка, как в TAACO, а с blank_lines - часть между пустыми строками"""
    doc = nlp(lines)
    sources = [lines, lines.replace("\n", "\r\n"), doc, spacy.blank("ru")(lines)]
    for source in sources:
        stats = CohesionStats(source)
        assert stats.n_paragraphs == 3 and not stats.blank_lines
        assert stats.noun_overlap_para == pytest.approx(3 / 4)
        assert CohesionStats(source, blank_lines=True).n_paragraphs == 1
    assert CohesionStats(doc, words_extractor=WordsExtractor()).n_paragraphs == 3
    assert CohesionStats(paragraphs, blank_lines=True).n_paragraphs == 3
    with pytest.raises(ParameterError, match=r"^The blank_lines must be a bool"):
        CohesionStats(lines, blank_lines="да")


def test_paragraph_without_content_words(nlp):
    """Строка без знаменательных слов - номер главы - присоединяется к следующему абзацу,
    последняя - к предыдущему"""
    text = "1\nКот сидел на окне.\nXII\nКот смотрел на птиц.\n2"
    for source in (text, nlp(text)):
        stats = CohesionStats(source)
        assert stats.n_paragraphs == 2
        # {кот, окно} -> {кот, птица}: 1 из 2
        assert stats.noun_overlap_para == pytest.approx(1 / 2)


@pytest.mark.parametrize(
    ("text", "n_paragraphs"),
    [
        ("***\n\nКот спал.\n\nКот ушел.", 2),
        ("Кот спал.\n\n***\nКот ушел. Пес лаял.\n\nПес спал.", 3),
        ("Кот спал.\r\n\r\nКот ушел.", 2),
    ],
)
def test_paragraphs_without_words(nlp, text, n_paragraphs):
    """Абзац, который начинается строкой без слов, открывает первое слово после нее"""
    assert CohesionStats(text).n_paragraphs == n_paragraphs
    assert CohesionStats(nlp(text)).n_paragraphs == n_paragraphs


def test_paragraph_inside_sentence_with_lemmas():
    """Пустая строка внутри предложения Doc: начало абзаца - по числу слов частей, а не поиском
    слова в тексте (лемма «церковь» нашлась бы внутри «Церковью»)"""
    words = ["Церковью", "гордились", ".", "\n\n", "Все", "пришли", "к", "церкви", "."]
    words += ["Пес", "спал", "."]
    spaces = [True, False, False, False, True, True, True, False, True, True, False, False]
    starts = [True] + [False] * 8 + [True, False, False]
    doc = Doc(spacy.blank("ru").vocab, words=words, spaces=spaces, sent_starts=starts)
    for extractor in (None, WordsExtractor(), WordsExtractor(use_lexemes=True)):
        stats = CohesionStats(doc, words_extractor=extractor)
        opened = [
            word.word for sent in stats.analyze(doc) for word in sent if word.paragraph_start
        ]
        assert stats.n_paragraphs == 2
        assert [normalize_yo(word) for word in opened] == ["все"]


def test_paragraph_inside_sentence(nlp):
    """Пустая строка внутри предложения Doc тоже открывает абзац"""
    doc = nlp("Глава первая\n\nКот сидел на окне.")
    assert len(list(doc.sents)) == 1
    assert CohesionStats(doc).n_paragraphs == 2
