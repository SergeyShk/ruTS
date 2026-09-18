# SEO style metrics

!!! info ""
    **ruts.style_stats.StyleStats**

## Description

A module for computing SEO metrics of text style and quality that replicate the indicators of the [Advego](https://advego.com/text/seo/) and [Text.ru](https://text.ru/seo) services: nausea, water content, spam score, naturalness of the word distribution by Zipf's law and keyword density. The data source can be either a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

The exact formulas of the services are not published, so the commonly accepted definitions are implemented; they are described in the [functions](style_stats_funcs.md) section. By default words are extracted in lower case without lemmatization, so forms of one word count as different words, as in Advego. To compute by lemmas, pass a [`WordsExtractor`](../extractors/words.md) object with `use_lexemes=True` and `lowercase=True`.

Lexical officialese markers: verbal nouns, compound prepositions, parentheticals, clichés - by the `COMPOUND_PREPOSITIONS`, `PARENTHETICALS` and `OFFICIALESE_CLICHES` lists of `ruts.constants`. They are counted over unfiltered word forms (`forms`) regardless of the extractor passed.

!!! note "Note"
    The metrics are computed by accessing the corresponding attribute or by calling the `get_stats` method of the `StyleStats` object. The service norms are meant for texts of several hundred words; on short texts nausea and spam values are uninformative.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `words_extractor` | WordsExtractor | `None` | Word extraction tool |
| `stopwords` | list[str] | `None` | Stop word list for water content; if not given, stop words are determined by part of speech with pymorphy3 |
| `top_n` | int | `10` | Number of the most frequent words for academic nausea and naturalness by Zipf's law |
| `cliches` | list[str] | `None` | List of clichés; if not given, `OFFICIALESE_CLICHES` is used |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `words` | tuple[str] | Tuple of extracted words |
| `forms` | tuple[str] | Tuple of unfiltered lowercased word forms; the officialese markers are counted over them |
| `classic_nausea` | float | Classic nausea |
| `academic_nausea` | float | Academic nausea in percent |
| `water` | float | Water content in percent |
| `spam` | float | Spam score in percent |
| `zipf_naturalness` | float | Naturalness by Zipf's law in percent |
| `verbal_nouns` | float | Share of verbal nouns among nouns in percent |
| `compound_prepositions` | float | Compound prepositions per 100 words |
| `parentheticals` | float | Parentheticals per 100 words |
| `cliches` | float | Clichés per 100 words |

Service norms:

| Metric | Norm |
| :----: | :--: |
| Classic nausea | at most 7, in practice 1-5 (Advego) |
| Academic nausea | 5-15% (Advego) |
| Water content | up to 15% - natural, 15-30% - excessive, above 30% - high (Text.ru) |
| Spam score | up to 30% - natural, 30-60% - SEO-optimized text, above 60% - spammed (Text.ru) |
| Naturalness by Zipf's law | at least 50% (pr-cy, megaindex) |

## Methods

### keyword_density

Returns the density of keywords and phrases - the frequency of each per 100 words of the text. A multi-word phrase separated by spaces is searched as a sequence of words, ignoring case.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `keywords` | tuple[str] | `-` | Keywords or phrases |

!!! example "Example"

    ``` python
    from ruts import StyleStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    ss = StyleStats(text)
    ss.keyword_density("когда", "нет а")
    # {'когда': 20.0, 'нет а': 13.333333333333334}
    ```

### get_stats

Returns a dictionary with the computed style metrics.

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts import StyleStats

    # Prepare the data
    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"

    # Compute the metrics
    ss = StyleStats(text)
    ss.get_stats()
    ```

    _Result_:

    ``` bash
    {'classic_nausea': 1.7320508075688772,
    'academic_nausea': 93.33333333333333,
    'water': 46.666666666666664,
    'spam': 26.666666666666668,
    'zipf_naturalness': 33.333333333333336,
    'verbal_nouns': 0.0,
    'compound_prepositions': 0.0,
    'parentheticals': 0.0,
    'cliches': 0.0}
    ```

### print_stats

Prints a table with the computed style metrics.

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed metrics
    ss.print_stats()
    ```

    _Result_:

    ``` bash
                         Метрика                      | Значение
    ------------------------------------------------------------
    Классическая тошнота                              |   1.73
    Академическая тошнота (%)                         |  93.33
    Водность (%)                                      |  46.67
    Заспамленность (%)                                |  26.67
    Естественность по Ципфу (%)                       |  33.33
    Отглагольные существительные (% существительных)  |   0.00
    Производные предлоги (на 100 слов)                |   0.00
    Вводные слова (на 100 слов)                       |   0.00
    Штампы (на 100 слов)                              |   0.00
    ```
