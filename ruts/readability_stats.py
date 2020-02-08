from .basic_stats import BasicStats
from .constants import READABILITY_STATS_DESC
from .extractors import SentsExtractor, WordsExtractor
from math import sqrt
from spacy.tokens import Doc
from typing import Dict, Union

class ReadabilityStats(object):
    """
    Класс для вычисления основных метрик удобочитаемости текста

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        sents_extractor (SentsExtractor): Инструмент для извлечения предложений
        words_extractor (WordsExtractor): Инструмент для извлечения слов

    Атрибуты:
        flesch_kincaid_grade (float): Тест Флеша-Кинкайда
        flesch_reading_easy (float): Индекс удобочитаемости Флеша
        coleman_liau_index (float): Индекс Колман-Лиау
        smog_index (float): Индекс SMOG
        automated_readability_index (float): Автоматический индекс удобочитаемости
        lix (float): Индекс удобочитаемости LIX

    Методы:
        get_stats: Получение вычисленных метрик удобочитаемости текста
        print_stats: Отображение вычисленных метрик удобочитаемости текста с описанием на экран
    """

    def __init__(
        self,
        source: Union[str, Doc],
        sents_extractor: SentsExtractor = None,
        words_extractor: WordsExtractor = None
    ):
        self.bs = BasicStats(source, sents_extractor, words_extractor)

    @property
    def flesch_kincaid_grade(self):
        return calc_flesch_kincaid_grade(self.bs.n_syllables, self.bs.n_words, self.bs.n_sents)

    @property
    def flesch_reading_easy(self):
        return calc_flesch_reading_easy(self.bs.n_syllables, self.bs.n_words, self.bs.n_sents)

    @property
    def coleman_liau_index(self):
        return calc_coleman_liau_index(self.bs.n_letters, self.bs.n_words, self.bs.n_sents)

    @property
    def smog_index(self):
        return calc_smog_index(self.bs.n_complex_words, self.bs.n_sents)

    @property
    def automated_readability_index(self):
        return calc_automated_readability_index(self.bs.n_letters, self.bs.n_words, self.bs.n_sents)

    @property
    def lix(self):
        return calc_lix(self.bs.n_long_words, self.bs.n_words, self.bs.n_sents)

    def get_stats(self) -> Dict[str, float]:
        """
        Получение вычисленных метрик удобочитаемости текста

        Вывод:
            dict[str, float]: Справочник вычисленных метрик удобочитаемости текста
        """
        return {
            'flesch_kincaid_grade': self.flesch_kincaid_grade,
            'flesch_reading_easy': self.flesch_reading_easy,
            'coleman_liau_index': self.coleman_liau_index,
            'smog_index': self.smog_index,
            'automated_readability_index': self.automated_readability_index,
            'lix': self.lix
        }

    def print_stats(self):
        """Отображение вычисленных метрик удобочитаемости текста с описанием на экран"""
        print(f"{'Метрика':^40}|{'Значение':^10}")
        print("-" * 50)
        for stat, value in READABILITY_STATS_DESC.items():
            print(f"{value:40}|{self.get_stats().get(stat):^10.2f}")


def calc_flesch_kincaid_grade(
    n_syllables: int,
    n_words: int,
    n_sents: int,
    A: float = 0.49,
    B: float = 7.3,
    C: float = 16.59
) -> float:
    """
    Вычисление теста Флеша-Кинкайда

    Описание:
        Чем выше показатель, тем сложнее текст для чтения
        Результатом является число лет обучения в американской системе образования, необходимых для понимания текста

    Ссылки:
        https://en.wikipedia.org/wiki/Flesch–Kincaid_readability_tests#Flesch–Kincaid_grade_level

    Аргументы:
        n_syllables (int): Количество слогов
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        A (float): Коэффициент A
        B (float): Коэффициент B
        C (float): Коэффициент C

    Вывод:
        float: Значение теста
    """
    return (A * n_words / n_sents) + (B * n_syllables / n_words) - C

def calc_flesch_reading_easy(
    n_syllables: int,
    n_words: int,
    n_sents: int,
    A: float = 1.3,
    B: float = 60.1,
    C: float = 206.835
) -> float:
    """
    Вычисление индекса удобочитаемости Флеша

    Описание:
        Чем выше показатель, тем легче текст для чтения
        Значения индекса лежат в пределах от 0 до 100 и могут интерпретироваться следующим образом:
            100-90 - 5-й класс
            90-80 - 6-й класс
            80-70 - 7-й класс
            70-60 - 8-й и 9-й класс
            60-50 - 10-й и 11-й класс
            50-30 - Студент университета
            30-0 - Выпускник университета

    Ссылки:
        https://ru.wikipedia.org/wiki/Индекс_удобочитаемости
        https://en.wikipedia.org/wiki/Flesch–Kincaid_readability_tests#Flesch_reading_ease

    Аргументы:
        n_syllables (int): Количество слогов
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        A (float): Коэффициент A
        B (float): Коэффициент B
        C (float): Коэффициент C

    Вывод:
        float: Значение индекса
    """
    return C - (A * n_words / n_sents) - (B * n_syllables / n_words)

def calc_coleman_liau_index(
    n_letters: int,
    n_words: int,
    n_sents: int,
    A: float = 6.26,
    B: float = 0.2805,
    C: float = 31.04
) -> float:
    """
    Вычисление индекса Колман-Лиау

    Описание:
        Чем выше показатель, тем сложнее текст для чтения
        Результатом является число лет обучения в американской системе образования, необходимых для понимания текста

    Ссылки:
        https://ru.wikipedia.org/wiki/Индекс_Колман_—_Лиау
        https://en.wikipedia.org/wiki/Coleman–Liau_index

    Аргументы:
        n_letters (int): Количество букв
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        A (float): Коэффициент A
        B (float): Коэффициент B
        C (float): Коэффициент C

    Вывод:
        float: Значение индекса
    """
    return (A * n_letters / n_words) + (B * n_words / n_sents) - C

def calc_smog_index(
    n_complex: int,
    n_sents: int,
    A: float = 1.1,
    B: float = 64.6,
    C: float = 0.05
) -> float:
    """
    Вычисление индекса SMOG

    Описание:
        Simple Measure of Gobbledygook («Простое измерение разглагольствований»)
        Наиболее авторитетная метрика читабельности
        Чем выше показатель, тем сложнее текст для чтения
        Результатом является число лет обучения в американской системе образования, необходимых для понимания текста

    Ссылки:
        https://en.wikipedia.org/wiki/SMOG

    Аргументы:
        n_complex (int): Количество сложных слов
        n_sents (int): Количество предложений
        A (float): Коэффициент A
        B (float): Коэффициент B
        C (float): Коэффициент C

    Вывод:
        float: Значение индекса
    """
    return (A * sqrt(B * n_complex / n_sents)) + C

def calc_automated_readability_index(
    n_letters: int,
    n_words: int,
    n_sents: int,
    A: float = 6.26,
    B: float = 0.2805,
    C: float = 31.04
) -> float:
    """
    Вычисление автоматического индекса удобочитаемости

    Описание:
        Чем выше показатель, тем сложнее текст для чтения
        Результатом является число лет обучения в американской системе образования, необходимых для понимания текста
        Значения индекса могут интерпретироваться следующим образом:
            1 - 6-7 лет
            2 - 7-8 лет
            3 - 8-9 лет
            4 - 9-10 лет
            5 - 10-11 лет
            6 - 11-12 лет
            7 - 12-13 лет
            8 - 13-14 лет
            9 - 14-15 лет
            10 - 15-16 лет
            11 - 16-17 лет
            12 - 17-18 лет

    Ссылки:
        https://en.wikipedia.org/wiki/Automated_readability_index
        https://ru.wikipedia.org/wiki/Автоматический_индекс_удобочитаемости

    Аргументы:
        n_letters (int): Количество букв
        n_words (int): Количество слов
        n_sents (int): Количество предложений
        A (float): Коэффициент A
        B (float): Коэффициент B
        C (float): Коэффициент C

    Вывод:
        float: Значение индекса
    """
    return (A * n_letters / n_words) + (B * n_words / n_sents) - C

def calc_lix(
    n_long_words: int,
    n_words: int,
    n_sents: int
) -> float:
    """
    Вычисление индекса удобочитаемости LIX

    Описание:
        Чем выше показатель, тем сложнее текст для чтения
        Значения индекса лежат в пределах от 0 до 100 и могут интерпретироваться следующим образом:
            0-30 - Очень простые тексты, детская литература
            30-40 - Простые тексты, художественная литература, газетные статьи
            40-50 - Тексты средней сложности, журнальные статьи
            50-60 - Сложные тексты, научно-популярные статьи, профессиональная литература, официальные тексты
            60-100 - Очень сложные тексты, написанные канцелярским языком, законы

    Ссылки:
        https://en.wikipedia.org/wiki/Lix_(readability_test)
        https://ru.wikipedia.org/wiki/LIX

    Аргументы:
        n_long_words (int): Количество длинных слов
        n_words (int): Количество слов
        n_sents (int): Количество предложений

    Вывод:
        float: Значение индекса
    """
    return (n_words / n_sents) + (100 * n_long_words / n_words)


if __name__ == "__main__":
    from pprint import pprint
    from ruts.extractors import WordsExtractor
    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    we = WordsExtractor(text, use_lexemes=True)
    rs = ReadabilityStats(text, words_extractor=we)
    pprint(rs.get_stats())
    rs.print_stats()
