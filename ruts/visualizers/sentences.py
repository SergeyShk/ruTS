from collections.abc import Iterable, Mapping

from anyts.visualizers.sentences import (
    sentence_lengths as core_sentence_lengths,
    sentence_lengths_plot as core_sentence_lengths_plot,
)
from matplotlib.axes import Axes
from spacy.tokens import Doc

from ..extractors import SentsExtractor, WordsExtractor
from ._labels import russian_labels


def sentence_lengths_plot(
    source: str | Doc | Iterable[int],
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
        source (str|Doc|Iterable[int]): Текст, объект Doc или длины предложений
            (список, массив numpy, Series)
        window (int): Окно скользящего среднего в предложениях
        inset (bool): Показывать врезку с гистограммой
        ax (Axes): Оси для графика; если не заданы, создается новая фигура
        labels (dict[str, str]): Подписи поверх VISUALIZER_LABELS["sentence_lengths_plot"]
        sents_extractor (SentsExtractor): Инструмент для извлечения предложений строки
        words_extractor (WordsExtractor): Инструмент для извлечения слов предложения строки

    Вывод:
        Axes: Оси с графиком

    Исключения:
        SourceTypeError: Если источник данных или экстрактор некорректны
        ParameterError: Если окно не целое число или меньше 1, подписи некорректны
        SourceError: Если предложений нет или длина отрицательна
    """
    return core_sentence_lengths_plot(
        source,
        window,
        inset,
        ax,
        russian_labels("sentence_lengths_plot", labels),
        SentsExtractor() if sents_extractor is None else sents_extractor,
        WordsExtractor() if words_extractor is None else words_extractor,
        join_hyphens=True,
    )


def sentence_lengths(
    source: str | Doc | Iterable[int],
    sents_extractor: SentsExtractor | None = None,
    words_extractor: WordsExtractor | None = None,
) -> list[int]:
    """
    Извлечение длин предложений в словах

    Описание:
        Строка делится на предложения sents_extractor, предложение - на слова
        words_extractor (по умолчанию SentsExtractor и WordsExtractor ruTS);
        объект Doc - по границам предложений, дефисные слова склеиваются, без границ -
        как его текст; готовые длины используются как есть. Предложения без слов
        пропускаются

    Аргументы:
        source (str|Doc|Iterable[int]): Текст, объект Doc или готовые длины
        sents_extractor (SentsExtractor): Инструмент для извлечения предложений строки
        words_extractor (WordsExtractor): Инструмент для извлечения слов предложения строки

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
    return core_sentence_lengths(
        source,
        SentsExtractor() if sents_extractor is None else sents_extractor,
        WordsExtractor() if words_extractor is None else words_extractor,
        join_hyphens=True,
    )
