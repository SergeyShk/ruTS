# Syntactic statistics

``` {.python .signature}
SyntaxStats(source)
```

--8<-- "stats/syntax_stats.md:SyntaxStats"

The class extends the `SyntaxStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/syntax_stats/) core with the Russian layer. The relations and features are those of the [Universal Dependencies](https://universaldependencies.org/u/dep/) annotation of the `ru_core_news_sm`, `ru_core_news_md` and `ru_core_news_lg` models; the quality of the statistics is bounded by the quality of the parse: the small `ru_core_news_sm` model errs in parts of speech and relations noticeably more often than `ru_core_news_lg`. The parts of a hyphenated word that spaCy splits are joined (`во-первых` is one word), and the clauses, participial clauses, negations and split predicates follow the rules of Russian given in the cards of the metrics. ruTS adds its own metrics of genitive chains and adverbial participle clauses. The syntactic markers of officialese are the passive, participial clauses, genitive chains, split predicates and the ratio of nouns to verbs. The `print_stats` table and the error messages are in Russian (`SYNTAX_STATS_DESC` and `CORE_MESSAGES` of `ruts.constants`).

Ivanov, Solnyshkina and Solovyev tested the features on a corpus of school textbooks: the numbers of coordination chains, participial clauses and noun phrase modifiers correlate with the textbook grade at 0.88-0.93. The cards of the metrics name the original features of the paper and their correlation coefficients with the textbook grade.

=== "Code"

    ``` python
    import spacy
    from ruts import SyntaxStats

    nlp = spacy.load("ru_core_news_sm")
    text = "Дом, построенный рабочими в прошлом году, был продан. Хлопнув дверью, он ушел и сказал, что не придет."
    ss = SyntaxStats(nlp(text))
    ss.print_stats()
    ```

=== "Result"

    ```
                           Статистика                        | Значение
    --------------------------------------------------------------------
    Средняя длина зависимости                                |   2.07
    Стандартное отклонение длины зависимости                 |   1.61
    Средний максимум длины зависимости в предложении         |   5.00
    Доля смежных связей                                      |   0.53
    Средняя глубина дерева зависимостей предложения          |   3.50
    Листьев на предложение                                   |   4.50
    Поддеревьев на предложение                               |   4.00
    Среднее число узлов на лист в предложении                |   1.90
    Среднее число слов до вершины предложения                |   5.00
    Валентность финитных глаголов                            |   1.67
    Сочинительных цепочек на предложение                     |   0.50
    Средняя длина сочинительной цепочки                      |   2.00
    Клауз на предложение                                     |   2.00
    Средняя длина клаузы (слов)                              |   4.25
    Придаточных клауз на предложение                         |   0.50
    Доля предложений с придаточными                          |   0.50
    Инфинитивных клауз на предложение                        |   0.00
    T-единиц на предложение                                  |   1.00
    Средняя длина T-единицы (слов)                           |   8.50
    Клауз на T-единицу                                       |   1.50
    Доля T-единиц с придаточными                             |   0.50
    Глагольных групп на T-единицу                            |   2.50
    Сочинённых групп на клаузу                               |   0.33
    Сложных именных групп на клаузу                          |   1.00
    Модификаторов на именную группу                          |   0.50
    Предложных цепочек на предложение                        |   0.00
    Максимальная длина предложной цепочки                    |    0
    Цепочек родительных падежей на предложение               |   0.00
    Максимальная длина цепочки родительных падежей           |    0
    Причастных оборотов на предложение                       |   0.50
    Средняя длина причастного оборота (слов)                 |   5.00
    Деепричастных оборотов на предложение                    |   0.50
    Средняя длина деепричастного оборота (слов)              |   2.00
    Доля пассивных форм среди глаголов                       |   0.33
    Доля безагентного пассива                                |   0.50
    Инфинитивов на предложение                               |   0.00
    Отрицаний на предложение                                 |   0.50
    Расщеплённых сказуемых на предложение                    |   0.00
    Доля именных подлежащих перед вершиной                   |   1.00
    Доля именных дополнений перед вершиной                   |   0.00
    Редакционное расстояние частей речи соседних предложений |   0.78
    Синтаксическая схожесть соседних предложений             |   0.06
    Отношение существительных к глаголам                     |   0.67
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `Doc` | - | Data source: a `Doc` with a dependency parse |

## Attributes

--8<-- "stats/syntax_stats.md:SyntaxStats-attributes"

The attributes of the constructions of ruTS are `n_genitive_chains` and `n_converb_clauses` (`int`): the numbers of genitive chains and of adverbial participle clauses.

=== "Code"

    ``` python
    ss.n_clauses, ss.n_nouns, ss.n_verbs
    ss.c_children
    ss.c_deps
    ss.sents[0]
    ```

=== "Result"

    ```
    (4, 4, 6)
    {0: 9, 1: 2, 2: 5, 3: 1}
    {'ROOT': 2,
     'acl': 1,
     'advcl': 1,
     'advmod': 1,
     'amod': 1,
     'aux:pass': 1,
     'case': 1,
     'cc': 1,
     'ccomp': 1,
     'conj': 1,
     'mark': 1,
     'nsubj': 1,
     'nsubj:pass': 1,
     'obj': 1,
     'obl': 1,
     'obl:agent': 1}
    (Дом, построенный, рабочими, в, прошлом, году, был, продан)
    ```

## Metrics

--8<-- "stats/syntax_stats.md:SyntaxStats-metrics"

The metrics of the constructions of ruTS:

| Metric | Measures | Range | Higher means |
| :----- | :------- | :---- | :----------- |
| [`genitive_chains_per_sent`](#genitive_chains) | Genitive chains per sentence | 0 and above | More chains |
| [`max_genitive_chain_len`](#genitive_chains) | Longest genitive chain of the text | 0 without chains, otherwise 2 and above | A longer chain |
| [`converb_clauses_per_sent`](#converb_clauses) | Adverbial participle clauses per sentence | 0 and above | More adverbial participle clauses |
| [`mean_converb_clause_len`](#converb_clauses) | Mean length of an adverbial participle clause in words | 2 and above, `nan` without adverbial participle clauses | Longer adverbial participle clauses |

<div class="metric-card" markdown>

### Dependency distance { #dependency_distances }

`mean_dependency_distance` · `std_dependency_distance` · `max_dependency_distance` · `p_adjacent_dependencies`
{ .metric-meta }

--8<-- "stats/syntax_stats.md:calc_dependency_distances"

The mean dependency distance grows with sentence length, and the longest one is the best of the tree features at the level of a single sentence. One-word sentences enter none of the metrics of the distances.

=== "Code"

    ``` python
    import spacy
    from ruts.syntax_stats import calc_dependency_distances

    nlp = spacy.load("ru_core_news_sm")
    doc = nlp("Повышение эффективности использования ресурсов предприятия обсуждалось на совещании.")
    calc_dependency_distances(doc)
    ```

=== "Result"

    ```
    [5, 1, 1, 1, 1, 1, 2]
    ```

</div>

<div class="metric-card" markdown>

### Tree depth { #tree_depth }

`tree_depth`
{ .metric-meta }

--8<-- "stats/syntax_stats.md:calc_tree_depth"

The depth is `LONGEST_PATH` of the paper of Ivanov et al. (r = 0.84).

</div>

<div class="metric-card" markdown>

### Leaves and subtrees { #leaves }

`leaves_per_sent` · `subtrees_per_sent` · `nodes_per_leaf`
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-leaves"

The features of the paper: `LEAVES_NUMBER` (r = 0.84), `PATH_NUMBER` (r = 0.87) and `AVERAGE_PATH` (r = 0.84). The distribution of the words by number of dependents, the branching profile, is the attribute `c_children`.

</div>

<div class="metric-card" markdown>

### Words before the root { #words_before_root }

`words_before_root` · [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664)
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-words_before_root"

</div>

<div class="metric-card" markdown>

### Valency of the finite verbs { #valency }

`verb_valency`
{ .metric-meta }

--8<-- "stats/syntax_stats.md:calc_valency"

A finite verb is one of [`is_finite_verb`](#is_finite_verb); the valency is `VERBS_DEP` of the paper (r = 0.43).

</div>

<div class="metric-card" markdown>

### Coordination chains { #coordination_chains }

`coordination_chains_per_sent` · `mean_coordination_chain_len`
{ .metric-meta }

--8<-- "stats/syntax_stats.md:calc_coordination_chains"

The number of chains per sentence (`SOCHIN_NUMBER`, r = 0.93) and their mean length (`AVERAGE_SOCHIN_LENGTH`, r = 0.87) are the strongest syntactic predictors of textbook complexity.

</div>

<div class="metric-card" markdown>

### Clauses { #clauses }

`clauses_per_sent` · `mean_clause_len`
{ .metric-meta }

``` {.python .signature}
is_clause_head(token)
```

Checks whether a word heads a clause: the head of the sentence or a word with `ccomp`, `advcl`, `acl`, `csubj`, `parataxis` and their subtypes (`anyts.constants.CLAUSE_DEPS`), except full participles, adverbial participles and infinitives under a noun («желание уйти»): participial and adverbial participle clauses are counted apart, and a short participle («дом построен») is the predicate of its clause. Under `xcomp` only an infinitive of `is_infinitive_clause` heads a clause: a finite form under `xcomp` is a parse error of the Russian models. An infinitive subject (`csubj`) of a modal word («нужно уйти», «можно войти», «следует отметить») heads no clause of its own. A parenthetical construction (`parataxis`) and a coordinated predicate (a `conj` relation from the clause head) form their own clause only if they can be a predicate ([`is_predicate`](#is_predicate)): «Он сказал: „Уходи“» and «думала, что он умен» are clauses, while the parentheticals «например», «конечно», «во-первых», which spaCy models also attach as `parataxis`, are not.

``` {.python .signature}
is_infinitive_clause(token)
```

Checks whether an infinitive under `xcomp` heads a clause of its own («хочет уйти», «попросил его уйти»): it does not when it makes one predicate with its head (`is_infinitive_periphrasis`) or stands in a participial or adverbial participle clause («решивший уйти», «желая уйти»).

``` {.python .signature}
is_infinitive_periphrasis(token)
```

Checks whether an infinitive makes one predicate with its head: a modal or phasal verb or a modal word of `INFINITIVE_PERIPHRASES` («может уйти», «должен прийти», «начал читать», «взялся читать», «перестал курить», «пришлось уйти», «стоит отметить», «нужно уйти», «можно войти», «невозможно описать», «пора идти»), the short form of a modal adjective of `MODAL_SHORT_ADJECTIVES` («готов уйти», «рад помочь») or the hortative «давай», «давайте» of `HORTATIVE_WORDS` without a negation («давайте играть», but not «не давайте детям играть»).

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |

</div>

<div class="metric-card" markdown>

### Subordinate clauses { #subordinate_clauses }

`subordinate_clauses_per_sent` · `p_complex_sents`
{ .metric-meta }

``` {.python .signature}
is_subordinate_clause_head(token)
```

Checks whether a word heads a subordinate clause: a clause head (`is_clause_head`) with a finite predicate under `ccomp`, `advcl`, `acl`, `csubj` and their subtypes, a coordinated predicate of a subordinate clause, or a clause under `conj` or `parataxis` with a subordinating conjunction of `SUBORDINATING_MARKS` («ушел, ибо устал»), which the models attach to the main clause as a conjunct. An infinitive heads an infinitive clause, not a subordinate one.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |

The features of the paper: `PODCHIN_RATE` (r = 0.64), the subordinate clauses per sentence, and `PODCHIN_NUMBER` (r = 0.62), the share of the sentences with at least one subordinate clause.

</div>

<div class="metric-card" markdown>

### Infinitive clauses { #infinitive_clauses }

`infinitive_clauses_per_sent`
{ .metric-meta }

``` {.python .signature}
is_infinitive_clause_head(token)
```

Checks whether a word heads an infinitive clause: an infinitive under `xcomp` that heads a clause of its own (`is_infinitive_clause`: «хочет уйти», «попросил его уйти»), an infinitive clause head under `ccomp`, `advcl`, `acl` or `csubj` («пришел, чтобы помочь», «трудно сказать»), or an infinitive coordinated with it. Such a clause is counted apart from the subordinate ones, as grammars of many languages take it for a part of a simple sentence.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |

=== "Code"

    ``` python
    import spacy
    from ruts.syntax_stats import is_clause_head, is_infinitive_clause_head, is_subordinate_clause_head

    nlp = spacy.load("ru_core_news_sm")
    doc = nlp("Он хочет уйти, но может остаться, если его попросят.")
    [token.text for token in doc if is_clause_head(token)]
    [token.text for token in doc if is_subordinate_clause_head(token)]
    [token.text for token in doc if is_infinitive_clause_head(token)]
    ```

=== "Result"

    ```
    ['хочет', 'уйти', 'может', 'попросят']
    ['попросят']
    ['уйти']
    ```

</div>

<div class="metric-card" markdown>

### Production units of L2SCA { #l2sca }

`t_units_per_sent` · `mean_t_unit_len` · `clauses_per_t_unit` · `p_complex_t_units` · `verb_phrases_per_t_unit` · `coordinate_phrases_per_clause` · `complex_nominals_per_clause` · [Lu 2010](https://doi.org/10.1075/ijcl.15.4.02lu)
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-l2sca"

</div>

<div class="metric-card" markdown>

### Modifiers of a noun { #noun_modifiers }

`modifiers_per_noun`
{ .metric-meta }

--8<-- "stats/syntax_stats.md:count_noun_modifiers"

The number of modifiers is `NOUNS_DEP` of the paper (r = 0.88).

</div>

<div class="metric-card" markdown>

### Prepositional chains { #prep_chains }

`prep_chains_per_sent` · `max_prep_chain_len` · [Profiling-UD](https://aclanthology.org/2020.lrec-1.883/)
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-prep_chains"

The genitive chains of ruTS ([`genitive_chains_per_sent`](#genitive_chains)) are counted apart: their links are prepositionless genitive modifiers («повышение эффективности использования ресурсов»), and those of a prepositional chain are complements with a preposition.

</div>

<div class="metric-card" markdown>

### Genitive chains { #genitive_chains }

`genitive_chains_per_sent` · `max_genitive_chain_len`
{ .metric-meta }

``` {.python .signature}
calc_genitive_chains(tokens)
```

The lengths of the genitive chains in the order of the words: the chains of [`calc_modifier_chains`](#calc_modifier_chains) whose modifiers are prepositionless genitive modifiers; «повышение эффективности использования ресурсов» is a chain of length 3.

``` {.python .signature}
is_genitive_modifier(token)
```

Checks whether a word is a prepositionless genitive modifier: a word with the `nmod` relation in the genitive case without a dependent preposition (`case`), «дом отца», but not «дом у дороги».

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `tokens` | `Doc` / `Span` / `list[Token]` | - | Sequence of tokens (`calc_genitive_chains`) |
| `token` | `Token` | - | Token (`is_genitive_modifier`) |

=== "Code"

    ``` python
    import spacy
    from ruts.syntax_stats import calc_genitive_chains

    nlp = spacy.load("ru_core_news_sm")
    calc_genitive_chains(
        nlp("Повышение эффективности использования ресурсов предприятия обсуждалось на совещании.")
    )
    ```

=== "Result"

    ```
    [4]
    ```

</div>

<div class="metric-card" markdown>

### Participial clauses { #participle_clauses }

`participle_clauses_per_sent` · `mean_participle_clause_len`
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-participle_clauses"

``` {.python .signature}
is_participle_clause(token)
```

Checks whether a word heads a participial clause: a full participle ([`is_participle`](#is_finite_verb)) with at least one dependent word, the coordination and parenthetical relations left out. Short participles («дом построен») are predicates rather than modifiers and head no clauses. The features of the paper are `PRICH_RATE` (r = 0.91) and `PRICH_V`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |

</div>

<div class="metric-card" markdown>

### Adverbial participle clauses { #converb_clauses }

`converb_clauses_per_sent` · `mean_converb_clause_len`
{ .metric-meta }

``` {.python .signature}
is_converb_clause(token)
```

Checks whether a word heads an adverbial participle clause: an adverbial participle ([`is_converb`](#is_finite_verb)) with at least one dependent word, the coordination and parenthetical relations left out. The length of a clause is the number of the words in the subtree of the adverbial participle (`subtree_len`). The features of the paper are `DEEPRICH_RATE` (r = 0.44) and `DEEPRICH_V`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |

</div>

<div class="metric-card" markdown>

### Passive { #passive }

`p_passive` · `p_agentless_passive`
{ .metric-meta }

--8<-- "stats/syntax_stats.md:is_passive"

--8<-- "stats/syntax_stats.md:has_agent"

--8<-- "stats/syntax_stats.md:is_agentless"

In Russian the passive is a passive participle or the reflexive passive («обсуждалось»), and an agentless form is «дом построен», but not «дом построен рабочими».

</div>

<div class="metric-card" markdown>

### Infinitives, negations and split predicates { #constructions }

`infinitives_per_sent` · `negations_per_sent` · `split_predicates_per_sent`
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-constructions"

``` {.python .signature}
is_negation(token)
```

Checks whether a word is a negative particle: a particle (`PART`) with the feature `Polarity=Neg` or the particle «не», «ни» (`NEGATION_PARTICLES`); the conjunction «ни» of «ни… ни» is no negation. The negations are `NEG` of the paper (r = 0.70).

``` {.python .signature}
find_split_predicates(tokens)
```

``` {.python .signature}
is_light_verb(token)
```

``` {.python .signature}
is_reflexive(token)
```

``` {.python .signature}
is_split_predicate_noun(token, verb=None)
```

The split predicates, a marker of officialese, are pairs of a verb and a noun in the order of the words: a light verb (`is_light_verb`) with a lemma of `LIGHT_VERBS` (for example: осуществлять, производить, проводить, вести, обеспечивать, оказывать, принимать, иметь and their reflexive passives проводиться, приниматься, вестись) with a nominal part (`is_split_predicate_noun`), a noun with a verbal lemma (`ruts.utils.is_verbal_noun`) or a lemma of `SPLIT_PREDICATE_NOUNS` (for example: роль, работа, помощь, мера) with a verb `verb` of its own phrase (оказать помощь, принять меры, but not получить работу): осуществлять проверку, оказать помощь, принято решение, проверка проводится. At most one nominal part is taken per verb in the order of preference `obj`, `nsubj:pass`, `nsubj` (only for a reflexive or passive verb, `is_reflexive`), `iobj`, `nmod`, `obl`; prepositional adjuncts and the passive agent (`obl:agent`, instrumental `obl`) are not counted. The verb lemma is taken from the pymorphy3 analysis twice: with the part of speech of the token ([`get_lemma`](#helpers)) and as a verb (`ruts.utils.lemmatize`).

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |
| `tokens` | `Doc` / `Span` / `list[Token]` | - | Sequence of tokens (`find_split_predicates`) |
| `verb` | `Token` | `None` | Light verb (`is_split_predicate_noun`); without it the phrase is not checked |

=== "Code"

    ``` python
    import spacy
    from ruts.syntax_stats import find_split_predicates, is_negation

    nlp = spacy.load("ru_core_news_sm")
    doc = nlp("Проверка проводится ежегодно, но решение не принято.")
    find_split_predicates(doc)
    [token.text for token in doc if is_negation(token)]
    ```

=== "Result"

    ```
    [(проводится, Проверка), (принято, решение)]
    ['не']
    ```

</div>

<div class="metric-card" markdown>

### Order of the subjects and the objects { #word_order }

`p_preverbal_subjects` · `p_preverbal_objects` · [Profiling-UD](https://aclanthology.org/2020.lrec-1.883/)
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-word_order"

</div>

<div class="metric-card" markdown>

### Similarity of adjacent sentences { #similarity }

`pos_edit_distance` · `syntax_similarity` · [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664)
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-similarity"

</div>

<div class="metric-card" markdown>

### Ratio of the nouns to the verbs { #noun_verb_ratio }

`noun_verb_ratio`
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-noun_verb_ratio"

</div>

## Methods

The methods `get_stats`, `to_dataframe`, `print_stats` and `describe` are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the syntactic statistics have no scales, so `describe` gives `None` for the statistics of `get_stats`.

=== "Code"

    ``` python
    ss.get_stats()
    ```

=== "Result"

    ```
    {'mean_dependency_distance': 1.9333333333333333,
     'std_dependency_distance': 1.6110727964792764,
     'max_dependency_distance': 5.0,
     'p_adjacent_dependencies': 0.6,
     'tree_depth': 4.0,
     'leaves_per_sent': 4.5,
     'subtrees_per_sent': 4.0,
     'nodes_per_leaf': 1.9,
     'words_before_root': 4.0,
     'verb_valency': 2.0,
     'coordination_chains_per_sent': 0.5,
     'mean_coordination_chain_len': 2.0,
     'clauses_per_sent': 1.5,
     'mean_clause_len': 5.666666666666667,
     'subordinate_clauses_per_sent': 0.5,
     'p_complex_sents': 0.5,
     'infinitive_clauses_per_sent': 0.0,
     't_units_per_sent': 1.0,
     'mean_t_unit_len': 8.5,
     'clauses_per_t_unit': 1.5,
     'p_complex_t_units': 0.5,
     'verb_phrases_per_t_unit': 2.5,
     'coordinate_phrases_per_clause': 0.3333333333333333,
     'complex_nominals_per_clause': 1.0,
     'modifiers_per_noun': 0.4,
     'prep_chains_per_sent': 0.0,
     'max_prep_chain_len': 0,
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
     'p_preverbal_subjects': 1.0,
     'p_preverbal_objects': nan,
     'pos_edit_distance': 0.7777777777777778,
     'syntax_similarity': 0.0625,
     'noun_verb_ratio': 1.0}
    ```

The functions work with spaCy tokens: the `calc_*` and `find_*` functions and `dependency_triples` take a sequence of tokens (`Doc`, `Span` or a list), the `is_*` and `count_*` functions a single token, and `calc_edit_distance` and `calc_multiset_similarity` lists of the items of sentences; the words of a sequence are the tokens of [`is_word`](#helpers). The functions of the dependency tree come from the core, those of the Russian constructions are ruTS's own. Relation subtypes (`acl:relcl`, `nsubj:pass`, `nummod:gov`) are counted by the base relation ([`base_dep`](#base_dep)) where noted.

## Words of a sequence { #get_words }

--8<-- "stats/syntax_stats.md:get_words"

## Hyphenated words { #hyphenated-words }

--8<-- "stats/syntax_stats.md:hyphenated_words"

`SyntaxStats` and the functions of the Russian constructions always join hyphenated words. The functions of the core, `is_predicate`, `count_noun_modifiers`, `is_passive`, `has_agent` and `is_agentless` included, take `join_hyphens=False` by default: they give the values of `SyntaxStats` with `join_hyphens=True`.

## Head of a sentence { #is_root }

--8<-- "stats/syntax_stats.md:is_root"

## Base relation { #base_dep }

--8<-- "stats/syntax_stats.md:base_dep"

## Dependent words { #get_children }

--8<-- "stats/syntax_stats.md:get_children"

--8<-- "stats/syntax_stats.md:count_children"

--8<-- "stats/syntax_stats.md:subtree_len"

## Verb forms { #is_finite_verb }

--8<-- "utils/spacy.md:is_finite_verb"

--8<-- "utils/spacy.md:is_infinitive"

``` {.python .signature}
is_participle(token)
```

``` {.python .signature}
is_converb(token)
```

`is_participle` checks whether a token is a full participle (`VerbForm=Part` without `Variant=Short` and `StyleVariant=Short`), `is_converb` whether it is an adverbial participle (`VerbForm=Conv`); the argument is the same token.

## Predicate of a clause { #is_predicate }

--8<-- "stats/syntax_stats.md:is_predicate"

## Chains of modifiers { #calc_modifier_chains }

--8<-- "stats/syntax_stats.md:calc_modifier_chains"

## Complements with a preposition { #is_prep_complement }

--8<-- "stats/syntax_stats.md:is_prep_complement"

## Dependency triples { #dependency_triples }

--8<-- "stats/syntax_stats.md:dependency_triples"

## Edit distance and multiset similarity { #calc_edit_distance }

--8<-- "stats/syntax_stats.md:calc_edit_distance"

--8<-- "stats/syntax_stats.md:calc_multiset_similarity"

## Helper functions { #helpers }

--8<-- "utils/spacy.md:is_word"

--8<-- "utils/spacy.md:has_feature"

``` {.python .signature}
get_lemma(token)
```

The lemma of a token in lower case by the pymorphy3 analysis with the part of speech of the token (`ruts.utils.lemmatize`), not `token.lemma_`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |
