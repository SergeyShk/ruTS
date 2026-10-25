import re
import shutil
from pathlib import Path
from statistics import median

import anyts.datasets as dataset_module
import numpy as np
import pytest
from anyts.datasets import extract_archive
from scipy.stats import spearmanr

from ruts import BasicStats, ReadabilityStats
from ruts.constants import (
    GRADE_AGE_LEVELS,
    LEVEL_NORMS,
    READABILITY_GRADE_STATS,
    READABILITY_PRESETS,
    READABILITY_STATS_DESC,
)
from ruts.datasets import (
    sov_chrest_lit as sov_chrest_lit_module,
    texts_by_grade as texts_by_grade_module,
)
from ruts.datasets.sov_chrest_lit import SovChLit
from ruts.datasets.texts_by_grade import GRADES, TextsByGrade
from ruts.exceptions import DownloadError, ParameterError
from ruts.readability_stats import level_features

BUNDLED_ARCHIVE = (
    Path(__file__).parents[2] / "ruts" / "datasets" / "data" / texts_by_grade_module.ARCHIVE
)
DOCS = Path(__file__).parents[2] / "docs"
FORMULA_ROW = re.compile(
    r"^\| (?P<label>[^|]+?) \| (?P<rho>−?[\d.]+) \| (?P<mae>[\d.]+|-) \|$", re.MULTILINE
)
NORM_ROW = re.compile(r"^\|[^|]+\| \d+ \|(?: [\d.]+-[\d.]+ \|){4}$", re.MULTILINE)
PRESET_ROW = re.compile(
    r"^\| (?P<group>[^|]+?) \| (?P<n>\d+) \| (?P<plainrussian>[\d.]+) \| (?P<fiction>[\d.]+)"
    r" \| (?P<academic>[\d.]+) \|$",
    re.MULTILINE,
)


@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    dataset = TextsByGrade(data_dir=tmp_path_factory.mktemp("ruts_data_tbg"))
    # В репозитории архив лежит рядом с кодом, сеть не нужна
    shutil.copy(BUNDLED_ARCHIVE, dataset._filepath)
    extract_archive(dataset._filepath)
    return dataset


def test_download(dataset):
    if dataset.filepath:
        pytest.skip(f"Не нужно загружать набор данных при каждом запуске теста {dataset.filepath}")
    dataset.download()
    assert Path(dataset._filepath).is_file()
    assert Path(dataset.data_dir).is_dir()


def test_oserror():
    dataset = TextsByGrade(data_dir="/tmp")
    with pytest.raises(OSError):
        _ = list(dataset.get_texts())


def test_info(dataset):
    assert dataset.info["Наименование"] == "texts_by_grade"
    assert dataset.info["license"] == "CC0 1.0"
    assert dataset.labels == tuple(f"grade_{grade}" for grade in GRADES)


def test_records_count(dataset):
    records = list(dataset)
    assert len(records) == 68
    assert sorted({record["grade"] for record in records}) == list(GRADES)


def test_get_texts(dataset):
    for text in dataset.get_texts(limit=2):
        assert isinstance(text, str)
        assert "\n\n" not in text


@pytest.mark.parametrize("limit", [1, 5, 10])
def test_get_texts_limit(dataset, limit):
    assert sum(1 for _ in dataset.get_texts(limit=limit)) == limit


@pytest.mark.parametrize("min_len", [1000, 3000, 5000])
def test_get_texts_min_len(dataset, min_len):
    assert all(len(text) >= min_len for text in dataset.get_texts(min_len=min_len, limit=5))


@pytest.mark.parametrize("max_len", [2000, 3000, 5000])
def test_get_texts_max_len(dataset, max_len):
    assert all(len(text) <= max_len for text in dataset.get_texts(max_len=max_len, limit=5))


def test_get_records(dataset):
    fields = ["grade", "subject", "source", "text", "file"]
    for record in dataset.get_records(limit=2):
        assert isinstance(record, dict)
        assert all(field in record for field in fields)


@pytest.mark.parametrize(("grade", "expected"), [(1, 11), (11, 15), (17, 15), (5, 1)])
def test_get_records_grade(dataset, grade, expected):
    records = list(dataset.get_records(grade=grade))
    assert len(records) == expected
    assert all(record["grade"] == grade for record in records)


def test_get_records_subject(dataset):
    records = list(dataset.get_records(subject="ряба"))
    assert len(records) == 1
    assert records[0]["subject"] == "Курочка Ряба"
    assert records[0]["source"] == "http://skazki.org.ru/tales/yaichko/"
    assert records[0]["text"].startswith("Жил себе дед да баба")


def test_get_records_no_source(dataset):
    records = list(dataset.get_records(subject="Буратино"))
    assert len(records) == 1
    assert records[0]["source"] == ""
    assert sum(1 for record in dataset if not record["source"]) == 2


def test_get_records_commented_source(dataset):
    records = list(dataset.get_records(subject="Котлован"))
    assert len(records) == 1
    assert records[0]["source"] == "http://ilibrary.ru/text/1010/p.1/index.html"


def test_iter_ignores_foreign_files(dataset):
    stray = dataset._dirpath / "grade_1" / ".DS_Store"
    stray.write_bytes(b"")
    try:
        assert sum(1 for _ in dataset) == 68
    finally:
        stray.unlink()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"grade": 0},
        {"grade": 2},
        {"grade": 18},
        {"min_len": 0},
        {"min_len": -1},
        {"max_len": -1},
        {"min_len": 10, "max_len": 5},
        {"limit": -1},
    ],
)
def test_get_filters_errors(dataset, kwargs):
    with pytest.raises(ParameterError):
        list(dataset.get_texts(**kwargs))


def test_download_extracts_existing_archive(tmp_path):
    dataset = TextsByGrade(data_dir=tmp_path)
    shutil.copy(BUNDLED_ARCHIVE, dataset._filepath)
    dataset.download()
    assert dataset.check_data()


def test_download_replaces_broken_archive(tmp_path, monkeypatch):
    dataset = TextsByGrade(data_dir=tmp_path)
    dataset._filepath.write_bytes(b"\x00" * 40)
    calls = []

    def fake_download(url, dirpath, filename, force=False, user_agent=None):
        calls.append(force)
        if not force and (Path(dirpath) / filename).is_file():
            return ""
        shutil.copy(BUNDLED_ARCHIVE, Path(dirpath) / filename)
        return str(Path(dirpath) / filename)

    monkeypatch.setattr(dataset_module, "download_file", fake_download)
    dataset.download()
    assert calls == [False, True]
    assert dataset.check_data()
    other = TextsByGrade(data_dir=tmp_path / "other")
    other._filepath.parent.mkdir()
    other._filepath.write_bytes(b"\x00" * 40)

    def broken_download(url, dirpath, filename, force=False, user_agent=None):
        path = Path(dirpath) / filename
        if not force and path.is_file():
            return ""
        path.write_bytes(b"\x00" * 40)
        return str(path)

    monkeypatch.setattr(dataset_module, "download_file", broken_download)
    with pytest.raises(DownloadError):
        other.download()


@pytest.mark.parametrize("subject, expected", [(".", 46), ("(", 0)])
def test_subject_escaped(dataset, subject, expected):
    assert len(list(dataset.get_records(subject=subject))) == expected


@pytest.fixture(scope="module")
def readability(dataset):
    labels = []
    stats = {stat: [] for stat in READABILITY_GRADE_STATS}
    stats.update(
        {
            "consensus_grade": [],
            "flesch_reading_easy": [],
            "lix": [],
            "rix": [],
            "matskovsky_index": [],
            "tuldava": [],
        }
    )
    for record in dataset:
        rs = ReadabilityStats(record["text"])
        labels.append(record["grade"])
        for stat in stats:
            stats[stat].append(getattr(rs, stat))
    return np.array(labels), {stat: np.array(values) for stat, values in stats.items()}


def test_readability_formulas_correlate_with_grades(readability):
    labels, stats = readability
    for stat, values in stats.items():
        rho, _ = spearmanr(labels, values)
        if stat == "flesch_reading_easy":
            assert rho < -0.7, stat
        else:
            assert rho > 0.7, stat


def test_consensus_grade_matches_labels(readability):
    labels, stats = readability
    consensus = stats["consensus_grade"]
    assert spearmanr(labels, consensus)[0] > 0.8
    assert np.mean(np.abs(consensus - labels)) < 4
    groups = [(1, 1), (3, 4), (5, 9), (10, 11), (12, 17)]
    means = [consensus[(labels >= low) & (labels <= high)].mean() for low, high in groups]
    assert means == sorted(means)
    for page in ("textsbygrade.md", "textsbygrade.en.md"):
        text = (DOCS / "datasets" / page).read_text(encoding="utf-8")
        assert re.findall(r"(\d+\.\d) (?:для|for) ", text) == [f"{mean:.1f}" for mean in means]


def test_readability_table_follows_docs(readability):
    """Таблица формул на странице набора совпадает с вычисленной"""
    labels, stats = readability
    names = {READABILITY_STATS_DESC[stat]: stat for stat in stats}
    page = (DOCS / "datasets" / "textsbygrade.md").read_text(encoding="utf-8")
    rows = {row["label"]: (row["rho"], row["mae"]) for row in FORMULA_ROW.finditer(page)}
    assert set(rows) == set(names)
    for label, (rho, mae) in rows.items():
        values = stats[names[label]]
        assert rho == f"{spearmanr(labels, values)[0]:.2f}".replace("-", "−"), label
        has_grade = names[label] in (*READABILITY_GRADE_STATS, "consensus_grade")
        assert mae == (f"{np.mean(np.abs(values - labels)):.1f}" if has_grade else "-"), label
    english = (DOCS / "datasets" / "textsbygrade.en.md").read_text(encoding="utf-8")
    english_rows = [(row["rho"], row["mae"]) for row in FORMULA_ROW.finditer(english)]
    assert english_rows == list(rows.values())


@pytest.fixture(scope="module")
def first_grade_reader(tmp_path_factory):
    reader = SovChLit(data_dir=tmp_path_factory.mktemp("ruts_data_scl"))
    archive = BUNDLED_ARCHIVE.with_name(sov_chrest_lit_module.ARCHIVE)
    shutil.copy(archive, reader._filepath)
    reader.download()
    return reader


@pytest.fixture(scope="module")
def presets(dataset, first_grade_reader):
    """Метки и объекты ReadabilityStats каждого пресета для TextsByGrade и SovChLit"""
    records = [(record["grade"], BasicStats(record["text"])) for record in dataset]
    reader = [(1, BasicStats(text)) for text in first_grade_reader.get_texts()]
    return {
        name: [
            (
                grade,
                {preset: ReadabilityStats(bs, preset=preset) for preset in READABILITY_PRESETS},
            )
            for grade, bs in texts
        ]
        for name, texts in (("TextsByGrade", records), ("SovChLit", reader))
    }


@pytest.mark.parametrize("page", ["readability_stats.md", "readability_stats.en.md"])
def test_presets_table_follows_docs(presets, page):
    """Медианы теста Флеша-Кинкайда по пресетам и числа оговорки в документации - вычисленные"""
    groups = {"1": (1, 1), "3-4": (3, 4), "5-9": (5, 9), "10-11": (10, 11), "12-17": (12, 17)}
    texts = presets["TextsByGrade"]
    samples = [
        [rs for grade, rs in texts if low <= grade <= high] for low, high in groups.values()
    ]
    samples.append([rs for _, rs in presets["SovChLit"]])
    text = (DOCS / "stats" / page).read_text(encoding="utf-8")
    rows = list(PRESET_ROW.finditer(text))
    for row, label, sample in zip(rows, [*groups, "1"], samples, strict=True):
        assert row["group"].split()[0] == label
        assert int(row["n"]) == len(sample), label
        for preset in READABILITY_PRESETS:
            grades = [rs[preset].flesch_kincaid_grade for rs in sample]
            assert row[preset] == f"{median(grades):.1f}", (label, preset)
    school = [(grade, rs) for grade, rs in texts if grade <= 11]
    for preset in READABILITY_PRESETS:
        fk = [rs[preset].flesch_kincaid_grade for _, rs in texts]
        assert f" {spearmanr([grade for grade, _ in texts], fk)[0]:.2f}," in text, preset
        bias = median(rs[preset].flesch_kincaid_grade - grade for grade, rs in school)
        assert f"{bias:+.1f}".replace("-", "−") in text, preset
    for preset in ("plainrussian", "fiction"):
        consensus = median(rs[preset].consensus_grade for _, rs in texts)
        assert f"{consensus:.2f}" in text, preset


def test_level_norms_follow_datasets(dataset, first_grade_reader):
    """LEVEL_NORMS - квартили признаков текстов от 100 слов с меткой школьной ступени"""
    digits = {"words_per_sent": 1, "letters_per_word": 2, "p_smog_complex_words": 3, "mtld": 0}
    texts = [*dataset, *first_grade_reader]
    stages: dict[int, list[dict[str, float]]] = {}
    for record in texts:
        if BasicStats(record["text"]).n_words < 100:
            continue
        for low, high, _, _ in GRADE_AGE_LEVELS:
            if low <= record["grade"] <= high <= 11:
                stages.setdefault(low, []).append(level_features(record["text"]))
    computed = {
        low: {
            stat: tuple(
                round(float(value), places)
                for value in np.percentile([f[stat] for f in rows], [25, 75])
            )
            for stat, places in digits.items()
        }
        for low, rows in stages.items()
        if len(rows) >= 10
    }
    assert computed == LEVEL_NORMS
    for page in ("readability_stats.md", "readability_stats.en.md"):
        text = (DOCS / "stats" / page).read_text(encoding="utf-8")
        rows = [row.strip("| ").split(" | ")[1:] for row in NORM_ROW.findall(text)]
        assert rows == [
            [str(len(stages[low])), *(f"{low_}-{high}" for low_, high in norms.values())]
            for low, norms in LEVEL_NORMS.items()
        ], page
