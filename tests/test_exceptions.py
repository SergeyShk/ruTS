import logging
from collections import Counter
from importlib.metadata import version

import pytest
from anyts.datasets import download_file, to_path

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


def test_logging():
    assert any(isinstance(h, logging.NullHandler) for h in logging.getLogger("ruts").handlers)


def test_version():
    assert ruts.__version__ == version("ruts")
    assert "__version__" in ruts.__all__
