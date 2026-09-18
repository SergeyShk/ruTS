import shutil
import tempfile
from pathlib import Path

import pytest

from ruts.datasets import dataset as dataset_module
from ruts.datasets.sov_chrest_lit import SovChLit
from ruts.exceptions import DataFileError, ParameterError

BUNDLED_ARCHIVE = (
    Path(__file__).parents[2] / "ruts" / "datasets" / "data" / "sov_chrest_lit.tar.xz"
)


@pytest.fixture(scope="module")
def dataset():
    path = Path(tempfile.gettempdir()) / "ruts_data_scl"
    path.mkdir(parents=True, exist_ok=True)
    dataset = SovChLit(data_dir=path)
    # В репозитории архив лежит рядом с кодом, сеть не нужна
    if not dataset.filepath:
        shutil.copy(BUNDLED_ARCHIVE, dataset._filepath)
    dataset.download()
    return dataset


@pytest.mark.network
def test_download(tmp_path):
    dataset = SovChLit(data_dir=tmp_path)
    dataset.download()
    assert Path(dataset._filepath).is_file()
    assert dataset.check_data()


def test_download_extracts_existing_archive(tmp_path):
    dataset = SovChLit(data_dir=tmp_path)
    shutil.copy(BUNDLED_ARCHIVE, dataset._filepath)
    dataset.download()
    assert dataset.check_data()


def test_download_replaces_broken_archive(tmp_path, monkeypatch):
    dataset = SovChLit(data_dir=tmp_path)
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
    other = SovChLit(data_dir=tmp_path / "other")
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


def test_oserror():
    dataset = SovChLit(data_dir="/tmp")
    with pytest.raises(OSError):
        _ = list(dataset.get_texts())


def test_get_texts(dataset):
    for text in dataset.get_texts(limit=2):
        assert isinstance(text, str)


@pytest.mark.parametrize("limit", [1, 5, 10])
def test_get_texts_limit(dataset, limit):
    assert sum(1 for _ in dataset.get_texts(limit=limit)) == limit


@pytest.mark.parametrize("min_len", [100, 200, 1000])
def test_get_texts_min_len(dataset, min_len):
    assert all(len(text) >= min_len for text in dataset.get_texts(min_len=min_len, limit=5))


@pytest.mark.parametrize("max_len", [250, 500, 1000])
def test_get_texts_max_len(dataset, max_len):
    assert all(len(text) <= max_len for text in dataset.get_texts(max_len=max_len, limit=5))


def test_get_records(dataset):
    fields = ["grade", "book", "year", "category", "type", "subject", "author"]
    for record in dataset.get_records(limit=2):
        assert isinstance(record, dict)
        assert all(field in record for field in fields)


@pytest.mark.parametrize("grade, expected", [(1, 179)])
def test_get_records_grade(dataset, grade, expected):
    records = list(dataset.get_records(grade=grade))
    assert len(records) == expected


@pytest.mark.parametrize(
    "book, expected", [("Родная речь. Книга для чтения в I классе начальной школы", 179)]
)
def test_get_records_book(dataset, book, expected):
    records = list(dataset.get_records(book=book))
    assert len(records) == expected


@pytest.mark.parametrize("year, expected", [(1963, 179)])
def test_get_records_year(dataset, year, expected):
    records = list(dataset.get_records(year=year))
    assert len(records) == expected


@pytest.mark.parametrize(
    "category, expected", [("Лето", 13), ("Весна", 53), ("Зима", 21), ("зима", 21), ("Зим", 21)]
)
def test_get_records_category(dataset, category, expected):
    records = list(dataset.get_records(category=category))
    assert len(records) == expected


@pytest.mark.parametrize(
    "text_type, expected", [("Рассказ", 109), ("Басня", 4), ("Стихотворение", 37), ("Совет", 1)]
)
def test_get_records_text_type(dataset, text_type, expected):
    records = list(dataset.get_records(text_type=text_type))
    assert len(records) == expected


@pytest.mark.parametrize("subject, expected", [("Лиса", 6), ("Погляди", 3), ("Ленин", 6)])
def test_get_records_subject(dataset, subject, expected):
    records = list(dataset.get_records(subject=subject))
    assert len(records) == expected


@pytest.mark.parametrize(
    "author, expected", [("Скребицкий", 10), ("Михалков", 4), ("Чуковский", 1)]
)
def test_get_records_author(dataset, author, expected):
    records = list(dataset.get_records(author=author))
    assert len(records) == expected


@pytest.mark.parametrize(
    "bad_filter",
    [
        {"grade": 0},
        {"grade": 2},
        {"grade": 99},
        {"text_type": "Сталин"},
        {"min_len": 0},
        {"min_len": -1},
        {"max_len": -1},
        {"min_len": 10, "max_len": 5},
        {"limit": -1},
    ],
)
def test_bad_filters(dataset, bad_filter):
    with pytest.raises(ValueError):
        list(dataset.get_texts(**bad_filter))


def test_bad_filters_error_type(dataset):
    with pytest.raises(ParameterError):
        list(dataset.get_records(grade=0))


def test_records_order(dataset):
    numbers = [int(record["file"].name) for record in dataset]
    assert numbers == sorted(numbers)
    assert numbers[:3] == [1, 2, 3]


def test_empty_header_field(dataset):
    assert any(record["author"] == "" for record in dataset)


@pytest.mark.parametrize("subject, expected", [("(", 0), (".", 1), ("лиса", 6)])
def test_subject_escaped(dataset, subject, expected):
    assert len(list(dataset.get_records(subject=subject))) == expected
