import tarfile
import unicodedata
import zipfile
from pathlib import Path

import pytest

from ruts import utils as utils_module
from ruts.exceptions import DataFileError, DownloadError
from ruts.utils import (
    add_dash_rules,
    download_file,
    extract_archive,
    find_phrases,
    is_verbal_noun,
    iter_text_words,
    iter_tokens,
    normalize_yo,
    parse_word,
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


def test_download_file_partial_cleanup(tmp_path, monkeypatch):
    class BrokenResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, size=-1):
            raise OSError("обрыв соединения")

    calls = {}

    def fake_urlopen(request, timeout=None):
        calls["timeout"] = timeout
        return BrokenResponse()

    monkeypatch.setattr(utils_module.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(DownloadError):
        download_file("https://example.com/data.zip", dirpath=tmp_path, force=True)
    assert calls["timeout"] == utils_module.DOWNLOAD_TIMEOUT
    assert list(tmp_path.iterdir()) == []


def test_download_file_mkdir_error(tmp_path):
    blocker = tmp_path / "file"
    blocker.write_text("не директория", encoding="utf-8")
    with pytest.raises(DownloadError):
        download_file("https://example.com/data.zip", dirpath=blocker / "data")


def test_extract_archive_traversal(tmp_path):
    payload = tmp_path / "payload.txt"
    payload.write_text("evil", encoding="utf-8")
    archive = tmp_path / "evil.tar"
    with tarfile.open(archive, mode="w") as tar_file:
        tar_file.add(payload, arcname="../evil.txt")
    with pytest.raises(DataFileError):
        extract_archive(archive, tmp_path / "out")
    assert not (tmp_path / "evil.txt").exists()
    zipped = tmp_path / "evil.zip"
    with zipfile.ZipFile(zipped, "w") as zip_file:
        zip_file.writestr("../evil.txt", "evil")
    with pytest.raises(DataFileError):
        extract_archive(zipped, tmp_path / "zip_out")
    assert not (tmp_path / "evil.txt").exists()
    assert not (tmp_path / "zip_out" / "evil.txt").exists()
    broken = tmp_path / "broken.zip"
    with zipfile.ZipFile(broken, "w") as zip_file:
        zip_file.writestr("good.txt", "good")
    broken.write_bytes(b"\x00" * 4 + broken.read_bytes()[4:])
    with pytest.raises(DataFileError):
        extract_archive(broken, tmp_path / "broken_out")


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
    not_an_archive = tmp_path / "russian.tar.xz"
    not_an_archive.write_text("и\nв\nне\n", encoding="utf-8")
    with pytest.raises(DataFileError):
        extract_archive(not_an_archive)


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


def test_extract_archive_single_file(tmp_path):
    import zipfile

    nested = tmp_path / "nested.zip"
    with zipfile.ZipFile(nested, "w") as zip_file:
        zip_file.writestr("corpus-abc/corpus.xml", "<items />")
    extracted = Path(extract_archive(nested, tmp_path))
    assert extracted == tmp_path / "nested"
    assert (extracted / "corpus.xml").read_text() == "<items />"
    flat = tmp_path / "flat.zip"
    with zipfile.ZipFile(flat, "w") as zip_file:
        zip_file.writestr("corpus.xml", "<items />")
    assert extract_archive(flat, tmp_path / "flat") == str(tmp_path / "flat")
    assert (tmp_path / "flat" / "corpus.xml").read_text() == "<items />"


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


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("-Нет -сказал он.", ["-", "Нет", "-", "сказал", "он", "."]),
        ("он —сказал", ["он", "—", "сказал"]),
        ("смеяться—говорил он—над", ["смеяться", "—", "говорил", "он", "—", "над"]),
        ("Нет- сказал", ["Нет", "-", "сказал"]),
        ("--Нет --сказал", ["--", "Нет", "--", "сказал"]),
        ("во-первых кто-то рок-н-ролл", ["во-первых", "кто-то", "рок-н-ролл"]),
        ("-5 1990—1995", ["-", "5", "1990—1995"]),
        ("Г—в и N—ский", ["Г—в", "и", "N—ский"]),
        ("Нет-сказал", ["Нет-сказал"]),
        ("Он сказа́л—и ушёл", ["Он", "сказа́л", "—", "и", "ушёл"]),
        ("Да́- сказал", ["Да́", "-", "сказал"]),
        (
            unicodedata.normalize("NFD", "мой—её"),
            [unicodedata.normalize("NFD", "мой"), "—", unicodedata.normalize("NFD", "её")],
        ),
    ],
)
def test_iter_tokens(text, expected):
    tokens = list(iter_tokens(text))
    assert [token for _, _, token in tokens] == expected
    assert all(text[start:stop] == token for start, stop, token in tokens)


def test_add_dash_rules():
    import spacy

    nlp = spacy.blank("ru")
    add_dash_rules(nlp)
    add_dash_rules(nlp)
    for text in (
        "-Нет -сказал он.",
        "Нет- сказал",
        "Нет,-сказал",
        "сказал:—Нет",
        "«-Нет»",
        "да--сказал",
        "Да́- нет",
        "Да́,-нет",
        "Он—«Нет»",
        "он—(тихо)—сказал",
    ):
        assert [token.text for token in nlp(text)] == [token for _, _, token in iter_tokens(text)]
    assert [token.text for token in nlp("во-первых")] == ["во", "-", "первых"]


def test_add_dash_rules_other_tokenizer():
    import spacy

    nlp = spacy.blank("ru")
    tokenizer = nlp.tokenizer = lambda text: spacy.tokens.Doc(nlp.vocab, words=text.split())
    add_dash_rules(nlp)
    assert nlp.tokenizer is tokenizer


def test_iter_text_words_dialogue():
    assert list(iter_text_words("он —сказал")) == [(0, 2, "он"), (4, 10, "сказал")]
