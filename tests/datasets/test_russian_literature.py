import hashlib
import tempfile
import zipfile
from pathlib import Path

import pytest

from ruts.datasets import RussianLiterature
from ruts.datasets import russian_literature as russian_literature_module
from ruts.datasets.russian_literature import (
    ARCHIVE,
    ARCHIVE_SHA256,
    AUTHORS,
    GENRES,
    NAME,
    load_years,
    parse_years,
    read_text,
)
from ruts.utils import sha256

TEXTS = {
    "prose/Chekhov/Агафья.txt": "Агафья. Рассказ о деревне.",
    "prose/Chekhov/Альбом.txt": "Альбом. Короткий рассказ.",
    "poems/Pushkin/19 октября.txt": "Роняет лес багряный свой убор.",
    "poems/Pushkin/Борис Годунов.txt": "Драма в стихах о смутном времени.",
    "poems/Lermontov/Парус.txt": "Белеет парус одинокий.",
    "publicism/Tolstoy/Не могу молчать.txt": "Статья о смертной казни.",
}
INFOS = {
    "prose/Chekhov/info.csv": "name,year\nАгафья,1886\nАльбом,1885\nНет файла,1887\n",
    "poems/Pushkin/info.csv": 'name,year\n19 октября,1825\n"Борис Годунов",1824-1825\n',
    "publicism/Tolstoy/info.csv": "name,year\nНе могу молчать,без даты\n",
}


def write_dataset(path: Path) -> Path:
    root = path / NAME
    for name, text in TEXTS.items():
        file = root / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding="utf-8")
    for name, content in INFOS.items():
        (root / name).write_text(content, encoding="utf-8")
    (root / "poems/Pushkin/Руслан и Людмила.txt").write_bytes("Поэма.".encode("cp1251"))
    return root


@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    path = tmp_path_factory.mktemp("literature")
    write_dataset(path)
    return RussianLiterature(data_dir=path)


@pytest.fixture(scope="module")
def network_dataset():
    path = Path(tempfile.gettempdir()) / "ruts_data_literature"
    path.mkdir(parents=True, exist_ok=True)
    return RussianLiterature(data_dir=path)


@pytest.mark.network
def test_download(network_dataset):
    if network_dataset.filepath:
        pytest.skip(
            f"Не нужно загружать набор данных при каждом запуске теста {network_dataset.filepath}"
        )
    network_dataset.download()
    assert sha256(network_dataset._filepath) == ARCHIVE_SHA256
    records = list(network_dataset)
    assert len(records) == 373
    assert {record["author"] for record in records} == set(AUTHORS.values())


def test_oserror(tmp_path):
    dataset = RussianLiterature(data_dir=tmp_path)
    assert dataset.filepath is None
    with pytest.raises(OSError):
        _ = list(dataset.get_texts())


def test_info(dataset):
    assert dataset.info["Наименование"] == "russian_literature"
    assert dataset.info["url"] == "https://github.com/d0rj/RusLit"
    assert dataset.genres == GENRES
    assert dataset.authors["Chekhov"] == "Антон Чехов"


def test_records(dataset):
    records = list(dataset)
    assert [record["title"] for record in records] == [
        "Агафья",
        "Альбом",
        "Парус",
        "19 октября",
        "Борис Годунов",
        "Руслан и Людмила",
        "Не могу молчать",
    ]
    assert records[0] == {
        "genre": "prose",
        "author": "Антон Чехов",
        "title": "Агафья",
        "year_from": 1886,
        "year_to": 1886,
        "text": "Агафья. Рассказ о деревне.",
        "file": dataset._dirpath / "prose/Chekhov/Агафья.txt",
    }
    assert (records[2]["year_from"], records[2]["year_to"]) == (None, None)
    assert (records[4]["year_from"], records[4]["year_to"]) == (1824, 1825)
    assert records[5]["text"] == "Поэма."
    assert (records[6]["year_from"], records[6]["year_to"]) == (None, None)
    assert list(dataset.get_records()) == records


def test_filters(dataset):
    assert [r["title"] for r in dataset.get_records(genre="publicism")] == ["Не могу молчать"]
    assert [r["title"] for r in dataset.get_records(author="лермонтов")] == ["Парус"]
    assert [r["title"] for r in dataset.get_records(year_from=1885)] == ["Агафья", "Альбом"]
    assert [r["title"] for r in dataset.get_records(year_to=1825)] == [
        "19 октября",
        "Борис Годунов",
    ]
    assert [r["title"] for r in dataset.get_records(year_from=1825, year_to=1825)] == [
        "19 октября"
    ]
    assert list(dataset.get_texts(genre="poems", min_len=30, limit=1)) == [
        "Роняет лес багряный свой убор."
    ]
    assert len(list(dataset.get_texts(max_len=10))) == 1
    with pytest.raises(ValueError):
        _ = list(dataset.get_texts(genre="drama"))
    with pytest.raises(ValueError):
        _ = list(dataset.get_texts(year_from=1900, year_to=1800))
    with pytest.raises(ValueError):
        _ = list(dataset.get_texts(min_len=-1))
    with pytest.raises(ValueError):
        _ = list(dataset.get_texts(max_len=-1))
    with pytest.raises(ValueError):
        _ = list(dataset.get_texts(min_len=5, max_len=1))


def test_helpers(tmp_path):
    assert parse_years("1825") == (1825, 1825)
    assert parse_years(" 1824-1825 ") == (1824, 1825)
    assert parse_years("") == (None, None)
    assert parse_years("около 1830") == (None, None)
    info = tmp_path / "info.csv"
    info.write_text(
        'name,year\nВчерашний день, часу в шестом...,1848\n"Мороз, красный нос",1862-1864\nбез запятой\n',
        encoding="utf-8",
    )
    assert load_years(info) == {
        "Вчерашний день, часу в шестом...": (1848, 1848),
        "Мороз, красный нос": (1862, 1864),
    }
    assert load_years(tmp_path / "missing.csv") == {}
    bom = tmp_path / "bom.txt"
    bom.write_bytes("﻿Текст ".encode())
    assert read_text(bom) == "Текст"
    binary = tmp_path / "binary.txt"
    binary.write_bytes(bytes(range(256)))
    with pytest.raises(ValueError):
        read_text(binary)


def make_archive(path: Path) -> Path:
    archive = path / ARCHIVE
    with zipfile.ZipFile(archive, "w") as zip_file:
        for name, text in TEXTS.items():
            zip_file.writestr(f"RusLit-abc/{name}", text)
        for name, content in INFOS.items():
            zip_file.writestr(f"RusLit-abc/{name}", content)
    return archive


def test_download_extracts(tmp_path, monkeypatch):
    dataset = RussianLiterature(data_dir=tmp_path)
    archive = make_archive(tmp_path)
    monkeypatch.setattr(russian_literature_module, "download_file", lambda **kwargs: str(archive))
    with pytest.raises(RuntimeError):
        dataset.download()
    assert dataset.filepath is None
    archive = make_archive(tmp_path)
    monkeypatch.setattr(russian_literature_module, "ARCHIVE_SHA256", sha256(archive))
    dataset.download()
    assert dataset.filepath is not None
    assert [record["title"] for record in dataset.get_records(genre="poems")] == [
        "Парус",
        "19 октября",
        "Борис Годунов",
    ]
    assert len(list(dataset)) == len(TEXTS)
    monkeypatch.setattr(russian_literature_module, "download_file", lambda **kwargs: "")
    dataset.download()
    assert len(list(dataset)) == len(TEXTS)


def test_sha256_helper(tmp_path):
    path = tmp_path / "file"
    path.write_bytes(b"ruts")
    assert sha256(path) == hashlib.sha256(b"ruts").hexdigest()
