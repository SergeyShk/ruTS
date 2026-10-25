from math import isnan

import pytest
import spacy

from ruts import BasicStats, ReadabilityStats, UnadaptedReadabilityStats
from ruts.constants import UNADAPTED_READABILITY_STATS_DESC
from ruts.exceptions import SourceError, SourceTypeError
from ruts.unadapted_readability_stats import (
    calc_fucks,
    calc_gulpease,
    calc_strain_index,
    calc_wheeler_smith,
)

text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"


@pytest.fixture(scope="module")
def urs():
    return UnadaptedReadabilityStats(text)


def test_russian_syllables(urs):
    """Формулы считаются по русским слогам и буквам BasicStats ruTS"""
    bs = urs.bs
    assert isinstance(bs, BasicStats)
    assert urs.fucks == calc_fucks(bs.n_syllables, bs.n_sents)
    assert urs.strain_index == calc_strain_index(bs.n_syllables, bs.n_sents)
    assert urs.wheeler_smith == calc_wheeler_smith(bs.n_polysyllable_words, bs.n_sents)
    assert urs.gulpease == calc_gulpease(bs.n_letters, bs.n_words, bs.n_sents)


def test_sources(urs):
    """Строка, Doc и готовые основные статистики дают одни формулы"""
    stats = urs.get_stats()
    assert list(stats) == list(UNADAPTED_READABILITY_STATS_DESC)
    assert UnadaptedReadabilityStats(BasicStats(text)).get_stats() == stats
    assert UnadaptedReadabilityStats(spacy.blank("ru")(text)).get_stats() == stats


def test_no_scales_and_no_grade(urs):
    """Без калибровки под русский: ни прочтения, ни вклада в сводный класс"""
    assert all(urs.describe(stat) is None for stat in UNADAPTED_READABILITY_STATS_DESC)
    assert not set(UNADAPTED_READABILITY_STATS_DESC) & set(ReadabilityStats.grade_stats)


def test_print_stats(urs, capsys):
    urs.print_stats()
    out = capsys.readouterr().out
    assert out.splitlines()[0].split("|")[0].strip() == "Метрика"
    assert all(desc in out for desc in UNADAPTED_READABILITY_STATS_DESC.values())


def test_errors():
    with pytest.raises(SourceTypeError, match=r"^Источник данных не может быть типа int$"):
        UnadaptedReadabilityStats(5)
    with pytest.raises(SourceError, match=r"^В источнике данных отсутствуют слова$"):
        UnadaptedReadabilityStats("?!")
    stats = UnadaptedReadabilityStats("Кот.")
    assert not isnan(stats.forcast)
