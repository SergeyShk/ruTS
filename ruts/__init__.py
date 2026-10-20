# Russian Texts Statistics (ruTS)
#
# Copyright (C) 2019-2026
# Авторы: Шкарин Сергей <kouki.sergey@gmail.com>
#         Смирнова Екатерина <ekanerina@yandex.ru>
# URL: <https://github.com/SergeyShk/ruTS>

import logging
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING

from anyts.utils import make_lazy

from .basic_stats import BasicStats
from .cohesion_stats import CohesionStats
from .diversity_stats import DiversityStats
from .exceptions import (
    DataFileError,
    DatasetNotFoundError,
    DownloadError,
    ParameterError,
    RutsError,
    SourceError,
    SourceTypeError,
    UnknownStatError,
)
from .extractors import CharNgramsExtractor, SentsExtractor, WordsExtractor
from .lexical_stats import LexicalStats
from .morph_stats import MorphStats
from .phon_stats import PhonStats
from .readability_stats import ReadabilityStats
from .style_stats import StyleStats
from .syntax_stats import SyntaxStats
from .verse_stats import VerseStats

if TYPE_CHECKING:
    from .components import (
        BasicStatsComponent as BasicStatsComponent,
        CohesionStatsComponent as CohesionStatsComponent,
        DiversityStatsComponent as DiversityStatsComponent,
        LexicalStatsComponent as LexicalStatsComponent,
        MorphStatsComponent as MorphStatsComponent,
        PhonStatsComponent as PhonStatsComponent,
        ReadabilityStatsComponent as ReadabilityStatsComponent,
        StyleStatsComponent as StyleStatsComponent,
        SyntaxStatsComponent as SyntaxStatsComponent,
        VerseStatsComponent as VerseStatsComponent,
    )

logging.getLogger(__name__).addHandler(logging.NullHandler())

# Метаданные

try:
    __version__ = version("ruts")
except PackageNotFoundError:
    __version__ = "0.0.0"
__description__ = """Инструмент для извлечения статистик для текстов на русском языке.
Требует версию Python 3.11 и выше"""
__author__ = "Шкарин Сергей, Смирнова Екатерина"
__author_email__ = "kouki.sergey@gmail.com, ekanerina@yandex.ru"

__all__ = [
    "BasicStats",
    "CharNgramsExtractor",
    "CohesionStats",
    "DataFileError",
    "DatasetNotFoundError",
    "DiversityStats",
    "DownloadError",
    "LexicalStats",
    "MorphStats",
    "ParameterError",
    "PhonStats",
    "ReadabilityStats",
    "RutsError",
    "SentsExtractor",
    "SourceError",
    "SourceTypeError",
    "StyleStats",
    "SyntaxStats",
    "UnknownStatError",
    "VerseStats",
    "WordsExtractor",
    "__version__",
]

# Компоненты регистрируют фабрики spaCy и импортируют его: модуль грузится при первом обращении,
# а при уже загруженном spaCy - сразу: точки входа он мог прочитать до установки ruTS. Компонентов
# нет в __all__, чтобы import * и help() не грузили spaCy; заглушка spaCy - не spaCy
if sys.modules.get("spacy.language") is not None:
    from . import components as components

make_lazy(
    __name__,
    dict.fromkeys(
        (
            "BasicStatsComponent",
            "CohesionStatsComponent",
            "DiversityStatsComponent",
            "LexicalStatsComponent",
            "MorphStatsComponent",
            "PhonStatsComponent",
            "ReadabilityStatsComponent",
            "StyleStatsComponent",
            "SyntaxStatsComponent",
            "VerseStatsComponent",
        ),
        "components",
    ),
)
