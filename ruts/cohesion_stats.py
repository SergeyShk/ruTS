from collections import Counter
from collections.abc import Collection, Sequence
from itertools import combinations, pairwise
from math import nan
from statistics import fmean
from typing import NamedTuple

import numpy as np
from spacy.tokens import Doc, Token

from .constants import (
    COHESION_STATS_DESC,
    CONTENT_POS,
    CONTENT_UD_POS,
    DEMONSTRATIVE_LEMMAS,
    STOPWORD_GRAMMEMES,
)
from .extractors import SentsExtractor, WordsExtractor
from .utils import lemmatize, parse_word, safe_divide


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
        леммы, части речи, время и вид берутся из token.lemma_, token.pos_
        и token.morph (без лемм - из разбора pymorphy3 с частью речи токена),
        для строки и Doc без разметки - из первого разбора pymorphy3
        Знаменательные слова: по pymorphy3 - CONTENT_POS без STOPWORD_GRAMMEMES,
        по UD - CONTENT_UD_POS; местоимения: по pymorphy3 - NPRO и Apro, по UD - PRON
        и DET; слова с леммой из DEMONSTRATIVE_LEMMAS считаются местоимениями
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
        'content_overlap_prop_all': 0.1865079365079365,
        'p_pronouns': 0.14285714285714285,
        'pronoun_noun_ratio': 0.5,
        'p_demonstratives': 0.047619047619047616,
        'p_given': 0.2857142857142857,
        'tense_repetition': 0.6666666666666666,
        'aspect_repetition': 0.3333333333333333,
        'temporal_cohesion': 0.5}
        >>> cs.lemmas[1]
        ('он', 'смотреть', 'на', 'птица')

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        sents_extractor (SentsExtractor): Инструмент для извлечения предложений
        words_extractor (WordsExtractor): Инструмент для извлечения слов

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
    ):
        sents: list[tuple[str, ...]]
        infos: list[list[WordInfo]]
        if isinstance(source, Doc):
            tokens = [
                [word for word in sent if not word.is_punct and not word.is_space]
                for sent in source.sents
            ]
            sents = [tuple(word.text for word in sent) for sent in tokens]
            if source.has_annotation("POS"):
                infos = [[token_info(word) for word in sent] for sent in tokens]
            else:
                infos = [[word_info(word) for word in sent] for sent in sents]
        elif isinstance(source, str):
            if not sents_extractor:
                sents_extractor = SentsExtractor()
            if not words_extractor:
                words_extractor = WordsExtractor()
            sents = [
                tuple(words_extractor.extract(sent)) for sent in sents_extractor.extract(source)
            ]
            infos = [[word_info(word) for word in sent] for sent in sents]
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
        Лемма берется из token.lemma_ в нижнем регистре, а если лемматизатора
        в пайплайне нет - из разбора pymorphy3 с частью речи токена (lemmatize)

    Аргументы:
        token (Token): Токен

    Вывод:
        WordInfo: Признаки слова
    """
    pos = token.pos_
    lemma = token.lemma_.lower() if token.lemma_ else lemmatize(token.text, pos)
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
