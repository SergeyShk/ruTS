from __future__ import annotations

import unicodedata
from collections import deque
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING

import anyts.corpus
from anyts.corpus.kwic import (
    Concordance as Concordance,
    format_kwic as format_kwic,
    print_kwic as print_kwic,
)

from ..utils import (
    analyze_words,
    iter_text_sents,
    iter_text_words,
    lemmatize,
    normalize_yo,
    parse_all,
    strip_marks,
)

if TYPE_CHECKING:
    from spacy.tokens import Doc, Token


def kwic(
    source: str | Doc,
    keyword: str,
    window: int = 5,
    by_lemma: bool = False,
    ignore_case: bool = True,
) -> list[Concordance]:
    """
    Построение конкорданса KWIC (keyword in context)

    Описание:
        Ищутся вхождения слова или словосочетания среди слов текста: по словоформе
        без учета регистра и буквы ё, с учетом регистра или по лемме ruMorph
        («кота» находится по «кот»): у слова строки - разбора в контексте предложения,
        у слова Doc с разметкой частей речи - с частью речи токена (lemmatize), так
        «стали» находится по «сталь» или «стать» в зависимости от соседних слов; слово
        ключевого слова совпадает по любой лемме своих разборов. Текст и ключевое слово режутся
        на слова одинаково (anySeg), знаки препинания и символы словами не считаются,
        знаки ударения и мягкие переносы при сравнении снимаются (strip_marks),
        точка сокращения не учитывается: «руб.» в тексте находится по «руб» и «руб.».
        Словосочетание не переходит через конец абзаца или предложения (границы Doc
        или anySeg), если такой границы нет в самом ключевом слове. Контекст -
        window слов слева и справа, как они записаны в тексте, со знаками препинания
        между ними; пробельные символы схлопываются в один пробел; вхождения
        не пересекаются

    Аргументы:
        source (str|Doc): Текст или объект Doc
        keyword (str): Слово или словосочетание
        window (int): Число слов контекста с каждой стороны
        by_lemma (bool): Сравнивать леммы, а не словоформы
        ignore_case (bool): Не учитывать регистр и букву ё при сравнении словоформ

    Вывод:
        list[Concordance]: Вхождения по порядку в тексте

    Исключения:
        SourceTypeError: Если источник данных не строка и не объект Doc или ключевое
            слово не строка
        ParameterError: Если в ключевом слове нет слов или окно не целое число
            или отрицательно

    Пример использования:
        >>> from ruts.corpus import kwic
        >>> text = "Кот спит. Коты играют в саду."
        >>> [line.keyword for line in kwic(text, "кот", by_lemma=True)]
        ['Кот', 'Коты']
    """
    # Свертка ядра без ignore_case не вызывается, а знаки снимать нужно и с учетом регистра
    case_sensitive = not by_lemma and not ignore_case
    return anyts.corpus.kwic(
        source,
        keyword,
        window,
        by_lemma,
        ignore_case or case_sensitive,
        tokenize=iter_text_words,
        lemmatize=_string_lemmatizer(source) if by_lemma and isinstance(source, str) else _lemma,
        fold=_fold_marks if case_sensitive else _fold,
        join_hyphens=True,
        sentenize=iter_text_sents,
    )


def _fold_marks(word: str) -> str:
    """Слово без знаков ударения, мягких переносов и точки сокращения, с учетом регистра"""
    return strip_marks(word).removesuffix(".")


def _fold(word: str) -> str:
    """Слово без учета регистра и буквы ё, без точки сокращения"""
    return normalize_yo(word).removesuffix(".")


def _lemma(word: str, tokens: Sequence[Token]) -> str | tuple[str, ...]:
    """Лемма ruMorph с частью речи токена для слова Doc из одного токена; у слова
    ключа (без токенов) контекста нет - леммы всех его разборов"""
    if not tokens:
        return _key_lemmas(word)
    return lemmatize(word, tokens[0].pos_ if len(tokens) == 1 else "")


def _key_lemmas(word: str) -> tuple[str, ...]:
    """Леммы всех разборов слова ключа"""
    return tuple(dict.fromkeys(analysis.lemma for analysis in parse_all(word)))


def _string_lemmatizer(text: str) -> Callable[[str, Sequence[Token]], str | tuple[str, ...]]:
    """Леммы слов строки в контексте предложений (analyze_words): ядро разбирает слова
    текста по порядку, по разу каждое, а затем слова ключа"""
    positions = [(start, word) for start, _, word in iter_text_words(text)]
    queue = deque(
        zip((word for _, word in positions), analyze_words(positions, text), strict=True)
    )

    def lemma(word: str, tokens: Sequence[Token]) -> str | tuple[str, ...]:
        if not queue:
            return _key_lemmas(word)
        if unicodedata.normalize("NFC", queue[0][0]) == word:
            _, analysis = queue.popleft()
            if analysis is not None:
                return analysis.lemma
        return lemmatize(word)

    return lemma
