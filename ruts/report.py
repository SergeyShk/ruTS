from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, ClassVar

import anyts.report
from anyts.report import escape as escape
from anyts.stats import Stats

from .basic_stats import BasicStats
from .cohesion_stats import CohesionStats
from .constants import REPORT_TEXTS, VISUALIZER_LABELS
from .diversity_stats import DiversityStats
from .lexical_stats import LexicalStats
from .morph_stats import MorphStats
from .phon_stats import PhonStats
from .readability_stats import ReadabilityStats
from .style_stats import StyleStats
from .unadapted_readability_stats import UnadaptedReadabilityStats
from .utils import get_document
from .visualizers.highlight import HighlightedText

if TYPE_CHECKING:
    from anyseg import Document
    from spacy.tokens import Doc

STATS_CLASSES: Mapping[str, type[Stats]] = {
    "basic": BasicStats,
    "readability": ReadabilityStats,
    "unadapted_readability": UnadaptedReadabilityStats,
    "diversity": DiversityStats,
    "morph": MorphStats,
    "lexical": LexicalStats,
    "style": StyleStats,
    "phon": PhonStats,
    "cohesion": CohesionStats,
}
STATS_TITLES: Mapping[str, str] = {
    "basic": "Базовые статистики",
    "readability": "Метрики удобочитаемости",
    "unadapted_readability": "Формулы других языков",
    "diversity": "Метрики лексического разнообразия",
    "morph": "Морфологические статистики",
    "lexical": "Статистики лексической сложности",
    "style": "SEO-метрики стиля",
    "phon": "Фоностатистики",
    "cohesion": "Статистики связности",
    "verse": "Стиховедческие статистики",
}


class Report(anyts.report.Report):
    """
    HTML-отчет о статистиках русского текста

    Описание:
        Один HTML-файл без внешних ресурсов: статистики каждого класса с
        описаниями и прочтениями по шкалам и нормам (describe), статистики каждого
        предложения, подсветка текста и графики. Текст делит anySeg (get_document),
        и каждый класс считает один его документ; стиховедческие статистики -
        только переданными в stats_classes

    Аргументы:
        source (str|Doc|Document): Источник данных
        title (str): Заголовок отчета; по умолчанию «Статистики текста»
        stats_classes (dict[str, type[Stats]]): Классы статистик по именам; по умолчанию
            STATS_CLASSES
        skip_errors (bool): Пропустить класс, который не может посчитать источник, с его
            ошибкой в errors, вместо исключения

    Атрибуты:
        document (Document): Документ источника
        title (str): Заголовок отчета
        stats (dict[str, Stats]): Статистики каждого класса по имени
        errors (dict[str, RutsError]): Ошибки классов, пропущенных с skip_errors

    Методы:
        to_html: Получение отчета одной HTML-страницей
        save: Запись отчета в файл в кодировке UTF-8

    Исключения:
        ParameterError: Если skip_errors не bool
        SourceTypeError, SourceError: Как у классов статистик, без skip_errors

    Пример использования:
        >>> from ruts.report import Report
        >>> text = "Кот спит на окне. Пёс громко лает во дворе."
        >>> report = Report(text, title="Два предложения", skip_errors=True)
        >>> page = report.to_html()
        >>> page.startswith("<!DOCTYPE html>"), report.stats["basic"].n_words
        (True, 9)
    """

    stats_classes: ClassVar[Mapping[str, type[Stats]]] = STATS_CLASSES
    titles: ClassVar[Mapping[str, str]] = STATS_TITLES
    sentence_columns: ClassVar[Sequence[tuple[str, str]]] = (
        ("basic", "n_words"),
        ("basic", "n_syllables"),
        ("readability", "flesch_reading_easy"),
        ("style", "water"),
    )
    highlight_class = HighlightedText
    visualizer_labels: ClassVar[Mapping[str, Mapping[str, str]]] = VISUALIZER_LABELS
    texts: ClassVar[Mapping[str, str]] = REPORT_TEXTS

    def parse(self, source: str | Doc | Document) -> Document:
        """Документ anySeg (ruts.utils.get_document)"""
        return get_document(source)
