from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any

from anyts.utils import is_doc, is_document
from anyts.visualizers.sentences import (
    sentence_lengths as core_sentence_lengths,
    sentence_lengths_plot as core_sentence_lengths_plot,
)
from matplotlib.axes import Axes

from ..extractors import SentsExtractor, WordsExtractor
from ..utils import get_document
from ._labels import russian_labels

if TYPE_CHECKING:
    from anyseg import Document
    from spacy.tokens import Doc


def sentence_lengths_plot(
    source: str | Doc | Document | Iterable[int],
    window: int = 10,
    inset: bool = True,
    ax: Axes | None = None,
    labels: Mapping[str, str] | None = None,
    sents_extractor: SentsExtractor | None = None,
    words_extractor: WordsExtractor | None = None,
) -> Axes:
    """
    Построение кривой длин предложений

    Описание:
        Длина каждого предложения в словах по порядку текста, скользящее среднее
        по окну из window предложений и врезка с гистограммой длин - ритм текста;
        длины берутся из sentence_lengths

    Аргументы:
        source (str|Doc|Document|Iterable[int]): Текст, объект Doc, Document или длины
            предложений (список, массив numpy, Series)
        window (int): Окно скользящего среднего в предложениях
        inset (bool): Показывать врезку с гистограммой
        ax (Axes): Оси для графика; если не заданы, создается новая фигура
        labels (dict[str, str]): Подписи поверх VISUALIZER_LABELS["sentence_lengths_plot"]
        sents_extractor (SentsExtractor): Инструмент для извлечения предложений строки
            или Doc без предложений
        words_extractor (WordsExtractor): Инструмент для извлечения слов предложения строки
            или Doc без предложений

    Вывод:
        Axes: Оси с графиком

    Исключения:
        SourceTypeError: Если источник данных или экстрактор некорректны
        ParameterError: Если окно не целое число или меньше 1, подписи некорректны
        SourceError: Если предложений нет или длина отрицательна
    """
    source, sents_extractor, words_extractor = _lengths_args(
        source, sents_extractor, words_extractor
    )
    return core_sentence_lengths_plot(
        source,
        window,
        inset,
        ax,
        russian_labels("sentence_lengths_plot", labels),
        sents_extractor,
        words_extractor,
    )


def sentence_lengths(
    source: str | Doc | Document | Iterable[int],
    sents_extractor: SentsExtractor | None = None,
    words_extractor: WordsExtractor | None = None,
) -> list[int]:
    """
    Извлечение длин предложений в словах

    Описание:
        Строка, Doc и Document дают предложения своего документа (get_document) с их
        словами с буквой или цифрой; с экстрактором строка и Doc без предложений
        делятся sents_extractor и words_extractor (недостающий - ruTS по умолчанию),
        а Doc с предложениями и Document сохраняют свои; готовые длины используются
        как есть. Предложения без слов пропускаются

    Аргументы:
        source (str|Doc|Document|Iterable[int]): Текст, объект Doc, Document или готовые
            длины
        sents_extractor (SentsExtractor): Инструмент для извлечения предложений строки
            или Doc без предложений
        words_extractor (WordsExtractor): Инструмент для извлечения слов предложения строки
            или Doc без предложений

    Вывод:
        list[int]: Длины предложений по порядку

    Исключения:
        SourceTypeError: Если источник данных или экстрактор некорректны
        SourceError: Если длина отрицательна

    Пример использования:
        >>> from ruts.visualizers import sentence_lengths
        >>> sentence_lengths("Кот спит. Где пёс? - Ест, - сказала она.")
        [2, 2, 3]
    """
    return core_sentence_lengths(*_lengths_args(source, sents_extractor, words_extractor))


def _lengths_args(
    source: Any,
    sents_extractor: SentsExtractor | None,
    words_extractor: WordsExtractor | None,
) -> tuple[Any, SentsExtractor | None, WordsExtractor | None]:
    """Документ текста, Doc или Document (get_document) без экстракторов; с экстрактором -
    экстракторы, недостающий - ruTS по умолчанию"""
    if sents_extractor is None and words_extractor is None:
        if isinstance(source, str) or is_doc(source) or is_document(source):
            return get_document(source), None, None
        return source, None, None
    return (
        source,
        SentsExtractor() if sents_extractor is None else sents_extractor,
        WordsExtractor() if words_extractor is None else words_extractor,
    )
