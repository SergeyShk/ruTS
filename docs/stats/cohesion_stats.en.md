# Cohesion statistics

!!! info ""
    **ruts.cohesion_stats.CohesionStats**

## Description

The cohesion statistics of a text in the manner of [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664) and [TAACO](https://doi.org/10.3758/s13428-015-0651-7): the overlap of nouns, arguments (nouns and pronouns) and content words between adjacent and between all pairs of sentences; givenness - the share of pronouns, the pronoun-to-noun ratio, the share of demonstratives and the share of content words already seen in the text; temporal cohesion - the repetition of the tense and aspect of the verbs of adjacent sentences; the density of connectors by class and type per 1000 words. Sentences are compared by lemmas. The data source can be either a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

The words are classified by the [pymorphy3](https://github.com/no-plagiarism/pymorphy3) tags or by the Universal Dependencies annotation of a `Doc`:

| Notion | pymorphy3 | Universal Dependencies (`Doc`) |
| :----- | :-------- | :----------------------------- |
| Nouns | `NOUN` | `NOUN`, `PROPN` |
| Pronouns | `NPRO`, `Apro`, lemmas from `DEMONSTRATIVE_LEMMAS` | `PRON`, `DET`, lemmas from `DEMONSTRATIVE_LEMMAS` |
| Arguments | `NOUN`, `NPRO` | `NOUN`, `PROPN`, `PRON` |
| Content words | `CONTENT_POS` without `STOPWORD_GRAMMEMES` and demonstratives | `CONTENT_UD_POS` without demonstratives |
| Demonstratives | lemmas from `DEMONSTRATIVE_LEMMAS`: этот, это, тот, такой, таковой, столько, сей, оный | the same lemmas |
| Tense and aspect | grammemes `past`, `pres`, `futr` and `perf`, `impf` of verb forms, the tense of the existential нет and нету | features `Tense` and `Aspect` |

Connectors are searched in every sentence by the dictionary `ruts/resources/connectors.tsv` (317 entries, see [`find_connectors`](cohesion_stats_funcs.md#find_connectors)); your own dictionary is passed with the `connectors` parameter. A one-word connector counts only with a part of speech from `CONNECTOR_POS` (conjunction, particle, adverb, preposition, interjection) or from `CONNECTOR_POS_EXTRA` for particular words (словом, главное, допустим, точнее): «раз» as a noun and «значит» as a verb do not count. The part of speech is taken from the `Doc` annotation; without it a word passes if a suitable part of speech appears in at least one pymorphy3 analysis. Classes after Krioni, Nikin and Filippova (2008):

| Class | Key | Examples |
| :---- | :-- | :------- |
| Causal (including consequential and purposive) | `causal` | потому что, поэтому, в результате, чтобы, таким образом |
| Adversative | `adversative` | но, однако, зато, с другой стороны, в то же время |
| Concessive | `concessive` | хотя, несмотря на, тем не менее, и всё же, в любом случае |
| Temporal | `temporal` | когда, затем, после того как, тем временем, в дальнейшем |
| Additive | `additive` | и, также, кроме того, более того, например, во-первых |
| Conditional | `conditional` | если, в случае если, при условии что, в противном случае |
| Reformulative | `reformulative` | то есть, иными словами, в общем, подводя итог |

Connector type: primary - conjunctions, adverbs and particles (потому что, однако, затем), secondary - lexicalized phrases with nouns and verbs (в результате этого, с другой стороны, иными словами).

!!! note "Note"
    The statistics are computed when the `CohesionStats` object is initialized.

## Language hooks

The class extends the `CohesionStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/cohesion_stats/) core with the Russian layer. `analyze` reads a string as well as a `Doc`: for a `Doc` with part-of-speech annotation the parts of speech, tense and aspect come from `token.pos_` and `token.morph`, and the lemma from the pymorphy3 analysis with the part of speech of the token ([`unit_info`](cohesion_stats_funcs.md#word_info)); for a string, a `Doc` without annotation and a `Doc` with a word extractor given, from the first pymorphy3 analysis ([`words_info`](cohesion_stats_funcs.md#word_info)), where the answer «нет» is a particle. The parts of a hyphenated word that spaCy splits are joined (`join_hyphens = True`, `во-первых` is one word). A string and a `Doc` without sentence boundaries are split into sentences by the Russian [`SentsExtractor`](../extractors/sentences.md) (`sents_extractor_class`); the words of a string come from the Russian [`WordsExtractor`](../extractors/words.md) or from the `words_extractor` given, a parameter the core does not have. The connectors come from the dictionary of `load_connectors` and are found by `RussianConnectorMatcher` ([`find_connectors`](cohesion_stats_funcs.md#find_connectors)), the core `ConnectorMatcher` with the Russian normalization of words and parts of speech. The `print_stats` table has Russian headers and the descriptions of `ruts.constants.COHESION_STATS_DESC`, the error messages are in Russian (`CORE_MESSAGES`).

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `sents_extractor` | SentsExtractor | `None` | Sentence extraction tool; when given, it is applied to the text of a Doc too |
| `words_extractor` | WordsExtractor | `None` | Word extraction tool; when given, it is applied to the text of a Doc too |
| `connectors` | dict[str, tuple[str, str]] | `None` | Connector dictionary - class and type by connector; if not given, the dictionary from `resources` is used |

A source that is neither a string nor a `Doc`, an extractor of another type and connectors that are not a dictionary of phrases and pairs of strings raise `SourceTypeError`; a source without words raises `SourceError`, and an unknown class or type of a connector `ParameterError`.

## Attributes

--8<-- "stats/cohesion_stats.md:CohesionStats-attributes"

`CohesionStats` of ruTS does not compare the mood: `mood_repetition` is always `nan` and is not in `get_stats`, and `temporal_cohesion` is the mean of `tense_repetition` and `aspect_repetition`. The extractors given are kept as attributes:

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `sents_extractor` | SentsExtractor | Sentence extraction tool given, `None` without it |
| `words_extractor` | WordsExtractor | Word extraction tool given, `None` without it |

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

--8<-- "stats/stats.md:Stats-print_stats"

To illustrate the method, we reuse the code from the `get_stats` example:

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
    Повтор существительных в соседних предложениях           |   0.33
    Повтор существительных во всех парах предложений         |   0.50
    Повтор аргументов в соседних предложениях                |   0.33
    Повтор аргументов во всех парах предложений              |   0.67
    Повтор знаменательных слов в соседних предложениях       |   0.33
    Повтор знаменательных слов во всех парах предложений     |   0.50
    Доля общих знаменательных слов в соседних предложениях   |   0.11
    Доля общих знаменательных слов во всех парах предложений |   0.19
    Доля местоимений                                         |   0.14
    Отношение местоимений к существительным                  |   0.50
    Доля указательных местоимений                            |   0.05
    Доля знаменательных слов, встречавшихся ранее            |   0.29
    Повтор времени в соседних предложениях                   |   0.67
    Повтор вида в соседних предложениях                      |   0.33
    Темпоральная связность                                   |   0.50
    Коннекторов на 1000 слов                                 |  47.62
    Причинных коннекторов на 1000 слов                       |   0.00
    Противительных коннекторов на 1000 слов                  |   0.00
    Уступительных коннекторов на 1000 слов                   |   0.00
    Временных коннекторов на 1000 слов                       |   0.00
    Аддитивных коннекторов на 1000 слов                      |  47.62
    Условных коннекторов на 1000 слов                        |   0.00
    Переформулирующих коннекторов на 1000 слов               |   0.00
    Первичных коннекторов на 1000 слов                       |  47.62
    Вторичных коннекторов на 1000 слов                       |   0.00
    ```

### to_dataframe, describe

The `to_dataframe` method (the statistics as a one-row `pandas.DataFrame`) and the `describe` method are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the cohesion statistics have no scales, so `describe` always gives `None`.
