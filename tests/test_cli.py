"""Команда ruts и HTML-отчет"""

import json
import re
import subprocess
import sys
from importlib.metadata import entry_points

import pytest
from anyts.constants import CLI_TEXTS as CORE_CLI_TEXTS, REPORT_TEXTS as CORE_REPORT_TEXTS

from ruts.cli import Command
from ruts.constants import _RU_CLI_TEXTS, _RU_REPORT_TEXTS
from ruts.datasets import FreqDict, StressDict
from ruts.datasets.stress_dict import FILENAME
from ruts.report import STATS_CLASSES, Report
from tests.datasets.test_freq2011 import write_dict
from tests.test_verse_stats import ROWS

TEXT = "Кот спит на окне. Пёс громко лает во дворе.\n\nПтица поёт в саду. Нет, не поёт!"


@pytest.fixture
def dictionaries(tmp_path_factory, monkeypatch):
    """Словари тестов: их читают FreqDict() и StressDict() классов команды"""
    path = tmp_path_factory.mktemp("dicts")
    write_dict(path)
    path.joinpath(FILENAME).write_text(
        "\n".join("\t".join(row) for row in sorted(ROWS)) + "\n", encoding="utf-8"
    )
    for cls in (FreqDict, StressDict):
        monkeypatch.setattr(cls.__init__, "__defaults__", (path,))


@pytest.fixture
def text_file(tmp_path):
    path = tmp_path / "текст.txt"
    path.write_text(TEXT, encoding="utf-8")
    return str(path)


def finite(stats):
    return {
        key: None if isinstance(value, float) and value != value else value
        for key, value in stats.items()
    }


def test_json_is_the_flat_statistics(capsys, text_file, dictionaries):
    """JSON - get_stats(flat=True) каждого класса по умолчанию, nan - null"""
    assert Command().run(["stats", "-f", "json", text_file]) == 0
    found = json.loads(capsys.readouterr().out)[text_file]
    assert list(found) == list(STATS_CLASSES)
    for name in STATS_CLASSES:
        stats = Report.compute(STATS_CLASSES[name], Command().parse(TEXT))
        assert found[name] == finite(stats.get_stats(flat=True)), name


def test_default_classes(capsys):
    """Без --stats считаются классы отчета: стиховедческие статистики - только по имени"""
    command = Command()
    assert command.run(["stats", "--help"]) == 0
    help_text = " ".join(capsys.readouterr().out.split())
    assert f"по умолчанию {', '.join(STATS_CLASSES)}" in help_text
    assert list(command.stats_classes) == [*STATS_CLASSES, "verse"]
    assert command.run(["stats", "-p", "sentences", "-s", "verse"]) == 2
    assert "verse не считает части sentences" in capsys.readouterr().err


def test_parts(capsys, text_file, dictionaries):
    """Части без --stats - классы по умолчанию, которые их считают; verse - по имени"""
    assert Command().run(["stats", "-p", "sentences", "-f", "json", text_file]) == 0
    found = json.loads(capsys.readouterr().out)[text_file]
    assert list(found) == [name for name in STATS_CLASSES if name not in {"diversity", "cohesion"}]
    assert [record["n_words"] for record in found["basic"]] == [4, 5, 4, 3]
    argv = ["stats", "-p", "paragraphs", "-f", "json", "-s", "verse", text_file]
    assert Command().run(argv) == 0
    assert [
        record["n_lines"] for record in json.loads(capsys.readouterr().out)[text_file]["verse"]
    ] == [1, 1]


def test_report(tmp_path, text_file, dictionaries):
    """Отчет открывается без сети: ни скриптов, ни внешних ресурсов; заголовки - русские"""
    output = tmp_path / "отчет.html"
    assert Command().run(["report", "-t", "Пример", "-o", str(output), text_file]) == 0
    page = output.read_text(encoding="utf-8")
    assert page.startswith('<!DOCTYPE html>\n<html lang="ru">')
    assert not re.search(r"<script|<link|<img|(src|href)=\"(https?:)?//", page)
    for heading in ("Базовые статистики", "Предложения", "Подсветка текста", "Графики"):
        assert f">{heading}<" in page
    assert "Водность (%)" in page


def test_report_of_verse(capsys, text_file, dictionaries):
    """Стиховедческие статистики - в отчете только по имени, со своим заголовком"""
    assert Command().run(["report", "-s", "basic", text_file]) == 0
    assert ">Стиховедческие статистики<" not in capsys.readouterr().out
    assert Command().run(["report", "-s", "basic,verse", text_file]) == 0
    assert ">Стиховедческие статистики<" in capsys.readouterr().out


def test_missing_dictionary(capsys, text_file, tmp_path, monkeypatch):
    """Класс без загруженного словаря пропускается с подсказкой команды загрузки"""
    from ruts.datasets import freq2011

    monkeypatch.setattr(freq2011.FreqDict.__init__, "__defaults__", (tmp_path,))
    assert Command().run(["stats", "-s", "basic,lexical", "-f", "json", text_file]) == 1
    out, err = capsys.readouterr()
    assert list(json.loads(out)[text_file]) == ["basic"]
    assert "lexical: Словарь freq2011 не обнаружен" in err
    assert "ruts download freq2011" in err


def test_datasets():
    command = Command()
    assert list(command.datasets) == ["freq2011", "stress_dict"]
    assert command.run(["download", "freq"]) == 2


@pytest.mark.core_sync
def test_texts_are_translated():
    """Русские тексты команды и отчета полны: новый ключ ядра не выйдет по-английски"""
    assert set(_RU_CLI_TEXTS) == set(CORE_CLI_TEXTS)
    assert set(_RU_REPORT_TEXTS) == set(CORE_REPORT_TEXTS)


def test_entry_points():
    """Команда ruts - точка входа пакета и python -m ruts"""
    (script,) = entry_points(group="console_scripts", name="ruts")
    assert script.value == "ruts.cli:main"
    found = subprocess.run(
        [sys.executable, "-m", "ruts", "--help"], capture_output=True, check=True, text=True
    )
    assert "Статистики русских текстов" in found.stdout
