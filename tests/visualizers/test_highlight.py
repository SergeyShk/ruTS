import pytest
import spacy
from spacy.tokens import Doc

from ruts.constants import (
    HIGHLIGHT_DEFAULT_LAYERS,
    HIGHLIGHT_LAYER_GROUPS,
    HIGHLIGHT_LAYERS_DESC,
    HIGHLIGHT_SYNTAX_LAYERS,
)
from ruts.visualizers import Highlight, HighlightedText, highlight
from ruts.visualizers.highlight import (
    Sent,
    Word,
    calc_alliteration_runs,
    find_alliteration,
    find_cliches,
    find_complex_words,
    find_compound_prepositions,
    find_connector_highlights,
    find_long_sents,
    find_parentheticals,
    find_rare_words,
    find_split_predicate_highlights,
    find_stopwords,
    find_verbal_nouns,
    get_doc_sents,
    get_doc_words,
    get_stem,
    get_text_sents,
    get_text_words,
    group_words_by_sents,
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
    return highlight(text, layers=["long_sents", "complex_words", "stopwords", "alliteration"])


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
    with pytest.raises(ValueError):
        highlight(text, alliteration_threshold="x")
    with pytest.raises(ValueError):
        highlight(text, layers=42)


@pytest.mark.parametrize("source", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(source):
    with pytest.raises(TypeError):
        highlight(source)


def test_init_string_lists():
    with pytest.raises(TypeError):
        highlight(text, stopwords="и на")
    with pytest.raises(TypeError):
        highlight(text, cliches="по вопросам")


def test_layers_generator():
    # генератор слоев не исчерпывается при проверке: слой остается включенным
    ht = highlight(text, layers=(layer for layer in ["complex_words"]))
    assert ht.layers == ("complex_words",)
    assert ht.counts["complex_words"] > 0


def test_highlight_returns_highlighted_text(ht):
    assert isinstance(ht, HighlightedText)
    assert ht.text == text
    assert all(isinstance(h, Highlight) for h in ht.highlights)


def test_layers_default_str():
    assert highlight(text).layers == ("long_sents", "complex_words", "cliches")
    assert highlight(text, layers="all").layers == tuple(
        layer for layer in HIGHLIGHT_LAYERS_DESC if layer not in HIGHLIGHT_SYNTAX_LAYERS
    )


def test_layers_default_doc(doc):
    assert highlight(doc).layers == HIGHLIGHT_DEFAULT_LAYERS
    assert highlight(doc, layers="all").layers == tuple(HIGHLIGHT_LAYERS_DESC)


def test_layers_default_blank_doc():
    blank = spacy.blank("ru")(text)
    assert highlight(blank).layers == ("complex_words", "cliches")
    assert "long_sents" not in highlight(blank, layers="all").layers


def test_layer_groups():
    grouped = [layer for group in HIGHLIGHT_LAYER_GROUPS.values() for layer in group]
    assert sorted(grouped) == sorted(HIGHLIGHT_LAYERS_DESC)
    assert len(grouped) == len(set(grouped)) == 15
    assert set(HIGHLIGHT_DEFAULT_LAYERS) < set(HIGHLIGHT_LAYERS_DESC)
    assert 5 <= len(HIGHLIGHT_DEFAULT_LAYERS) <= 6
    assert HIGHLIGHT_LAYER_GROUPS["Синтаксис"] == tuple(
        layer for layer in HIGHLIGHT_LAYERS_DESC if layer in HIGHLIGHT_SYNTAX_LAYERS
    )


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


def test_counts_all_layers():
    assert highlight(text, layers="all").counts == {
        "long_sents": 0,
        "complex_words": 4,
        "rare_words": 2,
        "verbal_nouns": 2,
        "compound_prepositions": 0,
        "cliches": 0,
        "stopwords": 0,
        "parentheticals": 0,
        "connectors": 0,
        "alliteration": 1,
    }


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


def test_group_words_by_sents():
    source = "Первое предложение.  Второе\nпредложение!\n\nТретье."
    words = get_text_words(source)
    groups = group_words_by_sents(words, get_text_sents(source, words))
    assert [[word.text for word in group] for group in groups] == [
        ["Первое", "предложение"],
        ["Второе", "предложение"],
        ["Третье"],
    ]
    assert group_words_by_sents(words, [Sent(21, 40, 2)]) == [words[2:4]]


def test_doc_sents_whitespace_start():
    nlp = spacy.blank("ru")
    nlp.add_pipe("sentencizer")
    doc = nlp("Дом продан.\n\nЧуть слышно шуршат камыши.")
    ht = highlight(doc, layers=["long_sents"], long_sent_word_factor=2)
    assert [doc.text[h.start : h.end] for h in ht.highlights] == [
        "Дом продан.",
        "Чуть слышно шуршат камыши.",
    ]


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
    source = "Чуть слышно, бесшумно шуршат камыши. Шепчут они."
    ht = highlight(source, layers=["alliteration"])
    assert [source[h.start : h.end] for h in ht.highlights] == ["слышно, бесшумно шуршат камыши"]
    words = get_text_words(source)
    assert [source[h.start : h.end] for h in find_alliteration(words, sents=None)] == [
        "слышно, бесшумно шуршат камыши. Шепчут"
    ]


def test_alliteration_threshold():
    source = "Полночной порою в болотной глуши"
    assert highlight(source, layers=["alliteration"]).highlights == ()
    ht = highlight(source, layers=["alliteration"], alliteration_threshold=0.05)
    assert [(source[h.start : h.end], h.note) for h in ht.highlights] == [
        ("Полночной порою", "аллитерация на «п»"),
        ("болотной глуши", "аллитерация на «л»"),
    ]


def test_calc_alliteration_runs():
    assert calc_alliteration_runs(["Чуть", "слышно", "бесшумно", "шуршат", "камыши"]) == [
        (1, 5, "ш")
    ]
    assert calc_alliteration_runs(["Карл", "у", "Клары", "украл", "кораллы"]) == [(0, 5, "к")]
    assert calc_alliteration_runs(["лицом", "к", "лицу"]) == [(0, 3, "ц")]
    assert calc_alliteration_runs(["баба", "и", "била"]) == []
    assert calc_alliteration_runs(["баба", "и", "била"], threshold=0.01) == [(0, 3, "б")]
    assert calc_alliteration_runs(["в", "двенадцать", "миллиардов", "рублей", "в", "год"]) == []
    assert calc_alliteration_runs(["полнота", "значений", "словарного", "состава", "языка"]) == []
    assert calc_alliteration_runs(["Шла", "Саша", "по", "шоссе"]) == [(0, 4, "ш")]
    assert calc_alliteration_runs(["подготовленный", "рабочей", "группой"]) == []
    assert calc_alliteration_runs(["этих", "крупных"], threshold=0.05) == []
    assert calc_alliteration_runs(["своим", "целям", "и", "нуждам"], threshold=0.05) == []
    assert calc_alliteration_runs(["шуршат"]) == []
    assert calc_alliteration_runs([]) == []


def test_calc_alliteration_runs_several_consonants():
    runs = calc_alliteration_runs(["Карл", "у", "Клары", "украл", "кораллы"], threshold=0.01)
    assert runs == [(0, 5, "к"), (0, 5, "р")]


def test_get_stem():
    assert get_stem("крупных") == "крупны"
    assert get_stem("руках") == "рука"
    assert get_stem("камыши") == "камыш"
    assert get_stem("подготовленный") == "подготов"
    assert get_stem("шла") == "шла"
    assert get_stem("люди") == "люди"


def test_passive(doc):
    ht = highlight(doc, layers=["passive"])
    assert [(doc.text[h.start : h.end], h.note) for h in ht.highlights] == [
        ("построенный", "пассив"),
        ("был продан", "пассив без агенса"),
        ("обсуждалось", "пассив без агенса"),
    ]


def test_passive_skips_punctuation():
    doc = build_doc(
        [
            ("Были", True, 2, "aux:pass", "AUX", "VerbForm=Fin"),
            ("-", True, 2, "punct", "VERB", "Voice=Pass"),
            (
                "отремонтированы",
                False,
                2,
                "ROOT",
                "VERB",
                "Variant=Short|VerbForm=Part|Voice=Pass",
            ),
            (".", False, 2, "punct", "PUNCT", ""),
        ]
    )
    assert doc[1].is_punct
    ht = highlight(doc, layers=["passive"])
    assert [doc.text[h.start : h.end] for h in ht.highlights] == ["Были - отремонтированы"]


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
    html = highlight(doc, layers="all").to_html(legend=False, css=False)
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
    ht = highlight(doc, layers="all", long_sent_word_factor=5)
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


officialese_text = (
    "Во-первых, в целях повышения качества комиссия осуществляет плановую проверку. "
    "Однако, как правило, на сегодняшний день фелинолог, т.е. специалист по кошкам, не привлекается."
)


def fragments(source, layer, **kwargs):
    ht = highlight(source, layers=[layer], **kwargs)
    text = ht.text
    return [(text[h.start : h.end], h.note) for h in ht.highlights]


def test_rare_words():
    assert fragments(officialese_text, "rare_words") == [
        ("фелинолог", "редкое слово: вне топ-10000"),
        ("привлекается", "редкое слово: вне топ-10000"),
    ]
    assert fragments("USA 2020 и т.е. кот", "rare_words") == []
    assert find_rare_words(get_text_words("Фелинолог")) == [
        Highlight(0, 9, "rare_words", "редкое слово: вне топ-10000")
    ]


def test_verbal_nouns():
    assert fragments(officialese_text, "verbal_nouns") == [
        ("повышения", "отглагольное существительное")
    ]
    assert find_verbal_nouns(get_text_words("здание")) == [
        Highlight(0, 6, "verbal_nouns", "отглагольное существительное")
    ]
    assert find_verbal_nouns(get_text_words("качество кот")) == []


def test_compound_prepositions():
    assert fragments(officialese_text, "compound_prepositions") == [
        ("в целях", "производный предлог: «в целях»")
    ]
    words = get_text_words("Путём проверки и за счёт этого")
    assert [h.start for h in find_compound_prepositions(words)] == [0, 17]
    assert [h.note for h in find_compound_prepositions(words)] == [
        "производный предлог: «путем»",
        "производный предлог: «за счет»",
    ]


def test_cliches():
    assert fragments(officialese_text, "cliches") == [
        ("на сегодняшний день", "штамп: «на сегодняшний день»")
    ]
    assert fragments(officialese_text, "cliches", cliches=["как правило"]) == [
        ("как правило", "штамп: «как правило»")
    ]
    assert fragments(officialese_text, "cliches", cliches=[]) == []
    assert find_cliches(get_text_words("имеет место быть"), None) == [
        Highlight(0, 16, "cliches", "штамп: «имеет место быть»")
    ]


def test_parentheticals():
    assert fragments(officialese_text, "parentheticals") == [
        ("Во-первых", "вводное слово"),
        ("Однако", "вводное слово"),
        ("как правило", "вводный оборот: «как правило»"),
    ]
    words = get_text_words("Конечно, таким образом, кот")
    assert [h.note for h in find_parentheticals(words)] == [
        "вводное слово",
        "вводный оборот: «таким образом»",
    ]


def test_connectors():
    assert fragments(officialese_text, "connectors") == [
        ("Во-первых", "коннектор «во-первых»: аддитивные, первичные"),
        ("в целях", "коннектор «в целях»: причинные, вторичные"),
        ("Однако", "коннектор «однако»: противительные, первичные"),
        ("т.е", "коннектор «т.е.»: переформулирующие, первичные"),
    ]
    source = "Он ушёл, потому. Что делать"
    words = get_text_words(source)
    sents = get_text_sents(source, words)
    assert find_connector_highlights(words, sents) == [
        Highlight(9, 15, "connectors", "коннектор «потому»: причинные, первичные")
    ]
    assert [h.note for h in find_connector_highlights(words, None)] == [
        "коннектор «потому что»: причинные, первичные"
    ]
    assert [h.note for h in find_connector_highlights(get_text_words("и всё же"), None)] == [
        "коннектор «и всё же»: уступительные, первичные"
    ]


def test_connectors_pos(nlp):
    source = "Раз он пришёл, значит, всё хорошо. В тот раз это значит много."
    assert [h.note for h in highlight(source, "connectors").highlights] == [
        "коннектор «раз»: условные, первичные",
        "коннектор «значит»: причинные, первичные",
        "коннектор «раз»: условные, первичные",
        "коннектор «значит»: причинные, первичные",
    ]
    doc = nlp(source)
    words = get_doc_words(doc)
    assert words[:2] == [Word(0, 3, "Раз", "SCONJ"), Word(4, 6, "он", "PRON")]
    assert [word.pos for word in get_doc_words(spacy.blank("ru")(source))] == [None] * 12
    assert [h.note for h in highlight(doc, "connectors").highlights] == [
        "коннектор «раз»: условные, первичные",
        "коннектор «значит»: причинные, первичные",
    ]
    words = [Word(0, 3, "Раз", "NOUN"), Word(4, 10, "значит", "VERB"), Word(11, 14, "кот")]
    assert find_connector_highlights(words, None) == []
    words = [Word(0, 3, "Раз", "SCONJ"), Word(4, 10, "значит"), Word(11, 14, "кот")]
    assert [h.note for h in find_connector_highlights(words, None)] == [
        "коннектор «раз»: условные, первичные",
        "коннектор «значит»: причинные, первичные",
    ]


def test_split_predicates(nlp):
    doc = nlp(officialese_text)
    assert fragments(doc, "split_predicates") == [
        ("осуществляет плановую проверку", "расщепленное сказуемое: осуществлять проверка")
    ]
    assert find_split_predicate_highlights(nlp("Кот спит.")) == []
    with pytest.raises(ValueError, match="split_predicates"):
        highlight(officialese_text, layers=["split_predicates"])


def test_new_layers_doc_matches_text(nlp):
    doc = nlp(officialese_text)
    for layer in (
        "rare_words",
        "verbal_nouns",
        "compound_prepositions",
        "cliches",
        "parentheticals",
        "connectors",
    ):
        assert [f.rstrip(".") for f, _ in fragments(doc, layer)] == [
            f.rstrip(".") for f, _ in fragments(officialese_text, layer)
        ]


def test_hyphenated_words_doc(nlp):
    source = "Во-первых, кот спит. По-видимому, он устал. Конечно, это так."
    doc = nlp(source)
    expected = ["Во-первых", "По-видимому", "Конечно"]
    assert [f for f, _ in fragments(doc, "parentheticals")] == expected
    assert [f for f, _ in fragments(source, "parentheticals")] == expected
    assert "Во" not in [f for f, _ in fragments(doc, "stopwords")]
    assert [sent.n_words for sent in get_doc_sents(doc)] == [3, 3, 3]
