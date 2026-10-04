from collections import Counter
from collections.abc import Iterable
from math import nan
from statistics import fmean, pstdev

from anyts.syntax import (
    base_dep as base_dep,
    calc_coordination_chains as calc_coordination_chains,
    calc_dependency_distances as calc_dependency_distances,
    calc_tree_depth as calc_tree_depth,
    calc_valency as calc_valency,
    count_children as count_children,
    get_children as get_children,
    get_words as get_words,
    has_feature as has_feature,
    is_root as is_root,
    is_word as is_word,
    subtree_len as subtree_len,
)
from anyts.utils import safe_divide
from spacy.tokens import Doc, Token

from .constants import (
    CLAUSE_DEPS,
    LIGHT_VERBS,
    NEGATION_PARTICLES,
    NOUN_MODIFIER_DEPS,
    PASSIVE_DEPS,
    SPLIT_PREDICATE_NOUNS,
    SUBJECT_DEPS,
    SUBORDINATE_CLAUSE_DEPS,
    SYNTAX_STATS_DESC,
)
from .exceptions import SourceError, SourceTypeError
from .utils import is_verbal_noun, lemmatize, normalize_yo

SPLIT_PREDICATE_DEPS = ("obj", "nsubj:pass", "nsubj", "iobj", "nmod", "obl")


class SyntaxStats:
    """
    Класс для вычисления синтаксических статистик текста

    Описание:
        Статистики считаются по дереву зависимостей Universal Dependencies, поэтому
        источником данных может быть только объект Doc библиотеки spaCy с разбором
        зависимостей (модели ru_core_news_sm, ru_core_news_md, ru_core_news_lg)
        Знаки препинания и пробельные токены не учитываются: узлы дерева - слова,
        длины зависимостей считаются по позициям слов
        Показатели предложения (максимальная длина зависимости, глубина дерева,
        число листьев и поддеревьев, узлов на лист) усредняются по предложениям,
        конструкции нормируются на число предложений, пассив и модификаторы - на число
        глаголов и существительных
        Определения признаков следуют работе Иванова, Солнышкиной и Соловьёва (2018)
        Синтаксические маркеры канцелярита: пассив, причастные и деепричастные обороты,
        цепочки родительных падежей, расщепленные сказуемые, отношение существительных
        к глаголам

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
        SourceTypeError: Если передаваемое значение не является объектом Doc
        SourceError: Если в источнике данных отсутствует разбор зависимостей
        SourceError: Если в источнике данных отсутствуют слова
    """

    def __init__(self, source: Doc):
        if not isinstance(source, Doc):
            raise SourceTypeError("Некорректный источник данных")
        if not source.has_annotation("DEP"):
            raise SourceError("В источнике данных отсутствует разбор зависимостей")
        spans, sents = [], []
        for span in source.sents:
            if sent_words := get_words(span, join_hyphens=True):
                spans.append(span)
                sents.append(sent_words)
        if not sents:
            raise SourceError("В источнике данных отсутствуют слова")
        words = [token for sent in sents for token in sent]
        self.n_sents = len(sents)
        self.n_words = len(words)

        # Предложение целиком: зависимое может висеть на второй части дефисного слова
        distances = [calc_dependency_distances(span, join_hyphens=True) for span in spans]
        all_distances = [distance for sent in distances for distance in sent]
        depths = [calc_tree_depth(span, join_hyphens=True) for span in spans]
        children = [[count_children(token, join_hyphens=True) for token in sent] for sent in sents]
        leaves = [sum(1 for count in sent if not count) for sent in children]
        self.c_children = dict(
            sorted(Counter(count for sent in children for count in sent).items())
        )
        self.c_deps = dict(sorted(Counter(token.dep_ for token in words).items()))
        self.n_leaves = sum(leaves)
        self.n_subtrees = self.n_words - self.n_leaves
        finite_verbs = [token for token in words if is_finite_verb(token)]
        chains = [
            length
            for span in spans
            for length in calc_coordination_chains(span, join_hyphens=True)
        ]
        self.n_coordination_chains = len(chains)
        self.n_clauses = sum(1 for token in words if is_clause_head(token))
        subordinate = [
            sum(1 for token in sent if is_subordinate_clause_head(token)) for sent in sents
        ]
        self.n_subordinate_clauses = sum(subordinate)
        self.n_complex_sents = sum(1 for count in subordinate if count)
        nouns = [token for token in words if token.pos_ in ("NOUN", "PROPN")]
        self.n_nouns = len(nouns)
        genitive_chains = [length for sent in sents for length in calc_genitive_chains(sent)]
        self.n_genitive_chains = len(genitive_chains)
        participle_clauses = [
            subtree_len(token, join_hyphens=True) for token in words if is_participle_clause(token)
        ]
        self.n_participle_clauses = len(participle_clauses)
        converb_clauses = [
            subtree_len(token, join_hyphens=True) for token in words if is_converb_clause(token)
        ]
        self.n_converb_clauses = len(converb_clauses)
        self.n_verbs = sum(1 for token in words if token.pos_ == "VERB")
        passive = [token for token in words if is_passive(token)]
        self.n_passive = len(passive)
        self.n_agentless_passive = sum(1 for token in passive if is_agentless(token))
        self.n_infinitives = sum(1 for token in words if is_infinitive(token))
        self.n_negations = sum(1 for token in words if is_negation(token))
        split_predicates = find_split_predicates(words)
        self.n_split_predicates = len(split_predicates)
        self.split_predicates = tuple(
            f"{verb.text} {noun.text}" for verb, noun in split_predicates
        )

        self.mean_dependency_distance = fmean(all_distances) if all_distances else nan
        self.std_dependency_distance = pstdev(all_distances) if all_distances else nan
        sent_maxima = [max(sent) for sent in distances if sent]
        self.max_dependency_distance = fmean(sent_maxima) if sent_maxima else nan
        self.p_adjacent_dependencies = safe_divide(
            sum(1 for distance in all_distances if distance == 1), len(all_distances), nan
        )
        self.tree_depth = fmean(depths)
        self.leaves_per_sent = self.n_leaves / self.n_sents
        self.subtrees_per_sent = self.n_subtrees / self.n_sents
        self.nodes_per_leaf = fmean(
            len(sent) / n_leaves for sent, n_leaves in zip(sents, leaves, strict=True)
        )
        self.verb_valency = safe_divide(
            sum(calc_valency(token, join_hyphens=True) for token in finite_verbs),
            len(finite_verbs),
            nan,
        )
        self.coordination_chains_per_sent = self.n_coordination_chains / self.n_sents
        self.mean_coordination_chain_len = fmean(chains) if chains else nan
        self.clauses_per_sent = self.n_clauses / self.n_sents
        self.mean_clause_len = safe_divide(self.n_words, self.n_clauses, nan)
        self.subordinate_clauses_per_sent = self.n_subordinate_clauses / self.n_sents
        self.p_complex_sents = self.n_complex_sents / self.n_sents
        self.modifiers_per_noun = safe_divide(
            sum(count_noun_modifiers(token) for token in nouns), self.n_nouns, nan
        )
        self.genitive_chains_per_sent = self.n_genitive_chains / self.n_sents
        self.max_genitive_chain_len = max(genitive_chains, default=0)
        self.participle_clauses_per_sent = self.n_participle_clauses / self.n_sents
        self.mean_participle_clause_len = fmean(participle_clauses) if participle_clauses else nan
        self.converb_clauses_per_sent = self.n_converb_clauses / self.n_sents
        self.mean_converb_clause_len = fmean(converb_clauses) if converb_clauses else nan
        self.p_passive = safe_divide(self.n_passive, self.n_verbs, nan)
        self.p_agentless_passive = safe_divide(self.n_agentless_passive, self.n_passive, nan)
        self.infinitives_per_sent = self.n_infinitives / self.n_sents
        self.negations_per_sent = self.n_negations / self.n_sents
        self.split_predicates_per_sent = self.n_split_predicates / self.n_sents
        self.noun_verb_ratio = safe_divide(self.n_nouns, self.n_verbs, nan)

    def get_stats(self) -> dict[str, float]:
        """
        Получение вычисленных синтаксических статистик текста

        Вывод:
            dict[str, float]: Справочник вычисленных синтаксических статистик текста
        """
        return {stat: getattr(self, stat) for stat in SYNTAX_STATS_DESC}

    def print_stats(self):
        """Отображение вычисленных синтаксических статистик текста с описанием на экран"""
        print(f"{'Статистика':^50}|{'Значение':^10}")
        print("-" * 60)
        stats = self.get_stats()
        for stat, value in SYNTAX_STATS_DESC.items():
            print(f"{value:50}|{stats[stat]:^10.2f}")


def is_finite_verb(token: Token) -> bool:
    """
    Проверка, является ли токен финитной формой глагола

    Аргументы:
        token (Token): Токен

    Вывод:
        bool: Результат проверки
    """
    return token.pos_ == "VERB" and has_feature(token, "VerbForm", "Fin")


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


def is_infinitive(token: Token) -> bool:
    """
    Проверка, является ли токен инфинитивом

    Аргументы:
        token (Token): Токен

    Вывод:
        bool: Результат проверки
    """
    return has_feature(token, "VerbForm", "Inf")


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
    return has_feature(token, "Polarity", "Neg") or token.lower_ in NEGATION_PARTICLES


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
    if not is_word(token):
        return False
    if is_root(token):
        return True
    if is_participle(token) or is_converb(token):
        return False
    if token.dep_ not in CLAUSE_DEPS:
        return token.dep_ == "conj" and is_clause_head(token.head) and is_predicate(token)
    if token.dep_ == "parataxis":
        return is_predicate(token)
    return not (token.dep_ == "acl" and is_infinitive(token))


def is_predicate(token: Token) -> bool:
    """
    Проверка, может ли токен быть сказуемым своей клаузы

    Описание:
        Глагол (VERB, AUX) или слово с собственным подлежащим (nsubj, csubj):
        именное сказуемое «он умён» проходит, вводное слово «конечно» - нет

    Аргументы:
        token (Token): Токен

    Вывод:
        bool: Результат проверки
    """
    return token.pos_ in ("VERB", "AUX") or any(
        base_dep(child) in SUBJECT_DEPS for child in get_children(token, join_hyphens=True)
    )


def is_subordinate_clause_head(token: Token) -> bool:
    """
    Проверка, является ли токен вершиной придаточной клаузы

    Описание:
        Вершина клаузы со связью ccomp, advcl, acl, acl:relcl, csubj или csubj:pass,
        а также однородное сказуемое придаточной клаузы

    Аргументы:
        token (Token): Токен

    Вывод:
        bool: Результат проверки
    """
    if not is_clause_head(token) or is_root(token):
        return False
    if token.dep_ in SUBORDINATE_CLAUSE_DEPS:
        return True
    return token.dep_ == "conj" and is_subordinate_clause_head(token.head)


def count_noun_modifiers(token: Token) -> int:
    """
    Вычисление количества модификаторов именной группы

    Описание:
        Зависимые слова со связями amod, det, nmod, nummod, acl и их подтипами
        (acl:relcl, nummod:gov); сочинительные и пояснительные связи (conj, appos)
        не учитываются, как в признаке NOUNS_DEP Иванова, Солнышкиной и Соловьёва (2018)

    Аргументы:
        token (Token): Токен

    Вывод:
        int: Количество модификаторов
    """
    return sum(
        1
        for child in get_children(token, join_hyphens=True)
        if base_dep(child) in NOUN_MODIFIER_DEPS
    )


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


def _genitive_chain_len(token: Token) -> int:
    return 1 + max(
        (
            _genitive_chain_len(child)
            for child in get_children(token, join_hyphens=True)
            if is_genitive_modifier(child)
        ),
        default=0,
    )


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
    chains = []
    for token in get_words(tokens, join_hyphens=True):
        if is_genitive_modifier(token) and not is_genitive_modifier(token.head):
            length = _genitive_chain_len(token)
            if length >= 2:
                chains.append(length)
    return chains


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


def is_passive(token: Token) -> bool:
    """
    Проверка, является ли токен пассивной глагольной формой

    Описание:
        Глагол с признаком Voice=Pass (страдательные причастия, возвратный пассив)
        или с зависимым nsubj:pass, csubj:pass или aux:pass

    Аргументы:
        token (Token): Токен

    Вывод:
        bool: Результат проверки
    """
    if token.pos_ != "VERB":
        return False
    return has_feature(token, "Voice", "Pass") or any(
        child.dep_ in PASSIVE_DEPS for child in get_children(token, join_hyphens=True)
    )


def is_agentless(token: Token) -> bool:
    """
    Проверка, является ли токен пассивной формой без агенса

    Описание:
        Пассивная форма без зависимого obl:agent: дом построен, но не дом построен рабочими

    Аргументы:
        token (Token): Токен

    Вывод:
        bool: Результат проверки
    """
    return is_passive(token) and not any(
        child.dep_ == "obl:agent" for child in get_children(token, join_hyphens=True)
    )


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
