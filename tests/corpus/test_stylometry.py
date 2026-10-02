import pytest
import spacy

from ruts import CharNgramsExtractor, WordsExtractor
from ruts.constants import FUNCTION_UD_POS
from ruts.corpus import (
    delta,
    function_words_profile,
)

texts = {
    "А": "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне.",
    "Б": "Собака лежала на полу и дремала. Потом собака ела и снова дремала на полу.",
    "В": "Завтра кот снова будет сидеть на окне и смотреть на птиц, а собака будет дремать.",
}
extractor = WordsExtractor(lowercase=True)
corpus = {name: extractor.extract(text) for name, text in texts.items()}


def test_delta_char_ngrams():
    ngrams = CharNgramsExtractor(n=2, lowercase=True)
    distances = delta({name: ngrams.extract(text) for name, text in texts.items()}, n_mfw=20)
    assert distances.shape == (3, 3)
    assert distances.loc["А", "В"] < distances.loc["А", "Б"]


def test_function_words_profile():
    profile = function_words_profile(corpus["А"])
    assert list(profile) == list(FUNCTION_UD_POS)
    assert profile["ADP"] == pytest.approx(3 / 15)
    assert profile["CCONJ"] == pytest.approx(2 / 15)
    assert profile["PRON"] == 0
    words = ["Он", "не", "знал", ",", "что", "-", "это", "тот"]
    profile = function_words_profile(words)
    assert profile["PRON"] == pytest.approx(1 / 6)
    assert profile["PART"] == pytest.approx(2 / 6)
    assert profile["SCONJ"] == pytest.approx(1 / 6)
    assert profile["DET"] == pytest.approx(1 / 6)
    assert function_words_profile(spacy.blank("ru")(" ".join(words))) == profile
    doc = spacy.blank("ru")(texts["А"])
    assert function_words_profile(doc) == function_words_profile(corpus["А"])
    with pytest.raises(ValueError):
        function_words_profile([",", "-"])
    with pytest.raises(ValueError):
        function_words_profile([])


def test_function_words_profile_tagged():
    pytest.importorskip("ru_core_news_sm")
    doc = spacy.load("ru_core_news_sm")("Он сказал, что кот спал, а пёс во-первых ел.")
    profile = function_words_profile(doc)
    assert profile["PRON"] == pytest.approx(1 / 9)
    assert profile["SCONJ"] == pytest.approx(1 / 9)
    assert profile["CCONJ"] == pytest.approx(2 / 9)
    assert profile["ADP"] == 0
