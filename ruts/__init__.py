# Russian Texts Statistics (ruTS)
#
# Copyright (C) 2019-2020
# Авторы: Шкарин Сергей <kouki.sergey@gmail.com>
#         Смирнова Екатерина <ekanerina@yandex.ru>
# URL: <https://github.com/SergeyShk/ruTS>

# Метаданные

import io
import os

version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
with io.open(version_file, mode='r', encoding='utf-8') as f:
    __version__ = f.read().strip()

__doc__ = """Инструмент для извлечения статистик для текстов на русском языке.
Требует версию Python 3.6 и выше"""
__author__ = "Шкарин Сергей, Смирнова Екатерина"
__author_email__ = "kouki.sergey@gmail.com, ekanerina@yandex.ru"

# Импорт основных классов

from .basic_stats import BasicStats
from .components import (
    BasicStatsComponent,
    DiversityStatsComponent,
    MorphStatsComponent,
    ReadabilityStatsComponent
)
from .diversity_stats import DiversityStats
from .extractors import SentsExtractor, WordsExtractor
from .morph_stats import MorphStats
from .readability_stats import ReadabilityStats