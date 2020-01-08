import re
import pytest
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
from ruts import SentsExtractor, WordsExtractor

@pytest.fixture(scope='module')
def text():
    return """
    Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие черты: полнота значений словарного состава языка или какого-либо его сегмента;
    тематический, или идеографический способ упорядочения значений слов. Отличительной особенностью тезаурусов по сравнению с формальными онтологиями является выход
    в сферу лексических значений, установление связей не только между значениями и выражающими их словами, а также между самими значениями (регистрация различных
    семантических отношений внутри словаря).
    """

class TestSentsExtractor(object):
    @staticmethod
    def test_default(text):
        se = SentsExtractor(text)
        assert len(tuple(se.extract())) == 2

    @staticmethod
    def test_tokenizer(text):
        se = SentsExtractor(text, tokenizer=re.compile(r'[;.]'))
        assert len(tuple(se.extract())) == 4

class TestWordsExtractor(object):
    @staticmethod
    def test_default(text):
        we = WordsExtractor(text)
        assert len(we.extract()) == 61
    
    @staticmethod
    def test_tokenizer(text):
        we_1 = WordsExtractor(text, tokenizer=re.compile(r'[^\w]+'))
        we_2 = WordsExtractor(text, tokenizer=wordpunct_tokenize)
        assert len(we_1.extract()) == 62
        assert len(we_2.extract()) == 63

    @staticmethod
    def test_filter_punct(text):
        we = WordsExtractor(text, filter_punct=False)
        assert len(we.extract()) == 72

    @staticmethod
    def test_filter_nums(text):
        we = WordsExtractor(text + " 33.5 + 99", filter_nums=True)
        assert len(we.extract()) == 62

    @staticmethod
    def test_use_lexemes(text):
        we = WordsExtractor(text, use_lexemes=True)
        assert len(set(['онтология', 'значение', 'связь']).intersection(set(we.extract()))) == 3

    @staticmethod
    def test_stopwords(text):
        we_1 = WordsExtractor(text, stopwords=stopwords.words('russian'))
        we_2 = WordsExtractor(text, stopwords=['и', 'а', 'с', 'в'])
        assert len(we_1.extract()) == 47
        assert len(we_2.extract()) == 57

    @staticmethod
    def test_min_len(text):
        we = WordsExtractor(text, min_len=6)
        assert len(we.extract()) == 41

    @staticmethod
    def test_max_len(text):
        we = WordsExtractor(text, max_len=6)
        assert len(we.extract()) == 26

    @staticmethod
    def test_ngram_range(text):
        we = WordsExtractor(text, ngram_range=(1, 3))
        assert len(we.extract()) == 180
        assert 'формальными_онтологиями_является' in we.words