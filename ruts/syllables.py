import re
from functools import lru_cache
from itertools import pairwise

from .constants import (
    RU_CONSONANTS_HIGH,
    RU_CONSONANTS_LOW,
    RU_CONSONANTS_SONOR,
    RU_CONSONANTS_YET,
    RU_MARKS,
    RU_VOWELS,
    STRESS_CORRECTIONS,
    VERSE_CLAUSULAS,
)
from .datasets.stress_dict import StressDict
from .exceptions import SourceTypeError
from .utils import MARKED, normalize_yo, strip_marks, take_marks

CACHE_SIZE = 1 << 16
VOWELS = frozenset(letter.lower() for letter in RU_VOWELS)
SONORANTS = frozenset(letter.lower() for letter in RU_CONSONANTS_SONOR + RU_CONSONANTS_YET)
CONSONANTS = (
    frozenset(letter.lower() for letter in RU_CONSONANTS_LOW + RU_CONSONANTS_HIGH) | SONORANTS
)
MARKS = frozenset(letter.lower() for letter in RU_MARKS)
LETTERS = VOWELS | CONSONANTS | MARKS
HYPHENS = re.compile(r"[-‐‑‒–—―]")
# Частицы, не несущие ударения в составных словах
PARTICLES = frozenset({"то", "нибудь", "либо", "ка", "таки", "де", "с", "тка", "ли", "же", "бы"})
# Приставки наречий через дефис, не несущие ударения: по-прежнему, по-французски
UNSTRESSED_PREFIXES = frozenset({"по"})
# Поэтические стяжения -ие > -ье: слово ищется в словаре в полной форме
CONTRACTED_ENDINGS = (
    ("ьями", "иями"),
    ("ьем", "ием"),
    ("ьям", "иям"),
    ("ьях", "иях"),
    ("ье", "ие"),
    ("ья", "ия"),
    ("ьи", "ии"),
    ("ью", "ию"),
)
# Деепричастия ищутся в словаре как причастия с тем же ударением
CONVERB_ENDINGS = (
    ("вшись", "вшийся"),
    ("вши", "вший"),
    ("в", "вший"),
    ("аясь", "ающийся"),
    ("яясь", "яющийся"),
    ("уясь", "ующийся"),
    ("юясь", "юющийся"),
    ("ясь", "ящийся"),
    ("ась", "ащийся"),
    ("ая", "ающий"),
    ("яя", "яющий"),
    ("уя", "ующий"),
    ("юя", "юющий"),
    ("я", "ящий"),
    ("а", "ащий"),
)

_DELETE_VOWELS = str.maketrans("", "", "".join(RU_VOWELS))


def syllabify(word: str) -> list[str]:
    """
    Деление слова на слоги по правилу восходящей звучности (Аванесов)

    Описание:
        Слогов столько, сколько гласных, у слова без гласных (в, к, с) слогов нет
        Граница слога проходит по правилам:
            одиночный согласный между гласными отходит к следующему слогу: ко-ро-ва
            сочетание шумных и шумного с сонорным отходит к следующему слогу: ко-шка, се-стра, по-зна-ко-мить
            сонорный перед шумным отходит к предыдущему слогу: кар-та, пол-ка
            между двумя сонорными проходит граница: вол-на, кар-ман
            й перед согласным отходит к предыдущему слогу: май-ка, вой-на
            ь и ъ отходят к предыдущей букве: боль-шой, по-дъезд
        Каждая гласная зияния образует свой слог: а-э-ро-порт
        Деление орфографическое, по буквам; составное слово делится по частям
        (со-рок-во-ро-вка), символы кроме русских букв отбрасываются

    Ссылки:
        https://ru.wikipedia.org/wiki/Слог

    Аргументы:
        word (str): Слово

    Вывод:
        list[str]: Список слогов

    Исключения:
        SourceTypeError: Если слово не строка
    """
    _check_word(word)
    return list(_syllables(strip_marks(word)))


def count_syllables(word: str) -> int:
    """
    Вычисление количества слогов в слове

    Описание:
        Число гласных букв

    Аргументы:
        word (str): Слово

    Вывод:
        int: Количество слогов

    Исключения:
        SourceTypeError: Если слово не строка
    """
    _check_word(word)
    return _count_syllables(strip_marks(word))


def word_stress(word: str, stress_dict: StressDict | None = None) -> int | None:
    """
    Определение ударного слога слова

    Описание:
        Слоги считаются с нуля; ударение - по знаку ударения в слове (take_marks),
        по букве ё, у односложного слова - на единственном слоге, иначе по словарю
        StressDict с поправками STRESS_CORRECTIONS; у составного слова главное -
        последнее из word_stresses

    Аргументы:
        word (str): Слово
        stress_dict (StressDict): Словарь ударений; если не задан, используется StressDict()

    Вывод:
        int|None: Номер ударного слога, None если слово не найдено или в нем нет гласных

    Исключения:
        SourceTypeError: Если слово не строка
        DatasetNotFoundError: Если словарь ударений не загружен
    """
    _check_word(word)
    marked = _marked_stress(word)
    if marked is not None:
        return marked
    if stress_dict is None:
        stress_dict = _default_stress_dict()
    return _word_stress(strip_marks(word).lower(), stress_dict)


def word_stresses(word: str, stress_dict: StressDict | None = None) -> list[int]:
    """
    Определение всех ударных слогов слова

    Описание:
        Номера слогов с нуля по возрастанию; слово со знаком ударения получает его
        ударение (take_marks); составное слово через дефис, которого
        нет в словаре целиком, получает ударение каждой знаменательной части
        (сорок-воровка - 0 и 3), частицы (PARTICLES: -то, -либо, -нибудь и другие) безударны

    Аргументы:
        word (str): Слово
        stress_dict (StressDict): Словарь ударений; если не задан, используется StressDict()

    Вывод:
        list[int]: Номера ударных слогов, пустой список если слово не найдено
            или в нем нет гласных

    Исключения:
        SourceTypeError: Если слово не строка
        DatasetNotFoundError: Если словарь ударений не загружен
    """
    _check_word(word)
    marked = _marked_stress(word)
    if marked is not None:
        return [marked]
    if stress_dict is None:
        stress_dict = _default_stress_dict()
    return list(_word_stresses(strip_marks(word).lower(), stress_dict))


def stress_type(word: str, stress_dict: StressDict | None = None) -> str | None:
    """
    Определение типа окончания слова по месту ударения

    Описание:
        Названия - как у клаузул стиха (VERSE_CLAUSULAS): мужская - ударение
        на последнем слоге (земля), женская - на предпоследнем (корова),
        дактилическая - на третьем от конца (золото), гипердактилическая - раньше
        (выскочивший)

    Аргументы:
        word (str): Слово
        stress_dict (StressDict): Словарь ударений; если не задан, используется StressDict()

    Вывод:
        str|None: Тип окончания, None если слово не найдено или в нем нет гласных

    Исключения:
        SourceTypeError: Если слово не строка
        DatasetNotFoundError: Если словарь ударений не загружен
    """
    stress = word_stress(word, stress_dict)
    if stress is None:
        return None
    tail = _count_vowels(strip_marks(word).lower()) - stress - 1
    return VERSE_CLAUSULAS[min(tail, len(VERSE_CLAUSULAS) - 1)]


def _marked_stress(word: str) -> int | None:
    """Номер слога с ударением по знаку (take_marks), None без знака"""
    if not MARKED.search(word):
        return None
    clean, _, stressed = take_marks(word, positions=False)
    vowels = [i for i, letter in enumerate(clean.lower()) if letter in VOWELS]
    return next((n for n, position in enumerate(vowels) if position in stressed), None)


@lru_cache(maxsize=1)
def _default_stress_dict() -> StressDict:
    """Словарь ударений по умолчанию, один на процесс: функции слова вызываются на каждом слове"""
    return StressDict()


def _check_word(word: object) -> None:
    """Проверка, что слово - строка"""
    if not isinstance(word, str):
        raise SourceTypeError(f"Слово должно быть строкой, а не {type(word).__name__}")


@lru_cache(maxsize=CACHE_SIZE)
def _count_syllables(word: str) -> int:
    """Число гласных букв с кэшем по словоформе - см. count_syllables"""
    return len(word) - len(word.translate(_DELETE_VOWELS))


@lru_cache(maxsize=CACHE_SIZE)
def _syllables(word: str) -> tuple[str, ...]:
    """Слоги слова кортежем с кэшем по слову - см. syllabify"""
    parts: list[str] = []
    pending = ""
    for part in HYPHENS.split(word):
        if any(letter in VOWELS for letter in part.lower()):
            parts.append(pending + part)
            pending = ""
        else:
            pending += part
    if parts:
        parts[-1] += pending
    return tuple(syllable for part in parts for syllable in _part_syllables(part))


def _part_syllables(word: str) -> tuple[str, ...]:
    """Слоги части слова без дефисов"""
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


def _word_stress(word: str, stress_dict: StressDict) -> int | None:
    """Главное ударение слова в нижнем регистре - см. word_stress"""
    stresses = _word_stresses(word, stress_dict)
    return stresses[-1] if stresses else None


def _word_stresses(word: str, stress_dict: StressDict) -> tuple[int, ...]:
    """Ударные слоги слова в нижнем регистре - см. word_stresses"""
    n_syllables = _count_vowels(word)
    if not n_syllables:
        return ()
    if "ё" in word:
        # Ё составного слова ставит ударение своей части: словарь ищет форму без ё
        stresses = _compound_stresses(word, stress_dict) if "-" in word else ()
        return stresses or (_count_vowels(word[: word.index("ё")]),)
    if n_syllables == 1:
        return (0,)
    stress = _lookup(word, stress_dict)
    if stress is not None:
        return (stress,)
    if "-" in word:
        return _compound_stresses(word, stress_dict)
    for contracted, full in CONTRACTED_ENDINGS:
        if word.endswith(contracted):
            stress = _lookup(word.removesuffix(contracted) + full, stress_dict)
            if stress is not None:
                n_stem = _count_vowels(word.removesuffix(contracted))
                return (stress if stress < n_stem else max(n_stem, stress - 1),)
    for converb, participle in CONVERB_ENDINGS:
        if word.endswith(converb):
            stem = word.removesuffix(converb)
            stress = _lookup(stem + participle, stress_dict)
            if stress is not None and stress < _count_vowels(stem) + _count_vowels(converb):
                return (stress,)
    return ()


def _lookup(word: str, stress_dict: StressDict) -> int | None:
    """Ударный слог по поправкам и словарю"""
    key = normalize_yo(word)
    if key in STRESS_CORRECTIONS:
        return STRESS_CORRECTIONS[key]
    return stress_dict.lookup(key)


def _compound_stresses(word: str, stress_dict: StressDict) -> tuple[int, ...]:
    """Ударения знаменательных частей составного слова через дефис"""
    parts = []
    offset = 0
    for part in word.split("-"):
        n_syllables = _count_vowels(part)
        if n_syllables and part not in PARTICLES:
            parts.append((offset, part))
        offset += n_syllables
    if len(parts) > 1 and parts[0][1] in UNSTRESSED_PREFIXES:
        parts = parts[1:]
    stresses = []
    for offset, part in parts:
        part_stress = _word_stress(part, stress_dict)
        if part_stress is None:
            return ()
        stresses.append(offset + part_stress)
    return tuple(stresses)


def _count_vowels(text: str) -> int:
    """Число гласных букв - слогов"""
    return sum(letter in VOWELS for letter in text)
