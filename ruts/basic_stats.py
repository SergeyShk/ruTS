from .constants import BASIC_STATS_DESC, COMPLEX_SYL_FACTOR, PUNCTUATIONS, RU_LETTERS, SPACES
from .extractors import SentsExtractor, WordsExtractor
from .utils import count_syllables
from collections import Counter
from spacy.tokens import Doc
from typing import Dict, Union

class BasicStats(object):
    """
    Класс для вычисления основных статистик текста

    Пример использования:
        >>> from ruts import BasicStats
        >>> text = "Существуют три вида лжи: ложь, наглая ложь и статистика"
        >>> bs = BasicStats(text)
        >>> bs.get_stats()
        {'c_letters': {1: 1, 3: 2, 4: 3, 6: 1, 10: 2},
        'c_syllables': {1: 5, 2: 1, 3: 1, 4: 2},
        'n_chars': 55,
        'n_complex_words': 2,
        'n_letters': 45,
        'n_long_words': 3,
        'n_monosyllable_words': 5,
        'n_polysyllable_words': 4,
        'n_punctuations': 2,
        'n_sents': 1,
        'n_simple_words': 7,
        'n_spaces': 8,
        'n_syllables': 18,
        'n_unique_words': 8,
        'n_words': 9}

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        sents_extractor (SentsExtractor): Инструмент для извлечения предложений
        words_extractor (WordsExtractor): Инструмент для извлечения слов
        normalize (bool): Вычислять нормализованные статистики

    Атрибуты:
        c_letters (dict[int, int]): Распределение слов по количеству букв
        c_syllables (dict[int, int]): Распределение слов по количеству слогов
        n_sents (int): Количество предложений
        n_words (int): Количество слов
        n_unique_words (int): Количество уникальных слов
        n_long_words (int): Количество длинных слов
        n_complex_words (int): Количество сложных слов
        n_simple_words (int): Количество простых слов
        n_monosyllable_words (int): Количество односложных слов
        n_polysyllable_words (int): Количество многосложных слов
        n_chars (int): Количество символов
        n_letters (int): Количество букв
        n_spaces (int): Количество пробелов
        n_syllables (int): Количество слогов
        n_punctuations (int): Количество знаков препинания
        p_unique_words (float): Нормализованное количество уникальных слов
        p_long_words (float): Нормализованное количество длинных слов
        p_complex_words (float): Нормализованное количество сложных слов
        p_simple_words (float): Нормализованное количество простых слов
        p_monosyllable_words (float): Нормализованное количество односложных слов
        p_polysyllable_words (float): Нормализованное количество многосложных слов
        p_letters (float): Нормализованное количество букв
        p_spaces (float): Нормализованное количество пробелов
        p_punctuations (float): Нормализованное количество знаков препинания

    Методы:
        get_stats: Получение вычисленных статистик текста
        print_stats: Отображение вычисленных статистик текста с описанием на экран

    Исключения:
        TypeError: Если передаваемое значение не является строкой или объектом Doc
        ValueError: Если в источнике данных отсутствуют слова
    """

    def __init__(
        self,
        source: Union[str, Doc],
        sents_extractor: SentsExtractor = None,
        words_extractor: WordsExtractor = None,
        normalize: bool = False
    ):
        if isinstance(source, Doc):
            text = source.text
            sents = source.sents
            words = tuple(word.text for word in source)
        elif isinstance(source, str):
            text = source
            if not sents_extractor:
                sents_extractor = SentsExtractor(text)
            sents = sents_extractor.extract()
            if not words_extractor:
                words_extractor = WordsExtractor(text)
            words = words_extractor.extract()
        else:
            raise TypeError("Некорректный источник данных")
        if not words:
            raise ValueError("В источнике данных отсутствуют слова")

        letters_per_word = tuple(len(word) for word in words)
        syllables_per_word = tuple(count_syllables(word) for word in words)
        self.c_letters = dict(sorted(Counter(letters_per_word).items()))
        self.c_syllables = dict(sorted(Counter(syllables_per_word).items()))
        self.n_sents = sum(1 for sent in sents)
        self.n_words = len(words)
        self.n_unique_words = len({word.lower() for word in words})
        self.n_long_words = sum(1 for cpw in letters_per_word if cpw >= 6)
        self.n_complex_words = sum(1 for spw in syllables_per_word if spw >= COMPLEX_SYL_FACTOR)
        self.n_simple_words = sum(1 for spw in syllables_per_word if COMPLEX_SYL_FACTOR > spw > 0)
        self.n_monosyllable_words = self.c_syllables.get(1, 0)
        self.n_polysyllable_words = self.n_words - self.c_syllables.get(1, 0) - self.c_syllables.get(0, 0)
        self.n_chars = len(text.replace('\n', ''))
        self.n_letters = sum((1 for char in text if char in RU_LETTERS))
        self.n_spaces = sum((1 for char in text if char in SPACES))
        self.n_syllables = sum(syllables_per_word)
        self.n_punctuations = sum((1 for char in text if char in PUNCTUATIONS))

        if normalize:
            self.p_unique_words = self.n_unique_words / self.n_words
            self.p_long_words = self.n_long_words / self.n_words
            self.p_complex_words = self.n_complex_words / self.n_words
            self.p_simple_words = self.n_simple_words / self.n_words
            self.p_monosyllable_words = self.n_monosyllable_words / self.n_words
            self.p_polysyllable_words = self.n_polysyllable_words / self.n_words
            self.p_letters = self.n_letters / self.n_chars
            self.p_spaces = self.n_spaces / self.n_chars
            self.p_punctuations = self.n_punctuations / self.n_chars

    def get_stats(self) -> Dict[str, int]:
        """
        Получение вычисленных статистик текста

        Вывод:
            dict[str, int]: Справочник вычисленных статистик текста
        """
        return vars(self)

    def print_stats(self):
        """Отображение вычисленных статистик текста с описанием на экран"""
        print(f"{'Статистика':^20}|{'Значение':^10}")
        print("-" * 30)
        for stat, value in BASIC_STATS_DESC.items():
            print(f"{value:20}|{self.get_stats().get(stat):^10}")