# Lexical sophistication statistics

!!! info ""
    **ruts.lexical_stats.LexicalStats**

## Description

--8<-- "stats/lexical_stats.md:LexicalStats"

Unlike the [lexical diversity metrics](diversity_stats.md), which compare the words of a text with each other, here the words are compared with the frequencies of the language ([TAALES](https://doi.org/10.3758/s13428-017-0924-4)). The data source can be either a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

Resources:

| Resource | Metrics | Availability |
| :------- | :------ | :----------- |
| [`FreqDict`](../datasets/freq2011.md) - the Lyashevskaya and Sharoff dictionary, 52,138 lemmas with ipm, R, D | `coverage`, `mean_ipm*`, `mean_log_ipm*`, `mean_range`, `mean_dispersion`, `surprisal`, `perplexity` | downloaded once with `FreqDict().download()`; without the dictionary accessing these metrics and `get_stats` raises `DatasetNotFoundError` |
| The embedded list of the 10,000 most frequent lemmas of the Leeds internet corpus (S. A. Sharoff, mirror [hingston/russian](https://github.com/hingston/russian), CC BY 2.5) | `p_top1000`, `p_top2000`, `p_top5000`, `p_top10000`, `p_beyond_top10000`, `band_coverage` | always |

`mean_ipm_content` is the FREQ2 feature of the 2023 Solovyev, Ivanov and Solnyshkina formula with frequency, see [`sis_grade_by_freq`](readability_stats.md#sis_grade_by_freq).

## Language hooks

The class extends the `LexicalStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/lexical_stats/) core with the Russian layer: the dictionary is the Lyashevskaya and Sharoff [`FreqDict`](../datasets/freq2011.md) (`freq_dict_class`), and the ranks of the lemmas and the size of the list (`rank`, `top_size`) come from the embedded list of the 10,000 Sharoff lemmas ([`get_rank`](lexical_stats_funcs.md#get_rank)). `analyze` takes the words of a string from the Russian [`WordsExtractor`](../extractors/words.md) or from a given extractor, which for a `Doc` is applied to its text; without an extractor the words of a `Doc` come from its tokens, and the parts of a hyphenated word that spaCy splits are joined. Numbers (2020, 5.5, 3-й) are not words. The lemmas come from pymorphy3: for a `Doc` with part-of-speech annotation by the part of speech of the token (`ruts.utils.lemmatize`), otherwise by the first analysis; content words are defined as in [`CohesionStats`](cohesion_stats.md). The keys of the words in the dictionary (`keys`, `dictionary_keys`) are the lemmas brought to its conventions by `dictionary_lemma`: должна - должен, денег - деньги, ночью - ночь. The `print_stats` table and the messages of the errors are in Russian (`LEXICAL_STATS_DESC` and `CORE_MESSAGES` of `ruts.constants`).

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `words_extractor` | WordsExtractor | `None` | Word extraction tool; when given, it is applied to the text of a Doc too |
| `freq_dict` | FreqDict | `None` | Frequency dictionary; if not given, `FreqDict()` from the default directory is used |

A source that is neither a string nor a `Doc` and an extractor of another type raise `SourceTypeError`.

## Attributes

--8<-- "stats/lexical_stats.md:LexicalStats-attributes"

Always read the means by the dictionary next to `coverage`.

!!! note "Note"
    Every statistic can be computed separately by calling the corresponding function. Detailed information on the statistics and the functions used to compute them is available in the corresponding [section](lexical_stats_funcs.md).

## Methods

### band_coverage

--8<-- "stats/lexical_stats.md:LexicalStats-band_coverage"

!!! example "Example"

    ``` python
    from ruts import LexicalStats

    ls = LexicalStats("Кот сидел на окне и смотрел на птиц")
    ls.band_coverage(unique=True)
    # {1000: 0.7142857142857143, 2000: 0.8571428571428571, 5000: 1.0, 10000: 1.0}
    ls.band_coverage(bands=(100, 500))
    # {100: 0.375, 500: 0.75}
    ```

### get_stats

Returns a dictionary with the computed lexical sophistication statistics.

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    from ruts import LexicalStats
    from ruts.datasets import FreqDict

    # Download the dictionary (once)
    FreqDict().download()

    # Compute the statistics
    ls = LexicalStats("Кот сидел на окне и смотрел на птиц")
    ls.get_stats()
    ```

    _Result_:

    ``` bash
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

Rare words raise surprisal and lower coverage and the bands:

!!! example "Example"

    ``` python
    ls = LexicalStats("Фелинолог пребывал на подоконнике")
    ls.coverage, ls.p_top1000, ls.p_beyond_top10000, ls.surprisal
    # (0.75, 0.25, 0.25, 14.515882690436708)
    ```

### print_stats

Prints a table with the computed lexical sophistication statistics.

!!! example "Example"

    _Code_:

    ``` python
    # Create the statistics object
    ls = LexicalStats("Кот сидел на окне и смотрел на птиц")

    # Print the table of computed statistics
    ls.print_stats()
    ```

    _Result_:

    ``` bash
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

### to_dataframe, describe

The `to_dataframe` method (the statistics as a one-row `pandas.DataFrame`) and the `describe` method are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the lexical sophistication statistics have no scales, so `describe` always gives `None`.
