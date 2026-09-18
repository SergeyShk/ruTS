# Lexical diversity metrics

!!! info ""
    **ruts.diversity_stats.DiversityStats**

## Description

A module for computing the main [lexical diversity](https://en.wikipedia.org/wiki/Lexical_diversity) metrics of a text. The data source can be either a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

The module allows using a pre-built [`WordsExtractor`](../extractors/words.md) object for the word tokenization needed before computing the statistics.

!!! note "Note"
    The metrics are computed by accessing the corresponding attribute or by calling the `get_stats` method of the `DiversityStats` object.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `words_extractor` | WordsExtractor | `None` | Word extraction tool |
| `window_len` | int | `50` | Window size for MATTR and segment size for MSTTR |
| `mtld_threshold` | float | `0.72` | TTR threshold for MTLD, MA-MTLD and MTLD-W |
| `mtld_min_len` | int | `10` | Minimum factor length for MTLD, MA-MTLD and MTLD-W |
| `hdd_sample_size` | int | `42` | Sample size for HD-D |
| `log_base` | float | `10` | Logarithm base for the Summer, Maas and Dugast metrics |

## Conventions { #conventions }

The values of some metrics depend on parameters that different libraries choose differently. The defaults match koRpus and Kyle's lexical-diversity, and all of them are class parameters. The comparison with the MTLD threshold is the only convention that is not a parameter:

| Parameter | ruTS | Other libraries |
| :-------: | :--: | :-------------: |
| Logarithm base for Summer, Maas, Dugast's U and Dugast's k | 10 | LexicalRichness, textcomplexity and zipfR - natural |
| MATTR window and MSTTR segment | 50 | quanteda and koRpus - 100 |
| TTR threshold for MTLD | 0.72 | 0.66-0.75 in the literature |
| Comparison with the MTLD threshold | a factor closes at TTR ≤ 0.72 - in McCarthy and Jarvis (2010) a factor ends when TTR "reaches" 0.720 | lexical-diversity and TAALED - strict `<`, so on factors where TTR hits the threshold exactly (18/25, 36/50) the MTLD, MA-MTLD and MTLD-W values diverge |
| Minimum MTLD factor length | 10 | koRpus applies it only to MA-MTLD, LexicalRichness and textcomplexity do not apply it |
| HD-D sample size | 42 | 35-50 in the literature |

By Zenker and Kyle (2021) MATTR, MTLD and HD-D are stable on texts of 50-200 words and longer, MTLD-W, MA-MTLD and Maas are unstable on short texts, and the TTR family never stabilizes. To compare texts of different lengths use the [windowed computation](#windowed) with confidence intervals.

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `words` | tuple[str] | Tuple of extracted words |
| `frequency_spectrum` | dict[int, int] | Frequency spectrum - the number of lexemes with a given frequency |
| `ttr` | float | Type-Token Ratio (TTR) |
| `rttr` | float | Root Type-Token Ratio (RTTR) |
| `cttr` | float | Corrected Type-Token Ratio (CTTR) |
| `httr` | float | Herdan Type-Token Ratio (HTTR) |
| `sttr` | float | Summer Type-Token Ratio (STTR) |
| `mttr` | float | Maas Type-Token Ratio (MTTR) |
| `dttr` | float | Dugast Type-Token Ratio (DTTR) |
| `mattr` | float | Moving Average Type-Token Ratio (MATTR) |
| `msttr` | float | Mean Segmental Type-Token Ratio (MSTTR) |
| `mtld` | float | Measure of Textual Lexical Diversity (MTLD) |
| `mamtld` | float | Moving Average Measure of Textual Lexical Diversity (MA-MTLD) |
| `mtldw` | float | MTLD with a moving window and text wrap (MTLD-W) |
| `hdd` | float | Hypergeometric Distribution D (HD-D) |
| `simpson_index` | float | Simpson's index (D) |
| `inverse_simpson_index` | float | Inverse Simpson's index (1/D) |
| `gini_simpson_index` | float | Gini-Simpson index (1-D) |
| `hapax_index` | float | Hapax index, a.k.a. Honoré's R |
| `honore_r` | float | Alias for the hapax index |
| `yule_k` | float | Yule's characteristic (Yule's K) |
| `yule_i` | float | Inverse Yule's characteristic (Yule's I) |
| `herdan_vm` | float | Herdan's Vm |
| `sichel_s` | float | Sichel's S |
| `michea_m` | float | Michéa's M |
| `brunet_w` | float | Brunet's W |
| `dugast_k` | float | Dugast's k |
| `baayen_p` | float | Baayen's P |
| `hapax_ratio` | float | Share of hapaxes among lexemes |
| `alpha2` | float | The α₂ exponent |
| `entropy` | float | Shannon entropy in bits |
| `evenness` | float | Evenness - the ratio of entropy to its maximum |
| `perplexity` | float | Perplexity |
| `zipf_alpha` | float | Zipf's law slope |
| `heaps_beta` | float | Heaps' law exponent |

!!! note "Note"
    Every metric can be computed separately by calling the corresponding function. Detailed information on the lexical diversity metrics and the functions used to compute them is available in the corresponding [section](diversity_stats_funcs.md).

## Methods

### windowed

Windowed computation of a metric: its value over consecutive text windows of equal length, the mean, the sample standard deviation and the confidence interval of the mean by Student's distribution. The standard way to compare texts of different lengths; Kubát and Milička's STTR is a windowed TTR with a 1000-word window and a 95% confidence interval. For texts shorter than the window the metric is computed over the whole text as a single window; windows with an undefined metric value (`nan`) are ignored. If the metric is infinite in at least one window, the mean is infinite and the standard deviation and confidence interval are undefined.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `stat` | str | `-` | Metric name from `get_stats` |
| `window_len` | int | `100` | Window size |
| `step` | int | `None` | Window step, by default equal to the window size (windows do not overlap) |
| `confidence` | float | `0.95` | Confidence level |

Returns a `WindowStats` named tuple with the fields `mean`, `std`, `lower`, `upper` and `n_windows`.

!!! example "Example"

    ``` python
    from ruts import DiversityStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    ds = DiversityStats(text)
    ds.windowed("ttr", window_len=5)
    # WindowStats(mean=0.9333333333333332, std=0.11547005383792512, lower=0.6464898180167025, upper=1.220176848649964, n_windows=3)
    ds.windowed("ttr", window_len=5, step=2).n_windows
    # 6
    ```

### get_stats

Returns a dictionary with the computed lexical diversity metrics.

An example of computing lexical diversity metrics:

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts import DiversityStats

    # Prepare the data
    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"

    # Compute the metrics
    ds = DiversityStats(text)
    ds.get_stats()
    ```

    _Result_:

    ``` bash
    {'ttr': 0.7333333333333333,
    'rttr': 2.840187787218772,
    'cttr': 2.008316044185609,
    'httr': 0.8854692840710255,
    'sttr': 0.2500605793160848,
    'mttr': 0.09738250756232528,
    'dttr': 10.268784661968118,
    'mattr': 0.7333333333333333,
    'msttr': 0.7333333333333333,
    'mtld': 15.0,
    'mamtld': 12.0,
    'mtldw': 13.25,
    'hdd': nan,
    'simpson_index': 0.047619047619047616,
    'inverse_simpson_index': 21.0,
    'gini_simpson_index': 0.9523809523809523,
    'hapax_index': 992.9517404041437,
    'yule_k': 444.44444444444446,
    'yule_i': 8.642857142857142,
    'herdan_vm': 0.1421338109037403,
    'sichel_s': 0.18181818181818182,
    'michea_m': 5.5,
    'brunet_w': 6.00637847898991,
    'dugast_k': 14.783895126869226,
    'baayen_p': 0.5333333333333333,
    'hapax_ratio': 0.7272727272727273,
    'alpha2': 0.5,
    'entropy': 3.3232314287976203,
    'evenness': 0.9606293157795304,
    'perplexity': 10.009038104159247,
    'zipf_alpha': 0.4884512334695912,
    'heaps_beta': 0.8366147342060046}
    ```

### print_stats

Prints a table with the computed lexical diversity metrics.

To illustrate the method, we reuse the code from the previous example:

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed metrics
    ds.print_stats()
    ```

    _Result_:

    ``` bash
                                      Метрика                                  | Значение
    -------------------------------------------------------------------------------------
    Type-Token Ratio (TTR)                                                     |   0.73
    Root Type-Token Ratio (RTTR)                                               |   2.84
    Corrected Type-Token Ratio (CTTR)                                          |   2.01
    Herdan Type-Token Ratio (HTTR)                                             |   0.89
    Summer Type-Token Ratio (STTR)                                             |   0.25
    Maas Type-Token Ratio (MTTR)                                               |   0.10
    Dugast Type-Token Ratio (DTTR)                                             |  10.27
    Moving Average Type-Token Ratio (MATTR)                                    |   0.73
    Mean Segmental Type-Token Ratio (MSTTR)                                    |   0.73
    Measure of Textual Lexical Diversity (MTLD)                                |  15.00
    Moving Average Measure of Textual Lexical Diversity (MA-MTLD)              |  12.00
    Moving Average Measure of Textual Lexical Diversity with Wrap (MTLD-W)     |  13.25
    Hypergeometric Distribution D (HD-D)                                       |   nan
    Индекс Симпсона (D)                                                        |   0.05
    Обратный индекс Симпсона (1/D)                                             |  21.00
    Индекс Джини-Симпсона (1-D)                                                |   0.95
    Гапакс-индекс (Honoré's R)                                                 |  992.95
    Характеристика Юла (Yule's K)                                              |  444.44
    Обратная характеристика Юла (Yule's I)                                     |   8.64
    Мера Хердана (Herdan's Vm)                                                 |   0.14
    Мера Сишела (Sichel's S)                                                   |   0.18
    Мера Мишеа (Michéa's M)                                                    |   5.50
    Мера Брюне (Brunet's W)                                                    |   6.01
    Мера Дюга (Dugast's k)                                                     |  14.78
    Мера Баайена (Baayen's P)                                                  |   0.53
    Доля гапаксов                                                              |   0.73
    Показатель α₂                                                              |   0.50
    Энтропия Шеннона (бит)                                                     |   3.32
    Выравненность                                                              |   0.96
    Перплексия                                                                 |  10.01
    Наклон закона Ципфа (α)                                                    |   0.49
    Показатель закона Хипса (β)                                                |   0.84
    ```
