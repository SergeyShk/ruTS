# Statistic functions

The functions of the overlaps, the givenness and the repetitions come from the [anyTS](https://sergeyshk.github.io/anyTS/stats/cohesion_stats_funcs/) core and take the elements of every sentence (lemmas or values of a feature of the verbs) in the order of the text; the features of the words and the dictionary of the connectors are those of ruTS, and the connectors are found by the matcher of the core with the Russian hooks (`RussianConnectorMatcher`). The names of the [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664) indices are given in parentheses.

--8<-- "stats/cohesion_stats_funcs.md:cohesion-checks"

## Binary overlap { #calc_overlap }

!!! info ""
    **ruts.cohesion_stats.calc_overlap()**

--8<-- "stats/cohesion_stats_funcs.md:calc_overlap"

Formula:

$$
\frac{|\{(i, j): S_i \cap S_j \neq \varnothing\}|}{|\{(i, j)\}|}
$$

where $S_i$ is the set of elements of sentence $i$, the pairs $(i, j)$ are adjacent or all.

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
    **ruts.cohesion_stats.calc_proportional_overlap()**, **ruts.cohesion_stats.dice()**

--8<-- "stats/cohesion_stats_funcs.md:calc_proportional_overlap"

### dice

--8<-- "stats/cohesion_stats_funcs.md:dice"

## All overlaps in one pass { #calc_overlaps }

!!! info ""
    **ruts.cohesion_stats.calc_overlaps()**, **ruts.cohesion_stats.Overlap**

--8<-- "stats/cohesion_stats_funcs.md:calc_overlaps"

`CohesionStats` computes with it the overlaps of the nouns and of the arguments without the proportional ones, and those of the content words with them.

## Givenness { #count_given }

!!! info ""
    **ruts.cohesion_stats.count_given()**

--8<-- "stats/cohesion_stats_funcs.md:count_given"

`CohesionStats` divides the number of given content words by their total (`p_given`); the share of pronouns `p_pronouns`, the pronoun-to-noun ratio `pronoun_noun_ratio` and the share of demonstratives `p_demonstratives` are computed from the class counters.

## Tense and aspect repetition { #calc_repetition }

!!! info ""
    **ruts.cohesion_stats.calc_repetition()**, **ruts.cohesion_stats.dominant()**

--8<-- "stats/cohesion_stats_funcs.md:calc_repetition"

`CohesionStats` computes `tense_repetition`, `aspect_repetition` and their mean `temporal_cohesion`.

### dominant

--8<-- "stats/cohesion_stats_funcs.md:dominant"

## Connectors { #find_connectors }

!!! info ""
    **ruts.cohesion_stats.find_connectors()**, **ruts.cohesion_stats.load_connectors()**, **ruts.cohesion_stats.RussianConnectorMatcher**, **ruts.cohesion_stats.Connector**, **ruts.cohesion_stats.connector_pos()**

--8<-- "stats/cohesion_stats_funcs.md:ConnectorMatcher"

ruTS searches with `RussianConnectorMatcher`, a subclass of the core `ConnectorMatcher`: words and connectors are compared in lower case without ё and stress marks (`normalize_yo`), a one-word connector takes a part of speech of `CONNECTOR_POS` (`CCONJ`, `SCONJ`, `PART`, `ADV`, `ADP`, `INTJ`, `X`) or of `CONNECTOR_POS_EXTRA` for its form (словом - `NOUN`, главное - `ADJ`, `NOUN`, допустим - `VERB`, точнее - `ADJ`, т.е. - `PUNCT`, значит - `VERB`, ежели and коли - `NOUN`, `PROPN`, `VERB`). The subordinating conjunctions and prepositions that open the subordinate clause or the prepositional phrase of a sentence when they open it, besides the one-word ones tagged `SCONJ` and `ADP`, are `CONNECTOR_SUBORDINATORS`: the multi-word ones (*так как*, *после того как*, *несмотря на*) and one-word ones the spaCy models or pymorphy3 tag otherwise (*ежели*, *коли*, *пока*, *раз*, *хоть*, *едва*); *ибо* opening a sentence attaches it to the one before (`CONNECTOR_PARCELLATION`). The context rules of the core are lists of `ruts.constants`: words after a connector (`CONNECTOR_BLOCKED_AFTER`: *пока что*, *хоть бы*) and before it (`CONNECTOR_BLOCKED_BEFORE`: *ещё раз*, *и так далее*) that make it no connector, connectors that count inside a sentence only after particular words (`CONNECTOR_ONLY_AFTER`: *и отсюда*) and do not count at its start (`CONNECTOR_NOT_AT_START`: the interrogative *отчего*), parts of speech of the word after a connector that make it a preposition or a member of the clause (`CONNECTOR_BLOCKED_AFTER_POS`: *после обеда*, *едва заметный*). The rules read through a punctuation mark only for `CONNECTOR_READ_THROUGH_MARKS` (*не знал, отчего*), and a mark between the words of a connector of `CONNECTOR_SPLIT_BY_MARKS` splits it (*так, как*). The dictionary `load_connectors()` reads `ruts/resources/connectors.tsv` - 316 connectors with a class from `CONNECTOR_CLASSES` and a type from `CONNECTOR_TYPES` of `ruts.constants`, compiled after the classification of Krioni, Nikin and Filippova (2008) and checked against the [Ru-RSTreebank](https://rstreebank.ru/markersFull) marker list, the [Ruscon](https://ruslinkers.github.io/) database and the causal marker list of Toldova et al. (2018). The one-word «и», «а», «но» are in the dictionary, as in Coh-Metrix and TAACO; «что» and «как» are not connectors.

`find_connectors(words, connectors, sent_index, pos, breaks)` searches a sentence with the `find` method of `RussianConnectorMatcher` over the dictionary `connectors` (class and type by connector), that of `load_connectors` by default:

--8<-- "stats/cohesion_stats_funcs.md:ConnectorMatcher-find"

`CohesionStats` passes the parts of speech of the `Doc` annotation, and for a string and a `Doc` without annotation those of `connector_pos(word)`: the first pymorphy3 analysis with a part of speech that suits a connector (`CONNECTOR_POS` or `CONNECTOR_POS_EXTRA` for the word), otherwise the first analysis. It computes from the occurrences the connector density per 1000 words - overall, by class and by type.

!!! example "Example"

    ``` python
    from ruts.cohesion_stats import find_connectors

    find_connectors(["Затем", "иными", "словами", "он", "уснул"])
    # [Connector(sent=0, start=0, end=1, text='затем', cls='temporal', kind='primary'),
    #  Connector(sent=0, start=1, end=3, text='иными словами', cls='reformulative', kind='secondary')]
    find_connectors(["Раз", "он", "пришел"])
    # [Connector(sent=0, start=0, end=1, text='раз', cls='conditional', kind='primary')]
    find_connectors(["Раз", "он", "пришел"], pos=["NOUN", "PRON", "VERB"])
    # []
    ```

## Word features { #word_info }

!!! info ""
    **ruts.cohesion_stats.word_info()**, **ruts.cohesion_stats.words_info()**, **ruts.cohesion_stats.token_info()**, **ruts.cohesion_stats.ud_info()**, **ruts.cohesion_stats.unit_info()**, **ruts.cohesion_stats.WordInfo**

Getting the features of a word for the cohesion statistics - a `WordInfo` named tuple: `lemma`, `noun`, `pronoun`, `demonstrative`, `argument`, `content`, `tense` and `aspect`, as defined in the table of the [class page](cohesion_stats.md). `word_info` takes them from the first pymorphy3 analysis; `words_info` does the same for the words of the sentences of a text, where the answer «нет» (Нет, не видел) is a particle without tense. `token_info` takes them from the spaCy annotation (`token.pos_`, `Tense`, `Aspect`), `ud_info` from a given part of speech, tense and aspect of UD; the lemma comes from the pymorphy3 analysis with that part of speech (`ruts.utils.lemmatize`), not from `token.lemma_`. `unit_info` gives the features of a word from its tokens: a single token by `token_info`, a hyphenated word of several tokens (жили-были, назовите-ка) by the pymorphy3 analysis of the joined text mapped to UD (`word_to_ud`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word (`word_info`, `ud_info`) |
| `sents` | list[list[str]] | `-` | Words of the sentences of a text (`words_info`) |
| `text` | str | `-` | Text the words are extracted from (`words_info`) |
| `token` | Token | `-` | spaCy token (`token_info`) |
| `pos`, `tense`, `aspect` | str | `-` | Part of speech, tense and aspect of UD (`ud_info`) |
| `unit` | list[Token] | `-` | Tokens of a word (`unit_info`) |

!!! example "Example"

    ``` python
    from ruts.cohesion_stats import word_info

    word_info("смотрел")
    # WordInfo(lemma='смотреть', noun=False, pronoun=False, demonstrative=False, argument=False, content=True, tense='past', aspect='impf')
    ```

## Words of a Doc { #split_doc_units }

!!! info ""
    **ruts.cohesion_stats.split_doc_units()**, **ruts.cohesion_stats.unit_text()**, **ruts.cohesion_stats.unit_pos()**

--8<-- "utils/spacy.md:split_doc_units"

`CohesionStats` joins the parts of hyphenated words (`во-первых` is one word), the function only with `join_hyphens=True`. `unit_text(unit)` gives the text of a word from its tokens without a byte order mark, stress marks and soft hyphens (`ruts.utils.strip_marks`), `unit_pos(unit)` its part of speech of UD: that of the token for a single token, and that of `connector_pos` of the joined text for a hyphenated word of several tokens.

!!! example "Example"

    ``` python
    import spacy
    from ruts import SentsExtractor
    from ruts.cohesion_stats import split_doc_units, unit_text

    doc = spacy.blank("ru")("Жили-были дед да баба. Во-первых, кот спит.")
    units = split_doc_units(doc, SentsExtractor())
    [[unit_text(unit) for unit in sent] for sent in units]
    # [['Жили', 'были', 'дед', 'да', 'баба'], ['Во', 'первых', 'кот', 'спит']]
    units = split_doc_units(doc, SentsExtractor(), join_hyphens=True)
    [[unit_text(unit) for unit in sent] for sent in units]
    # [['Жили-были', 'дед', 'да', 'баба'], ['Во-первых', 'кот', 'спит']]
    ```

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
