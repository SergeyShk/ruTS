# Lexical sophistication statistics

!!! info ""
    **ruts.lexical_stats.LexicalStats**

## Description

A module for computing lexical sophistication statistics of a text (modeled on [TAALES](https://doi.org/10.3758/s13428-017-0924-4)) - how rare the words of the text are relative to the language: the mean frequency, range and dispersion of lemmas by the [Lyashevskaya and Sharoff frequency dictionary](../datasets/freq2011.md), the shares of words from the top-1000, 2000, 5000 and 10000 frequency bands by the embedded Sharoff list, surprisal and perplexity by the unigram model of the dictionary, lexical density. Unlike the [lexical diversity metrics](diversity_stats.md), which compare the words of the text with each other, here words are compared with the frequencies of the language. The data source can be either a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

Lemmas for a `Doc` with part-of-speech annotation are taken from the pymorphy3 analysis with the token's part of speech (`ruts.utils.lemmatize`), for a string and a `Doc` without annotation - from the first pymorphy3 analysis; hyphenated words split by spaCy are glued back. Content words are defined as in [`CohesionStats`](cohesion_stats.md). Numbers (2020, 5.5, 3-й) do not count as words: they are absent from the dictionary and the list and would look like the rarest words of the text.

Resources:

| Resource | Metrics | Availability |
| :------- | :------ | :----------- |
| [`FreqDict`](../datasets/freq2011.md) - the Lyashevskaya and Sharoff dictionary, 52,138 lemmas with ipm, R, D | `coverage`, `mean_ipm*`, `mean_log_ipm*`, `mean_range`, `mean_dispersion`, `surprisal`, `perplexity` | downloaded once with `FreqDict().download()`; without the dictionary accessing these metrics and `get_stats` raises `DatasetNotFoundError` |
| The embedded list of the 10,000 most frequent lemmas of the Leeds internet corpus (S. A. Sharoff, mirror [hingston/russian](https://github.com/hingston/russian), CC BY 2.5) | `p_top1000`, `p_top2000`, `p_top5000`, `p_top10000`, `p_beyond_top10000`, `band_coverage` | always |

`mean_ipm_content` is the FREQ2 feature of the 2023 Solovyev, Ivanov and Solnyshkina formula with frequency, see [`sis_grade_by_freq`](readability_stats.md#sis_grade_by_freq).

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `words_extractor` | WordsExtractor | `None` | Word extraction tool |
| `freq_dict` | FreqDict | `None` | Frequency dictionary; if not given, `FreqDict()` from the default directory is used |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `words` | tuple[str] | Tuple of extracted words |
| `lemmas` | tuple[str] | Tuple of lowercased lemmas |
| `ranks` | tuple[int/None] | Tuple of lemma ranks by the embedded list, `None` outside the top-10000 |
| `entries` | tuple[Entry/None] | Tuple of dictionary entries for every word, `None` outside the dictionary |
| `n_words` | int | Number of words |
| `n_content_words` | int | Number of content words |
| `n_found` | int | Number of words found in the dictionary |
| `coverage` | float | Share of words found in the dictionary |
| `mean_ipm` | float | Mean frequency of the found words |
| `mean_ipm_content` | float | Mean frequency of content words (FREQ2) |
| `mean_log_ipm` | float | Mean decimal log frequency of the found words |
| `mean_log_ipm_content` | float | The same over content words |
| `mean_range` | float | Mean range R of the found words |
| `mean_dispersion` | float | Mean dispersion D of the found words |
| `surprisal` | float | Mean word surprisal by the unigram model of the dictionary in bits |
| `perplexity` | float | Unigram perplexity |
| `p_top1000` | float | Share of words with a lemma in the top-1000 |
| `p_top2000` | float | Share of words with a lemma in the top-2000 |
| `p_top5000` | float | Share of words with a lemma in the top-5000 |
| `p_top10000` | float | Share of words with a lemma in the top-10000 |
| `p_beyond_top10000` | float | Share of words with a lemma outside the top-10000 |
| `lexical_density` | float | Share of content words |

Dictionary means are computed only over found words, `nan` without them; always read them next to `coverage`.

!!! note "Note"
    Every statistic can be computed separately by calling the corresponding function. Detailed information on the statistics and the functions used to compute them is available in the corresponding [section](lexical_stats_funcs.md).

## Methods

### band_coverage

Returns the shares of words with a lemma in the top-N for every bound N.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `bands` | list[int] | `(1000, 2000, 5000, 10000)` | Band bounds - sizes of the top lists |
| `unique` | bool | `False` | Count over unique lemmas rather than words |

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
    ...

    # Print the table of computed statistics
    ls.print_stats()
    ```

    _Result_:

    ``` bash
                            Статистика                        | Значение
    --------------------------------------------------------------------
    Доля слов, найденных в частотном словаре                  |   1.00
    Средняя частотность (ipm)                                 | 8645.54
    Средняя частотность знаменательных слов (ipm)             |  324.18
    Средняя логарифмическая частотность (lg ipm)              |   3.07
    Средняя логарифмическая частотность знаменательных слов   |   2.32
    Средний диапазон (R)                                      |  99.75
    Средняя дисперсия (D)                                     |  95.12
    Средний сюрпризал (бит)                                   |   9.74
    Униграммная перплексия                                    |  856.21
    Доля слов из топ-1000                                     |   0.75
    Доля слов из топ-2000                                     |   0.88
    Доля слов из топ-5000                                     |   1.00
    Доля слов из топ-10000                                    |   1.00
    Доля слов вне топ-10000                                   |   0.00
    Лексическая плотность                                     |   0.62
    ```
