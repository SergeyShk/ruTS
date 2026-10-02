from collections.abc import Mapping
from re import Pattern

import anyts.basic_stats
from anyts.basic_stats import DASH_PATTERN
from anyts.utils import check_integer
from spacy.tokens import Doc

from .constants import BASIC_STATS_DESC, COMPLEX_SYL_FACTOR, LONG_WORD_LETTER_FACTOR
from .exceptions import ParameterError
from .extractors import SentsExtractor, WordsExtractor
from .syllables import count_syllables

PUNCTUATION_MARKS = {**anyts.basic_stats.PUNCTUATION_MARKS, "„": "straight_quotes"}


class BasicStats(anyts.basic_stats.BasicStats):
    """
    Класс для вычисления основных статистик текста

    Пример использования:
        >>> from ruts import BasicStats
        >>> text = "Существуют три вида лжи: ложь, наглая ложь и статистика"
        >>> bs = BasicStats(text)
        >>> bs.get_stats()
        {'c_letters': {1: 1, 3: 2, 4: 3, 6: 1, 10: 2},
         'c_syllables': {1: 5, 2: 1, 3: 1, 4: 2},
         'n_sents': 1,
         'n_words': 9,
         'n_unique_words': 8,
         'n_long_words': 3,
         'n_complex_words': 2,
         'n_simple_words': 7,
         'n_monosyllable_words': 5,
         'n_polysyllable_words': 4,
         'n_chars': 55,
         'n_letters': 45,
         'n_spaces': 8,
         'n_syllables': 18,
         'n_punctuations': 2,
         'c_punctuations': {'comma': 1,
                            'period': 0,
                            'question': 0,
                            'exclamation': 0,
                            'ellipsis': 0,
                            'colon': 1,
                            'semicolon': 0,
                            'dash': 0,
                            'hyphen': 0,
                            'angle_quotes': 0,
                            'straight_quotes': 0,
                            'parentheses': 0,
                            'other': 0}}

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc); для Doc слова
            берутся из токенов (дефисные слова склеиваются), предложения - из разметки,
            без границ предложений - через SentsExtractor
        sents_extractor (SentsExtractor): Инструмент для извлечения предложений;
            если задан, применяется и к тексту Doc
        words_extractor (WordsExtractor): Инструмент для извлечения слов;
            если задан, применяется и к тексту Doc
        normalize (bool): Вычислять нормализованные статистики
        complex_syl_factor (int): Минимальное количество слогов в сложном слове
        long_word_letter_factor (int): Минимальное количество букв в длинном слове

    Атрибуты:
        c_letters (dict[int, int]): Распределение слов по количеству букв
        c_syllables (dict[int, int]): Распределение слов по количеству слогов
        n_sents (int): Количество предложений со словами
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
        c_punctuations (dict[str, int]): Распределение знаков препинания по типам
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
        count_syllables: Количество слогов слова по правилам русского языка
        count_punctuations: Количество знаков препинания текста по типам
        count_words_by_syllables: Количество слов с заданным минимальным числом слогов
        count_words_by_letters: Количество слов с заданным минимальным числом букв
        get_stats: Получение вычисленных статистик текста
        print_stats: Отображение вычисленных статистик текста с описанием на экран

    Исключения:
        SourceTypeError: Если источник данных не строка и не объект Doc или экстрактор
            другого типа
        SourceError: Если в источнике данных отсутствуют слова
        ParameterError: Если порог не целое число или меньше 1
    """

    sents_extractor_class = SentsExtractor
    words_extractor_class = WordsExtractor
    join_hyphens = True
    stats_desc = BASIC_STATS_DESC
    stats_headers = ("Статистика", "Значение")

    def __init__(
        self,
        source: str | Doc,
        sents_extractor: SentsExtractor | None = None,
        words_extractor: WordsExtractor | None = None,
        normalize: bool = False,
        complex_syl_factor: int = COMPLEX_SYL_FACTOR,
        long_word_letter_factor: int = LONG_WORD_LETTER_FACTOR,
    ):
        super().__init__(
            source,
            sents_extractor,
            words_extractor,
            normalize,
            complex_syl_factor,
            long_word_letter_factor,
        )

    def count_syllables(self, word: str) -> int:
        """
        Подсчет слогов слова по правилам русского языка

        Аргументы:
            word (str): Слово

        Вывод:
            int: Количество слогов
        """
        return count_syllables(word)

    def count_punctuations(self, text: str) -> dict[str, int]:
        """
        Подсчет знаков препинания текста по типам (count_punctuations)

        Аргументы:
            text (str): Строка текста

        Вывод:
            dict[str, int]: Число знаков каждого типа в порядке PUNCTUATION_TYPES
        """
        return count_punctuations(text)


def count_punctuations(
    text: str,
    marks: Mapping[str, str] = PUNCTUATION_MARKS,
    dash_pattern: Pattern[str] = DASH_PATTERN,
) -> dict[str, int]:
    """
    Подсчет знаков препинания по типам

    Описание:
        Типы из PUNCTUATION_TYPES: запятые, точки, вопросительные и восклицательные
        знаки, многоточия («Кто там?..» - вопрос и многоточие), двоеточия, точки
        с запятой, тире (в том числе дефис, которым тире набирают в текстовых
        корпусах: «- Ушли, - сказал он»), дефисы в словах, кавычки-ёлочки, прямые
        кавычки и лапки, скобки и прочие знаки. Знаки ядра anyTS дополнены нижней
        кавычкой „

    Аргументы:
        text (str): Строка текста
        marks (dict[str, str]): Тип каждого знака
        dash_pattern (Pattern): Тире, набранные дефисами

    Вывод:
        dict[str, int]: Число знаков каждого типа в порядке PUNCTUATION_TYPES

    Исключения:
        SourceTypeError: Если текст не строка, знаки не словарь или тире
            не скомпилированное регулярное выражение
        ParameterError: Если знак не один символ или его тип неизвестен

    Пример использования:
        >>> from ruts.basic_stats import count_punctuations
        >>> counts = count_punctuations("- Кто там?.. - спросил он. „Никого“")
        >>> {kind: count for kind, count in counts.items() if count}
        {'period': 1, 'question': 1, 'ellipsis': 1, 'dash': 2, 'straight_quotes': 2}
    """
    return anyts.basic_stats.count_punctuations(text, marks, dash_pattern)


def punctuation_profile(text: str, n_words: int | None = None) -> dict[str, float]:
    """
    Вычисление профиля пунктуации - частот знаков по типам на 1000 слов

    Описание:
        Частоты типов из PUNCTUATION_TYPES (count_punctuations) на 1000 слов и доля
        буквы ё среди букв е и ё (yo_share) - пишет ли автор ё. Профиль - редакторский
        и стилометрический признак; он зависит от оформления текста (типографские
        кавычки и тире, буква ё) и легко подделывается, поэтому его стоит смотреть
        отдельно от лингвистических признаков

    Аргументы:
        text (str): Строка текста
        n_words (int): Число слов; если не задано, слова извлекаются WordsExtractor

    Вывод:
        dict[str, float]: Частоты типов на 1000 слов и yo_share; nan без слов
            или без букв е и ё

    Исключения:
        SourceTypeError: Если текст не строка
        ParameterError: Если число слов не целое или отрицательно
    """
    if n_words is not None:
        check_integer(n_words, "number of words")
        if n_words < 0:
            raise ParameterError("Число слов не может быть отрицательным")
    counts = count_punctuations(text)
    if n_words is None:
        n_words = len(WordsExtractor().extract(text))
    profile = {
        kind: count / n_words * 1000 if n_words else float("nan") for kind, count in counts.items()
    }
    lowered = text.lower()
    n_ye = lowered.count("е") + lowered.count("ё")
    profile["yo_share"] = lowered.count("ё") / n_ye if n_ye else float("nan")
    return profile
