from math import isnan
from statistics import pstdev

import pytest
import spacy
from spacy.tokens import Doc

from ruts import SyntaxStats
from ruts.constants import SYNTAX_STATS_DESC
from ruts.syntax_stats import (
    calc_coordination_chains,
    calc_dependency_distances,
    calc_genitive_chains,
    calc_tree_depth,
    calc_valency,
    count_noun_modifiers,
    find_split_predicates,
    get_lemma,
    is_agentless,
    is_clause_head,
    is_converb_clause,
    is_finite_verb,
    is_genitive_modifier,
    is_light_verb,
    is_negation,
    is_participle,
    is_participle_clause,
    is_passive,
    is_predicate,
    is_split_predicate_noun,
    is_subordinate_clause_head,
    subtree_len,
)

text = (
    "Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие черты: полнота значений\
    словарного состава языка или какого-либо его сегмента; тематический, или идеографический способ упорядочения\
    значений слов. Отличительной особенностью тезаурусов по сравнению с формальными онтологиями является выход в сферу\
    лексических значений, установление связей не только между значениями и выражающими их словами, а также между самими\
    значениями (регистрация различных семантических отношений внутри словаря)."
)

SENTENCES = [
    (
        "Дом , построенный рабочими , был продан .",
        [6, 2, 0, 2, 2, 6, 6, 6],
        ["nsubj:pass", "punct", "acl", "obl:agent", "punct", "aux:pass", "ROOT", "punct"],
        ["NOUN", "PUNCT", "VERB", "NOUN", "PUNCT", "AUX", "VERB", "PUNCT"],
        [
            "Case=Nom",
            "",
            "VerbForm=Part|Voice=Pass",
            "Case=Ins",
            "",
            "VerbForm=Fin",
            "Variant=Short|VerbForm=Part|Voice=Pass",
            "",
        ],
    ),
    (
        "Он сказал , что не придёт , и ушёл .",
        [1, 1, 5, 5, 5, 1, 8, 8, 1, 1],
        ["nsubj", "ROOT", "punct", "mark", "advmod", "ccomp", "punct", "cc", "conj", "punct"],
        ["PRON", "VERB", "PUNCT", "SCONJ", "PART", "VERB", "PUNCT", "CCONJ", "VERB", "PUNCT"],
        [
            "Case=Nom",
            "VerbForm=Fin",
            "",
            "",
            "Polarity=Neg",
            "VerbForm=Fin",
            "",
            "",
            "VerbForm=Fin",
            "",
        ],
    ),
    (
        "Повышение эффективности использования ресурсов обсуждалось .",
        [4, 0, 1, 2, 4, 4],
        ["nsubj:pass", "nmod", "nmod", "nmod", "ROOT", "punct"],
        ["NOUN", "NOUN", "NOUN", "NOUN", "VERB", "PUNCT"],
        ["Case=Nom", "Case=Gen", "Case=Gen", "Case=Gen", "VerbForm=Fin|Voice=Pass", ""],
    ),
    (
        "Ночь .",
        [0, 0],
        ["ROOT", "punct"],
        ["NOUN", "PUNCT"],
        ["Case=Nom", ""],
    ),
    (
        "Ни один из них не хотел уйти , хлопнув дверью .",
        [1, 5, 3, 1, 5, 5, 5, 8, 5, 8, 5],
        [
            "advmod",
            "nsubj",
            "case",
            "nmod",
            "advmod",
            "ROOT",
            "xcomp",
            "punct",
            "advcl",
            "obj",
            "punct",
        ],
        ["PART", "NUM", "ADP", "PRON", "PART", "VERB", "VERB", "PUNCT", "VERB", "NOUN", "PUNCT"],
        [
            "Polarity=Neg",
            "Case=Nom",
            "",
            "Case=Gen",
            "Polarity=Neg",
            "VerbForm=Fin",
            "VerbForm=Inf",
            "",
            "VerbForm=Conv",
            "Case=Ins",
            "",
        ],
    ),
]
DISTANCES = [[4, 1, 1, 1], [1, 2, 1, 3, 1, 5], [4, 1, 1, 1], [], [1, 4, 1, 2, 1, 1, 2, 1]]


def build_doc(sentences):
    words, heads, deps, pos, morphs = [], [], [], [], []
    for sent_words, sent_heads, sent_deps, sent_pos, sent_morphs in sentences:
        offset = len(words)
        words.extend(sent_words.split())
        heads.extend(head + offset for head in sent_heads)
        deps.extend(sent_deps)
        pos.extend(sent_pos)
        morphs.extend(sent_morphs)
    return Doc(
        spacy.blank("ru").vocab, words=words, heads=heads, deps=deps, pos=pos, morphs=morphs
    )


@pytest.fixture(scope="module")
def doc():
    return build_doc(SENTENCES)


@pytest.fixture(scope="module")
def sents(doc):
    return list(doc.sents)


@pytest.fixture(scope="module")
def ss(doc):
    return SyntaxStats(doc)


@pytest.fixture(scope="module")
def nlp():
    pytest.importorskip("ru_core_news_sm")
    return spacy.load("ru_core_news_sm")


def test_init_value_error():
    with pytest.raises(ValueError):
        SyntaxStats(spacy.blank("ru")(text))
    with pytest.raises(ValueError):
        SyntaxStats(
            build_doc([(". . .", [0, 0, 0], ["ROOT", "punct", "punct"], ["PUNCT"] * 3, [""] * 3)])
        )


@pytest.mark.parametrize("source", [666, ["a", "b"], {"a": "b"}, text])
def test_init_type_error(source):
    with pytest.raises(TypeError):
        SyntaxStats(source)


def test_counts(ss):
    assert ss.n_sents == 5
    assert ss.n_words == 27
    assert ss.n_leaves == 13
    assert ss.n_subtrees == 14
    assert ss.n_coordination_chains == 1
    assert ss.n_clauses == 7
    assert ss.n_subordinate_clauses == 1
    assert ss.n_complex_sents == 1
    assert ss.n_nouns == 8
    assert ss.n_genitive_chains == 1
    assert ss.n_participle_clauses == 1
    assert ss.n_converb_clauses == 1
    assert ss.n_verbs == 9
    assert ss.n_passive == 3
    assert ss.n_agentless_passive == 2
    assert ss.n_infinitives == 1
    assert ss.n_negations == 3


def test_distributions(ss):
    assert ss.c_children == {0: 13, 1: 9, 2: 3, 3: 1, 4: 1}
    assert sum(ss.c_deps.values()) == 27
    assert ss.c_deps["ROOT"] == 5
    assert ss.c_deps["nmod"] == 4
    assert "punct" not in ss.c_deps


def test_dependency_distances(ss):
    all_distances = [distance for sent in DISTANCES for distance in sent]
    assert ss.mean_dependency_distance == pytest.approx(40 / 22)
    assert ss.std_dependency_distance == pytest.approx(pstdev(all_distances))
    assert ss.max_dependency_distance == pytest.approx(17 / 4)
    assert ss.p_adjacent_dependencies == pytest.approx(14 / 22)


def test_tree_shape(ss):
    assert ss.tree_depth == pytest.approx(12 / 5)
    assert ss.leaves_per_sent == pytest.approx(13 / 5)
    assert ss.subtrees_per_sent == pytest.approx(14 / 5)
    assert ss.nodes_per_leaf == pytest.approx((2.5 + 1.75 + 5 + 1 + 1.8) / 5)
    assert ss.verb_valency == pytest.approx(9 / 5)


def test_clauses(ss):
    assert ss.coordination_chains_per_sent == pytest.approx(1 / 5)
    assert ss.mean_coordination_chain_len == 2
    assert ss.clauses_per_sent == pytest.approx(7 / 5)
    assert ss.mean_clause_len == pytest.approx(27 / 7)
    assert ss.subordinate_clauses_per_sent == pytest.approx(1 / 5)
    assert ss.p_complex_sents == pytest.approx(1 / 5)


def test_constructions(ss):
    assert ss.modifiers_per_noun == pytest.approx(4 / 8)
    assert ss.genitive_chains_per_sent == pytest.approx(1 / 5)
    assert ss.max_genitive_chain_len == 3
    assert ss.participle_clauses_per_sent == pytest.approx(1 / 5)
    assert ss.mean_participle_clause_len == 2
    assert ss.converb_clauses_per_sent == pytest.approx(1 / 5)
    assert ss.mean_converb_clause_len == 2
    assert ss.p_passive == pytest.approx(3 / 9)
    assert ss.p_agentless_passive == pytest.approx(2 / 3)
    assert ss.infinitives_per_sent == pytest.approx(1 / 5)
    assert ss.negations_per_sent == pytest.approx(3 / 5)
    assert ss.split_predicates_per_sent == 0
    assert ss.split_predicates == ()
    assert ss.noun_verb_ratio == pytest.approx(8 / 9)


def test_split_predicates():
    doc = build_doc(
        [
            (
                "Комиссия осуществляет проверку документов и оказывает помощь .",
                [1, 1, 1, 2, 5, 1, 5, 1],
                ["nsubj", "ROOT", "obj", "nmod", "cc", "conj", "obj", "punct"],
                ["NOUN", "VERB", "NOUN", "NOUN", "CCONJ", "VERB", "NOUN", "PUNCT"],
                [
                    "Case=Nom",
                    "VerbForm=Fin",
                    "Case=Acc",
                    "Case=Gen",
                    "",
                    "VerbForm=Fin",
                    "Case=Acc",
                    "",
                ],
            ),
            (
                "Было принято решение уехать .",
                [1, 1, 1, 1, 1],
                ["aux:pass", "ROOT", "nsubj:pass", "xcomp", "punct"],
                ["AUX", "VERB", "NOUN", "VERB", "PUNCT"],
                [
                    "VerbForm=Fin",
                    "Variant=Short|VerbForm=Part|Voice=Pass",
                    "Case=Nom",
                    "VerbForm=Inf",
                    "",
                ],
            ),
            (
                "Он читает книгу и проводит время .",
                [1, 1, 1, 4, 1, 4, 1],
                ["nsubj", "ROOT", "obj", "cc", "conj", "obj", "punct"],
                ["PRON", "VERB", "NOUN", "CCONJ", "VERB", "NOUN", "PUNCT"],
                ["Case=Nom", "VerbForm=Fin", "Case=Acc", "", "VerbForm=Fin", "Case=Acc", ""],
            ),
        ]
    )
    pairs = find_split_predicates(doc)
    assert [(verb.text, noun.text) for verb, noun in pairs] == [
        ("осуществляет", "проверку"),
        ("оказывает", "помощь"),
        ("принято", "решение"),
    ]
    assert is_light_verb(doc[1]) and is_light_verb(doc[5]) and not is_light_verb(doc[14])
    assert is_split_predicate_noun(doc[2]) and is_split_predicate_noun(doc[6])
    assert not is_split_predicate_noun(doc[3]) and not is_split_predicate_noun(doc[15])
    assert get_lemma(doc[2]) == "проверка"
    assert get_lemma(doc[1]) == "осуществлять"
    ss = SyntaxStats(doc)
    assert ss.n_split_predicates == 3
    assert ss.split_predicates == ("осуществляет проверку", "оказывает помощь", "принято решение")
    assert ss.split_predicates_per_sent == 1
    assert ss.noun_verb_ratio == pytest.approx(7 / 6)


def test_single_word_sentence():
    ss = SyntaxStats(build_doc(SENTENCES[3:4]))
    assert isnan(ss.mean_dependency_distance)
    assert isnan(ss.std_dependency_distance)
    assert isnan(ss.p_adjacent_dependencies)
    assert isnan(ss.max_dependency_distance)
    assert ss.tree_depth == 0
    assert ss.nodes_per_leaf == 1
    assert ss.clauses_per_sent == 1
    assert ss.mean_clause_len == 1
    assert isnan(ss.verb_valency)
    assert isnan(ss.mean_coordination_chain_len)
    assert ss.modifiers_per_noun == 0
    assert isnan(ss.p_passive)
    assert isnan(ss.p_agentless_passive)
    assert isnan(ss.mean_participle_clause_len)
    assert isnan(ss.mean_converb_clause_len)


def test_no_nouns():
    ss = SyntaxStats(build_doc(SENTENCES[1:2]))
    assert isnan(ss.modifiers_per_noun)
    assert ss.p_passive == 0
    assert isnan(ss.p_agentless_passive)


def test_calc_dependency_distances(doc, sents):
    for sent, expected in zip(sents, DISTANCES, strict=True):
        assert calc_dependency_distances(sent) == expected
    assert calc_dependency_distances(doc) == [d for sent in DISTANCES for d in sent]
    assert calc_dependency_distances(sents[1][2:6]) == [2, 1]


def test_calc_tree_depth(doc, sents):
    assert [calc_tree_depth(sent) for sent in sents] == [3, 2, 4, 0, 3]
    assert calc_tree_depth(doc) == 4
    assert calc_tree_depth([]) == 0


def test_calc_coordination_chains(doc, sents):
    assert [calc_coordination_chains(sent) for sent in sents] == [[], [2], [], [], []]
    assert calc_coordination_chains(doc) == [2]


def test_calc_genitive_chains(doc, sents):
    assert [calc_genitive_chains(sent) for sent in sents] == [[], [], [3], [], []]
    assert calc_genitive_chains(doc) == [3]
    assert [is_genitive_modifier(token) for token in sents[2]] == [
        False,
        True,
        True,
        True,
        False,
        False,
    ]
    assert not is_genitive_modifier(sents[4][3])


def test_clause_heads(sents):
    assert [token.text for sent in sents for token in sent if is_clause_head(token)] == [
        "продан",
        "сказал",
        "придёт",
        "ушёл",
        "обсуждалось",
        "Ночь",
        "хотел",
    ]
    assert [
        token.text for sent in sents for token in sent if is_subordinate_clause_head(token)
    ] == ["придёт"]


def test_subordinate_conj():
    doc = build_doc(
        [
            (
                "Он знал , что она придёт и уйдёт .",
                [1, 1, 5, 5, 5, 1, 7, 5, 1],
                ["nsubj", "ROOT", "punct", "mark", "nsubj", "ccomp", "cc", "conj", "punct"],
                ["PRON", "VERB", "PUNCT", "SCONJ", "PRON", "VERB", "CCONJ", "VERB", "PUNCT"],
                ["", "VerbForm=Fin", "", "", "", "VerbForm=Fin", "", "VerbForm=Fin", ""],
            )
        ]
    )
    assert [token.text for token in doc if is_subordinate_clause_head(token)] == [
        "придёт",
        "уйдёт",
    ]
    ss = SyntaxStats(doc)
    assert ss.n_clauses == 3
    assert ss.n_subordinate_clauses == 2


def test_parataxis():
    doc = build_doc(
        [
            (
                "Во-первых , он не пришёл .",
                [4, 4, 4, 4, 4, 4],
                ["parataxis", "punct", "nsubj", "advmod", "ROOT", "punct"],
                ["ADV", "PUNCT", "PRON", "PART", "VERB", "PUNCT"],
                ["", "", "Case=Nom", "Polarity=Neg", "VerbForm=Fin", ""],
            ),
            (
                "Он сказал : уходи .",
                [1, 1, 1, 1, 1],
                ["nsubj", "ROOT", "punct", "parataxis", "punct"],
                ["PRON", "VERB", "PUNCT", "VERB", "PUNCT"],
                ["Case=Nom", "VerbForm=Fin", "", "Mood=Imp|VerbForm=Fin", ""],
            ),
            (
                "Она думала , что он умён .",
                [1, 1, 5, 5, 5, 1, 1],
                ["nsubj", "ROOT", "punct", "mark", "nsubj", "ccomp", "punct"],
                ["PRON", "VERB", "PUNCT", "SCONJ", "PRON", "ADJ", "PUNCT"],
                ["Case=Nom", "VerbForm=Fin", "", "", "Case=Nom", "Variant=Short", ""],
            ),
        ]
    )
    assert [token.text for token in doc if is_clause_head(token)] == [
        "пришёл",
        "сказал",
        "уходи",
        "думала",
        "умён",
    ]
    assert not is_predicate(doc[0])
    assert is_predicate(doc[9])
    assert is_predicate(doc[16])
    ss = SyntaxStats(doc)
    assert ss.n_clauses == 5
    assert ss.n_subordinate_clauses == 1


def test_max_dependency_distance_skips_sents_without_dependencies():
    ss = SyntaxStats(build_doc([SENTENCES[3], SENTENCES[1]]))
    assert ss.max_dependency_distance == 5
    assert ss.mean_dependency_distance == pytest.approx(13 / 6)


def test_token_predicates(sents):
    first, second, _, _, last = sents
    assert is_participle(first[2])
    assert not is_participle(first[6])
    assert is_participle_clause(first[2])
    assert not is_participle_clause(first[6])
    assert subtree_len(first[2]) == 2
    assert is_passive(first[2]) and not is_agentless(first[2])
    assert is_passive(first[6]) and is_agentless(first[6])
    assert not is_passive(second[1])
    assert not is_finite_verb(first[5])
    assert is_finite_verb(second[1])
    assert [calc_valency(token) for token in (second[1], second[5], second[8])] == [2, 2, 0]
    assert is_negation(second[4]) and is_negation(last[0]) and not is_negation(last[1])
    assert is_converb_clause(last[8])
    assert not is_converb_clause(last[6])


def test_count_noun_modifiers(sents):
    assert [count_noun_modifiers(token) for token in sents[2]] == [1, 1, 1, 0, 0, 0]
    assert count_noun_modifiers(sents[0][0]) == 1


def test_get_stats(ss):
    stats = ss.get_stats()
    assert list(stats) == list(SYNTAX_STATS_DESC)
    for key in SYNTAX_STATS_DESC:
        assert stats[key] == getattr(ss, key)


def test_print_stats(ss, capsys):
    ss.print_stats()
    captured = capsys.readouterr().out
    for value in SYNTAX_STATS_DESC.values():
        assert value in captured


def test_model(nlp):
    doc = nlp(text)
    ss = SyntaxStats(doc)
    assert ss.n_sents == len(list(doc.sents))
    assert ss.n_words == sum(1 for token in doc if not token.is_punct and not token.is_space)
    assert ss.n_leaves + ss.n_subtrees == ss.n_words
    assert ss.n_clauses >= ss.n_sents
    assert ss.n_subordinate_clauses <= ss.n_clauses
    assert ss.n_passive <= ss.n_verbs
    assert 0 <= ss.p_adjacent_dependencies <= 1
    assert ss.tree_depth >= 1
    assert ss.max_dependency_distance >= 1
    assert ss.n_coordination_chains >= 1
    assert ss.n_genitive_chains >= 1
    assert ss.n_participle_clauses == ss.n_converb_clauses == ss.n_passive == 0


def test_model_parataxis(nlp):
    ss = SyntaxStats(
        nlp("Во-первых, он не пришёл. Он, например, не пришёл. Он, конечно, не пришёл.")
    )
    assert ss.n_clauses == 3
    assert isnan(ss.p_agentless_passive)


def test_model_split_predicates(nlp):
    doc = nlp(
        "Комиссия осуществляет проверку документов и оказывает содействие участникам. "
        "Было принято решение о проведении консультаций. Он читает книгу."
    )
    ss = SyntaxStats(doc)
    assert ss.split_predicates == (
        "осуществляет проверку",
        "оказывает содействие",
        "принято решение",
    )
    assert ss.split_predicates_per_sent == 1
    assert ss.noun_verb_ratio == pytest.approx(9 / 4)


def test_model_constructions(nlp):
    ss = SyntaxStats(
        nlp("Дом, построенный рабочими в прошлом году, был продан. Он ушёл, хлопнув дверью.")
    )
    assert ss.n_participle_clauses == 1
    assert ss.mean_participle_clause_len == 5
    assert ss.n_converb_clauses == 1
    assert ss.mean_converb_clause_len == 2
    assert ss.n_passive == 2
    assert ss.n_agentless_passive == 1
