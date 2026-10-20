# Lexical diversity metrics

``` {.python .signature}
DiversityStats(source, words_extractor=None, window_len=50, mtld_threshold=0.72, mtld_min_len=10, hdd_sample_size=42, log_base=10)
```

--8<-- "stats/diversity_stats.md:DiversityStats"

Raises:

- `SourceTypeError` - a source that is neither a string nor a `Doc`, an extractor of another type;
- `SourceError` - a source without words;
- `ParameterError` - a parameter that `check_params` rejects.

The class extends the `DiversityStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/diversity_stats/) core: instead of a list of words it takes a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library. The words of a text are extracted by the Russian [`WordsExtractor`](../extractors/words.md) or by a given one, which for a `Doc` is applied to its text; without an extractor the words of a `Doc` come from its tokens without stress marks, and the parts of a hyphenated word that spaCy splits are joined (`во-первых` is one word). The words are always lower-cased. The `print_stats` table has Russian headers and the Russian descriptions of the metrics from `ruts.constants.DIVERSITY_STATS_DESC`, and the error messages are in Russian, from `ruts.constants.CORE_MESSAGES`.

=== "Code"

    ``` python
    from ruts import DiversityStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    ds = DiversityStats(text)
    ds.print_stats()
    ```

=== "Result"

    ```
                                    Метрика                                | Значение
    ----------------------------------------------------------------------------------
    Type-Token Ratio (TTR)                                                 |   0.73
    Root Type-Token Ratio (RTTR)                                           |   2.84
    Corrected Type-Token Ratio (CTTR)                                      |   2.01
    Herdan Type-Token Ratio (HTTR)                                         |   0.89
    Summer Type-Token Ratio (STTR)                                         |   0.25
    Maas Type-Token Ratio (MTTR)                                           |   0.10
    Dugast Type-Token Ratio (DTTR)                                         |  10.27
    Moving Average Type-Token Ratio (MATTR)                                |   0.73
    Mean Segmental Type-Token Ratio (MSTTR)                                |   0.73
    Measure of Textual Lexical Diversity (MTLD)                            |  15.00
    Moving Average Measure of Textual Lexical Diversity (MA-MTLD)          |  12.00
    Moving Average Measure of Textual Lexical Diversity with Wrap (MTLD-W) |  13.25
    Hypergeometric Distribution D (HD-D)                                   |   nan
    Индекс Симпсона (D)                                                    |   0.05
    Обратный индекс Симпсона (1/D)                                         |  21.00
    Индекс Джини-Симпсона (1-D)                                            |   0.95
    Гапакс-индекс (Honoré's R)                                             |  992.95
    Характеристика Юла (Yule's K)                                          |  444.44
    Обратная характеристика Юла (Yule's I)                                 |   8.64
    Мера Хердана (Herdan's Vm)                                             |   0.14
    Мера Сишела (Sichel's S)                                               |   0.18
    Мера Мишеа (Michéa's M)                                                |   5.50
    Мера Брюне (Brunet's W)                                                |   6.01
    Мера Дюга (Dugast's k)                                                 |  14.78
    Мера Баайена (Baayen's P)                                              |   0.53
    Доля гапаксов                                                          |   0.73
    Показатель α₂                                                          |   0.50
    Энтропия Шеннона (бит)                                                 |   3.32
    Выравненность                                                          |   0.96
    Перплексия                                                             |  10.01
    Наклон закона Ципфа (α)                                                |   0.49
    Показатель закона Хипса (β)                                            |   0.84
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Data source |
| `words_extractor` | `WordsExtractor` | `None` | Word extraction tool; for a `Doc` it is applied to its text |
| `window_len` | `int` | `50` | Window size for MATTR and segment size for MSTTR (`MATTR_WINDOW_LEN`) |
| `mtld_threshold` | `float` | `0.72` | TTR threshold for MTLD, MA-MTLD and MTLD-W (`MTLD_TTR_THRESHOLD`) |
| `mtld_min_len` | `int` | `10` | Minimum factor length for MTLD, MA-MTLD and MTLD-W (`MTLD_MIN_LEN`) |
| `hdd_sample_size` | `int` | `42` | Sample size for HD-D (`HDD_SAMPLE_SIZE`) |
| `log_base` | `float` | `10` | Logarithm base for the Summer, Maas and Dugast metrics (`DIVERSITY_LOG_BASE`) |

--8<-- "stats/diversity_stats.md:DiversityStats-attributes"

``` {.python .signature}
check_params(window_len=50, mtld_threshold=0.72, mtld_min_len=10, hdd_sample_size=42, log_base=10, *, messages=CORE_MESSAGES)
```

--8<-- "stats/diversity_stats.md:check_params"

## Conventions { #conventions }

--8<-- "stats/diversity_stats.md:DiversityStats-conventions"

## Metrics

--8<-- "stats/diversity_stats.md:DiversityStats-metrics"

The functions and the named tuples of the cards are imported from `ruts.diversity_stats`.

<div class="metric-card" markdown>

### Type-Token Ratio (TTR) { #ttr }

`ttr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_ttr"

</div>

<div class="metric-card" markdown>

### Root Type-Token Ratio (RTTR) { #rttr }

`rttr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_rttr"

</div>

<div class="metric-card" markdown>

### Corrected Type-Token Ratio (CTTR) { #cttr }

`cttr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_cttr"

</div>

<div class="metric-card" markdown>

### Herdan Type-Token Ratio (HTTR) { #httr }

`httr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_httr"

</div>

<div class="metric-card" markdown>

### Summer Type-Token Ratio (STTR) { #sttr }

`sttr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_sttr"

</div>

<div class="metric-card" markdown>

### Maas Type-Token Ratio (MTTR) { #mttr }

`mttr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_mttr"

</div>

<div class="metric-card" markdown>

### Dugast Type-Token Ratio (DTTR) { #dttr }

`dttr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_dttr"

</div>

<div class="metric-card" markdown>

### Moving Average Type-Token Ratio (MATTR) { #mattr }

`mattr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_mattr"

</div>

<div class="metric-card" markdown>

### Mean Segmental Type-Token Ratio (MSTTR) { #msttr }

`msttr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_msttr"

</div>

<div class="metric-card" markdown>

### Measure of Textual Lexical Diversity (MTLD) { #mtld }

`mtld`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_mtld"

</div>

<div class="metric-card" markdown>

### Moving Average Measure of Textual Lexical Diversity (MA-MTLD) { #mamtld }

`mamtld`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_mamtld"

</div>

<div class="metric-card" markdown>

### MTLD with a moving window and text wrap (MTLD-W) { #mtldw }

`mtldw`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_mtldw"

</div>

<div class="metric-card" markdown>

### Hypergeometric Distribution D (HD-D) { #hdd }

`hdd`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_hdd"

</div>

<div class="metric-card" markdown>

### Simpson's index (D) { #simpson_index }

`simpson_index` · [Wikipedia](https://en.wikipedia.org/wiki/Diversity_index#Simpson_index)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_simpson_index"

</div>

<div class="metric-card" markdown>

### Inverse Simpson's index (1/D) { #inverse_simpson_index }

`inverse_simpson_index` · [Wikipedia](https://en.wikipedia.org/wiki/Diversity_index#Inverse_Simpson_index)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_inverse_simpson_index"

</div>

<div class="metric-card" markdown>

### Gini-Simpson index (1-D) { #gini_simpson_index }

`gini_simpson_index` · [Wikipedia](https://en.wikipedia.org/wiki/Diversity_index#Gini–Simpson_index)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_gini_simpson_index"

</div>

<div class="metric-card" markdown>

### Hapax index (Honoré's R) { #hapax_index }

`hapax_index` · `honore_r` · [Wikipedia](https://en.wikipedia.org/wiki/Hapax_legomenon)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_hapax_index"

A Russian example: боливар ("a hat of a certain style") is a hapax of Pushkin's language: the word occurs only in the famous passage of "Eugene Onegin".

</div>

<div class="metric-card" markdown>

### Frequency spectrum { #frequency_spectrum }

`frequency_spectrum`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_frequency_spectrum"

</div>

<div class="metric-card" markdown>

### Yule's characteristic (Yule's K) { #yule_k }

`yule_k`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_yule_k"

</div>

<div class="metric-card" markdown>

### Inverse Yule's characteristic (Yule's I) { #yule_i }

`yule_i`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_yule_i"

</div>

<div class="metric-card" markdown>

### Herdan's Vm { #herdan_vm }

`herdan_vm`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_herdan_vm"

</div>

<div class="metric-card" markdown>

### Sichel's S { #sichel_s }

`sichel_s`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_sichel_s"

</div>

<div class="metric-card" markdown>

### Michéa's M { #michea_m }

`michea_m`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_michea_m"

</div>

<div class="metric-card" markdown>

### Brunet's W { #brunet_w }

`brunet_w`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_brunet_w"

</div>

<div class="metric-card" markdown>

### Dugast's k { #dugast_k }

`dugast_k`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_dugast_k"

</div>

<div class="metric-card" markdown>

### Baayen's P { #baayen_p }

`baayen_p`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_baayen_p"

</div>

<div class="metric-card" markdown>

### Hapax ratio { #hapax_ratio }

`hapax_ratio`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_hapax_ratio"

</div>

<div class="metric-card" markdown>

### The α₂ exponent { #alpha2 }

`alpha2`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_alpha2"

</div>

<div class="metric-card" markdown>

### Shannon entropy { #entropy }

`entropy` · [Wikipedia](https://en.wikipedia.org/wiki/Diversity_index#Shannon_index)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_entropy"

</div>

<div class="metric-card" markdown>

### Evenness { #evenness }

`evenness`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_evenness"

</div>

<div class="metric-card" markdown>

### Perplexity { #perplexity }

`perplexity`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_perplexity"

</div>

<div class="metric-card" markdown>

### Zipf's law slope { #zipf_alpha }

`zipf_alpha` · [Wikipedia](https://en.wikipedia.org/wiki/Zipf's_law)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_zipf_alpha"

</div>

<div class="metric-card" markdown>

### Zipf-Mandelbrot fit { #fit_zipf_mandelbrot }

[Wikipedia](https://en.wikipedia.org/wiki/Zipf–Mandelbrot_law)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:fit_zipf_mandelbrot"

The [Zipf's law](../visualizers/zipf.md) visualizer draws this fit with `show_fit=True`.

=== "Code"

    ``` python
    from ruts.diversity_stats import fit_zipf_mandelbrot

    # the frequencies 12, 6, 4, 3 follow the law f = 12 / r exactly
    words = ["а"] * 12 + ["б"] * 6 + ["в"] * 4 + ["г"] * 3
    fit = fit_zipf_mandelbrot(words)
    round(fit.c, 3), round(fit.q, 3), round(fit.s, 3), round(fit.r2, 3)
    ```

=== "Result"

    ```
    (12.001, 0.0, 1.0, 1.0)
    ```

</div>

<div class="metric-card" markdown>

### Heaps' law exponent { #heaps_beta }

`heaps_beta` · [Wikipedia](https://en.wikipedia.org/wiki/Heaps'_law)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_heaps_beta"

--8<-- "stats/diversity_stats.md:vocabulary_growth"

--8<-- "stats/diversity_stats.md:fit_heaps"

The [Heaps' law](../visualizers/vocabulary.md) plot is built from `fit_heaps`.

</div>

<div class="metric-card" markdown>

### Windowed computation { #windowed }

`windowed(stat)`
{ .metric-meta }

``` {.python .signature}
calc_windowed(text, func, window_len=100, step=None, confidence=0.95, *, messages=CORE_MESSAGES)
```

--8<-- "stats/diversity_stats.md:calc_windowed"

In ruTS `messages` defaults to `CORE_MESSAGES`.

</div>

--8<-- "stats/diversity_stats.md:diversity-checks"

## Methods

--8<-- "stats/diversity_stats.md:DiversityStats-windowed"

=== "Code"

    ``` python
    ds.windowed("ttr", window_len=5)
    ds.windowed("ttr", window_len=5, step=2).n_windows
    ```

=== "Result"

    ```
    WindowStats(mean=0.9333333333333332, std=0.11547005383792512, lower=0.6464898180167025, upper=1.220176848649964, n_windows=3)
    6
    ```

--8<-- "stats/diversity_stats.md:DiversityStats-get_stats"

--8<-- "stats/diversity_stats.md:DiversityStats-print_stats"

The `to_dataframe` method (the metrics as a one-row `pandas.DataFrame`) and the `describe` method are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the lexical diversity metrics have no scales, so `describe` always gives `None`.
