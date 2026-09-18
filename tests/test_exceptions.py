import logging
import zipfile
from collections import Counter
from importlib.metadata import version

import pytest

import ruts
from ruts import BasicStats, MorphStats, ReadabilityStats, RutsError, WordsExtractor
from ruts.corpus import delta, keyness
from ruts.datasets import PoetryCorpus
from ruts.datasets.poetry_corpus import FILENAME, load_records
from ruts.exceptions import (
    DataFileError,
    DatasetNotFoundError,
    DownloadError,
    ParameterError,
    SourceError,
    SourceTypeError,
    UnknownStatError,
)
from ruts.utils import download_file, extract_archive, to_path
from ruts.visualizers import zipf


@pytest.mark.parametrize(
    "exception, builtin",
    [
        (SourceTypeError, TypeError),
        (SourceError, ValueError),
        (ParameterError, ValueError),
        (UnknownStatError, KeyError),
        (DatasetNotFoundError, OSError),
        (DataFileError, ValueError),
        (DownloadError, RuntimeError),
    ],
)
def test_hierarchy(exception, builtin):
    assert issubclass(exception, RutsError)
    assert issubclass(exception, builtin)
    assert getattr(ruts, exception.__name__) is exception
    assert exception.__name__ in ruts.__all__


def test_raised_classes(tmp_path):
    with pytest.raises(SourceError):
        BasicStats("...")
    with pytest.raises(SourceTypeError):
        BasicStats(42)
    with pytest.raises(SourceTypeError):
        zipf({"а": 1})
    with pytest.raises(SourceTypeError):
        to_path(42)
    with pytest.raises(ParameterError):
        ReadabilityStats("Кот спал.", preset="unknown")
    with pytest.raises(ParameterError):
        keyness(["кот"], ["пёс"], top_n=0)
    with pytest.raises(SourceError):
        delta({"а": ["кот"], "б": ["пёс"]})
    with pytest.raises(UnknownStatError):
        MorphStats("Кот спал.").explain_text("unknown")
    with pytest.raises(DatasetNotFoundError):
        _ = list(PoetryCorpus(data_dir=tmp_path).get_texts())
    (tmp_path / FILENAME).write_text("<items><item>", encoding="utf-8")
    with pytest.raises(DataFileError):
        _ = list(load_records(tmp_path / FILENAME))
    with pytest.raises(DownloadError):
        download_file("file:///nowhere/nothing.zip", dirpath=tmp_path, force=True)


def test_builtin_compatibility():
    with pytest.raises(ValueError):
        WordsExtractor(min_len=3, max_len=2)
    with pytest.raises(TypeError):
        zipf(Counter)
    with pytest.raises(RutsError):
        BasicStats("")


def test_logging(tmp_path, caplog):
    archive = tmp_path / "stopwords.zip"
    with zipfile.ZipFile(archive, mode="w") as zip_file:
        zip_file.writestr("stopwords/russian", "и\nв\n")
    text = tmp_path / "text.txt"
    text.write_text("текст", encoding="utf-8")
    with caplog.at_level(logging.INFO, logger="ruts"):
        assert download_file(archive.as_uri(), filename="copy.zip", dirpath=tmp_path) == str(
            tmp_path / "copy.zip"
        )
        assert download_file(archive.as_uri(), filename="copy.zip", dirpath=tmp_path) == ""
        extract_archive(archive, tmp_path / "out")
        extract_archive(text)
    messages = [(record.name, record.levelname, record.getMessage()) for record in caplog.records]
    assert messages == [
        ("ruts.utils", "INFO", f"Загрузка файла {archive.as_uri()}"),
        ("ruts.utils", "INFO", f"Файл загружен: {tmp_path / 'copy.zip'}"),
        ("ruts.utils", "INFO", f"Файл {tmp_path / 'copy.zip'} уже загружен"),
        ("ruts.utils", "INFO", f"Извлечение файлов из архива {archive}"),
        ("ruts.utils", "WARNING", f"Файл {text} не является архивом в формате ZIP или TAR"),
    ]
    assert any(isinstance(h, logging.NullHandler) for h in logging.getLogger("ruts").handlers)


def test_version():
    assert ruts.__version__ == version("ruts")
    assert "__version__" in ruts.__all__
