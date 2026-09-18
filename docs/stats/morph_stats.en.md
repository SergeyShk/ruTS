# Morphological statistics

!!! info ""
    **ruts.morph_stats.MorphStats**

## Description

A module for computing morphological statistics of a text. The data source can be either a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

The module allows using a pre-built [`WordsExtractor`](../extractors/words.md) object for the word tokenization needed before computing the statistics.

Parts of speech and grammatical features are given in [Universal Dependencies](https://universaldependencies.org/u/feat/) terms: `pos` - `NOUN`, `VERB`, `ADJ`, `PRON`, `DET` and others, `case` - `Nom`, `Gen`, `Dat`, `Acc`, `Ins`, `Loc`, likewise `animacy`, `aspect`, `gender`, `mood`, `number`, `person`, `tense`, `voice` and the verb form `verb_form` (`Fin`, `Inf`, `Part`, `Conv`). For a `Doc` object with part-of-speech annotation the values are taken from `token.pos_` and `token.morph`. For a string and a `Doc` without annotation the first [pymorphy3](https://github.com/no-plagiarism/pymorphy3) analysis is used, and the [OpenCorpora](http://opencorpora.org/dict.php?act=gram) grammemes are mapped to UD by the `OPENCORPORA_TO_UD_POS` and `OPENCORPORA_TO_UD_GRAMMEMES` tables of `ruts.constants`.

Correspondence between OpenCorpora and UD parts of speech:

| OpenCorpora | UD | Note |
| :---------- | :- | :--- |
| `NOUN` | `NOUN`, `PROPN` | first names, surnames, patronymics, toponyms and organizations by pymorphy3 tags - `PROPN`, but only for capitalized word forms: pymorphy3 ignores case and tags ordinary words as names (лев, роза, мороз) |
| `ADJF`, `ADJS`, `COMP` | `ADJ`, `DET`, `PRON`, `NUM` | pronominal adjectives (этот, мой, весь) - `DET`, «который» - `PRON`, «один» - `NUM`; a comparative without context counts as an adjective |
| `VERB`, `INFN`, `PRTF`, `PRTS`, `GRND` | `VERB` | the form goes into `verb_form`: `Fin`, `Inf`, `Part`, `Conv`; the auxiliary `AUX` is distinguished only by spaCy |
| `NUMR`, `NUMB`, `ROMN` | `NUM` | |
| `ADVB`, `PRED` | `ADV` | predicatives (надо, нельзя) - adverbs, as in the Russian UD corpora |
| `NPRO` | `PRON` | |
| `PREP` | `ADP` | |
| `CONJ` | `CCONJ`, `SCONJ` | subordinating conjunctions by the `SUBORDINATING_CONJUNCTIONS` list (что, чтобы, если, когда, хотя, потому) |
| `PRCL` | `PART` | |
| `INTJ` | `INTJ` | |
| `LATN`, `UNKN` | `X` | |

Transitivity (`transitivity`: `Tran`, `Intr`) and clusivity (`involvement`: `In`, `Ex`) are OpenCorpora features absent from Russian UD; they are computed via pymorphy3 for verbs (for a `Doc` - from the analysis with the spaCy lemma) and appear in the `tags` feature string as `Subcat` and `Clusivity`.

!!! note "Note"
    Values for a string and for an annotated `Doc` may differ: spaCy assigns `Voice=Act` to finite forms and `Voice=Mid` to reflexive verbs, distinguishes `AUX` and resolves homonymy by context; pymorphy3 determines voice only for participles and takes the first analysis.

!!! note "Note"
    The statistics are computed when the `MorphStats` object is initialized.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `words_extractor` | WordsExtractor | `None` | Word extraction tool |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `words` | tuple[str] | Tuple of extracted words |
| `tags` | tuple[str] | Tuple of grammatical feature strings in CoNLL-U format (`Animacy=Inan\|Case=Nom\|Gender=Masc\|Number=Sing`, `_` without features) |
| `pos` | tuple[str] | Tuple of part-of-speech values |
| `animacy` | tuple[str] | Tuple of animacy values |
| `aspect` | tuple[str] | Tuple of aspect values |
| `case` | tuple[str] | Tuple of case values |
| `gender` | tuple[str] | Tuple of gender values |
| `involvement` | tuple[str] | Tuple of clusivity values |
| `mood` | tuple[str] | Tuple of mood values |
| `number` | tuple[str] | Tuple of number values |
| `person` | tuple[str] | Tuple of person values |
| `tense` | tuple[str] | Tuple of tense values |
| `transitivity` | tuple[str] | Tuple of transitivity values |
| `verb_form` | tuple[str] | Tuple of verb form values |
| `voice` | tuple[str] | Tuple of voice values |

## Methods

### get_stats

Returns a dictionary with the computed morphological statistics.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `args` | tuple[str] | `-` | Selected statistics |
| `filter_none` | bool | `False` | Filter empty values |

!!! warning "Warning"
    To select statistics, pass their names directly to the method separated by commas.

An example of computing morphological statistics, selecting only part of speech, tense, number and person, and filtering empty values:

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts import MorphStats

    # Prepare the data
    text = "Постарайтесь получить то, что любите, иначе придется полюбить то, что получили"

    # Compute the statistics
    ms = MorphStats(text)
    ms.get_stats("pos", "tense", "number", "person", filter_none=True)
    ```

    _Result_:

    ``` bash
    {'number': {'Plur': 3, 'Sing': 1},
    'person': {'2': 1, '3': 1},
    'pos': {'ADV': 1, 'CCONJ': 2, 'SCONJ': 2, 'VERB': 6},
    'tense': {'Fut': 1, 'Past': 1, 'Pres': 1}}
    ```

### print_stats

Prints a table with the computed morphological statistics.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `args` | tuple[str] | `-` | Selected statistics |
| `filter_none` | bool | `False` | Filter empty values |

!!! warning "Warning"
    To select statistics, pass their names directly to the method separated by commas.

To illustrate the method, we reuse the code from the previous example:

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed statistics
    ms.print_stats("pos", "tense", "number", "person", filter_none=True)
    ```

    _Result_:

    ``` bash
    ---------------Часть речи---------------
    Глагол                        |    6
    Сочинительный союз            |    2
    Подчинительный союз           |    2
    Наречие                       |    1

    -----------------Время------------------
    Настоящее                     |    1
    Будущее                       |    1
    Прошедшее                     |    1

    -----------------Число------------------
    Множественное                 |    3
    Единственное                  |    1

    ------------------Лицо------------------
    2                             |    1
    3                             |    1
    ```

### explain_text

Analyzes the text by morphological statistics. Returns a mapping whose keys are the words of the text and whose values are dictionaries of their morphological statistics.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `args` | tuple[str] | `-` | Selected statistics |
| `filter_none` | bool | `False` | Filter empty values |

!!! warning "Warning"
    To select statistics, pass their names directly to the method separated by commas.

To illustrate the method, we reuse the code from the previous example:

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Analyze the text by morphological statistics
    ms.explain_text("pos", "tense", "number", "person", filter_none=True)
    ```

    _Result_:

    ``` bash
    (('Постарайтесь', {'number': 'Plur', 'pos': 'VERB'}),
    ('получить', {'pos': 'VERB'}),
    ('то', {'pos': 'CCONJ'}),
    ('что', {'pos': 'SCONJ'}),
    ('любите', {'number': 'Plur', 'person': '2', 'pos': 'VERB', 'tense': 'Pres'}),
    ('иначе', {'pos': 'ADV'}),
    ('придется', {'number': 'Sing', 'person': '3', 'pos': 'VERB', 'tense': 'Fut'}),
    ('полюбить', {'pos': 'VERB'}),
    ('то', {'pos': 'CCONJ'}),
    ('что', {'pos': 'SCONJ'}),
    ('получили', {'number': 'Plur', 'pos': 'VERB', 'tense': 'Past'}))
    ```
