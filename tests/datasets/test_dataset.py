import os
import shutil
import subprocess
import sys
from pathlib import Path

import anyts.datasets
import pytest

from ruts import datasets
from ruts.datasets import (
    SovChLit,
    StalinWorks,
    TextsByGrade,
    freq2011,
    poetry_corpus,
    sov_chrest_lit,
    stalin_works,
    stress_dict,
    texts_by_grade,
)
from ruts.datasets.dataset import Dataset, substring_filter
from ruts.exceptions import DatasetNotFoundError, DownloadError, ParameterError

BUNDLED_DIR = Path(__file__).parents[2] / "ruts" / "datasets" / "data"


class TestErrorDataset(Dataset):
    def __init__(self, name, meta):
        super().__init__(name, meta)


class TestDataset(Dataset):
    def __init__(self, name, meta):
        super().__init__(name, meta)

    def __iter__(self):
        super().__iter__()

    def check_data(self):
        super().check_data()

    def get_texts(self, *args):
        super().get_texts()

    def get_records(self, *args):
        super().get_records()

    def download(self):
        super().download()


@pytest.fixture(scope="module")
def dataset():
    return TestDataset("test", {"a": 1, "b": 2})


def test_iter_non_implement_error(dataset):
    with pytest.raises(NotImplementedError):
        dataset.__iter__()


def test_repr(dataset):
    assert dataset.__repr__() == "Набор данных('test')"


def test_info(dataset):
    assert list(dataset.info.keys()) == ["Наименование", "a", "b"]


def test_type_error():
    with pytest.raises(TypeError):
        TestErrorDataset("", {})


@pytest.mark.parametrize(
    "name", ["__iter__", "check_data", "get_texts", "get_records", "download"]
)
def test_methods(dataset, name):
    assert hasattr(dataset, name)
    with pytest.raises(NotImplementedError):
        getattr(dataset, name)()


def test_data_directory_of_the_environment(tmp_path):
    code = (
        "from ruts.datasets import FreqDict, SovChLit;"
        "print(FreqDict().data_dir);"
        "print(SovChLit().data_dir)"
    )
    environment = {**os.environ, "RUTS_DATA_DIR": str(tmp_path)}
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True, env=environment
    )
    assert result.stdout.splitlines() == [
        str((tmp_path / "dicts").resolve()),
        str((tmp_path / "texts").resolve()),
    ]


def test_substring_filter_folds_case_and_yo():
    match = substring_filter("author", "федор")
    assert match({"author": "Фёдор Достоевский"})
    assert substring_filter("author", "ФЁДОР")({"author": "Федор Сологуб"})
    assert not match({"author": None})
    # й - отдельная буква, а не и с диакритикой
    assert not substring_filter("author", "николаи")({"author": "Николай Некрасов"})
    with pytest.raises(ParameterError):
        substring_filter("author", 42)


def test_downloads_send_the_user_agent_of_ruts(tmp_path, monkeypatch):
    agents = []

    def fake_download(url, dirpath, filename=None, force=False, user_agent=None):
        agents.append(user_agent)
        raise DownloadError("Нет сети")

    for module in (anyts.datasets, freq2011, poetry_corpus, stress_dict):
        monkeypatch.setattr(module, "download_file", fake_download)
    names = datasets.__all__
    for name in names:
        with pytest.raises(DownloadError):
            getattr(datasets, name)(data_dir=tmp_path).download()
    assert agents == ["ruTS"] * len(names)


@pytest.mark.parametrize(
    ("module", "dataset_class"),
    [(sov_chrest_lit, SovChLit), (stalin_works, StalinWorks), (texts_by_grade, TextsByGrade)],
)
def test_incomplete_dataset_is_extracted_again(tmp_path, module, dataset_class):
    dataset = dataset_class(data_dir=tmp_path)
    shutil.copy(BUNDLED_DIR / module.ARCHIVE, dataset._filepath)
    dataset.download()
    assert sum(1 for _ in dataset) == sum(module.FILE_COUNTS.values())
    # Директории уровней остаются, как после очистки временных файлов системой
    files = sorted(path for path in dataset._dirpath.rglob("*") if path.is_file())
    files[0].unlink()
    with pytest.raises(DatasetNotFoundError, match="неполон"):
        dataset.check_data()
    for path in files[1:]:
        path.unlink()
    with pytest.raises(DatasetNotFoundError):
        list(dataset.get_texts())
    dataset.download()
    assert sum(1 for _ in dataset) == sum(module.FILE_COUNTS.values())
