import pymorphy2
import re
from abc import ABCMeta, abstractmethod
from collections import Counter
from collections.abc import Iterable
from nltk.tokenize import sent_tokenize, word_tokenize
from ruts.constants import PUNCTUATIONS
from typing import Pattern, Tuple

class Extractor(object, metaclass=ABCMeta):
    """
    Абстрактный класс для извлечения объектов из текста

    Аргументы:
        text (str): Строка текста
        tokenizer (func|Pattern): Токенизатор или регулярное выражение

    Методы:
        extract: Извлечение объектов из текста
    """

    @abstractmethod
    def __init__(self, text, tokenizer=None):
        self.text = text
        self.tokenizer = tokenizer

    @abstractmethod
    def extract(self):
        pass

class SentsExtractor(Extractor):
    """
    Класс для извлечения предложений из текста

    Аргументы:
        text (str): Строка текста
        tokenizer (func|Pattern): Токенизатор или регулярное выражение
        min_len (int): Минимальная длина извлекаемого предложения
        max_len (int): Максимальная длина извлекаемого предложения

    Методы:
        extract: Извлечение предложений из текста

    Исключения:
        ValueError: Если минимальная длина предложения больше максимальной
    """

    def __init__(self, text, tokenizer=None, min_len=0, max_len=0):
        super().__init__(text, tokenizer)
        self.min_len = min_len
        self.max_len = max_len
        if self.min_len > self.max_len:
            raise ValueError("Минимальная длина предложения больше максимальной")

    def extract(self):
        """
        Извлечение предложений из текста

        Вывод:
            sents (gen[str]): Генератор извлеченных предложений

        Исключения:
            TypeError: Если некорректно задан токенизатор
        """
        if not self.tokenizer:
            self.sents = sent_tokenize(self.text)
        elif isinstance(self.tokenizer, Pattern):
            self.sents = re.split(self.tokenizer, self.text)
        else:
            try:
                self.sents = self.tokenizer(self.text)
            except:
                raise TypeError("Токенизатор задан некорректно")
        if self.min_len > 0:
            self.sents = (sent for sent in self.sents if len(sent) >= self.min_len)
        if self.max_len > 0:
            self.sents = (sent for sent in self.sents if len(sent) <= self.max_len)

        for sent in self.sents:
            yield sent

class WordsExtractor(Extractor):
    """
    Класс для извлечения слов из текста

    Аргументы:
        text (str): Строка текста
        tokenizer (func|Pattern): Токенизатор или регулярное выражение
        filter_punct (bool): Фильтровать знаки препинания
        filter_nums (bool): Фильтровать числа
        use_lexemes (bool): Использовать леммы слов
        stopwords (list[str]): Использовать список стоп-слов
        lowercase (bool): Конвертировать слова в нижний регистр
        ngram_range (tuple[int, int]): Нижняя и верхняя граница размера N-грамм
        min_len (int): Минимальная длина извлекаемого слова
        max_len (int): Максимальная длина извлекаемого слова

    Методы:
        extract: Извлечение слов из текста
        get_most_common: Получение счетчика топ-слов

    Исключения:
        TypeError: Если список стоп-слов не является итерируемым типом
        TypeError: Если список стоп-слов содержит не строковые значения
        TypeError: Если значение границ N-грамм не является кортежем
        TypeError: Если список стоп-слов не является итерируемым типом
        ValueError: Если нижняя граница N-грамм большей верхней
        ValueError: Если минимальная длина слова больше максимальной
    """

    def __init__(
        self,
        text,
        tokenizer=None,
        filter_punct=True,
        filter_nums=False,
        use_lexemes=False,
        stopwords=None,
        lowercase=False,
        ngram_range=(1, 1),
        min_len=0,
        max_len=0
    ):
        super().__init__(text, tokenizer)
        self.filter_punct = filter_punct
        self.filter_nums = filter_nums
        self.use_lexemes = use_lexemes
        self.stopwords = stopwords
        if self.stopwords:
            if isinstance(self.stopwords, Iterable):
                if not all(isinstance(stopword, str) for stopword in self.stopwords):
                    raise TypeError("Список стоп-слов содержит не строковые значения")
            else:
                raise TypeError("Список стоп-слов не является итерируемым типом")
        self.lowercase = lowercase
        self.ngram_range = ngram_range
        if isinstance(self.ngram_range, Tuple):
            if len(self.ngram_range) != 2 or not all(isinstance(n, int) for n in self.ngram_range):
                raise TypeError("Кортеж границ N-грамм задан некорректно")
            if self.ngram_range[0] > self.ngram_range[1]:
                raise ValueError("Нижняя граница N-грамм большей верхней")
        else:
            raise TypeError("Значение границ N-грамм не является кортежем")
        self.min_len = min_len
        self.max_len = max_len
        if self.min_len and self.max_len and self.min_len > self.max_len:
            raise ValueError("Минимальная длина слова больше максимальной")
        self.words = ()

    def extract(self):
        """
        Извлечение слов из текста

        Вывод:
            words (tuple[str]): Кортеж извлеченных слов

        Исключения:
            TypeError: Если некорректно задан токенизатор
        """
        if not self.tokenizer:
            self.words = (word for word in word_tokenize(self.text))
        elif isinstance(self.tokenizer, Pattern):
            self.words = (word for word in re.split(self.tokenizer, self.text))
        else:
            try:
                self.words = (word for word in self.tokenizer(self.text))
            except:
                raise TypeError("Токенизатор задан некорректно")
        if self.filter_punct:
            self.words = (word for word in self.words if word not in PUNCTUATIONS)
        if self.filter_nums:
            self.words = (word for word in self.words if not word.isnumeric())
        if self.use_lexemes:
            morph = pymorphy2.MorphAnalyzer()
            self.words = (morph.parse(word)[0].normal_form for word in self.words)
        if self.stopwords:
            self.words = (word for word in self.words if word not in self.stopwords)
        if self.lowercase:
            self.words = (word.lower() for word in self.words)
        if self.min_len > 0:
            self.words = (word for word in self.words if len(word) >= self.min_len)
        if self.max_len > 0:
            self.words = (word for word in self.words if len(word) <= self.max_len)
        self.words = tuple(self.words)
        if self.ngram_range != (1, 1):
            self.words = self.__make_ngrams()
        return tuple(self.words)

    def get_most_common(self, n=10):
        """
        Получение счетчика топ-слов

        Аргументы:
            n (int): Количество слов

        Вывод:
            Counter: Счетчик топ-слов

        Исключения:
            TypeError: Если значение количества слов не является числом
            ValueError: Если указанное количество слов меньше 0
        """
        if isinstance(n, int):
            if n < 1:
                raise ValueError("Количество слов должно быть большь 0")
        else:
            raise TypeError("Количество слов должно быть числом")
        return Counter(self.words).most_common(n)

    def __make_ngrams(self):
        """
        Формирование N-грамм

        Вывод:
            ngrams (tuple[str]): Кортеж извлеченных N-грамм
        """
        ngrams = ()
        for n in range(self.ngram_range[0], self.ngram_range[1] + 1):
            ngrams += tuple('_'.join(self.words[i: i + n]) for i in range(len(self.words) - n + 1))
        return ngrams


if __name__ == "__main__":
    from nltk.corpus import stopwords
    text = 'Не имей 100 рублей, а имей 100 друзей'
    we = WordsExtractor(text,
    use_lexemes=True, stopwords=stopwords.words('russian'), filter_nums=True, ngram_range=(1, 2))
    print(we.extract())
    se = SentsExtractor(text, tokenizer=re.compile(r', '))
    print(tuple(se.extract()))
