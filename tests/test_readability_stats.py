import pytest

from ruts import ReadabilityStats, SentsExtractor
from ruts.constants import (
    READABILITY_GRADE_STATS,
    READABILITY_PRESETS,
    READABILITY_STATS_DESC,
    SIS_GRADE_STAGES,
)
from ruts.readability_stats import (
    calc_consensus_grade,
    calc_dale_chall_index,
    calc_flesch_kincaid_grade,
    calc_gunning_fog_index,
    calc_matskovsky_index,
    calc_reading_time,
    calc_rix,
    calc_sis_grade,
    flesch_reading_easy_to_grade,
    grade_to_age,
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
    with pytest.raises(ValueError, match="предложения"):
        ReadabilityStats("Текст один. Текст два.", sents_extractor=SentsExtractor(min_len=1000))


def test_init_preset_error():
    with pytest.raises(ValueError):
        ReadabilityStats(text, preset="unknown")


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


def test_calc_consensus_grade():
    assert calc_consensus_grade([-2.06, 1.17, 0.05, 0.29, 1.52, 4.1, 6.0], 87.17) == 1.5
    assert calc_consensus_grade([2.5, 2.5, 3.4]) == 3.0
    assert calc_consensus_grade([7.0]) == 7.0
    assert calc_consensus_grade([], 65) == 8.5
    assert calc_consensus_grade([8, 8, 9, 9], 65) == 8.5
    assert calc_consensus_grade([8.5]) == 9.0
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
        (55, 10),
        (45, 11),
        (30, 12),
        (29.9, 13),
        (-50, 13),
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
