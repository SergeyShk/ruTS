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
                se = SentsExtractor(tokenizer=tokenizer)
                se.extract(text)

    def test_extract_tokenizer(self, text):
        se_1 = SentsExtractor()
        se_2 = SentsExtractor(tokenizer=re.compile(r"[;.]"))
        se_3 = SentsExtractor(tokenizer=sent_tokenize)
        assert len(tuple(se_1.extract(text))) == 2
        assert len(tuple(se_2.extract(text))) == 4
        assert len(tuple(se_3.extract(text))) == 2

    def test_extract_min_len(self, text):
        se_1 = SentsExtractor(min_len=400)
        se_2 = SentsExtractor(min_len=250)
        assert len(tuple(se_1.extract(text))) == 0
        assert len(tuple(se_2.extract(text))) == 1

    def test_extract_max_len(self, text):
        se_1 = SentsExtractor(max_len=250)
        se_2 = SentsExtractor(max_len=100)
        assert len(tuple(se_1.extract(text))) == 1
        assert len(tuple(se_2.extract(text))) == 0


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

    def test_extract_tokenizer(self, text):
        we_1 = WordsExtractor()
        we_2 = WordsExtractor(tokenizer=re.compile(r"[^\w]+"))
        we_3 = WordsExtractor(tokenizer=wordpunct_tokenize)
        assert len(we_1.extract(text)) == 61
        assert len(we_2.extract(text)) == 62
        assert len(we_3.extract(text)) == 63

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

    def test_extract_stopwords(self, text):
        we_1 = WordsExtractor(stopwords=stopwords.words("russian"))
        we_2 = WordsExtractor(stopwords=["и", "а", "с", "в"])
        assert len(we_1.extract(text)) == 47
        assert len(we_2.extract(text)) == 57

    def test_extract_min_len(self, text):
        we = WordsExtractor(min_len=6)
        assert len(we.extract(text)) == 41

    def test_extract_max_len(self, text):
        we = WordsExtractor(max_len=6)
        assert len(we.extract(text)) == 26

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
