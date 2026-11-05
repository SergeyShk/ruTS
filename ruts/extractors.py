import re
from collections import deque
from collections.abc import Iterable
from contextvars import ContextVar
from typing import ClassVar

import anyts
import rumorph
from anyts.utils import is_punctuation

from .constants import CORE_MESSAGES
from .utils import analyze_text, iter_text_sents, iter_tokens, parse_word, strip_marks, word_form

# Разряды числа разделяют и пробелы: обычный, неразрывный, тонкий, узкий неразрывный
NUMBER_PATTERN = re.compile(r"\d+(?:[.,:/ \u00a0\u2009\u202f-]\d+)*(?:-[а-яё]{1,3})?")


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
        Токенизатор по умолчанию - сегментатор anySeg (ruts.utils.iter_text_sents)

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

    messages = CORE_MESSAGES

    def sentenize(self, text: str) -> Iterable[str]:
        """Разбиение текста на предложения anySeg (ruts.utils.iter_text_sents)"""
        return (sent for _, _, sent in iter_text_sents(text))


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
        Токенизатор по умолчанию - сегментатор anySeg (ruts.utils.iter_tokens); с ним
        леммы - разбор ruMorph в контексте предложения, с заданным токенизатором -
        первый разбор. Фильтры применяются по порядку: знаки препинания, числа,
        лемматизация, нижний регистр, стоп-слова (без учета регистра), длина слова
        Числами считаются и диапазоны, дроби, порядковые числительные, числа
        с пробелами между разрядами: 2020-2021, 1,5, 3-й, 1 250 000

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

    messages = CORE_MESSAGES

    number_pattern: ClassVar[re.Pattern[str]] = NUMBER_PATTERN

    def tokenize(self, text: str) -> Iterable[str]:
        """Разбиение текста на слова ruts.utils.iter_tokens без точки сокращения (word_form)"""
        return (word_form(word) for _, _, word in iter_tokens(text))

    def extract(self, text: str) -> tuple[str, ...]:
        """Извлечение слов из текста без знаков ударения и мягких переносов"""
        if isinstance(text, str):
            text = strip_marks(text)
        if not isinstance(text, str) or not self.use_lexemes or self.tokenizer is not None:
            return super().extract(text)
        token = _CONTEXT.set(deque(analyze_text(text)))
        try:
            return super().extract(text)
        finally:
            _CONTEXT.reset(token)

    def lemmatize(self, word: str) -> str:
        """Лемма слова: разбора в контексте предложения при извлечении строки, иначе первого"""
        context = _CONTEXT.get()
        if context and not is_punctuation(word):
            # Слова идут по порядку, а пропущенные фильтрами (числа) снимаются с очереди
            while context:
                form, analysis = context.popleft()
                if form == word:
                    return analysis.lemma
        return parse_word(word).lemma


# Разборы слов строки в контексте на время extract: очередь своя у каждого потока
_CONTEXT: ContextVar[deque[tuple[str, rumorph.Analysis]] | None] = ContextVar(
    "ruts_lemma_context", default=None
)


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
        N-граммы берутся окном по строке со знаками препинания, пробельные символы
        схлопываются в один пробел (Stamatatos 2009); при within_words - только внутри
        слов токенизатора без знаков препинания, слова короче n N-грамм не дают

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

    messages = CORE_MESSAGES

    def tokenize(self, text: str) -> Iterable[str]:
        """Разбиение текста на слова ruts.utils.iter_tokens без точки сокращения (word_form)"""
        return (word_form(word) for _, _, word in iter_tokens(text))

    def extract(self, text: str) -> tuple[str, ...]:
        """Извлечение N-грамм из текста без знаков ударения и мягких переносов (strip_marks)"""
        return super().extract(strip_marks(text) if isinstance(text, str) else text)
