import tarfile
import zipfile
from pathlib import Path

import pytest

from ruts.utils import (
    download_file,
    extract_archive,
    find_phrases,
    is_punctuation,
    is_verbal_noun,
    iter_doc_words,
    iter_text_words,
    normalize_yo,
    parse_word,
    safe_divide,
    to_path,
)

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
    path = tmp_path / "stopwords.zip"
    with zipfile.ZipFile(path, mode="w") as archive:
        archive.writestr("stopwords/russian", "и\nв\nне\n")
        archive.writestr("stopwords/english", "a\nthe\n")
    return path


@pytest.fixture
def tar_archive(tmp_path):
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


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("!", True),
        ("?!", True),
        ("!..", True),
        ("--", True),
        ("…", True),
        ("–", True),
        ("№", True),
        ("„", True),
        ("’", True),
        ("«»", True),
        ("+", True),
        ("слово", False),
        ("какого-либо", False),
        ("3-й", False),
        ("100", False),
        ("a", False),
    ],
)
def test_is_punctuation(token, expected):
    assert is_punctuation(token) is expected


def test_parse_word_cached():
    parse_word.cache_clear()
    assert parse_word("рублей").normal_form == "рубль"
    assert parse_word("рублей").tag.POS == "NOUN"
    assert parse_word.cache_info().hits == 1
    assert parse_word.cache_info().misses == 1


@pytest.mark.parametrize(
    ("lemma", "expected"),
    [
        ("повышение", True),
        ("Участие", True),
        ("реализация", True),
        ("производство", True),
        ("руководство", True),
        ("содействие", True),
        ("житьё", True),
        ("здание", True),
        ("качество", False),
        ("правительство", False),
        ("кот", False),
        ("проверка", False),
        ("ние", True),
        ("", False),
    ],
)
def test_is_verbal_noun(lemma, expected):
    assert is_verbal_noun(lemma) is expected


def test_normalize_yo():
    assert normalize_yo("Учёт") == "учет"
    assert normalize_yo("путем") == "путем"


def test_find_phrases():
    words = ["В", "целях", "повышения", "в", "связи", "с", "этим", "путём", "проверки", "в"]
    phrases = ["в целях", "в связи с", "путем", "в связи", "в"]
    assert find_phrases(words, phrases) == [(0, 2), (3, 6), (7, 8), (9, 10)]
    assert find_phrases(words, []) == []
    assert find_phrases(words, ["", "  "]) == []
    assert find_phrases(["кот", "дом"], ["дом", ""]) == [(1, 2)]
    assert find_phrases([], phrases) == []
    assert find_phrases(["связи", "с"], ["в связи с"]) == []
    assert find_phrases(["в", "связи"], ["в связи с", "в"]) == [(0, 1)]


def test_extract_archive_dotted_names(tmp_path):
    import zipfile

    archive = tmp_path / "dotted.zip"
    with zipfile.ZipFile(archive, "w") as zip_file:
        zip_file.writestr("dotted-abc/README.md", "readme")
        zip_file.writestr("dotted-abc/a/Ма-аленькая!....txt", "текст")
        zip_file.writestr("dotted-abc/a/обычный.txt", "текст")
    extracted = Path(extract_archive(archive, tmp_path))
    assert extracted == tmp_path / "dotted"
    assert sorted(path.name for path in extracted.joinpath("a").iterdir()) == [
        "Ма-аленькая!....txt",
        "обычный.txt",
    ]
    assert extracted.joinpath("a", "Ма-аленькая!....txt").read_text(encoding="utf-8") == "текст"


def test_iter_text_words():
    assert list(iter_text_words("Во-первых, кот - т.е. «зверь»!")) == [
        (0, 9, "Во-первых"),
        (11, 14, "кот"),
        (17, 18, "т"),
        (19, 20, "е"),
        (23, 28, "зверь"),
    ]
    assert list(iter_text_words("")) == []


def test_iter_doc_words():
    import spacy

    doc = spacy.blank("ru")("Во-первых, кот -\nсобака - дом-музей, кое-как-нибудь.")
    assert list(iter_doc_words(doc)) == [
        (0, 9, "Во-первых"),
        (11, 14, "кот"),
        (17, 23, "собака"),
        (26, 35, "дом-музей"),
        (37, 51, "кое-как-нибудь"),
    ]
    assert list(iter_doc_words(spacy.blank("ru")("- . ,"))) == []
