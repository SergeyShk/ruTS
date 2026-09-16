# Russian Texts Statistics (ruTS)
#
# Copyright (C) 2019-2026
# Авторы: Шкарин Сергей <kouki.sergey@gmail.com>
#         Смирнова Екатерина <ekanerina@yandex.ru>
# URL: <https://github.com/SergeyShk/ruTS>

from .basic_stats import BasicStats
from .cohesion_stats import CohesionStats
from .components import (
    BasicStatsComponent,
    CohesionStatsComponent,
    DiversityStatsComponent,
    LexicalStatsComponent,
    MorphStatsComponent,
    PhonStatsComponent,
    ReadabilityStatsComponent,
    StyleStatsComponent,
    SyntaxStatsComponent,
)
from .diversity_stats import DiversityStats
from .extractors import CharNgramsExtractor, SentsExtractor, WordsExtractor
from .lexical_stats import LexicalStats
from .morph_stats import MorphStats
from .phon_stats import PhonStats
from .readability_stats import ReadabilityStats
from .style_stats import StyleStats
from .syntax_stats import SyntaxStats

# Метаданные

__description__ = """Инструмент для извлечения статистик для текстов на русском языке.
Требует версию Python 3.11 и выше"""
__author__ = "Шкарин Сергей, Смирнова Екатерина"
__author_email__ = "kouki.sergey@gmail.com, ekanerina@yandex.ru"

__all__ = [
    "BasicStats",
    "BasicStatsComponent",
    "CharNgramsExtractor",
    "CohesionStats",
    "CohesionStatsComponent",
    "DiversityStats",
    "DiversityStatsComponent",
    "LexicalStats",
    "LexicalStatsComponent",
    "MorphStats",
    "MorphStatsComponent",
    "PhonStats",
    "PhonStatsComponent",
    "ReadabilityStats",
    "ReadabilityStatsComponent",
    "SentsExtractor",
    "StyleStats",
    "StyleStatsComponent",
    "SyntaxStats",
    "SyntaxStatsComponent",
    "WordsExtractor",
]
