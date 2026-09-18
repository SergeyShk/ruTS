# Metric functions

## Flesch-Kincaid test

!!! info ""
    **ruts.readability_stats.calc_flesch_kincaid_grade()**

Computation of the [Flesch-Kincaid test](https://en.wikipedia.org/wiki/Flesch–Kincaid_readability_tests#Flesch–Kincaid_grade_level).

The higher the value, the harder the text is to read. The result is the number of years of schooling in the US system needed to understand the text.

The default coefficients come from the current version of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project. Alternative coefficients for Russian are available through [presets](readability_stats.md#presets): Oborneva (`0.5`, `8.4`, `15.59`) and FKG_SIS of Solovyev, Ivanov and Solnyshkina (`0.36`, `5.76`, `11.97`).

Formula:

$$
a\times\frac{\textrm{Number of words}}{\textrm{Number of sentences}}+b\times\frac{\textrm{Number of syllables}}{\textrm{Number of words}}–C
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_syllables` | int | `-` | Number of syllables |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | int | `0.318` | Coefficient a |
| `b` | int | `14.2` | Coefficient b |
| `c` | int | `30.5` | Coefficient c |

## Flesch reading ease

!!! info ""
    **ruts.readability_stats.calc_flesch_reading_easy()**

Computation of the [Flesch reading ease](https://en.wikipedia.org/wiki/Flesch–Kincaid_readability_tests#Flesch_reading_ease).

The higher the value, the easier the text is to read. The index ranges from 0 to 100 and can be interpreted as follows:

| Value | Difficulty level |
|----------|----------|
|`100.0-90.0`|	5th grade|
|`90.0-80.0`|	6th grade|
|`80.0-70.0`|	7th grade|
|`70.0-60.0`|	8th and 9th grade|
|`60.0-50.0`|	10th and 11th grade|
|`50.0-30.0`|	College|
|`30.0-0.0`|	College graduate|

The default coefficients are Oborneva's (2005/2006, variant A). Variant B of the same works (`1.52`, `65.14`, `206.836`), used by the Kazan group, is available through the `academic` preset.

Formula:

$$
c–a\times\frac{\textrm{Number of words}}{\textrm{Number of sentences}}-b\times\frac{\textrm{Number of syllables}}{\textrm{Number of words}}
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_syllables` | int | `-` | Number of syllables |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | int | `1.3` | Coefficient a |
| `b` | int | `60.1` | Coefficient b |
| `c` | int | `206.835` | Coefficient c |

## Coleman-Liau index

!!! info ""
    **ruts.readability_stats.calc_coleman_liau_index()**

Computation of the [Coleman-Liau index](https://en.wikipedia.org/wiki/Coleman–Liau_index).

The higher the value, the harder the text is to read. The result is the number of years of schooling in the US system needed to understand the text.

Formula:

$$
a\times\frac{\textrm{Number of letters}}{\textrm{Number of words}}+b\times\frac{\textrm{Number of words}}{\textrm{Number of sentences}}–c
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_letters` | int | `-` | Number of letters |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | int | `6.26` | Coefficient a |
| `b` | int | `0.2805` | Coefficient b |
| `c` | int | `31.04` | Coefficient c |

## SMOG index

!!! info ""
    **ruts.readability_stats.calc_smog_index()**

Computation of the [SMOG index](https://en.wikipedia.org/wiki/SMOG) (Simple Measure of Gobbledygook). The most authoritative readability metric.

The higher the value, the harder the text is to read. The result is the number of years of schooling in the US system needed to understand the text.

!!! note "Note"
    The formula coefficients were derived for a complex word threshold of 5 syllables, so [`ReadabilityStats`](readability_stats.md) passes the number of words with at least 5 syllables to the function rather than the `n_complex_words` attribute of `BasicStats`.

Formula:

$$
a\times\sqrt{b\times\frac{\textrm{Number of complex words}}{\textrm{Number of sentences}}}+c
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_complex` | int | `-` | Number of complex words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | int | `1.1` | Coefficient a |
| `b` | int | `64.6` | Coefficient b |
| `c` | int | `0.05` | Coefficient c |

## Automated readability index

!!! info ""
    **ruts.readability_stats.calc_automated_readability_index()**

Computation of the [automated readability index](https://en.wikipedia.org/wiki/Automated_readability_index).

The higher the value, the harder the text is to read. The result is the age needed to understand the text. The index can be interpreted as follows:

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

Formula:

$$
a\times\frac{\textrm{Number of letters}}{\textrm{Number of words}}+b\times\frac{\textrm{Number of words}}{\textrm{Number of sentences}}–c
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_letters` | int | `-` | Number of letters |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | int | `6.26` | Coefficient a |
| `b` | int | `0.2805` | Coefficient b |
| `c` | int | `31.04` | Coefficient c |

## LIX readability index

!!! info ""
    **ruts.readability_stats.calc_lix()**

Computation of the [LIX readability index](https://en.wikipedia.org/wiki/Lix_(readability_test)).

The higher the value, the harder the text is to read. The index ranges from 0 to 100 and can be interpreted as follows:

| Value | Difficulty level |
|---|---|
|`4.9 and below`| up to grade 4 |
|`5.0-5.9`|	grades 5-6|
|`6.0-6.9`|	grades 7-8|
|`7.0-7.9`|	grades 9-10|
|`8.0-8.9`|	grades 11-12|
|`9.0-9.9`|	College|

!!! note "Note"
    In the canonical formula a long word is longer than 6 letters, so [`ReadabilityStats`](readability_stats.md) passes the number of words with at least 7 letters to the function rather than the `n_long_words` attribute of `BasicStats`.

Formula:

$$
\frac{\textrm{Number of words}}{\textrm{Number of sentences}}+100\times\frac{\textrm{Number of long words}}{\textrm{Number of words}}
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_long_words` | int | `-` | Number of long words |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |

## RIX readability index

!!! info ""
    **ruts.readability_stats.calc_rix()**

Computation of the [RIX readability index](https://en.wikipedia.org/wiki/Lix_(readability_test)).

A simplified, language-independent companion of the LIX index (Anderson, 1983). The higher the value, the harder the text is to read. The index can be interpreted as follows:

| Value | Difficulty level |
|---|---|
|`< 0.2`| grade 1 |
|`0.2-0.5`| grade 2 |
|`0.5-0.8`| grade 3 |
|`0.8-1.3`| grade 4 |
|`1.3-1.8`| grade 5 |
|`1.8-2.4`| grade 6 |
|`2.4-3.0`| grade 7 |
|`3.0-3.7`| grade 8 |
|`3.7-4.5`| grade 9 |
|`4.5-5.3`| grade 10 |
|`5.3-6.2`| grade 11 |
|`6.2-7.2`| grade 12 |
|`> 7.2`| College |

!!! note "Note"
    As for LIX, a long word is longer than 6 letters, so [`ReadabilityStats`](readability_stats.md) passes the number of words with at least 7 letters to the function.

Formula:

$$
\frac{\textrm{Number of long words}}{\textrm{Number of sentences}}
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_long_words` | int | `-` | Number of long words |
| `n_sents` | int | `-` | Number of sentences |

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
| `n_letters` | int | `-` | Number of letters |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | int | `-17.5` | Coefficient a (intercept) |
| `b` | int | `0.56` | Coefficient b (of the mean sentence length) |
| `c` | int | `2.45` | Coefficient c (of the mean word length) |

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
| `n_letters` | int | `-` | Number of letters |
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
| `a` | int | `0.62` | Coefficient a (of the mean sentence length) |
| `b` | int | `0.123` | Coefficient b (of the share of complex words) |
| `c` | int | `0.051` | Coefficient c (intercept) |

## Dale-Chall index

!!! info ""
    **ruts.readability_stats.calc_dale_chall_index()**

Computation of the [Dale-Chall index](https://en.wikipedia.org/wiki/Dale–Chall_readability_formula).

The higher the value, the harder the text is to read. The result is the number of years of schooling in the US system needed to understand the text.

The original formula uses a list of 3000 familiar words; no such free list exists for Russian, so the adaptation of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project is applied, where the share of complex words replaces the share of unfamiliar words. The original formula coefficients are `0.1579` and `0.0496`.

!!! note "Note"
    A complex word has more than four syllables, so [`ReadabilityStats`](readability_stats.md) passes the number of words with at least 5 syllables to the function.

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
| `a` | int | `0.552` | Coefficient a (of the share of complex words) |
| `b` | int | `0.273` | Coefficient b (of the mean sentence length) |

## Gunning fog index

!!! info ""
    **ruts.readability_stats.calc_gunning_fog_index()**

Computation of the [Gunning fog index](https://en.wikipedia.org/wiki/Gunning_fog_index) (Gunning, 1952).

The higher the value, the harder the text is to read. The result is the number of years of schooling in the US system needed to understand the text. The adaptation of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project is used. SEO services additionally multiply the result by `0.78`; no justification for this multiplier has been published.

!!! note "Note"
    A complex word has more than four syllables, so [`ReadabilityStats`](readability_stats.md) passes the number of words with at least 5 syllables to the function.

Formula:

$$
a\times\left(\frac{\textrm{Number of words}}{\textrm{Number of sentences}}+100\times\frac{\textrm{Number of complex words}}{\textrm{Number of words}}\right)
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_complex` | int | `-` | Number of complex words |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | int | `0.4` | Coefficient a |

## Flesch index to grade { #flesch_reading_easy_to_grade }

!!! info ""
    **ruts.readability_stats.flesch_reading_easy_to_grade()**

Conversion of the Flesch reading ease into a school grade for inclusion in the [consensus grade](#calc_consensus_grade), by analogy with `text_standard` of the [textstat](https://github.com/textstat/textstat) library:

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

Values above 100 map to grade 5.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `flesch_reading_easy` | float | `-` | Flesch reading ease value |

## Consensus grade { #calc_consensus_grade }

!!! info ""
    **ruts.readability_stats.calc_consensus_grade()**

Computation of the consensus grade - the median of the rounded grade formula values. An analog of `text_standard` in textstat, which uses the mode instead of the median; the median is more robust to outliers of individual formulas. Formula values are rounded arithmetically (half up). The Flesch index is [converted to a grade](#flesch_reading_easy_to_grade) and added without rounding, so for the 60-70 range it votes for 8.5.

[`ReadabilityStats`](readability_stats.md#interpretation) passes the Flesch-Kincaid test, the Coleman-Liau, SMOG, ARI, Dale-Chall and Gunning indices, the Solovyev, Ivanov and Solnyshkina formula and the Flesch index to the function.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `grades` | list[float] | `-` | Grade formula values |
| `flesch_reading_easy` | float | `None` | Flesch reading ease value |

## Grade and reader age { #grade_to_age }

!!! info ""
    **ruts.readability_stats.grade_to_age()**

Getting the school grade and reader age from a grade formula value. The mapping is taken from the `GRADE_TEXT` table of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project and is available in the `ruts.constants.GRADE_AGE_LEVELS` table:

| Grade | Stage | Age |
| :---: | :---: | :-: |
| 1-3 | grades 1-3 | 6-8 years |
| 4-6 | grades 4-6 | 9-11 years |
| 7-9 | grades 7-9 | 12-14 years |
| 10-11 | grades 10-11 | 15-16 years |
| 12-14 | university years 1-3 | 17-19 years |
| 15-17 | university years 4-6 | 20-22 years |
| above 17 | postgraduate | over 22 years |

The value is rounded arithmetically, values below 1 map to grades 1-3.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `grade` | float | `-` | Grade formula value |

## Reading time { #calc_reading_time }

!!! info ""
    **ruts.readability_stats.calc_reading_time()**

Computation of the reading time of a text in minutes. The silent reading norm for an adult is 120-180 words per minute (Kuznetsov and Khromov, 1991); the upper bound is used by default. The reading-aloud norms for primary school by the Russian federal standard are available in the `ruts.constants.READING_SPEED_NORMS` table:

| Norm | Words per minute |
|---|---|
| `adult_silent` | 120-180 |
| `grade_1` | 25-40 |
| `grade_2` | 60-80 |
| `grade_3` | 80-100 |
| `grade_4` | 90-110 |

Formula:

$$
\frac{\textrm{Number of words}}{\textrm{Reading speed}}
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_words` | int | `-` | Number of words |
| `wpm` | int | `180` | Reading speed, words per minute |
