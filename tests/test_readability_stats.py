import re
from math import isnan
from pathlib import Path

import anyts.basic_stats
import anyts.constants
import pytest
import spacy

from ruts import BasicStats, ReadabilityStats, SentsExtractor, WordsExtractor
from ruts.constants import (
    LEVEL_NORM_BANDS,
    LEVEL_NORMS,
    LEVEL_NORMS_DESC,
    LIX_LEVELS,
    READABILITY_GRADE_STATS,
    READABILITY_LEVEL_SCALES,
    READABILITY_PRESETS,
    READABILITY_STATS_DESC,
    READING_EASE_GRADES,
    READING_EASE_LEVELS,
    RIX_LEVELS,
    SIS_GRADE_FREQ_STAGES,
    SIS_GRADE_STAGES,
)
from ruts.exceptions import ParameterError, SourceTypeError, UnknownStatError
from ruts.readability_stats import (
    calc_automated_readability_index,
    calc_coleman_liau_index,
    calc_consensus_grade,
    calc_dale_chall_index,
    calc_flesch_kincaid_grade,
    calc_flesch_reading_easy,
    calc_gunning_fog_index,
    calc_matskovsky_index,
    calc_reading_time,
    calc_rix,
    calc_sis_grade,
    calc_sis_grade_freq,
    calc_smog_index,
    describe_level_norm,
    flesch_reading_easy_to_grade,
    grade_to_age,
    level_features,
    level_norms,
    scale_level,
)

text = "Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие черты: полнота\
        значений словарного состава языка или какого-либо его сегмента; тематический, или идеографический способ\
        упорядочения значений слов. Отличительной особенностью тезаурусов по сравнению с формальными онтологиями\
        является выход в сферу лексических значений, установление связей не только между значениями и выражающими их\
        словами, а также между самими значениями (регистрация различных семантических отношений внутри словаря)."


@pytest.fixture(scope="module")
def rs():
    return ReadabilityStats(text)


def test_init_value_error():
    text = "+ _"
    with pytest.raises(ValueError):
        ReadabilityStats(text)


@pytest.mark.parametrize("text", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(text):
    with pytest.raises(TypeError):
        ReadabilityStats(text)


def test_init_no_sents_error():
    with pytest.raises(ValueError, match="отсутствуют предложения"):
        ReadabilityStats("Текст один. Текст два.", sents_extractor=SentsExtractor(min_len=1000))


def test_basic_stats_of_another_library():
    class Foreign(anyts.basic_stats.BasicStats):
        def count_syllables(self, word):
            return 1

    with pytest.raises(SourceTypeError, match=r"^Базовые статистики должны быть объектом"):
        ReadabilityStats(Foreign("The cat sleeps."))


@pytest.mark.parametrize("preset", ["unknown", None, ["plainrussian"]])
def test_init_preset_error(preset):
    with pytest.raises(ValueError, match=r"^(Неизвестный пресет коэффициентов|Пресет должен)"):
        ReadabilityStats(text, preset=preset)


def test_init_foreign_basic_stats():
    """Базовые статистики ядра без слогов ruTS не принимаются"""

    class CoreBasicStats(anyts.basic_stats.BasicStats):
        def count_syllables(self, word):
            return 1

    with pytest.raises(TypeError):
        ReadabilityStats(CoreBasicStats(text))


def test_init_basic_stats(rs):
    basic = BasicStats(text)
    from_basic = ReadabilityStats(basic, preset="fiction")
    assert from_basic.bs is basic
    assert from_basic.preset == "fiction"
    assert ReadabilityStats(basic).get_stats() == rs.get_stats()


def test_default_preset(rs):
    assert rs.preset == "plainrussian"
    assert rs.coefficients == READABILITY_PRESETS["plainrussian"]


def test_coefficients_copy():
    rs = ReadabilityStats(text)
    rs.coefficients["flesch_kincaid_grade"] = (0.5, 8.4, 15.59)
    assert rs.flesch_kincaid_grade == pytest.approx(26.925573770491805, rel=0.01)
    assert READABILITY_PRESETS["plainrussian"]["flesch_kincaid_grade"] == (0.318, 14.2, 30.5)
    assert ReadabilityStats(text).flesch_kincaid_grade == pytest.approx(
        25.29080327868852, rel=0.01
    )


@pytest.mark.parametrize(
    ("preset", "flesch_kincaid_grade", "flesch_reading_easy"),
    [
        ("plainrussian", 25.29080327868852, -27.893688524590175),
        ("fiction", 26.925573770491805, -27.893688524590175),
        ("academic", 17.706393442622954, -50.96203278688523),
    ],
)
def test_presets(preset, flesch_kincaid_grade, flesch_reading_easy):
    rs = ReadabilityStats(text, preset=preset)
    assert rs.flesch_kincaid_grade == pytest.approx(flesch_kincaid_grade, rel=0.01)
    assert rs.flesch_reading_easy == pytest.approx(flesch_reading_easy, rel=0.01)
    assert rs.coleman_liau_index == pytest.approx(19.276557377049187, rel=0.01)
    assert rs.smog_index == pytest.approx(25.826171166408717, rel=0.01)
    assert rs.automated_readability_index == pytest.approx(23.900823770491805, rel=0.01)


def test_flesch_kincaid_grade(rs):
    assert rs.flesch_kincaid_grade == pytest.approx(25.29080327868852, rel=0.1)


def test_flesch_kincaid_grade_coefficients():
    assert calc_flesch_kincaid_grade(25, 15, 1) == pytest.approx(-2.0633333333333326)
    assert calc_flesch_kincaid_grade(25, 15, 1, 0.5, 8.4, 15.59) == pytest.approx(5.91)


def test_flesch_reading_easy(rs):
    assert rs.flesch_reading_easy == pytest.approx(-27.893688524590175, rel=0.1)


def test_coleman_liau_index(rs):
    assert rs.coleman_liau_index == pytest.approx(19.276557377049187, rel=0.1)


def test_smog_index(rs):
    assert rs.smog_index == pytest.approx(25.826171166408717, rel=0.1)


def test_automated_readability_index(rs):
    assert rs.automated_readability_index == pytest.approx(23.900823770491805, rel=0.1)


def test_lix(rs):
    assert rs.lix == pytest.approx(87.87704918032787, rel=0.1)


def test_rix(rs):
    assert rs.rix == pytest.approx(17.5, rel=0.1)
    assert calc_rix(2, 1) == 2.0


def test_sis_grade(rs):
    assert rs.sis_grade == pytest.approx(17.73409836065574, rel=0.01)
    assert calc_sis_grade(65, 15, 1) == pytest.approx(1.5166666666666675)


@pytest.mark.parametrize(
    ("stage", "expected"),
    [("2-4", 7.115), ("5-7", 10.739180327868853), ("8-11", 13.14827868852459)],
)
def test_sis_grade_by_stage(rs, stage, expected):
    assert rs.sis_grade_by_stage(stage) == pytest.approx(expected, rel=0.01)
    assert rs.sis_grade_by_stage(stage) == pytest.approx(
        calc_sis_grade(rs.bs.n_letters, rs.bs.n_words, rs.bs.n_sents, *SIS_GRADE_STAGES[stage])
    )


def test_sis_grade_by_freq(rs):
    assert calc_sis_grade_freq(65, 15, 1, 500) == pytest.approx(
        -14.46 + 0.58 * 15 + 2.15 * 65 / 15 - 1.3
    )
    assert rs.sis_grade_by_freq(500) == pytest.approx(
        calc_sis_grade_freq(rs.bs.n_letters, rs.bs.n_words, rs.bs.n_sents, 500)
    )
    assert rs.sis_grade_by_freq(0) > rs.sis_grade_by_freq(1000)
    for stage, coefficients in SIS_GRADE_FREQ_STAGES.items():
        assert rs.sis_grade_by_freq(500, stage) == pytest.approx(
            calc_sis_grade_freq(rs.bs.n_letters, rs.bs.n_words, rs.bs.n_sents, 500, *coefficients)
        )
    assert rs.sis_grade_by_freq(500, "2-4") != rs.sis_grade_by_freq(500)
    with pytest.raises(ValueError):
        rs.sis_grade_by_freq(500, "12")
    # nan - нет знаменательных слов в словаре
    assert isnan(rs.sis_grade_by_freq(float("nan")))


@pytest.mark.parametrize("mean_ipm", [-1, float("inf"), "100", True, None])
def test_sis_grade_by_freq_value(rs, mean_ipm):
    with pytest.raises(ParameterError, match=r"^Частотность должна быть"):
        rs.sis_grade_by_freq(mean_ipm)


def test_sis_grade_counted_letters():
    rs = ReadabilityStats(text, words_extractor=WordsExtractor(stopwords=["и", "в", "для", "к"]))
    letters = sum(n_letters * count for n_letters, count in rs.bs.c_letters.items())
    assert letters < rs.bs.n_letters
    assert rs.sis_grade == calc_sis_grade(letters, rs.bs.n_words, rs.bs.n_sents)
    assert rs.sis_grade_by_stage("5-7") == calc_sis_grade(
        letters, rs.bs.n_words, rs.bs.n_sents, *SIS_GRADE_STAGES["5-7"]
    )
    assert rs.sis_grade_by_freq(300) == calc_sis_grade_freq(
        letters, rs.bs.n_words, rs.bs.n_sents, 300
    )


def test_sis_grade_by_stage_error(rs):
    with pytest.raises(ValueError):
        rs.sis_grade_by_stage("12")


def test_matskovsky_index(rs):
    assert rs.matskovsky_index == pytest.approx(23.80034426229508, rel=0.01)
    assert calc_matskovsky_index(0, 15, 1) == pytest.approx(9.351)
    assert calc_matskovsky_index(5, 10, 2) == pytest.approx(0.62 * 5 + 0.123 * 50 + 0.051)


def test_dale_chall_index(rs):
    assert rs.dale_chall_index == pytest.approx(23.710106557377053, rel=0.01)
    assert calc_dale_chall_index(0, 15, 1) == pytest.approx(4.095)
    assert calc_dale_chall_index(5, 10, 2) == pytest.approx(0.552 * 50 + 0.273 * 5)


def test_gunning_fog_index(rs):
    assert rs.gunning_fog_index == pytest.approx(23.34754098360656, rel=0.01)
    assert calc_gunning_fog_index(0, 15, 1) == pytest.approx(6.0)
    assert calc_gunning_fog_index(5, 10, 2) == pytest.approx(0.4 * (5 + 50))


def test_consensus_grade(rs):
    assert rs.consensus_grade == 23.5
    grades = [getattr(rs, stat) for stat in READABILITY_GRADE_STATS]
    assert rs.consensus_grade == calc_consensus_grade(grades, rs.flesch_reading_easy)


def test_scale_level():
    flesch = calc_flesch_reading_easy(n_syllables=60, n_words=30, n_sents=2)
    assert scale_level(flesch, READING_EASE_LEVELS) == "8-й и 9-й класс"
    assert scale_level(109.4, READING_EASE_LEVELS) == "5-й класс"
    assert scale_level(-27.9, READING_EASE_LEVELS) == "выпускник университета"
    with pytest.raises(ValueError):
        scale_level(float("nan"), LIX_LEVELS)


FUNCS_PAGE = Path(__file__).parent.parent / "docs" / "stats" / "readability_stats_funcs.md"


def doc_scale(heading, after=""):
    """
    Шкала из таблицы раздела страницы функций: нижние границы по убыванию и подписи;
    after - текст, после которого начинается таблица шкалы
    """
    page = FUNCS_PAGE.read_text(encoding="utf-8")
    section = page.split(f"## {heading}\n", 1)[1].split("\n## ", 1)[0]
    if after:
        section = section.split(after, 1)[1]
    rows = re.findall(
        r"^\|\s*`(?:([\d.]+)-([\d.]+)|> ([\d.]+))`\s*\|\s*([^|]+?)\s*\|$", section, re.MULTILINE
    )
    return tuple(
        sorted(
            (
                (float(above) if above else min(float(a), float(b)), label.lower())
                for a, b, above, label in rows
            ),
            reverse=True,
        )
    )


@pytest.mark.parametrize(
    ("heading", "scale", "after"),
    [
        ("Индекс удобочитаемости Флеша", READING_EASE_LEVELS, ""),
        ("Индекс удобочитаемости LIX", LIX_LEVELS, ""),
        ("Индекс удобочитаемости RIX", RIX_LEVELS, "RIX_LEVELS"),
        (
            "Перевод индекса Флеша в класс { #flesch_reading_easy_to_grade }",
            READING_EASE_GRADES,
            "READING_EASE_GRADES",
        ),
    ],
)
def test_level_scales_follow_docs(heading, scale, after):
    """Шкалы прочтения и перевода в класс совпадают с таблицами документации"""
    assert tuple((bound, str(label)) for bound, label in scale) == doc_scale(heading, after)


def test_calc_consensus_grade():
    assert calc_consensus_grade([-2.06, 1.17, 0.05, 0.29, 1.52, 4.1, 6.0], 87.17) == 1.5
    assert calc_consensus_grade([2.5, 2.5, 3.4]) == 3.0
    assert calc_consensus_grade([7.0]) == 7.0
    assert calc_consensus_grade([], 65) == 8.5
    assert calc_consensus_grade([8, 8, 9, 9], 65) == 8.5
    assert calc_consensus_grade([8.5]) == 9.0
    assert calc_consensus_grade([12, 14], 45) == 14.0
    with pytest.raises(ValueError):
        calc_consensus_grade([])


@pytest.mark.parametrize(
    ("flesch_reading_easy", "grade"),
    [
        (120, 5),
        (90, 5),
        (89.9, 6),
        (75, 7),
        (65, 8.5),
        (55, 10.5),
        (45, 14),
        (30, 14),
        (29.9, 17),
        (-50, 17),
    ],
)
def test_flesch_reading_easy_to_grade(flesch_reading_easy, grade):
    assert flesch_reading_easy_to_grade(flesch_reading_easy) == grade


@pytest.mark.parametrize(
    ("grade", "expected"),
    [
        (-3, "1-3-й класс (6-8 лет)"),
        (0.4, "1-3-й класс (6-8 лет)"),
        (3.5, "4-6-й класс (9-11 лет)"),
        (6.49, "4-6-й класс (9-11 лет)"),
        (8, "7-9-й класс (12-14 лет)"),
        (9.5, "10-11-й класс (15-16 лет)"),
        (14, "1-3-й курс вуза (17-19 лет)"),
        (17.4, "4-6-й курс вуза (20-22 года)"),
        (17.5, "аспирантура (старше 22 лет)"),
        (40, "аспирантура (старше 22 лет)"),
    ],
)
def test_grade_to_age(grade, expected):
    assert grade_to_age(grade) == expected


def test_describe_grade(rs):
    assert rs.describe_grade() == grade_to_age(rs.consensus_grade)
    assert rs.describe_grade("smog_index") == grade_to_age(rs.smog_index)
    assert ReadabilityStats("Мама мыла раму").describe_grade() == "1-3-й класс (6-8 лет)"
    with pytest.raises(ValueError):
        rs.describe_grade("lix")


def test_describe(rs):
    """Шкалы индекса Флеша, LIX и RIX русские"""
    assert ReadabilityStats.level_scales is READABILITY_LEVEL_SCALES
    assert [label for _, label in READING_EASE_LEVELS][-2:] == [
        "университет",
        "выпускник университета",
    ]
    # индекс Флеша текста ниже нуля, LIX выше 60, RIX выше 7.2
    assert rs.describe("flesch_reading_easy") == rs.describe_level() == "выпускник университета"
    assert rs.describe("lix") == LIX_LEVELS[0][1]
    assert rs.describe("rix") == rs.describe_level("rix") == "университет и выше"
    assert rs.describe("consensus_grade") == rs.describe_grade()
    assert rs.describe("matskovsky_index") is None
    riddle = ReadabilityStats("Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать")
    assert riddle.describe("flesch_reading_easy") == "5-й класс"
    assert riddle.describe("lix") == "очень простые тексты, детские книги"
    assert riddle.describe("rix") == "4-й класс"


@pytest.mark.parametrize(
    ("rix", "level"),
    [(7.2, "университет и выше"), (7.1, "11-й класс"), (5.3, "11-й класс"), (5.2, "10-й класс")],
)
def test_describe_rix_above_school(rix, level):
    """RIX от 7.2 читается выше школы, а 6.2-7.2 - выпускным классом, а не одной полосой"""
    assert scale_level(rix, RIX_LEVELS) == level
    # перевод в годы обучения ядра остается для потребителей, читающих grade_scales
    assert ReadabilityStats.grade_scales["rix"] is anyts.constants.RIX_GRADES


def test_reading_ease_grades_follow_levels():
    """Индекс Флеша в сводном классе переводится по полосам той же шкалы, что и в describe"""
    assert ReadabilityStats.reading_ease_grades is READING_EASE_GRADES
    assert [bound for bound, _ in READING_EASE_GRADES] == [
        bound for bound, _ in READING_EASE_LEVELS
    ]
    rs = ReadabilityStats("Мама мыла раму")
    assert rs.reading_ease_to_grade(45) == flesch_reading_easy_to_grade(45) == 14
    assert scale_level(45, READING_EASE_LEVELS) == "университет"
    assert grade_to_age(14) == "1-3-й курс вуза (17-19 лет)"


def test_reading_time(rs):
    assert rs.reading_time == pytest.approx(61 / 180)
    assert calc_reading_time(180, 60) == 3.0
    with pytest.raises(ValueError):
        calc_reading_time(100, 0)


def test_reading_time_by_speed(rs):
    assert rs.reading_time_by_speed(180) == rs.reading_time
    assert rs.reading_time_by_speed(61) == 1.0
    with pytest.raises(ValueError):
        rs.reading_time_by_speed(-1)


@pytest.mark.parametrize(
    "formula",
    [
        lambda: calc_flesch_kincaid_grade(0, 0, 0),
        lambda: calc_flesch_reading_easy(5, 3, 0),
        lambda: calc_coleman_liau_index(0, 0, 0),
        lambda: calc_smog_index(5, 0),
        lambda: calc_automated_readability_index(5, 0, 2),
        lambda: calc_sis_grade(5, 3, 0),
        lambda: calc_sis_grade_freq(0, 0, 2, 300),
        lambda: calc_matskovsky_index(0, 3, 0),
        lambda: calc_dale_chall_index(0, 0, 2),
    ],
)
def test_formulas_without_words_or_sents(formula):
    assert isnan(formula())


def test_unknown_stage(rs):
    with pytest.raises(ValueError):
        rs.sis_grade_by_stage(["2-4"])
    with pytest.raises(ValueError):
        rs.sis_grade_by_freq(300, "1-3")


def test_reading_time_by_norm(rs):
    fast, slow = rs.reading_time_by_norm("grade_1")
    assert (fast, slow) == (pytest.approx(61 / 40), pytest.approx(61 / 25))
    assert rs.reading_time_by_norm("adult_silent")[0] == rs.reading_time
    with pytest.raises(ValueError):
        rs.reading_time_by_norm("grade_12")


def test_get_stats(rs):
    stats = rs.get_stats()
    assert isinstance(stats, dict)
    assert list(stats) == list(READABILITY_STATS_DESC)
    for key in READABILITY_STATS_DESC:
        assert stats[key] == getattr(rs, key)


def test_print_stats(capsys, rs):
    rs.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == len(READABILITY_STATS_DESC) + 1


@pytest.mark.parametrize(
    ("grade", "stage"),
    [
        (0.2, 1),
        (1, 1),
        (3.4, 1),
        (3.5, 4),
        (6, 4),
        (7, None),
        (9.4, None),
        (9.5, 10),
        (11, 10),
        (11.5, None),
        (25, None),
    ],
)
def test_level_norms(grade, stage):
    """Нормы ступени, к которой класс относится по таблице grade_to_age"""
    assert level_norms(grade) == (None if stage is None else LEVEL_NORMS[stage])


def test_level_norms_data():
    """Нормы - квартили: нижний не выше верхнего, признаки - ключи LEVEL_NORMS_DESC"""
    for norms in LEVEL_NORMS.values():
        assert set(norms) == set(LEVEL_NORMS_DESC)
        assert all(low <= high for low, high in norms.values())
    for grade in (float("nan"), float("inf"), "3", True):
        with pytest.raises(ParameterError, match="Класс должен быть конечным числом"):
            level_norms(grade)
    norms = level_norms(2)
    norms["words_per_sent"] = (1, 2)
    assert level_norms(2)["words_per_sent"] == LEVEL_NORMS[1]["words_per_sent"] == (8.1, 10.7)


def test_describe_level_norm():
    below, within, above = LEVEL_NORM_BANDS
    assert describe_level_norm("words_per_sent", 6.0, 2) == below
    assert describe_level_norm("words_per_sent", 8.1, 2) == within
    assert describe_level_norm("words_per_sent", 10.7, 2) == within
    assert describe_level_norm("words_per_sent", 11, 2) == above
    assert describe_level_norm("mtld", float("inf"), 10) == above
    assert describe_level_norm("mtld", float("nan"), 10) is None
    assert describe_level_norm("words_per_sent", 12, 8) is None
    for grade in (2, 8):
        with pytest.raises(UnknownStatError, match="n_words отсутствует"):
            describe_level_norm("n_words", 12, grade)
    with pytest.raises(ValueError):
        describe_level_norm("words_per_sent", "12", 2)
    with pytest.raises(ValueError):
        describe_level_norm("words_per_sent", True, 2)


def test_level_features():
    """Признаки норм считаются по тем же словам и предложениям, что формулы класса"""
    features = level_features("Ног нет, а хожу. Рта нет, а скажу: когда спать, когда вставать.")
    assert set(features) == set(LEVEL_NORMS_DESC)
    assert features["words_per_sent"] == 6.0
    assert features["letters_per_word"] == pytest.approx(46 / 12)
    assert features["p_smog_complex_words"] == 0.0
    bs = BasicStats("Здравоохранение и благоустройство. Кот спит.")
    features = level_features("Здравоохранение и благоустройство. Кот спит.")
    assert features["p_smog_complex_words"] == pytest.approx(2 / bs.n_words)


def test_level_features_of_doc():
    """Признаки Doc - по его тексту, как нормы, а не по границам предложений spaCy"""
    nlp = spacy.blank("ru")
    nlp.add_pipe("sentencizer")
    text = "Кот, т. е. зверь, спит на окне. Пёс лает во дворе."
    doc = nlp(text)
    assert BasicStats(doc).n_sents != BasicStats(text).n_sents
    assert level_features(doc) == level_features(text)
