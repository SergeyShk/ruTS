# Cohesion statistics

``` {.python .signature}
CohesionStats(source, sents_extractor=None, words_extractor=None, connectors=None, blank_lines=False)
```

The cohesion statistics of a text in the manner of [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664) and [TAACO](https://doi.org/10.3758/s13428-015-0651-7): the overlap of the sentences, the givenness, the temporal cohesion and the connectors of a dictionary. The sentences are compared by lemmas. The data source is a text or a `Doc` object of [spaCy](https://github.com/explosion/spaCy).

Raises:

- `SourceTypeError` - a source that is neither a string nor a `Doc`, an extractor of another type, connectors that are not a dictionary of phrases and pairs of strings;
- `SourceError` - a source without words;
- `ParameterError` - an unknown class or kind of a connector, a `blank_lines` that is not a `bool`.

The class extends the `CohesionStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/cohesion_stats/) core with the Russian layer and, unlike the core, reads a string too. A string and a `Doc` without sentence boundaries are split into sentences by the Russian [`SentsExtractor`](../extractors/sentences.md); the words of a string come from the Russian [`WordsExtractor`](../extractors/words.md) or from the `words_extractor` given. For a `Doc` with part-of-speech annotation the part of speech, the tense and the aspect come from `token.pos_` and `token.morph`, and the lemma from the pymorphy3 analysis with the part of speech of the token ([`unit_info`](#word_info)); for a string, a `Doc` without annotation and a `Doc` with a word extractor given, from the first pymorphy3 analysis ([`words_info`](#word_info)), where the answer «нет» is a particle. The parts of a hyphenated word that spaCy splits are joined (`во-первых` is one word). The connectors are found by [`RussianConnectorMatcher`](#ConnectorMatcher) over the dictionary of [`load_connectors`](#connectors). The `print_stats` table and the error messages are in Russian (`COHESION_STATS_DESC` and `CORE_MESSAGES` of `ruts.constants`).

The words are classified by the [pymorphy3](https://github.com/no-plagiarism/pymorphy3) tags or by the Universal Dependencies annotation of a `Doc`:

| Notion | pymorphy3 | Universal Dependencies (`Doc`) |
| :----- | :-------- | :----------------------------- |
| Nouns | `NOUN` | `NOUN`, `PROPN` |
| Pronouns | `NPRO`, `Apro`, lemmas of `DEMONSTRATIVE_LEMMAS` | `PRON`, `DET`, lemmas of `DEMONSTRATIVE_LEMMAS` |
| Arguments | `NOUN`, `NPRO` | `NOUN`, `PROPN`, `PRON` |
| Content words | `CONTENT_POS` without `STOPWORD_GRAMMEMES` and demonstratives | `CONTENT_UD_POS` without demonstratives |
| Demonstratives | lemmas of `DEMONSTRATIVE_LEMMAS`: этот, это, тот, такой, таковой, столько, сей, оный | the same lemmas |
| Tense and aspect | grammemes `past`, `pres`, `futr` and `perf`, `impf` of verb forms, the tense of the existential нет and нету | features `Tense` and `Aspect` |

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

In ruTS both a string and a `Doc` are split into paragraphs. In a poem without blank lines a paragraph is a line of verse; `blank_lines=True` gives the stanzas, as in [`VerseStats`](verse_stats.md), where blank lines set them off.

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

`CohesionStats` of ruTS does not compare the mood: `mood_repetition` is always `nan`, and `temporal_cohesion` is the mean of `tense_repetition` and `aspect_repetition`.

</div>

<div class="metric-card" markdown>

### Connectors { #connectors }

`connectors` · `connectors_inter` · `connectors_intra` · `connectors_<class>` · `connectors_<kind>`
{ .metric-meta }

--8<-- "stats/cohesion_stats.md:CohesionStats-connectors"

``` {.python .signature}
load_connectors()
```

The connector dictionary of ruTS: the file `ruts/resources/connectors.tsv`, 316 connectors with a class of `CONNECTOR_CLASSES` and a kind of `CONNECTOR_TYPES` of `ruts.constants`, compiled after the classification of Krioni, Nikin and Filippova (2008) and checked against the [Ru-RSTreebank](https://rstreebank.ru/markersFull) marker list, the [Ruscon](https://ruslinkers.github.io/) database and the causal marker list of Toldova et al. (2018). The one-word «и», «а», «но» are in the dictionary, as in Coh-Metrix and TAACO; «что» and «как» are no connectors.

| Class | Key | Examples |
| :---- | :-- | :------- |
| Causal (consequential and purposive included) | `causal` | потому что, поэтому, в результате, чтобы, таким образом |
| Adversative | `adversative` | но, однако, зато, с другой стороны, в то же время |
| Concessive | `concessive` | хотя, несмотря на, тем не менее, и всё же, в любом случае |
| Temporal | `temporal` | когда, затем, после того как, тем временем, в дальнейшем |
| Additive | `additive` | и, также, кроме того, более того, например, во-первых |
| Conditional | `conditional` | если, в случае если, при условии что, в противном случае |
| Reformulative | `reformulative` | то есть, иными словами, в общем, подводя итог |

The primary connectors (`primary`) are conjunctions, adverbs and particles (потому что, однако, затем), the secondary ones (`secondary`) lexicalized phrases with nouns and verbs (в результате этого, с другой стороны, иными словами). The rules by which a word of the dictionary counts as a connector are those of the [matcher](#ConnectorMatcher).

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

The methods `get_stats`, `to_dataframe`, `print_stats` and `describe` are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the cohesion statistics have no scales, so `describe` gives `None` for the statistics of `get_stats`.

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

`CohesionStats` computes with it the overlaps of the nouns and of the arguments without the proportional ones, and those of the content words with them.

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

`RussianConnectorMatcher` is a subclass of the core `ConnectorMatcher` with the rules of Russian. Words and connectors are compared in lower case without the letter ё and stress marks (`normalize_yo`). A one-word connector takes a part of speech of the core `CONNECTOR_POS` (`CCONJ`, `SCONJ`, `PART`, `ADV`, `ADP`, `INTJ`, `X`) or of `CONNECTOR_POS_EXTRA` for its form (for example: словом - `NOUN`, главное - `ADJ`, `NOUN`, допустим - `VERB`, точнее - `ADJ`, т.е. - `PUNCT`, значит - `VERB`, ежели and коли - `NOUN`, `PROPN`, `VERB`): «раз» as a noun is no connector. The context rules are lists of `ruts.constants`: words after a connector (`CONNECTOR_BLOCKED_AFTER`: *пока что*, *хоть бы*) and before it (`CONNECTOR_BLOCKED_BEFORE`: *ещё раз*, *и так далее*) that make it no connector; connectors that count inside a sentence only after particular words (`CONNECTOR_ONLY_AFTER`: *и отсюда*) and do not count at its start (`CONNECTOR_NOT_AT_START`: the interrogative *отчего*); parts of speech of the word after a connector that make it a preposition or a member of the clause (`CONNECTOR_BLOCKED_AFTER_POS`: *после обеда*, *едва заметный*). The rules read through a punctuation mark only for `CONNECTOR_READ_THROUGH_MARKS` (*не знал, отчего*), so the parenthetical *значит,* stays a connector, and a mark between the words of a connector of `CONNECTOR_SPLIT_BY_MARKS` splits it (*так, как*). These parts of speech and lists are attributes of the matcher: `CONNECTOR_POS` is `pos_tags`, the others are named without `CONNECTOR_` in lower case (`CONNECTOR_BLOCKED_AFTER` is `blocked_after`); the attributes `not_after_pos` and `start_only_pos` are empty in ruTS, so these rules of `find` do not apply.

--8<-- "stats/cohesion_stats.md:ConnectorMatcher-find"

--8<-- "stats/cohesion_stats.md:ConnectorMatcher-is_subordinator"

The subordinators of ruTS besides the one-word ones tagged `SCONJ` and `ADP` are `CONNECTOR_SUBORDINATORS`: the multi-word conjunctions and prepositions (*так как*, *после того как*, *несмотря на*) and the one-word ones the spaCy models or pymorphy3 tag otherwise (*ежели*, *коли*, *пока*, *раз*, *хоть*, *едва*). A conjunction of `CONNECTOR_PARCELLATION` (*ибо*) opening a sentence attaches it to the one before, so it is no subordinator.

## Connector search { #find_connectors }

``` {.python .signature}
find_connectors(words, connectors=None, sent_index=0, pos=None, breaks=None)
```

Searches a sentence for connectors with the `find` method of `RussianConnectorMatcher` over the dictionary `connectors`, that of `load_connectors` by default; the other parameters and the errors are those of the matcher and of `find`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `connectors` | `dict[str, tuple[str, str]]` | `None` | Class and kind by connector |

``` {.python .signature}
connector_pos(word)
```

The UD part of speech of a word by pymorphy3 for the check of a connector: the first analysis with a part of speech that suits a connector (`CONNECTOR_POS` or `CONNECTOR_POS_EXTRA` for the word), otherwise the first analysis. This is how `CohesionStats` gets the parts of speech of a string and of a `Doc` without annotation.

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
words_info(sents, text)
```

``` {.python .signature}
token_info(token)
```

``` {.python .signature}
ud_info(word, pos, tense, aspect)
```

``` {.python .signature}
unit_info(unit)
```

The features of a word for the cohesion statistics, a `WordInfo` named tuple: `lemma`, `noun`, `pronoun`, `demonstrative`, `argument`, `content`, `tense` and `aspect` after the table of the classes of words. `word_info` takes them from the first pymorphy3 analysis; `words_info` does the same for the words of the sentences of a text, where the answer «нет» (Нет, не видел) is a particle without tense. `token_info` takes them from the spaCy annotation (`token.pos_`, `Tense`, `Aspect`), `ud_info` from a given part of speech, tense and aspect of UD; the lemma comes from the pymorphy3 analysis with that part of speech (`ruts.utils.lemmatize`), not from `token.lemma_`. `unit_info` gives the features of a word from its tokens: a single token by `token_info`, a hyphenated word of several tokens (жили-были, назовите-ка) by the pymorphy3 analysis of the joined text mapped to UD (`word_to_ud`).

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word (`word_info`, `ud_info`) |
| `sents` | `list[list[str]]` | - | Words of the sentences of a text (`words_info`) |
| `text` | `str` | - | Text the words are extracted from (`words_info`) |
| `token` | `Token` | - | spaCy token (`token_info`) |
| `pos`, `tense`, `aspect` | `str` | - | Part of speech, tense and aspect of UD (`ud_info`) |
| `unit` | `list[Token]` | - | Tokens of a word (`unit_info`) |

=== "Code"

    ``` python
    from ruts.cohesion_stats import word_info

    word_info("смотрел")
    ```

=== "Result"

    ```
    WordInfo(lemma='смотреть', noun=False, pronoun=False, demonstrative=False, argument=False, content=True, tense='past', aspect='impf')
    ```

## Words of a Doc { #split_doc_units }

--8<-- "utils/spacy.md:split_doc_units"

`CohesionStats` always joins the parts of hyphenated words, the function only with `join_hyphens=True`.

``` {.python .signature}
unit_text(unit)
```

``` {.python .signature}
unit_pos(unit)
```

`unit_text` gives the text of a word from its tokens without a byte order mark, stress marks and soft hyphens (`ruts.utils.strip_marks`), `unit_pos` its part of speech of UD: that of the token for a single token, and that of `connector_pos` of the joined text for a hyphenated word of several tokens.

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

Checks whether a word is a pronoun by the pymorphy3 tags: `NPRO` (он, себя, кто) or `Apro` (этот, который, мой, весь).

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word |

## Content word { #is_content_word }

``` {.python .signature}
is_content_word(word)
```

Checks whether a word is a content word by the pymorphy3 tags: a part of speech of `CONTENT_POS` (nouns, adjectives, verbs in all forms, adverbs) without the grammemes of `STOPWORD_GRAMMEMES` (pronominal and parenthetical words).

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word |
