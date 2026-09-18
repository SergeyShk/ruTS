from collections import Counter
from collections.abc import Sequence
from functools import lru_cache
from itertools import pairwise
from math import log2, nan

import numpy as np
from spacy.tokens import Doc

from .constants import (
    PHON_STATS_DESC,
    PHON_WINDOW_LEN,
    RU_CONSONANTS_HIGH,
    RU_CONSONANTS_LOW,
    RU_CONSONANTS_SONOR,
    RU_CONSONANTS_YET,
    RU_MARKS,
    RU_VOWELS,
)
from .exceptions import ParameterError, SourceError, SourceTypeError
from .extractors import WordsExtractor
from .utils import iter_doc_words, safe_divide

VOWELS = frozenset(letter.lower() for letter in RU_VOWELS)
VOICELESS = frozenset(letter.lower() for letter in RU_CONSONANTS_LOW)
VOICED = frozenset(letter.lower() for letter in RU_CONSONANTS_HIGH)
SONORANTS = frozenset(letter.lower() for letter in RU_CONSONANTS_SONOR + RU_CONSONANTS_YET)
CONSONANTS = VOICELESS | VOICED | SONORANTS
MARKS = frozenset(letter.lower() for letter in RU_MARKS)
SOUNDS = VOWELS | CONSONANTS
LETTERS = SOUNDS | MARKS
IOTATED = frozenset("еёюя")
CACHE_SIZE = 1 << 16
SOUNDS_ORDER = sorted(SOUNDS)
CONSONANT_COLUMNS = [i for i, letter in enumerate(SOUNDS_ORDER) if letter in CONSONANTS]
VOWEL_COLUMNS = [i for i, letter in enumerate(SOUNDS_ORDER) if letter in VOWELS]


def check_params(window_len: int) -> None:
    """
    Проверка параметров фоностатистик

    Аргументы:
        window_len (int): Размер окна в словах для аллитерации и ассонанса

    Исключения:
        ParameterError: Если размер окна меньше 2
    """
    if window_len < 2:
        raise ParameterError("Размер окна должен быть не меньше 2")


class PhonStats:
    """
    Класс для вычисления фоностатистик текста

    Описание:
        Статистики считаются по буквам без учета оглушения, редукции и ударения:
        гласные - а, е, и, о, у, ы, э, ю, я, ё; сонорные - л, м, н, р, й;
        звонкие шумные - б, в, г, д, ж, з; глухие шумные - к, п, с, т, ф, х, ц, ч, ш, щ;
        ь и ъ не являются звуками и не учитываются в долях
        Слова делятся на слоги по правилу восходящей звучности (Аванесов)

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
        'alliteration': 0.9149440867502556,
        'assonance': 0.802520508857449,
        'p_open_syllables': 0.76,
        'mean_syllable_len': 2.6}
        >>> ps.syllables[:4]
        (('ног',), ('нет',), ('а',), ('хо', 'жу'))

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        words_extractor (WordsExtractor): Инструмент для извлечения слов
        window_len (int): Размер окна в словах для аллитерации и ассонанса

    Атрибуты:
        words (tuple[str]): Кортеж извлеченных слов в нижнем регистре
        syllables (tuple[tuple[str, ...], ...]): Кортеж слогов каждого слова
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
        print_stats: Отображение вычисленных фоностатистик текста с описанием на экран

    Исключения:
        SourceTypeError: Если передаваемое значение не является строкой или объектом Doc
        SourceError: Если в источнике данных отсутствуют слова
        ParameterError: Если размер окна меньше 2
    """

    def __init__(
        self,
        source: str | Doc,
        words_extractor: WordsExtractor | None = None,
        window_len: int = PHON_WINDOW_LEN,
    ):
        if isinstance(source, Doc):
            text = source.text
            words = tuple(word.lower() for _, _, word in iter_doc_words(source))
        elif isinstance(source, str):
            text = source
            if not words_extractor:
                words_extractor = WordsExtractor(lowercase=True)
            words = tuple(word.lower() for word in words_extractor.extract(text))
        else:
            raise SourceTypeError("Некорректный источник данных")
        if not words:
            raise SourceError("В источнике данных отсутствуют слова")
        check_params(window_len)
        self.words = words
        self.window_len = window_len
        self.syllables = tuple(_syllables(word) for word in words)

        counts = Counter(words)
        letters: Counter[str] = Counter()
        syllables: Counter[str] = Counter()
        for word, count in counts.items():
            for letter, number in Counter(word).items():
                letters[letter] += number * count
            for syllable in _syllables(word):
                syllables[syllable] += count
        self.n_vowels = sum(letters[letter] for letter in VOWELS)
        self.n_sonorants = sum(letters[letter] for letter in SONORANTS)
        self.n_voiced = sum(letters[letter] for letter in VOICED)
        self.n_voiceless = sum(letters[letter] for letter in VOICELESS)
        self.n_consonants = self.n_sonorants + self.n_voiced + self.n_voiceless
        self.n_marks = sum(letters[letter] for letter in MARKS)
        n_sounds = self.n_vowels + self.n_consonants
        self.c_clusters = _consonant_clusters(counts)
        patterns: Counter[str] = Counter()
        for syllable, count in syllables.items():
            patterns[cv_pattern(syllable)] += count
        self.c_syllable_patterns = dict(sorted(patterns.items()))

        self.p_vowels = safe_divide(self.n_vowels, n_sounds)
        self.p_sonorants = safe_divide(self.n_sonorants, n_sounds)
        self.p_voiced = safe_divide(self.n_voiced, n_sounds)
        self.p_voiceless = safe_divide(self.n_voiceless, n_sounds)
        self.consonant_vowel_ratio = safe_divide(self.n_consonants, self.n_vowels, nan)
        n_clusters = sum(self.c_clusters.values())
        self.p_heavy_clusters = safe_divide(
            sum(count for size, count in self.c_clusters.items() if size >= 3), n_clusters
        )
        self.p_hiatus = _hiatus(counts) / len(words)
        self.cv_entropy = _cv_entropy(counts)
        self.hardness = safe_divide(self.n_voiceless, self.n_vowels + self.n_sonorants, nan)
        windows = _letter_windows(words, SOUNDS_ORDER, window_len)
        self.alliteration = _repetition_index(windows, CONSONANT_COLUMNS, len(words), window_len)
        self.assonance = _repetition_index(windows, VOWEL_COLUMNS, len(words), window_len)
        n_syllables = sum(syllables.values())
        self.p_open_syllables = safe_divide(
            sum(count for syllable, count in syllables.items() if is_open_syllable(syllable)),
            n_syllables,
            nan,
        )
        self.mean_syllable_len = safe_divide(
            sum(len(syllable) * count for syllable, count in syllables.items()),
            n_syllables,
            nan,
        )

    def get_stats(self) -> dict[str, float]:
        """
        Получение вычисленных фоностатистик текста

        Вывод:
            dict[str, float]: Справочник вычисленных фоностатистик текста
        """
        return {stat: getattr(self, stat) for stat in PHON_STATS_DESC}

    def print_stats(self):
        """Отображение вычисленных фоностатистик текста с описанием на экран"""
        print(f"{'Статистика':^40}|{'Значение':^10}")
        print("-" * 50)
        stats = self.get_stats()
        for stat, value in PHON_STATS_DESC.items():
            print(f"{value:40}|{stats.get(stat):^10.2f}")


@lru_cache(maxsize=CACHE_SIZE)
def cv_pattern(word: str) -> str:
    """
    Получение CV-шаблона слова или слога

    Описание:
        Гласные обозначаются буквой V, согласные - C, ь и ъ пропускаются,
        остальные символы (латиница, цифры, дефис) не учитываются
        Результаты кэшируются по строке

    Аргументы:
        word (str): Слово или слог

    Вывод:
        str: CV-шаблон
    """
    return "".join("V" if letter in VOWELS else "C" for letter in word.lower() if letter in SOUNDS)


def syllabify(word: str) -> list[str]:
    """
    Деление слова на слоги по правилу восходящей звучности (Аванесов)

    Описание:
        Слогов в слове столько, сколько гласных; слово без гласных (предлоги в, к, с)
        слога не образует - это проклитика, для него возвращается пустой список
        Граница слога проходит по правилам:
            одиночный согласный между гласными отходит к следующему слогу: ко-ро-ва
            сочетание шумных и шумного с сонорным отходит к следующему слогу: ко-шка, се-стра, по-зна-ко-мить
            сонорный перед шумным отходит к предыдущему слогу: кар-та, пол-ка
            между двумя сонорными проходит граница: вол-на, кар-ман
            й перед согласным отходит к предыдущему слогу: май-ка, вой-на
            ь и ъ отходят к предыдущей букве: боль-шой, по-дъезд
        Каждая гласная зияния образует свой слог: а-э-ро-порт
        Правила применяются к буквам, а не звукам, поэтому деление на слоги
        орфографическое, как в школьной фонетике, а не морфемное
        Символы, кроме русских букв (дефис, цифры, латиница), отбрасываются

    Ссылки:
        https://ru.wikipedia.org/wiki/Слог

    Аргументы:
        word (str): Слово

    Вывод:
        list[str]: Список слогов
    """
    return list(_syllables(word))


@lru_cache(maxsize=CACHE_SIZE)
def _syllables(word: str) -> tuple[str, ...]:
    """Слоги слова кортежем с кэшем по слову - см. syllabify"""
    word = "".join(letter for letter in word.lower() if letter in LETTERS)
    vowel_positions = [i for i, letter in enumerate(word) if letter in VOWELS]
    if not vowel_positions:
        return ()
    if len(vowel_positions) == 1:
        return (word,)
    syllables = []
    start = 0
    for current, following in pairwise(vowel_positions):
        consonants = [
            (i, letter)
            for i, letter in enumerate(word[current + 1 : following], current + 1)
            if letter in CONSONANTS
        ]
        # Сочетание из двух и более согласных, первый из которых сонорный (в том числе й),
        # делится после сонорного; в остальных случаях согласные отходят к следующему слогу
        boundary = current + 1
        if len(consonants) > 1 and consonants[0][1] in SONORANTS:
            boundary = consonants[0][0] + 1
        while boundary < following and word[boundary] in MARKS:
            boundary += 1
        syllables.append(word[start:boundary])
        start = boundary
    syllables.append(word[start:])
    return tuple(syllables)


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
    pattern = cv_pattern(syllable)
    return pattern.endswith("V")


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
    return _consonant_clusters(Counter(text))


def _consonant_clusters(counts: Counter[str]) -> dict[int, int]:
    """Распределение кластеров по длине по счетчику словоформ"""
    counter: Counter[int] = Counter()
    for word, count in counts.items():
        for size in _clusters(word):
            counter[size] += count
    return dict(sorted(counter.items()))


@lru_cache(maxsize=CACHE_SIZE)
def _clusters(word: str) -> tuple[int, ...]:
    """Длины консонантных кластеров слова по порядку с кэшем по слову"""
    sizes = []
    size = 0
    for letter in word.lower():
        if letter in CONSONANTS:
            size += 1
        elif letter in MARKS:
            continue
        else:
            if size:
                sizes.append(size)
            size = 0
    if size:
        sizes.append(size)
    return tuple(sizes)


def calc_hiatus(text: Sequence[str]) -> int:
    """
    Вычисление количества зияний гласных

    Описание:
        Зияние - две и более гласных подряд внутри слова: аэропорт, аист, поэзия (о-э)
        Йотированные е, ё, ю, я после гласной обозначают [j] и гласный и зияния
        не образуют: заяц, моя, красивая, читает - иначе окончания прилагательных
        и глаголов давали бы четыре пятых всех зияний

    Аргументы:
        text (list[str]): Список слов

    Вывод:
        int: Количество зияний
    """
    return _hiatus(Counter(text))


def _hiatus(counts: Counter[str]) -> int:
    """Число зияний по счетчику словоформ"""
    return sum(_word_hiatus(word) * count for word, count in counts.items())


@lru_cache(maxsize=CACHE_SIZE)
def _word_hiatus(word: str) -> int:
    """Число зияний гласных в слове с кэшем по слову"""
    hiatus = 0
    previous_vowel = False
    run = False
    for letter in word.lower():
        is_vowel = letter in VOWELS
        if is_vowel and previous_vowel and letter not in IOTATED:
            if not run:
                hiatus += 1
            run = True
        else:
            run = False
        previous_vowel = is_vowel
    return hiatus


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
    return _cv_entropy(Counter(text))


def _cv_entropy(counts: Counter[str]) -> float:
    """Энтропия CV-шаблонов по счетчику словоформ"""
    patterns: Counter[str] = Counter()
    for word, count in counts.items():
        if pattern := cv_pattern(word):
            patterns[pattern] += count
    total = sum(patterns.values())
    if not total:
        return nan
    return -sum(count / total * log2(count / total) for count in patterns.values())


def _calc_repetition_index(text: Sequence[str], letters: frozenset[str], window_len: int) -> float:
    """
    Отношение наблюдаемого числа окон с повтором буквы в разных словах к ожидаемому
    при независимом распределении букв по словам
    """
    alphabet = sorted(letters)
    windows = _letter_windows([word.lower() for word in text], alphabet, window_len)
    return _repetition_index(windows, list(range(len(alphabet))), len(text), window_len)


def _letter_windows(
    words: Sequence[str], alphabet: Sequence[str], window_len: int
) -> tuple[np.ndarray, np.ndarray] | None:
    """
    Число слов с каждой буквой в каждом окне и во всем тексте

    Описание:
        Матрица «словоформа × буква» индексируется словами текста, кумулятивные суммы
        по словам дают счетчики окон разностью со сдвигом на окно; None для текста
        короче окна
    """
    n_words = len(words)
    if n_words < window_len:
        return None
    unique = list(dict.fromkeys(words))
    presence = np.array(
        [[letter in word for letter in alphabet] for word in unique], dtype=np.int32
    ).reshape(len(unique), len(alphabet))
    indices = dict(zip(unique, range(len(unique)), strict=True))
    rows = np.fromiter(map(indices.__getitem__, words), dtype=np.int64, count=n_words)
    cumulative = np.zeros((n_words + 1, len(alphabet)), dtype=np.int32)
    np.cumsum(presence[rows], axis=0, out=cumulative[1:])
    return cumulative[window_len:] - cumulative[:-window_len], cumulative[-1]


def _repetition_index(
    windows: tuple[np.ndarray, np.ndarray] | None,
    columns: Sequence[int],
    n_words: int,
    window_len: int,
) -> float:
    """Индекс повторов по счетчикам окон для столбцов выбранных букв"""
    if windows is None:
        return nan
    in_window, totals = windows
    n_windows = n_words - window_len + 1
    observed = int((in_window[:, columns] >= 2).sum())
    expected = 0.0
    for count in totals[columns]:
        if not count:
            continue
        p = int(count) / n_words
        p_single = window_len * p * (1 - p) ** (window_len - 1)
        expected += n_windows * (1 - (1 - p) ** window_len - p_single)
    return safe_divide(observed, expected, nan)


def calc_alliteration(text: Sequence[str], window_len: int = PHON_WINDOW_LEN) -> float:
    """
    Вычисление индекса аллитерации

    Описание:
        Отношение наблюдаемого числа окон из window_len соседних слов, в которых один
        и тот же согласный встречается минимум в двух словах, к ожидаемому при
        независимом распределении согласных по словам (сумма по всем согласным)
        Ожидаемое считается по частотам согласных в самом тексте, поэтому индекс
        показывает, сгруппированы ли повторы в соседних словах, а не общую частоту звука
        Значение около 1 - повторы согласных случайны, заметно больше 1 - аллитерация
        Считается по буквам без учета оглушения

    Аргументы:
        text (list[str]): Список слов
        window_len (int): Размер окна в словах

    Вывод:
        float: Значение индекса, nan для текстов короче окна
    """
    return _calc_repetition_index(text, CONSONANTS, window_len)


def calc_assonance(text: Sequence[str], window_len: int = PHON_WINDOW_LEN) -> float:
    """
    Вычисление индекса ассонанса

    Описание:
        Отношение наблюдаемого числа окон из window_len соседних слов, в которых одна
        и та же гласная встречается минимум в двух словах, к ожидаемому при независимом
        распределении гласных по словам (сумма по всем гласным)
        Ожидаемое считается по частотам гласных в самом тексте, поэтому индекс
        показывает, сгруппированы ли повторы в соседних словах, а не общую частоту звука
        Считается по всем гласным буквам без учета ударения и редукции

    Аргументы:
        text (list[str]): Список слов
        window_len (int): Размер окна в словах

    Вывод:
        float: Значение индекса, nan для текстов короче окна
    """
    return _calc_repetition_index(text, VOWELS, window_len)
