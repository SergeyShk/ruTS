from math import e, isnan

import pytest
import spacy

from ruts import DiversityStats, WordsExtractor
from ruts.constants import DIVERSITY_STATS_DESC
from ruts.diversity_stats import (
    WindowStats,
    calc_dugast_k,
    calc_mattr,
    calc_msttr,
    calc_mtld,
    calc_mttr,
)
from ruts.exceptions import ParameterError, SourceError, SourceTypeError

TEXT = (
    "Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие"
    " черты: полнота значений словарного состава языка или какого-либо его сегмента;"
    " тематический, или идеографический способ упорядочения значений слов. Отличительной"
    " особенностью тезаурусов по сравнению с формальными онтологиями является выход в сферу"
    " лексических значений, установление связей не только между значениями и выражающими их"
    " словами, а также между самими значениями (регистрация различных семантических отношений"
    " внутри словаря)."
)
RIDDLE_TEXT = (
    "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
)
# 15 слов, 11 лексем, спектр частот {1: 8, 2: 2, 3: 1}
riddle = (
    "ног", "нет", "а", "хожу", "рта", "нет", "а", "скажу",
    "когда", "спать", "когда", "вставать", "когда", "работу", "начинать",
)  # fmt: skip


@pytest.fixture(scope="module")
def ds():
    return DiversityStats(TEXT)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"window_len": 0},
        {"mtld_threshold": 0},
        {"mtld_threshold": 1},
        {"mtld_min_len": -1},
        {"hdd_sample_size": 0},
        {"log_base": 1},
    ],
)
def test_init_params_error(kwargs):
    with pytest.raises(ParameterError):
        DiversityStats(TEXT, **kwargs)


def test_init_params():
    ds = DiversityStats(TEXT, window_len=20, mtld_threshold=0.9, mtld_min_len=5, log_base=e)
    assert ds.mattr == pytest.approx(calc_mattr(ds.words, 20))
    assert ds.msttr == pytest.approx(calc_msttr(ds.words, 20))
    assert ds.mtld == pytest.approx(calc_mtld(ds.words, 5, 0.9))
    assert ds.mttr == pytest.approx(calc_mttr(ds.words, e))
    assert ds.mttr != pytest.approx(calc_mttr(ds.words))
    assert ds.dugast_k == pytest.approx(calc_dugast_k(ds.words, e))


def test_init_value_error():
    with pytest.raises(SourceError):
        DiversityStats("+ _")


@pytest.mark.parametrize("text", [666, ["а", "б"], {"а": "б"}])
def test_init_type_error(text):
    with pytest.raises(SourceTypeError):
        DiversityStats(text)


def test_init_extractor_type_error():
    with pytest.raises(SourceTypeError):
        DiversityStats(TEXT, words_extractor="слова")


def test_init_doc_lowercase():
    doc = spacy.blank("ru")(RIDDLE_TEXT)
    assert DiversityStats(doc).words == DiversityStats(RIDDLE_TEXT).words == riddle
    assert DiversityStats(doc).ttr == DiversityStats(RIDDLE_TEXT).ttr


def test_init_doc_hyphens():
    """Дефисные слова Doc склеиваются, как в строке"""
    text = "Кто-то пришел, во-первых, по-видимому"
    assert DiversityStats(spacy.blank("ru")(text)).words == DiversityStats(text).words


def test_init_byte_order_mark():
    """Слова строки и ее Doc совпадают и с меткой порядка байтов"""
    text = "﻿" + RIDDLE_TEXT
    assert DiversityStats(text).words == DiversityStats(spacy.blank("ru")(text)).words == riddle


def test_init_extractor_lowercase():
    """Слова приводятся к нижнему регистру при любом экстракторе"""
    text = "Тезаурусы - особый класс. ТЕЗАУРУСЫ - Особый класс."
    default = DiversityStats(text)
    custom = DiversityStats(text, WordsExtractor())
    assert custom.words == default.words
    assert custom.ttr == default.ttr == pytest.approx(3 / 6)


def test_init_doc_with_extractor():
    """Переданный экстрактор применяется к тексту Doc, а не к его токенам"""
    doc = spacy.blank("ru")(RIDDLE_TEXT)
    extractor = WordsExtractor(stopwords=["а", "когда"])
    assert DiversityStats(doc, extractor).words == DiversityStats(RIDDLE_TEXT, extractor).words
    assert "а" not in DiversityStats(doc, extractor).words


def test_init_params_checked_first():
    with pytest.raises(ParameterError):
        DiversityStats("+ _", window_len=0)


def test_custom_words_extractor():
    extractor = WordsExtractor(lowercase=True, stopwords=["а", "когда"])
    ds = DiversityStats(RIDDLE_TEXT, words_extractor=extractor)
    assert ds.words == tuple(word for word in riddle if word not in ("а", "когда"))
    assert ds.ttr == pytest.approx(9 / 10)


def test_words(ds):
    assert len(ds.words) == 61
    assert ds.frequency_spectrum == {1: 52, 2: 3, 3: 1}


def test_values(ds):
    assert ds.ttr == pytest.approx(0.9180327868852459)
    assert ds.mattr == pytest.approx(0.9133333333333336)
    assert ds.msttr == pytest.approx(0.94)
    assert ds.mtld == pytest.approx(208.3760000000001)
    assert ds.heaps_beta == pytest.approx(0.9684000563407611)


def test_single_word_nan():
    ds = DiversityStats("слово")
    for stat in ("simpson_index", "inverse_simpson_index", "gini_simpson_index", "hapax_index"):
        assert isnan(getattr(ds, stat))


def test_windowed(ds):
    stats = ds.windowed("ttr", window_len=20)
    assert isinstance(stats, WindowStats)
    assert stats.n_windows == 3
    assert stats.mean == pytest.approx(0.95)
    assert ds.windowed("ttr", window_len=20, step=10).n_windows == 5


def test_get_stats(ds):
    stats = ds.get_stats()
    assert list(stats) == list(DIVERSITY_STATS_DESC)
    for key in DIVERSITY_STATS_DESC:
        assert stats[key] == pytest.approx(getattr(ds, key), nan_ok=True)


def test_print_stats(capsys, ds):
    ds.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == len(DIVERSITY_STATS_DESC) + 1
    assert "Метрика" in captured.out
    assert DIVERSITY_STATS_DESC["yule_k"] in captured.out
