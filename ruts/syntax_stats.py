from collections.abc import Iterable, Sequence
from math import nan
from statistics import fmean

import anyts.syntax_stats
from anyts.constants import CLAUSE_DEPS
from anyts.syntax_stats import (
    base_dep as base_dep,
    calc_coordination_chains as calc_coordination_chains,
    calc_dependency_distances as calc_dependency_distances,
    calc_modifier_chains as calc_modifier_chains,
    calc_tree_depth as calc_tree_depth,
    calc_valency as calc_valency,
    count_children as count_children,
    count_noun_modifiers as count_noun_modifiers,
    get_children as get_children,
    get_words as get_words,
    has_agent as has_agent,
    is_agentless as is_agentless,
    is_passive as is_passive,
    is_predicate as is_predicate,
    is_root as is_root,
    subtree_len as subtree_len,
)
from anyts.utils import (
    has_feature as has_feature,
    is_finite_verb as is_finite_verb,
    is_infinitive as is_infinitive,
    is_word as is_word,
)
from spacy.tokens import Doc, Token

from .constants import (
    CORE_MESSAGES,
    LIGHT_VERBS,
    NEGATION_PARTICLES,
    SPLIT_PREDICATE_NOUNS,
    SYNTAX_STATS_DESC,
)
from .utils import is_verbal_noun, lemmatize, normalize_yo, strip_marks

SPLIT_PREDICATE_DEPS = ("obj", "nsubj:pass", "nsubj", "iobj", "nmod", "obl")


class SyntaxStats(anyts.syntax_stats.SyntaxStats):
    """
    Класс для вычисления синтаксических статистик текста

    Описание:
        Расширяет SyntaxStats ядра anyTS крючками русского языка: клаузы, причастные
        обороты, отрицания и расщепленные сказуемые - по правилам русского языка,
        дефисные слова склеиваются; свои статистики ruTS - цепочки родительных падежей
        и деепричастные обороты. Источник данных - объект Doc библиотеки spaCy
        с разбором зависимостей Universal Dependencies (модели ru_core_news_sm,
        ru_core_news_md, ru_core_news_lg). Определения признаков следуют работе
        Иванова, Солнышкиной и Соловьёва (2018)

    Ссылки:
        https://universaldependencies.org/u/dep/
        https://dialogue-conf.org/media/4302/ivanovvv.pdf

    Пример использования:
        >>> import spacy
        >>> from ruts import SyntaxStats
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> text = "Дом, построенный рабочими в прошлом году, был продан. Он сказал, что не придёт, и ушёл, хлопнув дверью."
        >>> ss = SyntaxStats(nlp(text))
        >>> ss.get_stats()
        {'mean_dependency_distance': 1.9333333333333333,
        'std_dependency_distance': 1.6110727964792764,
        'max_dependency_distance': 5.0,
        'p_adjacent_dependencies': 0.6,
        'tree_depth': 4.0,
        'leaves_per_sent': 4.5,
        'subtrees_per_sent': 4.0,
        'nodes_per_leaf': 1.9,
        'verb_valency': 2.0,
        'coordination_chains_per_sent': 0.5,
        'mean_coordination_chain_len': 2.0,
        'clauses_per_sent': 1.5,
        'mean_clause_len': 5.666666666666667,
        'subordinate_clauses_per_sent': 0.5,
        'p_complex_sents': 0.5,
        'modifiers_per_noun': 0.4,
        'genitive_chains_per_sent': 0.0,
        'max_genitive_chain_len': 0,
        'participle_clauses_per_sent': 0.5,
        'mean_participle_clause_len': 5.0,
        'converb_clauses_per_sent': 0.5,
        'mean_converb_clause_len': 2.0,
        'p_passive': 0.4,
        'p_agentless_passive': 0.5,
        'infinitives_per_sent': 0.0,
        'negations_per_sent': 0.5,
        'split_predicates_per_sent': 0.0,
        'noun_verb_ratio': 1.0}
        >>> ss.c_children
        {0: 9, 1: 2, 2: 5, 3: 1}

    Аргументы:
        source (Doc): Источник данных (объект Doc с разбором зависимостей)

    Атрибуты:
        sents (tuple[tuple[Token, ...], ...]): Слова предложений
        n_sents (int): Количество предложений, содержащих слова
        n_words (int): Количество слов
        n_leaves (int): Количество листьев - слов без зависимых слов
        n_subtrees (int): Количество поддеревьев - слов с зависимыми словами
        n_coordination_chains (int): Количество сочинительных цепочек
        n_clauses (int): Количество клауз
        n_subordinate_clauses (int): Количество придаточных клауз
        n_complex_sents (int): Количество предложений с придаточными
        n_nouns (int): Количество существительных
        n_genitive_chains (int): Количество цепочек родительных падежей
        n_participle_clauses (int): Количество причастных оборотов
        n_converb_clauses (int): Количество деепричастных оборотов
        n_verbs (int): Количество глагольных форм
        n_passive (int): Количество пассивных глагольных форм
        n_agentless_passive (int): Количество пассивных форм без агенса
        n_infinitives (int): Количество инфинитивов
        n_negations (int): Количество отрицательных частиц
        n_split_predicates (int): Количество расщепленных сказуемых
        split_predicates (tuple[str]): Кортеж расщепленных сказуемых (глагол и существительное)
        c_children (dict[int, int]): Распределение слов по числу зависимых слов
        c_deps (dict[str, int]): Распределение слов по синтаксическим отношениям
        mean_dependency_distance (float): Средняя длина зависимости
        std_dependency_distance (float): Стандартное отклонение длины зависимости
        max_dependency_distance (float): Среднее по предложениям с зависимостями наибольших длин зависимости
        p_adjacent_dependencies (float): Доля смежных связей - зависимостей длины 1
        tree_depth (float): Средняя по предложениям глубина дерева зависимостей
        leaves_per_sent (float): Листьев на предложение
        subtrees_per_sent (float): Поддеревьев на предложение
        nodes_per_leaf (float): Среднее по предложениям отношение числа слов к числу листьев
        verb_valency (float): Среднее число зависимых у финитного глагола
        coordination_chains_per_sent (float): Сочинительных цепочек на предложение
        mean_coordination_chain_len (float): Средняя длина сочинительной цепочки
        clauses_per_sent (float): Клауз на предложение
        mean_clause_len (float): Средняя длина клаузы в словах
        subordinate_clauses_per_sent (float): Придаточных клауз на предложение
        p_complex_sents (float): Доля предложений хотя бы с одной придаточной клаузой
        modifiers_per_noun (float): Среднее число модификаторов у существительного
        genitive_chains_per_sent (float): Цепочек родительных падежей на предложение
        max_genitive_chain_len (int): Максимальная длина цепочки родительных падежей
        participle_clauses_per_sent (float): Причастных оборотов на предложение
        mean_participle_clause_len (float): Средняя длина причастного оборота в словах
        converb_clauses_per_sent (float): Деепричастных оборотов на предложение
        mean_converb_clause_len (float): Средняя длина деепричастного оборота в словах
        p_passive (float): Доля пассивных форм среди глагольных форм
        p_agentless_passive (float): Доля форм без агенса среди пассивных
        infinitives_per_sent (float): Инфинитивов на предложение
        negations_per_sent (float): Отрицательных частиц на предложение
        split_predicates_per_sent (float): Расщепленных сказуемых на предложение
        noun_verb_ratio (float): Отношение числа существительных к числу глагольных форм

    Методы:
        get_stats: Получение вычисленных синтаксических статистик текста
        print_stats: Отображение вычисленных синтаксических статистик текста с описанием на экран

    Исключения:
        SourceTypeError: Если источник данных не объект Doc
        SourceError: Если в источнике данных отсутствует разбор зависимостей или слова
    """

    join_hyphens = True
    stats_desc = SYNTAX_STATS_DESC
    stats_headers = ("Статистика", "Значение")
    messages = CORE_MESSAGES

    def __init__(self, source: Doc):
        super().__init__(source)
        words = [token for sent in self.sents for token in sent]
        genitive_chains = [length for sent in self.sents for length in calc_genitive_chains(sent)]
        self.n_genitive_chains = len(genitive_chains)
        converb_clauses = [
            subtree_len(token, join_hyphens=True) for token in words if is_converb_clause(token)
        ]
        self.n_converb_clauses = len(converb_clauses)
        self.genitive_chains_per_sent = self.n_genitive_chains / self.n_sents
        self.max_genitive_chain_len = max(genitive_chains, default=0)
        self.converb_clauses_per_sent = self.n_converb_clauses / self.n_sents
        self.mean_converb_clause_len = fmean(converb_clauses) if converb_clauses else nan

    def is_clause_head(self, token: Token) -> bool:
        """Вершина клаузы по правилам русского языка (is_clause_head)"""
        return is_clause_head(token)

    def is_participle_clause(self, token: Token) -> bool:
        """Вершина причастного оборота - полного причастия (is_participle_clause)"""
        return is_participle_clause(token)

    def is_negation(self, token: Token) -> bool:
        """Отрицательная частица (is_negation)"""
        return is_negation(token)

    def find_split_predicates(self, words: Sequence[Token]) -> list[tuple[Token, Token]]:
        """Расщепленные сказуемые (find_split_predicates)"""
        return find_split_predicates(words)


def is_participle(token: Token) -> bool:
    """
    Проверка, является ли токен полной формой причастия

    Описание:
        Краткие причастия (дом построен) - сказуемые, а не определения,
        и полными не считаются

    Аргументы:
        token (Token): Токен

    Вывод:
        bool: Результат проверки
    """
    if not has_feature(token, "VerbForm", "Part"):
        return False
    return not (
        has_feature(token, "Variant", "Short") or has_feature(token, "StyleVariant", "Short")
    )


def is_converb(token: Token) -> bool:
    """
    Проверка, является ли токен деепричастием

    Аргументы:
        token (Token): Токен

    Вывод:
        bool: Результат проверки
    """
    return has_feature(token, "VerbForm", "Conv")


def is_negation(token: Token) -> bool:
    """
    Проверка, является ли токен отрицательной частицей

    Описание:
        Частица с признаком Polarity=Neg или частицы не и ни;
        союз ни в конструкции ни... ни отрицанием не считается

    Аргументы:
        token (Token): Токен

    Вывод:
        bool: Результат проверки
    """
    if token.pos_ != "PART":
        return False
    return has_feature(token, "Polarity", "Neg") or strip_marks(token.lower_) in NEGATION_PARTICLES


def is_clause_head(token: Token) -> bool:
    """
    Проверка, является ли токен вершиной клаузы

    Описание:
        Клаузу возглавляет вершина предложения или слово со связью ccomp, advcl, acl,
        acl:relcl, csubj или csubj:pass, кроме полных причастий, деепричастий
        и инфинитивов при существительном (желание уйти): причастные
        и деепричастные обороты считаются отдельно
        Вставная конструкция (parataxis) и однородное сказуемое (conj от вершины
        клаузы) образуют свою клаузу, только если это глагол или у него есть
        собственное подлежащее: модели spaCy вешают parataxis и на вводные слова
        (например, конечно, во-первых), которые клаузами не являются

    Аргументы:
        token (Token): Токен

    Вывод:
        bool: Результат проверки
    """
    seen = set()
    # Вверх по цепочке однородных до слова, которое само не conj; петля разбора - не клауза
    while is_word(token) and token.i not in seen:
        if is_root(token):
            return True
        if is_participle(token) or is_converb(token):
            return False
        dep = base_dep(token)
        if dep != "conj":
            if dep not in CLAUSE_DEPS:
                return False
            if dep == "parataxis":
                return is_predicate(token, join_hyphens=True)
            return not (token.dep_ == "acl" and is_infinitive(token))
        if not is_predicate(token, join_hyphens=True):
            return False
        seen.add(token.i)
        token = token.head
    return False


def is_subordinate_clause_head(token: Token) -> bool:
    """
    Проверка, является ли токен вершиной придаточной клаузы

    Описание:
        is_subordinate_clause_head ядра с русским правилом клаузы is_clause_head:
        вершина клаузы со связью ccomp, advcl, acl, csubj и их подтипами, а также
        однородное сказуемое придаточной клаузы

    Аргументы:
        token (Token): Токен

    Вывод:
        bool: Результат проверки
    """
    return anyts.syntax_stats.is_subordinate_clause_head(token, is_clause_head)


def is_genitive_modifier(token: Token) -> bool:
    """
    Проверка, является ли токен беспредложным определением в родительном падеже

    Описание:
        Слово со связью nmod в родительном падеже без предлога (зависимого case):
        дом отца, но не дом у дороги

    Аргументы:
        token (Token): Токен

    Вывод:
        bool: Результат проверки
    """
    if base_dep(token) != "nmod" or not has_feature(token, "Case", "Gen"):
        return False
    return not any(child.dep_ == "case" for child in get_children(token, join_hyphens=True))


def calc_genitive_chains(tokens: Iterable[Token]) -> list[int]:
    """
    Вычисление длин цепочек родительных падежей

    Описание:
        Цепочка - два и более вложенных беспредложных определения в родительном
        падеже: повышение эффективности использования ресурсов (длина 3)
        Цепочка начинается с определения, вершина которого сама не является
        таким определением, длина - число слов в самой длинной ветви

    Аргументы:
        tokens (Doc|Span|list[Token]): Последовательность токенов

    Вывод:
        list[int]: Длины цепочек в порядке слов
    """
    return calc_modifier_chains(tokens, is_genitive_modifier, join_hyphens=True)


def is_participle_clause(token: Token) -> bool:
    """
    Проверка, является ли токен вершиной причастного оборота

    Описание:
        Полное причастие хотя бы с одним зависимым словом, не считая
        сочинительных и вставных связей (Иванов, Солнышкина, Соловьёв 2018)

    Аргументы:
        token (Token): Токен

    Вывод:
        bool: Результат проверки
    """
    return is_participle(token) and calc_valency(token, join_hyphens=True) > 0


def is_converb_clause(token: Token) -> bool:
    """
    Проверка, является ли токен вершиной деепричастного оборота

    Описание:
        Деепричастие хотя бы с одним зависимым словом, не считая
        сочинительных и вставных связей

    Аргументы:
        token (Token): Токен

    Вывод:
        bool: Результат проверки
    """
    return is_converb(token) and calc_valency(token, join_hyphens=True) > 0


def get_lemma(token: Token) -> str:
    """
    Получение леммы токена в нижнем регистре

    Описание:
        Разбор pymorphy3 с частью речи токена (lemmatize), а не token.lemma_:
        лемматизатор моделей ru_core_news возвращает словоформу для AUX
        и при расхождении признаков теггера и pymorphy3 (были, них, стихли)

    Аргументы:
        token (Token): Токен

    Вывод:
        str: Лемма
    """
    return lemmatize(token.text, token.pos_)


def is_light_verb(token: Token) -> bool:
    """
    Проверка, является ли токен легким глаголом

    Описание:
        Глагол с леммой из LIGHT_VERBS (осуществлять, производить, проводить,
        обеспечивать, оказывать, принимать, иметь), который в расщепленном сказуемом
        несет только грамматическое значение; возвратный пассив (проводиться,
        приниматься, вестись) входит в список отдельными леммами, так как у части
        возвратных форм другое значение (получиться, оказаться). Кроме леммы spaCy
        проверяется лемма pymorphy3: лемматизатор модели оставляет часть форм
        без изменений (ведётся)

    Аргументы:
        token (Token): Токен

    Вывод:
        bool: Результат проверки
    """
    return token.pos_ == "VERB" and not _verb_lemmas(token).isdisjoint(LIGHT_VERBS)


def _verb_lemmas(token: Token) -> set[str]:
    """Леммы глагола по spaCy и pymorphy3"""
    return {normalize_yo(get_lemma(token)), normalize_yo(lemmatize(token.text, "VERB"))}


def is_reflexive(token: Token) -> bool:
    """
    Проверка, является ли токен возвратным или пассивным глаголом

    Описание:
        Лемма на -ся или -сь либо залог Voice=Mid или Voice=Pass: у возвратного
        пассива (проверка проводится) именная часть расщепленного сказуемого -
        подлежащее nsubj

    Аргументы:
        token (Token): Токен

    Вывод:
        bool: Результат проверки
    """
    if token.pos_ != "VERB":
        return False
    return (
        get_lemma(token).endswith(("ся", "сь"))
        or has_feature(token, "Voice", "Mid")
        or has_feature(token, "Voice", "Pass")
    )


def is_split_predicate_noun(token: Token, verb: Token | None = None) -> bool:
    """
    Проверка, может ли токен быть именной частью расщепленного сказуемого

    Описание:
        Существительное с отглагольной леммой (is_verbal_noun: проверка, участие,
        реализация) - при любом легком глаголе - или с леммой из SPLIT_PREDICATE_NOUNS
        (роль, работа, помощь, мера) - только при глаголе своего оборота: оказать
        помощь, принять меры, но не получить работу

    Аргументы:
        token (Token): Токен
        verb (Token): Легкий глагол; если не задан, оборот не проверяется

    Вывод:
        bool: Результат проверки
    """
    if token.pos_ != "NOUN":
        return False
    lemma = normalize_yo(get_lemma(token))
    if is_verbal_noun(lemma):
        return True
    if lemma not in SPLIT_PREDICATE_NOUNS:
        return False
    if verb is None:
        return True
    verb_lemmas = _verb_lemmas(verb)
    verb_lemmas |= {verb_lemma.removesuffix("ся").removesuffix("сь") for verb_lemma in verb_lemmas}
    return not verb_lemmas.isdisjoint(SPLIT_PREDICATE_NOUNS[lemma])


def find_split_predicates(tokens: Iterable[Token]) -> list[tuple[Token, Token]]:
    """
    Поиск расщепленных сказуемых

    Описание:
        Легкий глагол (is_light_verb) с зависимой именной частью
        (is_split_predicate_noun): осуществлять проверку, оказать помощь, принять
        участие, проводится проверка, принято решение
        У глагола берется не больше одной именной части, в порядке предпочтения
        obj, nsubj:pass, nsubj (только у возвратного или пассивного глагола:
        проверка проводится), iobj, nmod, obl; предложные обстоятельства (obl
        с зависимым case) и агенс пассива (obl:agent, творительный obl при пассивном
        или возвратном глаголе) не учитываются

    Аргументы:
        tokens (Doc|Span|list[Token]): Последовательность токенов

    Вывод:
        list[tuple[Token, Token]]: Пары глагол - существительное в порядке слов
    """
    pairs = []
    for token in get_words(tokens, join_hyphens=True):
        if not is_light_verb(token):
            continue
        candidates = [
            child
            for child in get_children(token, join_hyphens=True)
            if is_split_predicate_noun(child, token) and _is_nominal_part(child, token)
        ]
        if candidates:
            pairs.append((token, min(candidates, key=_nominal_part_rank)))
    return pairs


def _nominal_part_dep(child: Token) -> str:
    return child.dep_ if child.dep_ == "nsubj:pass" else base_dep(child)


def _is_nominal_part(child: Token, verb: Token) -> bool:
    dep = _nominal_part_dep(child)
    if dep not in SPLIT_PREDICATE_DEPS:
        return False
    if dep == "nsubj":
        return is_reflexive(verb)
    if dep != "obl":
        return True
    if child.dep_ == "obl:agent" or any(
        grandchild.dep_ == "case" for grandchild in get_children(child, join_hyphens=True)
    ):
        return False
    return not (is_reflexive(verb) and has_feature(child, "Case", "Ins"))


def _nominal_part_rank(child: Token) -> int:
    return SPLIT_PREDICATE_DEPS.index(_nominal_part_dep(child))
