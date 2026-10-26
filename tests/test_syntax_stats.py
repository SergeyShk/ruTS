from math import isnan
from statistics import pstdev

import anyts.syntax_stats
import pytest
import spacy
from anyts.utils import iter_doc_units
from spacy.tokens import Doc

from ruts import SyntaxStats
from ruts.constants import SYNTAX_STATS_DESC
from ruts.syntax_stats import (
    calc_genitive_chains,
    calc_valency,
    count_noun_modifiers,
    find_split_predicates,
    get_lemma,
    is_agentless,
    is_clause_head,
    is_converb_clause,
    is_finite_verb,
    is_genitive_modifier,
    is_infinitive_clause,
    is_infinitive_clause_head,
    is_infinitive_periphrasis,
    is_light_verb,
    is_negation,
    is_participle,
    is_participle_clause,
    is_passive,
    is_predicate,
    is_reflexive,
    is_split_predicate_noun,
    is_subordinate_clause_head,
    is_subordinating_mark,
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
    assert ss.n_clauses == 8
    assert ss.n_subordinate_clauses == 1
    assert ss.n_complex_sents == 1
    assert ss.n_infinitive_clauses == 1
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
    assert ss.clauses_per_sent == pytest.approx(8 / 5)
    assert ss.mean_clause_len == pytest.approx(27 / 8)
    assert ss.subordinate_clauses_per_sent == pytest.approx(1 / 5)
    assert ss.p_complex_sents == pytest.approx(1 / 5)
    assert ss.infinitive_clauses_per_sent == pytest.approx(1 / 5)


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
            (
                "Проверка проведена комиссией в присутствии руководства .",
                [1, 1, 1, 4, 1, 4, 1],
                ["nsubj:pass", "ROOT", "obl:agent", "case", "obl", "nmod", "punct"],
                ["NOUN", "VERB", "NOUN", "ADP", "NOUN", "NOUN", "PUNCT"],
                [
                    "Case=Nom",
                    "Variant=Short|VerbForm=Part|Voice=Pass",
                    "Case=Ins",
                    "",
                    "Case=Loc",
                    "Case=Gen",
                    "",
                ],
            ),
            (
                "Работа проводится отделом .",
                [1, 1, 1, 1],
                ["nsubj", "ROOT", "obl", "punct"],
                ["NOUN", "VERB", "NOUN", "PUNCT"],
                ["Case=Nom", "VerbForm=Fin|Voice=Mid", "Case=Ins", ""],
            ),
        ]
    )
    pairs = find_split_predicates(doc)
    assert [(verb.text, noun.text) for verb, noun in pairs] == [
        ("осуществляет", "проверку"),
        ("оказывает", "помощь"),
        ("принято", "решение"),
        ("проведена", "Проверка"),
        ("проводится", "Работа"),
    ]
    assert is_light_verb(doc[1]) and is_light_verb(doc[5]) and not is_light_verb(doc[14])
    assert is_split_predicate_noun(doc[2]) and is_split_predicate_noun(doc[6])
    assert not is_split_predicate_noun(doc[3]) and not is_split_predicate_noun(doc[15])
    assert get_lemma(doc[2]) == "проверка"
    assert get_lemma(doc[1]) == "осуществлять"
    ss = SyntaxStats(doc)
    assert ss.n_split_predicates == 5
    assert ss.split_predicates == (
        "осуществляет проверку",
        "оказывает помощь",
        "принято решение",
        "проведена Проверка",
        "проводится Работа",
    )
    assert ss.split_predicates_per_sent == 1
    assert ss.noun_verb_ratio == pytest.approx(13 / 8)


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
        "уйти",
    ]
    assert [
        token.text for sent in sents for token in sent if is_subordinate_clause_head(token)
    ] == ["придёт"]
    assert [
        token.text for sent in sents for token in sent if is_infinitive_clause_head(token)
    ] == ["уйти"]


@pytest.mark.parametrize(
    ("text", "clauses", "infinitive", "periphrasis"),
    [
        ("Он может уйти.", ["может"], [], True),
        ("Она должна была прийти.", ["должна"], [], True),
        ("Он начал читать и писать.", ["начал"], [], True),
        ("Он перестал курить.", ["перестал"], [], True),
        ("Давайте играть.", ["Давайте"], [], True),
        ("Давай пойдём.", ["Давай"], [], True),
        ("Не давайте детям играть.", ["давайте", "играть"], ["играть"], False),
        ("Он хочет уйти.", ["хочет", "уйти"], ["уйти"], False),
        ("Я попросил его уйти.", ["попросил", "уйти"], ["уйти"], False),
        ("Он решил уехать.", ["решил", "уехать"], ["уехать"], False),
        # Инфинитив дополняет слово выше неличных xcomp
        ("Он оказался способным понять.", ["оказался", "понять"], ["понять"], False),
        # Глагол с леммой краткой формы - не модальное прилагательное
        ("Его вынудили уйти.", ["вынудили", "уйти"], ["уйти"], False),
        ("Он продолжал пытаться уйти.", ["продолжал", "уйти"], ["уйти"], True),
        # Инфинитив в обороте принадлежит обороту
        ("Желая уйти, он встал.", ["встал"], [], False),
        ("Человек, решивший уйти, встал.", ["встал"], [], False),
    ],
)
def test_model_infinitive_clauses(nlp, text, clauses, infinitive, periphrasis):
    """Инфинитив при глаголе - своя клауза, но не придаточная, кроме сочетаний одной предикации"""
    doc = nlp(text)
    assert [token.text for token in doc if is_clause_head(token)] == clauses
    assert not any(is_subordinate_clause_head(token) for token in doc)
    assert [token.text for token in doc if is_infinitive_clause_head(token)] == infinitive
    ss = SyntaxStats(doc)
    assert (ss.n_clauses, ss.n_subordinate_clauses) == (len(clauses), 0)
    assert ss.n_infinitive_clauses == len(infinitive)
    assert [token.text for token in doc if is_infinitive_clause(token)] == infinitive
    xcomp = next(token for token in doc if token.dep_ == "xcomp")
    assert ss.is_infinitive_periphrasis(xcomp) is is_infinitive_periphrasis(xcomp) is periphrasis


def test_infinitive_periphrasis_hook(nlp):
    """Крючок подкласса меняет и клаузы, и придаточные"""

    class Wishes(SyntaxStats):
        def is_infinitive_periphrasis(self, token):
            return get_lemma(token.head) == "хотеть" or super().is_infinitive_periphrasis(token)

    doc = nlp("Он хочет уйти, но может остаться.")
    ss, wishes = SyntaxStats(doc), Wishes(doc)
    assert (ss.n_clauses, ss.n_infinitive_clauses) == (3, 1)
    assert (wishes.n_clauses, wishes.n_infinitive_clauses) == (2, 0)


@pytest.mark.parametrize(
    "text",
    [
        "Мне нужно уйти.",
        "Мне надо уйти.",
        "Можно войти?",
        "Нельзя курить.",
        "Необходимо проверить данные.",
        "Вам следует уйти.",
        "Пора идти домой.",
        "Он взялся читать.",
        "Он кинулся бежать.",
        "Мне пришлось уйти.",
        "Мне приходится уходить.",
        "Стоит отметить это.",
        # Модальные краткие прилагательные во всех формах; полная форма - своя клауза (выше)
        *(
            f"{subject} {adjective} {verb}."
            for adjective_forms, verb in (
                (("готов", "готова", "готовы"), "уйти"),
                (("рад", "рада", "рады"), "помочь"),
                (("намерен", "намерена", "намерены"), "уехать"),
                (("обязан", "обязана", "обязаны"), "прийти"),
                (("способен", "способна", "способны"), "решить"),
                (("склонен", "склонна", "склонны"), "преувеличивать"),
                (("вынужден", "вынуждена", "вынуждены"), "уйти"),
            )
            for subject, adjective in zip(("Он", "Она", "Они"), adjective_forms, strict=True)
        ),
    ],
)
def test_model_periphrases_of_one_clause(nlp, text):
    """Инфинитив-подлежащее модального слова и инфинитив при «взяться», «кинуться» -
    одна предикация"""
    ss = SyntaxStats(nlp(text))
    assert (ss.n_clauses, ss.n_subordinate_clauses, ss.n_infinitive_clauses) == (1, 0, 0)


def test_finite_xcomp_is_no_clause():
    """Личная форма со связью xcomp у русских моделей - ошибка разбора, а не клауза"""
    doc = build_doc(
        [
            (
                "Он сказал , пойдём .",
                [1, 1, 3, 1, 1],
                ["nsubj", "ROOT", "punct", "xcomp", "punct"],
                ["PRON", "VERB", "PUNCT", "VERB", "PUNCT"],
                ["", "VerbForm=Fin", "", "VerbForm=Fin", ""],
            )
        ]
    )
    assert not is_clause_head(doc[3]) and not is_infinitive_periphrasis(doc[3])
    assert anyts.syntax_stats.is_clause_head(doc[3])


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
    assert ss.n_words == sum(1 for _ in iter_doc_units(doc, join_hyphens=True))
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


@pytest.mark.parametrize(
    ("hyphenated", "plain"),
    [
        ("Затем я понял кое-что и другое.", "Затем я понял всё и другое."),
        (
            "В углу стоял диван-кровать, который купили вчера.",
            "В углу стоял диван, который купили вчера.",
        ),
        ("Он занял кресло вице-губернатора области.", "Он занял кресло губернатора области."),
        ("Он вице-губернатор.", "Он губернатор."),
    ],
)
def test_model_hyphenated_words(nlp, hyphenated, plain):
    # Связь дефисного слова держит не первая часть, деревья пар одинаковые
    first, second = SyntaxStats(nlp(hyphenated)), SyntaxStats(nlp(plain))
    for name in (
        "mean_dependency_distance",
        "max_dependency_distance",
        "tree_depth",
        "n_coordination_chains",
        "n_leaves",
        "c_children",
        "c_deps",
        "n_clauses",
        "n_genitive_chains",
    ):
        assert getattr(first, name) == getattr(second, name), name


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


def test_is_split_predicate_noun_verb(nlp):
    doc = nlp("Провели работу. Получили работу. Получили разрешение.")
    assert is_split_predicate_noun(doc[1], doc[0])
    assert not is_split_predicate_noun(doc[4], doc[3])
    assert is_split_predicate_noun(doc[4])
    assert is_split_predicate_noun(doc[7], doc[6])


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Проверка проводится комиссией.", [("проводится", "Проверка")]),
        ("Меры принимаются руководством.", [("принимаются", "Меры")]),
        ("Контроль осуществляется ежедневно.", [("осуществляется", "Контроль")]),
        ("Работа ведётся постоянно.", [("ведётся", "Работа")]),
        (
            "Проверка была проведена инспекцией в присутствии руководства.",
            [("проведена", "Проверка")],
        ),
        ("Решение принято комиссией с учетом замечаний.", [("принято", "Решение")]),
        ("Он предпринял шаг навстречу при поддержке друзей.", [("предпринял", "шаг")]),
        ("Он сделал шаг назад.", []),
        ("Он получил работу на заводе.", []),
        ("Он получил место учителя.", []),
        ("Эпидемия приняла массовый характер.", [("приняла", "характер")]),
        ("Образцы подвергли тщательному анализу.", [("подвергли", "анализу")]),
        ("По этому факту ведётся проверка.", [("ведётся", "проверка")]),
        ("Он совершил попытку побега.", [("совершил", "попытку")]),
        ("Помощь была оказана вовремя.", [("оказана", "Помощь")]),
        ("Ошибка получилась случайно.", []),
        ("Кот имеет хвост.", []),
    ],
)
def test_model_split_predicates_cases(nlp, text, expected):
    assert [(verb.text, noun.text) for verb, noun in find_split_predicates(nlp(text))] == expected


def test_is_reflexive(nlp):
    doc = nlp("Проверка проводится, решение принято, кот спит.")
    assert is_reflexive(doc[1])
    assert is_reflexive(doc[4])
    assert not is_reflexive(doc[7])
    assert not is_reflexive(doc[0])


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


def test_negation_stress_mark():
    """Частица «не» со знаком ударения без признака Polarity - тоже отрицание"""
    doc = Doc(spacy.blank("ru").vocab, words=["не\u0301", "НЕ"], pos=["PART", "PART"])
    assert [is_negation(token) for token in doc] == [True, True]


def test_clause_head_conj_loop():
    """Однородные, зацикленные разбором через conj, - не клауза, а не RecursionError"""
    vocab = spacy.blank("ru").vocab
    doc = Doc(
        vocab,
        words=["Он", "пришел", "ушел", "спал"],
        heads=[1, 1, 3, 2],
        deps=["nsubj", "ROOT", "conj", "conj"],
        pos=["PRON", "VERB", "VERB", "VERB"],
    )
    assert not is_clause_head(doc[2])
    assert SyntaxStats(doc).n_clauses == 1


def test_pickle(nlp):
    """Объект синтаксических статистик сериализуется вместе со словами предложений"""
    import copy
    import pickle

    stats = SyntaxStats(nlp("Дом, построенный рабочими, был продан. Он ушёл, хлопнув дверью."))
    for clone in (pickle.loads(pickle.dumps(stats)), copy.deepcopy(stats)):
        assert repr(clone.get_stats()) == repr(stats.get_stats())
        assert [token.text for token in clone.sents[1]] == ["Он", "ушёл", "хлопнув", "дверью"]


@pytest.mark.parametrize(
    ("text", "word", "expected"),
    [
        ("Он ушел, ибо устал.", "ибо", True),
        ("Он ушел, после того как все легли.", "как", True),
        ("Он бежал быстро, как бегают зайцы.", "как", False),
        ("Петля не петля, а вышла, что называется, штука хорошая.", "что", False),
        ("Ну и что ж ты бы мог сделать?", "что", False),
        ("— А что вы теперь с нашими письмами сделаете?", "что", False),
        ("Он сказал, что придет.", "что", True),
        ("Когда у тебя заболел живот, то я к тебе зашёл.", "то", False),
        ("Любопытно стало Ваське: что это с ним сделалось?", "что", False),
    ],
)
def test_is_subordinating_mark(nlp, text, word, expected):
    """Подчинительный союз - по списку и контексту: составной «после того как», не «то»
    главной клаузы и не местоимение «что»"""
    doc = nlp(text)
    marks = [token for token in doc if token.dep_ == "mark" and token.lower_ == word]
    assert marks and is_subordinating_mark(marks[0]) is expected
    stats = SyntaxStats(doc)
    assert stats.is_subordinating_mark(marks[0]) is expected
    # Модульные проверки клауз - с тем же правилом союза
    marked = [
        token
        for token in doc
        if token.dep_ in ("conj", "parataxis") and marks[0] in token.children
    ]
    for head in marked:
        assert is_subordinate_clause_head(head) == stats.is_subordinate_clause_head(head)


@pytest.mark.parametrize(
    ("text", "n_subordinate"),
    [
        # «Не то чтобы» - частица (Чехов)
        (
            "Скажу вам без обиняков, больная моя… как бы это того… ну, полюбила, что ли, меня… "
            "или нет, не то чтобы полюбила… а впрочем… право, как это, того-с…",
            1,
        ),
        # «Чем» в начале вставленной реплики с восклицанием - местоимение (Тургенев)
        (
            "Признаться сказать, рана моего сердца не очень была глубока; но я почел долгом "
            "предаться на некоторое время печали и одиночеству – чем молодость не тешится! – "
            "и поселился в З.",
            0,
        ),
    ],
)
def test_marks_of_particles_and_replicas(nlp, text, n_subordinate):
    """Союз после «не то» и местоимение в начале реплики с вопросом или восклицанием -
    не подчинительные союзы"""
    assert SyntaxStats(nlp(text)).n_subordinate_clauses == n_subordinate


def test_conjuncts_of_a_marked_clause(nlp):
    """Однородные помеченной клаузы с общим подлежащим - сказуемые главной, которые модель
    повесила на придаточное, а не придаточные"""
    doc = nlp(
        "Поздно одумалась королевна, что сказала слово нехорошее, заплакала горькими слезами, "
        "воротилась домой и стала жить одна-одинехонька."
    )
    stats = SyntaxStats(doc)
    heads = {token.text: token for token in doc}
    assert stats.is_subordinate_clause_head(heads["сказала"])
    assert not any(
        stats.is_subordinate_clause_head(heads[word]) for word in ("заплакала", "воротилась")
    )
    assert stats.n_t_units == 1


def test_doc_without_morphologizer():
    """Без морфологического анализатора части речи есть только у пробелов - это не разметка"""
    nlp = spacy.load("ru_core_news_sm", exclude=["morphologizer"])
    doc = nlp("Мама мыла раму, а папа читал книгу.\n\nДети играли во дворе.")
    assert doc.has_annotation("POS")
    with pytest.raises(ValueError, match=r"не отключая ее теггер или морфологический анализатор"):
        SyntaxStats(doc)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Вчера вечером кот спал.", {"words_before_root": 3.0}),
        ("Кот спит. Спит собака.", {"p_preverbal_subjects": 0.5}),
        (
            "Книга лежит на столе в комнате у окна.",
            {"prep_chains_per_sent": 1.0, "max_prep_chain_len": 2},
        ),
        (
            "Я знаю, что он придёт. Мы уйдём.",
            {"t_units_per_sent": 1.0, "clauses_per_t_unit": 1.5, "p_complex_t_units": 0.5},
        ),
        # Русское сочетание одной предикации - одна клауза; инфинитивная клауза - не клауза L2SCA
        ("Он может уйти.", {"clauses_per_sent": 1.0, "clauses_per_t_unit": 1.0}),
        ("Он хочет уйти.", {"clauses_per_sent": 2.0, "clauses_per_t_unit": 1.0}),
        ("Невозможно описать.", {"clauses_per_sent": 1.0}),
        # Причастие-определение - не глагольная группа, однородное сказуемое - не клауза L2SCA
        ("Читающий мальчик сидел у окна.", {"verb_phrases_per_t_unit": 1.0}),
        (
            "Он взял ведро и пошел за водой.",
            {"clauses_per_t_unit": 1.0, "coordinate_phrases_per_clause": 1.0},
        ),
        # Инфинитив с «чтобы» и при предикативе - инфинитивная клауза, а не придаточная
        (
            "Он пришел, чтобы помочь.",
            {"subordinate_clauses_per_sent": 0.0, "infinitive_clauses_per_sent": 1.0},
        ),
        ("Трудно сказать.", {"p_complex_sents": 0.0, "infinitive_clauses_per_sent": 1.0}),
        # Инфинитив при однородном инфинитиве перифразы сохраняет свою клаузу
        (
            "Мы все готовы придти к вам и помочь вам жить.",
            {"clauses_per_sent": 2.0, "infinitive_clauses_per_sent": 1.0},
        ),
        # Клауза conj с «ибо» - придаточная; «то» после «если» - соотносительное слово
        (
            "Он ушел, ибо устал.",
            {
                "t_units_per_sent": 1.0,
                "subordinate_clauses_per_sent": 1.0,
                "p_complex_t_units": 1.0,
            },
        ),
        (
            "Он ушёл, ибо устал.",
            {
                "t_units_per_sent": 1.0,
                "subordinate_clauses_per_sent": 1.0,
                "p_complex_t_units": 1.0,
            },
        ),
        ("Если пойдет дождь, то мы останемся.", {"subordinate_clauses_per_sent": 1.0}),
        # Союз с «то» после него у того же сказуемого - главная клауза, местоимение - не союз
        (
            "Пел он громко, и так как мать молчала, то Васька решил, что ей понравилось пение.",
            {"t_units_per_sent": 2.0, "subordinate_clauses_per_sent": 1.0},
        ),
        (
            "Когда у тебя заболел живот, то я к тебе зашёл, а когда у меня горло, то ты не зашёл.",
            {"t_units_per_sent": 2.0},
        ),
        ("Петля не петля, а вышла, что называется, штука хорошая.", {"p_complex_t_units": 0.0}),
        # «То» вложенного «если..., то» не делает главной клаузу с «что»
        (
            "Они говорили, что сначала надо подумать и что если б удалось исключить Петрова "
            "из списка, то было бы очень хорошо.",
            {"t_units_per_sent": 1.0, "subordinate_clauses_per_sent": 3.0},
        ),
        ("Он молчит, тогда как все кричат.", {"subordinate_clauses_per_sent": 1.0}),
        # Предложная цепочка от именного сказуемого без связки
        ("Он в доме у мэра.", {"max_prep_chain_len": 2}),
    ],
)
def test_model_new_core_stats(nlp, text, expected):
    """Метрики ядра 0.4 на русских предложениях с русскими крючками клауз"""
    stats = SyntaxStats(nlp(text)).get_stats()
    assert {key: stats[key] for key in expected} == pytest.approx(expected)
