import pymorphy2
import re
from .constants import PUNCTUATIONS
from abc import ABCMeta, abstractmethod
from collections import Counter
from nltk.tokenize import sent_tokenize, word_tokenize
from typing import Callable, List, Pattern, Tuple, Union

class Extractor(object, metaclass=ABCMeta):
    """
    Абстрактный класс для извлечения объектов из текста

    Аргументы:
        text (str): Строка текста
        tokenizer (pattern|callable): Токенизатор или регулярное выражение

    Методы:
        extract: Извлечение объектов из текста
    """

    @abstractmethod
    def __init__(
        self,
        text: str,
        tokenizer: Union[Pattern, Callable] = None
    ):
        self.text = text
        self.tokenizer = tokenizer

    @abstractmethod
    def extract(self) -> Tuple[str, ...]:
        pass

class SentsExtractor(Extractor):
    """
    Класс для извлечения предложений из текста

    Аргументы:
        text (str): Строка текста
        tokenizer (pattern|callable): Токенизатор или регулярное выражение
        min_len (int): Минимальная длина извлекаемого предложения
        max_len (int): Максимальная длина извлекаемого предложения

    Методы:
        extract: Извлечение предложений из текста

    Исключения:
        ValueError: Если минимальная длина предложения больше максимальной
    """

    def __init__(
        self,
        text: str,
        tokenizer: Union[Pattern, Callable] = None,
        min_len: int = 0,
        max_len: int = 0
    ):
        super().__init__(text, tokenizer)
        self.min_len = min_len
        self.max_len = max_len
        if self.min_len > self.max_len:
            raise ValueError("Минимальная длина предложения больше максимальной")

    def extract(self) -> Tuple[str, ...]:
        """
        Извлечение предложений из текста

        Вывод:
            sents (tuple[str]): Кортеж извлеченных предложений

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
        return tuple(self.sents)

class WordsExtractor(Extractor):
    """
    Класс для извлечения слов из текста

    Аргументы:
        text (str): Строка текста
        tokenizer (pattern|callable): Токенизатор или регулярное выражение
        filter_punct (bool): Фильтровать знаки препинания
        filter_nums (bool): Фильтровать числа
        use_lexemes (bool): Использовать леммы слов
        stopwords (list[str]): Список стоп-слов
        lowercase (bool): Конвертировать слова в нижний регистр
        ngram_range (tuple[int, int]): Нижняя и верхняя граница размера N-грамм
        min_len (int): Минимальная длина извлекаемого слова
        max_len (int): Максимальная длина извлекаемого слова

    Методы:
        extract: Извлечение слов из текста
        get_most_common: Получение счетчика топ-слов

    Исключения:
        ValueError: Если нижняя граница N-грамм большей верхней
        ValueError: Если минимальная длина слова больше максимальной
    """

    def __init__(
        self,
        text: str,
        tokenizer: Union[Pattern, Callable] = None,
        filter_punct: bool = True,
        filter_nums: bool = False,
        use_lexemes: bool = False,
        stopwords: List[str] = None,
        lowercase: bool = False,
        ngram_range: Tuple[int, int] = (1, 1),
        min_len: int = 0,
        max_len: int = 0
    ):
        super().__init__(text, tokenizer)
        self.filter_punct = filter_punct
        self.filter_nums = filter_nums
        self.use_lexemes = use_lexemes
        self.stopwords = stopwords
        self.lowercase = lowercase
        self.ngram_range = ngram_range
        if self.ngram_range[0] > self.ngram_range[1]:
            raise ValueError("Нижняя граница N-грамм большей верхней")
        self.min_len = min_len
        self.max_len = max_len
        if self.min_len and self.max_len and self.min_len > self.max_len:
            raise ValueError("Минимальная длина слова больше максимальной")
        self.words = ()

    def extract(self) -> Tuple[str, ...]:
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

    def get_most_common(self, n: int = 10) -> Counter:
        """
        Получение счетчика топ-слов

        Аргументы:
            n (int): Количество слов

        Вывод:
            Counter: Счетчик топ-слов

        Исключения:
            ValueError: Если указанное количество слов меньше 0
        """
        if n < 1:
            raise ValueError("Количество слов должно быть больше 0")
        return Counter(self.words).most_common(n)

    def __make_ngrams(self) -> Tuple[str, ...]:
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
    print(se.extract())