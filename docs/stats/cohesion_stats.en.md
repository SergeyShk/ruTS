# Cohesion statistics

``` {.python .signature}
CohesionStats(source, sents_extractor=None, words_extractor=None, connectors=None, blank_lines=False)
```

The cohesion statistics of a text in the manner of [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664) and [TAACO](https://doi.org/10.3758/s13428-015-0651-7): the overlap of the sentences, the givenness, the temporal cohesion and the connectors of a dictionary. The sentences are compared by lemmas. The data source is a text or a `Doc` object of [spaCy](https://github.com/explosion/spaCy).

Raises:

- `SourceTypeError` - a source that is neither a string nor a `Doc`, an extractor of another type, connectors that are not a dictionary of phrases and pairs of strings;
- `SourceError` - a source without words;
- `ParameterError` - an unknown class or kind of a connector, a `blank_lines` that is not a `bool`.

The class extends the `CohesionStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/cohesion_stats/) core with the Russian layer. A string and a `Doc` without sentence boundaries are split into sentences by the Russian [`SentsExtractor`](../extractors/sentences.md); the words of a string come from the Russian [`WordsExtractor`](../extractors/words.md) or from the `words_extractor` given, and the parts of a hyphenated word that spaCy splits are joined (`во-первых` is one word). The [features of the words](#word_info) of a string come from the ruMorph analysis in the context of the sentence, those of a `Doc` of the [recommended pipeline](../components.md#load_pipeline) from its ruMorph annotation, and with a plain model the part of speech, the tense and the aspect come from `token.pos_` and `token.morph`, with the lemma by ruMorph. In a `Doc` without annotation the sentences whose words are those of the string are analyzed in context, and the other words, as with a word extractor given, get the first ruMorph analysis. The connectors are found by [`RussianConnectorMatcher`](#ConnectorMatcher) over the dictionary of [`load_connectors`](#connectors). The `print_stats` table and the error messages are in Russian (`COHESION_STATS_DESC` and `CORE_MESSAGES` of `ruts.constants`).

The words are classified by the Universal Dependencies parts of speech and features - of the [ruMorph](https://github.com/SergeyShk/ruMorph) analysis for a string or of the annotation of a `Doc`:

| Notion | String (ruMorph) | `Doc` |
| :----- | :--------------- | :---- |
| Nouns | `NOUN`, `PROPN` | `NOUN`, `PROPN` |
| Pronouns | `PRON`, `DET`, lemmas of `DEMONSTRATIVE_LEMMAS` | `PRON`, `DET`, lemmas of `DEMONSTRATIVE_LEMMAS` |
| Arguments | `NOUN`, `PROPN`, `PRON`, the possessive его, её, их with the lemma он, она, они | the same |
| Content words | `CONTENT_UD_POS` and the copula быть (`AUX` with a verb form) without demonstratives, pronominal (`PronType` Dem, Int, Rel: там, где, почему) and parenthetical (the `Prnt` label and `PARENTHETICAL_WORDS`: кстати, наверно) words, predicatives and numbers in digits | the same by the features of the token |
| Demonstratives | lemmas of `DEMONSTRATIVE_LEMMAS`: этот, это, тот, то (a pronoun only), такой, таковой, столько, сей, оный | the same lemmas |
| Tense and aspect | features `Tense` and `Aspect` | features `Tense` and `Aspect` |

=== "Code"

    ``` python
    from ruts import CohesionStats

    text = "Кот сидел на окне. Он смотрел на птиц. Птицы улетели, и кот уснул. Завтра он снова будет сидеть на этом окне."
    cs = CohesionStats(text)
    cs.print_stats()
    ```

=== "Result"

    ```
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
    Повтор существительных в двух следующих предложениях     |   0.67
    Повтор аргументов в двух следующих предложениях          |   0.75
    Повтор знаменательных слов в двух следующих предложениях |   0.40
    Повтор существительных в соседних абзацах                |   nan
    Повтор аргументов в соседних абзацах                     |   nan
    Повтор знаменательных слов в соседних абзацах            |   nan
    Доля местоимений                                         |   0.14
    Отношение местоимений к существительным                  |   0.50
    Доля указательных местоимений                            |   0.05
    Доля знаменательных слов, встречавшихся ранее            |   0.29
    Повтор времени в соседних предложениях                   |   0.67
    Повтор вида в соседних предложениях                      |   0.33
    Темпоральная связность                                   |   0.50
    Коннекторов на 1000 слов                                 |  47.62
    Межпредложенческих коннекторов на 1000 слов              |   0.00
    Внутрипредложенческих коннекторов на 1000 слов           |  47.62
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

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Data source |
| `sents_extractor` | `SentsExtractor` | `None` | Sentence extraction tool; given, it splits a `Doc` by its text too, whatever its boundaries |
| `words_extractor` | `WordsExtractor` | `None` | Word extraction tool; given, it is applied to the text of a `Doc` too |
| `connectors` | `dict[str, tuple[str, str]]` | `None` | Class and kind by connector; the dictionary of `load_connectors` by default |
| `blank_lines` | `bool` | `False` | Start the paragraphs after the blank lines alone, for a text whose lines are wrapped inside its paragraphs; a paragraph is a line by default |

## Attributes

--8<-- "stats/cohesion_stats.md:CohesionStats-attributes"

The extractors given are kept in the attributes `sents_extractor` and `words_extractor`, `None` without them.

=== "Code"

    ``` python
    cs.lemmas[1]
    cs.n_nouns, cs.n_pronouns, cs.n_content_words, cs.n_given
    cs.connector_spans
    cs.c_connectors
    ```

=== "Result"

    ```
    ('он', 'смотреть', 'на', 'птица')
    (6, 3, 14, 4)
    (Connector(sent=2, start=2, end=3, text='и', cls='additive', kind='primary'),)
    {'и': 1}
    ```

## Metrics

--8<-- "stats/cohesion_stats.md:CohesionStats-metrics"

<div class="metric-card" markdown>

### Binary overlap { #overlap }

`noun_overlap_adjacent` · `noun_overlap_all` · `argument_overlap_adjacent` · `argument_overlap_all` · `content_overlap_adjacent` · `content_overlap_all` · [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664)
{ .metric-meta }

--8<-- "stats/cohesion_stats.md:calc_overlap"

</div>

<div class="metric-card" markdown>

### Proportional overlap { #proportional_overlap }

`content_overlap_prop_adjacent` · `content_overlap_prop_all` · [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664)
{ .metric-meta }

--8<-- "stats/cohesion_stats.md:calc_proportional_overlap"

--8<-- "stats/cohesion_stats.md:dice"

</div>

<div class="metric-card" markdown>

### Overlap with the next sentences and paragraphs { #forward_overlap }

`noun_overlap_2_sent` · `argument_overlap_2_sent` · `content_overlap_2_sent` · `noun_overlap_para` · `argument_overlap_para` · `content_overlap_para` · [TAACO](https://doi.org/10.3758/s13428-015-0651-7)
{ .metric-meta }

--8<-- "stats/cohesion_stats.md:CohesionStats-forward_overlap"

--8<-- "stats/cohesion_stats.md:calc_forward_overlap"

In ruTS both a string and a `Doc` are split into paragraphs. In a poem a paragraph is a line of verse by default, and `blank_lines=True` gives the stanzas set off by blank lines, as in [`VerseStats`](verse_stats.md).

=== "Code"

    ``` python
    from ruts.cohesion_stats import calc_forward_overlap

    calc_forward_overlap([{"кот", "окно"}, {"птица"}, {"кот"}], span=2)
    text = "Кот сидел на окне. Он смотрел на птиц.\nПтицы улетели, и кот уснул. Завтра он снова будет сидеть на этом окне."
    paragraphs = CohesionStats(text)
    paragraphs.n_paragraphs, paragraphs.noun_overlap_para, paragraphs.content_overlap_para
    CohesionStats(text, blank_lines=True).n_paragraphs
    ```

=== "Result"

    ```
    0.5
    (2, 1.0, 0.8)
    1
    ```

</div>

<div class="metric-card" markdown>

### Pronouns and demonstratives { #pronouns }

`p_pronouns` · `pronoun_noun_ratio` · `p_demonstratives`
{ .metric-meta }

--8<-- "stats/cohesion_stats.md:CohesionStats-pronouns"

In ruTS they are marked by the functions of the [word features](#word_info) after the table of the classes of words.

</div>

<div class="metric-card" markdown>

### Givenness { #given }

`p_given`
{ .metric-meta }

--8<-- "stats/cohesion_stats.md:count_given"

</div>

<div class="metric-card" markdown>

### Temporal cohesion { #temporal_cohesion }

`tense_repetition` · `mood_repetition` · `aspect_repetition` · `temporal_cohesion` · [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664)
{ .metric-meta }

--8<-- "stats/cohesion_stats.md:calc_repetition"

--8<-- "stats/cohesion_stats.md:dominant"

ruTS does not compare the mood: `mood_repetition` is always `nan`, and `temporal_cohesion` is the mean of `tense_repetition` and `aspect_repetition`.

</div>

<div class="metric-card" markdown>

### Connectors { #connectors }

`connectors` · `connectors_inter` · `connectors_intra` · `connectors_<class>` · `connectors_<kind>`
{ .metric-meta }

--8<-- "stats/cohesion_stats.md:CohesionStats-connectors"

``` {.python .signature}
load_connectors()
```

The connector dictionary of ruTS: the file `ruts/resources/connectors.tsv`, 316 connectors with a class of `CONNECTOR_CLASSES` and a kind of `CONNECTOR_TYPES` of `ruts.constants`, compiled after the classification of Krioni, Nikin and Filippova (2008) and checked against the [Ru-RSTreebank](https://rstreebank.ru/markersFull) marker list, the [Ruscon](https://ruslinkers.github.io/) database and the causal marker list of Toldova et al. (2018). The one-word «и», «а», «но» are in the dictionary, while «что» and «как» are no connectors.

| Class | Key | Examples |
| :---- | :-- | :------- |
| Causal (consequential and purposive included) | `causal` | потому что, поэтому, чтобы |
| Adversative | `adversative` | но, однако, с другой стороны |
| Concessive | `concessive` | хотя, несмотря на, тем не менее |
| Temporal | `temporal` | когда, затем, после того как |
| Additive | `additive` | и, кроме того, например |
| Conditional | `conditional` | если, при условии что, в противном случае |
| Reformulative | `reformulative` | то есть, иными словами, подводя итог |

The primary connectors (`primary`) are conjunctions, adverbs and particles (потому что, однако), the secondary ones (`secondary`) lexicalized phrases with nouns and verbs (с другой стороны, иными словами). The rules by which a word of the dictionary counts as a connector are those of the [matcher](#ConnectorMatcher).

</div>

--8<-- "stats/cohesion_stats.md:cohesion-checks"

=== "Code"

    ``` python
    from ruts.cohesion_stats import calc_overlap, calc_repetition, count_given

    sets = [{"кот", "окно"}, {"птица"}, {"птица", "кот"}, {"окно"}]
    calc_overlap(sets), calc_overlap(sets, adjacent=False)
    count_given([["кот", "окно"], ["птица"], ["птица", "кот"]])
    calc_repetition([["past"], ["past", "pres", "past"], ["futr"]])
    ```

=== "Result"

    ```
    (0.3333333333333333, 0.5)
    2
    0.5
    ```

## Methods

The methods `get_stats`, `to_dataframe`, `print_stats` and `describe` are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; `describe` gives `None` for the statistics of `get_stats`: the cohesion statistics have no scales.

=== "Code"

    ``` python
    cs.get_stats()
    ```

=== "Result"

    ```
    {'noun_overlap_adjacent': 0.3333333333333333,
     'noun_overlap_all': 0.5,
     'argument_overlap_adjacent': 0.3333333333333333,
     'argument_overlap_all': 0.6666666666666666,
     'content_overlap_adjacent': 0.3333333333333333,
     'content_overlap_all': 0.5,
     'content_overlap_prop_adjacent': 0.1111111111111111,
     'content_overlap_prop_all': 0.18650793650793648,
     'noun_overlap_2_sent': 0.6666666666666666,
     'argument_overlap_2_sent': 0.75,
     'content_overlap_2_sent': 0.4,
     'noun_overlap_para': nan,
     'argument_overlap_para': nan,
     'content_overlap_para': nan,
     'p_pronouns': 0.14285714285714285,
     'pronoun_noun_ratio': 0.5,
     'p_demonstratives': 0.047619047619047616,
     'p_given': 0.2857142857142857,
     'tense_repetition': 0.6666666666666666,
     'aspect_repetition': 0.3333333333333333,
     'temporal_cohesion': 0.5,
     'connectors': 47.61904761904762,
     'connectors_inter': 0.0,
     'connectors_intra': 47.61904761904762,
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

## Overlaps at once { #calc_overlaps }

--8<-- "stats/cohesion_stats.md:calc_overlaps"

=== "Code"

    ``` python
    from ruts.cohesion_stats import calc_overlaps

    calc_overlaps([{"кот", "окно"}, {"птица"}, {"птица", "кот"}, {"окно"}])
    ```

=== "Result"

    ```
    Overlap(adjacent=0.3333333333333333, all=0.5, prop_adjacent=0.2222222222222222, prop_all=0.3055555555555555)
    ```

## Connector matcher { #ConnectorMatcher }

``` {.python .signature}
RussianConnectorMatcher(connectors)
```

--8<-- "stats/cohesion_stats.md:ConnectorMatcher"

`RussianConnectorMatcher` is a subclass of the core `ConnectorMatcher` with the rules of Russian - lists of `ruts.constants` that become attributes of the matcher named without `CONNECTOR_` in lower case (`CONNECTOR_BLOCKED_AFTER` is `blocked_after`, the core `CONNECTOR_POS` is `pos_tags`); the attributes `not_after_pos` and `start_only_pos` are empty in ruTS. Words and connectors are compared in lower case without the letter ё and stress marks. A one-word connector takes a part of speech of `CONNECTOR_POS` (`CCONJ`, `SCONJ`, `PART`, `ADV`, `ADP`, `INTJ`, `X`) or of `CONNECTOR_POS_EXTRA` for its form (словом - `NOUN`, допустим - `VERB`): «раз» as a noun and «значит» as a verb are no connectors. A connector does not count with a word after it of `CONNECTOR_BLOCKED_AFTER` (*пока что*), before it of `CONNECTOR_BLOCKED_BEFORE` (*ещё раз*) or with a part of speech of the next word of `CONNECTOR_BLOCKED_AFTER_POS` (*после обеда*); a connector of `CONNECTOR_ONLY_AFTER` counts inside a sentence only after the words given (*и отсюда*), and one of `CONNECTOR_NOT_AT_START` does not count at its start (the interrogative *отчего*). The rules read through a punctuation mark only for `CONNECTOR_READ_THROUGH_MARKS` (*не знал, отчего*), and a mark between the words of a connector of `CONNECTOR_SPLIT_BY_MARKS` splits it (*так, как*).

--8<-- "stats/cohesion_stats.md:ConnectorMatcher-find"

--8<-- "stats/cohesion_stats.md:ConnectorMatcher-is_subordinator"

The subordinators of ruTS besides the one-word ones tagged `SCONJ` and `ADP` are `CONNECTOR_SUBORDINATORS`: the multi-word conjunctions and prepositions (*так как*, *несмотря на*) and the one-word ones the spaCy models or ruMorph tag otherwise (*ежели*, *пока*). A conjunction of `CONNECTOR_PARCELLATION` (*ибо*) opening a sentence attaches it to the one before and is no subordinator.

## Connector search { #find_connectors }

``` {.python .signature}
find_connectors(words, connectors=None, sent_index=0, pos=None, breaks=None, blocked=None)
```

Searches a sentence for connectors with the `find` method of `RussianConnectorMatcher` over the dictionary `connectors`, that of `load_connectors` by default; the other parameters and the errors are those of the matcher and of `find`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `connectors` | `dict[str, tuple[str, str]]` | `None` | Class and kind by connector |

``` {.python .signature}
connector_pos(word)
```

The UD part of speech of a word by ruMorph for the check of a connector: the first analysis with a part of speech that suits a connector (`CONNECTOR_POS` or `CONNECTOR_POS_EXTRA` for the word), otherwise the first analysis.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word |

=== "Code"

    ``` python
    from ruts.cohesion_stats import find_connectors

    find_connectors(["Затем", "иными", "словами", "он", "уснул"])
    find_connectors(["Раз", "он", "пришел"])
    find_connectors(["Раз", "он", "пришел"], pos=["NOUN", "PRON", "VERB"])
    ```

=== "Result"

    ```
    [Connector(sent=0, start=0, end=1, text='затем', cls='temporal', kind='primary'),
     Connector(sent=0, start=1, end=3, text='иными словами', cls='reformulative', kind='secondary')]
    [Connector(sent=0, start=0, end=1, text='раз', cls='conditional', kind='primary')]
    []
    ```

## Word features { #word_info }

``` {.python .signature}
word_info(word)
```

``` {.python .signature}
words_info(sents, text, analyses=None)
```

``` {.python .signature}
analysis_info(analysis)
```

``` {.python .signature}
token_info(token)
```

``` {.python .signature}
ud_info(word, pos, tense, aspect, feats=None)
```

``` {.python .signature}
unit_info(unit)
```

The features of a word for the cohesion statistics, a `WordInfo` named tuple: `lemma`, `noun`, `pronoun`, `demonstrative`, `argument`, `content`, `tense` and `aspect` after the table of the classes of words. `word_info` takes them from the first ruMorph analysis, `analysis_info` from a given analysis, for example one chosen by context, `words_info` for the words of the sentences of a text: by the analysis of `analyses` when it is given, otherwise by the first one. `token_info` takes them from the ruMorph analysis the token is annotated with (the `rumorph` component), and without it from the spaCy annotation (`token.pos_`, `token.morph`), `ud_info` from a given part of speech, tense, aspect and features of UD; the lemma then comes from the ruMorph analysis with that part of speech, not from `token.lemma_`. `unit_info` gives the features of a word from its tokens: a single token by `token_info`, a hyphenated word of several tokens (жили-были) by the ruMorph analysis of the joined text.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word (`word_info`, `ud_info`) |
| `sents` | `list[list[str]]` | - | Words of the sentences of a text (`words_info`) |
| `text` | `str` | - | Text the words are extracted from (`words_info`) |
| `analyses` | `list[list[Analysis \| None]]` | `None` | Analyses of the words of the sentences, `None` for the analysis by word (`words_info`) |
| `analysis` | `Analysis` | - | ruMorph analysis (`analysis_info`) |
| `token` | `Token` | - | spaCy token (`token_info`) |
| `pos`, `tense`, `aspect` | `str` | - | Part of speech, tense and aspect of UD (`ud_info`) |
| `feats` | `dict[str, str]` | `None` | Features of UD of the word, `None` - unknown (`ud_info`) |
| `unit` | `list[Token]` | - | Tokens of a word (`unit_info`) |

=== "Code"

    ``` python
    from ruts.cohesion_stats import word_info

    word_info("смотрел")
    ```

=== "Result"

    ```
    WordInfo(lemma='смотреть', noun=False, pronoun=False, demonstrative=False, argument=False, content=True, tense='Past', aspect='Imp')
    ```

## Words of a Doc { #split_doc_units }

--8<-- "utils/spacy.md:split_doc_units"

``` {.python .signature}
unit_text(unit)
```

``` {.python .signature}
unit_pos(unit)
```

`unit_text` gives the text of a word from its tokens without a byte order mark, stress marks, soft hyphens and the period of an abbreviation when the word is the same without it, `unit_pos` its part of speech of UD: that of the token for a single token, and that of `connector_pos` of the joined text for a hyphenated word of several tokens.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `unit` | `list[Token]` | - | Tokens of a word |

=== "Code"

    ``` python
    import spacy
    from ruts import SentsExtractor
    from ruts.cohesion_stats import split_doc_units, unit_text

    doc = spacy.blank("ru")("Жили-были дед да баба. Во-первых, кот спит.")
    units = split_doc_units(doc, SentsExtractor())
    [[unit_text(unit) for unit in sent] for sent in units]
    units = split_doc_units(doc, SentsExtractor(), join_hyphens=True)
    [[unit_text(unit) for unit in sent] for sent in units]
    ```

=== "Result"

    ```
    [['Жили', 'были', 'дед', 'да', 'баба'], ['Во', 'первых', 'кот', 'спит']]
    [['Жили-были', 'дед', 'да', 'баба'], ['Во-первых', 'кот', 'спит']]
    ```

## Pronoun { #is_pronoun }

``` {.python .signature}
is_pronoun(word)
```

Checks whether a word is a pronoun by the ruMorph analysis: `PRON` (он, себя, кто) or `DET` (этот, который, мой, весь).

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word |

## Content word { #is_content_word }

``` {.python .signature}
is_content_word(word)
```

Checks whether a word is a content word by the ruMorph analysis: a part of speech of `CONTENT_UD_POS` (nouns, proper nouns, adjectives, verbs in all forms, adverbs) and the copula быть, except pronominal and parenthetical words, predicatives and numbers in digits.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word |
