import os

import pytest

from ruts.datasets.sov_chrest_lit import SovChLit


@pytest.fixture(scope="module")
def dataset():
    path = "/tmp/ruts_data_scl"
    os.makedirs(path, exist_ok=True)
    dataset_ = SovChLit(data_dir=path)
    return dataset_


def test_download(dataset):
    if dataset.filepath:
        pytest.skip(f"Не нужно загружать набор данных при каждом запуске теста {dataset.filepath}")
    dataset.download()
    assert os.path.isfile(dataset._filepath)
    assert os.path.isdir(dataset.data_dir)


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
    assert all(len(text) < max_len for text in dataset.get_texts(max_len=max_len, limit=5))


def test_get_records(dataset):
    fields = ["grade", "book", "year", "category", "type", "subject", "author"]
    for record in dataset.get_records(limit=2):
        assert isinstance(record, dict)
        assert all(field in record.keys() for field in fields)


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


@pytest.mark.parametrize("category, expected", [("Лето", 13), ("Весна", 53), ("Зима", 21)])
def test_get_records_category(dataset, category, expected):
    records = list(dataset.get_records(category=category))
    assert len(records) == expected


@pytest.mark.parametrize(
    "text_type, expected", [("Рассказ", 109), ("Басня", 4), ("Стихотворение", 37)]
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
        {"grade": 99},
        {"text_type": "Сталин"},
        {"min_len": -1},
        {"max_len": -1},
        {"min_len": 10, "max_len": 5},
    ],
)
def test_bad_filters(dataset, bad_filter):
    with pytest.raises(ValueError):
        list(dataset.get_texts(**bad_filter))
