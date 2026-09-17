from math import isnan, sqrt

import numpy as np
import pytest
from scipy.stats import mannwhitneyu

from ruts.corpus import (
    bootstrap_median_diff,
    calc_cliff_delta,
    calc_cohen_d,
    compare_corpora,
    corpus_features,
    holm_correction,
    sentence_rhythm,
    split_windows,
    text_features,
)
from ruts.corpus.compare import COMPARISON_COLUMNS, compare_values

text = "Кот сидел на окне. Он смотрел на птиц, а птицы улетели. Кот уснул. Завтра он снова будет сидеть на окне и смотреть на птиц."
short = [
    "Кот спал. Пёс ел. Дождь шёл. Кот встал. Пёс лёг. Дождь стих. Кот ушёл. Пёс спал.",
    "Ночь была. Свет горел. Кот сидел. Мышь бежала. Кот прыгнул. Мышь ушла. Кот ждал. Ночь шла.",
    "Утро настало. Птицы пели. Кот проснулся. Солнце встало. Роса блестела. Кот умылся.",
]
long = [
    "Когда за окном занимался долгий и туманный рассвет, старый кот медленно поднимался с продавленного кресла и подходил к холодному стеклу, за которым просыпался двор.",
    "Пёс, проживший в этом доме одиннадцать лет и знавший каждый его угол, каждую скрипучую половицу и каждый запах, лежал у порога и ждал, когда хозяин возьмёт поводок.",
    "Дождь, начавшийся ещё ночью, всё не кончался, и серые струи стекали по стёклам, по крышам, по листьям старой липы, под которой стояла забытая с лета скамейка.",
]


def test_split_windows():
    assert split_windows(text, 5) == [
        "Кот сидел на окне. Он",
        "смотрел на птиц, а птицы",
        "улетели. Кот уснул. Завтра он",
        "снова будет сидеть на окне",
        "и смотреть на птиц.",
    ]
    assert split_windows(text, None) == [text]
    assert split_windows(text, 100) == [text]
    assert split_windows(" \n" + text + "\n ", None) == [text]
    assert len(split_windows(text, 8)) == 3
    assert split_windows("Кто там?! Никого… Ушли!!!", None) == ["Кто там?! Никого… Ушли!!!"]
    assert split_windows("Кто там?! Никого… Ушли, все ушли!!! Вот так.", 3) == [
        "Кто там?! Никого…",
        "Ушли, все ушли!!!",
        "Вот так.",
    ]
    assert split_windows("", 5) == []
    assert split_windows("... !!!", 5) == []
    with pytest.raises(ValueError):
        split_windows(text, 0)


def test_text_features():
    features = text_features(text)
    prefixes = {key.split("_", 1)[0] for key in features}
    assert prefixes == {"basic", "readability", "diversity", "morph", "sents", "punct"}
    assert features["basic_words_per_sent"] == 6.0
    assert features["basic_letters_per_word"] == pytest.approx(4.0, rel=0.2)
    assert features["morph_pos_NOUN"] == pytest.approx(7 / 24)
    assert features["morph_pos_INTJ"] == 0.0
    assert features["morph_case_Voc"] == 0.0
    assert isnan(text_features("Кот, пёс, дом.")["morph_tense_Past"])
    assert sum(1 for key in features if key.startswith("morph_")) == 55
    assert features["morph_case_Nom"] + features["morph_case_Loc"] + features[
        "morph_case_Gen"
    ] == (pytest.approx(1.0))
    assert features["sents_mean"] == 6.0
    assert features["punct_period"] == pytest.approx(4 / 24 * 1000)
    assert features["punct_yo_share"] == 0.0
    assert all(isinstance(value, float) for value in features.values())
    with pytest.raises(ValueError):
        text_features("...")


def test_sentence_rhythm():
    rhythm = sentence_rhythm([4, 8, 2, 7])
    assert rhythm["sents_mean"] == 5.25
    assert rhythm["sents_std"] == pytest.approx(np.std([4, 8, 2, 7], ddof=1))
    assert rhythm["sents_cv"] == pytest.approx(rhythm["sents_std"] / 5.25)
    centered = np.array([4, 8, 2, 7]) - 5.25
    assert rhythm["sents_autocorr"] == pytest.approx(
        (centered[:-1] * centered[1:]).sum() / (centered**2).sum()
    )
    assert sentence_rhythm([5, 5, 5])["sents_std"] == 0
    assert isnan(sentence_rhythm([5, 5, 5])["sents_autocorr"])
    assert isnan(sentence_rhythm([3])["sents_std"])
    assert isnan(sentence_rhythm([3, 4])["sents_autocorr"])
    assert all(isnan(value) for value in sentence_rhythm([]).values())


def test_corpus_features():
    table = corpus_features([text, "Кот спал."], window=8)
    assert table.index.names == ["text", "window"]
    assert list(table.index) == [(0, 0), (0, 1), (0, 2), (1, 0)]
    assert "morph_pos_NOUN" in table.columns
    assert table.dtypes.eq(float).all()
    custom = corpus_features([text], window=None, features=lambda t: {"length": len(t)})
    assert custom.loc[(0, 0), "length"] == len(text)
    assert corpus_features([text, "..."], window=None).shape[0] == 1
    with pytest.raises(ValueError):
        corpus_features(["...", ""])


def test_compare_corpora():
    result = compare_corpora(
        short, long, window=None, labels=("короткие", "длинные"), n_bootstrap=200
    )
    columns = [
        column.replace("_a", "_короткие").replace("_b", "_длинные")
        for column in COMPARISON_COLUMNS
    ]
    assert list(result.columns) == columns
    row = result.loc["sents_mean"]
    assert row["mean_короткие"] < row["mean_длинные"]
    assert row["cliff_delta"] == -1.0
    assert row["auc"] == 0.0
    assert (
        row["ci_high"] <= row["median_diff"] <= row["ci_low"]
        or row["ci_low"] <= row["median_diff"] <= row["ci_high"]
    )
    assert row["n_короткие"] == 3 and row["n_длинные"] == 3
    assert result["n_короткие"].dtype.kind == "i"
    assert result["cliff_delta"].abs().dropna().is_monotonic_decreasing
    assert (result["p_holm"].dropna() >= result["p_value"].dropna()).all()
    assert (
        result.index[0] in {"sents_mean", "basic_words_per_sent"}
        or abs(result.iloc[0]["cliff_delta"]) == 1.0
    )
    assert result["cliff_delta"].isna().sum() == result["u"].isna().sum()
    assert result.loc["diversity_michea_m", "n_длинные"] == 2
    assert np.isfinite(result.drop(columns=["p_holm"]).dropna()).all().all()
    undefined = result[result["cliff_delta"].isna()]
    assert list(undefined.index) == list(result.index[-len(undefined) :])


def test_compare_corpora_rare_values():
    a = ["Ах, кот спал. Ох, пёс ел. Эх, дождь шёл. Кот встал."] * 3
    b = ["Кот спал. Пёс ел. Дождь шёл. Кот встал. Пёс лёг."] * 3
    row = compare_corpora(a, b, window=None, n_bootstrap=10).loc["morph_pos_INTJ"]
    assert row["mean_A"] == pytest.approx(3 / 11)
    assert row["mean_B"] == 0.0
    assert row["cliff_delta"] == 1.0
    assert (row["n_A"], row["n_B"]) == (3, 3)


def test_compare_corpora_options():
    lengths = lambda t: {"length": float(len(t)), "constant": 1.0}  # noqa: E731
    result = compare_corpora(short, long, window=None, features=lengths, n_bootstrap=50, seed=1)
    assert list(result.index) == ["length", "constant"]
    assert result.loc["length", "cliff_delta"] == -1.0
    assert isnan(result.loc["constant", "cohen_d"])
    assert result.loc["constant", "cliff_delta"] == 0.0
    repeated = compare_corpora(short, long, window=None, features=lengths, n_bootstrap=50, seed=1)
    assert result.equals(repeated)
    windowed = compare_corpora(short, long, window=5, features=lengths, n_bootstrap=50)
    assert windowed.loc["length", "n_A"] > 3
    with pytest.raises(ValueError):
        compare_corpora(short, long, features=lengths, n_bootstrap=0)
    with pytest.raises(ValueError):
        compare_corpora(["..."], long, features=lengths)
    single = compare_corpora(short[:1], long, window=None, features=lengths, n_bootstrap=50)
    assert isnan(single.loc["length", "cliff_delta"])
    assert (single.loc["length", "n_A"], single.loc["length", "n_B"]) == (1, 3)


def test_compare_values():
    a = np.array([1.0, 2.0, 3.0, 4.0])
    b = np.array([3.0, 4.0, 5.0, 6.0])
    values = compare_values(a, b, n_bootstrap=100, rng=np.random.default_rng(0))
    assert len(values) == len(COMPARISON_COLUMNS)
    assert values[:5] == (2.5, 4.5, 2.5, 4.5, -2.0)
    assert values[8] == pytest.approx(calc_cliff_delta(a, b))
    assert values[9] == pytest.approx(mannwhitneyu(a, b)[0] / 16)
    assert values[11] == pytest.approx(mannwhitneyu(a, b, alternative="two-sided")[1])
    assert isnan(values[12])
    assert values[13:] == (4, 4)
    assert all(isnan(value) for value in compare_values(np.array([1.0]), b)[:13])
    assert compare_values(np.array([1.0]), b)[13:] == (1, 4)


def test_effect_sizes():
    a = [2.0, 4.0, 6.0, 8.0]
    b = [1.0, 3.0, 5.0, 7.0]
    assert calc_cohen_d(a, b) == pytest.approx(1 / sqrt(20 / 3))
    assert isnan(calc_cohen_d([1.0, 1.0], [1.0, 1.0]))
    assert isnan(calc_cohen_d([1.0], [2.0, 3.0]))
    assert calc_cliff_delta(a, b) == pytest.approx((10 - 6) / 16)
    assert calc_cliff_delta([1, 1], [1, 1]) == 0.0
    assert calc_cliff_delta([5, 6], [1, 2]) == 1.0
    assert isnan(calc_cliff_delta([], [1.0]))
    low, high = bootstrap_median_diff(a, b, n_bootstrap=500, rng=np.random.default_rng(0))
    assert low <= 1.0 <= high
    assert bootstrap_median_diff([3.0, 3.0, 3.0], [1.0, 1.0, 1.0], n_bootstrap=10) == (2.0, 2.0)
    assert all(isnan(value) for value in bootstrap_median_diff([], [1.0]))
    assert bootstrap_median_diff(a, b, n_bootstrap=20) != (float("nan"), float("nan"))


def test_holm_correction():
    adjusted = holm_correction([0.01, 0.04, 0.03, float("nan")])
    assert adjusted[:3] == pytest.approx([0.03, 0.06, 0.06])
    assert isnan(adjusted[3])
    assert list(holm_correction([0.5, 0.9])) == [1.0, 1.0]
    assert list(holm_correction([])) == []
    assert all(isnan(value) for value in holm_correction([float("nan")]))
