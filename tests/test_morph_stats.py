from collections import Counter

import pytest
import spacy

from ruts import MorphStats
from ruts.constants import MORPHOLOGY_STATS_DESC
from ruts.morph_stats import (
    format_features,
    parse_verb,
    tag_to_ud,
    tag_to_ud_pos,
    token_to_ud,
    word_to_ud,
)
from ruts.utils import get_morph_analyzer

text = "Постарайтесь получить то, что любите, иначе придется полюбить то, что получили"


@pytest.fixture(scope="module")
def ms():
    return MorphStats(text)


@pytest.fixture(scope="module")
def nlp():
    pytest.importorskip("ru_core_news_sm")
    return spacy.load("ru_core_news_sm")


def make_tag(tag: str):
    return get_morph_analyzer().TagClass(tag)


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
        "CCONJ",
        "SCONJ",
        "VERB",
        "ADV",
        "VERB",
        "VERB",
        "CCONJ",
        "SCONJ",
        "VERB",
    )


def test_animacy(ms):
    assert ms.animacy == (None,) * 11


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
    assert ms.case == (None,) * 11


def test_gender(ms):
    assert ms.gender == (None,) * 11


def test_involvement(ms):
    assert ms.involvement == ("Ex",) + (None,) * 10


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
        None,
        None,
        "Plur",
        None,
        "Sing",
        None,
        None,
        None,
        "Plur",
    )


def test_person(ms):
    assert ms.person == (None, None, None, None, "2", None, "3", None, None, None, None)


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
    assert ms.voice == (None,) * 11


def test_tags(ms):
    assert ms.tags[0] == "Aspect=Perf|Clusivity=Ex|Mood=Imp|Number=Plur|Subcat=Intr|VerbForm=Fin"
    assert ms.tags[1] == "Aspect=Perf|Subcat=Tran|VerbForm=Inf"
    assert ms.tags[2] == "_"
    assert (
        ms.tags[4]
        == "Aspect=Imp|Mood=Ind|Number=Plur|Person=2|Subcat=Tran|Tense=Pres|VerbForm=Fin"
    )


def test_init_doc_blank(ms):
    doc = spacy.blank("ru")(text)
    doc_ms = MorphStats(doc)
    assert doc_ms.words == ms.words
    assert doc_ms.tags == ms.tags
    assert doc_ms.get_stats() == ms.get_stats()


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
    assert MorphStats(doc.text).pos[-1] == "VERB"


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
    assert MorphStats("Лев Толстой").pos == ("PROPN", "PROPN")


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
        ("надо", "ADV"),
        ("читал", "VERB"),
        ("читать", "VERB"),
        ("читающий", "VERB"),
        ("прочитан", "VERB"),
        ("прочитав", "VERB"),
        ("он", "PRON"),
        ("который", "PRON"),
        ("этот", "DET"),
        ("мой", "DET"),
        ("весь", "DET"),
        ("три", "NUM"),
        ("один", "NUM"),
        ("одна", "NUM"),
        ("2020", "NUM"),
        ("III", "NUM"),
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
    ("tag", "expected"),
    [
        (
            "NOUN,inan,masc sing,loc2",
            {"pos": "NOUN", "animacy": "Inan", "gender": "Masc", "number": "Sing", "case": "Loc"},
        ),
        ("NOUN,inan,masc sing,gen2", {"case": "Par"}),
        ("NOUN,anim,ms-f sing,nomn", {"gender": "Com", "case": "Nom"}),
        (
            "VERB,impf,intr plur,impr,incl",
            {
                "pos": "VERB",
                "aspect": "Imp",
                "transitivity": "Intr",
                "number": "Plur",
                "mood": "Imp",
                "involvement": "In",
                "verb_form": "Fin",
            },
        ),
        ("PRTF,impf,tran,pres,actv masc,sing,nomn", {"verb_form": "Part", "voice": "Act"}),
        ("PRTS,perf,past,pssv masc,sing", {"verb_form": "Part", "voice": "Pass", "tense": "Past"}),
        ("GRND,perf,tran past", {"verb_form": "Conv", "aspect": "Perf"}),
        ("INFN,impf,tran", {"verb_form": "Inf", "mood": None, "tense": None}),
        ("VERB,impf,tran sing,3per,pres,indc", {"person": "3", "tense": "Pres", "mood": "Ind"}),
        ("LATN", {"pos": "X", "verb_form": None}),
        ("PNCT", {"pos": "PUNCT"}),
        ("UNKN", {"pos": "X"}),
    ],
)
def test_tag_to_ud(tag, expected):
    features = tag_to_ud(make_tag(tag), "")
    assert set(features) == set(MORPHOLOGY_STATS_DESC)
    for key, value in expected.items():
        assert features[key] == value


def test_tag_to_ud_pos_lemma():
    tag = make_tag("ADJF,Subx,Apro,Anph masc,sing,nomn")
    assert tag_to_ud_pos(tag, "который") == "PRON"
    assert tag_to_ud_pos(tag, "этот") == "DET"
    assert tag_to_ud_pos(make_tag("ADJF,Apro,Anum masc,sing,nomn"), "один") == "NUM"
    tag = make_tag("NOUN,anim,masc,Name sing,nomn")
    assert tag_to_ud_pos(tag, "лев", "Лев") == "PROPN"
    assert tag_to_ud_pos(tag, "лев", "лев") == "NOUN"
    assert tag_to_ud_pos(tag, "лев") == "NOUN"
    tag = make_tag("CONJ")
    assert tag_to_ud_pos(tag, "что") == "SCONJ"
    assert tag_to_ud_pos(tag, "и") == "CCONJ"


def test_parse_verb():
    assert parse_verb("стали", "стать").normal_form == "стать"
    assert parse_verb("стали", "сталь").normal_form == "стать"
    assert parse_verb("стали").tag.POS == "VERB"
    assert parse_verb("читающий", "читать").tag.POS == "PRTF"
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


def test_format_features():
    assert format_features(dict.fromkeys(MORPHOLOGY_STATS_DESC)) == "_"
    features = dict.fromkeys(MORPHOLOGY_STATS_DESC)
    features.update({"pos": "NOUN", "number": "Sing", "case": "Nom", "animacy": "Inan"})
    assert format_features(features) == "Animacy=Inan|Case=Nom|Number=Sing"


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
    assert stats["pos"] == {"VERB": 6, "CCONJ": 2, "SCONJ": 2, "ADV": 1}
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
        },
    )


def test_print_stats(capsys, ms):
    ms.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == 32
    assert "Подчинительный союз" in captured.out
    assert "Личная форма" in captured.out


def test_print_stats_args(capsys, ms):
    ms.print_stats("pos", "tense")
    captured = capsys.readouterr()
    assert captured.out.count("|") == 8


def test_check_stat_key_error(ms, capsys):
    with pytest.raises(KeyError) as excinfo:
        ms.get_stats("foo", "tense")
    assert str(excinfo.value) == (
        "foo отсутствует в справочнике морфологических статистик, доступны: "
        + ", ".join(MORPHOLOGY_STATS_DESC)
    )
    assert capsys.readouterr().out == ""
