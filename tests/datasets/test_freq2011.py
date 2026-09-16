import hashlib
import tempfile
import zipfile
from pathlib import Path

import pytest

from ruts.datasets import FreqDict
from ruts.datasets import freq2011 as freq2011_module
from ruts.datasets.freq2011 import ARCHIVE, FILENAME, Entry, load_entries, load_min_ipm
from ruts.utils import sha256

ROWS = (
    ("а", "conj", 8198.0, 100, 97, 32332),
    ("а", "part", 6.1, 59, 79, 128),
    ("Абрам", "s.PROP", 4.1, 65, 83, 126),
    ("еще", "adv", 2000.0, 100, 97, 20000),
    ("еще", "part", 409.4, 90, 90, 5000),
    ("кот", "s", 40.3, 98, 90, 947),
    ("на", "pr", 29000.0, 100, 98, 33000),
    ("на", "part", 1000.0, 80, 85, 3000),
    ("окно", "s", 100.0, 90, 80, 2000),
    ("птица", "s", 50.0, 80, 70, 1500),
    ("сидеть", "v", 200.0, 100, 95, 4000),
    ("и", "conj", 35000.0, 100, 98, 33000),
)


def write_dict(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    lines = ["Lemma\tPoS\tFreq(ipm)\tR\tD\tDoc"]
    lines += ["\t".join(str(value) for value in row) for row in ROWS]
    path.joinpath(FILENAME).write_text("\n".join(lines) + "\n", encoding="utf-8")


@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    path = tmp_path_factory.mktemp("dicts")
    write_dict(path)
    return FreqDict(data_dir=path)


@pytest.fixture(scope="module")
def network_dataset():
    path = Path(tempfile.gettempdir()) / "ruts_data_freq2011"
    path.mkdir(parents=True, exist_ok=True)
    return FreqDict(data_dir=path)


@pytest.mark.network
def test_download(network_dataset):
    if network_dataset.filepath:
        pytest.skip(
            f"Не нужно загружать словарь при каждом запуске теста {network_dataset.filepath}"
        )
    network_dataset.download()
    assert Path(network_dataset._filepath).is_file()
    assert len(network_dataset) > 50000
    assert network_dataset.lookup("кот").pos == ("s",)
    assert network_dataset.min_ipm == pytest.approx(0.4)


def test_oserror(tmp_path):
    dataset = FreqDict(data_dir=tmp_path)
    assert dataset.filepath is None
    with pytest.raises(OSError):
        _ = list(dataset.get_texts())
    with pytest.raises(OSError):
        _ = dataset.entries


def test_info(dataset):
    assert dataset.info["Наименование"] == "freq2011"
    assert dataset.info["author"] == "Ляшевская О. Н., Шаров С. А."
    assert "Азбуковник, 2009" in dataset.info["citation"]
    assert repr(dataset) == "Набор данных('freq2011')"
    assert dataset.filepath is not None


def test_records(dataset):
    records = list(dataset)
    assert len(records) == len(ROWS)
    assert records[0] == {
        "lemma": "а",
        "pos": "conj",
        "ipm": 8198.0,
        "range": 100,
        "dispersion": 97,
        "docs": 32332,
    }
    assert [record["lemma"] for record in dataset.get_records(pos="s")] == ["кот", "окно", "птица"]
    assert [record["lemma"] for record in dataset.get_records(min_ipm=2000)] == [
        "а",
        "еще",
        "на",
        "и",
    ]
    assert list(dataset.get_texts(pos="s", min_ipm=41, limit=2)) == ["окно", "птица"]


def test_entries(dataset):
    assert len(dataset) == 9
    assert dataset.lookup("а") == Entry("а", ("conj", "part"), 8204.1, 100, 97, 32332)
    assert dataset.lookup("на") == Entry("на", ("pr", "part"), 30000.0, 100, 98, 33000)
    assert dataset.lookup("Ещё") == Entry("еще", ("adv", "part"), 2409.4, 100, 97, 20000)
    assert dataset.lookup("абрам") == Entry("абрам", ("s.PROP",), 4.1, 65, 83, 126)
    assert dataset.lookup("собака") is None


def test_ipm_and_contains(dataset):
    assert dataset.ipm("КОТ") == 40.3
    assert dataset.ipm("собака") == 0.0
    assert dataset.min_ipm == 4.1
    assert "кот" in dataset
    assert "Ещё" in dataset
    assert "собака" not in dataset
    assert 5 not in dataset


def make_archive(path: Path, content: bytes | None = None) -> Path:
    archive = path / ARCHIVE
    if content is not None:
        archive.write_bytes(content)
        return archive
    csv_dir = path / "src"
    write_dict(csv_dir)
    with zipfile.ZipFile(archive, "w") as zip_file:
        zip_file.write(csv_dir / FILENAME, FILENAME)
        zip_file.writestr("freqrnc_readme.txt", "readme")
    return archive


def test_entries_cached(dataset):
    other = FreqDict(data_dir=dataset.data_dir)
    assert other.entries is dataset.entries
    assert load_entries(dataset._filepath) is dataset.entries
    assert dataset.min_ipm == 4.1
    assert load_min_ipm.cache_info().hits >= 1


def test_check_data_once(tmp_path, monkeypatch):
    write_dict(tmp_path)
    dataset = FreqDict(data_dir=tmp_path)
    calls = []
    original = dataset.check_data
    monkeypatch.setattr(dataset, "check_data", lambda: calls.append(1) or original())
    with pytest.raises(OSError):
        _ = FreqDict(data_dir=tmp_path / "missing").entries
    assert dataset.ipm("кот") == 40.3
    assert dataset.lookup("окно") is not None
    assert dataset.min_ipm == 4.1
    assert "кот" in dataset
    assert calls == [1]


def test_download_corrupted(tmp_path, monkeypatch):
    def fake_download(url, filename, dirpath, force):
        return str(make_archive(Path(dirpath), b"<html>not an archive</html>"))

    monkeypatch.setattr(freq2011_module, "download_file", fake_download)
    dataset = FreqDict(data_dir=tmp_path)
    with pytest.raises(RuntimeError):
        dataset.download()
    assert not (tmp_path / ARCHIVE).exists()
    assert dataset.filepath is None


def test_download_extracts_existing_archive(tmp_path, monkeypatch):
    archive = make_archive(tmp_path)
    monkeypatch.setattr(freq2011_module, "ARCHIVE_SHA256", sha256(archive))
    monkeypatch.setattr(freq2011_module, "download_file", lambda **kwargs: "")
    dataset = FreqDict(data_dir=tmp_path)
    assert dataset.filepath is None
    dataset.download()
    assert dataset.filepath is not None
    assert len(dataset) == 9
    dataset.download()
    assert dataset.lookup("кот").ipm == 40.3


def test_download_force_reloads(tmp_path, monkeypatch):
    archive = make_archive(tmp_path)
    monkeypatch.setattr(freq2011_module, "ARCHIVE_SHA256", sha256(archive))
    monkeypatch.setattr(freq2011_module, "download_file", lambda **kwargs: str(archive))
    dataset = FreqDict(data_dir=tmp_path)
    dataset.download()
    before = dataset.entries
    assert dataset.min_ipm == 4.1
    dataset.download(force=True)
    assert dataset.entries == before
    assert dataset.entries is not before
    assert load_min_ipm.cache_info().currsize == 0 or dataset.min_ipm == 4.1


def test_sha256(tmp_path):
    path = tmp_path / "file.txt"
    path.write_bytes(b"ruts")
    assert sha256(path) == hashlib.sha256(b"ruts").hexdigest()
    assert sha256(tmp_path / "missing") == ""
