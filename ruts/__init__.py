# Russian Texts Statistics (ruTS)
#
# Copyright (C) 2019-2022
# Авторы: Шкарин Сергей <kouki.sergey@gmail.com>
#         Смирнова Екатерина <ekanerina@yandex.ru>
# URL: <https://github.com/SergeyShk/ruTS>

from .basic_stats import BasicStats
from .components import (
    BasicStatsComponent,
    DiversityStatsComponent,
    MorphStatsComponent,
    ReadabilityStatsComponent,
)
from .diversity_stats import DiversityStats
from .extractors import SentsExtractor, WordsExtractor
from .morph_stats import MorphStats
from .readability_stats import ReadabilityStats

# Метаданные

__doc__ = """Инструмент для извлечения статистик для текстов на русском языке.
Требует версию Python 3.8 и выше"""
__author__ = "Шкарин Сергей, Смирнова Екатерина"
__author_email__ = "kouki.sergey@gmail.com, ekanerina@yandex.ru"

__all__ = [
    "BasicStats",
    "BasicStatsComponent",
    "DiversityStatsComponent",
    "MorphStatsComponent",
    "ReadabilityStatsComponent",
    "DiversityStats",
    "SentsExtractor",
    "WordsExtractor",
    "MorphStats",
    "ReadabilityStats",
]
