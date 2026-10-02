import re
from collections.abc import Iterable
from typing import ClassVar

import anyts
from razdel import sentenize

from .utils import iter_tokens, parse_word

NUMBER_PATTERN = re.compile(r"\d+(?:[.,:/-]\d+)*(?:-[а-яё]{1,3})?")


class SentsExtractor(anyts.SentsExtractor):
    """
    Класс для извлечения предложений из текста

    Пример использования:
        >>> import re
        >>> from ruts import SentsExtractor
        >>> text = "Не имей 100 рублей, а имей 100 друзей"
        >>> se = SentsExtractor(tokenizer=re.compile(r', '))
        >>> se.extract(text)
        ('Не имей 100 рублей', 'а имей 100 друзей')

    Описание:
        Токенизатор по умолчанию - razdel

    Аргументы:
        tokenizer (pattern|callable): Токенизатор или регулярное выражение
        min_len (int): Минимальная длина извлекаемого предложения
        max_len (int): Максимальная длина извлекаемого предложения

    Методы:
        extract: Извлечение предложений из текста

    Исключения:
        ParameterError: Если граница длины не целое число, отрицательна или минимальная
            длина больше максимальной
    """

    def sentenize(self, text: str) -> Iterable[str]:
        """Разбиение текста на предложения razdel"""
        return (sent.text for sent in sentenize(text))


class WordsExtractor(anyts.WordsExtractor):
    """
    Класс для извлечения слов из текста

    Пример использования:
        >>> from ruts import WordsExtractor
        >>> text = "Не имей 100 рублей, а имей 100 друзей"
        >>> we = WordsExtractor(use_lexemes=True, stopwords=["не", "а"],
        ...                     filter_nums=True, ngram_range=(1, 2))
        >>> we.extract(text)
        ('иметь', 'рубль', 'иметь', 'друг', 'иметь_рубль', 'рубль_иметь', 'иметь_друг')

    Описание:
        Токенизатор по умолчанию - razdel с отделением приклеенных тире
        (ruts.utils.iter_tokens), леммы - первый разбор pymorphy3. Фильтры применяются
        по порядку: знаки препинания, числа, лемматизация, нижний регистр, стоп-слова,
        длина слова; стоп-слова сравниваются без учета регистра
        Числами считаются также диапазоны, дроби и порядковые числительные:
        2020-2021, 5.5, 1,5, 3-й, 90-х

    Аргументы:
        tokenizer (pattern|callable): Токенизатор или регулярное выражение
        filter_punct (bool): Фильтровать знаки препинания
        filter_nums (bool): Фильтровать числа
        use_lexemes (bool): Использовать леммы слов
        stopwords (collection[str]): Стоп-слова
        lowercase (bool): Конвертировать слова в нижний регистр
        ngram_range (tuple[int, int]): Нижняя и верхняя граница размера N-грамм
        min_len (int): Минимальная длина извлекаемого слова
        max_len (int): Максимальная длина извлекаемого слова

    Методы:
        extract: Извлечение слов из текста
        get_most_common: Получение счетчика топ-слов

    Исключения:
        ParameterError: Если границы N-грамм не пара целых чисел, нижняя меньше единицы
            или больше верхней
        ParameterError: Если граница длины не целое число, отрицательна или минимальная
            длина больше максимальной
        SourceTypeError: Если стоп-слова не набор строк
    """

    number_pattern: ClassVar[re.Pattern[str]] = NUMBER_PATTERN

    def tokenize(self, text: str) -> Iterable[str]:
        """Разбиение текста на слова ruts.utils.iter_tokens"""
        return (word for _, _, word in iter_tokens(text))

    def lemmatize(self, word: str) -> str:
        """Лемма слова по первому разбору pymorphy3"""
        return str(parse_word(word).normal_form)


class CharNgramsExtractor(anyts.CharNgramsExtractor):
    """
    Класс для извлечения символьных N-грамм из текста

    Пример использования:
        >>> from ruts import CharNgramsExtractor
        >>> text = "Кот сидел  на окне, а пёс - на полу."
        >>> ce = CharNgramsExtractor(n=3, lowercase=True)
        >>> ce.extract(text)[:6]
        ('кот', 'от ', 'т с', ' си', 'сид', 'иде')
        >>> ce.get_most_common(2)
        [(' на', 2), ('на ', 2)]
        >>> CharNgramsExtractor(n=3, lowercase=True, within_words=True).extract(text)
        ('кот', 'сид', 'иде', 'дел', 'окн', 'кне', 'пёс', 'пол', 'олу')

    Описание:
        N-граммы берутся окном по строке, пробельные символы предварительно
        схлопываются в один пробел, знаки препинания сохраняются (Stamatatos 2009);
        при within_words N-граммы не пересекают границ слов: текст режется
        токенизатором на слова (по умолчанию ruts.utils.iter_tokens), знаки
        препинания отбрасываются, слова короче N N-грамм не дают

    Аргументы:
        n (int): Длина N-граммы в символах
        lowercase (bool): Конвертировать текст в нижний регистр
        within_words (bool): Брать N-граммы только внутри слов
        tokenizer (pattern|callable): Токенизатор слов для within_words
            или регулярное выражение

    Методы:
        extract: Извлечение N-грамм из текста
        get_most_common: Получение счетчика топ-N-грамм

    Исключения:
        ParameterError: Если длина N-граммы не целое число или меньше единицы
    """

    def tokenize(self, text: str) -> Iterable[str]:
        """Разбиение текста на слова ruts.utils.iter_tokens"""
        return (word for _, _, word in iter_tokens(text))
