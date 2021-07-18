from typing import Any, Callable, List, Pattern, Tuple, Union

import re
from abc import ABCMeta, abstractmethod
from collections import Counter

import pymorphy2
from razdel import sentenize, tokenize

from .constants import PUNCTUATIONS


class Extractor(object, metaclass=ABCMeta):
    """
    Абстрактный класс для извлечения объектов из текста

    Аргументы:
        tokenizer (pattern|callable): Токенизатор или регулярное выражение
        min_len (int): Минимальная длина извлекаемого объекта
        max_len (int): Максимальная длина извлекаемого объекта

    Методы:
        extract: Извлечение объектов из текста
    """

    @abstractmethod
    def __init__(
        self, tokenizer: Union[Pattern, Callable] = None, min_len: int = 0, max_len: int = 0
    ):
        self.tokenizer = tokenizer
        self.min_len = min_len
        self.max_len = max_len

    @abstractmethod
    def extract(self) -> Tuple[str, ...]:
        raise NotImplementedError


class SentsExtractor(Extractor):
    """
    Класс для извлечения предложений из текста

    Пример использования:
        >>> import re
        >>> from ruts import SentsExtractor
        >>> text = "Не имей 100 рублей, а имей 100 друзей"
        >>> se = SentsExtractor(tokenizer=re.compile(r', '))
        >>> se.extract(text)
        ('Не имей 100 рублей', 'а имей 100 друзей')

    Аргументы:
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
        tokenizer: Union[Pattern, Callable] = None,
        min_len: int = 0,
        max_len: int = 0,
    ):
        super().__init__(tokenizer, min_len, max_len)
        if self.min_len and self.max_len and self.min_len > self.max_len:
            raise ValueError("Минимальная длина предложения больше максимальной")
        self.sents = ()
        if not self.tokenizer:
            self.tokenizer = lambda text: (sent.text for sent in sentenize(text))

    def extract(self, text: str) -> Tuple[str, ...]:
        """
        Извлечение предложений из текста

        Аргументы:
            text (str): Строка текста

        Вывод:
            sents (tuple[str]): Кортеж извлеченных предложений

        Исключения:
            TypeError: Если некорректно задан токенизатор
        """
        if isinstance(self.tokenizer, Pattern):
            self.sents = re.split(self.tokenizer, text)
        else:
            try:
                self.sents = self.tokenizer(text)
            except Exception:
                raise TypeError("Токенизатор задан некорректно")
        if self.min_len > 0:
            self.sents = (sent for sent in self.sents if len(sent) >= self.min_len)
        if self.max_len > 0:
            self.sents = (sent for sent in self.sents if len(sent) <= self.max_len)
        return tuple(self.sents)


class WordsExtractor(Extractor):
    """
    Класс для извлечения слов из текста

    Пример использования:
        >>> from nltk.corpus import stopwords
        >>> from ruts import WordsExtractor
        >>> text = "Не имей 100 рублей, а имей 100 друзей"
        >>> we = WordsExtractor(use_lexemes=True, stopwords=stopwords.words('russian'),
        >>>                     filter_nums=True, ngram_range=(1, 2))
        >>> we.extract(text)
        ('иметь', 'рубль', 'иметь', 'друг', 'иметь_рубль', 'рубль_иметь', 'иметь_друг')

    Аргументы:
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
        tokenizer: Union[Pattern, Callable] = None,
        filter_punct: bool = True,
        filter_nums: bool = False,
        use_lexemes: bool = False,
        stopwords: List[str] = None,
        lowercase: bool = False,
        ngram_range: Tuple[int, int] = (1, 1),
        min_len: int = 0,
        max_len: int = 0,
    ):
        super().__init__(tokenizer, min_len, max_len)
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
        if not self.tokenizer:
            self.tokenizer = lambda text: (word.text for word in tokenize(text))

    def extract(
        self,
        text: str,
    ) -> Tuple[str, ...]:
        """
        Извлечение слов из текста

        Аргументы:
            text (str): Строка текста

        Вывод:
            words (tuple[str]): Кортеж извлеченных слов

        Исключения:
            TypeError: Если некорректно задан токенизатор
        """
        if isinstance(self.tokenizer, Pattern):
            self.words = (word for word in re.split(self.tokenizer, text))
        else:
            try:
                self.words = (word for word in self.tokenizer(text))
            except Exception:
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

    def get_most_common(self, n: int = 10) -> List[Tuple[Any, int]]:
        """
        Получение счетчика топ-слов

        Аргументы:
            n (int): Количество слов

        Вывод:
            List: Список топ-слов

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
        ngrams: Tuple[str, ...] = ()
        for n in range(self.ngram_range[0], self.ngram_range[1] + 1):
            ngrams += tuple(
                "_".join(tuple(self.words)[i : i + n])
                for i in range(len(tuple(self.words)) - n + 1)
            )
        return ngrams
