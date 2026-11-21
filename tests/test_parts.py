"""Статистики по частям документа (by_parts ядра)"""

import pytest
from anyts.document import document_part

import ruts
from ruts.datasets import FreqDict, StressDict
from ruts.datasets.stress_dict import FILENAME
from ruts.utils import _document_analyses, get_document
from tests.datasets.test_freq2011 import write_dict
from tests.test_verse_stats import ROWS

# Предложение стиха через строки: отдельно от текста anySeg делит его по строкам
VERSE = "Инда жалко подчас... да куды! —\nНе утешишь ее и обновкой:\nТо натерли ей ногу коты,"
PROSE = (
    "Мост сделан из стали. Мы стали друзьями, и, конечно, нет ничего лучше.\nПтица поёт в саду."
)
TEXT = VERSE + "\n\n" + PROSE
# Счетчики, которые части делят без остатка: уникальные слова и пробелы между частями - нет
ADDITIVE = {
    ruts.BasicStats: lambda stats: [
        key
        for key in stats.get_stats(flat=True)
        if key not in {"n_chars", "n_spaces", "n_unique_words"} and (key.startswith(("n_", "c_")))
    ],
    ruts.MorphStats: lambda stats: [
        key
        for stat, value in stats.get_stats().items()
        if isinstance(value, dict)
        for key in stats.get_stats(flat=True)
        if key.startswith(f"{stat}_")
    ],
    ruts.VerseStats: lambda stats: ["n_lines", "n_stanzas"],
}
CLASSES = [
    ruts.BasicStats,
    ruts.ReadabilityStats,
    ruts.UnadaptedReadabilityStats,
    ruts.MorphStats,
    ruts.LexicalStats,
    ruts.StyleStats,
    ruts.PhonStats,
    ruts.CohesionStats,
    ruts.VerseStats,
]


@pytest.fixture(scope="module")
def doc(nlp):
    return nlp(TEXT)


@pytest.fixture(scope="module")
def params(tmp_path_factory):
    """Словари классов, которым они нужны"""
    path = tmp_path_factory.mktemp("dicts")
    write_dict(path)
    path.joinpath(FILENAME).write_text(
        "\n".join("\t".join(row) for row in sorted(ROWS)) + "\n", encoding="utf-8"
    )
    return {
        ruts.LexicalStats: {"freq_dict": FreqDict(data_dir=path)},
        ruts.VerseStats: {"stress_dict": StressDict(data_dir=path)},
    }


def sources(doc):
    return {"str": TEXT, "Document": get_document(TEXT), "Doc": doc}


@pytest.mark.parametrize("cls", list(ADDITIVE), ids=lambda cls: cls.__name__)
@pytest.mark.parametrize("kind", ["str", "Document", "Doc"])
def test_parts_add_up(cls, kind, doc, params):
    """Счетчики частей в сумме дают счетчики целого текста"""
    source = sources(doc)[kind]
    whole = cls(source, **params.get(cls, {}))
    flat = whole.get_stats(flat=True)
    for parts in cls.part_kinds:
        table = cls.by_parts(source, parts, **params.get(cls, {}))
        for key in ADDITIVE[cls](whole):
            total = int(table[key].fillna(0).sum()) if key in table else 0
            assert total == flat[key], (parts, key)


def test_parts_analyzed_as_whole():
    """Часть разбирается в контексте своих предложений документа, как в целом тексте"""
    document = get_document(TEXT)
    whole = [(analysis.lemma, analysis.pos) for analysis in _document_analyses(document)]
    found = []
    for sentence in document.sentences:
        part = document_part(document, sentence.start, sentence.end)
        found += [(analysis.lemma, analysis.pos) for analysis in _document_analyses(part)]
    assert found == whole


@pytest.mark.parametrize("cls", CLASSES, ids=lambda cls: cls.__name__)
def test_by_parts(cls, doc, params):
    """Строка таблицы на каждую часть каждого вида у строки, Document и Doc"""
    document = get_document(TEXT)
    sizes = {"sentences": 5, "lines": 3, "paragraphs": 2}
    for source in sources(doc).values():
        for parts in cls.part_kinds:
            table = cls.by_parts(source, parts, **params.get(cls, {}))
            assert len(table) == sizes[parts]
            assert table.index.name == parts[:-1]
    paragraphs = cls.by_parts(document, "paragraphs", **params.get(cls, {}))
    assert list(paragraphs["start"]) == [0, len(VERSE) + 2]


def test_by_parts_syntax(doc):
    """SyntaxStats считает части Doc с разбором зависимостей"""
    table = ruts.SyntaxStats.by_parts(doc)
    assert len(table) == 5
    assert table["tree_depth"].notna().all()


def test_by_parts_kinds():
    """VerseStats считает только строфы, DiversityStats - не считает частей; ошибки - русские"""
    with pytest.raises(ruts.ParameterError, match="Части должны быть одним из видов"):
        ruts.VerseStats.by_parts(TEXT, "sentences")
    with pytest.raises(ruts.ParameterError, match="считает текст целиком"):
        ruts.DiversityStats.by_parts(TEXT)
