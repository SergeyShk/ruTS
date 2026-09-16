import pytest
import spacy

from ruts.corpus import Concordance, format_kwic, kwic, print_kwic

text = "Кот сидел на окне. Кота звали Васька, и кот любил окно. Потому что кот спал."


def test_kwic():
    assert kwic(text, "кот", window=2) == [
        Concordance(0, 3, "", "Кот", "сидел на"),
        Concordance(40, 43, "Васька, и", "кот", "любил окно"),
        Concordance(67, 70, "Потому что", "кот", "спал"),
    ]
    assert kwic(text, "кот", window=0) == [
        Concordance(0, 3, "", "Кот", ""),
        Concordance(40, 43, "", "кот", ""),
        Concordance(67, 70, "", "кот", ""),
    ]
    assert [line.keyword for line in kwic(text, "кот", ignore_case=False)] == ["кот", "кот"]
    assert [line.keyword for line in kwic(text, "кот", by_lemma=True)] == [
        "Кот",
        "Кота",
        "кот",
        "кот",
    ]
    assert kwic(text, "любил окно", window=1) == [
        Concordance(44, 54, "кот", "любил окно", ". Потому")
    ]
    assert kwic(text, "любить окно", by_lemma=True, window=1) == [
        Concordance(44, 54, "кот", "любил окно", ". Потому")
    ]
    assert kwic(text, "Ваську", by_lemma=True)[0].keyword == "Васька"
    assert kwic(text, "собака") == []
    assert kwic("кот кот кот", "кот кот") == [Concordance(0, 7, "", "кот кот", "кот")]
    assert kwic("Кот:\n\n  «сидел» тихо", "сидел", window=1) == [
        Concordance(9, 14, "Кот: «", "сидел", "» тихо")
    ]


def test_kwic_doc():
    nlp = spacy.blank("ru")
    assert kwic(nlp(text), "кот", window=2) == kwic(text, "кот", window=2)
    doc = nlp("Во-первых, кот спал. Во-вторых, кот ел.")
    assert kwic(doc, "во-первых") == [
        Concordance(0, 9, "", "Во-первых", ", кот спал. Во-вторых, кот ел")
    ]


def test_kwic_errors():
    with pytest.raises(TypeError):
        kwic(["кот"], "кот")
    with pytest.raises(ValueError):
        kwic(text, "  ")
    with pytest.raises(ValueError):
        kwic(text, "кот", window=-1)


def test_format_kwic(capsys):
    lines = kwic(text, "кот", window=2, by_lemma=True)
    formatted = format_kwic(lines, width=10)
    assert formatted.split("\n") == [
        "            Кот   сидел на",
        "  на окне.  Кота  звали Вась",
        " Васька, и  кот   любил окно",
        "Потому что  кот   спал",
    ]
    assert format_kwic([]) == ""
    print_kwic(lines, width=10)
    assert capsys.readouterr().out == formatted + "\n"
