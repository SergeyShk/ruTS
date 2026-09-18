# Statistic functions

All functions work with spaCy `Token` objects: the `calc_*` functions take a sequence of tokens (`Doc`, `Span` or a list), the `is_*` and `count_*` functions - a single token. Punctuation and whitespace tokens are skipped. Syntactic relations and morphological features are taken from the [Universal Dependencies](https://universaldependencies.org/u/dep/) annotation; relation subtypes (`acl:relcl`, `nsubj:pass`, `nummod:gov`) are counted by the base relation where noted.

The feature definitions follow [Ivanov, Solnyshkina and Solovyev (2018)](https://dialogue-conf.org/media/4302/ivanovvv.pdf); the original feature names and their correlation coefficients with the textbook grade from that paper are given in parentheses.

## Dependency distances { #calc_dependency_distances }

!!! info ""
    **ruts.syntax_stats.calc_dependency_distances()**

Computation of dependency distances - the distances between a word and its head in word positions, ignoring punctuation (Liu, 2008). Sentence roots have no dependency and are skipped, as are words whose head lies outside the given sequence. `SyntaxStats` derives from the distances the mean (`mean_dependency_distance`), the standard deviation over all dependencies of the text (`std_dependency_distance`), the maximum in a sentence averaged over sentences with dependencies (`max_dependency_distance`), and the share of adjacent relations of distance 1 (`p_adjacent_dependencies`); one-word sentences enter none of the statistics. The mean dependency distance grows with sentence length; the maximum distance is the best of the tree features at the level of an individual sentence.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `tokens` | Doc/Span/list[Token] | `-` | Sequence of tokens |

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

Computation of the dependency tree depth - the length of the longest path from the sentence root to a leaf in relations (`LONGEST_PATH`, r = 0.84). For a sequence of several sentences the maximum is taken, for a one-word sentence - 0. `SyntaxStats` averages the depth over sentences (`tree_depth`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `tokens` | Doc/Span/list[Token] | `-` | Sequence of tokens |

## Leaves, subtrees and branching { #count_children }

!!! info ""
    **ruts.syntax_stats.count_children()**

Computation of the number of dependents of a token. A word without dependents is a leaf (`LEAVES_NUMBER`, r = 0.84), a word with dependents heads a subtree (`PATH_NUMBER`, r = 0.87). `SyntaxStats` counts the numbers of leaves and subtrees per sentence (`leaves_per_sent`, `subtrees_per_sent`), the ratio of words to leaves (`AVERAGE_PATH`, r = 0.84; `nodes_per_leaf`) and the distribution of words by number of dependents - the branching profile (`c_children`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `token` | Token | `-` | Token |

## Valency { #calc_valency }

!!! info ""
    **ruts.syntax_stats.calc_valency()**

Computation of the valency of a token - the number of dependents excluding coordination (`cc`, `conj`) and parenthetical (`parataxis`) relations. `SyntaxStats` averages the valency over finite verb forms (`VERBS_DEP`, r = 0.43; `verb_valency`); a finite form is a verb with the feature `VerbForm=Fin`, see [`is_finite_verb`](#is_finite_verb).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `token` | Token | `-` | Token |

## Coordination chains { #calc_coordination_chains }

!!! info ""
    **ruts.syntax_stats.calc_coordination_chains()**

Computation of coordination chain lengths. In Universal Dependencies all coordinated members attach with the `conj` relation to the first of them, so a chain is a word with `conj` dependents, and its length is the number of coordinated members including the first: the sentence «Он купил хлеб, молоко и сыр» has one chain of length 3. The number of chains per sentence (`SOCHIN_NUMBER`, r = 0.93) and their mean length (`AVERAGE_SOCHIN_LENGTH`, r = 0.87) are the strongest syntactic predictors of textbook complexity.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `tokens` | Doc/Span/list[Token] | `-` | Sequence of tokens |

## Clauses { #is_clause_head }

!!! info ""
    **ruts.syntax_stats.is_clause_head()**, **ruts.syntax_stats.is_subordinate_clause_head()**, **ruts.syntax_stats.is_predicate()**

Checking whether a token heads a clause. A clause is headed by the sentence root or by a word with the relation `ccomp`, `advcl`, `acl`, `acl:relcl`, `csubj` or `csubj:pass`, except full participles, adverbial participles and infinitives attached to a noun («желание уйти»): participial and adverbial participle clauses are counted separately. A parenthetical construction (`parataxis`) and a coordinated predicate (a `conj` relation from the clause head) form their own clause only if it is a verb or has its own subject (`is_predicate`): «Он сказал: „Уходи“» and «думала, что он умён» are clauses, while the parentheticals «например», «конечно», «во-первых», which spaCy models also attach as `parataxis`, are not.

A subordinate clause is a clause with the relation `ccomp`, `advcl`, `acl`, `acl:relcl`, `csubj` or `csubj:pass`, as well as a coordinated predicate of a subordinate clause (`PODCHIN_RATE`, r = 0.64). `SyntaxStats` counts clauses and subordinate clauses per sentence (`clauses_per_sent`, `subordinate_clauses_per_sent`), the mean clause length in words (`mean_clause_len`) and the share of sentences with at least one subordinate clause (`PODCHIN_NUMBER`, r = 0.62; `p_complex_sents`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `token` | Token | `-` | Token |

## Noun phrase modifiers { #count_noun_modifiers }

!!! info ""
    **ruts.syntax_stats.count_noun_modifiers()**

Computation of the number of noun phrase modifiers - dependents with the relations `amod`, `det`, `nmod`, `nummod`, `acl` and their subtypes (`acl:relcl`, `nummod:gov`). Coordination and apposition relations (`conj`, `appos`) are not counted. `SyntaxStats` averages the number of modifiers over nouns and proper names (`NOUNS_DEP`, r = 0.88; `modifiers_per_noun`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `token` | Token | `-` | Token |

## Genitive chains { #calc_genitive_chains }

!!! info ""
    **ruts.syntax_stats.calc_genitive_chains()**, **ruts.syntax_stats.is_genitive_modifier()**

Computation of genitive chain lengths - two or more nested prepositionless genitive modifiers: «повышение эффективности использования ресурсов» is a chain of length 3. A prepositionless modifier is a word with the `nmod` relation in the genitive case without a dependent preposition (`case`): «дом отца», but not «дом у дороги». A chain starts with a modifier whose head is not itself such a modifier; the length is the number of words in the longest branch. `SyntaxStats` counts the number of chains per sentence (`genitive_chains_per_sent`) and the maximum length over the text (`max_genitive_chain_len`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `tokens` | Doc/Span/list[Token] | `-` | Sequence of tokens |

## Participial and adverbial participle clauses { #is_participle_clause }

!!! info ""
    **ruts.syntax_stats.is_participle_clause()**, **ruts.syntax_stats.is_converb_clause()**, **ruts.syntax_stats.subtree_len()**

Checking whether a token heads a participial or adverbial participle clause: a full participle (`VerbForm=Part` without `Variant=Short`) or an adverbial participle (`VerbForm=Conv`) with at least one dependent word, not counting coordination and parenthetical relations. Short participles («дом построен») are predicates rather than modifiers and form no clauses. The clause length is the number of words in the subtree including the participle itself (`subtree_len`). `SyntaxStats` counts clauses per sentence (`PRICH_RATE`, r = 0.91; `DEEPRICH_RATE`, r = 0.44) and their mean length (`PRICH_V`, `DEEPRICH_V`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `token` | Token | `-` | Token |

## Passive voice { #is_passive }

!!! info ""
    **ruts.syntax_stats.is_passive()**, **ruts.syntax_stats.is_agentless()**

Checking whether a token is a passive verb form - a verb with the feature `Voice=Pass` (passive participles, the reflexive passive «обсуждалось») or with a dependent `nsubj:pass`, `csubj:pass` or `aux:pass`. An agentless form is a passive without a dependent `obl:agent`: «дом построен», but not «дом построен рабочими». `SyntaxStats` counts the share of passive forms among all verb forms (`p_passive`) and the share of agentless forms among passive ones (`p_agentless_passive`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `token` | Token | `-` | Token |

## Verb forms { #is_finite_verb }

!!! info ""
    **ruts.syntax_stats.is_finite_verb()**, **ruts.syntax_stats.is_participle()**, **ruts.syntax_stats.is_converb()**, **ruts.syntax_stats.is_infinitive()**

Verb form checks by the `VerbForm` feature: finite form (`Fin`, only for the part of speech `VERB`), full participle (`Part` without `Variant=Short`), adverbial participle (`Conv`), infinitive (`Inf`). `SyntaxStats` counts infinitives per sentence (`infinitives_per_sent`).

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

Search for split predicates - an officialese marker: a light verb with a lemma from `LIGHT_VERBS` (осуществлять, производить, проводить, обеспечивать, оказывать, принимать, иметь and their reflexive passives проводиться, приниматься, вестись) with a nominal part - a noun with a verbal lemma (`ruts.utils.is_verbal_noun`) or a lemma from `SPLIT_PREDICATE_NOUNS` (роль, работа, помощь, мера): осуществлять проверку, оказать помощь, принято решение, проверка проводится. At most one nominal part is taken per verb in the order of preference `obj`, `nsubj:pass`, `nsubj` (only for a reflexive or passive verb, `is_reflexive`), `iobj`, `nmod`, `obl`; prepositional adjuncts and the passive agent (`obl:agent`, instrumental `obl`) are not counted. The verb lemma is checked both by spaCy and by pymorphy3 (`get_lemma`, `ruts.utils.lemmatize`). `SyntaxStats` counts split predicates per sentence (`split_predicates_per_sent`) and keeps the found pairs in `split_predicates`; the ratio of nouns to verb forms (`noun_verb_ratio`) is computed from the class counters.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `tokens` | Doc/Span/list[Token] | `-` | Sequence of tokens |

## Helper functions { #helpers }

!!! info ""
    **ruts.syntax_stats.is_word()**, **ruts.syntax_stats.get_words()**, **ruts.syntax_stats.is_root()**, **ruts.syntax_stats.base_dep()**, **ruts.syntax_stats.get_children()**, **ruts.syntax_stats.has_feature()**, **ruts.syntax_stats.get_lemma()**

| Function | Description |
| :------- | :---------- |
| `is_word(token)` | The token is neither punctuation nor whitespace |
| `get_words(tokens)` | List of words of a token sequence |
| `is_root(token)` | The token is the sentence root |
| `base_dep(token)` | Base relation without the subtype: `acl:relcl` → `acl` |
| `get_children(token)` | List of the token's dependent words |
| `has_feature(token, field, value)` | The token has the morphological feature `field` with the value `value` |
| `get_lemma(token)` | Lowercased lemma of the token from pymorphy3 by the token's part of speech |
