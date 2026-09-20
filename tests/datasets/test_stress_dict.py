import tempfile
import zipfile
from pathlib import Path

import pytest

from ruts.datasets import StressDict
from ruts.datasets import stress_dict as stress_dict_module
from ruts.datasets.stress_dict import (
    ARCHIVE,
    FILENAME,
    StressIndex,
    load_index,
    stress_from_accented,
)
from ruts.exceptions import DatasetNotFoundError, ParameterError
from ruts.utils import sha256

ROWS = (
    ("-де", "-д^е"),
    ("а", "^а"),
    ("б", "б"),
    ("голова", "голов^а"),
    ("головы", "г^оловы"),
    ("еж", "^еж"),
    ("еще", "^еще"),
    ("замок", "зам^ок"),
    ("корова", "кор^ова"),
    ("кто-нибудь", "кт^о-нибудь"),
    ("окно", "окн^о"),
    ("я", "^я"),
)


def write_dict(path: Path, rows=ROWS, trailing_newline: bool = True) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    text = "\n".join("\t".join(row) for row in rows)
    if trailing_newline:
        text += "\n"
    filepath = path.joinpath(FILENAME)
    filepath.write_text(text, encoding="utf-8")
    return filepath


@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    path = tmp_path_factory.mktemp("dicts")
    write_dict(path)
    return StressDict(data_dir=path)


@pytest.fixture(scope="module")
def network_dataset():
    path = Path(tempfile.gettempdir()) / "ruts_data_stress_dict"
    path.mkdir(parents=True, exist_ok=True)
    return StressDict(data_dir=path)


@pytest.mark.network
def test_download(network_dataset):
    if network_dataset.filepath:
        pytest.skip(
            f"Не нужно загружать словарь при каждом запуске теста {network_dataset.filepath}"
        )
    network_dataset.download()
    assert Path(network_dataset._filepath).is_file()
    assert len(network_dataset) > 1_600_000
    assert network_dataset.lookup("корова") == 1
    assert network_dataset.lookup("ёжик") == 0


def test_info(dataset):
    assert dataset.info["Наименование"] == "stress_dict"
    assert dataset.info["author"] == "Козиев И."
    assert dataset.info["license"] == "CC0-1.0"
    assert repr(dataset) == "Набор данных('stress_dict')"
    assert dataset.filepath is not None


def test_not_found(tmp_path):
    dataset = StressDict(data_dir=tmp_path)
    assert dataset.filepath is None
    with pytest.raises(DatasetNotFoundError, match=r"sd\.download"):
        dataset.check_data()
    with pytest.raises(OSError):
        _ = list(dataset.get_texts())
    with pytest.raises(OSError):
        dataset.lookup("корова")
    with pytest.raises(OSError):
        _ = len(dataset)


def test_records(dataset):
    records = list(dataset)
    assert len(records) == len(ROWS)
    assert records[0] == {"word": "-де", "stress": 0}
    assert records[2] == {"word": "б", "stress": None}
    assert list(dataset.get_records(limit=2)) == [
        {"word": "-де", "stress": 0},
        {"word": "а", "stress": 0},
    ]
    assert list(dataset.get_texts(limit=3)) == ["-де", "а", "б"]
    assert len(list(dataset.get_texts())) == len(ROWS)
    with pytest.raises(ParameterError):
        _ = list(dataset.get_texts(limit=-1))


def test_lookup(dataset):
    assert dataset.lookup("корова") == 1
    assert dataset.lookup("Корова") == 1
    assert dataset.lookup("голова") == 2
    assert dataset.lookup("головы") == 0
    assert dataset.lookup("ёж") == 0
    assert dataset.lookup("ещё") == 0
    assert dataset.lookup("кто-нибудь") == 0
    assert dataset.lookup("-де") == 0
    assert dataset.lookup("я") == 0
    assert dataset.lookup("б") is None
    assert dataset.lookup("собака") is None
    assert dataset.lookup("") is None
    assert dataset.lookup("яя") is None


def test_contains_and_len(dataset):
    assert len(dataset) == len(ROWS)
    assert "корова" in dataset
    assert "Ёж" in dataset
    assert "б" in dataset
    assert "собака" not in dataset
    assert 5 not in dataset


def test_stress_from_accented():
    assert stress_from_accented("кор^ова") == 1
    assert stress_from_accented("^а") == 0
    assert stress_from_accented("б") is None
    assert stress_from_accented("") is None
    assert stress_from_accented("кт^о-нибудь") == 0


def test_index_without_trailing_newline(tmp_path):
    write_dict(tmp_path, trailing_newline=False)
    dataset = StressDict(data_dir=tmp_path)
    assert len(dataset) == len(ROWS)
    assert dataset.lookup("я") == 0
    assert dataset.lookup("-де") == 0


def test_index_malformed_lines():
    index = StressIndex("а\t^а\nб\nв\tв\n".encode())
    assert len(index) == 3
    assert index.find("а") == "^а"
    assert index.find("б") == ""
    assert index.find("в") == "в"
    assert index.find("г") is None
    assert len(StressIndex(b"")) == 1
    assert StressIndex(b"").find("") == ""


def test_index_cached(dataset):
    other = StressDict(data_dir=dataset.data_dir)
    assert other._index is dataset._index
    assert load_index(dataset._filepath) is dataset._index


def make_archive(path: Path, content: bytes | None = None) -> Path:
    archive = path / ARCHIVE
    if content is not None:
        archive.write_bytes(content)
        return archive
    filepath = write_dict(path / "src")
    with zipfile.ZipFile(archive, "w") as zip_file:
        zip_file.write(filepath, FILENAME)
    return archive


def test_download_corrupted(tmp_path, monkeypatch):
    def fake_download(url, filename, dirpath, force):
        return str(make_archive(Path(dirpath), b"<html>not an archive</html>"))

    monkeypatch.setattr(stress_dict_module, "download_file", fake_download)
    dataset = StressDict(data_dir=tmp_path)
    with pytest.raises(RuntimeError):
        dataset.download()
    assert not (tmp_path / ARCHIVE).exists()
    assert dataset.filepath is None


def test_download_extracts_existing_archive(tmp_path, monkeypatch):
    archive = make_archive(tmp_path)
    monkeypatch.setattr(stress_dict_module, "ARCHIVE_SHA256", sha256(archive))
    monkeypatch.setattr(stress_dict_module, "download_file", lambda **kwargs: "")
    dataset = StressDict(data_dir=tmp_path)
    assert dataset.filepath is None
    dataset.download()
    assert dataset.filepath is not None
    assert len(dataset) == len(ROWS)
    dataset.download()
    assert dataset.lookup("корова") == 1


def test_download_force_reloads(tmp_path, monkeypatch):
    archive = make_archive(tmp_path)
    monkeypatch.setattr(stress_dict_module, "ARCHIVE_SHA256", sha256(archive))
    monkeypatch.setattr(stress_dict_module, "download_file", lambda **kwargs: str(archive))
    dataset = StressDict(data_dir=tmp_path)
    dataset.download()
    before = dataset._index
    dataset.download(force=True)
    assert dataset._index is not before
    assert dataset.lookup("окно") == 1
