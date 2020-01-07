# Russian Texts Statistics (ruTS)
#
# Copyright (C) 2019
# Авторы: Шкарин Сергей <kouki.sergey@gmail.com>
#         Смирнова Екатерина <ekanerina@yandex.ru>
# URL: <https://github.com/SergeyShk/ruTS>

# Метаданные

import os

version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
with open(version_file, 'r') as f:
    __version__ = f.read().strip()

__doc__ = """Инструмент для извлечения статистик для текстов на русском языке.
Требует версию Python 3.6 и выше"""
__author__ = "Шкарин Сергей, Смирнова Екатерина"
__author_email__ = "kouki.sergey@gmail.com, ekanerina@yandex.ru"

# Импорт основных классов

from ruts.extractors import SentsExtractor, WordsExtractor
from ruts.basic_stats import BasicStats
from ruts.morph_stats import MorphStats
from ruts.readability_stats import ReadabilityStats