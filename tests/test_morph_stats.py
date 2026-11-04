from collections import Counter
from math import isnan

import pytest
import spacy
from spacy.tokens import Doc

from ruts import MorphStats, WordsExtractor
from ruts.constants import MORPHOLOGY_MARKERS_DESC, MORPHOLOGY_STATS_DESC
from ruts.morph_stats import (
    analysis_to_ud,
    answer_particles,
    find_answer_particles,
    parse_verb,
    token_to_ud,
    word_to_ud,
)
from ruts.utils import parse_word

text = "Постарайтесь получить то, что любите, иначе придется полюбить то, что получили"


@pytest.fixture(scope="module")
def ms():
    return MorphStats(text)


@pytest.fixture(scope="module")
def nlp():
    pytest.importorskip("ru_core_news_sm")
    return spacy.load("ru_core_news_sm")


def test_init_value_error():
    with pytest.raises(ValueError):
        MorphStats("+ _")


@pytest.mark.parametrize("source", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(source):
    with pytest.raises(TypeError):
        MorphStats(source)


def test_pos(ms):
    assert ms.pos == (
        "VERB",
        "VERB",
        "PRON",
        "PRON",
        "VERB",
        "ADV",
        "VERB",
        "VERB",
        "PRON",
        "PRON",
        "VERB",
    )


def test_animacy(ms):
    assert ms.animacy == (
        None,
        None,
        "Inan",
        "Inan",
        None,
        None,
        None,
        None,
        "Inan",
        "Inan",
        None,
    )


def test_aspect(ms):
    assert ms.aspect == (
        "Perf",
        "Perf",
        None,
        None,
        "Imp",
        None,
        "Perf",
        "Perf",
        None,
        None,
        "Perf",
    )


def test_case(ms):
    assert ms.case == (
        None,
        None,
        "Acc",
        "Acc",
        None,
        None,
        None,
        None,
        "Acc",
        "Acc",
        None,
    )


def test_gender(ms):
    assert ms.gender == (
        None,
        None,
        "Neut",
        "Neut",
        None,
        None,
        None,
        None,
        "Neut",
        "Neut",
        None,
    )


def test_involvement(ms):
    assert ms.involvement == (
        "Ex",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )


def test_mood(ms):
    assert ms.mood == (
        "Imp",
        None,
        None,
        None,
        "Ind",
        None,
        "Ind",
        None,
        None,
        None,
        "Ind",
    )


def test_number(ms):
    assert ms.number == (
        "Plur",
        None,
        "Sing",
        "Sing",
        "Plur",
        None,
        "Sing",
        None,
        "Sing",
        "Sing",
        "Plur",
    )


def test_person(ms):
    assert ms.person == (
        "2",
        None,
        None,
        None,
        "2",
        None,
        "3",
        None,
        None,
        None,
        None,
    )


def test_tense(ms):
    assert ms.tense == (
        None,
        None,
        None,
        None,
        "Pres",
        None,
        "Fut",
        None,
        None,
        None,
        "Past",
    )


def test_transitivity(ms):
    assert ms.transitivity == (
        "Intr",
        "Tran",
        None,
        None,
        "Tran",
        None,
        "Intr",
        "Tran",
        None,
        None,
        "Tran",
    )


def test_verb_form(ms):
    assert ms.verb_form == (
        "Fin",
        "Inf",
        None,
        None,
        "Fin",
        None,
        "Fin",
        "Inf",
        None,
        None,
        "Fin",
    )


def test_voice(ms):
    assert ms.voice == (
        "Mid",
        "Act",
        None,
        None,
        "Act",
        None,
        "Mid",
        "Act",
        None,
        None,
        "Act",
    )


def test_tags(ms):
    assert ms.tags[0] == (
        "Aspect=Perf|Clusivity=Ex|Mood=Imp|Number=Plur|Person=2|Subcat=Intr|VerbForm=Fin|Voice=Mid"
    )
    assert ms.tags[1] == "Aspect=Perf|Subcat=Tran|VerbForm=Inf|Voice=Act"
    assert ms.tags[2] == "Animacy=Inan|Case=Acc|Gender=Neut|Number=Sing"
    # «что» в «то, что любите» - местоимение, по контексту
    assert ms.tags[3] == "Animacy=Inan|Case=Acc|Gender=Neut|Number=Sing"
    assert ms.tags[4] == (
        "Aspect=Imp|Mood=Ind|Number=Plur|Person=2|Subcat=Tran|Tense=Pres|VerbForm=Fin|Voice=Act"
    )


def test_init_doc_blank(ms):
    doc = spacy.blank("ru")(text)
    doc_ms = MorphStats(doc)
    assert doc_ms.words == ms.words
    assert doc_ms.tags == ms.tags
    assert doc_ms.get_stats() == ms.get_stats()
    # Слова те же, что у строки, - разбор в контексте, иначе (т.е. одним токеном) - по слову
    nlp = spacy.blank("ru")
    assert MorphStats(nlp("Нож сделан из стали.")).pos[-1] == "NOUN"
    assert MorphStats(nlp("Нож сделан из стали, т.е. из металла.")).pos[3] == "VERB"


def test_init_doc_byte_order_mark():
    """BOM в начале Doc не входит в слово, как в строке"""
    text_ms, doc_ms = MorphStats("\ufeff2020 год"), MorphStats(spacy.blank("ru")("\ufeff2020 год"))
    assert doc_ms.words == text_ms.words == ("2020", "год")
    assert doc_ms.get_stats() == text_ms.get_stats()


def test_init_doc_context(nlp):
    doc = nlp("Мы стали ждать, а нож сделан из стали.")
    ms = MorphStats(doc)
    assert ms.words == ("Мы", "стали", "ждать", "а", "нож", "сделан", "из", "стали")
    assert ms.pos == ("PRON", "VERB", "VERB", "CCONJ", "NOUN", "VERB", "ADP", "NOUN")
    assert ms.case == ("Nom", None, None, None, "Nom", None, None, "Gen")
    assert ms.person == ("1", None, None, None, None, None, None, None)
    assert ms.verb_form == (None, "Fin", "Inf", None, None, "Part", None, None)
    assert ms.voice == (None, "Act", "Act", None, None, "Pass", None, None)
    assert ms.transitivity == (None, "Intr", "Tran", None, None, None, None, None)
    assert (
        ms.tags[1]
        == "Aspect=Perf|Mood=Ind|Number=Plur|Subcat=Intr|Tense=Past|VerbForm=Fin|Voice=Act"
    )
    # Строка разбирается в контексте, как Doc, а заданный экстрактор слов - по слову
    assert MorphStats(doc.text).pos[-1] == "NOUN"
    assert MorphStats(doc.text, words_extractor=WordsExtractor()).pos[-1] == "VERB"


def test_proper_nouns_by_case():
    ms = MorphStats("лев лежит на полу, мороз крепчает, один улей и два цветка")
    assert ms.pos == (
        "NOUN",
        "VERB",
        "ADP",
        "NOUN",
        "NOUN",
        "VERB",
        "NUM",
        "NOUN",
        "CCONJ",
        "NUM",
        "NOUN",
    )
    # «Лев» перед фамилией контекстная модель ruMorph 0.5 размечает NOUN (находка в плане ruMorph)
    assert MorphStats("Роза Люксембург").pos == ("PROPN", "PROPN")


def test_init_doc_verbs(nlp):
    ms = MorphStats(nlp("Идите домой. Он умылся и был готов."))
    assert ms.pos == ("VERB", "ADV", "PRON", "VERB", "CCONJ", "AUX", "ADJ")
    assert ms.involvement == ("Ex", None, None, None, None, None, None)
    assert ms.transitivity == ("Intr", None, None, "Intr", None, "Intr", None)
    assert ms.voice == ("Act", None, None, "Mid", None, "Act", None)
    assert ms.mood == ("Imp", None, None, "Ind", None, "Ind", None)


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("кот", "NOUN"),
        ("Иван", "PROPN"),
        ("Петров", "PROPN"),
        ("Москва", "PROPN"),
        ("лев", "NOUN"),
        ("Лев", "PROPN"),
        ("мороз", "NOUN"),
        ("роза", "NOUN"),
        ("улей", "NOUN"),
        ("красивый", "ADJ"),
        ("красив", "ADJ"),
        ("лучше", "ADJ"),
        ("первый", "ADJ"),
        ("быстро", "ADV"),
        ("надо", "VERB"),
        ("читал", "VERB"),
        ("читать", "VERB"),
        ("читающий", "VERB"),
        ("прочитан", "VERB"),
        ("прочитав", "VERB"),
        ("он", "PRON"),
        ("который", "DET"),
        ("этот", "DET"),
        ("мой", "DET"),
        ("весь", "DET"),
        ("три", "NUM"),
        ("один", "NUM"),
        ("одна", "NUM"),
        ("2020", "ADJ"),
        ("III", "ADJ"),
        ("в", "ADP"),
        ("и", "CCONJ"),
        ("что", "SCONJ"),
        ("если", "SCONJ"),
        ("не", "PART"),
        ("ой", "INTJ"),
        ("USA", "X"),
    ],
)
def test_word_to_ud_pos(word, expected):
    assert word_to_ud(word)["pos"] == expected


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        (
            "пойдемте",
            {
                "pos": "VERB",
                "aspect": "Perf",
                "transitivity": "Intr",
                "number": "Plur",
                "mood": "Imp",
                "involvement": "In",
                "verb_form": "Fin",
            },
        ),
        ("читающий", {"verb_form": "Part", "voice": "Act", "transitivity": "Tran"}),
        (
            "прочитан",
            {"verb_form": "Part", "voice": "Pass", "tense": "Past", "style_variant": "Short"},
        ),
        ("краток", {"pos": "ADJ", "degree": "Pos", "style_variant": "Short"}),
        ("важнейший", {"degree": "Sup", "style_variant": None}),
        ("лучше", {"pos": "ADJ", "degree": "Cmp"}),
        ("быстро", {"degree": "Pos"}),
        ("этот", {"pos": "DET", "degree": None}),
        ("не", {"pos": "PART", "polarity": "Neg"}),
        ("прочитав", {"verb_form": "Conv", "aspect": "Perf", "tense": "Past"}),
        ("надо", {"pos": "VERB", "tense": None, "degree": None, "verb_form": None}),
        ("читать", {"verb_form": "Inf", "mood": None, "tense": None}),
        ("читает", {"person": "3", "tense": "Pres", "mood": "Ind"}),
    ],
)
def test_analysis_to_ud(word, expected):
    features = analysis_to_ud(parse_word(word))
    assert set(features) == set(MORPHOLOGY_STATS_DESC)
    for key, value in expected.items():
        assert features[key] == value, key


@pytest.mark.parametrize(
    ("text", "tense", "doc_tense"),
    [
        ("Надо идти. Нельзя молчать. Было надо спать.", {"Past": 1}, {"Past": 1}),
        ("Меня нет дома. Хлеба нету.", {}, {"Pres": 2}),
    ],
)
def test_predicatives_tense(nlp, text, tense, doc_tense):
    """Предикативы (надо, нельзя) и бытийные «нет», «нету» у ruMorph - без времени;
    у ru_core_news_sm бытийные - в настоящем"""
    assert MorphStats(text).get_stats("tense", filter_none=True) == {"tense": tense}
    assert MorphStats(nlp(text)).get_stats("tense", filter_none=True) == {"tense": doc_tense}


def test_degree_polarity_short_forms(nlp):
    """Степень, отрицание и краткая форма строки - по правилам русского UD, как у Doc"""
    text = "Он не рад. Книга прочитана. Он бежал быстрее и быстро. Ни один кот не спит."
    expected = {
        "degree": {"Pos": 2, "Cmp": 1},
        "polarity": {"Neg": 3},
        "style_variant": {"Short": 2},
    }
    stats = ("degree", "polarity", "style_variant")
    assert MorphStats(text).get_stats(*stats, filter_none=True) == expected
    assert MorphStats(nlp(text)).get_stats(*stats, filter_none=True) == expected
    analytic = "Этот вопрос более важен, а тот менее интересен."
    expected = {"degree": {"Cmp": 2, "Pos": 2}}
    assert MorphStats(analytic).get_stats("degree", filter_none=True) == expected
    assert MorphStats(nlp(analytic)).get_stats("degree", filter_none=True) == expected


def test_comparative_adverbs(nlp):
    """«выше» и «ниже» - сравнительная степень, как у Doc"""
    text = "Солнце поднималось всё выше и выше. Температура упала ниже нуля."
    expected = {"degree": {"Cmp": 3}}
    assert MorphStats(text).get_stats("degree", filter_none=True) == expected
    assert MorphStats(nlp(text)).get_stats("degree", filter_none=True) == expected


def test_existential_verb(nlp):
    """Бытийное и связочное «есть» - глагол «быть» в настоящем времени, как у Doc"""
    text = "У меня есть книга. Ленинизм есть марксизм эпохи империализма."
    expected = {"tense": {"Pres": 2}, "verb_form": {"Fin": 2}}
    assert MorphStats(text).get_stats("tense", "verb_form", filter_none=True) == expected
    assert MorphStats(nlp(text)).get_stats("tense", "verb_form", filter_none=True) == expected


def test_answer_particle(nlp):
    """Ответное «нет» - частица; бытийное у ruMorph - глагол с отрицанием без времени,
    у ru_core_news_sm - в настоящем без отрицания"""
    text = "Нет, я не пойду. Денег нет."
    expected = {"tense": {"Fut": 1}, "polarity": {"Neg": 3}}
    for source in (text, spacy.blank("ru")(text)):
        assert MorphStats(source).get_stats("tense", "polarity", filter_none=True) == expected
    expected = {"tense": {"Fut": 1, "Pres": 1}, "polarity": {"Neg": 2}}
    assert MorphStats(nlp(text)).get_stats("tense", "polarity", filter_none=True) == expected
    assert MorphStats(text).pos[0] == "PART"
    # Слово с неразрывным дефисом не сбивает счет «нет» в словах и в тексте
    hyphenated = "Нет, я не пойду. Нет\u2011нет да и заглянет."
    assert MorphStats(hyphenated).pos[0] == "PART"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Нет, денег нет. Или нет?", [True, False, True]),
        ("— Нет, — сказал он.", [True]),
        ("Да нет же. Ну нет!", [True, True]),
        ("Если нет, то что? Он ответил: нет.", [True, True]),
        ("Его нет? Нет денег. Хлеба нет — магазин закрыт.", [False, False, False]),
        # «нет» в дефисных словах, в том числе с неразрывным дефисом, не считается
        ("Нет, не пойду. Нет-нет да и заглянет. Нет\u2011с, Да\u2010нет.", [True]),
        ("Кот спит.", []),
    ],
)
def test_find_answer_particles(text, expected):
    assert find_answer_particles(text) == expected


def test_answer_particles_mismatch():
    """Если «нет» в словах и в тексте не совпали, ответных «нет» не ищут"""
    assert answer_particles(["нет", "кот"], "Нет, кот.") == [True, False]
    assert answer_particles(["нет"], "Кот.") == [False]


def test_word_to_ud_copy():
    features = word_to_ud("кот")
    features["pos"] = "X"
    assert word_to_ud("кот")["pos"] == "NOUN"


def test_short_form_of_ud_annotation():
    """Краткая форма разметки русского UD (Variant=Short) читается как StyleVariant модели"""
    vocab = spacy.blank("ru").vocab
    doc = Doc(vocab, words=["Он", "рад"], pos=["PRON", "ADJ"], morphs=["", "Variant=Short"])
    ms = MorphStats(doc)
    assert ms.style_variant == (None, "Short")
    assert ms.tags[1] == "StyleVariant=Short"


def test_parse_verb():
    assert parse_verb("стали", "стать").lemma == "стать"
    assert parse_verb("стали", "сталь").lemma == "стать"
    assert parse_verb("стали").pos == "VERB"
    assert parse_verb("читающий", "читать").feats["VerbForm"] == "Part"
    assert parse_verb("стол") is None


def test_token_to_ud(nlp):
    doc = nlp("Я читаю.")
    features = token_to_ud(doc[1])
    assert features["pos"] == "VERB"
    assert features["person"] == "1"
    assert features["transitivity"] == "Tran"
    assert features["verb_form"] == "Fin"
    assert token_to_ud(doc[0])["person"] == "1"
    assert token_to_ud(doc[2])["pos"] == "PUNCT"
    assert token_to_ud(spacy.blank("ru")("слово")[0]) == dict.fromkeys(MORPHOLOGY_STATS_DESC)


def test_get_stats(ms):
    stats = ms.get_stats()
    assert isinstance(stats, dict)
    assert list(stats) == list(MORPHOLOGY_STATS_DESC)
    for key in MORPHOLOGY_STATS_DESC:
        assert stats[key] == Counter(getattr(ms, key))


def test_get_stats_args(ms):
    stats = ms.get_stats("pos", "tense")
    assert set(stats.keys()) == {"pos", "tense"}


def test_get_stats_filter_none(ms):
    stats = ms.get_stats(filter_none=True)
    assert all(None not in v for v in stats.values())
    assert stats["pos"] == {"VERB": 6, "PRON": 4, "ADV": 1}
    assert stats["verb_form"] == {"Fin": 4, "Inf": 2}


def test_explain_text(ms):
    explain = ms.explain_text()
    assert isinstance(explain, tuple)
    assert next(zip(*explain, strict=False)) == ms.words


def test_explain_text_args(ms):
    explain = ms.explain_text("pos", "tense")
    assert all(set(v.keys()) == {"pos", "tense"} for v in tuple(zip(*explain, strict=False))[1])


def test_explain_text_filter_none(ms):
    explain = ms.explain_text(filter_none=True)
    assert all(None not in v.values() for v in tuple(zip(*explain, strict=False))[1])
    assert explain[4] == (
        "любите",
        {
            "pos": "VERB",
            "aspect": "Imp",
            "mood": "Ind",
            "number": "Plur",
            "person": "2",
            "tense": "Pres",
            "transitivity": "Tran",
            "verb_form": "Fin",
            "voice": "Act",
        },
    )


def test_print_stats(capsys, ms):
    ms.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == 40
    assert "Местоимение-существительное" in captured.out
    assert "Личная форма" in captured.out


def test_print_stats_args(capsys, ms):
    ms.print_stats("pos", "tense")
    captured = capsys.readouterr()
    assert captured.out.count("|") == 7


def test_check_stat_key_error(ms, capsys):
    with pytest.raises(KeyError) as excinfo:
        ms.get_stats("foo", "tense")
    assert str(excinfo.value) == (
        f"Неизвестная статистика: foo. Доступные статистики: {tuple(MORPHOLOGY_STATS_DESC)}"
    )
    assert capsys.readouterr().out == ""


def test_print_stats_value_without_description(capsys):
    ms = MorphStats(text)
    ms.case = ("Abl", *ms.case[1:])
    ms.print_stats("case")
    assert "Abl " in capsys.readouterr().out


def test_lemmas(ms):
    assert "lemmas" not in MorphStats(text).__dict__
    assert ms.lemmas[:3] == ("постараться", "получить", "то")
    assert len(ms.lemmas) == len(ms.words)


def test_lemmas_doc(nlp):
    ms = MorphStats(nlp("Стали из стали делали ножи"))
    assert ms.lemmas == ("стать", "из", "сталь", "делать", "нож")


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "Если бы я знал, я бы пришел за книгами, прочитанными вчера",
            {"p_indicative": 0.0, "p_conditional": 1.0, "p_participle": 1 / 3, "p_passive": 1 / 3},
        ),
        ("Иди сюда, не спорь", {"p_imperative": 1.0, "p_perfective": 0.0}),
        ("Хорошо бы ему уехать, а он остаётся и молчит", {"p_conditional": 0.0}),
        ("Статью подписали А. Б. Иванов и В. Г. Петров", {"p_conditional": 0.0}),
        ("ЕСЛИ БЫ Я ЗНАЛ, Я БЫ ПРИШЁЛ", {"p_conditional": 1.0}),
        ("Бы знать заранее, я б пришел", {"p_conditional": 1.0}),
        ("Он учился, улыбаясь, и решил прочитать", {"p_converb": 0.25, "p_infinitive": 0.25}),
        ("Он учился, улыбаясь, и решил прочитать", {"p_reflexive": 0.5, "p_perfective": 0.5}),
    ],
)
def test_get_markers(source, expected):
    markers = MorphStats(source).get_markers()
    assert list(markers) == list(MORPHOLOGY_MARKERS_DESC)
    for marker, value in expected.items():
        assert markers[marker] == pytest.approx(value)


def test_get_markers_doc(nlp):
    source = "Если бы я знал, я бы пришел за книгами, прочитанными вчера. Иди сюда!"
    assert MorphStats(nlp(source)).get_markers() == pytest.approx(MorphStats(source).get_markers())


def test_get_markers_of_several_values(nlp):
    """Признак из нескольких значений Doc входит в долю каждого значения"""
    doc = nlp("Я вижу дом и стол.")
    doc[1].set_morph("Aspect=Imp|Mood=Ind,Imp|Number=Sing|Person=First|Tense=Pres|VerbForm=Fin")
    markers = MorphStats(doc).get_markers()
    assert (markers["p_indicative"], markers["p_imperative"], markers["p_conditional"]) == (
        1.0,
        1.0,
        0.0,
    )


def test_doc_without_morphologizer():
    """Без морфологического анализатора части речи есть только у пробелов: признаки -
    по ruMorph, как у Doc без разметки"""
    nlp = spacy.load("ru_core_news_sm", exclude=["morphologizer"])
    doc = nlp("Мама мыла раму.\n\nПапа читал книгу.")
    assert doc.has_annotation("POS")
    assert MorphStats(doc).pos == MorphStats(spacy.blank("ru")(doc.text)).pos
    assert MorphStats(doc).pos[0] == "NOUN"


def test_get_markers_empty_base():
    markers = MorphStats("Кот и пёс").get_markers()
    assert all(isnan(value) for value in markers.values())


def test_print_markers(capsys):
    MorphStats("Иди сюда").print_markers()
    output = capsys.readouterr().out
    for desc in MORPHOLOGY_MARKERS_DESC.values():
        assert desc in output


def test_stats_interface(ms):
    """Плоские статистики, таблица и прочтение базового класса ядра"""
    flat = ms.get_stats("pos", flat=True)
    assert flat == {f"pos_{value}": n for value, n in ms.get_stats("pos")["pos"].items() if value}
    assert not any(key.endswith("_None") for key in ms.get_stats(flat=True))
    frame = ms.to_dataframe()
    assert len(frame) == 1 and set(frame.columns) == set(ms.get_stats(flat=True))
    assert ms.describe("case") is None
    with pytest.raises(KeyError):
        ms.describe("foo")


def test_multiple_values_of_a_feature():
    """Признак из нескольких значений разметки сохраняется целиком, как в ядре"""
    doc = Doc(
        spacy.blank("ru").vocab,
        words=["мама", "мыла"],
        pos=["NOUN", "VERB"],
        morphs=["Case=Acc,Nom|Number=Sing", "Tense=Past|VerbForm=Fin"],
    )
    ms = MorphStats(doc)
    assert ms.case == ("Acc,Nom", None)
    assert ms.tags[0] == "Case=Acc,Nom|Number=Sing"
