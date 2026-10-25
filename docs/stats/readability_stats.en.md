# Readability metrics

``` {.python .signature}
ReadabilityStats(source, sents_extractor=None, words_extractor=None, preset='plainrussian')
```

--8<-- "stats/readability_stats.md:ReadabilityStats"

The metrics assess readability on the side of the language - the complexity of words and syntactic constructions, not the typographic design of the text. They presume that short sentences are easier to read than long ones, long words make reading harder, and low-frequency and unfamiliar words slow a reader down.

The class extends the `ReadabilityStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/readability_stats/) core with the hooks of Russian, given in the cards of the metrics: the [basic statistics](basic_stats.md) of ruTS, which take the Russian [`SentsExtractor`](../extractors/sentences.md) and [`WordsExtractor`](../extractors/words.md) by default, the coefficient [presets](#presets), the Russian formulas, the consensus grade over the formulas of ruTS, the stages of the Russian school, the scales with Russian labels and the reading speeds of Russian readers. The `print_stats` table and the error messages are in Russian (`READABILITY_STATS_DESC` and `CORE_MESSAGES` of `ruts.constants`).

=== "Code"

    ``` python
    from ruts import ReadabilityStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    rs = ReadabilityStats(text)
    rs.print_stats()
    ```

=== "Result"

    ```
                    Метрика                 | Значение
    ---------------------------------------------------
    Тест Флеша-Кинкайда                     |  -2.06
    Индекс удобочитаемости Флеша            |  87.17
    Индекс Колман-Лиау                      |   1.17
    Индекс SMOG                             |   0.05
    Автоматический индекс удобочитаемости   |   0.29
    Индекс удобочитаемости LIX              |  28.33
    Индекс удобочитаемости RIX              |   2.00
    Формула Соловьёва, Иванова, Солнышкиной |   1.52
    Формула Мацковского                     |   9.35
    Формула Тулдавы                         |   1.96
    Индекс Дейла-Чейла                      |   4.10
    Индекс Ганнинга                         |   6.00
    Сводный класс                           |   1.50
    Время чтения (мин.)                     |   0.08
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` / `BasicStats` | - | Data source (a string, a Doc object or ready basic statistics) |
| `sents_extractor` | `SentsExtractor` | `None` | Sentence extraction tool |
| `words_extractor` | `WordsExtractor` | `None` | Word extraction tool |
| `preset` | `str` | `'plainrussian'` | Coefficient preset: `plainrussian`, `fiction` or `academic` |

The object keeps the basic statistics of the text in `bs`, the name of the preset in `preset`, read-only, and the coefficients of the preset by formula in `coefficients`, a copy that can be changed for one object. An object of another preset can reuse the basic statistics: `ReadabilityStats(rs.bs, preset="fiction")`.

## Coefficient presets { #presets }

The coefficients of the formulas are parameters of their functions, and a preset gives them by formula. The presets differ in the coefficients of the Flesch-Kincaid test and the Flesch index; the coefficients of the Coleman-Liau, SMOG and ARI indices in all presets come from the plainrussian project, since no other adaptations for Russian have been published, and the other formulas do not depend on the preset.

| Preset | Source | Corpus | Flesch-Kincaid test | Flesch index |
| :----- | :----- | :----- | :------------------ | :----------- |
| `plainrussian` | [Plain Russian Language](https://github.com/infoculture/plainrussian) (Begtin) | 68 grade-labeled texts | `0.318·ASL + 14.2·ASW − 30.5` | `206.835 − 1.3·ASL − 60.1·ASW` (Oborneva, variant A, since plainrussian does not derive the Flesch index) |
| `fiction` | Oborneva (2005/2006) | about 6 million words of fiction | `0.5·ASL + 8.4·ASW − 15.59` | `206.835 − 1.3·ASL − 60.1·ASW` (variant A) |
| `academic` | Solovyev, Ivanov, Solnyshkina (2018); Solnyshkina and Kiselnikov (2015) | 14 social studies textbooks for grades 5-11 | `0.36·ASL + 5.76·ASW − 11.97` (FKG_SIS) | `206.836 − 1.52·ASL − 65.14·ASW` (Oborneva, variant B) |

Here ASL is the mean number of words per sentence, ASW the mean number of syllables per word. The table of all coefficients is `ruts.constants.READABILITY_PRESETS`.

=== "Code"

    ``` python
    ReadabilityStats(text).flesch_kincaid_grade
    ReadabilityStats(text, preset="fiction").flesch_kincaid_grade
    ReadabilityStats(text, preset="academic").flesch_kincaid_grade
    ```

=== "Result"

    ```
    -2.0633333333333326
    5.91
    3.0299999999999994
    ```

The presets agree with the grade label alike but give different scales, and they do not order texts quite alike. On the [`TextsByGrade`](../datasets/textsbygrade.md) dataset the Spearman correlation of the Flesch-Kincaid test with the grade label for all three presets is 0.79, while the medians of the test by label group differ:

| Label | Texts | `plainrussian` | `fiction` | `academic` |
| :---- | :---- | :------------- | :-------- | :--------- |
| 1 | 11 | 2.9 | 7.5 | 4.0 |
| 3-4 | 10 | 4.2 | 8.7 | 4.9 |
| 5-9 | 12 | 4.4 | 8.7 | 4.9 |
| 10-11 | 18 | 6.7 | 11.7 | 7.0 |
| 12-17 | 17 | 23.7 | 24.4 | 15.9 |
| 1 ([`SovChLit`](../datasets/sovchlit.md)) | 179 | 1.5 | 6.1 | 3.1 |

On school texts (labels 1-11) the test with the `fiction` preset is about four grades above the label (median deviation +3.9 against −0.9 for `plainrussian` and −0.2 for `academic`), and about five on the first-grade reader `SovChLit`. Its value should therefore not be read as a grade of the Russian school: for the grade of the reader use `plainrussian` (the default; its coefficients were fitted on `TextsByGrade`) or `academic`, and `fiction` to compare with works that use Oborneva's coefficients. The consensus grade depends on the preset less, since the Flesch-Kincaid test is only one of its formulas (the median on `TextsByGrade` is 7.75 for `fiction` against 6.75 for `plainrussian`).

## Metrics

A formula is computed by the function of its card on the counts of `bs`; the default coefficients of the functions are adapted for Russian. The core formulas take their coefficients from `coefficients`, where the preset sets those of the Flesch-Kincaid test, the Flesch index and the Coleman-Liau, SMOG and ARI indices, while the formulas of Solovyev, Ivanov and Solnyshkina, of Matskovsky and of Dale-Chall are computed with the coefficients of their functions, and `coefficients` does not affect them. A formula of counts gives `nan` when the number of words or of sentences it divides by is zero. The formulas of other languages, with their original coefficients and without a calibration for Russian, are computed by the [`UnadaptedReadabilityStats`](unadapted_readability_stats.md) class.

| Metric | Measures | Range | Higher means |
| :----- | :------- | :---- | :----------- |
| [`flesch_kincaid_grade`](#flesch_kincaid_grade) | Grade by the sentence length and the syllables per word | Years of schooling, below 0 for the simplest texts | A harder text |
| [`flesch_reading_easy`](#flesch_reading_easy) | Ease of reading by the sentence length and the syllables per word | Nominally 0-100, above 100 for the simplest texts and below 0 for the hardest | An easier text |
| [`coleman_liau_index`](#coleman_liau_index) | Grade by the letters and the sentences per 100 words | Years of schooling, below 0 for the simplest texts | A harder text |
| [`smog_index`](#smog_index) | Grade by the complex words per sentence | Years of schooling | A harder text |
| [`automated_readability_index`](#automated_readability_index) | Grade by the letters per word and the sentence length | Years of schooling, below 0 for the simplest texts | A harder text |
| [`lix`](#lix) | Sentence length and the share of long words | 0 and above | A harder text |
| [`rix`](#rix) | Long words per sentence | 0 and above | A harder text |
| [`sis_grade`](#sis_grade) | Grade by the sentence length and the letters per word | School grade, below 0 for the simplest texts | A harder text |
| [`matskovsky_index`](#matskovsky_index) | Sentence length and the share of complex words | 0 and above | A harder text |
| [`tuldava`](#tuldava) | Syllables per word and the logarithm of the sentence length | 0 and above | A harder text |
| [`dale_chall_index`](#dale_chall_index) | Grade by the share of complex words and the sentence length | Years of schooling | A harder text |
| [`gunning_fog_index`](#gunning_fog_index) | Grade by the sentence length and the share of complex words | Years of schooling | A harder text |
| [`consensus_grade`](#consensus_grade) | Median of the grade formulas and the reading ease as a grade | Years of schooling, below 0 for the simplest texts | A harder text |
| [`reading_time`](#reading_time) | Reading time at the reading speed (`reading_speed`) | Minutes, above 0 | A longer text |
| [`mu_index`](#mu_index) | Mean word length in letters against its variance; outside `get_stats` | Above 0, `nan` with fewer than two words or without variability | An easier text |

<div class="metric-card" markdown>

### Flesch-Kincaid grade { #flesch_kincaid_grade }

`flesch_kincaid_grade` · Kincaid et al., 1975
{ .metric-meta }

``` {.python .signature}
calc_flesch_kincaid_grade(n_syllables, n_words, n_sents, a=0.318, b=14.2, c=30.5)
```

--8<-- "stats/readability_stats.md:calc_flesch_kincaid_grade"

The default coefficients come from the current version of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project. Other coefficients for Russian are given by the [presets](#presets): Oborneva's (`0.5`, `8.4`, `15.59`) and FKG_SIS of Solovyev, Ivanov and Solnyshkina (`0.36`, `5.76`, `11.97`).

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_syllables` | `int` | - | Number of syllables |
| `n_words` | `int` | - | Number of words |
| `n_sents` | `int` | - | Number of sentences |
| `a` | `float` | `0.318` | Coefficient a, at the mean sentence length |
| `b` | `float` | `14.2` | Coefficient b, at the mean word length |
| `c` | `float` | `30.5` | Coefficient c, the constant |

</div>

<div class="metric-card" markdown>

### Flesch reading ease { #flesch_reading_easy }

`flesch_reading_easy` · Flesch, 1948
{ .metric-meta }

``` {.python .signature}
calc_flesch_reading_easy(n_syllables, n_words, n_sents, a=1.3, b=60.1, c=206.835)
```

--8<-- "stats/readability_stats.md:calc_flesch_reading_easy"

The default coefficients are Oborneva's (2005/2006, variant A). Variant B of the same works (`1.52`, `65.14`, `206.836`), used by the Kazan group, is given by the `academic` preset.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_syllables` | `int` | - | Number of syllables |
| `n_words` | `int` | - | Number of words |
| `n_sents` | `int` | - | Number of sentences |
| `a` | `float` | `1.3` | Coefficient a, at the mean sentence length |
| `b` | `float` | `60.1` | Coefficient b, at the mean word length |
| `c` | `float` | `206.835` | Coefficient c, the constant |

The bands of `describe` are the scale `ruts.constants.READING_EASE_LEVELS`:

| Value | Reading |
| :---- | :------ |
| `[90, ∞)` | 5th grade |
| `[80, 90)` | 6th grade |
| `[70, 80)` | 7th grade |
| `[60, 70)` | 8th and 9th grade |
| `[50, 60)` | 10th and 11th grade |
| `[30, 50)` | university |
| `(−∞, 30)` | university graduate |

</div>

<div class="metric-card" markdown>

### Coleman-Liau index { #coleman_liau_index }

`coleman_liau_index` · Coleman and Liau, 1975
{ .metric-meta }

``` {.python .signature}
calc_coleman_liau_index(n_letters, n_words, n_sents, a=0.055, b=0.35, c=20.33)
```

--8<-- "stats/readability_stats.md:calc_coleman_liau_index"

The default coefficients come from the [Plain Russian Language](https://github.com/infoculture/plainrussian) project.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_letters` | `int` | - | Number of letters of the words |
| `n_words` | `int` | - | Number of words |
| `n_sents` | `int` | - | Number of sentences |
| `a` | `float` | `0.055` | Coefficient a, at the letters per 100 words |
| `b` | `float` | `0.35` | Coefficient b, at the sentences per 100 words |
| `c` | `float` | `20.33` | Coefficient c, the constant |

</div>

<div class="metric-card" markdown>

### SMOG index { #smog_index }

`smog_index` · McLaughlin, 1969
{ .metric-meta }

``` {.python .signature}
calc_smog_index(n_complex, n_sents, a=1.1, b=64.6, c=0.05)
```

--8<-- "stats/readability_stats.md:calc_smog_index"

The default coefficients of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project were fitted for complex words of five or more syllables, so `ReadabilityStats` passes the number of words of at least 5 syllables to the function (`ruts.constants.SMOG_COMPLEX_SYL_FACTOR`) rather than the `n_complex_words` attribute of the basic statistics.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_complex` | `int` | - | Number of complex words |
| `n_sents` | `int` | - | Number of sentences |
| `a` | `float` | `1.1` | Coefficient a, at the square root |
| `b` | `float` | `64.6` | Coefficient b, under the square root |
| `c` | `float` | `0.05` | Coefficient c, the constant |

</div>

<div class="metric-card" markdown>

### Automated readability index (ARI) { #automated_readability_index }

`automated_readability_index` · Smith and Senter, 1967
{ .metric-meta }

``` {.python .signature}
calc_automated_readability_index(n_letters, n_words, n_sents, a=6.26, b=0.2805, c=31.04)
```

--8<-- "stats/readability_stats.md:calc_automated_readability_index"

The default coefficients come from the [Plain Russian Language](https://github.com/infoculture/plainrussian) project.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_letters` | `int` | - | Number of letters of the words |
| `n_words` | `int` | - | Number of words |
| `n_sents` | `int` | - | Number of sentences |
| `a` | `float` | `6.26` | Coefficient a, at the letters per word |
| `b` | `float` | `0.2805` | Coefficient b, at the mean sentence length |
| `c` | `float` | `31.04` | Coefficient c, the constant |

The grade can be read as reader age:

| Value | Age |
| :---- | :-- |
| `1` | 6-7 years |
| `2` | 7-8 years |
| `3` | 8-9 years |
| `4` | 9-10 years |
| `5` | 10-11 years |
| `6` | 11-12 years |
| `7` | 12-13 years |
| `8` | 13-14 years |
| `9` | 14-15 years |
| `10` | 15-16 years |
| `11` | 16-17 years |
| `12` | 17-18 years |
| `13` | 18-24 years |
| `14` | 24+ years |

</div>

<div class="metric-card" markdown>

### LIX readability index { #lix }

`lix` · Björnsson, 1968
{ .metric-meta }

--8<-- "stats/readability_stats.md:calc_lix"

These bands are the scale of `describe`, `ruts.constants.LIX_LEVELS`; its last band is open above. The `n_long_words` attribute of the basic statistics of ruTS counts words of six or more letters, so `ReadabilityStats` passes the number of words of at least 7 letters to the function.

</div>

<div class="metric-card" markdown>

### RIX readability index { #rix }

`rix` · Anderson, 1983
{ .metric-meta }

--8<-- "stats/readability_stats.md:calc_rix"

As for LIX, `ReadabilityStats` passes the number of words of at least 7 letters to the function. The bands of `describe` are the grades of Anderson as the grades of the Russian school (`ruts.constants.RIX_LEVELS`); it has no 12th grade, and its band joins the 11th:

| Value | Reading |
| :---- | :------ |
| `[0, 0.2)` | 1st grade |
| `[0.2, 0.5)` | 2nd grade |
| `[0.5, 0.8)` | 3rd grade |
| `[0.8, 1.3)` | 4th grade |
| `[1.3, 1.8)` | 5th grade |
| `[1.8, 2.4)` | 6th grade |
| `[2.4, 3.0)` | 7th grade |
| `[3.0, 3.7)` | 8th grade |
| `[3.7, 4.5)` | 9th grade |
| `[4.5, 5.3)` | 10th grade |
| `[5.3, 7.2)` | 11th grade |
| `[7.2, ∞)` | university and above |

</div>

<div class="metric-card" markdown>

### Solovyev, Ivanov and Solnyshkina formula { #sis_grade }

`sis_grade` · `sis_grade_by_stage(stage)` · [Solovyev, Ivanov, Solnyshkina, 2023](http://ftp.pdmi.ras.ru/pub/publicat/znsl/v529/p140.pdf)
{ .metric-meta }

``` {.python .signature}
calc_sis_grade(n_letters, n_words, n_sents, a=-17.5, b=0.56, c=2.45)
```

The school grade needed to read a Russian academic text, by the mean sentence length in words and the mean word length in letters, not in syllables as in the Flesch-Kincaid test. The formula was derived on the Russian Academic Corpus of 154 textbooks for grades 2-11 (5.7 million tokens); the mean error is about one grade. The authors computed the mean sentence length over spaCy tokens, which include punctuation, so the ruTS computation over words gives a slightly lower grade.

$$
a + b \cdot \frac{\textrm{Number of words}}{\textrm{Number of sentences}} + c \cdot \frac{\textrm{Number of letters}}{\textrm{Number of words}}
$$

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_letters` | `int` | - | Number of letters of the words |
| `n_words` | `int` | - | Number of words |
| `n_sents` | `int` | - | Number of sentences |
| `a` | `float` | `-17.5` | Coefficient a, the constant |
| `b` | `float` | `0.56` | Coefficient b, at the mean sentence length |
| `c` | `float` | `2.45` | Coefficient c, at the mean word length |

The default coefficients are those of the general formula. The coefficients the authors give for the education stages are in the `ruts.constants.SIS_GRADE_STAGES` table, taken by the [`sis_grade_by_stage`](#sis_grade_by_stage) method:

| Stage | a | b | c |
| :---- | :- | :- | :- |
| grades 2-4 | `-2.59` | `0.17` | `0.61` |
| grades 5-7 | `-5.29` | `0.20` | `1.34` |
| grades 8-11 | `-3.26` | `0.21` | `1.35` |

</div>

<div class="metric-card" markdown>

### Solovyev, Ivanov and Solnyshkina formula with frequency { #calc_sis_grade_freq }

`sis_grade_by_freq(mean_ipm, stage)` · [Solovyev, Ivanov, Solnyshkina, 2023](http://ftp.pdmi.ras.ru/pub/publicat/znsl/v529/p140.pdf)
{ .metric-meta }

``` {.python .signature}
calc_sis_grade_freq(n_letters, n_words, n_sents, mean_ipm, a=-14.46, b=0.58, c=2.15, d=-0.0026)
```

The variant of the general formula with a fourth feature FREQ2 - the mean frequency of the words of the text by the Lyashevskaya and Sharoff dictionary (table 7 of the paper): the more frequent the words, the lower the grade. In the paper FREQ2 values lie within 200-1000, which corresponds to the mean frequency of content words (`LexicalStats.mean_ipm_content`); the mean over all words including conjunctions and prepositions is several times larger. On the [`TextsByGrade`](../datasets/textsbygrade.md) dataset the formula with frequency gives the same correlation with the grade as the formula without it (Spearman's ρ 0.76 against 0.77), as in the paper.

$$
a + b \cdot \frac{\textrm{Number of words}}{\textrm{Number of sentences}} + c \cdot \frac{\textrm{Number of letters}}{\textrm{Number of words}} + d \cdot \textrm{FREQ2}
$$

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_letters` | `int` | - | Number of letters of the words |
| `n_words` | `int` | - | Number of words |
| `n_sents` | `int` | - | Number of sentences |
| `mean_ipm` | `float` | - | Mean frequency of content words (ipm) |
| `a` | `float` | `-14.46` | Coefficient a, the constant |
| `b` | `float` | `0.58` | Coefficient b, at the mean sentence length |
| `c` | `float` | `2.15` | Coefficient c, at the mean word length |
| `d` | `float` | `-0.0026` | Coefficient d, at the mean frequency |

The default coefficients are those of the general formula. The coefficients of the education stages from the same table are in the `ruts.constants.SIS_GRADE_FREQ_STAGES` table, taken by the `stage` parameter of the [`sis_grade_by_freq`](#sis_grade_by_freq) method:

| Stage | a | b | c | d |
| :---- | :- | :- | :- | :- |
| grades 2-4 | `-1.21` | `0.2` | `0.56` | `-0.0025` |
| grades 5-7 | `-5.18` | `0.17` | `1.35` | `-0.00043` |
| grades 8-11 | `1.3` | `0.23` | `0.88` | `-0.0035` |

=== "Code"

    ``` python
    from ruts import LexicalStats, ReadabilityStats

    text = "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул."
    rs = ReadabilityStats(text)
    rs.sis_grade, rs.sis_grade_by_stage("2-4")
    rs.sis_grade_by_freq(LexicalStats(text).mean_ipm_content)
    ```

=== "Result"

    ```
    (-4.625384615384615, 0.8142307692307695)
    -3.106298290598293
    ```

</div>

<div class="metric-card" markdown>

### Matskovsky formula { #matskovsky_index }

`matskovsky_index` · Matskovsky, 1976
{ .metric-meta }

``` {.python .signature}
calc_matskovsky_index(n_complex, n_words, n_sents, a=0.62, b=0.123, c=0.051)
```

The first readability formula for Russian, derived by the method of successive intervals - by the mean sentence length and the percentage of complex words. A complex word here has more than three syllables, so `ReadabilityStats` passes the number of words of at least 4 syllables to the function.

$$
a \cdot \frac{\textrm{Number of words}}{\textrm{Number of sentences}} + b \cdot \frac{100 \cdot \textrm{Number of complex words}}{\textrm{Number of words}} + c
$$

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_complex` | `int` | - | Number of complex words |
| `n_words` | `int` | - | Number of words |
| `n_sents` | `int` | - | Number of sentences |
| `a` | `float` | `0.62` | Coefficient a, at the mean sentence length |
| `b` | `float` | `0.123` | Coefficient b, at the share of complex words |
| `c` | `float` | `0.051` | Coefficient c, the constant |

</div>

<div class="metric-card" markdown>

### Tuldava formula { #tuldava }

`tuldava` · Tuldava, 1975
{ .metric-meta }

``` {.python .signature}
calc_tuldava(n_syllables, n_words, n_sents)
```

The text difficulty formula of Tuldava ("Ob izmerenii trudnosti tekstov" - "On measuring the difficulty of texts", Uchenye zapiski Tartuskogo universiteta, issue 345, 1975, pp. 102-120) as given by [Ivanov, Solnyshkina and Solovyev (2018)](https://dialogue-conf.org/media/4302/ivanovvv.pdf): the mean number of syllables per word times the decimal logarithm of the mean sentence length in words; there are no coefficients to fit. The formula has no scale and no conversion to a grade: it does not enter the consensus grade, and `describe` gives `None`. koRpus computes it with the natural logarithm.

$$
\frac{\textrm{Number of syllables}}{\textrm{Number of words}} \cdot \lg \frac{\textrm{Number of words}}{\textrm{Number of sentences}}
$$

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_syllables` | `int` | - | Number of syllables |
| `n_words` | `int` | - | Number of words |
| `n_sents` | `int` | - | Number of sentences |

=== "Code"

    ``` python
    from ruts import ReadabilityStats
    from ruts.readability_stats import calc_tuldava

    calc_tuldava(n_syllables=200, n_words=100, n_sents=10)
    rs = ReadabilityStats("Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул.")
    rs.tuldava, rs.describe("tuldava")
    ```

=== "Result"

    ```
    2.0
    (1.3131677299615359, None)
    ```

</div>

<div class="metric-card" markdown>

### Dale-Chall index { #dale_chall_index }

`dale_chall_index` · [Dale and Chall, 1948](https://en.wikipedia.org/wiki/Dale–Chall_readability_formula)
{ .metric-meta }

``` {.python .signature}
calc_dale_chall_index(n_complex, n_words, n_sents, a=0.552, b=0.273)
```

The years of schooling in the US system needed to understand the text, by the percentage of complex words and the mean sentence length. The original formula takes the share of unfamiliar words by a list of 3000 familiar ones; no such free list exists for Russian, so the adaptation of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project with the share of complex words is applied. A complex word has five or more syllables, so `ReadabilityStats` passes the number of words of at least 5 syllables to the function (`ruts.constants.SMOG_COMPLEX_SYL_FACTOR`). The original coefficients of the formula are `0.1579` and `0.0496`.

$$
a \cdot \frac{100 \cdot \textrm{Number of complex words}}{\textrm{Number of words}} + b \cdot \frac{\textrm{Number of words}}{\textrm{Number of sentences}}
$$

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_complex` | `int` | - | Number of complex words |
| `n_words` | `int` | - | Number of words |
| `n_sents` | `int` | - | Number of sentences |
| `a` | `float` | `0.552` | Coefficient a, at the share of complex words |
| `b` | `float` | `0.273` | Coefficient b, at the mean sentence length |

</div>

<div class="metric-card" markdown>

### Gunning fog index { #gunning_fog_index }

`gunning_fog_index` · Gunning, 1952
{ .metric-meta }

``` {.python .signature}
calc_gunning_fog_index(n_complex, n_words, n_sents, a=0.4)
```

--8<-- "stats/readability_stats.md:calc_gunning_fog_index"

The index is used in the adaptation of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project: a complex word has five or more syllables, so `ReadabilityStats` passes the number of words of at least 5 syllables to the function (`ruts.constants.SMOG_COMPLEX_SYL_FACTOR`). SEO services additionally multiply the result by `0.78`; no justification for this multiplier has been published.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_complex` | `int` | - | Number of complex words |
| `n_words` | `int` | - | Number of words |
| `n_sents` | `int` | - | Number of sentences |
| `a` | `float` | `0.4` | Coefficient a |

</div>

<div class="metric-card" markdown>

### Consensus grade { #consensus_grade }

`consensus_grade`
{ .metric-meta }

--8<-- "stats/readability_stats.md:ReadabilityStats-consensus"

The grade formulas of ruTS (`ruts.constants.READABILITY_GRADE_STATS`) are the Flesch-Kincaid test, the Coleman-Liau, SMOG, ARI, Dale-Chall and Gunning indices and the Solovyev, Ivanov and Solnyshkina formula, and the Flesch index is converted to a grade by the bands of its reading scale, so an index of 45 reads as university both in `describe` and in the consensus grade. The consensus grade is an analog of `text_standard` of textstat, which takes the mode instead of the median; the median is more robust to the outliers of individual formulas.

--8<-- "stats/readability_stats.md:calc_consensus_grade"

``` {.python .signature}
flesch_reading_easy_to_grade(flesch_reading_easy, grades=((90, 5), (80, 6), (70, 7), (60, 8.5), (50, 10.5), (30, 14), (0, 17)), below=17)
```

--8<-- "stats/readability_stats.md:flesch_reading_easy_to_grade"

The default bands of ruTS are the bands of the reading scale of the index (`READING_EASE_LEVELS`), so that the consensus grade and `describe` read a value alike: 8.5 and 10.5 are the middles of the bands "8th and 9th grade" and "10th and 11th grade", 14 is "university" and 17 is "university graduate", that is university years 1-3 and 4-6 by the [table of stages](#grade_to_age). These bands are `ruts.constants.READING_EASE_GRADES`, the `reading_ease_grades` attribute of `ReadabilityStats`:

| Flesch index | Grade |
| :----------- | :---- |
| `[90, ∞)` | 5 |
| `[80, 90)` | 6 |
| `[70, 80)` | 7 |
| `[60, 70)` | 8.5 |
| `[50, 60)` | 10.5 |
| `[30, 50)` | 14 |
| `(−∞, 30)` | 17 |

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `flesch_reading_easy` | `float` | - | Value of the reading ease |
| `grades` | `list[tuple[float, float]]` | `READING_EASE_GRADES` | Lower bounds and their grades in descending order of the bounds |
| `below` | `float` | `17` | Grade below the last bound |

</div>

<div class="metric-card" markdown>

### Reading time { #reading_time }

`reading_time` · `reading_time_by_speed(wpm)` · `reading_time_by_norm(norm)` · Kuznetsov and Khromov, 1991
{ .metric-meta }

``` {.python .signature}
calc_reading_time(n_words, wpm=180, *, messages=CORE_MESSAGES)
```

--8<-- "stats/readability_stats.md:calc_reading_time"

The silent reading norm of an adult is 120-180 words per minute (Kuznetsov and Khromov, 1991); the upper bound is the default. The norms are in the `ruts.constants.READING_SPEED_NORMS` table, the reading-aloud norms of primary school by the Russian federal standard among them:

| Norm | Words per minute |
| :--- | :--------------- |
| `adult_silent` | 120-180 |
| `grade_1` | 25-40 |
| `grade_2` | 60-80 |
| `grade_3` | 80-100 |
| `grade_4` | 90-110 |

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_words` | `int` | - | Number of words |
| `wpm` | `float` | `180` | Reading speed, words per minute (`READING_SPEED_WPM`) |
| `messages` | `dict[str, str]` | `CORE_MESSAGES` | Messages of the errors by key, a keyword |

</div>

<div class="metric-card" markdown>

### Legibilidad µ { #mu_index }

`mu_index` · Muñoz Baquedano and Muñoz Urra, 2006
{ .metric-meta }

The mean number of letters per word divided by its sample variance, times 100; there are no coefficients to fit. Words without letters (numbers) are left out; with fewer than two words or without variability the index is undefined (`nan`).

$$
100 \cdot \frac{\bar{x}}{s^2}, \quad s^2 = \frac{\sum (x_i - \bar{x})^2}{n - 1}
$$

where $x_i$ is the number of letters of a word and $n$ the number of words.

The index was fitted on Spanish texts, so it stays outside the `get_stats` of ruTS, though the object has the `mu_index` property. Its function is [`calc_mu_index`](https://sergeyshk.github.io/anyTS/stats/readability_stats/#mu_index) of the anyTS core.

</div>

## Methods

--8<-- "stats/readability_stats.md:ReadabilityStats-describe_grade"

--8<-- "stats/readability_stats.md:ReadabilityStats-describe_level"

--8<-- "stats/readability_stats.md:ReadabilityStats-describe"

--8<-- "stats/readability_stats.md:ReadabilityStats-reading_time_by_speed"

--8<-- "stats/readability_stats.md:ReadabilityStats-reading_time_by_norm"

In ruTS the norms come from the `ruts.constants.READING_SPEED_NORMS` table, and the method returns the reading times at the upper and at the lower bound of the norm.

`sis_grade_by_stage(stage)` returns the value of the [Solovyev, Ivanov and Solnyshkina formula](#sis_grade) with the coefficients of the education stage `stage`: `2-4`, `5-7` or `8-11`; an unknown stage raises `ParameterError`.
{ #sis_grade_by_stage }

`sis_grade_by_freq(mean_ipm, stage=None)` returns the value of the [formula with frequency](#calc_sis_grade_freq) at the mean frequency of content words `mean_ipm` - the [`mean_ipm_content`](lexical_stats.md#frequency) attribute of `LexicalStats` - with the coefficients of the stage `stage` or, without it, of the general formula. A negative or infinite frequency, a frequency that is not a number and an unknown stage raise `ParameterError`, and `nan` gives `nan`.
{ #sis_grade_by_freq }

--8<-- "stats/readability_stats.md:ReadabilityStats-get_stats"

--8<-- "stats/readability_stats.md:ReadabilityStats-print_stats"

=== "Code"

    ``` python
    from ruts import ReadabilityStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    rs = ReadabilityStats(text)
    rs.describe_grade(), rs.describe_grade("gunning_fog_index")
    rs.describe("flesch_reading_easy"), rs.describe_level("lix")
    rs.describe("rix"), rs.describe("matskovsky_index")
    rs.reading_time_by_speed(120), rs.reading_time_by_norm("grade_1")
    rs.get_stats()
    ```

=== "Result"

    ```
    ('1-3-й класс (6-8 лет)', '4-6-й класс (9-11 лет)')
    ('6-й класс', 'очень простые тексты, детские книги')
    ('6-й класс', None)
    (0.125, (0.375, 0.6))
    {'flesch_kincaid_grade': -2.0633333333333326,
     'flesch_reading_easy': 87.16833333333334,
     'coleman_liau_index': 1.1700000000000053,
     'smog_index': 0.05,
     'automated_readability_index': 0.2941666666666656,
     'lix': 28.333333333333336,
     'rix': 2.0,
     'sis_grade': 1.5166666666666675,
     'matskovsky_index': 9.351,
     'tuldava': 1.9601520984261356,
     'dale_chall_index': 4.095000000000001,
     'gunning_fog_index': 6.0,
     'consensus_grade': 1.5,
     'reading_time': 0.08333333333333333}
    ```

The `to_dataframe` method is that of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core.

## Scales { #scales }

The `describe_level` method reads the Flesch index, LIX and RIX by the scales of bands of their cards (`ruts.constants.READABILITY_LEVEL_SCALES`), and `describe` reads any metric: these three by the same scales, the grade formulas and the consensus grade by the education stages of [`grade_to_age`](#grade_to_age); for a metric without a scale it gives `None`.

### School stage and age { #grade_to_age }

``` {.python .signature}
grade_to_age(grade, levels=((1, 3, '1-3-й класс', '6-8 лет'), (4, 6, '4-6-й класс', '9-11 лет'), (7, 9, '7-9-й класс', '12-14 лет'), (10, 11, '10-11-й класс', '15-16 лет'), (12, 14, '1-3-й курс вуза', '17-19 лет'), (15, 17, '4-6-й курс вуза', '20-22 года')), above=('аспирантура', 'старше 22 лет'))
```

--8<-- "stats/readability_stats.md:grade_to_age"

The default stages of ruTS are taken from the `GRADE_TEXT` table of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project (`ruts.constants.GRADE_AGE_LEVELS` and `POSTGRADUATE_LEVEL`):

| Grade | Stage | Age |
| :---- | :---- | :-- |
| 1-3 | grades 1-3 | 6-8 years |
| 4-6 | grades 4-6 | 9-11 years |
| 7-9 | grades 7-9 | 12-14 years |
| 10-11 | grades 10-11 | 15-16 years |
| 12-14 | university years 1-3 | 17-19 years |
| 15-17 | university years 4-6 | 20-22 years |
| above 17 | postgraduate | over 22 years |

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `grade` | `float` | - | Value of a grade formula |
| `levels` | `list[tuple[int, int, str, str]]` | `GRADE_AGE_LEVELS` | Stages as the first and the last year, the stage and the age, in ascending order |
| `above` | `tuple[str, str]` | `POSTGRADUATE_LEVEL` | Stage and age above the last stage |

### Band of a scale { #scale_level }

--8<-- "stats/readability_stats.md:scale_level"

The scales of ruTS are `ruts.constants.READING_EASE_LEVELS`, `LIX_LEVELS` and `RIX_LEVELS`.

=== "Code"

    ``` python
    from ruts.constants import READING_EASE_LEVELS
    from ruts.readability_stats import calc_flesch_reading_easy, scale_level

    flesch = calc_flesch_reading_easy(n_syllables=60, n_words=30, n_sents=2)
    flesch, scale_level(flesch, READING_EASE_LEVELS)
    ```

=== "Result"

    ```
    (67.135, '8-й и 9-й класс')
    ```

## Stage norms { #level_norms }

The consensus grade tells which stage a text is for, but not what a text of that stage is like. For this the `ruts.constants.LEVEL_NORMS` table holds the norms of the features of the stages: the usual ranges (quartiles) of the sentence length in words, the word length in letters, the share of words of five or more syllables and the lexical diversity MTLD of texts of at least 100 words labeled with the stage in the [`SovChLit`](../datasets/sovchlit.md) and [`TextsByGrade`](../datasets/textsbygrade.md) datasets. School stages with at least 10 such texts have norms:

| Stage | Texts | Words per sentence | Letters per word | Share of words of 5+ syllables | MTLD |
| :---- | :---- | :----------------- | :--------------- | :----------------------------- | :--- |
| grades 1-3 | 73 | 8.1-10.7 | 4.56-5.03 | 0.0-0.022 | 104-178 |
| grades 4-6 | 12 | 10.2-14.6 | 5.16-5.33 | 0.039-0.052 | 220-373 |
| grades 10-11 | 18 | 15.6-17.9 | 5.11-5.57 | 0.035-0.065 | 277-513 |

The norms of grades 1-3 come almost entirely from texts of grade 1 (70 of 73), so a text for grades 2-3 can come out above the norm, the sentence length above all. Grades 7-9 have seven texts in the datasets, and the university labels of `TextsByGrade` mark a Wikipedia article, a newspaper article and regulatory documents, not texts written for students of a given year, so these stages have no norms. The features of a text shorter than 100 words, MTLD above all, should not be compared with the norms.

### Features of a text { #level_features }

``` {.python .signature}
level_features(source)
```

The features of a text that the stage norms cover: words per sentence, letters per word (of the words the grade formulas count), the share of words of five or more syllables (the complex words of SMOG, Gunning fog and Dale-Chall) and the lexical diversity MTLD. They are computed the same way as for the norms, so they can be compared with them; the features of a `Doc` are computed from its text, not from the sentence boundaries of spaCy. A source that is neither a string nor a `Doc` raises `SourceTypeError`, a source without words or sentences `SourceError`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Data source (a string or a Doc object) |

### Norms and the reading of a feature { #describe_level_norm }

``` {.python .signature}
level_norms(grade)
```

The norms of the features of the stage a grade belongs to - the usual range (quartiles) of each feature of `level_features` - or `None` for a stage without norms. A grade belongs to a stage as in [`grade_to_age`](#grade_to_age): it is rounded half up, and a grade below 1 belongs to the first stage. A grade that is not a finite number raises `ParameterError`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `grade` | `float` | - | Grade of the reader or consensus grade of a text |

``` {.python .signature}
describe_level_norm(stat, value, grade)
```

The reading of a feature of a text by the norms of the stage a grade belongs to: «ниже нормы ступени» (below), «в норме ступени» (between the quartiles, inclusive) or «выше нормы ступени» (above), the bands of `ruts.constants.LEVEL_NORM_BANDS`. A stage without norms and an undefined value (nan) give `None`, an unknown feature raises `UnknownStatError`, and a value that is not a number and a grade that is not a finite number raise `ParameterError`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `stat` | `str` | - | Name of a feature of `ruts.constants.LEVEL_NORMS_DESC` |
| `value` | `float` | - | Value of the feature |
| `grade` | `float` | - | Grade of the reader or consensus grade of a text |

=== "Code"

    ``` python
    from ruts.datasets import SovChLit
    from ruts.readability_stats import describe_level_norm, level_features, level_norms

    level_norms(2)["words_per_sent"], level_norms(8)
    text = next(SovChLit().get_texts())
    features = level_features(text)
    {stat: describe_level_norm(stat, value, 1) for stat, value in features.items()}
    ```

=== "Result"

    ```
    ((8.1, 10.7), None)
    {'words_per_sent': 'выше нормы ступени',
     'letters_per_word': 'выше нормы ступени',
     'p_smog_complex_words': 'выше нормы ступени',
     'mtld': 'в норме ступени'}
    ```
