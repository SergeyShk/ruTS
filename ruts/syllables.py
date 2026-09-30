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
from .utils import normalize_yo

CACHE_SIZE = 1 << 16
VOWELS = frozenset(letter.lower() for letter in RU_VOWELS)
SONORANTS = frozenset(letter.lower() for letter in RU_CONSONANTS_SONOR + RU_CONSONANTS_YET)
CONSONANTS = (
    frozenset(letter.lower() for letter in RU_CONSONANTS_LOW + RU_CONSONANTS_HIGH) | SONORANTS
)
MARKS = frozenset(letter.lower() for letter in RU_MARKS)
LETTERS = VOWELS | CONSONANTS | MARKS
# Частицы, не несущие ударения в составных словах
PARTICLES = frozenset({"то", "нибудь", "либо", "ка", "таки", "де", "с", "тка"})
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

    Исключения:
        SourceTypeError: Если слово не строка
    """
    _check_word(word)
    return list(_syllables(word))


def count_syllables(word: str) -> int:
    """
    Вычисление количества слогов в слове

    Описание:
        Число гласных букв - столько же слогов дает syllabify; результаты кэшируются
        по словоформе

    Аргументы:
        word (str): Слово

    Вывод:
        int: Количество слогов

    Исключения:
        SourceTypeError: Если слово не строка
    """
    _check_word(word)
    return _count_syllables(word)


def word_stress(word: str, stress_dict: StressDict | None = None) -> int | None:
    """
    Определение ударного слога слова

    Описание:
        Слоги считаются по гласным с нуля, как в syllabify; у слов с буквой ё
        ударение на ней, у односложных слов - на единственном слоге; иначе ударение
        берется из словаря StressDict с поправками STRESS_CORRECTIONS. Составные
        слова через дефис ищутся целиком, затем по частям (частицы -то, -нибудь, -ка
        безударны), и главным считается последнее из word_stresses; поэтические
        стяжения (желанье - желание) и деепричастия (забыв - забывший) ищутся
        в словаре по полной форме

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
    if stress_dict is None:
        stress_dict = StressDict()
    return _word_stress(word.lower(), stress_dict)


def word_stresses(word: str, stress_dict: StressDict | None = None) -> list[int]:
    """
    Определение всех ударных слогов слова

    Описание:
        Номера слогов с нуля по возрастанию. У большинства слов одно ударение
        (см. word_stress); составное слово через дефис, которого нет в словаре
        целиком, получает ударение каждой знаменательной части (сорок-воровка -
        0 и 3), частицы -то, -нибудь, -ка безударны. Словарь хранит одно ударение
        слова, поэтому у составных слов, найденных целиком, побочное ударение
        не выделяется

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
    if stress_dict is None:
        stress_dict = StressDict()
    return list(_word_stresses(word.lower(), stress_dict))


def stress_type(word: str, stress_dict: StressDict | None = None) -> str | None:
    """
    Определение типа окончания слова по месту ударения

    Описание:
        Названия - как у клаузул стиха (VERSE_CLAUSULAS): мужская - ударение
        на последнем слоге (земля), женская - на предпоследнем (корова),
        дактилическая - на третьем от конца (золото), гипердактилическая - раньше
        (выскочивший); ударение - главное, по word_stress

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
    tail = _count_vowels(word.lower()) - stress - 1
    return VERSE_CLAUSULAS[min(tail, len(VERSE_CLAUSULAS) - 1)]


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
        return (_count_vowels(word[: word.index("ё")]),)
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
    stresses = []
    offset = 0
    for part in word.split("-"):
        n_syllables = _count_vowels(part)
        if n_syllables and part not in PARTICLES:
            part_stress = _word_stress(part, stress_dict)
            if part_stress is None:
                return ()
            stresses.append(offset + part_stress)
        offset += n_syllables
    return tuple(stresses)


def _count_vowels(text: str) -> int:
    """Число гласных букв - слогов"""
    return sum(letter in VOWELS for letter in text)
