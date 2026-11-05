# Readability metrics

``` {.python .signature}
ReadabilityStats(source, sents_extractor=None, words_extractor=None, preset='plainrussian')
```

--8<-- "stats/readability_stats.md:ReadabilityStats"

The class extends the `ReadabilityStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/readability_stats/) core for Russian: the [basic statistics](basic_stats.md) of ruTS with the Russian [`SentsExtractor`](../extractors/sentences.md) and [`WordsExtractor`](../extractors/words.md) by default, the coefficient [presets](#presets), the Russian formulas, scales and reading speeds. The `print_stats` table and the error messages are in Russian.

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

The object keeps the basic statistics of the text in `bs`, the name of the preset in `preset` (read-only) and the coefficients of the preset in `coefficients`, a copy that can be changed for one object. The basic statistics can be passed to an object of another preset: `ReadabilityStats(rs.bs, preset="fiction")`.

## Coefficient presets { #presets }

The presets differ in the coefficients of the Flesch-Kincaid test and the Flesch index; the coefficients of the Coleman-Liau, SMOG and ARI indices in all presets come from the plainrussian project, and the other formulas do not depend on the preset.

| Preset | Source | Corpus | Flesch-Kincaid test | Flesch index |
| :----- | :----- | :----- | :------------------ | :----------- |
| `plainrussian` | [Plain Russian Language](https://github.com/infoculture/plainrussian) (Begtin) | 68 grade-labeled texts | `0.318·ASL + 14.2·ASW − 30.5` | `206.835 − 1.3·ASL − 60.1·ASW` (Oborneva, variant A) |
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

On the [`TextsByGrade`](../datasets/textsbygrade.md) dataset, on which the coefficients of `plainrussian` were fitted, the presets agree with the grade label alike - the Spearman correlation of the Flesch-Kincaid test is for `plainrussian` 0.80, for `fiction` and `academic` 0.79, - but give different scales, the medians of the test by label group:

| Label | Texts | `plainrussian` | `fiction` | `academic` |
| :---- | :---- | :------------- | :-------- | :--------- |
| 1 | 11 | 2.6 | 6.9 | 3.6 |
| 3-4 | 10 | 4.1 | 8.6 | 4.8 |
| 5-9 | 12 | 4.4 | 8.6 | 4.8 |
| 10-11 | 18 | 6.9 | 11.9 | 7.2 |
| 12-17 | 17 | 23.7 | 24.4 | 15.9 |
| 1 ([`SovChLit`](../datasets/sovchlit.md)) | 179 | 1.3 | 6.0 | 3.0 |

On school texts (labels 1-11) the test with the `fiction` preset is about four grades above the label (median deviation +3.7 against −1.0 for `plainrussian` and −0.1 for `academic`). For the grade of the reader use `plainrussian` or `academic`, and `fiction` to compare with works on Oborneva's coefficients. The consensus grade depends on the preset less: its median on `TextsByGrade` is 7.75 for `fiction` and 6.75 for `plainrussian`.

## Metrics

A formula is computed by the function of its card on the counts of `bs`. The core formulas take their coefficients from `coefficients`, while the formulas of Solovyev, Ivanov and Solnyshkina, of Matskovsky and of Dale-Chall take those of their functions, and `coefficients` does not affect them. A formula gives `nan` when the number of words or of sentences it divides by is zero. The formulas of other languages with their original coefficients are computed by the [`UnadaptedReadabilityStats`](unadapted_readability_stats.md) class.

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

The default coefficients come from the [Plain Russian Language](https://github.com/infoculture/plainrussian) project, other ones are given by the [presets](#presets).

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

The default coefficients are Oborneva's (2005/2006, variant A), variant B is given by the `academic` preset.

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

The default coefficients of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project were fitted for complex words of five or more syllables: `ReadabilityStats` passes the number of such words to the function (`ruts.constants.SMOG_COMPLEX_SYL_FACTOR`) rather than the `n_complex_words` of the basic statistics.

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

These bands are the scale of `describe` (`ruts.constants.LIX_LEVELS`), the last one open above. `ReadabilityStats` passes the number of words of at least 7 letters to the function rather than the `n_long_words` of the basic statistics of ruTS - words of six or more letters.

</div>

<div class="metric-card" markdown>

### RIX readability index { #rix }

`rix` · Anderson, 1983
{ .metric-meta }

--8<-- "stats/readability_stats.md:calc_rix"

As for LIX, `ReadabilityStats` passes the number of words of at least 7 letters to the function. The bands of `describe` (`ruts.constants.RIX_LEVELS`) are the grades of Anderson, the band of the 12th grade joining the 11th:

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

The school grade needed to read a Russian academic text, by the mean sentence length in words and the mean word length in letters. The formula was derived on the Russian Academic Corpus of 154 textbooks for grades 2-11 (5.7 million tokens); the mean error is about one grade. The authors counted the sentence length in spaCy tokens with punctuation, so the ruTS computation over words gives a slightly lower grade.

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

The default coefficients are those of the general formula, the coefficients of the education stages are in `ruts.constants.SIS_GRADE_STAGES`, taken by the [`sis_grade_by_stage`](#sis_grade_by_stage) method:

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

The variant of the general formula with a fourth feature FREQ2 - the mean frequency of the content words of the text by the Lyashevskaya and Sharoff dictionary (table 7 of the paper): the more frequent the words, the lower the grade. On the [`TextsByGrade`](../datasets/textsbygrade.md) dataset the formula with frequency correlates with the grade no better than the formula without it (Spearman's ρ 0.76 against 0.78).

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

The default coefficients are those of the general formula, the coefficients of the stages are in `ruts.constants.SIS_GRADE_FREQ_STAGES`, taken by the `stage` parameter of the [`sis_grade_by_freq`](#sis_grade_by_freq) method:

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

The first readability formula for Russian - by the mean sentence length and the percentage of complex words; `ReadabilityStats` passes the number of words of at least 4 syllables to the function.

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

The text difficulty formula of Tuldava ("Ob izmerenii trudnosti tekstov" - "On measuring the difficulty of texts", Uchenye zapiski Tartuskogo universiteta, issue 345, 1975, pp. 102-120) as given by [Ivanov, Solnyshkina and Solovyev (2018)](https://dialogue-conf.org/media/4302/ivanovvv.pdf): the mean number of syllables per word times the decimal logarithm of the mean sentence length in words; there are no coefficients to fit. The formula has no scale: it does not enter the consensus grade, and `describe` gives `None`.

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

The years of schooling needed to understand the text, by the percentage of complex words and the mean sentence length. This is the adaptation of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project: the share of unfamiliar words by a list of 3000 familiar ones is replaced by the share of words of five or more syllables, and `ReadabilityStats` passes their number to the function (`ruts.constants.SMOG_COMPLEX_SYL_FACTOR`). The original coefficients of the formula are `0.1579` and `0.0496`.

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

In the adaptation of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project a complex word has five or more syllables: `ReadabilityStats` passes the number of such words to the function (`ruts.constants.SMOG_COMPLEX_SYL_FACTOR`).

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

The grade formulas of ruTS (`ruts.constants.READABILITY_GRADE_STATS`) are the Flesch-Kincaid test, the Coleman-Liau, SMOG, ARI, Dale-Chall and Gunning indices and the Solovyev, Ivanov and Solnyshkina formula.

--8<-- "stats/readability_stats.md:calc_consensus_grade"

``` {.python .signature}
flesch_reading_easy_to_grade(flesch_reading_easy, grades=((90, 5), (80, 6), (70, 7), (60, 8.5), (50, 10.5), (30, 14), (0, 17)), below=17)
```

--8<-- "stats/readability_stats.md:flesch_reading_easy_to_grade"

The default bands of ruTS (`ruts.constants.READING_EASE_GRADES`, the `reading_ease_grades` attribute) follow the reading scale of the index; 14 and 17 are university years 1-3 and 4-6 by the [table of stages](#grade_to_age):

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

The default speed is the upper bound of the silent reading norm of an adult. The norms are in `ruts.constants.READING_SPEED_NORMS`, for primary school the reading-aloud norms of the Russian federal standard:

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

The index was fitted on Spanish texts and stays outside the `get_stats` of ruTS, but is available as the `mu_index` property; its function is [`calc_mu_index`](https://sergeyshk.github.io/anyTS/stats/readability_stats/#mu_index) of the anyTS core.

</div>

## Methods

--8<-- "stats/readability_stats.md:ReadabilityStats-describe_grade"

--8<-- "stats/readability_stats.md:ReadabilityStats-describe_level"

--8<-- "stats/readability_stats.md:ReadabilityStats-describe"

--8<-- "stats/readability_stats.md:ReadabilityStats-reading_time_by_speed"

--8<-- "stats/readability_stats.md:ReadabilityStats-reading_time_by_norm"

In ruTS the method returns the reading times at the upper and the lower bound of the norm of `ruts.constants.READING_SPEED_NORMS`.

`sis_grade_by_stage(stage)` returns the value of the [Solovyev, Ivanov and Solnyshkina formula](#sis_grade) with the coefficients of the education stage `stage`: `2-4`, `5-7` or `8-11`; an unknown stage raises `ParameterError`.
{ #sis_grade_by_stage }

`sis_grade_by_freq(mean_ipm, stage=None)` returns the value of the [formula with frequency](#calc_sis_grade_freq) at the mean frequency of content words `mean_ipm` - the [`mean_ipm_content`](lexical_stats.md#frequency) attribute of `LexicalStats` - with the coefficients of the stage `stage` or, without it, of the general formula. A negative, infinite or non-numeric frequency and an unknown stage raise `ParameterError`, and `nan` gives `nan`.
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

The scales of bands of the Flesch index, LIX and RIX are given in their cards (`ruts.constants.READABILITY_LEVEL_SCALES`), and `describe` reads the grade formulas and the consensus grade by the education stages of [`grade_to_age`](#grade_to_age).

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

The `ruts.constants.LEVEL_NORMS` table holds the norms of the features of the education stages - the usual ranges (quartiles) of the sentence length in words, the word length in letters, the share of words of five or more syllables and the lexical diversity MTLD of texts of at least 100 words labeled with the stage in the [`SovChLit`](../datasets/sovchlit.md) and [`TextsByGrade`](../datasets/textsbygrade.md) datasets. School stages with at least 10 such texts have norms:

| Stage | Texts | Words per sentence | Letters per word | Share of words of 5+ syllables | MTLD |
| :---- | :---- | :----------------- | :--------------- | :----------------------------- | :--- |
| grades 1-3 | 73 | 7.6-10.3 | 4.54-5.01 | 0.0-0.021 | 104-178 |
| grades 4-6 | 12 | 10.1-14.6 | 5.15-5.33 | 0.039-0.052 | 220-369 |
| grades 10-11 | 18 | 15.0-18.4 | 5.11-5.57 | 0.035-0.065 | 276-513 |

The norms of grades 1-3 come almost entirely from texts of grade 1 (70 of 73), so a text for grades 2-3 can come out above the norm, the sentence length above all. The features of a text shorter than 100 words, MTLD above all, should not be compared with the norms.

### Features of a text { #level_features }

``` {.python .signature}
level_features(source)
```

The features of a text that the stage norms cover - words per sentence, letters per word, the share of words of five or more syllables and MTLD - computed the same way as the norms. The features of a `Doc` are computed from its text, not from the sentence boundaries of spaCy. A source that is neither a string nor a `Doc` raises `SourceTypeError`, a source without words or sentences `SourceError`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Data source (a string or a Doc object) |

### Norms and the reading of a feature { #describe_level_norm }

``` {.python .signature}
level_norms(grade)
```

The norms (quartiles) of the features of `level_features` of the education stage a grade belongs to (as in [`grade_to_age`](#grade_to_age)), or `None` for a stage without norms. A grade that is not a finite number raises `ParameterError`.

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
    ((7.6, 10.3), None)
    {'words_per_sent': 'выше нормы ступени',
     'letters_per_word': 'выше нормы ступени',
     'p_smog_complex_words': 'выше нормы ступени',
     'mtld': 'в норме ступени'}
    ```
