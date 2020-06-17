import re
import pytest
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, wordpunct_tokenize
from ruts import SentsExtractor, WordsExtractor
from ruts.extractors import Extractor

@pytest.fixture(scope='module')
def text():
    return "Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие черты: полнота значений словарного состава языка или\
        какого-либо его сегмента; тематический, или идеографический способ упорядочения значений слов. Отличительной особенностью тезаурусов по сравнению\
        с формальными онтологиями является выход в сферу лексических значений, установление связей не только между значениями и выражающими их словами,\
        а также между самими значениями (регистрация различных семантических отношений внутри словаря)."

class TestSentsExtractor(object):
    @staticmethod
    def test_init_value_error(text):
        with pytest.raises(ValueError):
            SentsExtractor(text, min_len=10, max_len=5)

    @staticmethod
    def test_extract(text):
        se = SentsExtractor(text)
        assert len(tuple(se.extract())) == 2

    @staticmethod
    def test_extract_type_error(text):
        tokenizers = [666, ['a', 'b'], {'a': 'b'}]
        for tokenizer in tokenizers:
            try:
                SentsExtractor(text, tokenizer=tokenizer)
            except TypeError:
                pytest.fail("Токенизатор задан некорректно")

    @staticmethod
    def test_extract_tokenizer(text):
        se_1 = SentsExtractor(text)
        se_2 = SentsExtractor(text, tokenizer=re.compile(r'[;.]'))
        se_3 = SentsExtractor(text, tokenizer=sent_tokenize)
        assert len(tuple(se_1.extract())) == 2
        assert len(tuple(se_2.extract())) == 4
        assert len(tuple(se_3.extract())) == 2

    @staticmethod
    def test_extract_min_len(text):
        se_1 = SentsExtractor(text, min_len=400)
        se_2 = SentsExtractor(text, min_len=250)
        assert len(tuple(se_1.extract())) == 0
        assert len(tuple(se_2.extract())) == 1

    @staticmethod
    def test_extract_max_len(text):
        se_1 = SentsExtractor(text, max_len=250)
        se_2 = SentsExtractor(text, max_len=100)
        assert len(tuple(se_1.extract())) == 1
        assert len(tuple(se_2.extract())) == 0

class TestWordsExtractor(object):
    @staticmethod
    def test_init_value_error_1(text):
        with pytest.raises(ValueError):
            WordsExtractor(text, ngram_range=(2, 1))

    @staticmethod
    def test_init_value_error_2(text):
        with pytest.raises(ValueError):
            WordsExtractor(text, min_len=10, max_len=5)

    @staticmethod
    def test_extract(text):
        we = WordsExtractor(text)
        assert len(we.extract()) == 61

    @staticmethod
    def test_extract_type_error(text):
        tokenizers = [666, ['a', 'b'], {'a': 'b'}]
        for tokenizer in tokenizers:
            try:
                WordsExtractor(text, tokenizer=tokenizer)
            except TypeError:
                pytest.fail("Токенизатор задан некорректно")

    @staticmethod
    def test_extract_tokenizer(text):
        we_1 = WordsExtractor(text)
        we_2 = WordsExtractor(text, tokenizer=re.compile(r'[^\w]+'))
        we_3 = WordsExtractor(text, tokenizer=wordpunct_tokenize)
        assert len(we_1.extract()) == 61
        assert len(we_2.extract()) == 62
        assert len(we_3.extract()) == 63

    @staticmethod
    def test_extract_filter_punct(text):
        we = WordsExtractor(text, filter_punct=False)
        assert len(we.extract()) == 72

    @staticmethod
    def test_extract_filter_nums(text):
        we = WordsExtractor(text + " 33.5 + 99", filter_nums=True)
        assert len(we.extract()) == 62

    @staticmethod
    def test_extract_use_lexemes(text):
        we = WordsExtractor(text, use_lexemes=True)
        assert len(set(['онтология', 'значение', 'связь']).intersection(set(we.extract()))) == 3

    @staticmethod
    def test_extract_stopwords(text):
        we_1 = WordsExtractor(text, stopwords=stopwords.words('russian'))
        we_2 = WordsExtractor(text, stopwords=['и', 'а', 'с', 'в'])
        assert len(we_1.extract()) == 47
        assert len(we_2.extract()) == 57

    @staticmethod
    def test_extract_min_len(text):
        we = WordsExtractor(text, min_len=6)
        assert len(we.extract()) == 41

    @staticmethod
    def test_extract_max_len(text):
        we = WordsExtractor(text, max_len=6)
        assert len(we.extract()) == 26

    @staticmethod
    def test_extract_ngram_range(text):
        we = WordsExtractor(text, ngram_range=(1, 3))
        assert len(we.extract()) == 180
        assert 'формальными_онтологиями_является' in we.words

    @staticmethod
    def test_get_most_common_value_error(text):
        with pytest.raises(ValueError):
            we = WordsExtractor(text)
            we.get_most_common(0)

    @staticmethod
    def test_get_most_common(text):
        we = WordsExtractor(text)
        we.extract()
        assert we.get_most_common(1) == [('значений', 3)]