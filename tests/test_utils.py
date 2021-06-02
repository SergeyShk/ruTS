import shutil
from pathlib import Path

import pytest

from ruts.utils import download_file, extract_archive, safe_divide, to_path


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


def test_download_file():
    url_zip = (
        "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/stopwords.zip"
    )
    url_tar = "https://bit.ly/30JYkQF"
    filename = "razdel.tar.gz"
    dirpath = "/tmp/ruts_download"
    assert download_file(url_zip, dirpath=dirpath) == "/tmp/ruts_download/stopwords.zip"
    assert (
        download_file(url_tar, filename=filename, dirpath=dirpath)
        == "/tmp/ruts_download/razdel.tar.gz"
    )
    assert download_file(url_zip, dirpath=dirpath) == ""


def test_download_file_runtime_error():
    url = "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/stopword.zip"
    dirpath = "/tmp/ruts_download"
    with pytest.raises(RuntimeError):
        download_file(url, dirpath=dirpath, force=True)


def test_extract_archive():
    archive_file_zip = "/tmp/ruts_download/stopwords.zip"
    archive_file_tar = "/tmp/ruts_download/razdel.tar.gz"
    extract_dir = "/tmp/ruts_extract"
    assert (
        extract_archive(archive_file_zip, extract_dir=extract_dir) == "/tmp/ruts_extract/stopwords"
    )
    assert extract_archive(archive_file_tar) == "/tmp/ruts_download/razdel"
    assert extract_archive("/tmp/ruts_extract/stopwords/russian") == "/tmp/ruts_extract/stopwords"
    shutil.rmtree("/tmp/ruts_extract", ignore_errors=True)
    shutil.rmtree("/tmp/ruts_download", ignore_errors=True)


@pytest.mark.parametrize("args, result", [((1, 5), 0.2), ((1, 0), 0), ((1, "", -1), -1)])
def test_safe_divide(args, result):
    assert safe_divide(*args) == result
