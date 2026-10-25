# Formulas of other languages

``` {.python .signature}
UnadaptedReadabilityStats(source, sents_extractor=None, words_extractor=None)
```

--8<-- "stats/unadapted_readability_stats.md:UnadaptedReadabilityStats"

The class extends the `UnadaptedReadabilityStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/unadapted_readability_stats/) core with the [basic statistics](basic_stats.md) of ruTS, which count the syllables and the letters of Russian words and take the Russian [`SentsExtractor`](../extractors/sentences.md) and [`WordsExtractor`](../extractors/words.md) by default. The `print_stats` table and the error messages are in Russian (`UNADAPTED_READABILITY_STATS_DESC` and `CORE_MESSAGES` of `ruts.constants`).

The formulas are not calibrated for Russian. Their values serve to compare Russian texts with each other and with the results of these formulas in other tools, but they give no grade of the Russian school: on the first-grade texts of the [`TextsByGrade`](../datasets/textsbygrade.md) dataset the median FORCAST is 15.4, the Powers-Sumner-Kearl grade 8.2 and the Wiener Sachtextformel 1 9.6. These formulas therefore have no reading scales, `describe` gives `None` for them, and they do not enter the [consensus grade](readability_stats.md#consensus_grade). The formulas with coefficients for Russian are in [`ReadabilityStats`](readability_stats.md).

=== "Code"

    ``` python
    from ruts import UnadaptedReadabilityStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    urs = UnadaptedReadabilityStats(text)
    urs.print_stats()
    ```

=== "Result"

    ```
                     Метрика                  | Значение
    -----------------------------------------------------
    Класс FORCAST                             |  13.00
    Класс Linsear Write                       |   8.50
    Класс Пауэрса-Самнера-Керла               |   6.55
    Индекс EFLAW Макалпайна                   |  21.00
    Венская формула 1 (Wiener Sachtextformel) |   4.42
    Венская формула 2 (Wiener Sachtextformel) |   4.25
    Венская формула 3 (Wiener Sachtextformel) |   5.69
    Венская формула 4 (Wiener Sachtextformel) |   5.95
    Индекс Дикеса-Штайвера                    |  42.20
    Индекс Gulpease                           |  65.67
    Индекс Фукса                              |  25.00
    Индекс Strain                             |   7.50
    Формула легкости на слух (ELF)            |  10.00
    Индекс Уилера-Смита                       |  80.00
    ```

## Parameters

--8<-- "stats/unadapted_readability_stats.md:UnadaptedReadabilityStats-parameters"

## Attributes

--8<-- "stats/unadapted_readability_stats.md:UnadaptedReadabilityStats-attributes"

Ready basic statistics can be taken from a [`ReadabilityStats`](readability_stats.md) object, so as not to compute them again:

=== "Code"

    ``` python
    from ruts import ReadabilityStats

    rs = ReadabilityStats(text)
    urs = UnadaptedReadabilityStats(rs.bs)
    urs.bs is rs.bs, urs.forcast
    ```

=== "Result"

    ```
    (True, 13.0)
    ```

## Metrics

--8<-- "stats/unadapted_readability_stats.md:UnadaptedReadabilityStats-metrics"

Here ASL is the mean number of words per sentence, ASW the mean number of syllables per word. The functions of the formulas are imported from `ruts.unadapted_readability_stats` and compute a value from counts:

=== "Code"

    ``` python
    from ruts.unadapted_readability_stats import calc_forcast, calc_gulpease

    calc_forcast(n_monosyllable_words=30, n_words=150)
    calc_gulpease(n_letters=550, n_words=100, n_sents=8)
    ```

=== "Result"

    ```
    17.0
    58.0
    ```

<div class="metric-card" markdown>

### FORCAST { #forcast }

`forcast` · Caylor et al., 1973
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_forcast"

</div>

<div class="metric-card" markdown>

### Linsear Write { #linsear_write }

`linsear_write`
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_linsear_write"

</div>

<div class="metric-card" markdown>

### Powers-Sumner-Kearl grade { #powers_sumner_kearl }

`powers_sumner_kearl` · [Powers et al., 1958](https://doi.org/10.1037/h0043254)
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_powers_sumner_kearl"

</div>

<div class="metric-card" markdown>

### McAlpine EFLAW { #eflaw }

`eflaw` · McAlpine, 2005
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_eflaw"

</div>

<div class="metric-card" markdown>

### Wiener Sachtextformel { #wiener_sachtextformel }

`wiener_sachtextformel_1` · `wiener_sachtextformel_2` · `wiener_sachtextformel_3` · `wiener_sachtextformel_4` · Bamberger and Vanecek, 1984
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_wiener_sachtextformel"

</div>

<div class="metric-card" markdown>

### Dickes-Steiwer index { #dickes_steiwer }

`dickes_steiwer` · Dickes and Steiwer, 1977
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_dickes_steiwer"

</div>

<div class="metric-card" markdown>

### Gulpease index { #gulpease }

`gulpease` · Lucisano and Piemontese, 1988
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_gulpease"

</div>

<div class="metric-card" markdown>

### Fucks index { #fucks }

`fucks` · Fucks, 1955
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_fucks"

</div>

<div class="metric-card" markdown>

### Strain index { #strain_index }

`strain_index` · Nathaniel, 2009
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_strain_index"

</div>

<div class="metric-card" markdown>

### Easy listening formula { #elf }

`elf` · [Fang, 1966](https://doi.org/10.1080/08838156609363529)
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_elf"

</div>

<div class="metric-card" markdown>

### Wheeler-Smith index { #wheeler_smith }

`wheeler_smith` · Wheeler and Smith, 1954
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_wheeler_smith"

</div>

## Methods

The methods `get_stats`, `to_dataframe`, `print_stats` and `describe` are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the formulas have no scales, and `describe` gives `None` for any of them.

=== "Code"

    ``` python
    from ruts import UnadaptedReadabilityStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    urs = UnadaptedReadabilityStats(text)
    urs.describe("forcast"), urs.describe("gulpease")
    urs.get_stats()
    ```

=== "Result"

    ```
    (None, None)
    {'forcast': 13.0,
     'linsear_write': 8.5,
     'powers_sumner_kearl': 6.547433333333334,
     'eflaw': 21.0,
     'wiener_sachtextformel_1': 4.416333333333334,
     'wiener_sachtextformel_2': 4.250666666666667,
     'wiener_sachtextformel_3': 5.693766666666667,
     'wiener_sachtextformel_4': 5.949666666666667,
     'dickes_steiwer': 42.19782322089459,
     'gulpease': 65.66666666666667,
     'fucks': 25.0,
     'strain_index': 7.5,
     'elf': 10.0,
     'wheeler_smith': 80.0}
    ```
