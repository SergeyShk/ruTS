from math import e, inf, isnan, log, log2, log10, nan, sqrt

import pytest
import spacy

from ruts import DiversityStats
from ruts.constants import DIVERSITY_STATS_DESC
from ruts.diversity_stats import (
    WindowStats,
    calc_alpha2,
    calc_baayen_p,
    calc_brunet_w,
    calc_dugast_k,
    calc_entropy,
    calc_evenness,
    calc_frequency_spectrum,
    calc_gini_simpson_index,
    calc_hapax_index,
    calc_hapax_ratio,
    calc_hdd,
    calc_heaps_beta,
    calc_herdan_vm,
    calc_honore_r,
    calc_inverse_simpson_index,
    calc_mamtld,
    calc_mattr,
    calc_michea_m,
    calc_msttr,
    calc_mtld,
    calc_mtldw,
    calc_mttr,
    calc_perplexity,
    calc_sichel_s,
    calc_simpson_index,
    calc_sttr,
    calc_ttr,
    calc_windowed,
    calc_yule_i,
    calc_yule_k,
    calc_zipf_alpha,
)

text = "Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие черты: полнота\
        значений словарного состава языка или какого-либо его сегмента; тематический, или идеографический способ\
        упорядочения значений слов. Отличительной особенностью тезаурусов по сравнению с формальными онтологиями\
        является выход в сферу лексических значений, установление связей не только между значениями и выражающими их\
        словами, а также между самими значениями (регистрация различных семантических отношений внутри словаря)."
# 15 слов, 11 лексем, спектр частот {1: 8, 2: 2, 3: 1}
riddle = (
    "ног", "нет", "а", "хожу", "рта", "нет", "а", "скажу",
    "когда", "спать", "когда", "вставать", "когда", "работу", "начинать",
)  # fmt: skip


@pytest.fixture(scope="module")
def ds():
    return DiversityStats(text)


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
    with pytest.raises(ValueError):
        DiversityStats(text, **kwargs)


def test_init_params():
    ds = DiversityStats(text, window_len=20, mtld_threshold=0.9, mtld_min_len=5, log_base=e)
    assert ds.mattr == pytest.approx(calc_mattr(ds.words, 20))
    assert ds.msttr == pytest.approx(calc_msttr(ds.words, 20))
    assert ds.mtld == pytest.approx(calc_mtld(ds.words, 5, 0.9))
    assert ds.mttr == pytest.approx(calc_mttr(ds.words, e))
    assert ds.mttr != pytest.approx(calc_mttr(ds.words))
    assert ds.dugast_k == pytest.approx(calc_dugast_k(ds.words, e))


def test_init_value_error():
    text = "+ _"
    with pytest.raises(ValueError):
        DiversityStats(text)


@pytest.mark.parametrize("text", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(text):
    with pytest.raises(TypeError):
        DiversityStats(text)


def test_init_doc_lowercase():
    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать. Ног — это ноги"
    doc = spacy.blank("ru")(text)
    assert DiversityStats(doc).words == DiversityStats(text).words
    assert DiversityStats(doc).ttr == DiversityStats(text).ttr


def test_single_word_nan():
    ds = DiversityStats("слово")
    for stat in ("simpson_index", "inverse_simpson_index", "gini_simpson_index", "hapax_index"):
        assert isnan(getattr(ds, stat))


@pytest.mark.parametrize(
    "func",
    [calc_simpson_index, calc_inverse_simpson_index, calc_gini_simpson_index, calc_hapax_index],
)
def test_short_text_nan(func):
    assert isnan(func(["слово"]))
    assert isnan(func([]))


def test_ttr(ds):
    assert ds.ttr == pytest.approx(0.9180327868852459, rel=0.01)


def test_rttr(ds):
    assert ds.rttr == pytest.approx(7.170065276242175, rel=0.05)


def test_cttr(ds):
    assert ds.cttr == pytest.approx(5.070001778381037, rel=0.05)


def test_httr(ds):
    assert ds.httr == pytest.approx(0.9791961085978588, rel=0.01)


def test_sttr(ds):
    assert ds.sttr == pytest.approx(0.9637280435448702, rel=0.01)


def test_mttr(ds):
    assert ds.mttr == pytest.approx(0.011652687920277623, rel=0.005)


def test_dttr(ds):
    assert ds.dttr == pytest.approx(85.81710990988037, rel=0.1)


def test_mattr(ds):
    assert ds.mattr == pytest.approx(0.9133333333333336, rel=0.01)


def test_mattr_n_words():
    text = ["социалистическая", "революция"]
    assert calc_mattr(text, 50) == calc_ttr(text)


def test_msttr(ds):
    assert ds.msttr == pytest.approx(0.94, rel=0.01)


def test_msttr_n_words():
    text = ["социалистическая", "революция"]
    assert calc_msttr(text, 50) == calc_ttr(text)


def test_mtld(ds):
    assert ds.mtld == pytest.approx(208.3760000000001, rel=0.01)
    assert calc_mtld(riddle) == 15.0


def test_mtld_threshold():
    # прямой проход: фактор закрывается ровно на пороге (9 лексем на 13 словах),
    # обратный: порог не достигается, остается частичный фактор (11 лексем на 15 словах)
    threshold = 9 / 13
    backward = 15 / ((1 - 11 / 15) / (1 - threshold))
    assert calc_mtld(riddle, 10, threshold) == pytest.approx((15 + backward) / 2)
    assert calc_mtld(["а", "б", "в"]) == inf


def test_mtld_partial_factor():
    # незавершенный фактор учитывается частично
    words = ["а", "б", "в", "г", "а", "б", "в", "г", "а", "б", "в"]
    factors = 1 + (1 - 4 / 5) / (1 - 0.72)
    assert calc_mtld(words, 4, 0.72) == pytest.approx(len(words) / factors)


def test_mtld_partial_factor_clamp():
    # хвост короче минимальной длины с TTR ниже порога весит не больше одного фактора
    words = [*"абвгдежзик", "а", "а", "а", "а", "а", "б", "б", "б"]
    assert calc_mtld(words) == pytest.approx((18 / 2 + 18 / 1) / 2)


def test_mamtld(ds):
    assert isnan(ds.mamtld)
    assert calc_mamtld(riddle) == 12.0


def test_mtldw(ds):
    assert isnan(ds.mtldw)
    assert calc_mtldw(riddle) == 13.25
    assert calc_mtldw(riddle) != calc_mamtld(riddle)


def test_hdd(ds):
    assert ds.hdd == pytest.approx(0.9403815874780037, rel=0.01)


def test_hdd_n_words():
    text = ["социалистическая", "революция"]
    assert isnan(calc_hdd(text))


def test_hdd_zero_division_error(ds):
    text = ds.words
    assert calc_hdd(text, 0) == 0.0


def test_simpson_index(ds):
    assert ds.simpson_index == pytest.approx(0.003278688524590164, rel=0.01)


def test_simpson_index_unique_words():
    text = ["социалистическая", "революция"]
    assert calc_simpson_index(text) == 0.0


def test_inverse_simpson_index(ds):
    assert ds.inverse_simpson_index == pytest.approx(305.0, rel=0.01)


def test_inverse_simpson_index_unique_words():
    text = ["социалистическая", "революция"]
    assert calc_inverse_simpson_index(text) == inf


def test_gini_simpson_index(ds):
    assert ds.gini_simpson_index == pytest.approx(0.9967213114754099, rel=0.01)


def test_hapax_index(ds):
    assert ds.hapax_index == pytest.approx(5755.223409842638, rel=0.01)


def test_hapax_index_all_hapaxes():
    text = ["социалистическая", "революция"]
    assert calc_hapax_index(text) == inf


def test_honore_r(ds):
    assert ds.honore_r == ds.hapax_index
    assert calc_honore_r is calc_hapax_index


def test_frequency_spectrum(ds):
    assert calc_frequency_spectrum(riddle) == {1: 8, 2: 2, 3: 1}
    assert ds.frequency_spectrum == {1: 52, 2: 3, 3: 1}


def test_yule_k(ds):
    assert calc_yule_k(riddle) == pytest.approx(1e4 * (25 - 15) / 15**2)
    assert ds.yule_k == pytest.approx(32.249395323837675)
    assert isnan(calc_yule_k(["слово"]))


def test_yule_i(ds):
    assert calc_yule_i(riddle) == pytest.approx(11**2 / (25 - 11))
    assert calc_yule_i(["а", "б"]) == inf
    assert isnan(calc_yule_i(["слово"]))


def test_herdan_vm(ds):
    assert calc_herdan_vm(riddle) == pytest.approx(sqrt(25 / 15**2 - 1 / 11))
    assert calc_herdan_vm(["а", "б"]) == 0.0
    assert isnan(calc_herdan_vm(["слово"]))


def test_sichel_s_michea_m(ds):
    assert calc_sichel_s(riddle) == pytest.approx(2 / 11)
    assert calc_michea_m(riddle) == pytest.approx(11 / 2)
    assert calc_michea_m(["а", "б"]) == inf
    assert ds.sichel_s == pytest.approx(3 / 56)


def test_brunet_w(ds):
    assert calc_brunet_w(riddle) == pytest.approx(15 ** (11**-0.172))
    assert ds.brunet_w == pytest.approx(7.822893973715437)
    assert isnan(calc_brunet_w([]))


def test_dugast_k(ds):
    assert calc_dugast_k(riddle) == pytest.approx(log10(11) / log10(log10(15)))
    assert calc_dugast_k(riddle, e) == pytest.approx(log(11) / log(log(15)))
    assert isnan(calc_dugast_k(["а"] * 10))


def test_hapax_measures(ds):
    assert calc_baayen_p(riddle) == pytest.approx(8 / 15)
    assert calc_hapax_ratio(riddle) == pytest.approx(8 / 11)
    assert calc_alpha2(riddle) == pytest.approx(1 - 2 * 2 / 8)
    assert isnan(calc_alpha2(["а", "а"]))
    assert ds.baayen_p == pytest.approx(52 / 61)


def test_entropy(ds):
    expected = -(8 / 15 * log2(1 / 15) + 4 / 15 * log2(2 / 15) + 3 / 15 * log2(3 / 15))
    assert calc_entropy(riddle) == pytest.approx(expected)
    assert calc_perplexity(riddle) == pytest.approx(2**expected)
    assert calc_evenness(riddle) == pytest.approx(expected / log2(11))
    assert calc_entropy(["а", "а"]) == 0.0
    assert calc_perplexity(["а", "б", "в", "г"]) == pytest.approx(4.0)
    assert isnan(calc_evenness(["а", "а"]))
    assert ds.evenness == pytest.approx(0.9908861751368601)


def test_zipf_alpha(ds):
    # частоты 12, 6, 4, 3 на рангах 1-4 в точности следуют закону f = 12 / r
    words = ["а"] * 12 + ["б"] * 6 + ["в"] * 4 + ["г"] * 3
    assert calc_zipf_alpha(words) == pytest.approx(1.0)
    assert ds.zipf_alpha == pytest.approx(0.17143058908533987)
    assert isnan(calc_zipf_alpha(["слово"]))


def test_heaps_beta(ds):
    assert calc_heaps_beta(["а", "б", "в", "г"]) == pytest.approx(1.0)
    assert calc_heaps_beta(["а"] * 10) == pytest.approx(0.0)
    assert ds.heaps_beta == pytest.approx(0.9684000563407611)
    assert isnan(calc_heaps_beta(["слово"]))


def test_windowed(ds):
    stats = ds.windowed("ttr", window_len=20)
    assert isinstance(stats, WindowStats)
    assert stats.n_windows == 3
    assert stats.mean == pytest.approx(0.95)
    assert stats.lower < stats.mean < stats.upper
    assert ds.windowed("ttr", window_len=20, step=10).n_windows == 5
    assert ds.windowed("ttr", window_len=20, confidence=0.99).upper > stats.upper


def test_windowed_short_text():
    stats = calc_windowed(riddle, calc_ttr, window_len=100)
    assert stats == WindowStats(calc_ttr(riddle), nan, nan, nan, 1) or (
        stats.mean == calc_ttr(riddle) and stats.n_windows == 1 and isnan(stats.upper)
    )


def test_windowed_nan_windows():
    assert calc_windowed(riddle, calc_hdd, window_len=5) == WindowStats(nan, nan, nan, nan, 0)


def test_windowed_errors(ds):
    with pytest.raises(ValueError):
        ds.windowed("unknown")
    with pytest.raises(ValueError):
        calc_windowed(riddle, calc_ttr, window_len=0)
    with pytest.raises(ValueError):
        calc_windowed(riddle, calc_ttr, step=0)
    with pytest.raises(ValueError):
        calc_windowed(riddle, calc_ttr, confidence=1)


def test_sttr_base():
    assert calc_sttr(riddle, e) != pytest.approx(calc_sttr(riddle))
    assert calc_sttr(["а"], e) == 0


def test_get_stats(ds):
    stats = ds.get_stats()
    assert isinstance(stats, dict)
    for key in DIVERSITY_STATS_DESC:
        assert stats[key] == pytest.approx(getattr(ds, key), nan_ok=True)


def test_print_stats(capsys, ds):
    ds.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == len(DIVERSITY_STATS_DESC) + 1
