# SEO style metrics

``` {.python .signature}
StyleStats(source, words_extractor=None, stopwords=None, top_n=10, cliches=None, nausea_stopwords=None)
```

--8<-- "stats/style_stats.md:StyleStats"

The class extends the `StyleStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/style_stats/) core with the hooks of Russian, given in the cards of the metrics. The words of a string are extracted by the Russian [`WordsExtractor`](../extractors/words.md) and are not lemmatized, so the forms of one word count as different words, as in Advego; to compute by lemmas, pass a `WordsExtractor` with `use_lexemes=True` and `lowercase=True`. The given word lists and the phrases are compared without the letter ё (`normalize_yo`). The words of a `Doc` lose their stress marks, and the parts of a hyphenated word that spaCy splits are joined (`во-первых` is one word). The `print_stats` table and the error messages are in Russian (`STYLE_STATS_DESC` and `CORE_MESSAGES` of `ruts.constants`).

=== "Code"

    ``` python
    from ruts import StyleStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    StyleStats(text).print_stats()
    ```

=== "Result"

    ```
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

## Parameters

--8<-- "stats/style_stats.md:StyleStats-parameters"

`NAUSEA_TOP_N` is a constant of `anyts.constants`.

## Attributes

--8<-- "stats/style_stats.md:StyleStats-attributes"

## Metrics

--8<-- "stats/style_stats.md:StyleStats-metrics"

The cards give the bands that [`describe`](#methods) reads, after the norms of [Advego](https://advego.com/text/seo/), [Text.ru](https://text.ru/seo), pr-cy and megaindex, in Russian (`STYLE_NORMS`). The norms are guidelines of the services for website texts of several hundred words: on short texts nausea and spam values are uninformative, and the norms do not apply to fiction. The markers of the officialese have no norms.

<div class="metric-card" markdown>

### Classic nausea { #classic_nausea }

`classic_nausea` · [Advego](https://advego.com/text/seo/)
{ .metric-meta }

--8<-- "stats/style_stats.md:calc_classic_nausea"

| Value | Reading |
| :---- | :------ |
| `[0, 5]` | the Advego norm |
| `(5, 7]` | at the upper bound of the Advego norm |
| `(7, ∞)` | above the Advego norm |

</div>

<div class="metric-card" markdown>

### Academic nausea { #academic_nausea }

`academic_nausea` · `nausea_words()` · [Advego](https://advego.com/text/seo/)
{ .metric-meta }

``` {.python .signature}
calc_academic_nausea(text, top_n=10, stopwords=None)
```

The share of the occurrences of the `top_n` most frequent significant words among all the words, in percent.

$$
100 \cdot \frac{\sum_{w \in \textrm{top}_n} f_w}{\textrm{Number of words}}
$$

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |
| `top_n` | `int` | `10` | Number of the most frequent words |
| `stopwords` | `list[str]` | `None` | Stop words; without them `is_stopword` decides |

A `top_n` that is not an integer of at least one raises `ParameterError`.

| Value | Reading |
| :---- | :------ |
| `[0, 5)` | below the Advego norm |
| `[5, 15]` | the Advego norm |
| `(15, 100]` | above the Advego norm |

``` {.python .signature}
find_nausea_words(text, top_n=10, stopwords=None)
```

The `top_n` most frequent words without the stop words, those the academic nausea counts, with their occurrences: the most frequent first, words of equal frequency in the order of the text. A stop word is a word of `stopwords`, compared ignoring case and the letter ё, or, without the list, a word of `is_stopword`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |
| `top_n` | `int` | `10` | Number of the most frequent words |
| `stopwords` | `list[str]` | `None` | Stop words; without them `is_stopword` decides |

A `top_n` that is not an integer of at least one raises `ParameterError`.

``` {.python .signature}
is_stopword(word)
```

Whether a word is insignificant for the academic nausea by its part of speech in pymorphy3: conjunctions, particles, prepositions, pronominal nouns, interjections and predicatives (`CONJ`, `PRCL`, `PREP`, `NPRO`, `INTJ`, `PRED`), and the words with the grammemes `Apro`, `Prnt`, `Dmns`, `Ques` - pronominal adjectives, parenthetical words, demonstrative and interrogative adverbs. The sets are `ruts.constants.STOPWORD_POS` and `ruts.constants.STOPWORD_GRAMMEMES`.

=== "Code"

    ``` python
    from ruts.style_stats import find_nausea_words

    find_nausea_words(["кот", "и", "кот", "и", "пес"], top_n=1)
    ```

=== "Result"

    ```
    {'кот': 2}
    ```

</div>

<div class="metric-card" markdown>

### Water content { #water }

`water` · [Text.ru](https://text.ru/seo)
{ .metric-meta }

``` {.python .signature}
calc_water(text, stopwords=None)
```

The share of the words without content, in percent: the words of `stopwords`, compared ignoring case and the letter ё, or, without the list, the words of `is_water_word`. Advego's "water" is a different indicator; it is not implemented here.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |
| `stopwords` | `list[str]` | `None` | Water words |

| Value | Reading |
| :---- | :------ |
| `[0, 15)` | natural water content by Text.ru |
| `[15, 30]` | excessive water content by Text.ru |
| `(30, 100]` | high water content by Text.ru |

``` {.python .signature}
is_water_word(word)
```

Whether a word is "water" by its part of speech in pymorphy3, for the water content and the `stopwords` layer of the highlighting: conjunctions, particles, pronominal nouns and interjections (`CONJ`, `PRCL`, `NPRO`, `INTJ`; the set `ruts.constants.WATER_POS`). pymorphy3 tags the parenthetical words конечно and например as conjunctions, so they are water too. Prepositions, pronominal adjectives and predicatives, unlike in `is_stopword`, are not water.

</div>

<div class="metric-card" markdown>

### Spam score { #spam }

`spam` · [Text.ru](https://text.ru/seo)
{ .metric-meta }

--8<-- "stats/style_stats.md:calc_spam"

| Value | Reading |
| :---- | :------ |
| `[0, 30)` | natural text by Text.ru |
| `[30, 60]` | SEO-optimized text by Text.ru |
| `(60, 100]` | spammed text by Text.ru |

</div>

<div class="metric-card" markdown>

### Naturalness by Zipf's law { #zipf_naturalness }

`zipf_naturalness` · pr-cy, megaindex
{ .metric-meta }

``` {.python .signature}
calc_zipf_naturalness(text, top_n=10)
```

The agreement of the frequencies of the most frequent words with the ideal distribution of [Zipf's law](https://en.wikipedia.org/wiki/Zipf's_law), $f_r = f_1 / r$, where $f_1$ is the frequency of the most frequent word and $r$ the rank. The ranks run from 2 to $R = \min(\textrm{top}_n, V, f_1)$, where $V$ is the number of lexemes. Negative values are cut to 0. Without ranks to compare - all the words hapaxes, one lexeme or `top_n` below 2 - the value is `nan`.

$$
100 \cdot \left(1 - \frac{1}{R - 1} \sum_{r=2}^{R} \frac{|r \cdot f_r - f_1|}{f_1}\right)
$$

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |
| `top_n` | `int` | `10` | Number of the most frequent words |

A `top_n` that is not an integer of at least one raises `ParameterError`.

| Value | Reading |
| :---- | :------ |
| `[0, 50)` | below the pr-cy and megaindex norm |
| `[50, 100]` | the pr-cy and megaindex norm |

</div>

<div class="metric-card" markdown>

### Verbal nouns { #verbal_nouns }

`verbal_nouns`
{ .metric-meta }

``` {.python .signature}
calc_verbal_nouns(text)
```

The share of the verbal nouns among the nouns (by the first pymorphy3 analysis), in percent; `nan` for a text without nouns. A noun is verbal when its lemma ends with a suffix of `VERBAL_NOUN_SUFFIXES` (-ние, -нье, -тие, -тье, -ствие, -ция) or belongs to `VERBAL_NOUN_LEMMAS` (производство, руководство, строительство) - the function `ruts.utils.is_verbal_noun`. The heuristic also catches non-verbal words with the same suffixes (здание). `find_verbal_nouns(text)` returns the bounds of the words found as slices of the list.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |

</div>

<div class="metric-card" markdown>

### Compound prepositions and cliches { #phrase_density }

`compound_prepositions` · `cliches`
{ .metric-meta }

``` {.python .signature}
calc_phrase_density(text, phrases)
```

The occurrences of the phrases of a list per 100 words. The phrases are compared ignoring case and the letter ё, and a phrase starting with an infinitive, alone or after «не», is found in any form of its verb, participles and gerunds included («имело место», «доведено до сведения»). `expand_phrases(text, phrases)` gives these variants from the text, each with its phrase. `StyleStats` counts this way, over the word forms (`forms`), the compound prepositions of `COMPOUND_PREPOSITIONS` (в целях, в связи с, в рамках, за счет) and the cliches of `OFFICIALESE_CLICHES` (на сегодняшний день, в настоящее время, иметь место) or of the parameter `cliches`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |
| `phrases` | `list[str]` | - | Phrases with words separated by spaces |

</div>

<div class="metric-card" markdown>

### Parenthetical words { #parentheticals }

`parentheticals`
{ .metric-meta }

``` {.python .signature}
calc_parentheticals(text)
```

The number of parenthetical words per 100 words: the phrases of `PARENTHETICALS` (таким образом, как правило, в частности, кроме того) and, outside them, the single words with the pymorphy3 grammeme `Prnt` (конечно, например, впрочем; the function `is_parenthetical(word)`). `find_parentheticals(text)` returns the bounds of the words and phrases found as slices of the list.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |

</div>

<div class="metric-card" markdown>

### Keyword density { #keyword_density }

`keyword_density(*keywords)` · [Text.ru](https://text.ru/seo)
{ .metric-meta }

``` {.python .signature}
calc_keyword_density(text, keywords)
```

The occurrences of every keyword per 100 words. A keyword of several words separated by spaces is a sequence of words whose occurrences may overlap. The words and the keywords are compared in lower case without the letter ё, as the stop words and the phrases, and the keywords of a set come in sorted order.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |
| `keywords` | `list[str]` | - | Keywords or phrases |

</div>

The functions check their words: words, stop words, keywords and phrases that are not a list of strings raise `SourceTypeError`.

## Methods { #methods }

--8<-- "stats/style_stats.md:StyleStats-keyword_density"

--8<-- "stats/style_stats.md:StyleStats-markers"

=== "Code"

    ``` python
    from ruts import StyleStats

    text = "В целях повышения качества в кратчайшие сроки, как правило, проводится проверка"
    StyleStats(text).markers()
    StyleStats(text, top_n=2).nausea_words()
    ```

=== "Result"

    ```
    {'verbal_nouns': ('повышения',),
     'compound_prepositions': ('в целях',),
     'parentheticals': ('как правило',),
     'cliches': ('в кратчайшие сроки',)}
    {'целях': 1, 'повышения': 1}
    ```

The other methods - `get_stats`, `to_dataframe`, `print_stats` and `describe` - are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; `describe` reads the SEO metrics by the bands of the norms of their cards and gives `None` for the markers of the officialese.

=== "Code"

    ``` python
    from ruts import StyleStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    ss = StyleStats(text)
    ss.keyword_density("когда", "нет а")
    ss.describe("water"), ss.describe("cliches")
    ss.get_stats()
    ```

=== "Result"

    ```
    {'когда': 20.0, 'нет а': 13.333333333333334}
    ('высокая водность по Text.ru', None)
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
