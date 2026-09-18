import shutil
import tempfile
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import spearmanr

from ruts import ReadabilityStats
from ruts.constants import READABILITY_GRADE_STATS
from ruts.datasets import dataset as dataset_module
from ruts.datasets.texts_by_grade import GRADES, TextsByGrade
from ruts.exceptions import DataFileError, ParameterError
from ruts.utils import extract_archive

BUNDLED_ARCHIVE = (
    Path(__file__).parents[2] / "ruts" / "datasets" / "data" / "texts_by_grade.tar.xz"
)


@pytest.fixture(scope="module")
def dataset():
    path = Path(tempfile.gettempdir()) / "ruts_data_tbg"
    path.mkdir(parents=True, exist_ok=True)
    dataset = TextsByGrade(data_dir=path)
    # В репозитории архив лежит рядом с кодом, сеть не нужна
    if not dataset.filepath and BUNDLED_ARCHIVE.is_file():
        shutil.copy(BUNDLED_ARCHIVE, dataset._filepath)
        extract_archive(dataset._filepath)
    return dataset


def test_download(dataset):
    if dataset.filepath:
        pytest.skip(f"Не нужно загружать набор данных при каждом запуске теста {dataset.filepath}")
    dataset.download()
    assert Path(dataset._filepath).is_file()
    assert Path(dataset.data_dir).is_dir()


def test_oserror():
    dataset = TextsByGrade(data_dir="/tmp")
    with pytest.raises(OSError):
        _ = list(dataset.get_texts())


def test_info(dataset):
    assert dataset.info["Наименование"] == "texts_by_grade"
    assert dataset.info["license"] == "CC0 1.0"
    assert dataset.labels == tuple(f"grade_{grade}" for grade in GRADES)


def test_records_count(dataset):
    records = list(dataset)
    assert len(records) == 68
    assert sorted({record["grade"] for record in records}) == list(GRADES)


def test_get_texts(dataset):
    for text in dataset.get_texts(limit=2):
        assert isinstance(text, str)
        assert "\n\n" not in text


@pytest.mark.parametrize("limit", [1, 5, 10])
def test_get_texts_limit(dataset, limit):
    assert sum(1 for _ in dataset.get_texts(limit=limit)) == limit


@pytest.mark.parametrize("min_len", [1000, 3000, 5000])
def test_get_texts_min_len(dataset, min_len):
    assert all(len(text) >= min_len for text in dataset.get_texts(min_len=min_len, limit=5))


@pytest.mark.parametrize("max_len", [2000, 3000, 5000])
def test_get_texts_max_len(dataset, max_len):
    assert all(len(text) <= max_len for text in dataset.get_texts(max_len=max_len, limit=5))


def test_get_records(dataset):
    fields = ["grade", "subject", "source", "text", "file"]
    for record in dataset.get_records(limit=2):
        assert isinstance(record, dict)
        assert all(field in record for field in fields)


@pytest.mark.parametrize(("grade", "expected"), [(1, 11), (11, 15), (17, 15), (5, 1)])
def test_get_records_grade(dataset, grade, expected):
    records = list(dataset.get_records(grade=grade))
    assert len(records) == expected
    assert all(record["grade"] == grade for record in records)


def test_get_records_subject(dataset):
    records = list(dataset.get_records(subject="ряба"))
    assert len(records) == 1
    assert records[0]["subject"] == "Курочка Ряба"
    assert records[0]["source"] == "http://skazki.org.ru/tales/yaichko/"
    assert records[0]["text"].startswith("Жил себе дед да баба")


def test_get_records_no_source(dataset):
    records = list(dataset.get_records(subject="Буратино"))
    assert len(records) == 1
    assert records[0]["source"] == ""
    assert sum(1 for record in dataset if not record["source"]) == 2


def test_get_records_commented_source(dataset):
    records = list(dataset.get_records(subject="Котлован"))
    assert len(records) == 1
    assert records[0]["source"] == "http://ilibrary.ru/text/1010/p.1/index.html"


def test_iter_ignores_foreign_files(dataset):
    stray = dataset.data_dir / "texts_by_grade" / "grade_1" / ".DS_Store"
    stray.write_bytes(b"")
    try:
        assert sum(1 for _ in dataset) == 68
    finally:
        stray.unlink()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"grade": 0},
        {"grade": 2},
        {"grade": 18},
        {"min_len": 0},
        {"min_len": -1},
        {"max_len": -1},
        {"min_len": 10, "max_len": 5},
        {"limit": -1},
    ],
)
def test_get_filters_errors(dataset, kwargs):
    with pytest.raises(ParameterError):
        list(dataset.get_texts(**kwargs))


def test_download_extracts_existing_archive(tmp_path):
    dataset = TextsByGrade(data_dir=tmp_path)
    shutil.copy(BUNDLED_ARCHIVE, dataset._filepath)
    dataset.download()
    assert dataset.check_data()


def test_download_replaces_broken_archive(tmp_path, monkeypatch):
    dataset = TextsByGrade(data_dir=tmp_path)
    dataset._filepath.write_bytes(b"\x00" * 40)
    calls = []

    def fake_download(url, filename, dirpath, force=False):
        calls.append(force)
        if not force and (Path(dirpath) / filename).is_file():
            return ""
        shutil.copy(BUNDLED_ARCHIVE, Path(dirpath) / filename)
        return str(Path(dirpath) / filename)

    monkeypatch.setattr(dataset_module, "download_file", fake_download)
    dataset.download()
    assert calls == [False, True]
    assert dataset.check_data()
    other = TextsByGrade(data_dir=tmp_path / "other")
    other._filepath.parent.mkdir()
    other._filepath.write_bytes(b"\x00" * 40)

    def broken_download(url, filename, dirpath, force=False):
        path = Path(dirpath) / filename
        if not force and path.is_file():
            return ""
        path.write_bytes(b"\x00" * 40)
        return str(path)

    monkeypatch.setattr(dataset_module, "download_file", broken_download)
    with pytest.raises(DataFileError):
        other.download()


@pytest.mark.parametrize("subject, expected", [(".", 46), ("(", 0)])
def test_subject_escaped(dataset, subject, expected):
    assert len(list(dataset.get_records(subject=subject))) == expected


@pytest.fixture(scope="module")
def readability(dataset):
    labels = []
    stats = {stat: [] for stat in READABILITY_GRADE_STATS}
    stats.update({"consensus_grade": [], "flesch_reading_easy": [], "lix": [], "rix": []})
    for record in dataset:
        rs = ReadabilityStats(record["text"])
        labels.append(record["grade"])
        for stat in stats:
            stats[stat].append(getattr(rs, stat))
    return np.array(labels), {stat: np.array(values) for stat, values in stats.items()}


def test_readability_formulas_correlate_with_grades(readability):
    labels, stats = readability
    for stat, values in stats.items():
        rho, _ = spearmanr(labels, values)
        if stat == "flesch_reading_easy":
            assert rho < -0.7, stat
        else:
            assert rho > 0.7, stat


def test_consensus_grade_matches_labels(readability):
    labels, stats = readability
    consensus = stats["consensus_grade"]
    assert spearmanr(labels, consensus)[0] > 0.8
    assert np.mean(np.abs(consensus - labels)) < 4
    groups = [(1, 1), (3, 4), (5, 9), (10, 11), (12, 17)]
    means = [consensus[(labels >= low) & (labels <= high)].mean() for low, high in groups]
    assert means == sorted(means)
