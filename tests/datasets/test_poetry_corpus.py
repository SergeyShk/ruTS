import tempfile
from pathlib import Path

import pytest

from ruts.datasets import PoetryCorpus
from ruts.datasets import poetry_corpus as poetry_corpus_module
from ruts.datasets.poetry_corpus import FILE_SHA256, FILENAME, load_records
from ruts.utils import sha256

XML = """<?xml version="1.0" encoding="UTF-8"?><items>
<item><themes></themes><author>Михаил Лермонтов</author><date_from>1829</date_from>
<text>Забывши волнения жизни мятежной,
Один жил в пустыне рыбак молодой.</text><name>Забывши волнения жизни мятежной...</name><date_to>1829</date_to></item>
<item><themes><item>О любви</item><item>Посвящения</item></themes><author>Александр Пушкин</author>
<date_from>1825</date_from><text>Я помню чудное мгновенье:
Передо мной явилась ты.</text><name>К***</name><date_to>1826</date_to></item>
<item><themes /><author>Александр Межиров</author><date_from /><text>Как я молод - и страх мне неведом.</text>
<name>Как я молод...</name><date_to /></item>
</items>
"""


def write_corpus(path: Path, content: str = XML) -> None:
    path.mkdir(parents=True, exist_ok=True)
    path.joinpath(FILENAME).write_text(content, encoding="utf-8")


@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    path = tmp_path_factory.mktemp("poetry")
    write_corpus(path)
    return PoetryCorpus(data_dir=path)


@pytest.fixture(scope="module")
def network_dataset():
    path = Path(tempfile.gettempdir()) / "ruts_data_poetry"
    path.mkdir(parents=True, exist_ok=True)
    return PoetryCorpus(data_dir=path)


@pytest.mark.network
def test_download(network_dataset):
    if network_dataset.filepath:
        pytest.skip(
            f"Не нужно загружать набор данных при каждом запуске теста {network_dataset.filepath}"
        )
    network_dataset.download()
    assert sha256(network_dataset._filepath) == FILE_SHA256
    records = list(network_dataset)
    assert len(records) == 16694
    assert len(network_dataset.authors) == 195
    assert len(network_dataset.themes) == 20


def test_oserror(tmp_path):
    dataset = PoetryCorpus(data_dir=tmp_path)
    assert dataset.filepath is None
    with pytest.raises(OSError):
        _ = list(dataset.get_texts())
    with pytest.raises(OSError):
        _ = dataset.authors


def test_info(dataset):
    assert dataset.info["Наименование"] == "poetry_corpus"
    assert dataset.info["license"] == "Apache-2.0"
    assert dataset.filepath == str(dataset._filepath)


def test_records(dataset):
    records = list(dataset)
    assert len(records) == 3
    assert records[0] == {
        "author": "Михаил Лермонтов",
        "title": "Забывши волнения жизни мятежной...",
        "themes": (),
        "year_from": 1829,
        "year_to": 1829,
        "text": "Забывши волнения жизни мятежной,\nОдин жил в пустыне рыбак молодой.",
    }
    assert records[1]["themes"] == ("О любви", "Посвящения")
    assert (records[1]["year_from"], records[1]["year_to"]) == (1825, 1826)
    assert records[2]["themes"] == ()
    assert (records[2]["year_from"], records[2]["year_to"]) == (None, None)
    assert list(dataset.get_records()) == records
    assert dataset.authors == {
        "Михаил Лермонтов": 1,
        "Александр Пушкин": 1,
        "Александр Межиров": 1,
    }
    assert dataset.themes == {"О любви": 1, "Посвящения": 1}


def test_filters(dataset):
    assert [r["title"] for r in dataset.get_records(author="пушкин")] == ["К***"]
    assert [r["title"] for r in dataset.get_records(theme="любв")] == ["К***"]
    assert [r["author"] for r in dataset.get_records(year_from=1830)] == []
    assert [r["author"] for r in dataset.get_records(year_from=1826)] == ["Михаил Лермонтов"]
    assert [r["author"] for r in dataset.get_records(year_to=1826)] == ["Александр Пушкин"]
    assert [r["author"] for r in dataset.get_records(year_from=1820, year_to=1830)] == [
        "Михаил Лермонтов",
        "Александр Пушкин",
    ]
    assert len(list(dataset.get_texts(min_len=45))) == 2
    assert len(list(dataset.get_texts(max_len=40))) == 1
    assert len(list(dataset.get_texts(limit=2))) == 2
    assert next(dataset.get_texts(author="Межиров")) == "Как я молод - и страх мне неведом."
    with pytest.raises(ValueError):
        _ = list(dataset.get_texts(year_from=1830, year_to=1820))
    with pytest.raises(ValueError):
        _ = list(dataset.get_texts(min_len=-1))
    with pytest.raises(ValueError):
        _ = list(dataset.get_texts(max_len=-1))
    with pytest.raises(ValueError):
        _ = list(dataset.get_texts(min_len=10, max_len=5))


def test_load_records_error(tmp_path):
    write_corpus(tmp_path, "<items><item><author>А</author>")
    with pytest.raises(ValueError):
        _ = list(load_records(tmp_path / FILENAME))


def test_load_records_without_title(tmp_path):
    write_corpus(
        tmp_path,
        "<items><item><author>А</author><name /><date_from /><date_to /><themes />"
        "<text>\n\nДень прошел, и ночь!..\nВторая строка.</text></item>"
        "<item><author>Б</author><text /></item></items>",
    )
    records = list(load_records(tmp_path / FILENAME))
    assert records[0]["title"] == "День прошел, и ночь..."
    assert records[0]["text"] == "День прошел, и ночь!..\nВторая строка."
    assert records[1]["title"] == ""


def test_download_checks_sha(tmp_path, monkeypatch):
    dataset = PoetryCorpus(data_dir=tmp_path)
    calls = []

    def fake_download(**kwargs):
        calls.append(kwargs["force"])
        write_corpus(tmp_path)
        return str(dataset._filepath)

    monkeypatch.setattr(poetry_corpus_module, "download_file", fake_download)
    with pytest.raises(RuntimeError):
        dataset.download()
    assert calls == [False, True]
    assert dataset.filepath is None
    monkeypatch.setattr(poetry_corpus_module, "FILE_SHA256", sha256_of(XML))
    dataset.download()
    assert dataset.filepath is not None
    assert len(list(dataset)) == 3


def test_download_retries_corrupted_file(tmp_path, monkeypatch):
    dataset = PoetryCorpus(data_dir=tmp_path)
    calls = []

    def fake_download(**kwargs):
        calls.append(kwargs["force"])
        write_corpus(tmp_path, XML[:100] if len(calls) == 1 else XML)
        return str(dataset._filepath)

    monkeypatch.setattr(poetry_corpus_module, "download_file", fake_download)
    monkeypatch.setattr(poetry_corpus_module, "FILE_SHA256", sha256_of(XML))
    dataset.download()
    assert calls == [False, True]
    assert len(list(dataset)) == 3


def sha256_of(content: str) -> str:
    import hashlib

    return hashlib.sha256(content.encode("utf-8")).hexdigest()
