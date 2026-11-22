from ruts.verse_stats import PATTERN_STRESSED
from ruts.visualizers import rhythm_plot


def test_rhythm_plot():
    """Ритм строк с русскими подписями по схемам VerseStats"""
    ax = rhythm_plot(["cCcCcCcC", "cCcCcccCc"], PATTERN_STRESSED)
    assert ax.get_title() == "Ритм строк"
    assert [label.get_text() for label in ax.get_legend().get_texts()] == [
        "Ударный слог",
        "Безударный слог",
    ]
    assert rhythm_plot(["cC"], "C", labels={"title": "Стих"}).get_title() == "Стих"
