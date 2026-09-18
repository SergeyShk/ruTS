# Cohesion statistics

!!! info ""
    **ruts.cohesion_stats.CohesionStats**

## Description

A module for computing text cohesion statistics modeled on [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664) and [TAACO](https://doi.org/10.3758/s13428-015-0651-7): overlap of nouns, arguments (nouns and pronouns) and content words between adjacent sentences and all sentence pairs; givenness - the share of pronouns, the pronoun-to-noun ratio, the share of demonstratives and the share of content words already seen in the text; temporal cohesion - repetition of verb tense and aspect in adjacent sentences; connective density by class and type per 1000 words. The data source can be either a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

Sentence pairs are compared by lemmas. For a `Doc` object with part-of-speech annotation, parts of speech, tense and aspect are taken from `token.pos_` and `token.morph`, the lemma - from the pymorphy3 analysis with the token's part of speech (`ruts.utils.lemmatize`): the lemmatizer of the `ru_core_news` models returns the word form for `AUX` and when the tagger's features disagree with pymorphy3 (были, них, стихли). For a string and a `Doc` without annotation the first [pymorphy3](https://github.com/no-plagiarism/pymorphy3) analysis is used. `Doc` words are taken from the tokens (hyphenated words split by spaCy are glued back); a `Doc` without sentence boundaries is split into sentences by `SentsExtractor` over the text, a word belongs to a sentence by the position of its first token.

| Notion | pymorphy3 | Universal Dependencies (`Doc`) |
| :----- | :-------- | :----------------------------- |
| Nouns | `NOUN` | `NOUN`, `PROPN` |
| Pronouns | `NPRO`, `Apro`, lemmas from `DEMONSTRATIVE_LEMMAS` | `PRON`, `DET`, lemmas from `DEMONSTRATIVE_LEMMAS` |
| Arguments | `NOUN`, `NPRO` | `NOUN`, `PROPN`, `PRON` |
| Content words | `CONTENT_POS` without `STOPWORD_GRAMMEMES` and demonstratives | `CONTENT_UD_POS` without demonstratives |
| Demonstratives | lemmas from `DEMONSTRATIVE_LEMMAS`: этот, это, тот, такой, таковой, столько, сей, оный | the same lemmas |
| Tense and aspect | grammemes `past`, `pres`, `futr` and `perf`, `impf` | features `Tense` and `Aspect` |

The overlap indicators range from 0 to 1; for a one-sentence text they are `nan`, as is the temporal cohesion of a text without verbs in adjacent sentences. All-pair overlaps are computed without enumerating pairs, see [`calc_overlaps`](cohesion_stats_funcs.md#calc_overlaps).

Connectives are searched by word forms in every sentence using the `ruts/resources/connectors.tsv` dictionary (317 entries, see [`find_connectors`](cohesion_stats_funcs.md#find_connectors)); your own dictionary is passed with the `connectors` parameter. A single-word connective counts only with a part of speech from `CONNECTOR_POS` (conjunction, particle, adverb, preposition, interjection) or from `CONNECTOR_POS_EXTRA` for particular words (словом, главное, допустим, точнее): «раз» as a noun and «значит» as a verb do not count. The part of speech is taken from the `Doc` annotation; without annotation a word passes if a suitable part of speech appears in at least one pymorphy3 analysis (`connector_pos`): for «раз» the first analysis is a noun, the conjunction comes only in the following ones. Classes after Krioni, Nikin and Filippova (2008):

| Class | Key | Examples |
| :---- | :-- | :------- |
| Causal (including consequential and purposive) | `causal` | потому что, поэтому, в результате, чтобы, таким образом |
| Adversative | `adversative` | но, однако, зато, с другой стороны, в то же время |
| Concessive | `concessive` | хотя, несмотря на, тем не менее, и всё же, в любом случае |
| Temporal | `temporal` | когда, затем, после того как, тем временем, в дальнейшем |
| Additive | `additive` | и, также, кроме того, более того, например, во-первых |
| Conditional | `conditional` | если, в случае если, при условии что, в противном случае |
| Reformulative | `reformulative` | то есть, иными словами, в общем, подводя итог |

Connective type: primary - conjunctions, adverbs and particles (потому что, однако, затем), secondary - lexicalized phrases with nouns and verbs (в результате этого, с другой стороны, иными словами).

!!! note "Note"
    The statistics are computed when the `CohesionStats` object is initialized.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `sents_extractor` | SentsExtractor | `None` | Sentence extraction tool |
| `words_extractor` | WordsExtractor | `None` | Word extraction tool |
| `connectors` | dict[str, tuple[str, str]] | `None` | Connective dictionary - class and type by connective; if not given, the dictionary from `resources` is used |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `words` | tuple[tuple[str, ...], ...] | Tuple of the words of each sentence |
| `lemmas` | tuple[tuple[str, ...], ...] | Tuple of the lemmas of each sentence |
| `n_sents` | int | Number of sentences containing words |
| `n_words` | int | Number of words |
| `n_nouns` | int | Number of nouns |
| `n_pronouns` | int | Number of pronouns |
| `n_demonstratives` | int | Number of demonstrative pronouns |
| `n_content_words` | int | Number of content words |
| `n_given` | int | Number of content words whose lemma occurred earlier |
| `n_connectors` | int | Number of connectives |
| `connector_spans` | tuple[Connector] | Tuple of connective occurrences: sentence number, boundaries, connective, class, type |
| `c_connectors` | dict[str, int] | Distribution of occurrences by connective |
| `noun_overlap_adjacent` | float | Share of adjacent sentence pairs sharing a noun |
| `noun_overlap_all` | float | Share of all sentence pairs sharing a noun |
| `argument_overlap_adjacent` | float | Share of adjacent sentence pairs sharing a noun or pronoun |
| `argument_overlap_all` | float | Share of all sentence pairs sharing a noun or pronoun |
| `content_overlap_adjacent` | float | Share of adjacent sentence pairs sharing a content word |
| `content_overlap_all` | float | Share of all sentence pairs sharing a content word |
| `content_overlap_prop_adjacent` | float | Mean share of shared content words in adjacent sentences |
| `content_overlap_prop_all` | float | Mean share of shared content words in all sentence pairs |
| `p_pronouns` | float | Share of pronouns among words |
| `pronoun_noun_ratio` | float | Ratio of pronouns to nouns |
| `p_demonstratives` | float | Share of demonstrative pronouns among words |
| `p_given` | float | Share of content words whose lemma occurred earlier in the text |
| `tense_repetition` | float | Share of adjacent sentence pairs with the same dominant tense |
| `aspect_repetition` | float | Share of adjacent sentence pairs with the same dominant aspect |
| `temporal_cohesion` | float | Mean of tense and aspect repetition |
| `connectors` | float | Connectives per 1000 words |
| `connectors_causal` | float | Causal connectives per 1000 words |
| `connectors_adversative` | float | Adversative connectives per 1000 words |
| `connectors_concessive` | float | Concessive connectives per 1000 words |
| `connectors_temporal` | float | Temporal connectives per 1000 words |
| `connectors_additive` | float | Additive connectives per 1000 words |
| `connectors_conditional` | float | Conditional connectives per 1000 words |
| `connectors_reformulative` | float | Reformulative connectives per 1000 words |
| `connectors_primary` | float | Primary connectives per 1000 words |
| `connectors_secondary` | float | Secondary connectives per 1000 words |

!!! note "Note"
    Every statistic can be computed separately by calling the corresponding function. Detailed information on the cohesion statistics and the functions used to compute them is available in the corresponding [section](cohesion_stats_funcs.md).

## Methods

### get_stats

Returns a dictionary with the computed cohesion statistics.

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts import CohesionStats

    # Prepare the data
    text = "Кот сидел на окне. Он смотрел на птиц. Птицы улетели, и кот уснул. Завтра он снова будет сидеть на этом окне."

    # Compute the statistics
    cs = CohesionStats(text)
    cs.get_stats()
    ```

    _Result_:

    ``` bash
    {'noun_overlap_adjacent': 0.3333333333333333,
    'noun_overlap_all': 0.5,
    'argument_overlap_adjacent': 0.3333333333333333,
    'argument_overlap_all': 0.6666666666666666,
    'content_overlap_adjacent': 0.3333333333333333,
    'content_overlap_all': 0.5,
    'content_overlap_prop_adjacent': 0.1111111111111111,
    'content_overlap_prop_all': 0.18650793650793648,
    'p_pronouns': 0.14285714285714285,
    'pronoun_noun_ratio': 0.5,
    'p_demonstratives': 0.047619047619047616,
    'p_given': 0.2857142857142857,
    'tense_repetition': 0.6666666666666666,
    'aspect_repetition': 0.3333333333333333,
    'temporal_cohesion': 0.5,
    'connectors': 47.61904761904762,
    'connectors_causal': 0.0,
    'connectors_adversative': 0.0,
    'connectors_concessive': 0.0,
    'connectors_temporal': 0.0,
    'connectors_additive': 47.61904761904762,
    'connectors_conditional': 0.0,
    'connectors_reformulative': 0.0,
    'connectors_primary': 47.61904761904762,
    'connectors_secondary': 0.0}
    ```

Words, lemmas and counters are available as attributes:

!!! example "Example"

    ``` python
    cs.lemmas[1]
    # ('он', 'смотреть', 'на', 'птица')
    cs.n_nouns, cs.n_pronouns, cs.n_content_words, cs.n_given
    # (6, 3, 14, 4)
    cs.connector_spans
    # (Connector(sent=2, start=2, end=3, text='и', cls='additive', kind='primary'),)
    ```

### print_stats

Prints a table with the computed cohesion statistics.

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed statistics
    cs.print_stats()
    ```

    _Result_:

    ``` bash
                            Статистика                        | Значение
    --------------------------------------------------------------------
    Повтор существительных в соседних предложениях            |   0.33
    Повтор существительных во всех парах предложений          |   0.50
    Повтор аргументов в соседних предложениях                 |   0.33
    Повтор аргументов во всех парах предложений               |   0.67
    Повтор знаменательных слов в соседних предложениях        |   0.33
    Повтор знаменательных слов во всех парах предложений      |   0.50
    Доля общих знаменательных слов в соседних предложениях    |   0.11
    Доля общих знаменательных слов во всех парах предложений  |   0.19
    Доля местоимений                                          |   0.14
    Отношение местоимений к существительным                   |   0.50
    Доля указательных местоимений                             |   0.05
    Доля знаменательных слов, встречавшихся ранее             |   0.29
    Повтор времени в соседних предложениях                    |   0.67
    Повтор вида в соседних предложениях                       |   0.33
    Темпоральная связность                                    |   0.50
    Коннекторов на 1000 слов                                  |  47.62
    Причинных коннекторов на 1000 слов                        |   0.00
    Противительных коннекторов на 1000 слов                   |   0.00
    Уступительных коннекторов на 1000 слов                    |   0.00
    Временных коннекторов на 1000 слов                        |   0.00
    Аддитивных коннекторов на 1000 слов                       |  47.62
    Условных коннекторов на 1000 слов                         |   0.00
    Переформулирующих коннекторов на 1000 слов                |   0.00
    Первичных коннекторов на 1000 слов                        |  47.62
    Вторичных коннекторов на 1000 слов                        |   0.00
    ```
