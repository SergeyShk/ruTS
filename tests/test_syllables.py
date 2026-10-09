import pytest

import ruts.phon_stats
import ruts.verse_stats
from ruts.datasets import StressDict
from ruts.datasets.stress_dict import FILENAME
from ruts.exceptions import SourceTypeError
from ruts.syllables import (
    _default_stress_dict,
    count_syllables,
    stress_type,
    syllabify,
    word_stress,
    word_stresses,
)

ROWS = (
    ("белый", "б^елый"),
    ("воевода", "воев^ода"),
    ("воровка", "вор^овка"),
    ("выскочивший", "в^ыскочивший"),
    ("далеко-далеко", "далеко-далек^о"),
    ("еще", "^еще"),
    ("желание", "жел^ание"),
    ("желания", "жел^ания"),
    ("забывший", "заб^ывший"),
    ("земля", "земл^я"),
    ("золото", "з^олото"),
    ("корова", "кор^ова"),
    ("мороз", "мор^оз"),
    ("прежнему", "пр^ежнему"),
    ("сорок", "с^орок"),
)


@pytest.fixture(scope="module")
def stress_dict(tmp_path_factory):
    path = tmp_path_factory.mktemp("dicts")
    lines = "\n".join("\t".join(row) for row in sorted(ROWS)) + "\n"
    path.joinpath(FILENAME).write_text(lines, encoding="utf-8")
    return StressDict(data_dir=path)


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("корова", ["ко", "ро", "ва"]),
        ("кошка", ["ко", "шка"]),
        ("сестра", ["се", "стра"]),
        ("познакомить", ["по", "зна", "ко", "мить"]),
        ("открыть", ["о", "ткрыть"]),
        ("карта", ["кар", "та"]),
        ("полка", ["пол", "ка"]),
        ("волна", ["вол", "на"]),
        ("карман", ["кар", "ман"]),
        ("майка", ["май", "ка"]),
        ("война", ["вой", "на"]),
        ("район", ["ра", "йон"]),
        ("большой", ["боль", "шой"]),
        ("подъезд", ["по", "дъезд"]),
        ("аэропорт", ["а", "э", "ро", "порт"]),
        ("заяц", ["за", "яц"]),
        ("ёлка", ["ёл", "ка"]),
        ("Мама", ["ма", "ма"]),
        ("к", []),
        ("вскрь", []),
        ("дом", ["дом"]),
        ("какого-либо", ["ка", "ко", "го", "ли", "бо"]),
        ("сорок-воровка", ["со", "рок", "во", "ро", "вка"]),
        ("в-третьих", ["втре", "тьих"]),
        ("да-с", ["дас"]),
        ("100", []),
        ("", []),
    ],
)
def test_syllabify(word, expected):
    assert syllabify(word) == expected


def test_syllabify_joins_back():
    for word in ("здравствуйте", "электричество", "подъёмник"):
        assert "".join(syllabify(word)) == word


def test_word_stress(stress_dict):
    assert word_stress("корова", stress_dict) == 1
    assert word_stress("Корова", stress_dict) == 1
    assert word_stress("ёжик", stress_dict) == 0
    assert word_stress("мой", stress_dict) == 0
    assert word_stress("еще", stress_dict) == 1
    assert word_stress("ещё", stress_dict) == 1
    assert word_stress("бою", stress_dict) == 1
    assert word_stress("спешит", stress_dict) == 1
    assert word_stress("кто-нибудь", stress_dict) == 0
    assert word_stress("по-прежнему", stress_dict) == 1
    assert word_stress("мороз-воевода", stress_dict) == 4
    assert word_stress("все-таки", stress_dict) == 0
    assert word_stress("желанье", stress_dict) == 1
    assert word_stress("желанья", stress_dict) == 1
    assert word_stress("забыв", stress_dict) == 1
    assert word_stress("забывши", stress_dict) == 1
    assert word_stress("собака", stress_dict) is None
    assert word_stress("собака-корова", stress_dict) is None
    assert word_stress("вздрогнув", stress_dict) is None
    assert word_stress("ь", stress_dict) is None
    assert word_stress("xyz", stress_dict) is None


def test_count_syllables():
    for word in ("корова", "Здравствуйте", "какого-либо", "вскрь", "100", ""):
        assert count_syllables(word) == len(syllabify(word))


def test_word_stresses(stress_dict):
    assert word_stresses("корова", stress_dict) == [1]
    assert word_stresses("мороз-воевода", stress_dict) == [1, 4]
    assert word_stresses("сорок-воровка", stress_dict) == [0, 3]
    assert word_stresses("кто-нибудь", stress_dict) == [0]
    assert word_stresses("корова-ли", stress_dict) == [1]
    assert word_stresses("корова-же", stress_dict) == [1]
    assert word_stresses("по-прежнему", stress_dict) == [1]
    assert word_stresses("по-то", stress_dict) == [0]
    assert word_stresses("собака-корова", stress_dict) == []
    assert word_stresses("xyz", stress_dict) == []


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("земля", "мужская"),
        ("корова", "женская"),
        ("золото", "дактилическая"),
        ("выскочивший", "гипердактилическая"),
        ("мороз-воевода", "женская"),
        ("собака", None),
        ("ь", None),
    ],
)
def test_stress_type(stress_dict, word, expected):
    assert stress_type(word, stress_dict) == expected


@pytest.mark.parametrize(
    "function", [syllabify, count_syllables, word_stress, word_stresses, stress_type]
)
@pytest.mark.parametrize("word", [None, 42, ["корова"]])
def test_word_type_error(function, word):
    with pytest.raises(SourceTypeError):
        function(word)


def test_default_stress_dict(stress_dict, monkeypatch):
    created = []
    monkeypatch.setattr("ruts.syllables.StressDict", lambda: created.append(1) or stress_dict)
    _default_stress_dict.cache_clear()
    try:
        assert word_stress("корова") == 1
        assert word_stresses("корова") == [1]
        assert stress_type("корова") == "женская"
        assert created == [1]
    finally:
        # Тестовый словарь не должен остаться словарем по умолчанию для других тестов
        _default_stress_dict.cache_clear()


def test_previous_modules():
    assert ruts.phon_stats.syllabify is syllabify
    assert ruts.verse_stats.word_stress is word_stress


def test_compound_stresses_with_yo(stress_dict):
    assert word_stresses("чёрно-белый", stress_dict) == [0, 2]
    assert word_stresses("далёко-далёко", stress_dict) == [1, 4]
    assert word_stresses("далеко-далеко", stress_dict) == [5]
    assert word_stresses("всё-таки", stress_dict) == [0]
    assert word_stresses("ёлка-собака", stress_dict) == [0]
    assert stress_type("чёрно-белый", stress_dict) == "женская"


def test_stress_marks():
    """Знаки снимаются, а ударение по знаку важнее словаря - словарь не нужен"""
    assert count_syllables("домá") == count_syllables("дома") == 2
    assert syllabify("ѐлка") == syllabify("елка")
    assert syllabify("зѝма") == syllabify("зима")
    assert syllabify("со­лнце") == syllabify("солнце")
    assert word_stress("за́мок") == 0
    assert word_stress("замо́к") == 1
    assert word_stress("си́роты") == 0
    assert word_stresses("домá") == [1]
    assert stress_type("домá") == "мужская"
    assert stress_type("за́мок") == "женская"
