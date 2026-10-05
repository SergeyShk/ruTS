# Metric functions

The coefficients of the formulas are parameters; the defaults below are those adapted for Russian. A formula of counts gives `nan` when the number of words or of sentences it divides by is zero.

## Flesch-Kincaid test

!!! info ""
    **ruts.readability_stats.calc_flesch_kincaid_grade()**

--8<-- "stats/readability_stats_funcs.md:calc_flesch_kincaid_grade"

The default coefficients come from the current version of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project. Alternative coefficients for Russian are available through [presets](readability_stats.md#presets): Oborneva (`0.5`, `8.4`, `15.59`) and FKG_SIS of Solovyev, Ivanov and Solnyshkina (`0.36`, `5.76`, `11.97`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_syllables` | int | `-` | Number of syllables |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | float | `0.318` | Coefficient a, at the mean sentence length |
| `b` | float | `14.2` | Coefficient b, at the mean word length |
| `c` | float | `30.5` | Coefficient c, the constant |

## Flesch reading ease

!!! info ""
    **ruts.readability_stats.calc_flesch_reading_easy()**

--8<-- "stats/readability_stats_funcs.md:calc_flesch_reading_easy"

The values can be interpreted as follows:

| Value | Difficulty level |
|----------|----------|
|`100.0-90.0`|	5th grade|
|`90.0-80.0`|	6th grade|
|`80.0-70.0`|	7th grade|
|`70.0-60.0`|	8th and 9th grade|
|`60.0-50.0`|	10th and 11th grade|
|`50.0-30.0`|	College|
|`30.0-0.0`|	College graduate|

Values above 100 belong to the first band and below 0 to the last; the scale is `ruts.constants.READING_EASE_LEVELS`, by which `describe_level` and `describe` read the index.

The default coefficients are Oborneva's (2005/2006, variant A). Variant B of the same works (`1.52`, `65.14`, `206.836`), used by the Kazan group, is available through the `academic` preset.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_syllables` | int | `-` | Number of syllables |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | float | `1.3` | Coefficient a, at the mean sentence length |
| `b` | float | `60.1` | Coefficient b, at the mean word length |
| `c` | float | `206.835` | Coefficient c, the constant |

## Coleman-Liau index

!!! info ""
    **ruts.readability_stats.calc_coleman_liau_index()**

--8<-- "stats/readability_stats_funcs.md:calc_coleman_liau_index"

The default coefficients come from the [Plain Russian Language](https://github.com/infoculture/plainrussian) project.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_letters` | int | `-` | Number of letters of the words |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | float | `0.055` | Coefficient a, at the letters per 100 words |
| `b` | float | `0.35` | Coefficient b, at the sentences per 100 words |
| `c` | float | `20.33` | Coefficient c, the constant |

## SMOG index

!!! info ""
    **ruts.readability_stats.calc_smog_index()**

--8<-- "stats/readability_stats_funcs.md:calc_smog_index"

!!! note "Note"
    The default coefficients of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project were fitted for complex words of five or more syllables, so [`ReadabilityStats`](readability_stats.md) passes the number of words with at least 5 syllables (`ruts.constants.SMOG_COMPLEX_SYL_FACTOR`) to the function rather than the `n_complex_words` attribute of `BasicStats`.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_complex` | int | `-` | Number of complex words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | float | `1.1` | Coefficient a, at the square root |
| `b` | float | `64.6` | Coefficient b, under the square root |
| `c` | float | `0.05` | Coefficient c, the constant |

## Automated readability index

!!! info ""
    **ruts.readability_stats.calc_automated_readability_index()**

--8<-- "stats/readability_stats_funcs.md:calc_automated_readability_index"

The grade can be read as reader age:

| Value | Age |
|----------|----------|
|`1`|	6-7 years|
|`2`|	7-8 years|
|`3`|	8-9 years|
|`4`|	9-10 years|
|`5`|	10-11 years|
|`6`|	11-12 years|
|`7`|	12-13 years|
|`8`|	13-14 years|
|`9`|	14-15 years|
|`10`|	15-16 years|
|`11`|	16-17 years|
|`12`|	17-18 years|
|`13`|	18-24 years|
|`14`|	24+ years|

The default coefficients come from the [Plain Russian Language](https://github.com/infoculture/plainrussian) project.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_letters` | int | `-` | Number of letters of the words |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | float | `6.26` | Coefficient a, at the letters per word |
| `b` | float | `0.2805` | Coefficient b, at the mean sentence length |
| `c` | float | `31.04` | Coefficient c, the constant |

## LIX readability index

!!! info ""
    **ruts.readability_stats.calc_lix()**

--8<-- "stats/readability_stats_funcs.md:calc_lix"

!!! note "Note"
    The `n_long_words` attribute of the ruTS `BasicStats` counts words of six or more letters, so [`ReadabilityStats`](readability_stats.md) passes the number of words with at least 7 letters to the function instead.

## RIX readability index

!!! info ""
    **ruts.readability_stats.calc_rix()**

--8<-- "stats/readability_stats_funcs.md:calc_rix"

!!! note "Note"
    As for LIX, [`ReadabilityStats`](readability_stats.md) passes the number of words with at least 7 letters to the function.

## Solovyev, Ivanov and Solnyshkina formula

!!! info ""
    **ruts.readability_stats.calc_sis_grade()**

Computation of the readability formula for Russian academic texts ([Solovyev, Ivanov, Solnyshkina, 2023](http://ftp.pdmi.ras.ru/pub/publicat/znsl/v529/p140.pdf)).

The formula was derived on the Russian Academic Corpus of 154 textbooks for grades 2-11 (5.7 million tokens). The result is a school grade, the mean error is about one grade. Unlike the Flesch-Kincaid test it uses the mean word length in letters rather than syllables.

The default coefficients correspond to the general formula. For individual education stages the authors give their own coefficients, available in the `ruts.constants.SIS_GRADE_STAGES` table and through the [`sis_grade_by_stage`](readability_stats.md#sis_grade_by_stage) method:

| Stage | a | b | c |
|---|---|---|---|
| grades 2-4 | `-2.59` | `0.17` | `0.61` |
| grades 5-7 | `-5.29` | `0.20` | `1.34` |
| grades 8-11 | `-3.26` | `0.21` | `1.35` |

!!! note "Note"
    The authors computed the mean sentence length over spaCy tokens, which include punctuation, so the ruTS computation over words gives a slightly lower grade.

Formula:

$$
a+b\times\frac{\textrm{Number of words}}{\textrm{Number of sentences}}+c\times\frac{\textrm{Number of letters}}{\textrm{Number of words}}
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_letters` | int | `-` | Number of letters of the words |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | float | `-17.5` | Coefficient a (intercept) |
| `b` | float | `0.56` | Coefficient b (of the mean sentence length) |
| `c` | float | `2.45` | Coefficient c (of the mean word length) |

## Solovyev, Ivanov and Solnyshkina formula with frequency { #calc_sis_grade_freq }

!!! info ""
    **ruts.readability_stats.calc_sis_grade_freq()**

Computation of the variant of the general formula with a fourth feature FREQ2 - the mean frequency of the text words by the Lyashevskaya and Sharoff dictionary ([Solovyev, Ivanov, Solnyshkina, 2023](http://ftp.pdmi.ras.ru/pub/publicat/znsl/v529/p140.pdf), table 7): the more frequent the words, the lower the grade. In the paper FREQ2 values lie within 200-1000, which corresponds to the mean frequency of content words (`LexicalStats.mean_ipm_content`); the mean over all words including conjunctions and prepositions is several times larger. On the [`TextsByGrade`](../datasets/textsbygrade.md) dataset the formula with frequency gives the same correlation with the grade as the formula without it (Spearman's ρ 0.76 vs 0.77), as in the paper.

The default coefficients correspond to the general formula; the education stage coefficients from the same table are available in the `ruts.constants.SIS_GRADE_FREQ_STAGES` table and through the `stage` parameter of the [`sis_grade_by_freq`](readability_stats.md#sis_grade_by_freq) method:

| Stage | a | b | c | d |
|---|---|---|---|---|
| grades 2-4 | `-1.21` | `0.2` | `0.56` | `-0.0025` |
| grades 5-7 | `-5.18` | `0.17` | `1.35` | `-0.00043` |
| grades 8-11 | `1.3` | `0.23` | `0.88` | `-0.0035` |

Formula:

$$
a+b\times\frac{\textrm{Number of words}}{\textrm{Number of sentences}}+c\times\frac{\textrm{Number of letters}}{\textrm{Number of words}}+d\times\textrm{FREQ2}
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_letters` | int | `-` | Number of letters of the words |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |
| `mean_ipm` | float | `-` | Mean frequency of content words (ipm) |
| `a` | float | `-14.46` | Coefficient a (intercept) |
| `b` | float | `0.58` | Coefficient b (of the mean sentence length) |
| `c` | float | `2.15` | Coefficient c (of the mean word length) |
| `d` | float | `-0.0026` | Coefficient d (of the mean frequency) |

## Matskovsky formula

!!! info ""
    **ruts.readability_stats.calc_matskovsky_index()**

Computation of the Matskovsky formula - the first readability formula for Russian (1976), derived by the method of successive intervals.

The higher the value, the harder the text is to read.

!!! note "Note"
    A complex word has more than three syllables, so [`ReadabilityStats`](readability_stats.md) passes the number of words with at least 4 syllables to the function.

Formula:

$$
a\times\frac{\textrm{Number of words}}{\textrm{Number of sentences}}+b\times100\times\frac{\textrm{Number of complex words}}{\textrm{Number of words}}+c
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_complex` | int | `-` | Number of complex words |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | float | `0.62` | Coefficient a (of the mean sentence length) |
| `b` | float | `0.123` | Coefficient b (of the share of complex words) |
| `c` | float | `0.051` | Coefficient c (intercept) |

## Dale-Chall index

!!! info ""
    **ruts.readability_stats.calc_dale_chall_index()**

Computation of the [Dale-Chall index](https://en.wikipedia.org/wiki/Dale–Chall_readability_formula).

The higher the value, the harder the text is to read. The result is the number of years of schooling in the US system needed to understand the text.

The original formula uses a list of 3000 familiar words; no such free list exists for Russian, so the adaptation of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project is applied, where the share of complex words replaces the share of unfamiliar words. The original formula coefficients are `0.1579` and `0.0496`.

!!! note "Note"
    A complex word has five or more syllables, so [`ReadabilityStats`](readability_stats.md) passes the number of words with at least 5 syllables (`ruts.constants.SMOG_COMPLEX_SYL_FACTOR`) to the function.

Formula:

$$
a\times100\times\frac{\textrm{Number of complex words}}{\textrm{Number of words}}+b\times\frac{\textrm{Number of words}}{\textrm{Number of sentences}}
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_complex` | int | `-` | Number of complex words |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | float | `0.552` | Coefficient a (of the share of complex words) |
| `b` | float | `0.273` | Coefficient b (of the mean sentence length) |

## Gunning fog index

!!! info ""
    **ruts.readability_stats.calc_gunning_fog_index()**

--8<-- "stats/readability_stats_funcs.md:calc_gunning_fog_index"

The adaptation of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project is used. SEO services additionally multiply the result by `0.78`; no justification for this multiplier has been published.

!!! note "Note"
    A complex word has five or more syllables, so [`ReadabilityStats`](readability_stats.md) passes the number of words with at least 5 syllables (`ruts.constants.SMOG_COMPLEX_SYL_FACTOR`) to the function.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_complex` | int | `-` | Number of complex words |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | float | `0.4` | Coefficient a |

## Flesch index to grade { #flesch_reading_easy_to_grade }

!!! info ""
    **ruts.readability_stats.flesch_reading_easy_to_grade()**

--8<-- "stats/readability_stats_funcs.md:flesch_reading_easy_to_grade"

The default bands are those of `text_standard` of the [textstat](https://github.com/textstat/textstat) library (`anyts.constants.READING_EASE_GRADES`):

| Flesch index | Grade |
|---|---|
|`90-100`| 5 |
|`80-90`| 6 |
|`70-80`| 7 |
|`60-70`| 8.5 (grades 8-9) |
|`50-60`| 10 |
|`40-50`| 11 |
|`30-40`| 12 |
|`below 30`| 13 |

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `flesch_reading_easy` | float | `-` | Flesch reading ease value |
| `grades` | list[tuple[float, float]] | `READING_EASE_GRADES` | Lower bounds and their grades in descending order of the bounds |
| `below` | float | `13` | Grade below the last bound |

## Consensus grade { #calc_consensus_grade }

!!! info ""
    **ruts.readability_stats.calc_consensus_grade()**

--8<-- "stats/readability_stats_funcs.md:calc_consensus_grade"

An analog of `text_standard` in textstat, which uses the mode instead of the median; the median is more robust to outliers of individual formulas. [`ReadabilityStats`](readability_stats.md#interpretation) passes the Flesch-Kincaid test, the Coleman-Liau, SMOG, ARI, Dale-Chall and Gunning indices, the Solovyev, Ivanov and Solnyshkina formula and the Flesch index to the function.

## Grade and reader age { #grade_to_age }

!!! info ""
    **ruts.readability_stats.grade_to_age()**

--8<-- "stats/readability_stats_funcs.md:grade_to_age"

The default stages of ruTS are taken from the `GRADE_TEXT` table of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project (`ruts.constants.GRADE_AGE_LEVELS` and `POSTGRADUATE_LEVEL`):

| Grade | Stage | Age |
| :---: | :---: | :-: |
| 1-3 | grades 1-3 | 6-8 years |
| 4-6 | grades 4-6 | 9-11 years |
| 7-9 | grades 7-9 | 12-14 years |
| 10-11 | grades 10-11 | 15-16 years |
| 12-14 | university years 1-3 | 17-19 years |
| 15-17 | university years 4-6 | 20-22 years |
| above 17 | postgraduate | over 22 years |

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `grade` | float | `-` | Grade formula value |
| `levels` | list[tuple[int, int, str, str]] | `GRADE_AGE_LEVELS` | Stages as the first and the last year, the stage and the age, in ascending order |
| `above` | tuple[str, str] | `POSTGRADUATE_LEVEL` | Stage and age above the last stage |

## Band of a scale { #scale_level }

!!! info ""
    **ruts.readability_stats.scale_level()**

--8<-- "stats/readability_stats_funcs.md:scale_level"

The scales of ruTS are `ruts.constants.READING_EASE_LEVELS` and `LIX_LEVELS`, the RIX grades of the core are `anyts.constants.RIX_GRADES`.

!!! example "Example"

    ``` python
    from ruts.constants import READING_EASE_LEVELS
    from ruts.readability_stats import calc_flesch_reading_easy, scale_level

    flesch = calc_flesch_reading_easy(n_syllables=60, n_words=30, n_sents=2)
    flesch, scale_level(flesch, READING_EASE_LEVELS)
    # (67.135, '8-й и 9-й класс')
    ```

## Reading time { #calc_reading_time }

!!! info ""
    **ruts.readability_stats.calc_reading_time()**

--8<-- "stats/readability_stats_funcs.md:calc_reading_time"

The silent reading norm for an adult is 120-180 words per minute (Kuznetsov and Khromov, 1991); the upper bound is used by default. The reading-aloud norms for primary school by the Russian federal standard are available in the `ruts.constants.READING_SPEED_NORMS` table:

| Norm | Words per minute |
|---|---|
| `adult_silent` | 120-180 |
| `grade_1` | 25-40 |
| `grade_2` | 60-80 |
| `grade_3` | 80-100 |
| `grade_4` | 90-110 |

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_words` | int | `-` | Number of words |
| `wpm` | float | `180` | Reading speed, words per minute |
