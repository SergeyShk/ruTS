import tarfile
import zipfile
from pathlib import Path

import pytest

from ruts.utils import download_file, extract_archive, safe_divide, to_path

STOPWORDS_URL = (
    "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/stopwords.zip"
)


def test_to_path_is_str():
    path = "/usr/local/"
    assert to_path(path) == Path(path)


def test_to_path_is_path():
    path = Path("/usr/local/")
    assert to_path(path) == path


@pytest.mark.parametrize("path", [666, ["a", "b"], {"a": "b"}])
def test_to_path_type_error(path):
    with pytest.raises(TypeError):
        to_path(path)


@pytest.mark.network
def test_download_file(tmp_path):
    assert download_file(STOPWORDS_URL, dirpath=tmp_path) == str(tmp_path / "stopwords.zip")
    assert download_file(STOPWORDS_URL, filename="sw.zip", dirpath=tmp_path) == str(
        tmp_path / "sw.zip"
    )
    assert download_file(STOPWORDS_URL, dirpath=tmp_path) == ""


@pytest.mark.network
def test_download_file_runtime_error(tmp_path):
    url = "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/stopword.zip"
    with pytest.raises(RuntimeError):
        download_file(url, dirpath=tmp_path, force=True)


@pytest.fixture
def zip_archive(tmp_path):
    """ZIP, корневая директория которого совпадает с именем архива."""
    path = tmp_path / "stopwords.zip"
    with zipfile.ZipFile(path, mode="w") as archive:
        archive.writestr("stopwords/russian", "и\nв\nне\n")
        archive.writestr("stopwords/english", "a\nthe\n")
    return path


@pytest.fixture
def tar_archive(tmp_path):
    """TAR, корневая директория которого отличается от имени архива."""
    payload = tmp_path / "payload.txt"
    payload.write_text("razdel", encoding="utf-8")
    path = tmp_path / "razdel.tar.gz"
    with tarfile.open(path, mode="w:gz") as archive:
        archive.add(payload, arcname="razdel-0.5.0/setup.py")
        archive.add(payload, arcname="razdel-0.5.0/README.md")
    return path


def test_extract_archive_zip(zip_archive, tmp_path):
    extract_dir = tmp_path / "extract"
    assert extract_archive(zip_archive, extract_dir=extract_dir) == str(extract_dir / "stopwords")
    assert (extract_dir / "stopwords" / "russian").is_file()


def test_extract_archive_tar_renames_root(tar_archive):
    """Корневая директория архива приводится к имени архива без расширений."""
    extracted = extract_archive(tar_archive)
    assert extracted == str(tar_archive.parent / "razdel")
    assert (Path(extracted) / "setup.py").is_file()


def test_extract_archive_defaults_to_archive_dir(tar_archive):
    assert Path(extract_archive(tar_archive)).parent == tar_archive.parent


def test_extract_archive_not_an_archive(tmp_path):
    not_an_archive = tmp_path / "russian"
    not_an_archive.write_text("и\nв\nне\n", encoding="utf-8")
    assert extract_archive(not_an_archive) == str(tmp_path)


@pytest.mark.parametrize("args, result", [((1, 5), 0.2), ((1, 0), 0), ((1, "", -1), -1)])
def test_safe_divide(args, result):
    assert safe_divide(*args) == result
