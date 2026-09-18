# Syntactic statistics

!!! info ""
    **ruts.syntax_stats.SyntaxStats**

## Description

A module for computing syntactic statistics of a text over the dependency tree: dependency distances, tree depth and shape, coordination chains, clauses, noun phrase modifiers, genitive chains, participial and adverbial participle clauses, passive voice, infinitives, negations, split predicates and the noun-to-verb ratio. Syntactic officialese markers: passive voice, participial clauses, genitive chains, split predicates, noun-to-verb ratio. The feature definitions follow Ivanov, Solnyshkina and Solovyev (2018), where they were tested on a corpus of school textbooks: the numbers of coordination chains, participial clauses and noun phrase modifiers correlate with the textbook grade at 0.88-0.93.

The statistics are computed over [Universal Dependencies](https://universaldependencies.org/u/dep/) annotation, so the data source can only be a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library with a dependency parse - from the `ru_core_news_sm`, `ru_core_news_md` or `ru_core_news_lg` models. Punctuation and whitespace tokens are ignored: words are the tree nodes, dependency distances are measured in word positions.

Sentence-level indicators (maximum dependency distance, tree depth, numbers of leaves and subtrees, nodes per leaf) are averaged over sentences; constructions (clauses, chains, participial clauses, infinitives, negations) are normalized by the number of sentences; passive voice and modifiers - by the numbers of verb forms and nouns. Values undefined for a text (the mean clause length without clauses, the passive share without verbs) are `nan`.

!!! note "Note"
    The quality of the statistics is bounded by the quality of the parse: the small `ru_core_news_sm` model errs in parts of speech and relations noticeably more often than `ru_core_news_lg`.

!!! note "Note"
    The statistics are computed when the `SyntaxStats` object is initialized.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | Doc | `-` | Data source (a Doc object with a dependency parse) |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `n_sents` | int | Number of sentences containing words |
| `n_words` | int | Number of words |
| `n_leaves` | int | Number of leaves - words without dependents |
| `n_subtrees` | int | Number of subtrees - words with dependents |
| `n_coordination_chains` | int | Number of coordination chains |
| `n_clauses` | int | Number of clauses |
| `n_subordinate_clauses` | int | Number of subordinate clauses |
| `n_complex_sents` | int | Number of sentences with subordinate clauses |
| `n_nouns` | int | Number of nouns |
| `n_genitive_chains` | int | Number of genitive chains |
| `n_participle_clauses` | int | Number of participial clauses |
| `n_converb_clauses` | int | Number of adverbial participle clauses |
| `n_verbs` | int | Number of verb forms |
| `n_passive` | int | Number of passive verb forms |
| `n_agentless_passive` | int | Number of passive forms without an agent |
| `n_infinitives` | int | Number of infinitives |
| `n_negations` | int | Number of negative particles |
| `n_split_predicates` | int | Number of split predicates |
| `split_predicates` | tuple[str] | Tuple of split predicates (verb and noun) |
| `c_children` | dict[int, int] | Distribution of words by number of dependents |
| `c_deps` | dict[str, int] | Distribution of words by syntactic relation |
| `mean_dependency_distance` | float | Mean dependency distance |
| `std_dependency_distance` | float | Standard deviation of dependency distance |
| `max_dependency_distance` | float | Maximum dependency distance in a sentence (over sentences with dependencies) |
| `p_adjacent_dependencies` | float | Share of adjacent relations - dependencies of distance 1 |
| `tree_depth` | float | Dependency tree depth |
| `leaves_per_sent` | float | Leaves per sentence |
| `subtrees_per_sent` | float | Subtrees per sentence |
| `nodes_per_leaf` | float | Ratio of words to leaves |
| `verb_valency` | float | Mean number of dependents of a finite verb |
| `coordination_chains_per_sent` | float | Coordination chains per sentence |
| `mean_coordination_chain_len` | float | Mean coordination chain length |
| `clauses_per_sent` | float | Clauses per sentence |
| `mean_clause_len` | float | Mean clause length in words |
| `subordinate_clauses_per_sent` | float | Subordinate clauses per sentence |
| `p_complex_sents` | float | Share of sentences with at least one subordinate clause |
| `modifiers_per_noun` | float | Mean number of modifiers per noun |
| `genitive_chains_per_sent` | float | Genitive chains per sentence |
| `max_genitive_chain_len` | int | Maximum genitive chain length |
| `participle_clauses_per_sent` | float | Participial clauses per sentence |
| `mean_participle_clause_len` | float | Mean participial clause length in words |
| `converb_clauses_per_sent` | float | Adverbial participle clauses per sentence |
| `mean_converb_clause_len` | float | Mean adverbial participle clause length in words |
| `p_passive` | float | Share of passive forms among verb forms |
| `p_agentless_passive` | float | Share of agentless forms among passive ones |
| `infinitives_per_sent` | float | Infinitives per sentence |
| `negations_per_sent` | float | Negative particles per sentence |
| `split_predicates_per_sent` | float | Split predicates per sentence |
| `noun_verb_ratio` | float | Ratio of nouns to verb forms |

!!! note "Note"
    Every statistic can be computed separately by calling the corresponding function. Detailed information on the syntactic statistics and the functions used to compute them is available in the corresponding [section](syntax_stats_funcs.md).

## Methods

### get_stats

Returns a dictionary with the computed syntactic statistics.

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import spacy
    from ruts import SyntaxStats

    # Prepare the data
    nlp = spacy.load("ru_core_news_sm")
    text = "Дом, построенный рабочими в прошлом году, был продан. Он сказал, что не придёт, и ушёл, хлопнув дверью."

    # Compute the statistics
    ss = SyntaxStats(nlp(text))
    ss.get_stats()
    ```

    _Result_:

    ``` bash
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
    ```

Counters and distributions are available as attributes:

!!! example "Example"

    ``` python
    ss.n_clauses, ss.n_nouns, ss.n_verbs
    # (3, 5, 5)
    ss.c_children
    # {0: 9, 1: 2, 2: 5, 3: 1}
    ss.c_deps
    # {'ROOT': 2, 'acl': 1, 'advcl': 1, 'advmod': 1, 'amod': 1, 'aux:pass': 1, 'case': 1, 'cc': 1, 'ccomp': 1, 'conj': 1, 'iobj': 1, 'mark': 1, 'nsubj': 1, 'nsubj:pass': 1, 'obl': 1, 'obl:agent': 1}
    ```

### print_stats

Prints a table with the computed syntactic statistics.

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed statistics
    ss.print_stats()
    ```

    _Result_:

    ``` bash
                        Статистика                    | Значение
    ------------------------------------------------------------
    Средняя длина зависимости                         |   1.93
    Стандартное отклонение длины зависимости          |   1.61
    Максимальная длина зависимости                    |   5.00
    Доля смежных связей                               |   0.60
    Глубина дерева зависимостей                       |   4.00
    Листьев на предложение                            |   4.50
    Поддеревьев на предложение                        |   4.00
    Узлов на лист                                     |   1.90
    Валентность финитных глаголов                     |   2.00
    Сочинительных цепочек на предложение              |   0.50
    Средняя длина сочинительной цепочки               |   2.00
    Клауз на предложение                              |   1.50
    Средняя длина клаузы (слов)                       |   5.67
    Придаточных клауз на предложение                  |   0.50
    Доля предложений с придаточными                   |   0.50
    Модификаторов на именную группу                   |   0.40
    Цепочек родительных падежей на предложение        |   0.00
    Максимальная длина цепочки родительных падежей    |   0.00
    Причастных оборотов на предложение                |   0.50
    Средняя длина причастного оборота (слов)          |   5.00
    Деепричастных оборотов на предложение             |   0.50
    Средняя длина деепричастного оборота (слов)       |   2.00
    Доля пассивных форм среди глаголов                |   0.40
    Доля безагентного пассива                         |   0.50
    Инфинитивов на предложение                        |   0.00
    Отрицаний на предложение                          |   0.50
    Расщеплённых сказуемых на предложение             |   0.00
    Отношение существительных к глаголам              |   1.00
    ```
