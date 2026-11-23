from __future__ import annotations

import sys
from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, ClassVar

import anyts.cli
from anyts.stats import Stats

from . import __version__
from .constants import CLI_TEXTS
from .datasets.freq2011 import NAME as FREQ_DICT_NAME, FreqDict
from .datasets.stress_dict import NAME as STRESS_DICT_NAME, StressDict
from .report import STATS_CLASSES, Report
from .utils import get_document
from .verse_stats import VerseStats

if TYPE_CHECKING:
    from anyseg import Document
    from anyts.datasets import Dataset


class Command(anyts.cli.Command):
    """
    Команда ruts: статистики русских текстов, HTML-отчет и загрузка словарей

    Описание:
        ruts stats выводит статистики текстов из файлов или стандартного ввода
        таблицей, JSON или CSV, по частям с --parts; ruts report записывает
        HTML-отчет о тексте (Report); ruts download загружает частотный словарь
        и словарь ударений. Без --stats считаются классы отчета, стиховедческие
        статистики (verse) - только с --stats

    Методы:
        run: Запуск команды с аргументами, по умолчанию - командной строки

    Пример использования:
        >>> from ruts.cli import Command
        >>> import pathlib, tempfile
        >>> path = pathlib.Path(tempfile.mkdtemp()) / "кот.txt"
        >>> _ = path.write_text("Кот спит на окне.", encoding="utf-8")
        >>> Command().run(["stats", "-s", "basic", "-f", "json", str(path)])  # doctest: +ELLIPSIS
        {"...кот.txt": {"basic": {"c_letters_2": 1, ..., "n_words": 4, ...}}}
        0
    """

    prog = "ruts"
    stats_classes: ClassVar[Mapping[str, type[Stats]]] = {**STATS_CLASSES, "verse": VerseStats}
    default_stats: ClassVar[Sequence[str] | None] = tuple(STATS_CLASSES)
    datasets: ClassVar[Mapping[str, Callable[[], Dataset]]] = {
        FREQ_DICT_NAME: FreqDict,
        STRESS_DICT_NAME: StressDict,
    }
    texts: ClassVar[Mapping[str, str]] = CLI_TEXTS
    report_class = Report
    version = __version__

    def parse(self, text: str) -> Document:
        """Документ anySeg (ruts.utils.get_document)"""
        return get_document(text)


def main() -> None:
    """Точка входа команды ruts"""
    sys.exit(Command().run())
