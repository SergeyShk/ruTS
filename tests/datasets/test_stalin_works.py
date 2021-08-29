import os

import pytest

from ruts.datasets.stalin_works import StalinWorks


@pytest.fixture(scope="module")
def dataset():
    path = "/tmp/ruts_data_sw"
    os.makedirs(path, exist_ok=True)
    dataset_ = StalinWorks(data_dir=path)
    return dataset_


def test_download(dataset):
    if dataset.filepath:
        pytest.skip(f"Не нужно загружать набор данных при каждом запуске теста {dataset.filepath}")
    dataset.download()
    assert os.path.isfile(dataset._filepath)
    assert os.path.isdir(dataset.data_dir)


def test_oserror():
    dataset = StalinWorks(data_dir="/tmp")
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
    assert all(len(text) < max_len for text in dataset.get_texts(max_len=max_len, limit=1))


def test_get_records(dataset):
    fields = ["volume", "year", "type", "is_translation", "source", "subject", "topic"]
    for record in dataset.get_records(limit=2):
        assert isinstance(record, dict)
        assert all(field in record.keys() for field in fields)


@pytest.mark.parametrize("volume, expected", [(1, 62), (5, 63), (10, 38)])
def test_get_records_volume(dataset, volume, expected):
    records = list(dataset.get_records(volume=volume))
    assert len(records) == expected


@pytest.mark.parametrize("year, expected", [(1917, 124), (1937, 14), (1945, 22)])
def test_get_records_year(dataset, year, expected):
    records = list(dataset.get_records(year=year))
    assert len(records) == expected


@pytest.mark.parametrize(
    "text_type, expected", [("Доклад", 367), ("Письмо", 101), ("Телеграмма", 20)]
)
def test_get_records_text_type(dataset, text_type, expected):
    records = list(dataset.get_records(text_type=text_type))
    assert len(records) == expected


@pytest.mark.parametrize("is_translation, expected", [(True, 63), (False, 1180)])
def test_get_records_is_translation(dataset, is_translation, expected):
    records = list(dataset.get_records(is_translation=is_translation))
    assert len(records) == expected


@pytest.mark.parametrize(
    "source, expected", [("Правда", 692), ("Большевик", 49), ("Коммунист", 42)]
)
def test_get_records_source(dataset, source, expected):
    records = list(dataset.get_records(source=source))
    assert len(records) == expected


@pytest.mark.parametrize(
    "subject, expected", [("Съезд", 161), ("Интервью", 3), ("Приветствие", 20)]
)
def test_get_records_subject(dataset, subject, expected):
    records = list(dataset.get_records(subject=subject))
    assert len(records) == expected


@pytest.mark.parametrize("topic, expected", [("I", 330), ("2", 38), ("Доклад", 18)])
def test_get_records_topic(dataset, topic, expected):
    records = list(dataset.get_records(topic=topic))
    assert len(records) == expected


@pytest.mark.parametrize(
    "bad_filter",
    [
        {"volume": 99},
        {"text_type": "Фильм"},
        {"min_len": -1},
        {"max_len": -1},
        {"min_len": 10, "max_len": 5},
    ],
)
def test_bad_filters(dataset, bad_filter):
    with pytest.raises(ValueError):
        list(dataset.get_texts(**bad_filter))
