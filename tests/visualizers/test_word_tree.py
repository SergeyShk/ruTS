import pytest
from graphviz import Digraph

from ruts.visualizers import wordtree


@pytest.fixture(scope="module")
def texts():
    return [["говорит", "рабочий", "класс"], ["8-часовой", "рабочий", "день"]]


def test_wordtree_type_error():
    with pytest.raises(TypeError):
        wordtree(1, "тест")


def test_wordtree_value_error(texts):
    with pytest.raises(ValueError):
        wordtree(texts, "тест")


def test_wordtree(texts):
    g = wordtree(texts, "рабочий", max_n=2)
    assert isinstance(g, Digraph)
    assert len(g.body) == 11
    assert g.name == "рабочий"
