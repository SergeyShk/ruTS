from collections import Counter
from collections.abc import Mapping, Sequence
from functools import cache, lru_cache
from math import nan
from statistics import fmean
from typing import NamedTuple

import anyts
from anyts.cohesion import (
    Overlap as Overlap,
    calc_overlap as calc_overlap,
    calc_overlaps as calc_overlaps,
    calc_proportional_overlap as calc_proportional_overlap,
    calc_repetition as calc_repetition,
    count_given as count_given,
    dice as dice,
    dominant as dominant,
)
from anyts.utils import check_words, iter_doc_units, safe_divide
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
from .exceptions import ParameterError, SourceError, SourceTypeError
from .extractors import SentsExtractor, WordsExtractor
from .morph_stats import tag_to_ud_pos, word_to_ud
from .utils import get_morph_analyzer, lemmatize, normalize_yo, parse_word

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
        для строки и Doc без разметки - из первого разбора pymorphy3. Слова Doc
        берутся из токенов, дефисные слова, разрезанные spaCy, склеиваются
        (iter_doc_units); Doc без границ предложений разбивается на предложения
        через sents_extractor по тексту (split_doc_units)
        Знаменательные слова: по pymorphy3 - CONTENT_POS без STOPWORD_GRAMMEMES,
        по UD - CONTENT_UD_POS; местоимения: по pymorphy3 - NPRO и Apro, по UD - PRON
        и DET; слова с леммой из DEMONSTRATIVE_LEMMAS считаются местоимениями
        Коннекторы (потому что, однако, затем, иными словами) ищутся по словоформам
        в каждом предложении по словарю resources/connectors.tsv с классами
        по Криони, Никину и Филипповой (2008) и типом - первичные (союзы и наречия)
        или вторичные (лексикализованные обороты); плотность считается на 1000 слов
        Однословный коннектор засчитывается только при части речи из CONNECTOR_POS
        (союз, частица, наречие, предлог, междометие) или из CONNECTOR_POS_EXTRA
        для отдельных слов (словом, главное, допустим, точнее) - по разметке Doc,
        так «раз» и «значит» как существительное и глагол не считаются; без разметки
        слово проходит, если подходящая часть речи есть хотя бы в одном разборе
        pymorphy3 (connector_pos)
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
        SourceTypeError: Если передаваемое значение не является строкой или объектом Doc
        SourceError: Если в источнике данных отсутствуют слова
    """

    def __init__(
        self,
        source: str | Doc,
        sents_extractor: SentsExtractor | None = None,
        words_extractor: WordsExtractor | None = None,
        connectors: Mapping[str, tuple[str, str]] | None = None,
    ):
        if sents_extractor is not None and not isinstance(sents_extractor, anyts.SentsExtractor):
            raise SourceTypeError("Экстрактор предложений должен быть SentsExtractor")
        if words_extractor is not None and not isinstance(words_extractor, anyts.WordsExtractor):
            raise SourceTypeError("Экстрактор слов должен быть WordsExtractor")
        sents: list[tuple[str, ...]]
        infos: list[list[WordInfo]]
        pos: list[list[str | None]]
        if isinstance(source, Doc):
            if source.has_annotation("SENT_START"):
                units = [list(iter_doc_units(sent, join_hyphens=True)) for sent in source.sents]
            else:
                units = split_doc_units(source, sents_extractor or SentsExtractor())
            sents = [tuple(unit_text(unit) for unit in sent) for sent in units]
            if source.has_annotation("POS"):
                infos = [[unit_info(unit) for unit in sent] for sent in units]
                pos = [[unit_pos(unit) for unit in sent] for sent in units]
            else:
                infos = [[word_info(word) for word in sent] for sent in sents]
                pos = [[connector_pos(word) for word in sent] for sent in sents]
        elif isinstance(source, str):
            if not sents_extractor:
                sents_extractor = SentsExtractor()
            if not words_extractor:
                words_extractor = WordsExtractor()
            sents = [
                tuple(words_extractor.extract(sent)) for sent in sents_extractor.extract(source)
            ]
            infos = [[word_info(word) for word in sent] for sent in sents]
            pos = [[connector_pos(word) for word in sent] for sent in sents]
        else:
            raise SourceTypeError("Некорректный источник данных")
        self.words = tuple(sent for sent in sents if sent)
        if not self.words:
            raise SourceError("В источнике данных отсутствуют слова")
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
            print(f"{value:58}|{stats[stat]:^10.2f}")


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
            raise ParameterError(f"Неизвестный класс или тип коннектора: {cls}, {kind}")
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


@lru_cache(maxsize=131072)
def connector_pos(word: str) -> str | None:
    """
    Часть речи UD слова по pymorphy3 для проверки коннектора

    Описание:
        Из разборов pymorphy3 берется первый с частью речи, подходящей коннектору
        (CONNECTOR_POS или CONNECTOR_POS_EXTRA для этого слова), иначе часть речи
        первого разбора: у «раз» и «отчего» первый разбор - существительное
        и прилагательное, союз только в следующих. Результаты кэшируются по словоформе

    Аргументы:
        word (str): Слово

    Вывод:
        str|None: Часть речи UD
    """
    normalized = normalize_yo(word)
    poses = [
        tag_to_ud_pos(parse.tag, parse.normal_form, word)
        for parse in get_morph_analyzer().parse(word)
    ]
    return next((pos for pos in poses if _is_connector_pos(normalized, pos)), poses[0])


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
        ParameterError: Если в словаре встречается неизвестный класс или тип
    """
    check_words(words)
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
    tense = token.morph.get("Tense", [])
    aspect = token.morph.get("Aspect", [])
    return ud_info(
        token.text, token.pos_, tense[0] if tense else None, aspect[0] if aspect else None
    )


def ud_info(word: str, pos: str, tense: str | None, aspect: str | None) -> WordInfo:
    """
    Получение признаков слова по части речи и признакам Universal Dependencies

    Описание:
        Как в token_info: лемма - из разбора pymorphy3 с частью речи (lemmatize)

    Аргументы:
        word (str): Слово
        pos (str): Часть речи UD
        tense (str): Время UD
        aspect (str): Вид UD

    Вывод:
        WordInfo: Признаки слова
    """
    lemma = lemmatize(word, pos)
    demonstrative = lemma in DEMONSTRATIVE_LEMMAS
    return WordInfo(
        lemma=lemma,
        noun=pos in ("NOUN", "PROPN"),
        pronoun=demonstrative or pos in ("PRON", "DET"),
        demonstrative=demonstrative,
        argument=pos in ("NOUN", "PROPN", "PRON"),
        content=not demonstrative and pos in CONTENT_UD_POS,
        tense=tense,
        aspect=aspect,
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


def split_doc_units(source: Doc, sents_extractor: SentsExtractor) -> list[list[list[Token]]]:
    """
    Разбиение слов объекта Doc без границ предложений по предложениям

    Описание:
        Предложения извлекаются sents_extractor из текста и находятся в нем
        по порядку; слово относится к предложению, в границах которого лежит его
        первый токен. Слова вне найденных предложений (отброшенных экстрактором
        по длине) не учитываются, как и для строки: если экстрактор не нашел
        ни одного предложения, слов нет

    Аргументы:
        source (Doc): Объект Doc
        sents_extractor (SentsExtractor): Инструмент для извлечения предложений

    Вывод:
        list[list[list[Token]]]: Токены каждого слова каждого предложения
    """
    text = source.text
    spans = []
    cursor = 0
    for sent in sents_extractor.extract(text):
        start = text.find(sent, cursor)
        if start != -1:
            spans.append((start, start + len(sent)))
            cursor = start + len(sent)
    if not spans:
        return []
    units: list[list[list[Token]]] = [[] for _ in spans]
    index = 0
    for unit in iter_doc_units(source, join_hyphens=True):
        position = unit[0].idx
        while index + 1 < len(spans) and spans[index + 1][0] <= position:
            index += 1
        if spans[index][0] <= position < spans[index][1]:
            units[index].append(unit)
    return units


def unit_pos(unit: Sequence[Token]) -> str | None:
    """
    Часть речи UD слова из токенов iter_doc_units

    Описание:
        Обычное слово - по разметке токена, дефисное слово из нескольких токенов -
        по разбору pymorphy3 склеенного текста (connector_pos)

    Аргументы:
        unit (list[Token]): Токены слова

    Вывод:
        str|None: Часть речи UD
    """
    if len(unit) == 1:
        return unit[0].pos_ or None
    return connector_pos(unit_text(unit))


def unit_info(unit: Sequence[Token]) -> WordInfo:
    """
    Получение признаков слова из токенов iter_doc_units

    Описание:
        Обычное слово - по разметке токена (token_info), дефисное слово из нескольких
        токенов - по разбору pymorphy3 склеенного текста, переведенному в UD
        (word_to_ud), чтобы время и вид сравнивались с разметкой остальных слов

    Аргументы:
        unit (list[Token]): Токены слова

    Вывод:
        WordInfo: Признаки слова
    """
    if len(unit) == 1:
        return token_info(unit[0])
    text = unit_text(unit)
    features = word_to_ud(text)
    return ud_info(text, features["pos"] or "", features["tense"], features["aspect"])


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
