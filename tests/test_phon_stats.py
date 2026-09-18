import random
from collections import Counter
from math import isnan, log2, nan

import pytest
import spacy

from ruts import PhonStats
from ruts.constants import PHON_STATS_DESC
from ruts.phon_stats import (
    CONSONANTS,
    VOWELS,
    _calc_repetition_index,
    calc_alliteration,
    calc_assonance,
    calc_consonant_clusters,
    calc_cv_entropy,
    calc_hiatus,
    cv_pattern,
    is_open_syllable,
    syllabify,
)

text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"


@pytest.fixture(scope="module")
def ps():
    return PhonStats(text)


def test_init_value_error():
    with pytest.raises(ValueError):
        PhonStats("+ _")
    with pytest.raises(ValueError):
        PhonStats(text, window_len=1)


@pytest.mark.parametrize("source", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(source):
    with pytest.raises(TypeError):
        PhonStats(source)


def test_init_doc(ps):
    doc = spacy.blank("ru")(text)
    assert PhonStats(doc).words == ps.words
    assert PhonStats(doc).get_stats() == ps.get_stats()


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
        ("100", []),
        ("", []),
    ],
)
def test_syllabify(word, expected):
    assert syllabify(word) == expected


def test_syllabify_joins_back():
    for word in ("здравствуйте", "электричество", "подъёмник"):
        assert "".join(syllabify(word)) == word


@pytest.mark.parametrize(
    ("word", "expected"),
    [("мама", "CVCV"), ("боль", "CVC"), ("я", "V"), ("ъ", ""), ("100", ""), ("Ёж-2", "VC")],
)
def test_cv_pattern(word, expected):
    assert cv_pattern(word) == expected


@pytest.mark.parametrize(
    ("syllable", "expected"),
    [("ма", True), ("боль", False), ("ко", True), ("порт", False), ("а", True), ("ткрыть", False)],
)
def test_is_open_syllable(syllable, expected):
    assert is_open_syllable(syllable) is expected


def test_letter_counts(ps):
    # 62 звука: 25 гласных, 7 сонорных, 12 звонких, 18 глухих; три мягких знака не считаются
    assert (ps.n_vowels, ps.n_sonorants, ps.n_voiced, ps.n_voiceless) == (25, 7, 12, 18)
    assert ps.n_consonants == 37
    assert ps.n_marks == 3
    assert ps.p_vowels == pytest.approx(25 / 62)
    assert ps.p_sonorants == pytest.approx(7 / 62)
    assert ps.p_voiced == pytest.approx(12 / 62)
    assert ps.p_voiceless == pytest.approx(18 / 62)
    assert ps.consonant_vowel_ratio == pytest.approx(37 / 25)
    assert ps.hardness == pytest.approx(18 / (25 + 7))


def test_marks_not_counted():
    ps = PhonStats("боль объём")
    assert ps.n_marks == 2
    assert ps.p_vowels + ps.p_sonorants + ps.p_voiced + ps.p_voiceless == pytest.approx(1.0)


def test_consonant_clusters(ps):
    assert calc_consonant_clusters(["здравствуйте", "мама"]) == {1: 2, 2: 1, 3: 1, 4: 1}
    assert calc_consonant_clusters(["большой"]) == {1: 2, 2: 1}
    assert calc_consonant_clusters(["а", "100"]) == {}
    assert ps.c_clusters == {1: 22, 2: 6, 3: 1}
    assert ps.p_heavy_clusters == pytest.approx(1 / 29)


def test_hiatus(ps):
    # йотированные гласные после гласной зияния не образуют: за-яц, поэзи-я, чита-ет
    assert calc_hiatus(["аэропорт", "поэзия", "заяц", "мама"]) == 2
    assert calc_hiatus(["аист", "свои", "читает", "красивая", "моя"]) == 2
    assert calc_hiatus(["аэроион", "ааа"]) == 3
    assert ps.p_hiatus == 0.0
    assert PhonStats("поэзия и аэропорт").p_hiatus == pytest.approx(2 / 3)


def test_cv_entropy(ps):
    assert calc_cv_entropy(["мама", "папа", "дом", "кот"]) == pytest.approx(1.0)
    assert calc_cv_entropy(["мама", "мама"]) == 0.0
    assert isnan(calc_cv_entropy(["100", "ok"]))
    assert ps.cv_entropy == pytest.approx(3.1395722619867223)
    assert ps.cv_entropy <= log2(len(ps.words))


def test_alliteration():
    # повторы м и р сгруппированы в начале текста - чаще ожидаемого
    clustered = ["мороз", "мера", "мир", "кит", "лес", "сук", "гол", "пар"]
    assert calc_alliteration(clustered, window_len=2) > 1
    # ожидаемое считается по частотам букв самого текста: если м есть в каждом слове,
    # повторы м не отличаются от ожидаемых
    assert calc_alliteration(["мороз", "мера", "мир", "мост"], window_len=2) <= 1
    # окно длиннее текста
    assert isnan(calc_alliteration(["мама", "мыла"], window_len=3))
    # согласные не повторяются ни в одном окне
    assert calc_alliteration(["дом", "кит", "лес"], window_len=2) == 0.0


def repetition_index_by_windows(text, letters, window_len):
    # прямой перебор окон со счетчиком букв - эталон для векторного расчета
    tokens = [{letter for letter in word.lower() if letter in letters} for word in text]
    n_words = len(tokens)
    if n_words < window_len:
        return nan
    n_windows = n_words - window_len + 1
    observed = 0
    for i in range(n_windows):
        counts = Counter(letter for token in tokens[i : i + window_len] for letter in token)
        observed += sum(1 for count in counts.values() if count >= 2)
    expected = 0.0
    for count in Counter(letter for token in tokens for letter in token).values():
        p = count / n_words
        p_single = window_len * p * (1 - p) ** (window_len - 1)
        expected += n_windows * (1 - (1 - p) ** window_len - p_single)
    return observed / expected if expected else nan


@pytest.mark.parametrize("window_len", [2, 3, 5])
def test_repetition_index_matches_windows(window_len):
    rng = random.Random(0)
    alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюяЙЁ-1x"
    for _ in range(80):
        words = [
            "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 8)))
            for _ in range(rng.randint(0, 30))
        ]
        for letters in (CONSONANTS, VOWELS):
            expected = repetition_index_by_windows(words, letters, window_len)
            actual = _calc_repetition_index(words, letters, window_len)
            assert actual == pytest.approx(expected, nan_ok=True)
    assert calc_alliteration(["Мороз", "МЕРА", "мир"], window_len=2) == calc_alliteration(
        ["мороз", "мера", "мир"], window_len=2
    )


def test_assonance(ps):
    # а сгруппирована в первых трех словах: 3 окна с повтором при 1.94 ожидаемых
    clustered = ["сад", "мак", "бал", "кит", "лис", "дым"]
    assert calc_assonance(clustered, window_len=2) == pytest.approx(3 / (5 / 4 + 5 / 9 + 5 / 36))
    assert calc_assonance(["сад", "мак", "бал", "вал"], window_len=2) == pytest.approx(1.0)
    assert calc_assonance(["дом", "кит", "лес"], window_len=2) == 0.0
    assert ps.assonance == pytest.approx(0.802520508857449)
    assert PhonStats(text, window_len=5).alliteration != pytest.approx(ps.alliteration)


def test_syllable_stats(ps):
    assert ps.syllables[:4] == (("ног",), ("нет",), ("а",), ("хо", "жу"))
    assert sum(len(word) for word in ps.syllables) == ps.n_vowels
    # предлоги без гласных слога не образуют и не смещают статистики слогов
    with_clitics = PhonStats("в лесу к дому с мамой")
    assert with_clitics.syllables[0] == ()
    assert sum(len(word) for word in with_clitics.syllables) == with_clitics.n_vowels
    assert "C" not in with_clitics.c_syllable_patterns
    assert ps.c_syllable_patterns == {"CCCV": 1, "CCV": 5, "CCVC": 1, "CV": 11, "CVC": 5, "V": 2}
    assert ps.p_open_syllables == pytest.approx(19 / 25)
    assert ps.mean_syllable_len == pytest.approx(65 / 25)
    assert PhonStats("мама мыла раму").p_open_syllables == 1.0


def test_get_stats(ps):
    stats = ps.get_stats()
    assert isinstance(stats, dict)
    assert list(stats) == list(PHON_STATS_DESC)
    for key in PHON_STATS_DESC:
        assert stats[key] == pytest.approx(getattr(ps, key), nan_ok=True)


def test_print_stats(capsys, ps):
    ps.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == len(PHON_STATS_DESC) + 1
