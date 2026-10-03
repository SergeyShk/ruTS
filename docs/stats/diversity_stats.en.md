# Lexical diversity metrics

!!! info ""
    **ruts.diversity_stats.DiversityStats**

## Description

--8<-- "stats/diversity_stats.md:DiversityStats"

## Language hooks

The class extends the `DiversityStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/diversity_stats/) core: instead of a list of words it takes a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library. The words of a text are extracted by the Russian [`WordsExtractor`](../extractors/words.md) or by a given one, which for a `Doc` is applied to its text; without an extractor the words of a `Doc` come from its tokens, and the parts of a hyphenated word that spaCy splits are joined (`во-первых` is one word). The words are always lower-cased. The `print_stats` table has Russian headers and the Russian descriptions of the metrics from `ruts.constants.DIVERSITY_STATS_DESC`.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `words_extractor` | WordsExtractor | `None` | Word extraction tool; for a Doc it is applied to its text when given |
| `window_len` | int | `50` | Window size for MATTR and segment size for MSTTR |
| `mtld_threshold` | float | `0.72` | TTR threshold for MTLD, MA-MTLD and MTLD-W |
| `mtld_min_len` | int | `10` | Minimum factor length for MTLD, MA-MTLD and MTLD-W |
| `hdd_sample_size` | int | `42` | Sample size for HD-D |
| `log_base` | float | `10` | Logarithm base for the Summer, Maas and Dugast metrics |

--8<-- "stats/diversity_stats.md:check_params"

## Conventions { #conventions }

--8<-- "stats/diversity_stats.md:DiversityStats-conventions"

## Attributes

--8<-- "stats/diversity_stats.md:DiversityStats-attributes"

## Methods

### windowed

--8<-- "stats/diversity_stats.md:DiversityStats-windowed"

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

--8<-- "stats/diversity_stats.md:DiversityStats-get_stats"

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

--8<-- "stats/diversity_stats.md:DiversityStats-print_stats"

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
