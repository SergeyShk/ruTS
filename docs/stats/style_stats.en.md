# SEO style metrics

!!! info ""
    **ruts.style_stats.StyleStats**

## Description

--8<-- "stats/style_stats.md:StyleStats"

The definitions and formulas of the metrics are given in the [functions](style_stats_funcs.md) section. By default the words are not lemmatized, so the forms of one word count as different words, as in Advego; to compute by lemmas, pass a [`WordsExtractor`](../extractors/words.md) object with `use_lexemes=True` and `lowercase=True`.

## Language hooks

The class extends the `StyleStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/style_stats/) core with the hooks of Russian: the words of a string are extracted by the Russian [`WordsExtractor`](../extractors/words.md), the stopwords of the academic nausea and the water words are determined by part of speech with pymorphy3 ([`is_stopword`](style_stats_funcs.md#is_stopword), [`is_water_word`](style_stats_funcs.md#is_water_word)), the single parenthetical words by the pymorphy3 grammeme `Prnt` ([`is_parenthetical`](style_stats_funcs.md#calc_parentheticals)), the nouns and their lemmas by pymorphy3 and the verbal nouns among them by `is_verbal_noun` ([`calc_verbal_nouns`](style_stats_funcs.md#calc_verbal_nouns)). The given word lists and the phrases are compared without the letter ё (`normalize_yo`), and a phrase is found in any form of its verb ([`expand_phrases`](style_stats_funcs.md#calc_phrase_density)). The phrase lists are `COMPOUND_PREPOSITIONS`, `PARENTHETICALS` and `OFFICIALESE_CLICHES` of `ruts.constants`, the norms of the services are `STYLE_NORMS` ([below](#norms)); the `print_stats` table has Russian headers and the descriptions of `STYLE_STATS_DESC`, the error messages are in Russian (`CORE_MESSAGES`). The words of a `Doc` lose their stress marks, and the parts of a hyphenated word that spaCy splits are joined (`во-первых` is one word).

## Parameters

--8<-- "stats/style_stats.md:StyleStats-parameters"

## Attributes

--8<-- "stats/style_stats.md:StyleStats-attributes"

## Service norms { #norms }

The [`describe`](#describe) method reads a metric by the bands of the norms of [Advego](https://advego.com/text/seo/), [Text.ru](https://text.ru/seo), pr-cy and megaindex; the officialese markers have no norms. The norms are guidelines of the services for website texts of several hundred words: on short texts nausea and spam values are uninformative, and the norms do not apply to fiction. The method returns the readings in Russian.

| Metric | Value | Reading |
| :-----: | :------: | :-------: |
| `classic_nausea` | `(7, ∞)` | above the Advego norm |
| `classic_nausea` | `(5, 7]` | at the upper bound of the Advego norm |
| `classic_nausea` | `[0, 5]` | the Advego norm |
| `academic_nausea` | `(15, 100]` | above the Advego norm |
| `academic_nausea` | `[5, 15]` | the Advego norm |
| `academic_nausea` | `[0, 5)` | below the Advego norm |
| `water` | `(30, 100]` | high water content by Text.ru |
| `water` | `[15, 30]` | excessive water content by Text.ru |
| `water` | `[0, 15)` | natural water content by Text.ru |
| `spam` | `(60, 100]` | spammed text by Text.ru |
| `spam` | `[30, 60]` | SEO-optimized text by Text.ru |
| `spam` | `[0, 30)` | natural text by Text.ru |
| `zipf_naturalness` | `[50, 100]` | the pr-cy and megaindex norm |
| `zipf_naturalness` | `[0, 50)` | below the pr-cy and megaindex norm |

## Methods

### keyword_density, nausea_words

--8<-- "stats/style_stats.md:StyleStats-keyword_density"

!!! example "Example"

    ``` python
    from ruts import StyleStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    StyleStats(text).keyword_density("когда", "нет а")
    # {'когда': 20.0, 'нет а': 13.333333333333334}

    text = "Кот ловит мышей, кот спит, а мыши бегают вокруг кота"
    StyleStats(text, top_n=2).nausea_words()
    # {'кот': 2, 'ловит': 1}
    ```

### markers

--8<-- "stats/style_stats.md:StyleStats-markers"

!!! example "Example"

    ``` python
    from ruts import StyleStats

    text = "В целях повышения качества в кратчайшие сроки, как правило, проводится проверка"
    StyleStats(text).markers()
    # {'verbal_nouns': ('повышения',),
    #  'compound_prepositions': ('в целях',),
    #  'parentheticals': ('как правило',),
    #  'cliches': ('в кратчайшие сроки',)}
    ```

### describe

--8<-- "stats/stats.md:Stats-describe"

!!! example "Example"

    ``` python
    from ruts import StyleStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    ss = StyleStats(text)
    ss.describe("water")
    # 'высокая водность по Text.ru'
    ss.describe("cliches")
    # None
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
    'academic_nausea': 53.333333333333336,
    'water': 33.333333333333336,
    'spam': 26.666666666666668,
    'zipf_naturalness': 33.333333333333336,
    'verbal_nouns': 0.0,
    'compound_prepositions': 0.0,
    'parentheticals': 0.0,
    'cliches': 0.0}
    ```

### to_dataframe

Returns the computed metrics as a one-row `pandas.DataFrame` with a column for every metric.

### print_stats

--8<-- "stats/stats.md:Stats-print_stats"

To illustrate the method, we reuse the code from the `get_stats` example:

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed metrics
    ss.print_stats()
    ```

    _Result_:

    ``` bash
                         Метрика                     | Значение
    ------------------------------------------------------------
    Классическая тошнота                             |   1.73
    Академическая тошнота (%)                        |  53.33
    Водность (%)                                     |  33.33
    Заспамленность (%)                               |  26.67
    Естественность по Ципфу (%)                      |  33.33
    Отглагольные существительные (% существительных) |   0.00
    Производные предлоги (на 100 слов)               |   0.00
    Вводные слова (на 100 слов)                      |   0.00
    Штампы (на 100 слов)                             |   0.00
    ```
