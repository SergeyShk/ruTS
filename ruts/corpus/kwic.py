from collections.abc import Sequence

import anyts.corpus
from anyts.corpus.kwic import (
    Concordance as Concordance,
    format_kwic as format_kwic,
    print_kwic as print_kwic,
)
from spacy.tokens import Doc, Token

from ..utils import iter_text_sents, iter_text_words, lemmatize, normalize_yo, strip_marks


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
        без учета регистра и буквы ё, с учетом регистра или по лемме pymorphy3
        («кота» находится по «кот»); для Doc с разметкой частей речи лемма слова
        берется с частью речи токена (lemmatize), так «стали» находится по «сталь»
        или «стать» в зависимости от разметки. Текст и ключевое слово режутся
        на слова одинаково (razdel), знаки препинания и символы словами не считаются,
        знаки ударения и мягкие переносы при сравнении снимаются (strip_marks).
        Словосочетание не переходит через конец абзаца или предложения (границы Doc
        или razdel), если такой границы нет в самом ключевом слове. Контекст -
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
        lemmatize=_lemma,
        fold=strip_marks if case_sensitive else normalize_yo,
        join_hyphens=True,
        sentenize=iter_text_sents,
    )


def _lemma(word: str, tokens: Sequence[Token]) -> str:
    """Лемма pymorphy3 с частью речи токена для слова Doc из одного токена"""
    return lemmatize(word, tokens[0].pos_ if len(tokens) == 1 else "")
