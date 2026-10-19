# Statistic functions

All functions work with spaCy `Token` objects: the `calc_*` functions take a sequence of tokens (`Doc`, `Span` or a list), the `is_*` and `count_*` functions - a single token. The functions of the dependency tree come from the [anyTS](https://sergeyshk.github.io/anyTS/stats/syntax_stats_funcs/) core, the functions of the Russian constructions are those of ruTS. Syntactic relations and morphological features are taken from the [Universal Dependencies](https://universaldependencies.org/u/dep/) annotation; relation subtypes (`acl:relcl`, `nsubj:pass`, `nummod:gov`) are counted by the base relation where noted.

The feature definitions follow [Ivanov, Solnyshkina and Solovyev (2018)](https://dialogue-conf.org/media/4302/ivanovvv.pdf); the original feature names and their correlation coefficients with the textbook grade from that paper are given in parentheses.

## Hyphenated words { #hyphenated-words }

--8<-- "stats/syntax_stats_funcs.md:hyphenated_words"

`SyntaxStats` and the functions of the Russian constructions always join hyphenated words (`во-первых` is one word). The functions of the core, `is_predicate`, `count_noun_modifiers`, `is_passive`, `has_agent` and `is_agentless` included, take `join_hyphens=False` by default: they give the values of `SyntaxStats` with `join_hyphens=True`.

## Dependency distances { #calc_dependency_distances }

!!! info ""
    **ruts.syntax_stats.calc_dependency_distances()**

--8<-- "stats/syntax_stats_funcs.md:calc_dependency_distances"

`SyntaxStats` derives from the distances the mean (`mean_dependency_distance`), the standard deviation over all dependencies of the text (`std_dependency_distance`), the maximum in a sentence averaged over sentences with dependencies (`max_dependency_distance`), and the share of adjacent relations of distance 1 (`p_adjacent_dependencies`); one-word sentences enter none of the statistics. The mean dependency distance grows with sentence length; the maximum distance is the best of the tree features at the level of an individual sentence.

!!! example "Example"

    ``` python
    import spacy
    from ruts.syntax_stats import calc_dependency_distances

    nlp = spacy.load("ru_core_news_sm")
    calc_dependency_distances(
        nlp("Повышение эффективности использования ресурсов предприятия обсуждалось на совещании.")
    )
    # [5, 1, 1, 1, 1, 1, 2]
    ```

## Tree depth { #calc_tree_depth }

!!! info ""
    **ruts.syntax_stats.calc_tree_depth()**

--8<-- "stats/syntax_stats_funcs.md:calc_tree_depth"

The depth is `LONGEST_PATH` of the paper (r = 0.84); `SyntaxStats` averages it over sentences (`tree_depth`).

## Leaves, subtrees and branching { #count_children }

!!! info ""
    **ruts.syntax_stats.count_children()**

--8<-- "stats/syntax_stats_funcs.md:count_children"

A word without dependents is a leaf (`LEAVES_NUMBER`, r = 0.84), a word with dependents heads a subtree (`PATH_NUMBER`, r = 0.87). `SyntaxStats` counts the numbers of leaves and subtrees per sentence (`leaves_per_sent`, `subtrees_per_sent`), the ratio of words to leaves (`AVERAGE_PATH`, r = 0.84; `nodes_per_leaf`) and the distribution of words by number of dependents - the branching profile (`c_children`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `token` | Token | `-` | Token |
| `join_hyphens` | bool | `False` | Take a hyphenated word for one word |

## Valency { #calc_valency }

!!! info ""
    **ruts.syntax_stats.calc_valency()**

--8<-- "stats/syntax_stats_funcs.md:calc_valency"

`SyntaxStats` averages the valency over finite verb forms (`VERBS_DEP`, r = 0.43; `verb_valency`), see [`is_finite_verb`](#is_finite_verb).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `token` | Token | `-` | Token |
| `join_hyphens` | bool | `False` | Take a hyphenated word for one word |

## Coordination chains { #calc_coordination_chains }

!!! info ""
    **ruts.syntax_stats.calc_coordination_chains()**

--8<-- "stats/syntax_stats_funcs.md:calc_coordination_chains"

The number of chains per sentence (`SOCHIN_NUMBER`, r = 0.93) and their mean length (`AVERAGE_SOCHIN_LENGTH`, r = 0.87) are the strongest syntactic predictors of textbook complexity.

## Clauses { #is_clause_head }

!!! info ""
    **ruts.syntax_stats.is_clause_head()**, **ruts.syntax_stats.is_infinitive_clause()**, **ruts.syntax_stats.is_infinitive_periphrasis()**, **ruts.syntax_stats.is_subordinate_clause_head()**, **ruts.syntax_stats.is_predicate()**

Checking whether a token heads a clause. A clause is headed by the sentence root or by a word with the relation `ccomp`, `advcl`, `acl`, `acl:relcl`, `csubj` or `csubj:pass`, except full participles, adverbial participles and infinitives attached to a noun («желание уйти»): participial and adverbial participle clauses are counted separately. An infinitive attached to a verb (`xcomp`) heads a clause of its own («хочет уйти», «попросил его уйти», `is_infinitive_clause`), except in combinations of one predication (`is_infinitive_periphrasis`): with the modal and phasal verbs of `INFINITIVE_PERIPHRASES` («может уйти», «должен прийти», «начал читать», «перестал курить») and the hortative «давай», «давайте» without a negation (`HORTATIVE_WORDS`). A parenthetical construction (`parataxis`) and a coordinated predicate (a `conj` relation from the clause head) form their own clause only if it can be a predicate (`is_predicate`): «Он сказал: „Уходи“» and «думала, что он умен» are clauses, while the parentheticals «например», «конечно», «во-первых», which spaCy models also attach as `parataxis`, are not.

--8<-- "stats/syntax_stats_funcs.md:is_predicate"

A subordinate clause is a clause with the relation `ccomp`, `advcl`, `acl`, `acl:relcl`, `csubj`, `csubj:pass` or `xcomp`, as well as a coordinated predicate of a subordinate clause (`PODCHIN_RATE`, r = 0.64). `SyntaxStats` counts clauses and subordinate clauses per sentence (`clauses_per_sent`, `subordinate_clauses_per_sent`), the mean clause length in words (`mean_clause_len`) and the share of sentences with at least one subordinate clause (`PODCHIN_NUMBER`, r = 0.62; `p_complex_sents`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `token` | Token | `-` | Token |

## Noun phrase modifiers { #count_noun_modifiers }

!!! info ""
    **ruts.syntax_stats.count_noun_modifiers()**

--8<-- "stats/syntax_stats_funcs.md:count_noun_modifiers"

`SyntaxStats` averages the number of modifiers over nouns and proper names (`NOUNS_DEP`, r = 0.88; `modifiers_per_noun`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `token` | Token | `-` | Token |
| `join_hyphens` | bool | `False` | Take a hyphenated word for one word |

## Genitive chains { #calc_genitive_chains }

!!! info ""
    **ruts.syntax_stats.calc_genitive_chains()**, **ruts.syntax_stats.is_genitive_modifier()**, **ruts.syntax_stats.calc_modifier_chains()**

Computation of genitive chain lengths - the chains of `calc_modifier_chains` whose modifiers are prepositionless genitive modifiers (`is_genitive_modifier`): a word with the `nmod` relation in the genitive case without a dependent preposition (`case`), «дом отца», but not «дом у дороги». `SyntaxStats` counts the number of chains per sentence (`genitive_chains_per_sent`) and the maximum length over the text (`max_genitive_chain_len`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `tokens` | Doc/Span/list[Token] | `-` | Sequence of tokens |

!!! example "Example"

    ``` python
    import spacy
    from ruts.syntax_stats import calc_genitive_chains

    nlp = spacy.load("ru_core_news_sm")
    calc_genitive_chains(nlp("Повышение эффективности использования ресурсов обсуждалось долго."))
    # [3]
    ```

### calc_modifier_chains

--8<-- "stats/syntax_stats_funcs.md:calc_modifier_chains"

## Participial and adverbial participle clauses { #is_participle_clause }

!!! info ""
    **ruts.syntax_stats.is_participle_clause()**, **ruts.syntax_stats.is_converb_clause()**, **ruts.syntax_stats.subtree_len()**

Checking whether a token heads a participial or adverbial participle clause: a full participle ([`is_participle`](#is_finite_verb)) or an adverbial participle ([`is_converb`](#is_finite_verb)) with at least one dependent word, not counting coordination and parenthetical relations. Short participles («дом построен») are predicates rather than modifiers and form no clauses. The clause length is the number of words in the subtree including the participle itself ([`subtree_len`](#helpers)). `SyntaxStats` counts clauses per sentence (`PRICH_RATE`, r = 0.91; `DEEPRICH_RATE`, r = 0.44) and their mean length (`PRICH_V`, `DEEPRICH_V`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `token` | Token | `-` | Token |

## Passive voice { #is_passive }

!!! info ""
    **ruts.syntax_stats.is_passive()**, **ruts.syntax_stats.has_agent()**, **ruts.syntax_stats.is_agentless()**

--8<-- "stats/syntax_stats_funcs.md:is_passive"

--8<-- "stats/syntax_stats_funcs.md:has_agent"

--8<-- "stats/syntax_stats_funcs.md:is_agentless"

In Russian the passive is a passive participle or the reflexive passive («обсуждалось»), and an agentless form is «дом построен», but not «дом построен рабочими». `SyntaxStats` counts the share of passive forms among all verb forms (`p_passive`) and the share of agentless forms among passive ones (`p_agentless_passive`).

## Verb forms { #is_finite_verb }

!!! info ""
    **ruts.syntax_stats.is_finite_verb()**, **ruts.syntax_stats.is_participle()**, **ruts.syntax_stats.is_converb()**, **ruts.syntax_stats.is_infinitive()**

--8<-- "utils/spacy.md:is_finite_verb"

--8<-- "utils/spacy.md:is_infinitive"

`is_participle(token)` checks whether a token is a full participle (`VerbForm=Part` without `Variant=Short`), `is_converb(token)` - whether it is an adverbial participle (`VerbForm=Conv`). `SyntaxStats` counts infinitives per sentence (`infinitives_per_sent`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `token` | Token | `-` | Token |

## Negations { #is_negation }

!!! info ""
    **ruts.syntax_stats.is_negation()**

Checking whether a token is a negative particle - a particle (`PART`) with the feature `Polarity=Neg` or the particle «не», «ни». The conjunction «ни» in the «ни… ни» construction does not count as a negation. `SyntaxStats` counts negations per sentence (`NEG`, r = 0.70; `negations_per_sent`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `token` | Token | `-` | Token |

## Split predicates { #find_split_predicates }

!!! info ""
    **ruts.syntax_stats.find_split_predicates()**, **ruts.syntax_stats.is_light_verb()**, **ruts.syntax_stats.is_reflexive()**, **ruts.syntax_stats.is_split_predicate_noun()**

Search for split predicates - an officialese marker: a light verb with a lemma from `LIGHT_VERBS` (осуществлять, производить, проводить, обеспечивать, оказывать, принимать, иметь and their reflexive passives проводиться, приниматься, вестись) with a nominal part - a noun with a verbal lemma (`ruts.utils.is_verbal_noun`) or a lemma from `SPLIT_PREDICATE_NOUNS` (роль, работа, помощь, мера) with a verb of its own phrase (оказать помощь, принять меры, but not получить работу): осуществлять проверку, оказать помощь, принято решение, проверка проводится. At most one nominal part is taken per verb in the order of preference `obj`, `nsubj:pass`, `nsubj` (only for a reflexive or passive verb, `is_reflexive`), `iobj`, `nmod`, `obl`; prepositional adjuncts and the passive agent (`obl:agent`, instrumental `obl`) are not counted. The verb lemma is checked both by spaCy and by pymorphy3 (`get_lemma`, `ruts.utils.lemmatize`). `SyntaxStats` counts split predicates per sentence (`split_predicates_per_sent`) and keeps the found pairs in `split_predicates`; the ratio of nouns to verb forms (`noun_verb_ratio`) is computed from the class counters.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `tokens` | Doc/Span/list[Token] | `-` | Sequence of tokens |

## Helper functions { #helpers }

!!! info ""
    **ruts.syntax_stats.is_word()**, **ruts.syntax_stats.get_words()**, **ruts.syntax_stats.is_root()**, **ruts.syntax_stats.base_dep()**, **ruts.syntax_stats.get_children()**, **ruts.syntax_stats.subtree_len()**, **ruts.syntax_stats.has_feature()**, **ruts.syntax_stats.get_lemma()**

### is_word

--8<-- "utils/spacy.md:is_word"

### get_words

--8<-- "stats/syntax_stats_funcs.md:get_words"

### is_root

--8<-- "stats/syntax_stats_funcs.md:is_root"

### base_dep

--8<-- "stats/syntax_stats_funcs.md:base_dep"

### get_children, subtree_len

--8<-- "stats/syntax_stats_funcs.md:get_children"

--8<-- "stats/syntax_stats_funcs.md:subtree_len"

### has_feature

--8<-- "utils/spacy.md:has_feature"

### get_lemma

`get_lemma(token)` returns the lemma of a token in lower case from pymorphy3 by the part of speech of the token.
