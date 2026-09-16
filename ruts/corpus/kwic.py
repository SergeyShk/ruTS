from collections.abc import Sequence
from typing import NamedTuple

from spacy.tokens import Doc

from ..utils import iter_doc_words, iter_text_words, lemmatize, normalize_yo


class Concordance(NamedTuple):
    """
    Строка конкорданса - вхождение ключевого слова с контекстом

    Атрибуты:
        start (int): Позиция первого символа вхождения в тексте
        end (int): Позиция за последним символом вхождения
        left (str): Контекст слева
        keyword (str): Вхождение как в тексте
        right (str): Контекст справа
    """

    start: int
    end: int
    left: str
    keyword: str
    right: str


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
        Ищутся вхождения слова или словосочетания (слова через пробел) среди слов
        текста: по словоформе без учета регистра и буквы ё, с учетом регистра
        или по лемме pymorphy3 («кота» находится по «кот»). Контекст - window слов
        слева и справа, как они записаны в тексте, со знаками препинания между ними,
        пробельные символы схлопываются в один пробел; вхождения не пересекаются

    Аргументы:
        source (str|Doc): Текст или объект Doc
        keyword (str): Слово или словосочетание
        window (int): Число слов контекста с каждой стороны
        by_lemma (bool): Сравнивать леммы, а не словоформы
        ignore_case (bool): Не учитывать регистр и букву ё при сравнении словоформ

    Вывод:
        list[Concordance]: Вхождения по порядку в тексте

    Исключения:
        TypeError: Если источник данных не строка и не объект Doc
        ValueError: Если ключевое слово пустое или окно отрицательное
    """
    if isinstance(source, Doc):
        text = source.text
        words = list(iter_doc_words(source))
    elif isinstance(source, str):
        text = source
        words = list(iter_text_words(source))
    else:
        raise TypeError("Некорректный источник данных")
    pattern = keyword.split()
    if not pattern:
        raise ValueError("Ключевое слово не задано")
    if window < 0:
        raise ValueError("Окно не может быть отрицательным")
    normalized = [_normalize(word, by_lemma, ignore_case) for _, _, word in words]
    target = [_normalize(word, by_lemma, ignore_case) for word in pattern]
    found = []
    index = 0
    while index <= len(words) - len(target):
        if normalized[index : index + len(target)] != target:
            index += 1
            continue
        last = index + len(target) - 1
        start = words[index][0]
        end = words[last][1]
        left = text[words[max(index - window, 0)][0] : start] if window else ""
        right = text[end : words[min(last + window, len(words) - 1)][1]] if window else ""
        found.append(
            Concordance(
                start, end, " ".join(left.split()), text[start:end], " ".join(right.split())
            )
        )
        index = last + 1
    return found


def _normalize(word: str, by_lemma: bool, ignore_case: bool) -> str:
    if by_lemma:
        return normalize_yo(lemmatize(word))
    return normalize_yo(word) if ignore_case else word


def format_kwic(concordances: Sequence[Concordance], width: int = 40) -> str:
    """
    Форматирование конкорданса с выравниванием по ключевому слову

    Описание:
        Левый контекст обрезается слева и выравнивается по правому краю, правый -
        обрезается справа; строки разделяются переводом строки

    Аргументы:
        concordances (list[Concordance]): Строки конкорданса
        width (int): Ширина контекста в символах

    Вывод:
        str: Конкорданс в виде текста
    """
    keyword_width = max((len(line.keyword) for line in concordances), default=0)
    return "\n".join(
        f"{line.left[-width:]:>{width}}  {line.keyword:<{keyword_width}}  {line.right[:width]}"
        for line in concordances
    )


def print_kwic(concordances: Sequence[Concordance], width: int = 40) -> None:
    """
    Вывод конкорданса с выравниванием по ключевому слову

    Аргументы:
        concordances (list[Concordance]): Строки конкорданса
        width (int): Ширина контекста в символах
    """
    print(format_kwic(concordances, width))
