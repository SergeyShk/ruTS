from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from functools import lru_cache
from typing import TYPE_CHECKING

import anyts
import anyts.phon_stats
from anyts.phon_stats import calc_repetition_index, consonant_clusters, count_hiatus
from anyts.utils import check_words, shannon_entropy

from .constants import (
    CORE_MESSAGES,
    PHON_STATS_DESC,
    PHON_WINDOW_LEN,
    RU_CONSONANTS_HIGH,
    RU_CONSONANTS_LOW,
)
from .extractors import WordsExtractor
from .syllables import CONSONANTS, MARKS, SONORANTS, VOWELS, _syllables, syllabify as syllabify
from .utils import strip_marks

if TYPE_CHECKING:
    from spacy.tokens import Doc

VOICELESS = frozenset(letter.lower() for letter in RU_CONSONANTS_LOW)
VOICED = frozenset(letter.lower() for letter in RU_CONSONANTS_HIGH)
IOTATED = frozenset("еёюя")
CACHE_SIZE = 1 << 16


def check_params(window_len: int) -> None:
    """
    Проверка параметров фоностатистик

    Аргументы:
        window_len (int): Размер окна в словах для аллитерации и ассонанса

    Исключения:
        ParameterError: Если размер окна не целое число или меньше 2
    """
    anyts.phon_stats.check_params(window_len, messages=CORE_MESSAGES)


class PhonStats(anyts.phon_stats.PhonStats):
    """
    Класс для вычисления фоностатистик текста

    Описание:
        Расширяет PhonStats ядра anyTS крючками русского языка: звуки - буквы без учета
        оглушения, редукции и ударения (гласные - а, е, и, о, у, ы, э, ю, я, ё;
        сонорные - л, м, н, р, й; звонкие шумные - б, в, г, д, ж, з; глухие шумные -
        к, п, с, т, ф, х, ц, ч, ш, щ), ь и ъ - не звуки и не разрывают кластер,
        йотированные е, ё, ю, я после гласной не дают зияния, слоги - по правилу
        восходящей звучности (Аванесов). Слова Doc - без знаков ударения, дефисные
        слова склеиваются

    Пример использования:
        >>> from ruts import PhonStats
        >>> text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
        >>> ps = PhonStats(text)
        >>> ps.get_stats()
        {'p_vowels': 0.4032258064516129,
        'p_sonorants': 0.11290322580645161,
        'p_voiced': 0.1935483870967742,
        'p_voiceless': 0.2903225806451613,
        'consonant_vowel_ratio': 1.48,
        'p_heavy_clusters': 0.034482758620689655,
        'p_hiatus': 0.0,
        'cv_entropy': 3.13957226198672...,
        'hardness': 0.5625,
        'alliteration': 1.0916179337231968,
        'assonance': 0.8305084745762712,
        'p_open_syllables': 0.76,
        'mean_syllable_len': 2.6}
        >>> ps.syllables[:4]
        (('ног',), ('нет',), ('а',), ('хо', 'жу'))

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        words_extractor (WordsExtractor): Инструмент для извлечения слов;
            если задан, применяется и к тексту Doc
        window_len (int): Размер окна в словах для аллитерации и ассонанса

    Атрибуты:
        words (tuple[str]): Кортеж извлеченных слов в нижнем регистре
        window_len (int): Размер окна в словах для аллитерации и ассонанса
        syllables (tuple[tuple[str, ...], ...]): Кортеж слогов каждого слова
        sounds (tuple[str]): Звуки каждого слова - его буквы
        n_vowels (int): Количество гласных
        n_consonants (int): Количество согласных
        n_sonorants (int): Количество сонорных согласных
        n_voiced (int): Количество звонких шумных согласных
        n_voiceless (int): Количество глухих шумных согласных
        n_marks (int): Количество мягких и твердых знаков
        c_clusters (dict[int, int]): Распределение консонантных кластеров по длине
        c_syllable_patterns (dict[str, int]): Распределение слогов по CV-шаблону
        p_vowels (float): Доля гласных среди звуков
        p_sonorants (float): Доля сонорных согласных среди звуков
        p_voiced (float): Доля звонких шумных согласных среди звуков
        p_voiceless (float): Доля глухих шумных согласных среди звуков
        consonant_vowel_ratio (float): Отношение согласных к гласным
        p_heavy_clusters (float): Доля кластеров из 3 и более согласных
        p_hiatus (float): Зияний гласных на слово
        cv_entropy (float): Энтропия CV-шаблонов слов в битах
        hardness (float): Жёсткость - отношение глухих шумных к гласным и сонорным
        alliteration (float): Индекс аллитерации
        assonance (float): Индекс ассонанса
        p_open_syllables (float): Доля открытых слогов
        mean_syllable_len (float): Средняя длина слога в буквах

    Методы:
        get_stats: Получение вычисленных фоностатистик текста
        to_dataframe: Получение статистик таблицей из одной строки
        describe: Прочтение статистики по шкале; шкал нет - None
        print_stats: Отображение вычисленных фоностатистик текста с описанием на экран

    Исключения:
        SourceTypeError: Если источник данных не строка и не объект Doc или экстрактор
            другого типа
        SourceError: Если в источнике данных отсутствуют слова
        ParameterError: Если размер окна не целое число или меньше 2
    """

    words_extractor_class = WordsExtractor
    join_hyphens = True
    vowels = VOWELS
    sonorants = SONORANTS
    voiced = VOICED
    voiceless = VOICELESS
    skipped = MARKS
    glides = IOTATED
    stats_desc = PHON_STATS_DESC
    stats_headers = ("Статистика", "Значение")
    messages = CORE_MESSAGES

    def __init__(
        self,
        source: str | Doc,
        words_extractor: anyts.WordsExtractor | None = None,
        window_len: int = PHON_WINDOW_LEN,
    ):
        super().__init__(source, words_extractor, window_len)
        letters = "".join(self.words)
        self.n_marks = sum(map(letters.count, MARKS))

    def doc_words(self, doc: Doc) -> tuple[str, ...]:
        """Слова Doc ядра без знаков ударения"""
        return tuple(map(strip_marks, super().doc_words(doc)))

    def syllabify(self, word: str) -> tuple[str, ...]:
        """Слоги слова по правилу восходящей звучности (ruts.syllables.syllabify)"""
        return _syllables(word)


@lru_cache(maxsize=CACHE_SIZE)
def cv_pattern(word: str) -> str:
    """
    Получение CV-шаблона слова или слога

    Описание:
        Гласные обозначаются буквой V, согласные - C, ь и ъ пропускаются,
        остальные символы (латиница, цифры, дефис) не учитываются (cv_pattern ядра)

    Аргументы:
        word (str): Слово или слог

    Вывод:
        str: CV-шаблон
    """
    return anyts.phon_stats.cv_pattern(word.lower(), VOWELS, CONSONANTS)


def is_open_syllable(syllable: str) -> bool:
    """
    Проверка, является ли слог открытым

    Описание:
        Открытый слог оканчивается на гласную, ь и ъ после гласной не закрывают слог

    Аргументы:
        syllable (str): Слог

    Вывод:
        bool: Результат проверки
    """
    return cv_pattern(syllable).endswith("V")


def calc_consonant_clusters(text: Sequence[str]) -> dict[int, int]:
    """
    Вычисление распределения консонантных кластеров по длине

    Описание:
        Кластер - последовательность согласных внутри слова, ь и ъ не прерывают кластер
        Кластеры длиной 1 - одиночные согласные между гласными или на краях слова

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        dict[int, int]: Количество кластеров каждой длины
    """
    check_words(text)
    counter: Counter[int] = Counter()
    for word, count in Counter(text).items():
        for size in consonant_clusters(word.lower(), CONSONANTS, MARKS):
            counter[size] += count
    return dict(sorted(counter.items()))


def calc_hiatus(text: Sequence[str]) -> int:
    """
    Вычисление количества зияний гласных

    Описание:
        Зияние - две и более гласных подряд внутри слова: аэропорт, аист, поэзия (о-э)
        Йотированные е, ё, ю, я после гласной обозначают [j] и гласный и зияния
        не образуют: заяц, моя, красивая, читает

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        int: Количество зияний
    """
    check_words(text)
    return sum(
        count_hiatus(word.lower(), VOWELS, IOTATED) * count
        for word, count in Counter(text).items()
    )


def calc_cv_entropy(text: Sequence[str]) -> float:
    """
    Вычисление энтропии CV-шаблонов слов

    Описание:
        Энтропия Шеннона распределения слов по CV-шаблону в битах: чем выше значение,
        тем разнообразнее фонетическая форма слов текста
        Слова без гласных и согласных (числа, латиница) не учитываются

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        float: Значение энтропии, nan если в тексте нет слов с буквами
    """
    check_words(text)
    return shannon_entropy(Counter(pattern for word in text if (pattern := cv_pattern(word))))


def calc_alliteration(text: Sequence[str], window_len: int = PHON_WINDOW_LEN) -> float:
    """
    Вычисление индекса аллитерации

    Описание:
        Отношение наблюдаемого числа окон из window_len соседних слов, в которых один
        и тот же согласный встречается минимум в двух словах, к ожидаемому при
        случайном порядке слов (сумма по всем согласным)
        Ожидаемое считается по частотам согласных в самом тексте, поэтому индекс
        показывает, сгруппированы ли повторы в соседних словах, а не общую частоту звука
        Значение около 1 - повторы согласных случайны, заметно больше 1 - аллитерация
        Считается по буквам без учета оглушения

    Аргументы:
        text (list[str]): Список слов
        window_len (int): Размер окна в словах

    Вывод:
        float: Значение индекса, nan для текстов короче окна или без согласной в двух словах
    """
    check_words(text)
    check_params(window_len)
    return calc_repetition_index([word.lower() for word in text], window_len, CONSONANTS)


def calc_assonance(text: Sequence[str], window_len: int = PHON_WINDOW_LEN) -> float:
    """
    Вычисление индекса ассонанса

    Описание:
        Отношение наблюдаемого числа окон из window_len соседних слов, в которых одна
        и та же гласная встречается минимум в двух словах, к ожидаемому при случайном
        порядке слов (сумма по всем гласным)
        Ожидаемое считается по частотам гласных в самом тексте, поэтому индекс
        показывает, сгруппированы ли повторы в соседних словах, а не общую частоту звука
        Считается по всем гласным буквам без учета ударения и редукции

    Аргументы:
        text (list[str]): Список слов
        window_len (int): Размер окна в словах

    Вывод:
        float: Значение индекса, nan для текстов короче окна или без гласной в двух словах
    """
    check_words(text)
    check_params(window_len)
    return calc_repetition_index([word.lower() for word in text], window_len, VOWELS)
