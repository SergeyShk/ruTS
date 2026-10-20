# Lexical sophistication statistics

``` {.python .signature}
LexicalStats(source, words_extractor=None, freq_dict=None)
```

--8<-- "stats/lexical_stats.md:LexicalStats"

In ruTS a source that is neither a string nor a `Doc` and an extractor of another type raise `SourceTypeError` too, and the metrics by the dictionary without the dictionary downloaded `DatasetNotFoundError`.

Unlike the [lexical diversity metrics](diversity_stats.md), which compare the words of a text with each other, here the words are compared with the frequencies of the language ([TAALES](https://doi.org/10.3758/s13428-017-0924-4)). The data source is a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

The class extends the `LexicalStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/lexical_stats/) core with the Russian layer: the dictionary is the Lyashevskaya and Sharoff [`FreqDict`](../datasets/freq2011.md) (`freq_dict_class`), and the ranks of the lemmas and the size of the list (`rank`, `top_size`) come from the embedded list of the Sharoff lemmas ([`get_rank`](#bands)). The words of a string are extracted by the Russian [`WordsExtractor`](../extractors/words.md) or by a given extractor, which for a `Doc` is applied to its text; without an extractor the words of a `Doc` come from its tokens, and the parts of a hyphenated word that spaCy splits are joined. Numbers (2020, 5.5, 3-й) are not words. The lemmas come from pymorphy3: for a `Doc` with part-of-speech annotation by the part of speech of the token (`ruts.utils.lemmatize`), otherwise by the first analysis. The keys of the words in the dictionary (`keys`, `dictionary_keys`) are the lemmas brought to its conventions by `dictionary_lemma`: должна - должен, денег - деньги, ночью - ночь. The `print_stats` table and the error messages are in Russian (`LEXICAL_STATS_DESC` and `CORE_MESSAGES` of `ruts.constants`).

=== "Code"

    ``` python
    from ruts import LexicalStats
    from ruts.datasets import FreqDict

    FreqDict().download()
    ls = LexicalStats("Кот сидел на окне и смотрел на птиц")
    ls.print_stats()
    ```

=== "Result"

    ```
                           Статистика                       | Значение
    -------------------------------------------------------------------
    Доля слов, найденных в частотном словаре                |   1.00
    Средняя частотность (ipm)                               | 8645.54
    Средняя частотность знаменательных слов (ipm)           |  324.18
    Средняя логарифмическая частотность (lg ipm)            |   3.07
    Средняя логарифмическая частотность знаменательных слов |   2.32
    Средний диапазон (R)                                    |  99.75
    Средняя дисперсия (D)                                   |  95.12
    Средний сюрпризал (бит)                                 |   9.74
    Униграммная перплексия                                  |  856.21
    Доля слов из топ-1000                                   |   0.75
    Доля слов из топ-2000                                   |   0.88
    Доля слов из топ-5000                                   |   1.00
    Доля слов из топ-10000                                  |   1.00
    Доля слов вне топ-10000                                 |   0.00
    Лексическая плотность                                   |   0.62
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Data source |
| `words_extractor` | `WordsExtractor` | `None` | Word extraction tool; used for a `Doc` too, on its text |
| `freq_dict` | `FreqDict` | `None` | Frequency dictionary; `FreqDict()` from the default directory by default |

## Attributes

--8<-- "stats/lexical_stats.md:LexicalStats-attributes"

In ruTS the dictionary is a `FreqDict`, and its entries are the named tuples `Entry`.

## Metrics

--8<-- "stats/lexical_stats.md:LexicalStats-metrics"

The metrics rely on two resources; always read the means by the dictionary next to `coverage`.

| Resource | Metrics | Availability |
| :------- | :------ | :----------- |
| [`FreqDict`](../datasets/freq2011.md) - the Lyashevskaya and Sharoff dictionary, 52,138 lemmas with ipm, R, D | `coverage`, `mean_ipm*`, `mean_log_ipm*`, `mean_range`, `mean_dispersion`, `surprisal`, `perplexity` | downloaded once with `FreqDict().download()` |
| The embedded list of the 10,000 most frequent lemmas of the Leeds internet corpus (S. A. Sharoff, mirror [hingston/russian](https://github.com/hingston/russian), CC BY 2.5) | `p_top1000`, `p_top2000`, `p_top5000`, `p_top10000`, `p_beyond_top10000`, `band_coverage` | always |

<div class="metric-card" markdown>

### Dictionary frequency { #frequency }

`coverage` · `mean_ipm` · `mean_ipm_content` · `mean_log_ipm` · `mean_log_ipm_content` · `mean_range` · `mean_dispersion` · [Lyashevskaya, Sharoff](http://dict.ruslang.ru/freq.php)
{ .metric-meta }

The metrics are computed from the `FreqDict` entries for the keys of the words (`keys`, `entries`): the means are taken over the words found in the dictionary, over all of them or only over the content words. The mean frequency in ipm is sensitive to function words (и - 35,000 ipm, в - 31,000), so for comparing texts the log frequency or the mean over the content words is more convenient. The mean frequency of the content words `mean_ipm_content` is the FREQ2 feature of the 2023 Solovyev, Ivanov and Solnyshkina formula, whose values in the paper lie within 200-1000 ([`sis_grade_by_freq`](readability_stats.md#sis_grade_by_freq)).

Rare words lower the coverage and the log frequency and raise the surprisal and the share beyond the top 10000:

=== "Code"

    ``` python
    from ruts import LexicalStats

    ls = LexicalStats("Фелинолог пребывал на подоконнике")
    ls.coverage, ls.mean_log_ipm, ls.surprisal, ls.p_beyond_top10000
    ```

=== "Result"

    ```
    (0.75, 2.3063585317426494, 14.515882690436708, 0.25)
    ```

</div>

<div class="metric-card" markdown>

### Surprisal and perplexity { #surprisal }

`surprisal` · `perplexity`
{ .metric-meta }

--8<-- "stats/lexical_stats.md:calc_surprisal"

In ruTS the dictionary is a `FreqDict` with the lowest frequency of 0.4 ipm: a dictionary of another class raises `SourceTypeError`.

=== "Code"

    ``` python
    from ruts.datasets import FreqDict
    from ruts.lexical_stats import calc_surprisal

    calc_surprisal(["кот", "сидеть", "фелинолог"], FreqDict())
    ```

=== "Result"

    ```
    15.570731790883956
    ```

</div>

<div class="metric-card" markdown>

### Frequency bands { #bands }

`p_top1000` · `p_top2000` · `p_top5000` · `p_top10000` · `p_beyond_top10000` · `band_coverage(bands, unique)`
{ .metric-meta }

--8<-- "stats/lexical_stats.md:LexicalStats-bands"

This builds a frequency band profile in the manner of the Lexical Frequency Profile.

``` {.python .signature}
get_rank(lemma)
```

The rank of a lemma by the embedded Sharoff list, `None` for a lemma outside the list; the lemma may be in any case, with ё or without.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `lemma` | `str` | - | Lemma |

``` {.python .signature}
load_top_lemmas()
```

The whole list from the file `ruts/resources/sharoff_top10000.txt`: the rank of every lemma, lowercased and with ё replaced by е, starting from 1; duplicates keep the smaller rank.

=== "Code"

    ``` python
    from ruts.lexical_stats import get_rank, load_top_lemmas

    get_rank("и"), get_rank("кот"), get_rank("фелинолог")
    len(load_top_lemmas())
    ```

=== "Result"

    ```
    (1, 2009, None)
    9989
    ```

</div>

<div class="metric-card" markdown>

### Lexical density { #lexical_density }

`lexical_density`
{ .metric-meta }

The share of the content words (nouns, adjectives, verbs, adverbs without pronominal and parenthetical words) among all the words; a content word is defined by [`is_content_word`](cohesion_stats.md#is_content_word) for a string and by `CONTENT_UD_POS` for an annotated `Doc`.

$$
\frac{\textrm{Number of content words}}{\textrm{Number of words}}
$$

</div>

## Methods

--8<-- "stats/lexical_stats.md:LexicalStats-band_coverage"

=== "Code"

    ``` python
    from ruts import LexicalStats

    ls = LexicalStats("Кот сидел на окне и смотрел на птиц")
    ls.band_coverage(unique=True)
    ls.band_coverage(bands=(100, 500))
    ```

=== "Result"

    ```
    {1000: 0.7142857142857143, 2000: 0.8571428571428571, 5000: 1.0, 10000: 1.0}
    {100: 0.375, 500: 0.75}
    ```

The other methods - `get_stats`, `to_dataframe`, `print_stats` and `describe` - are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the lexical sophistication statistics have no scales, so `describe` gives `None` for the statistics of `get_stats`.

=== "Code"

    ``` python
    ls.get_stats()
    ```

=== "Result"

    ```
    {'coverage': 1.0,
     'mean_ipm': 8645.5375,
     'mean_ipm_content': 324.18,
     'mean_log_ipm': 3.0674194359404705,
     'mean_log_ipm_content': 2.316850597556863,
     'mean_range': 99.75,
     'mean_dispersion': 95.125,
     'surprisal': 9.74182176626998,
     'perplexity': 856.2105288389297,
     'p_top1000': 0.75,
     'p_top2000': 0.875,
     'p_top5000': 1.0,
     'p_top10000': 1.0,
     'p_beyond_top10000': 0.0,
     'lexical_density': 0.625}
    ```
