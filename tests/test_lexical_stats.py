from math import isnan, log2, log10

import pytest
import spacy

from ruts import LexicalStats, WordsExtractor
from ruts.constants import FREQUENCY_BANDS, LEXICAL_STATS_DESC
from ruts.datasets import FreqDict
from ruts.lexical_stats import calc_surprisal, get_rank, is_number, load_top_lemmas
from tests.datasets.test_freq2011 import write_dict

text = "Кот сидел на окне и смотрел на птиц"
# леммы: кот, сидеть, на, окно, и, смотреть, на, птица; знаменательные: кот, сидеть, окно, смотреть, птица
IPM = {"кот": 40.3, "сидеть": 200.0, "на": 30000.0, "окно": 100.0, "и": 35000.0, "птица": 50.0}
RANGE = {"кот": 98, "сидеть": 100, "на": 100, "окно": 90, "и": 100, "птица": 80}
DISPERSION = {"кот": 90, "сидеть": 95, "на": 98, "окно": 80, "и": 98, "птица": 70}
FOUND = ["кот", "сидеть", "на", "окно", "и", "на", "птица"]
CONTENT_FOUND = ["кот", "сидеть", "окно", "птица"]


@pytest.fixture(scope="module")
def freq_dict(tmp_path_factory):
    path = tmp_path_factory.mktemp("dicts")
    write_dict(path)
    return FreqDict(data_dir=path)


@pytest.fixture(scope="module")
def ls(freq_dict):
    return LexicalStats(text, freq_dict=freq_dict)


@pytest.fixture(scope="module")
def nlp():
    pytest.importorskip("ru_core_news_sm")
    return spacy.load("ru_core_news_sm")


def test_init_value_error(freq_dict):
    with pytest.raises(ValueError):
        LexicalStats("+ _", freq_dict=freq_dict)


@pytest.mark.parametrize("source", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(source, freq_dict):
    with pytest.raises(TypeError):
        LexicalStats(source, freq_dict=freq_dict)


def test_words_and_lemmas(ls):
    assert ls.n_words == 8
    assert ls.lemmas == ("кот", "сидеть", "на", "окно", "и", "смотреть", "на", "птица")
    assert ls.n_content_words == 5
    assert ls.lexical_density == pytest.approx(5 / 8)
    assert ls.ranks == (2009, 204, 4, 424, 1, 153, 4, 1307)


def test_frequency(ls):
    assert ls.n_found == 7
    assert ls.coverage == pytest.approx(7 / 8)
    assert ls.mean_ipm == pytest.approx(sum(IPM[lemma] for lemma in FOUND) / 7)
    assert ls.mean_ipm_content == pytest.approx(sum(IPM[lemma] for lemma in CONTENT_FOUND) / 4)
    assert ls.mean_log_ipm == pytest.approx(sum(log10(IPM[lemma]) for lemma in FOUND) / 7)
    assert ls.mean_log_ipm_content == pytest.approx(
        sum(log10(IPM[lemma]) for lemma in CONTENT_FOUND) / 4
    )
    assert ls.mean_range == pytest.approx(sum(RANGE[lemma] for lemma in FOUND) / 7)
    assert ls.mean_dispersion == pytest.approx(sum(DISPERSION[lemma] for lemma in FOUND) / 7)


def test_surprisal(ls, freq_dict):
    floor = freq_dict.min_ipm
    expected = sum(-log2(IPM.get(lemma, floor) / 1_000_000) for lemma in ls.lemmas) / 8
    assert ls.surprisal == pytest.approx(expected)
    assert ls.perplexity == pytest.approx(2**expected)
    assert calc_surprisal(["кот"], freq_dict) == pytest.approx(-log2(40.3 / 1_000_000))
    assert calc_surprisal(["собака"], freq_dict) == pytest.approx(-log2(floor / 1_000_000))
    assert isnan(calc_surprisal([], freq_dict))


def test_bands(ls):
    assert ls.p_top1000 == pytest.approx(6 / 8)
    assert ls.p_top2000 == pytest.approx(7 / 8)
    assert ls.p_top5000 == 1
    assert ls.p_top10000 == 1
    assert ls.p_beyond_top10000 == 0
    assert ls.band_coverage() == {
        1000: pytest.approx(6 / 8),
        2000: pytest.approx(7 / 8),
        5000: 1,
        10000: 1,
    }
    assert ls.band_coverage(unique=True) == {
        1000: pytest.approx(5 / 7),
        2000: pytest.approx(6 / 7),
        5000: 1,
        10000: 1,
    }
    assert ls.band_coverage(bands=(100, 500)) == {
        100: pytest.approx(3 / 8),
        500: pytest.approx(6 / 8),
    }


def test_rare_words(freq_dict):
    ls = LexicalStats("Фелинолог пребывал на подоконнике", freq_dict=freq_dict)
    assert ls.coverage == pytest.approx(1 / 4)
    assert ls.ranks[0] is None
    assert ls.p_top1000 == pytest.approx(1 / 4)
    assert ls.p_top10000 == pytest.approx(3 / 4)
    assert ls.p_beyond_top10000 == pytest.approx(1 / 4)
    assert isnan(ls.mean_ipm_content)
    assert ls.surprisal > LexicalStats(text, freq_dict=freq_dict).surprisal


def test_numbers(freq_dict):
    ls = LexicalStats("В 2020 году 5 котов и 3-й кот", freq_dict=freq_dict)
    assert ls.words == ("В", "году", "котов", "и", "кот")
    assert ls.n_words == 5
    assert ls.coverage == pytest.approx(3 / 5)
    doc = spacy.blank("ru")("В 2020 году 5 котов и 3-й кот")
    assert LexicalStats(doc, freq_dict=freq_dict).words == ls.words
    with pytest.raises(ValueError):
        LexicalStats("2020 5.5 3-й", freq_dict=freq_dict)
    assert is_number("2020") and is_number("5,5") and is_number("3-й")
    assert not is_number("кот") and not is_number("5-миллионный")


def test_without_dict(tmp_path):
    ls = LexicalStats(text, freq_dict=FreqDict(data_dir=tmp_path))
    assert ls.p_top1000 == pytest.approx(6 / 8)
    assert ls.lexical_density == pytest.approx(5 / 8)
    with pytest.raises(OSError):
        _ = ls.mean_ipm
    with pytest.raises(OSError):
        ls.get_stats()


def test_init_doc_blank(ls, freq_dict):
    doc = spacy.blank("ru")(text)
    doc_ls = LexicalStats(doc, freq_dict=freq_dict)
    assert doc_ls.lemmas == ls.lemmas
    assert doc_ls.get_stats() == ls.get_stats()


def test_init_doc_model(nlp, freq_dict):
    ls = LexicalStats(nlp("Нож сделан из стали. Мы стали ждать."), freq_dict=freq_dict)
    assert ls.lemmas == ("нож", "сделать", "из", "сталь", "мы", "стать", "ждать")
    assert ls.n_content_words == 5
    assert (
        LexicalStats("Нож сделан из стали. Мы стали ждать.", freq_dict=freq_dict).lemmas[3]
        == "стать"
    )


def test_init_extractor(freq_dict):
    ls = LexicalStats(
        text, words_extractor=WordsExtractor(stopwords=["и", "на"]), freq_dict=freq_dict
    )
    assert ls.n_words == 5
    assert ls.p_top1000 == pytest.approx(3 / 5)


def test_top_lemmas():
    ranks = load_top_lemmas()
    assert 9900 < len(ranks) <= 10000
    assert ranks["и"] == 1
    assert ranks["в"] == 2
    assert get_rank("И") == 1
    assert get_rank("ещё") == get_rank("еще")
    assert get_rank("фелинолог") is None
    assert all(1 <= rank <= 10000 for rank in ranks.values())


def test_get_stats(ls):
    stats = ls.get_stats()
    assert list(stats) == list(LEXICAL_STATS_DESC)
    for key in LEXICAL_STATS_DESC:
        assert stats[key] == getattr(ls, key)
    for band in FREQUENCY_BANDS:
        assert f"p_top{band}" in stats


def test_print_stats(ls, capsys):
    ls.print_stats()
    captured = capsys.readouterr().out
    for value in LEXICAL_STATS_DESC.values():
        assert value in captured
