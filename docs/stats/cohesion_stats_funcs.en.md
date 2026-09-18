# Statistic functions

The overlap functions take sets or lists of the lemmas of every sentence in text order; word features for `CohesionStats` are given by [`word_info`](#word_info) and [`token_info`](#word_info). The names of the [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664) indices are given in parentheses.

## Binary overlap { #calc_overlap }

!!! info ""
    **ruts.cohesion_stats.calc_overlap()**

Computation of the share of sentence pairs with a shared element: a noun lemma (`CRFNO1`, `CRFNOa`), an argument (`CRFAO1`, `CRFAOa`) or a content word (`CRFSO1`, `CRFSOa`). By default adjacent sentence pairs are counted, with `adjacent=False` - all pairs. For a text shorter than two sentences `nan` is returned.

Formula:

$$
\frac{|\{(i, j): S_i \cap S_j \neq \varnothing\}|}{|\{(i, j)\}|}
$$

where $S_i$ is the set of lemmas of sentence $i$, the pairs $(i, j)$ are adjacent or all.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `sets` | list[set[str]] | `-` | Sets of elements of every sentence |
| `adjacent` | bool | `True` | Count only adjacent pairs, otherwise all pairs |

!!! example "Example"

    ``` python
    from ruts.cohesion_stats import calc_overlap

    sets = [{"кот", "окно"}, {"птица"}, {"птица", "кот"}, {"окно"}]
    calc_overlap(sets)
    # 0.3333333333333333
    calc_overlap(sets, adjacent=False)
    # 0.5
    ```

## Proportional overlap { #calc_proportional_overlap }

!!! info ""
    **ruts.cohesion_stats.calc_proportional_overlap()**

Computation of the mean share of shared elements in sentence pairs (`CRFCWO1`, `CRFCWOa`): the Dice coefficient of the lemma sets averaged over adjacent or all pairs; a pair without elements gets 0.

Formula:

$$
\frac{1}{|\{(i, j)\}|} \sum_{(i, j)} \frac{2 \cdot |S_i \cap S_j|}{|S_i| + |S_j|}
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `sets` | list[set[str]] | `-` | Sets of elements of every sentence |
| `adjacent` | bool | `True` | Count only adjacent pairs, otherwise all pairs |

## All overlaps in one pass { #calc_overlaps }

!!! info ""
    **ruts.cohesion_stats.calc_overlaps()**, **ruts.cohesion_stats.dice()**, **ruts.cohesion_stats.Overlap**

Computation of the binary and proportional overlaps over adjacent and all sentence pairs; returns `Overlap(adjacent, all, prop_adjacent, prop_all)` with the same values as [`calc_overlap`](#calc_overlap) and [`calc_proportional_overlap`](#calc_proportional_overlap). Adjacent pairs are traversed directly. The number of all pairs with a shared element is computed from bit masks of element occurrences in sentences (in blocks of 4096 sentences), the sum of Dice coefficients - from histograms of sentence lengths for every element: $(h W h - h \cdot \mathrm{diag}(W)) / 2$, where $h$ is the histogram of lengths of sentences containing the element, $W_{kl} = 2/(k+l)$. Time is linear in the number of occurrences. The `dice` function computes the Dice coefficient of two sets.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `sets` | list[set[str]] | `-` | Sets of elements of every sentence |

## Givenness { #count_given }

!!! info ""
    **ruts.cohesion_stats.count_given()**

Computation of the number of given elements - lemmas that already occurred earlier in the text, including the current sentence. `CohesionStats` divides the number of given content words by their total (`p_given`); the share of pronouns `p_pronouns`, the pronoun-to-noun ratio `pronoun_noun_ratio` and the share of demonstratives `p_demonstratives` are computed from the class counters.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `sents` | list[list[str]] | `-` | Lemmas of every sentence in text order |

## Tense and aspect repetition { #calc_repetition }

!!! info ""
    **ruts.cohesion_stats.calc_repetition()**, **ruts.cohesion_stats.dominant()**

Computation of the share of adjacent sentence pairs with the same dominant value of a verb feature - tense or aspect (`SMTEMP`). `dominant` takes the most frequent value (the first on a tie); pairs where one of the sentences has no verbs with the feature are skipped, and without such pairs `nan` is returned. `CohesionStats` computes `tense_repetition`, `aspect_repetition` and their mean `temporal_cohesion`.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `sents` | list[list[str]] | `-` | Verb feature values of every sentence |

## Connectives { #find_connectors }

!!! info ""
    **ruts.cohesion_stats.find_connectors()**, **ruts.cohesion_stats.load_connectors()**, **ruts.cohesion_stats.Connector**, **ruts.cohesion_stats.connector_pos()**

Search for connectives in a sentence by lowercased word forms with ё replaced by е: at every position the longest one is taken («и всё же» does not fall apart into «и»), matches do not overlap; patterns are indexed by the first word, so the search is linear in the number of words. A hyphen or period inside a connective may be split off by the tokenizer («Во», «первых» in spaCy, «т», «е» in `WordsExtractor`) - such variants are handled, and the occurrence boundaries are then counted in source words. The `load_connectors` dictionary reads `ruts/resources/connectors.tsv` - 317 connectives with a class from `CONNECTOR_CLASSES` and a type from `CONNECTOR_TYPES`, compiled after the classification of Krioni, Nikin and Filippova (2008) and checked against the [Ru-RSTreebank](https://rstreebank.ru/markersFull) marker list, the [Ruscon](https://ruslinkers.github.io/) database and the causal marker list of Toldova et al. (2018). The single-word «и», «а», «но» are in the dictionary, as in Coh-Metrix and TAACO; «что» and «как» do not count as connectives. If UD parts of speech (`pos`) are given, a single-word connective counts only with a part of speech from `CONNECTOR_POS` (`CCONJ`, `SCONJ`, `PART`, `ADV`, `ADP`, `INTJ`, `X`) or from `CONNECTOR_POS_EXTRA` for that word (словом - `NOUN`, главное - `ADJ`, `NOUN`, допустим - `VERB`, точнее - `ADJ`, т.е. - `PUNCT`); a part of speech of `None` is not checked. For a string the part of speech is given by `connector_pos` - the first pymorphy3 analysis with a suitable part of speech, otherwise the first analysis. The result is a list of `Connector(sent, start, end, text, cls, kind)` named tuples. `CohesionStats` computes from the occurrences the connective density per 1000 words - overall, by class and by type.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `words` | list[str] | `-` | Words of the sentence |
| `connectors` | dict[str, tuple[str, str]] | `None` | Connective dictionary - class and type by connective |
| `sent_index` | int | `0` | Sentence number to record in the occurrences |
| `pos` | list[str] | `None` | UD parts of speech of the sentence words; without them parts of speech are not checked |

!!! example "Example"

    ``` python
    from ruts.cohesion_stats import find_connectors

    find_connectors(["Затем", "иными", "словами", "он", "уснул"])
    # [Connector(sent=0, start=0, end=1, text='затем', cls='temporal', kind='primary'),
    #  Connector(sent=0, start=1, end=3, text='иными словами', cls='reformulative', kind='secondary')]
    ```

## Word features { #word_info }

!!! info ""
    **ruts.cohesion_stats.word_info()**, **ruts.cohesion_stats.token_info()**, **ruts.cohesion_stats.WordInfo**

Getting the word features for the cohesion statistics - a `WordInfo` named tuple: lemma, noun, pronoun, demonstrative, argument, content word, tense and aspect. `word_info` takes them from the first pymorphy3 analysis, `token_info` - from the spaCy annotation (`token.pos_`, `Tense`, `Aspect`), and the lemma - from the pymorphy3 analysis with the token's part of speech (`ruts.utils.lemmatize`) rather than from `token.lemma_`: the lemmatizer of the `ru_core_news` models returns the word form for `AUX` and when the tagger's features disagree with pymorphy3 (были, них, стихли). A hyphenated word made of several `Doc` tokens (жили-были, назовите-ка) gets its features from the pymorphy3 analysis of the glued text mapped to UD, so tense and aspect are comparable with the annotation of the other words.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` / `token` | str / Token | `-` | Word or spaCy token |

## Pronoun { #is_pronoun }

!!! info ""
    **ruts.cohesion_stats.is_pronoun()**

Checking whether a word is a pronoun: `NPRO` (он, себя, кто) or `Apro` (этот, который, мой, весь) by pymorphy3 tags.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |

## Content word { #is_content_word }

!!! info ""
    **ruts.cohesion_stats.is_content_word()**

Checking whether a word is a content word: a part of speech from `CONTENT_POS` (nouns, adjectives, verbs in all forms, adverbs) without the `STOPWORD_GRAMMEMES` grammemes (pronominal and parenthetical words).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |
