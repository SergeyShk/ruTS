import re
from collections.abc import Iterable, Iterator, Sequence
from functools import lru_cache

import pymorphy3
from anyts.utils import check_words, is_punctuation
from razdel import tokenize
from spacy.language import Language
from spacy.tokenizer import Tokenizer

from .constants import (
    LETTER,
    TOKENIZER_INFIXES,
    TOKENIZER_PREFIXES,
    TOKENIZER_SUFFIXES,
    UD_TO_OPENCORPORA_POS,
    VERBAL_NOUN_LEMMAS,
    VERBAL_NOUN_SUFFIXES,
)

DASHES = frozenset("-—–―")
BYTE_ORDER_MARK = "\ufeff"
GLUED_DASHES = re.compile(
    rf"^(?:-+|[—–―]+)(?={LETTER})|(?<={LETTER})(?:-+|[—–―]+)$|(?<={LETTER}{{2}})[—–―]+(?={LETTER})"
)


@lru_cache(maxsize=1)
def get_morph_analyzer() -> pymorphy3.MorphAnalyzer:
    """
    Получение морфологического анализатора pymorphy3

    Вывод:
        MorphAnalyzer: Морфологический анализатор
    """
    return pymorphy3.MorphAnalyzer()


@lru_cache(maxsize=131072)
def parse_word(word: str) -> pymorphy3.analyzer.Parse:
    """
    Морфологический разбор словоформы с кэшированием

    Описание:
        Возвращает первый (наиболее вероятный) разбор pymorphy3
        Результаты кэшируются по словоформе: в тексте на 75 тысяч токенов
        всего около 14 тысяч уникальных форм, повторный разбор не нужен

    Аргументы:
        word (str): Словоформа

    Вывод:
        Parse: Разбор словоформы
    """
    return get_morph_analyzer().parse(word)[0]


@lru_cache(maxsize=131072)
def lemmatize(word: str, pos: str = "") -> str:
    """
    Лемматизация словоформы pymorphy3 с учетом части речи Universal Dependencies

    Описание:
        Среди разборов словоформы выбирается первый, часть речи которого соответствует
        заданной части речи UD по таблице UD_TO_OPENCORPORA_POS, как делает
        лемматизатор spaCy для русского языка: «стали» с NOUN - сталь, с VERB - стать
        Без части речи или без подходящего разбора берется первый разбор

    Аргументы:
        word (str): Словоформа
        pos (str): Часть речи UD

    Вывод:
        str: Лемма
    """
    parses = get_morph_analyzer().parse(word)
    allowed = UD_TO_OPENCORPORA_POS.get(pos, frozenset())
    parse = next((parse for parse in parses if parse.tag.POS in allowed), parses[0])
    return str(parse.normal_form)


def is_verbal_noun(lemma: str) -> bool:
    """
    Проверка, является ли лемма отглагольным существительным по суффиксу

    Описание:
        Суффиксы из VERBAL_NOUN_SUFFIXES: -ние, -нье, -тие, -тье, -ствие, -ция
        (повышение, участие, содействие, реализация) или лемма из VERBAL_NOUN_LEMMAS
        (производство, руководство, строительство); суффикс -ство в список не входит,
        так как в основном не отглагольный (правительство, общество, средство)
        Эвристика захватывает и неотглагольные слова с теми же суффиксами (здание)

    Аргументы:
        lemma (str): Лемма существительного

    Вывод:
        bool: Результат проверки
    """
    lemma = normalize_yo(lemma)
    return lemma.endswith(VERBAL_NOUN_SUFFIXES) or lemma in VERBAL_NOUN_LEMMAS


def normalize_yo(word: str) -> str:
    """
    Замена буквы ё на е в нижнем регистре

    Аргументы:
        word (str): Слово

    Вывод:
        str: Слово без буквы ё
    """
    return word.lower().replace("ё", "е")


def find_phrases(words: Sequence[str], phrases: Iterable[str]) -> list[tuple[int, int]]:
    """
    Поиск словосочетаний в последовательности слов

    Описание:
        Слова и словосочетания сравниваются в нижнем регистре без буквы ё; в каждой
        позиции выбирается самое длинное словосочетание, найденные не пересекаются
        Словосочетания индексируются по первому слову, так что в каждой позиции
        сравниваются только начинающиеся с этого слова

    Аргументы:
        words (list[str]): Слова текста
        phrases (list[str]): Словосочетания через пробел

    Вывод:
        list[tuple[int, int]]: Границы найденных словосочетаний как срезы words;
            пустые словосочетания пропускаются
    """
    check_words(words)
    patterns = sorted(
        {pattern for phrase in phrases if (pattern := tuple(normalize_yo(phrase).split()))},
        key=len,
        reverse=True,
    )
    by_first: dict[str, list[tuple[str, ...]]] = {}
    for pattern in patterns:
        by_first.setdefault(pattern[0], []).append(pattern)
    normalized = [normalize_yo(word) for word in words]
    spans = []
    position = 0
    while position < len(normalized):
        for pattern in by_first.get(normalized[position], ()):
            end = position + len(pattern)
            if tuple(normalized[position:end]) == pattern:
                spans.append((position, end))
                position = end
                break
        else:
            position += 1
    return spans


def iter_tokens(text: str) -> Iterator[tuple[int, int, str]]:
    """
    Токенизация строки razdel с отделением тире, приклеенных к словам

    Описание:
        razdel оставляет в слове приклеенные тире реплик и ремарок (-Нет -сказал он,
        —сказал); они становятся отдельными токенами, а дефис внутри слова (кто-то),
        минус перед числом и тире в сокращенном имени (N—ский) остаются; метка порядка
        байтов (BOM) в начале токена отбрасывается

    Аргументы:
        text (str): Строка текста

    Вывод:
        generator[tuple[int, int, str]]: Позиция первого символа, позиция за последним
            символом и текст каждого токена
    """
    for token in tokenize(text):
        word = token.text.lstrip(BYTE_ORDER_MARK)
        if not word:
            continue
        offset = token.stop - len(word)
        if not DASHES.intersection(word):
            yield offset, token.stop, word
            continue
        start = 0
        for match in GLUED_DASHES.finditer(word):
            if match.start() > start:
                yield offset + start, offset + match.start(), word[start : match.start()]
            yield offset + match.start(), offset + match.end(), match.group()
            start = match.end()
        if start < len(word):
            yield offset + start, token.stop, word[start:]


def iter_text_words(text: str) -> Iterator[tuple[int, int, str]]:
    """
    Извлечение слов с позициями из строки

    Описание:
        Токены iter_tokens, знаки препинания отбрасываются как в WordsExtractor

    Аргументы:
        text (str): Строка текста

    Вывод:
        generator[tuple[int, int, str]]: Позиция первого символа, позиция за последним
            символом и текст каждого слова
    """
    for start, stop, token in iter_tokens(text):
        if not is_punctuation(token):
            yield start, stop, token


def count_words_by_spans(starts: Sequence[int], spans: Sequence[tuple[int, int]]) -> list[int]:
    """
    Число слов в каждом отрезке текста по позициям слов и границам отрезков

    Аргументы:
        starts (list[int]): Позиции первых символов слов по порядку
        spans (list[tuple[int, int]]): Границы отрезков по порядку - начало и позиция
            за концом

    Вывод:
        list[int]: Число слов в каждом отрезке; отрезки без слов пропускаются
    """
    lengths = []
    index = 0
    for start, stop in spans:
        count = 0
        while index < len(starts) and starts[index] < stop:
            count += starts[index] >= start
            index += 1
        lengths.append(count)
    return [length for length in lengths if length]


def add_dash_rules(nlp: Language) -> None:
    """
    Добавление в токенизатор пайплайна spaCy правил для тире реплик

    Описание:
        С правилами TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES и TOKENIZER_INFIXES
        слова Doc совпадают со словами строки (iter_tokens); повторно правила
        не добавляются. Компоненты ruTS добавляют их в свой пайплайн сами

    Аргументы:
        nlp (Language): Пайплайн, в токенизатор которого добавляются правила

    Примеры использования:
        >>> import spacy
        >>> from ruts.utils import add_dash_rules
        >>> nlp = spacy.blank("ru")
        >>> [token.text for token in nlp("-Нет -сказал он.")]
        ['-Нет', '-сказал', 'он', '.']
        >>> add_dash_rules(nlp)
        >>> [token.text for token in nlp("-Нет -сказал он.")]
        ['-', 'Нет', '-', 'сказал', 'он', '.']
    """
    tokenizer = nlp.tokenizer
    if not isinstance(tokenizer, Tokenizer):
        return
    prefixes = _extend_rules(tokenizer.prefix_search, [f"^{rule}" for rule in TOKENIZER_PREFIXES])
    suffixes = _extend_rules(tokenizer.suffix_search, [f"{rule}$" for rule in TOKENIZER_SUFFIXES])
    infixes = _extend_rules(tokenizer.infix_finditer, list(TOKENIZER_INFIXES))
    if prefixes is not None:
        tokenizer.prefix_search = prefixes.search
    if suffixes is not None:
        tokenizer.suffix_search = suffixes.search
    if infixes is not None:
        tokenizer.infix_finditer = infixes.finditer


def _extend_rules(method: object, rules: list[str]) -> re.Pattern[str] | None:
    """Регулярное выражение токенизатора с добавленными правилами, которых в нем нет"""
    if method is None:
        return re.compile("|".join(rules))
    pattern = getattr(getattr(method, "__self__", None), "pattern", None)
    if not isinstance(pattern, str):
        return None
    missing = [rule for rule in rules if rule not in pattern]
    return re.compile("|".join([pattern, *missing]))
