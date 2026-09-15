from collections import Counter
from collections.abc import Collection, Mapping, Sequence
from functools import cache
from itertools import combinations, pairwise
from math import nan
from statistics import fmean
from typing import NamedTuple

import numpy as np
from spacy.tokens import Doc, Token

from .constants import (
    COHESION_STATS_DESC,
    CONNECTOR_CLASSES,
    CONNECTOR_POS,
    CONNECTOR_POS_EXTRA,
    CONNECTOR_TYPES,
    CONTENT_POS,
    CONTENT_UD_POS,
    DEMONSTRATIVE_LEMMAS,
    RESOURCES_DIR,
    STOPWORD_GRAMMEMES,
)
from .extractors import SentsExtractor, WordsExtractor
from .morph_stats import word_pos
from .utils import iter_doc_units, lemmatize, normalize_yo, parse_word, safe_divide

CONNECTORS_FILE = RESOURCES_DIR / "connectors.tsv"


class WordInfo(NamedTuple):
    """
    Признаки слова, нужные для статистик связности

    Атрибуты:
        lemma (str): Лемма в нижнем регистре
        noun (bool): Существительное
        pronoun (bool): Местоимение, включая указательные
        demonstrative (bool): Указательное местоимение
        argument (bool): Аргумент - существительное или местоимение-существительное
        content (bool): Знаменательное слово
        tense (str|None): Время глагольной формы
        aspect (str|None): Вид глагольной формы
    """

    lemma: str
    noun: bool
    pronoun: bool
    demonstrative: bool
    argument: bool
    content: bool
    tense: str | None
    aspect: str | None


class Overlap(NamedTuple):
    """
    Повторы элементов между предложениями

    Атрибуты:
        adjacent (float): Доля пар соседних предложений с общим элементом
        all (float): Доля всех пар предложений с общим элементом
        prop_adjacent (float): Средний коэффициент Дайса по парам соседних предложений
        prop_all (float): Средний коэффициент Дайса по всем парам предложений
    """

    adjacent: float
    all: float
    prop_adjacent: float
    prop_all: float


class Connector(NamedTuple):
    """
    Вхождение коннектора в текст

    Атрибуты:
        sent (int): Номер предложения
        start (int): Позиция первого слова коннектора в предложении
        end (int): Позиция за последним словом коннектора
        text (str): Коннектор в словарной форме
        cls (str): Класс коннектора (causal, adversative, concessive, temporal,
            additive, conditional, reformulative)
        kind (str): Тип коннектора (primary, secondary)
    """

    sent: int
    start: int
    end: int
    text: str
    cls: str
    kind: str


class CohesionStats:
    """
    Класс для вычисления статистик связности текста

    Описание:
        Референциальная связность по образцу Coh-Metrix: повторы существительных,
        аргументов (существительных и местоимений) и знаменательных слов между
        соседними предложениями и всеми парами предложений, данность (местоимения,
        указательные, повторяющиеся леммы) и темпоральная связность (повтор времени
        и вида глаголов в соседних предложениях)
        Пары предложений сравниваются по леммам. Для Doc с разметкой частей речи
        части речи, время и вид берутся из token.pos_ и token.morph, лемма - из разбора
        pymorphy3 с частью речи токена (lemmatize): лемматизатор моделей ru_core_news
        возвращает словоформу для AUX и при расхождении признаков (были, них, стихли);
        для строки и Doc без разметки - из первого разбора pymorphy3. Doc без границ
        предложений разбивается на предложения и слова как строка; дефисные слова,
        разрезанные spaCy, склеиваются (iter_doc_units)
        Знаменательные слова: по pymorphy3 - CONTENT_POS без STOPWORD_GRAMMEMES,
        по UD - CONTENT_UD_POS; местоимения: по pymorphy3 - NPRO и Apro, по UD - PRON
        и DET; слова с леммой из DEMONSTRATIVE_LEMMAS считаются местоимениями
        Коннекторы (потому что, однако, затем, иными словами) ищутся по словоформам
        в каждом предложении по словарю resources/connectors.tsv с классами
        по Криони, Никину и Филипповой (2008) и типом - первичные (союзы и наречия)
        или вторичные (лексикализованные обороты); плотность считается на 1000 слов
        Однословный коннектор засчитывается только при части речи из CONNECTOR_POS
        (союз, частица, наречие, предлог, междометие) или из CONNECTOR_POS_EXTRA
        для отдельных слов (словом, главное, допустим, точнее) - по разметке Doc
        или по pymorphy3 для строки, так «раз» и «значит» как существительное
        и глагол не считаются
        и не считаются знаменательными в обоих случаях

    Ссылки:
        https://doi.org/10.1017/CBO9780511894664 (McNamara и др. 2014, Coh-Metrix)
        https://doi.org/10.3758/s13428-015-0651-7 (Crossley и др. 2016, TAACO)

    Пример использования:
        >>> from ruts import CohesionStats
        >>> text = "Кот сидел на окне. Он смотрел на птиц. Птицы улетели, и кот уснул. Завтра он снова будет сидеть на этом окне."
        >>> cs = CohesionStats(text)
        >>> cs.get_stats()
        {'noun_overlap_adjacent': 0.3333333333333333,
        'noun_overlap_all': 0.5,
        'argument_overlap_adjacent': 0.3333333333333333,
        'argument_overlap_all': 0.6666666666666666,
        'content_overlap_adjacent': 0.3333333333333333,
        'content_overlap_all': 0.5,
        'content_overlap_prop_adjacent': 0.1111111111111111,
        'content_overlap_prop_all': 0.18650793650793648,
        'p_pronouns': 0.14285714285714285,
        'pronoun_noun_ratio': 0.5,
        'p_demonstratives': 0.047619047619047616,
        'p_given': 0.2857142857142857,
        'tense_repetition': 0.6666666666666666,
        'aspect_repetition': 0.3333333333333333,
        'temporal_cohesion': 0.5,
        'connectors': 47.61904761904762,
        'connectors_causal': 0.0,
        'connectors_adversative': 0.0,
        'connectors_concessive': 0.0,
        'connectors_temporal': 0.0,
        'connectors_additive': 47.61904761904762,
        'connectors_conditional': 0.0,
        'connectors_reformulative': 0.0,
        'connectors_primary': 47.61904761904762,
        'connectors_secondary': 0.0}
        >>> cs.lemmas[1]
        ('он', 'смотреть', 'на', 'птица')
        >>> cs.connector_spans
        (Connector(sent=2, start=2, end=3, text='и', cls='additive', kind='primary'),)

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        sents_extractor (SentsExtractor): Инструмент для извлечения предложений
        words_extractor (WordsExtractor): Инструмент для извлечения слов
        connectors (dict[str, tuple[str, str]]): Словарь коннекторов - класс и тип
            по коннектору; если не задан, используется словарь из resources

    Атрибуты:
        words (tuple[tuple[str, ...], ...]): Кортеж слов каждого предложения
        lemmas (tuple[tuple[str, ...], ...]): Кортеж лемм каждого предложения
        n_sents (int): Количество предложений, содержащих слова
        n_words (int): Количество слов
        n_nouns (int): Количество существительных
        n_pronouns (int): Количество местоимений
        n_demonstratives (int): Количество указательных местоимений
        n_content_words (int): Количество знаменательных слов
        n_given (int): Количество знаменательных слов, лемма которых встречалась ранее
        n_connectors (int): Количество коннекторов
        connector_spans (tuple[Connector]): Кортеж вхождений коннекторов
        c_connectors (dict[str, int]): Распределение вхождений по коннекторам
        noun_overlap_adjacent (float): Доля пар соседних предложений с общим существительным
        noun_overlap_all (float): Доля всех пар предложений с общим существительным
        argument_overlap_adjacent (float): Доля пар соседних предложений с общим существительным или местоимением
        argument_overlap_all (float): Доля всех пар предложений с общим существительным или местоимением
        content_overlap_adjacent (float): Доля пар соседних предложений с общим знаменательным словом
        content_overlap_all (float): Доля всех пар предложений с общим знаменательным словом
        content_overlap_prop_adjacent (float): Средняя доля общих знаменательных слов в соседних предложениях
        content_overlap_prop_all (float): Средняя доля общих знаменательных слов во всех парах предложений
        p_pronouns (float): Доля местоимений среди слов
        pronoun_noun_ratio (float): Отношение числа местоимений к числу существительных
        p_demonstratives (float): Доля указательных местоимений среди слов
        p_given (float): Доля знаменательных слов, лемма которых встречалась ранее в тексте
        tense_repetition (float): Доля пар соседних предложений с одинаковым преобладающим временем
        aspect_repetition (float): Доля пар соседних предложений с одинаковым преобладающим видом
        temporal_cohesion (float): Среднее повтора времени и вида
        connectors (float): Коннекторов на 1000 слов
        connectors_causal (float): Причинных коннекторов на 1000 слов
        connectors_adversative (float): Противительных коннекторов на 1000 слов
        connectors_concessive (float): Уступительных коннекторов на 1000 слов
        connectors_temporal (float): Временных коннекторов на 1000 слов
        connectors_additive (float): Аддитивных коннекторов на 1000 слов
        connectors_conditional (float): Условных коннекторов на 1000 слов
        connectors_reformulative (float): Переформулирующих коннекторов на 1000 слов
        connectors_primary (float): Первичных коннекторов на 1000 слов
        connectors_secondary (float): Вторичных коннекторов на 1000 слов

    Методы:
        get_stats: Получение вычисленных статистик связности текста
        print_stats: Отображение вычисленных статистик связности текста с описанием на экран

    Исключения:
        TypeError: Если передаваемое значение не является строкой или объектом Doc
        ValueError: Если в источнике данных отсутствуют слова
    """

    def __init__(
        self,
        source: str | Doc,
        sents_extractor: SentsExtractor | None = None,
        words_extractor: WordsExtractor | None = None,
        connectors: Mapping[str, tuple[str, str]] | None = None,
    ):
        sents: list[tuple[str, ...]]
        infos: list[list[WordInfo]]
        pos: list[list[str | None]]
        if isinstance(source, Doc) and source.has_annotation("SENT_START"):
            units = [list(iter_doc_units(sent)) for sent in source.sents]
            sents = [tuple(unit_text(unit) for unit in sent) for sent in units]
            if source.has_annotation("POS"):
                infos = [[unit_info(unit) for unit in sent] for sent in units]
                pos = [[unit_pos(unit) for unit in sent] for sent in units]
            else:
                infos = [[word_info(word) for word in sent] for sent in sents]
                pos = [[word_pos(word) for word in sent] for sent in sents]
        elif isinstance(source, str | Doc):
            text = source if isinstance(source, str) else source.text
            if not sents_extractor:
                sents_extractor = SentsExtractor()
            if not words_extractor:
                words_extractor = WordsExtractor()
            sents = [
                tuple(words_extractor.extract(sent)) for sent in sents_extractor.extract(text)
            ]
            infos = [[word_info(word) for word in sent] for sent in sents]
            pos = [[word_pos(word) for word in sent] for sent in sents]
        else:
            raise TypeError("Некорректный источник данных")
        self.words = tuple(sent for sent in sents if sent)
        if not self.words:
            raise ValueError("В источнике данных отсутствуют слова")
        infos = [sent for sent in infos if sent]
        self.n_sents = len(self.words)
        self.n_words = sum(len(sent) for sent in self.words)

        self.lemmas = tuple(tuple(info.lemma for info in sent) for sent in infos)
        nouns = [frozenset(info.lemma for info in sent if info.noun) for sent in infos]
        arguments = [frozenset(info.lemma for info in sent if info.argument) for sent in infos]
        content = [[info.lemma for info in sent if info.content] for sent in infos]
        content_sets = [frozenset(sent) for sent in content]
        tenses = [[info.tense for info in sent if info.tense] for sent in infos]
        aspects = [[info.aspect for info in sent if info.aspect] for sent in infos]

        self.n_nouns = sum(1 for sent in infos for info in sent if info.noun)
        self.n_pronouns = sum(1 for sent in infos for info in sent if info.pronoun)
        self.n_demonstratives = sum(1 for sent in infos for info in sent if info.demonstrative)
        self.n_content_words = sum(len(sent) for sent in content)
        self.n_given = count_given(content)

        noun_overlap = calc_overlaps(nouns)
        argument_overlap = calc_overlaps(arguments)
        content_overlap = calc_overlaps(content_sets)
        self.noun_overlap_adjacent = noun_overlap.adjacent
        self.noun_overlap_all = noun_overlap.all
        self.argument_overlap_adjacent = argument_overlap.adjacent
        self.argument_overlap_all = argument_overlap.all
        self.content_overlap_adjacent = content_overlap.adjacent
        self.content_overlap_all = content_overlap.all
        self.content_overlap_prop_adjacent = content_overlap.prop_adjacent
        self.content_overlap_prop_all = content_overlap.prop_all
        self.p_pronouns = self.n_pronouns / self.n_words
        self.pronoun_noun_ratio = safe_divide(self.n_pronouns, self.n_nouns, nan)
        self.p_demonstratives = self.n_demonstratives / self.n_words
        self.p_given = safe_divide(self.n_given, self.n_content_words, nan)
        self.tense_repetition = calc_repetition(tenses)
        self.aspect_repetition = calc_repetition(aspects)
        self.temporal_cohesion = fmean((self.tense_repetition, self.aspect_repetition))

        index = _normalize_connectors() if connectors is None else _normalize(connectors)
        pos = [sent for sent in pos if sent]
        self.connector_spans = tuple(
            connector
            for sent_index, (sent, sent_pos) in enumerate(zip(self.words, pos, strict=True))
            for connector in _find(sent, index, sent_index, sent_pos)
        )
        self.n_connectors = len(self.connector_spans)
        self.c_connectors = dict(
            sorted(Counter(connector.text for connector in self.connector_spans).items())
        )
        per_1000 = 1000 / self.n_words
        classes = Counter(connector.cls for connector in self.connector_spans)
        kinds = Counter(connector.kind for connector in self.connector_spans)
        self.connectors = self.n_connectors * per_1000
        self.connectors_causal = classes["causal"] * per_1000
        self.connectors_adversative = classes["adversative"] * per_1000
        self.connectors_concessive = classes["concessive"] * per_1000
        self.connectors_temporal = classes["temporal"] * per_1000
        self.connectors_additive = classes["additive"] * per_1000
        self.connectors_conditional = classes["conditional"] * per_1000
        self.connectors_reformulative = classes["reformulative"] * per_1000
        self.connectors_primary = kinds["primary"] * per_1000
        self.connectors_secondary = kinds["secondary"] * per_1000

    def get_stats(self) -> dict[str, float]:
        """
        Получение вычисленных статистик связности текста

        Вывод:
            dict[str, float]: Справочник вычисленных статистик связности текста
        """
        return {stat: getattr(self, stat) for stat in COHESION_STATS_DESC}

    def print_stats(self):
        """Отображение вычисленных статистик связности текста с описанием на экран"""
        print(f"{'Статистика':^58}|{'Значение':^10}")
        print("-" * 68)
        stats = self.get_stats()
        for stat, value in COHESION_STATS_DESC.items():
            print(f"{value:58}|{stats.get(stat):^10.2f}")


@cache
def load_connectors() -> dict[str, tuple[str, str]]:
    """
    Загрузка словаря коннекторов

    Описание:
        Файл resources/connectors.tsv: коннектор, класс из CONNECTOR_CLASSES
        и тип из CONNECTOR_TYPES; 317 коннекторов по классификации Криони, Никина
        и Филипповой (2008) со сверкой по маркерам Ru-RSTreebank, базе Рускон
        и списку причинных маркеров Тольдовой и др. (2018)

    Вывод:
        dict[str, tuple[str, str]]: Класс и тип по коннектору
    """
    connectors: dict[str, tuple[str, str]] = {}
    with CONNECTORS_FILE.open(encoding="utf-8") as file:
        next(file)
        for line in file:
            connector, cls, kind = line.rstrip("\n").split("\t")
            connectors[connector] = (cls, kind)
    return connectors


class ConnectorIndex(NamedTuple):
    """
    Индекс словаря коннекторов для поиска

    Атрибуты:
        entries (dict[str, tuple[str, str, str]]): Коннектор, класс и тип по нормализованному ключу
        by_first (dict[str, tuple[tuple[str, ...], ...]]): Шаблоны по первому слову,
            от длинных к коротким
    """

    entries: dict[str, tuple[str, str, str]]
    by_first: dict[str, tuple[tuple[str, ...], ...]]


def _normalize(connectors: Mapping[str, tuple[str, str]]) -> ConnectorIndex:
    """
    Построение индекса словаря коннекторов

    Описание:
        Ключ - словоформы в нижнем регистре без буквы ё через один пробел; для
        коннекторов с дефисом или точкой (во-первых, из-за, т.е.) добавляется ключ
        с пробелами вместо них, так как spaCy отделяет дефис, а WordsExtractor - точку;
        шаблоны группируются по первому слову
    """
    entries: dict[str, tuple[str, str, str]] = {}
    patterns: dict[str, list[tuple[str, ...]]] = {}
    for connector, (cls, kind) in connectors.items():
        if cls not in CONNECTOR_CLASSES or kind not in CONNECTOR_TYPES:
            raise ValueError(f"Неизвестный класс или тип коннектора: {cls}, {kind}")
        key = " ".join(normalize_yo(connector).split())
        split = " ".join(key.replace("-", " ").replace(".", " ").split())
        for variant in {key, split}:
            if not variant:
                continue
            entries[variant] = (connector, cls, kind)
            pattern = tuple(variant.split())
            patterns.setdefault(pattern[0], []).append(pattern)
    by_first = {
        first: tuple(sorted(set(group), key=len, reverse=True))
        for first, group in patterns.items()
    }
    return ConnectorIndex(entries, by_first)


@cache
def _normalize_connectors() -> ConnectorIndex:
    return _normalize(load_connectors())


def _find(
    words: Sequence[str],
    index: ConnectorIndex,
    sent_index: int,
    pos: Sequence[str | None] | None = None,
) -> list[Connector]:
    normalized = [normalize_yo(word) for word in words]
    found = []
    position = 0
    while position < len(normalized):
        for pattern in index.by_first.get(normalized[position], ()):
            end = position + len(pattern)
            if tuple(normalized[position:end]) != pattern:
                continue
            if (
                len(pattern) == 1
                and pos is not None
                and not _is_connector_pos(pattern[0], pos[position])
            ):
                continue
            text, cls, kind = index.entries[" ".join(pattern)]
            found.append(Connector(sent_index, position, end, text, cls, kind))
            position = end
            break
        else:
            position += 1
    return found


def _is_connector_pos(word: str, pos: str | None) -> bool:
    return pos is None or pos in CONNECTOR_POS or pos in CONNECTOR_POS_EXTRA.get(word, frozenset())


def find_connectors(
    words: Sequence[str],
    connectors: Mapping[str, tuple[str, str]] | None = None,
    sent_index: int = 0,
    pos: Sequence[str | None] | None = None,
) -> list[Connector]:
    """
    Поиск коннекторов в предложении

    Описание:
        Коннекторы ищутся по словоформам в нижнем регистре без буквы ё: в каждой
        позиции берется самый длинный («и все же» не распадается на «и»), найденные
        не пересекаются; дефис и точка внутри коннектора (во-первых, т.е.) могут
        быть отделены токенизатором. Если переданы части речи UD, однословный
        коннектор засчитывается только при части речи из CONNECTOR_POS или
        из CONNECTOR_POS_EXTRA для этого слова

    Аргументы:
        words (list[str]): Слова предложения
        connectors (dict[str, tuple[str, str]]): Словарь коннекторов - класс и тип
            по коннектору; если не задан, используется словарь из resources
        sent_index (int): Номер предложения для записи во вхождения
        pos (list[str]): Части речи UD слов предложения; без них части речи не проверяются

    Вывод:
        list[Connector]: Вхождения коннекторов в порядке слов

    Исключения:
        ValueError: Если в словаре встречается неизвестный класс или тип
    """
    index = _normalize_connectors() if connectors is None else _normalize(connectors)
    return _find(words, index, sent_index, pos)


def word_info(word: str) -> WordInfo:
    """
    Получение признаков слова по первому разбору pymorphy3

    Описание:
        Существительное - NOUN, местоимение - NPRO, Apro или лемма из DEMONSTRATIVE_LEMMAS,
        аргумент - NOUN или NPRO, знаменательное слово - по is_content_word, кроме
        указательных (столько - наречие для pymorphy3), время и вид - граммемы
        глагольной формы

    Аргументы:
        word (str): Слово

    Вывод:
        WordInfo: Признаки слова
    """
    parse = parse_word(word)
    tag = parse.tag
    demonstrative = parse.normal_form in DEMONSTRATIVE_LEMMAS
    return WordInfo(
        lemma=parse.normal_form,
        noun=tag.POS == "NOUN",
        pronoun=demonstrative or is_pronoun(word),
        demonstrative=demonstrative,
        argument=tag.POS in ("NOUN", "NPRO"),
        content=not demonstrative and is_content_word(word),
        tense=tag.tense,
        aspect=tag.aspect,
    )


def token_info(token: Token) -> WordInfo:
    """
    Получение признаков токена spaCy по разметке Universal Dependencies

    Описание:
        Существительное - NOUN или PROPN, местоимение - PRON, DET или лемма
        из DEMONSTRATIVE_LEMMAS, аргумент - NOUN, PROPN или PRON, знаменательное слово -
        NOUN, PROPN, ADJ, VERB, ADV (CONTENT_UD_POS), кроме указательных, время и вид -
        признаки Tense и Aspect
        Лемма берется из разбора pymorphy3 с частью речи токена (lemmatize), а не
        из token.lemma_: лемматизатор моделей ru_core_news возвращает словоформу
        для AUX и при расхождении признаков теггера и pymorphy3 (были, них, стихли)

    Аргументы:
        token (Token): Токен

    Вывод:
        WordInfo: Признаки слова
    """
    pos = token.pos_
    lemma = lemmatize(token.text, pos)
    tense = token.morph.get("Tense", [])
    aspect = token.morph.get("Aspect", [])
    demonstrative = lemma in DEMONSTRATIVE_LEMMAS
    return WordInfo(
        lemma=lemma,
        noun=pos in ("NOUN", "PROPN"),
        pronoun=demonstrative or pos in ("PRON", "DET"),
        demonstrative=demonstrative,
        argument=pos in ("NOUN", "PROPN", "PRON"),
        content=not demonstrative and pos in CONTENT_UD_POS,
        tense=tense[0] if tense else None,
        aspect=aspect[0] if aspect else None,
    )


def unit_text(unit: Sequence[Token]) -> str:
    """
    Текст слова из токенов iter_doc_units

    Аргументы:
        unit (list[Token]): Токены слова

    Вывод:
        str: Текст слова
    """
    return "".join(token.text for token in unit)


def unit_pos(unit: Sequence[Token]) -> str | None:
    """
    Часть речи UD слова из токенов iter_doc_units

    Описание:
        Обычное слово - по разметке токена, дефисное слово из нескольких токенов -
        по разбору pymorphy3 склеенного текста

    Аргументы:
        unit (list[Token]): Токены слова

    Вывод:
        str|None: Часть речи UD
    """
    if len(unit) == 1:
        return unit[0].pos_ or None
    return word_pos(unit_text(unit))


def unit_info(unit: Sequence[Token]) -> WordInfo:
    """
    Получение признаков слова из токенов iter_doc_units

    Описание:
        Обычное слово - по разметке токена (token_info), дефисное слово из нескольких
        токенов - по разбору pymorphy3 склеенного текста (word_info)

    Аргументы:
        unit (list[Token]): Токены слова

    Вывод:
        WordInfo: Признаки слова
    """
    return token_info(unit[0]) if len(unit) == 1 else word_info(unit_text(unit))


def is_pronoun(word: str) -> bool:
    """
    Проверка, является ли слово местоимением

    Описание:
        Местоимения-существительные (NPRO: он, себя, кто, это) и местоименные
        прилагательные (Apro: этот, который, мой, весь, каждый) по разметке pymorphy3

    Аргументы:
        word (str): Слово

    Вывод:
        bool: Результат проверки
    """
    tag = parse_word(word).tag
    return tag.POS == "NPRO" or "Apro" in tag.grammemes


def is_content_word(word: str) -> bool:
    """
    Проверка, является ли слово знаменательным

    Описание:
        Существительные, прилагательные, глаголы во всех формах (включая инфинитивы,
        причастия и деепричастия) и наречия по разметке pymorphy3, кроме местоименных
        (этот, такой, там, тогда) и вводных (конечно, например) слов

    Аргументы:
        word (str): Слово

    Вывод:
        bool: Результат проверки
    """
    tag = parse_word(word).tag
    return tag.POS in CONTENT_POS and not STOPWORD_GRAMMEMES & tag.grammemes


def calc_overlap(sets: Sequence[Collection[str]], adjacent: bool = True) -> float:
    """
    Вычисление доли пар предложений с общим элементом

    Описание:
        Бинарный повтор Coh-Metrix: пара предложений считается связанной, если
        у них есть хотя бы один общий элемент (лемма существительного, аргумента
        или знаменательного слова); доля таких пар среди соседних (CRFNO1, CRFAO1,
        CRFSO1) или среди всех пар предложений текста (CRFNOa, CRFAOa, CRFSOa)

    Аргументы:
        sets (list[set[str]]): Множества элементов каждого предложения
        adjacent (bool): Считать только соседние пары, иначе все пары

    Вывод:
        float: Доля пар с общим элементом, nan для текста короче двух предложений
    """
    frozen = [frozenset(elements) for elements in sets]
    n_sents = len(frozen)
    if n_sents < 2:
        return nan
    pairs = pairwise(frozen) if adjacent else combinations(frozen, 2)
    n_pairs = n_sents - 1 if adjacent else n_sents * (n_sents - 1) // 2
    return sum(1 for first, second in pairs if not first.isdisjoint(second)) / n_pairs


def calc_proportional_overlap(sets: Sequence[Collection[str]], adjacent: bool = True) -> float:
    """
    Вычисление средней доли общих элементов в парах предложений

    Описание:
        Пропорциональный повтор Coh-Metrix (CRFCWO1, CRFCWOa): для пары предложений
        считается коэффициент Дайса множеств лемм 2·|A ∩ B| / (|A| + |B|), пара
        без элементов получает 0; результат усредняется по соседним или всем парам

    Аргументы:
        sets (list[set[str]]): Множества элементов каждого предложения
        adjacent (bool): Считать только соседние пары, иначе все пары

    Вывод:
        float: Средняя доля общих элементов, nan для текста короче двух предложений
    """
    frozen = [frozenset(elements) for elements in sets]
    n_sents = len(frozen)
    if n_sents < 2:
        return nan
    pairs = pairwise(frozen) if adjacent else combinations(frozen, 2)
    n_pairs = n_sents - 1 if adjacent else n_sents * (n_sents - 1) // 2
    return sum(dice(first, second) for first, second in pairs) / n_pairs


def dice(first: frozenset[str], second: frozenset[str]) -> float:
    """
    Вычисление коэффициента Дайса двух множеств

    Аргументы:
        first (frozenset[str]): Первое множество
        second (frozenset[str]): Второе множество

    Вывод:
        float: Коэффициент 2·|A ∩ B| / (|A| + |B|), 0 для двух пустых множеств
    """
    return safe_divide(2 * len(first & second), len(first) + len(second))


def calc_overlaps(sets: Sequence[Collection[str]]) -> Overlap:
    """
    Вычисление бинарного и пропорционального повторов по соседним и всем парам предложений

    Описание:
        Дает те же значения, что calc_overlap и calc_proportional_overlap, но без перебора
        всех пар предложений: класс CohesionStats считает так все повторы
        Соседние пары обходятся напрямую; число всех пар с общим элементом считается
        по битовым маскам вхождений элементов в предложения, а сумма коэффициентов
        Дайса по всем парам - по гистограммам длин предложений для каждого элемента,
        так что время растет линейно с числом вхождений, а не квадратично
        с числом предложений

    Аргументы:
        sets (list[set[str]]): Множества элементов каждого предложения

    Вывод:
        Overlap: Доли пар с общим элементом и средние коэффициенты Дайса,
            nan для текста короче двух предложений
    """
    frozen = [frozenset(elements) for elements in sets]
    n_sents = len(frozen)
    if n_sents < 2:
        return Overlap(nan, nan, nan, nan)
    n_all = n_sents * (n_sents - 1) // 2
    return Overlap(
        sum(1 for first, second in pairwise(frozen) if not first.isdisjoint(second))
        / (n_sents - 1),
        _count_sharing_pairs(frozen) / n_all,
        sum(dice(first, second) for first, second in pairwise(frozen)) / (n_sents - 1),
        _sum_dice(frozen) / n_all,
    )


def _count_sharing_pairs(sets: Sequence[frozenset[str]], block_size: int = 4096) -> int:
    """
    Число пар предложений с общим элементом по битовым маскам вхождений

    Описание:
        Предложения обрабатываются блоками: для каждого элемента строится маска
        предложений блока, где он встречается, объединение масок элементов предложения
        i дает все предложения блока, с которыми оно связано, и остается посчитать
        биты правее i; память ограничена размером блока
    """
    total = 0
    for start in range(0, len(sets), block_size):
        end = min(start + block_size, len(sets))
        masks: dict[str, int] = {}
        for j in range(start, end):
            bit = 1 << (j - start)
            for element in sets[j]:
                masks[element] = masks.get(element, 0) | bit
        for i in range(end):
            union = 0
            for element in sets[i]:
                union |= masks.get(element, 0)
            if i >= start:
                union >>= i - start + 1
            total += union.bit_count()
    return total


def _sum_dice(sets: Sequence[frozenset[str]]) -> float:
    """
    Сумма коэффициентов Дайса по всем парам предложений по гистограммам длин

    Описание:
        Пара предложений длин k и l с общим элементом дает 2/(k + l) за каждый общий
        элемент, поэтому для каждого элемента достаточно знать, сколько содержащих его
        предложений имеют каждую длину: сумма по парам внутри элемента равна
        (h·W·h - h·diag(W)) / 2, где h - гистограмма длин, W[k, l] = 2/(k + l)
        Элементы из одного предложения пар не образуют и пропускаются
    """
    sizes = sorted({len(elements) for elements in sets if elements})
    columns = {size: column for column, size in enumerate(sizes)}
    postings: dict[str, list[int]] = {}
    for elements in sets:
        if not elements:
            continue
        column = columns[len(elements)]
        for element in elements:
            postings.setdefault(element, []).append(column)
    rows = [row for row in postings.values() if len(row) > 1]
    if not rows:
        return 0.0
    histograms = np.zeros((len(rows), len(sizes)))
    for index, row in enumerate(rows):
        np.add.at(histograms[index], row, 1)
    lengths = np.array(sizes, dtype=float)
    weights = 2 / (lengths[:, None] + lengths[None, :])
    full = np.einsum("ik,kl,il->", histograms, weights, histograms)
    diagonal = (histograms * np.diag(weights)).sum()
    return float((full - diagonal) / 2)


def count_given(sents: Sequence[Sequence[str]]) -> int:
    """
    Вычисление количества данных элементов - уже встречавшихся ранее в тексте

    Описание:
        Элемент считается данным (given), если та же лемма встречалась раньше
        в любом предложении, включая текущее; первое вхождение - новое

    Аргументы:
        sents (list[list[str]]): Леммы каждого предложения в порядке текста

    Вывод:
        int: Количество данных элементов
    """
    seen: set[str] = set()
    given = 0
    for sent in sents:
        for lemma in sent:
            if lemma in seen:
                given += 1
            seen.add(lemma)
    return given


def dominant(values: Sequence[str]) -> str | None:
    """
    Получение преобладающего значения

    Описание:
        Самое частое значение, при равенстве - встретившееся первым

    Аргументы:
        values (list[str]): Значения

    Вывод:
        str|None: Преобладающее значение, None для пустого списка
    """
    if not values:
        return None
    return Counter(values).most_common(1)[0][0]


def calc_repetition(sents: Sequence[Sequence[str]]) -> float:
    """
    Вычисление доли пар соседних предложений с одинаковым преобладающим значением

    Описание:
        Повтор времени и вида Coh-Metrix (SMTEMP): для каждого предложения берется
        преобладающее значение признака глаголов, пара соседних предложений считается
        согласованной при совпадении; пары, где хотя бы у одного предложения
        нет глаголов с признаком, пропускаются

    Аргументы:
        sents (list[list[str]]): Значения признака глаголов каждого предложения

    Вывод:
        float: Доля согласованных пар, nan если нет ни одной пары с признаком
    """
    pairs = [
        (first, second)
        for first, second in pairwise(dominant(sent) for sent in sents)
        if first and second
    ]
    if not pairs:
        return nan
    return sum(1 for first, second in pairs if first == second) / len(pairs)
