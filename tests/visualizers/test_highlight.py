import pytest
import spacy
from spacy.tokens import Doc

from ruts.constants import HIGHLIGHT_LAYERS_DESC
from ruts.visualizers import Highlight, HighlightedText, highlight
from ruts.visualizers.highlight import (
    calc_alliteration_runs,
    find_alliteration,
    find_complex_words,
    find_long_sents,
    find_stopwords,
    get_text_sents,
    get_text_words,
    plural,
    split_segments,
)

text = "Чуть слышно, бесшумно шуршат камыши. Повышение эффективности использования ресурсов обсуждалось."
long_text = (
    "Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие черты: "
    "полнота значений словарного состава языка или какого-либо его сегмента; "
    "тематический способ упорядочения значений слов. Ночь."
)

TOKENS = [
    ("Дом", False, 9, "nsubj:pass", "NOUN", "Case=Nom"),
    (",", True, 2, "punct", "PUNCT", ""),
    ("построенный", True, 0, "acl", "VERB", "VerbForm=Part|Voice=Pass"),
    ("рабочими", True, 2, "obl:agent", "NOUN", "Case=Ins"),
    ("в", True, 6, "case", "ADP", ""),
    ("прошлом", True, 6, "amod", "ADJ", "Case=Loc"),
    ("году", False, 2, "obl", "NOUN", "Case=Loc"),
    (",", True, 2, "punct", "PUNCT", ""),
    ("был", True, 9, "aux:pass", "AUX", "VerbForm=Fin"),
    ("продан", False, 9, "ROOT", "VERB", "Variant=Short|VerbForm=Part|Voice=Pass"),
    (".", True, 9, "punct", "PUNCT", ""),
    ("Повышение", True, 15, "nsubj:pass", "NOUN", "Case=Nom"),
    ("эффективности", True, 11, "nmod", "NOUN", "Case=Gen"),
    ("использования", True, 12, "nmod", "NOUN", "Case=Gen"),
    ("ресурсов", True, 13, "nmod", "NOUN", "Case=Gen"),
    ("обсуждалось", False, 15, "ROOT", "VERB", "VerbForm=Fin|Voice=Pass"),
    (",", True, 18, "punct", "PUNCT", ""),
    ("не", True, 18, "advmod", "PART", "Polarity=Neg"),
    ("выходя", True, 15, "advcl", "VERB", "VerbForm=Conv"),
    ("за", True, 20, "case", "ADP", ""),
    ("рамки", False, 18, "obl", "NOUN", "Case=Acc"),
    (".", False, 15, "punct", "PUNCT", ""),
]


def build_doc(tokens):
    words, spaces, heads, deps, pos, morphs = map(list, zip(*tokens, strict=True))
    return Doc(
        spacy.blank("ru").vocab,
        words=words,
        spaces=spaces,
        heads=heads,
        deps=deps,
        pos=pos,
        morphs=morphs,
    )


@pytest.fixture(scope="module")
def doc():
    return build_doc(TOKENS)


@pytest.fixture(scope="module")
def nlp():
    pytest.importorskip("ru_core_news_sm")
    return spacy.load("ru_core_news_sm")


@pytest.fixture(scope="module")
def ht():
    return highlight(text)


def test_init_value_error():
    with pytest.raises(ValueError):
        highlight("+ _")
    with pytest.raises(ValueError):
        highlight(text, long_sent_word_factor=0)
    with pytest.raises(ValueError):
        highlight(text, complex_syl_factor=0)
    with pytest.raises(ValueError):
        highlight(text, alliteration_threshold=0)
    with pytest.raises(ValueError):
        highlight(text, alliteration_threshold=1.5)


@pytest.mark.parametrize("source", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(source):
    with pytest.raises(TypeError):
        highlight(source)


def test_highlight_returns_highlighted_text(ht):
    assert isinstance(ht, HighlightedText)
    assert ht.text == text
    assert all(isinstance(h, Highlight) for h in ht.highlights)


def test_layers_default_str(ht):
    assert ht.layers == ("long_sents", "complex_words", "stopwords", "alliteration")


def test_layers_default_doc(doc):
    assert highlight(doc).layers == tuple(HIGHLIGHT_LAYERS_DESC)


def test_layers_default_blank_doc():
    blank = spacy.blank("ru")(text)
    assert highlight(blank).layers == ("complex_words", "stopwords", "alliteration")


def test_layers_selection(doc):
    assert highlight(text, layers=["alliteration", "complex_words"]).layers == (
        "complex_words",
        "alliteration",
    )
    assert highlight(text, layers="stopwords").layers == ("stopwords",)
    assert highlight(doc, layers=["passive"]).layers == ("passive",)


def test_layers_unknown():
    with pytest.raises(ValueError, match="Неизвестный слой"):
        highlight(text, layers=["typos"])


def test_layers_unavailable():
    with pytest.raises(ValueError, match="passive"):
        highlight(text, layers=["passive"])
    with pytest.raises(ValueError, match="long_sents"):
        highlight(spacy.blank("ru")(text), layers=["long_sents"])


def test_counts(ht):
    assert ht.counts == {
        "long_sents": 0,
        "complex_words": 4,
        "stopwords": 0,
        "alliteration": 1,
    }
    assert list(ht.counts) == list(ht.layers)


def test_highlights_sorted(ht):
    positions = [(h.start, -h.end) for h in ht.highlights]
    assert positions == sorted(positions)


def test_get_text_words():
    words = get_text_words("Жили-были старик, со старухой.")
    assert [word.text for word in words] == ["Жили-были", "старик", "со", "старухой"]
    assert words[0].start == 0
    assert words[0].end == 9
    assert words[-1].end == 29


def test_get_text_sents():
    source = "Первое предложение.  Второе\nпредложение!\n\nТретье."
    words = get_text_words(source)
    sents = get_text_sents(source, words)
    assert [(s.start, s.end, s.n_words) for s in sents] == [(0, 19, 2), (21, 40, 2), (42, 49, 1)]


def test_get_text_sents_no_words():
    assert get_text_sents("...", []) == [(0, 3, 0)]


def test_plural():
    assert plural(1, "слово", "слова", "слов") == "1 слово"
    assert plural(3, "слово", "слова", "слов") == "3 слова"
    assert plural(5, "слово", "слова", "слов") == "5 слов"
    assert plural(11, "слово", "слова", "слов") == "11 слов"
    assert plural(21, "слово", "слова", "слов") == "21 слово"
    assert plural(112, "слово", "слова", "слов") == "112 слов"


def test_long_sents():
    ht = highlight(long_text, layers=["long_sents"])
    assert ht.counts == {"long_sents": 1}
    (h,) = ht.highlights
    assert (h.start, h.end) == (0, len(long_text) - len(" Ночь."))
    assert h.note == "длинное предложение, 24 слова"
    assert highlight(long_text, layers=["long_sents"], long_sent_word_factor=25).highlights == ()
    assert highlight(long_text, layers=["long_sents"], long_sent_word_factor=1).counts == {
        "long_sents": 2
    }


def test_find_long_sents():
    sents = get_text_sents(text, get_text_words(text))
    assert find_long_sents(sents, 5) == [
        Highlight(0, 36, "long_sents", "длинное предложение, 5 слов"),
        Highlight(37, 96, "long_sents", "длинное предложение, 5 слов"),
    ]
    assert find_long_sents(sents, 6) == []


def test_complex_words(ht):
    complex_words = [h for h in ht.highlights if h.layer == "complex_words"]
    assert [text[h.start : h.end] for h in complex_words] == [
        "Повышение",
        "эффективности",
        "использования",
        "обсуждалось",
    ]
    assert complex_words[0].note == "сложное слово, 5 слогов"
    assert complex_words[2].note == "сложное слово, 6 слогов"
    assert highlight(text, layers=["complex_words"], complex_syl_factor=6).counts == {
        "complex_words": 1
    }


def test_find_complex_words():
    words = get_text_words("Ночь и электрификация")
    assert find_complex_words(words, 4) == [
        Highlight(7, 21, "complex_words", "сложное слово, 7 слогов")
    ]
    assert find_complex_words(words, 1) == [
        Highlight(0, 4, "complex_words", "сложное слово, 1 слог"),
        Highlight(5, 6, "complex_words", "сложное слово, 1 слог"),
        Highlight(7, 21, "complex_words", "сложное слово, 7 слогов"),
    ]


def test_stopwords():
    source = "Он сказал, что не придёт, и ушёл."
    ht = highlight(source, layers=["stopwords"])
    assert [source[h.start : h.end] for h in ht.highlights] == ["Он", "что", "не", "и"]
    assert ht.highlights[0].note == "стоп-слово"


def test_stopwords_list():
    source = "Он сказал, что не придёт, и ушёл."
    words = get_text_words(source)
    assert [source[h.start : h.end] for h in find_stopwords(words, ["ОН", "ушёл"])] == [
        "Он",
        "ушёл",
    ]
    assert find_stopwords(words, []) == []


def test_alliteration(ht):
    (h,) = [h for h in ht.highlights if h.layer == "alliteration"]
    assert text[h.start : h.end] == "слышно, бесшумно шуршат камыши"
    assert h.note == "аллитерация на «ш»"


def test_alliteration_within_sentence():
    source = "Шуршат камыши. Шепчут они."
    assert [h.start for h in highlight(source, layers=["alliteration"]).highlights] == [0]
    words = get_text_words(source)
    assert [source[h.start : h.end] for h in find_alliteration(words, sents=None)] == [
        "Шуршат камыши. Шепчут"
    ]


def test_alliteration_threshold():
    source = "Полночной порою в болотной глуши"
    assert highlight(source, layers=["alliteration"]).highlights == ()
    ht = highlight(source, layers=["alliteration"], alliteration_threshold=0.05)
    assert [(source[h.start : h.end], h.note) for h in ht.highlights] == [
        ("Полночной порою", "аллитерация на «п»")
    ]


def test_calc_alliteration_runs():
    assert calc_alliteration_runs(["Чуть", "слышно", "бесшумно", "шуршат", "камыши"]) == [
        (1, 5, "ш")
    ]
    assert calc_alliteration_runs(["Клары", "украл", "кораллы"]) == [(0, 3, "к")]
    assert calc_alliteration_runs(["баба", "и", "била"]) == [(0, 3, "б")]
    assert calc_alliteration_runs(["в", "двенадцать", "миллиардов", "рублей", "в", "год"]) == []
    assert calc_alliteration_runs(["полнота", "значений", "словарного", "состава", "языка"]) == []
    assert calc_alliteration_runs(["Шла", "Саша", "по", "шоссе"]) == [(0, 4, "ш")]
    assert calc_alliteration_runs(["подготовленный", "рабочей", "группой"]) == []
    assert calc_alliteration_runs(["шуршат"]) == []
    assert calc_alliteration_runs([]) == []


def test_calc_alliteration_runs_several_consonants():
    runs = calc_alliteration_runs(["Карл", "у", "Клары", "украл", "кораллы"])
    assert runs == [(0, 5, "к"), (0, 5, "л"), (0, 5, "р")]


def test_passive(doc):
    ht = highlight(doc, layers=["passive"])
    assert [(doc.text[h.start : h.end], h.note) for h in ht.highlights] == [
        ("построенный", "пассив"),
        ("был продан", "пассив без агенса"),
        ("обсуждалось", "пассив без агенса"),
    ]


def test_participle_clauses(doc):
    ht = highlight(doc, layers=["participle_clauses"])
    assert [(doc.text[h.start : h.end], h.note) for h in ht.highlights] == [
        ("построенный рабочими в прошлом году", "причастный оборот, 5 слов")
    ]


def test_converb_clauses(doc):
    ht = highlight(doc, layers=["converb_clauses"])
    assert [(doc.text[h.start : h.end], h.note) for h in ht.highlights] == [
        ("не выходя за рамки", "деепричастный оборот, 4 слова")
    ]


def test_genitive_chains(doc):
    ht = highlight(doc, layers=["genitive_chains"])
    assert [(doc.text[h.start : h.end], h.note) for h in ht.highlights] == [
        ("Повышение эффективности использования ресурсов", "цепочка из 3 родительных")
    ]


def test_genitive_chains_single_modifier():
    doc = build_doc(
        [
            ("дом", True, 0, "ROOT", "NOUN", "Case=Nom"),
            ("отца", False, 0, "nmod", "NOUN", "Case=Gen"),
        ]
    )
    assert highlight(doc, layers=["genitive_chains"]).highlights == ()


def test_doc_long_sents(doc):
    ht = highlight(doc, layers=["long_sents"], long_sent_word_factor=8)
    assert [doc.text[h.start : h.end] for h in ht.highlights] == [
        "Дом, построенный рабочими в прошлом году, был продан.",
        "Повышение эффективности использования ресурсов обсуждалось, не выходя за рамки.",
    ]
    assert ht.highlights[0].note == "длинное предложение, 8 слов"


def test_doc_text_layers(doc):
    ht = highlight(doc, layers=["complex_words", "stopwords", "alliteration"])
    assert ht.counts == {"complex_words": 6, "stopwords": 3, "alliteration": 0}
    assert [doc.text[h.start : h.end] for h in ht.highlights if h.layer == "stopwords"] == [
        "в",
        "не",
        "за",
    ]


def test_split_segments():
    highlights = [
        Highlight(0, 10, "long_sents", "a"),
        Highlight(2, 5, "complex_words", "b"),
        Highlight(4, 8, "alliteration", "c"),
    ]
    segments = [
        (start, end, [h.layer for h in active])
        for start, end, active in split_segments(12, highlights)
    ]
    assert segments == [
        (0, 2, ["long_sents"]),
        (2, 4, ["long_sents", "complex_words"]),
        (4, 5, ["long_sents", "complex_words", "alliteration"]),
        (5, 8, ["long_sents", "alliteration"]),
        (8, 10, ["long_sents"]),
        (10, 12, []),
    ]


def test_split_segments_empty():
    assert list(split_segments(3, [])) == [(0, 3, [])]


def test_to_html(ht):
    html = ht.to_html()
    assert html.startswith('<div class="ruts-highlight"><style>')
    assert html.endswith("</div></div>")
    assert '<div class="ruts-highlight-legend">' in html
    assert '<span class="ruts-hl ruts-hl-complex_words">Сложные слова</span>' in html
    assert '<span class="ruts-highlight-count">4</span>' in html
    assert (
        '<span class="ruts-hl ruts-hl-alliteration" title="аллитерация на «ш»">'
        "слышно, бесшумно шуршат камыши</span>. "
        '<span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 5 слогов">'
        "Повышение</span>"
    ) in html
    assert ht._repr_html_() == html


def test_to_html_without_legend_and_css(ht):
    html = ht.to_html(legend=False, css=False)
    assert "<style>" not in html
    assert "ruts-highlight-legend" not in html
    assert html.startswith('<div class="ruts-highlight"><div class="ruts-highlight-text">Чуть ')


def test_to_html_escaping():
    source = "Дом <b>продан</b> & куплен.\nНочь."
    html = highlight(source, layers=["stopwords"]).to_html(legend=False, css=False)
    assert "<b>" not in html
    assert "&lt;b&gt;продан&lt;/b&gt; &amp; куплен.&#10;Ночь." in html
    assert "\n" not in html


def test_to_html_title_escaping():
    source = 'Он сказал "да".'
    html = highlight(source, layers=["stopwords"]).to_html(legend=False, css=False)
    assert 'title="стоп-слово">Он</span>' in html
    assert (
        'сказал &quot;<span class="ruts-hl ruts-hl-stopwords" title="стоп-слово">да</span>&quot;.'
        in html
    )


def test_to_html_nested_classes(doc):
    html = highlight(doc).to_html(legend=False, css=False)
    assert (
        '<span class="ruts-hl ruts-hl-complex_words ruts-hl-passive ruts-hl-participle_clauses" '
        'title="сложное слово, 4 слога; пассив; причастный оборот, 5 слов">построенный</span>'
    ) in html
    assert (
        '<span class="ruts-hl ruts-hl-participle_clauses" title="причастный оборот, 5 слов"> '
        "</span>"
    ) in html


def test_parsed_doc(nlp):
    doc = nlp("Дом, построенный рабочими, был продан.\n\nЧуть слышно, бесшумно шуршат камыши.")
    ht = highlight(doc, long_sent_word_factor=5)
    assert ht.layers == tuple(HIGHLIGHT_LAYERS_DESC)
    assert [doc.text[h.start : h.end] for h in ht.highlights if h.layer == "long_sents"] == [
        "Дом, построенный рабочими, был продан.",
        "Чуть слышно, бесшумно шуршат камыши.",
    ]
    assert ht.counts["passive"] == 2
    assert ht.counts["participle_clauses"] == 1
    assert "слышно, бесшумно шуршат камыши" in [
        doc.text[h.start : h.end] for h in ht.highlights if h.layer == "alliteration"
    ]
    assert "&#10;&#10;" in ht.to_html()
