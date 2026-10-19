# Syntactic statistics

!!! info ""
    **ruts.syntax_stats.SyntaxStats**

## Description

--8<-- "stats/syntax_stats.md:SyntaxStats"

The relations and features are those of the [Universal Dependencies](https://universaldependencies.org/u/dep/) annotation of the `ru_core_news_sm`, `ru_core_news_md` and `ru_core_news_lg` models. The syntactic markers of officialese are the passive, participial clauses, genitive chains, split predicates and the ratio of nouns to verbs. [Ivanov, Solnyshkina and Solovyev](https://dialogue-conf.org/media/4302/ivanovvv.pdf) tested the features on a corpus of school textbooks: the numbers of coordination chains, participial clauses and noun phrase modifiers correlate with the textbook grade at 0.88-0.93.

!!! note "Note"
    The quality of the statistics is bounded by the quality of the parse: the small `ru_core_news_sm` model errs in parts of speech and relations noticeably more often than `ru_core_news_lg`.

!!! note "Note"
    The statistics are computed when the `SyntaxStats` object is initialized.

## Language hooks

The class extends the `SyntaxStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/syntax_stats/) core with the Russian layer: the parts of a hyphenated word that spaCy splits are joined (`во-первых` is one word), and the clauses, participial clauses, negations and split predicates follow the rules of Russian. A short participle (`дом построен`) is a predicate and heads a clause ([`is_clause_head`](syntax_stats_funcs.md#is_clause_head)), full participles and adverbial participles head participial and adverbial participle clauses, counted apart, an infinitive under a noun (`желание уйти`) heads none, and an infinitive under a verb heads a subordinate clause (`хочет уйти`), except with the modal and phasal verbs (`может уйти`, `начал читать`); a participial clause is a full participle with a dependent ([`is_participle_clause`](syntax_stats_funcs.md#is_participle_clause)); negations are the particles with `Polarity=Neg` and the particles «не», «ни» ([`is_negation`](syntax_stats_funcs.md#is_negation)); a split predicate is a light verb with a noun that carries its meaning, such as `осуществлять проверку` ([`find_split_predicates`](syntax_stats_funcs.md#find_split_predicates)). ruTS adds the statistics of genitive chains ([`calc_genitive_chains`](syntax_stats_funcs.md#calc_genitive_chains), built on the `calc_modifier_chains` of the core) and of adverbial participle clauses. The `print_stats` table has Russian headers and the descriptions of `ruts.constants.SYNTAX_STATS_DESC`, the error messages are in Russian (`CORE_MESSAGES`).

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | Doc | `-` | Data source (a Doc object with a dependency parse) |

## Attributes

--8<-- "stats/syntax_stats.md:SyntaxStats-attributes"

The statistics of the constructions of ruTS:

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `n_genitive_chains`, `n_converb_clauses` | int | Numbers of genitive chains and of adverbial participle clauses |
| `genitive_chains_per_sent` | float | Genitive chains per sentence |
| `max_genitive_chain_len` | int | Maximum genitive chain length, 0 without chains |
| `converb_clauses_per_sent`, `mean_converb_clause_len` | float | Adverbial participle clauses per sentence and their mean length in words |

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
    'infinitive_clauses_per_sent': 0.0,
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

Counters, distributions and the words of the sentences are available as attributes:

!!! example "Example"

    ``` python
    ss.n_clauses, ss.n_nouns, ss.n_verbs
    # (3, 5, 5)
    ss.c_children
    # {0: 9, 1: 2, 2: 5, 3: 1}
    ss.c_deps
    # {'ROOT': 2, 'acl': 1, 'advcl': 1, 'advmod': 1, 'amod': 1, 'aux:pass': 1, 'case': 1, 'cc': 1, 'ccomp': 1, 'conj': 1, 'iobj': 1, 'mark': 1, 'nsubj': 1, 'nsubj:pass': 1, 'obl': 1, 'obl:agent': 1}
    ss.sents[0]
    # (Дом, построенный, рабочими, в, прошлом, году, был, продан)
    ```

### print_stats

--8<-- "stats/stats.md:Stats-print_stats"

To illustrate the method, we reuse the code from the `get_stats` example:

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
    Средняя длина зависимости                        |   1.93
    Стандартное отклонение длины зависимости         |   1.61
    Средний максимум длины зависимости в предложении |   5.00
    Доля смежных связей                              |   0.60
    Средняя глубина дерева зависимостей предложения  |   4.00
    Листьев на предложение                           |   4.50
    Поддеревьев на предложение                       |   4.00
    Среднее число узлов на лист в предложении        |   1.90
    Валентность финитных глаголов                    |   2.00
    Сочинительных цепочек на предложение             |   0.50
    Средняя длина сочинительной цепочки              |   2.00
    Клауз на предложение                             |   1.50
    Средняя длина клаузы (слов)                      |   5.67
    Придаточных клауз на предложение                 |   0.50
    Доля предложений с придаточными                  |   0.50
    Инфинитивных клауз при глаголе на предложение    |   0.00
    Модификаторов на именную группу                  |   0.40
    Цепочек родительных падежей на предложение       |   0.00
    Максимальная длина цепочки родительных падежей   |    0
    Причастных оборотов на предложение               |   0.50
    Средняя длина причастного оборота (слов)         |   5.00
    Деепричастных оборотов на предложение            |   0.50
    Средняя длина деепричастного оборота (слов)      |   2.00
    Доля пассивных форм среди глаголов               |   0.40
    Доля безагентного пассива                        |   0.50
    Инфинитивов на предложение                       |   0.00
    Отрицаний на предложение                         |   0.50
    Расщеплённых сказуемых на предложение            |   0.00
    Отношение существительных к глаголам             |   1.00
    ```

### to_dataframe, describe

The `to_dataframe` method (the statistics as a one-row `pandas.DataFrame`) and the `describe` method are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the syntactic statistics have no scales, so `describe` always gives `None`.
