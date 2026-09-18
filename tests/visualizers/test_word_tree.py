import pytest
from graphviz import Digraph

from ruts.exceptions import ParameterError, SourceError, SourceTypeError
from ruts.visualizers import wordtree


@pytest.fixture(scope="module")
def texts():
    return [["говорит", "рабочий", "класс"], ["8-часовой", "рабочий", "день"]]


def test_wordtree_type_error():
    with pytest.raises(TypeError):
        wordtree(1, "тест")
    with pytest.raises(SourceTypeError):
        wordtree("рабочий класс", "рабочий")
    with pytest.raises(SourceTypeError):
        wordtree([["рабочий", "класс"], "рабочий день"], "рабочий")


def test_wordtree_value_error(texts):
    with pytest.raises(ValueError):
        wordtree(texts, "тест")
    with pytest.raises(SourceError):
        wordtree([], "тест")
    with pytest.raises(ParameterError):
        wordtree(texts, "рабочий", max_n=1)
    with pytest.raises(ParameterError):
        wordtree(texts, "рабочий", max_per_n=0)


def test_wordtree_html_like_words():
    g = wordtree([["<script>", "кот", "спал"], ["злой", "<script>", "ел"]], "<script>")
    assert g.source.splitlines()[0] == 'digraph "<script>" {'
    assert '"<script>" [label="<script>"' in g.source
    assert "\t<script>" not in g.source


def test_wordtree(texts):
    g = wordtree(texts, "рабочий", max_n=2)
    assert isinstance(g, Digraph)
    assert len(g.body) == 11
    assert g.name == "рабочий"
