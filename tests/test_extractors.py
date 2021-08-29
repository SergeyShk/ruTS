import re

import pytest
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, wordpunct_tokenize

from ruts import SentsExtractor, WordsExtractor


@pytest.fixture(scope="module")
def text():
    return "Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие черты: полнота\
        значений словарного состава языка или какого-либо его сегмента; тематический, или идеографический способ\
        упорядочения значений слов. Отличительной особенностью тезаурусов по сравнению с формальными онтологиями\
        является выход в сферу лексических значений, установление связей не только между значениями и выражающими их\
        словами, а также между самими значениями (регистрация различных семантических отношений внутри словаря)."


class TestSentsExtractor(object):
    def test_init_value_error(self):
        with pytest.raises(ValueError):
            SentsExtractor(min_len=10, max_len=5)

    def test_extract(self, text):
        se = SentsExtractor()
        assert len(tuple(se.extract(text))) == 2

    def test_extract_type_error(self, text):
        tokenizers = [666, ["a", "b"], {"a": "b"}]
        for tokenizer in tokenizers:
            with pytest.raises(TypeError):
                se = SentsExtractor(tokenizer=tokenizer)  # type: ignore
                se.extract(text)

    @pytest.mark.parametrize(
        "tokenizer, expected",
        [(None, 2), (re.compile(r"[;.]"), 4), (sent_tokenize, 2)],
    )
    def test_extract_tokenizer(self, text, tokenizer, expected):
        se = SentsExtractor(tokenizer=tokenizer)
        assert len(tuple(se.extract(text))) == expected

    @pytest.mark.parametrize(
        "min_len, expected",
        [(400, 0), (250, 1)],
    )
    def test_extract_min_len(self, text, min_len, expected):
        se = SentsExtractor(min_len=min_len)
        assert len(tuple(se.extract(text))) == expected

    @pytest.mark.parametrize(
        "max_len, expected",
        [(250, 1), (100, 0)],
    )
    def test_extract_max_len(self, text, max_len, expected):
        se = SentsExtractor(max_len=max_len)
        assert len(tuple(se.extract(text))) == expected


class TestWordsExtractor(object):
    def test_init_value_error_1(self):
        with pytest.raises(ValueError):
            WordsExtractor(ngram_range=(2, 1))

    def test_init_value_error_2(self):
        with pytest.raises(ValueError):
            WordsExtractor(min_len=10, max_len=5)

    def test_extract(self, text):
        we = WordsExtractor()
        assert len(we.extract(text)) == 61

    @pytest.mark.parametrize("tokenizer", [666, ["a", "b"], {"a": "b"}])
    def test_extract_type_error(self, text, tokenizer):
        tokenizers = [666, ["a", "b"], {"a": "b"}]
        for tokenizer in tokenizers:
            with pytest.raises(TypeError):
                we = WordsExtractor(tokenizer=tokenizer)
                we.extract(text)

    @pytest.mark.parametrize(
        "tokenizer, expected",
        [
            (None, 61),
            (re.compile(r"[^\w]+"), 62),
            (wordpunct_tokenize, 63),
        ],
    )
    def test_extract_tokenizer(self, text, tokenizer, expected):
        we = WordsExtractor(tokenizer=tokenizer)
        assert len(we.extract(text)) == expected

    def test_extract_filter_punct(self, text):
        we = WordsExtractor(filter_punct=False)
        assert len(we.extract(text)) == 72

    def test_extract_filter_nums(self, text):
        we = WordsExtractor(filter_nums=True)
        assert len(we.extract(text + " 33.5 + 99")) == 62

    def test_extract_use_lexemes(self, text):
        we = WordsExtractor(use_lexemes=True)
        assert (
            len(set(["онтология", "значение", "связь"]).intersection(set(we.extract(text)))) == 3
        )

    @pytest.mark.parametrize(
        "stopwords, expected",
        [
            (stopwords.words("russian"), 47),
            (["и", "а", "с", "в"], 57),
        ],
    )
    def test_extract_stopwords(self, text, stopwords, expected):
        we = WordsExtractor(stopwords=stopwords)
        assert len(we.extract(text)) == expected

    @pytest.mark.parametrize(
        "min_len, expected",
        [(6, 41), (3, 54)],
    )
    def test_extract_min_len(self, text, min_len, expected):
        we = WordsExtractor(min_len=min_len)
        assert len(we.extract(text)) == expected

    @pytest.mark.parametrize(
        "max_len, expected",
        [(6, 26), (3, 11)],
    )
    def test_extract_max_len(self, text, max_len, expected):
        we = WordsExtractor(max_len=max_len)
        assert len(we.extract(text)) == expected

    def test_extract_ngram_range(self, text):
        we = WordsExtractor(ngram_range=(1, 3))
        assert len(we.extract(text)) == 180
        assert "формальными_онтологиями_является" in we.words

    def test_get_most_common_value_error(self):
        with pytest.raises(ValueError):
            we = WordsExtractor()
            we.get_most_common(0)

    def test_get_most_common(self, text):
        we = WordsExtractor()
        we.extract(text)
        assert we.get_most_common(1) == [("значений", 3)]
