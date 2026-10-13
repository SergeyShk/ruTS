# Readability metrics

!!! info ""
    **ruts.readability_stats.ReadabilityStats**

## Description

--8<-- "stats/readability_stats.md:ReadabilityStats"

!!! quote "Definition"

    Readability is a property of text material characterizing how easily a person perceives it while reading.

    Text readability should be distinguished from the point of view of:

    *   the typographic design of the text;
    *   the linguistic features of the text material (complexity of syntactic constructions, vocabulary hard to perceive, etc.).

The coefficients of the formulas adapted for Russian are set by a preset (see [below](#presets)): by default the coefficients of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project fitted on 68 grade-labeled texts are used; the coefficients of Oborneva obtained on fiction (the Flesch-Kincaid test with them is above the grade of the Russian school, see [below](#presets)) and of the Kazan group (Solovyev, Ivanov, Solnyshkina) obtained on textbooks are also available.

The main presumptions of readability metrics:

*   short sentences are easier to read than long ones;
*   long words make reading harder;
*   a reader slows down at low-frequency and/or unfamiliar words.

## Language hooks

The class extends the `ReadabilityStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/readability_stats/) core with the hooks of Russian: the [basic statistics](basic_stats.md) of ruTS, which take the Russian [`SentsExtractor`](../extractors/sentences.md) and [`WordsExtractor`](../extractors/words.md) by default, the coefficient presets of `ruts.constants.READABILITY_PRESETS`, the Russian formulas - Solovyev, Ivanov and Solnyshkina, Matskovsky and Dale-Chall in the plainrussian adaptation, the grade formulas of the consensus grade `ruts.constants.READABILITY_GRADE_STATS`, complex words of five or more syllables in SMOG, Gunning fog and Dale-Chall (`ruts.constants.SMOG_COMPLEX_SYL_FACTOR`), the grades and ages of the plainrussian table, the scales of the Flesch index, LIX and RIX with Russian labels (`ruts.constants.READABILITY_LEVEL_SCALES`), the conversion of the Flesch index into a grade by the bands of its scale (`ruts.constants.READING_EASE_GRADES`) and the reading speeds of Russian readers.

The `mu_index` attribute of the core (Legibilidad µ) stays outside `get_stats`: it was fitted on Spanish texts.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc/BasicStats | `-` | Data source (a string, a Doc object or ready basic statistics) |
| `sents_extractor` | SentsExtractor | `None` | Sentence extraction tool |
| `words_extractor` | WordsExtractor | `None` | Word extraction tool |
| `preset` | str | `plainrussian` | Coefficient preset (`plainrussian`, `fiction`, `academic`) |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `flesch_kincaid_grade` | float | Flesch-Kincaid test |
| `flesch_reading_easy` | float | Flesch reading ease |
| `coleman_liau_index` | float | Coleman-Liau index |
| `smog_index` | float | SMOG index |
| `automated_readability_index` | float | Automated readability index |
| `lix` | float | LIX readability index |
| `rix` | float | RIX readability index |
| `sis_grade` | float | Solovyev, Ivanov and Solnyshkina formula (2023) |
| `matskovsky_index` | float | Matskovsky formula |
| `dale_chall_index` | float | Dale-Chall index in the plainrussian adaptation |
| `gunning_fog_index` | float | Gunning fog index in the plainrussian adaptation |
| `consensus_grade` | float | Consensus grade over all grade formulas and the Flesch index |
| `reading_time` | float | Reading time in minutes at 180 words per minute |
| `mu_index` | float | Legibilidad µ of the core, outside `get_stats` |
| `bs` | BasicStats | Basic text statistics |
| `preset` | str | Name of the coefficient preset |
| `coefficients` | dict[str, tuple[float, float, float]] | Formula coefficients of the preset, a copy that can be changed for one object |

## Coefficient presets { #presets }

A preset sets the coefficients of the Flesch-Kincaid test and the Flesch index. The coefficients of the Coleman-Liau, SMOG and ARI indices in all presets come from the plainrussian project, since no other adaptations for Russian have been published. The other formulas do not depend on the preset.

| Preset | Source | Corpus | Flesch-Kincaid test | Flesch index |
| :----: | :----: | :----: | :-----------------: | :----------: |
| `plainrussian` | [Plain Russian Language](https://github.com/infoculture/plainrussian) (Begtin) | 68 grade-labeled texts | `0.318·ASL + 14.2·ASW − 30.5` | `206.835 − 1.3·ASL − 60.1·ASW` (Oborneva, variant A, since plainrussian does not derive the Flesch index) |
| `fiction` | Oborneva (2005/2006) | about 6 million words of fiction | `0.5·ASL + 8.4·ASW − 15.59` | `206.835 − 1.3·ASL − 60.1·ASW` (variant A) |
| `academic` | Solovyev, Ivanov, Solnyshkina (2018); Solnyshkina and Kiselnikov (2015) | 14 social studies textbooks for grades 5-11 | `0.36·ASL + 5.76·ASW − 11.97` (FKG_SIS) | `206.836 − 1.52·ASL − 65.14·ASW` (Oborneva, variant B) |

Here ASL is the mean number of words per sentence, ASW the mean number of syllables per word. The table of all coefficients is available as `ruts.constants.READABILITY_PRESETS`.

!!! example "Example"

    ``` python
    from ruts import ReadabilityStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    ReadabilityStats(text).flesch_kincaid_grade
    # -2.0633333333333326
    ReadabilityStats(text, preset="fiction").flesch_kincaid_grade
    # 5.91
    ReadabilityStats(text, preset="academic").flesch_kincaid_grade
    # 3.0299999999999994
    ```

The presets agree with the grade label alike but give different scales, and they do not order texts quite alike. On the [`TextsByGrade`](../datasets/textsbygrade.md) dataset the Spearman correlation of the Flesch-Kincaid test with the grade label for all three presets is 0.79, while the medians of the test by label group differ:

| Label | Texts | `plainrussian` | `fiction` | `academic` |
| :---: | :---: | :------------: | :-------: | :--------: |
| 1 | 11 | 2.9 | 7.5 | 4.0 |
| 3-4 | 10 | 4.2 | 8.7 | 4.9 |
| 5-9 | 12 | 4.4 | 8.7 | 4.9 |
| 10-11 | 18 | 6.7 | 11.7 | 7.0 |
| 12-17 | 17 | 23.7 | 24.4 | 15.9 |
| 1 ([`SovChLit`](../datasets/sovchlit.md)) | 179 | 1.5 | 6.1 | 3.1 |

On school texts (labels 1-11) the test with the `fiction` preset is about four grades above the label (median deviation +3.9 against −0.9 for `plainrussian` and −0.2 for `academic`), and about five on the first-grade reader `SovChLit`. Its value should therefore not be read as a grade of the Russian school: for the grade of the reader use `plainrussian` (the default; its coefficients were fitted on `TextsByGrade`) or `academic`, and `fiction` to compare with works that use Oborneva's coefficients. The consensus grade depends on the preset less, since the Flesch-Kincaid test is only one of its formulas (the median on `TextsByGrade` is 7.75 for `fiction` against 6.75 for `plainrussian`).

!!! note "Note"
    Every metric can be computed separately by calling the corresponding function. Detailed information on the readability metrics and the functions used to compute them is available in the corresponding [section](readability_stats_funcs.md).

## Interpretation { #interpretation }

--8<-- "stats/readability_stats.md:ReadabilityStats-consensus"

The grade formulas of ruTS are the Flesch-Kincaid test, the Coleman-Liau, SMOG, ARI, Dale-Chall and Gunning indices and the Solovyev, Ivanov and Solnyshkina formula, and the Flesch index is [converted to a grade](readability_stats_funcs.md#flesch_reading_easy_to_grade) by the bands of its reading scale, so an index of 45 reads as university both in `describe` and in the consensus grade. The [`describe_grade`](#describe_grade) method translates the consensus grade or an individual formula into a school grade and reader age by the plainrussian project table:

| Grade | Stage | Age |
| :---: | :---: | :-: |
| 1-3 | grades 1-3 | 6-8 years |
| 4-6 | grades 4-6 | 9-11 years |
| 7-9 | grades 7-9 | 12-14 years |
| 10-11 | grades 10-11 | 15-16 years |
| 12-14 | university years 1-3 | 17-19 years |
| 15-17 | university years 4-6 | 20-22 years |
| above 17 | postgraduate | over 22 years |

The [`describe_level`](#describe_level) method reads the Flesch index, LIX and RIX by their scales - the tables of the [metric functions](readability_stats_funcs.md) page, and [`describe`](#describe) reads any metric: a grade formula and the consensus grade by the table above, the Flesch index, LIX and RIX by their scales; for a metric without a scale it gives `None`.

The `reading_time` attribute estimates silent reading time at 180 words per minute (the upper bound of the adult norm by Kuznetsov and Khromov, 1991). A different speed is accepted by the [`reading_time_by_speed`](#reading_time_by_speed) method, and the [`reading_time_by_norm`](#reading_time_by_norm) method computes the time within the norm bounds from the `ruts.constants.READING_SPEED_NORMS` table, including the school reading-aloud norms of the Russian federal standard.

## Methods

### describe_grade

--8<-- "stats/readability_stats.md:ReadabilityStats-describe_grade"

!!! example "Example"

    ``` python
    from ruts import ReadabilityStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    rs = ReadabilityStats(text)
    rs.describe_grade()
    # '1-3-й класс (6-8 лет)'
    rs.describe_grade("gunning_fog_index")
    # '4-6-й класс (9-11 лет)'
    ```

### describe_level

--8<-- "stats/readability_stats.md:ReadabilityStats-describe_level"

### describe

--8<-- "stats/readability_stats.md:ReadabilityStats-describe"

!!! example "Example"

    ``` python
    from ruts import ReadabilityStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    rs = ReadabilityStats(text)
    rs.describe("flesch_reading_easy"), rs.describe_level("lix")
    # ('6-й класс', 'очень простые тексты, детские книги')
    rs.describe("rix"), rs.describe("matskovsky_index")
    # ('6-й класс', None)
    ```

### reading_time_by_speed

--8<-- "stats/readability_stats.md:ReadabilityStats-reading_time_by_speed"

### reading_time_by_norm

--8<-- "stats/readability_stats.md:ReadabilityStats-reading_time_by_norm"

The norms of the `ruts.constants.READING_SPEED_NORMS` table are `adult_silent`, `grade_1`, `grade_2`, `grade_3` and `grade_4`, each with a lower and an upper bound, and the method returns the reading times at the upper and at the lower bound.

!!! example "Example"

    ``` python
    from ruts import ReadabilityStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    rs = ReadabilityStats(text)
    rs.reading_time_by_speed(120)
    # 0.125
    rs.reading_time_by_norm("grade_1")
    # (0.375, 0.6)
    ```

### sis_grade_by_stage

Returns the value of the Solovyev, Ivanov and Solnyshkina formula (2023) with the coefficients for the given education stage. The general formula is available through the `sis_grade` attribute, the stage coefficients - in the `ruts.constants.SIS_GRADE_STAGES` table.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `stage` | str | `-` | Education stage (`2-4`, `5-7`, `8-11`) |

### sis_grade_by_freq { #sis_grade_by_freq }

Returns the value of the Solovyev, Ivanov and Solnyshkina formula (2023) with word frequency: `−14.46 + 0.58·ASL + 2.15·AWL − 0.0026·FREQ2`, where FREQ2 is the mean frequency of the content words of the text by the Lyashevskaya and Sharoff dictionary, the [`mean_ipm_content`](lexical_stats.md) attribute of `LexicalStats`. The stage coefficients are in the `ruts.constants.SIS_GRADE_FREQ_STAGES` table.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `mean_ipm` | float | `-` | Mean frequency of content words (ipm) |
| `stage` | str | `None` | Education stage (`2-4`, `5-7`, `8-11`); without it - the general formula |

!!! example "Example"

    ``` python
    from ruts import LexicalStats, ReadabilityStats

    text = "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул."
    rs = ReadabilityStats(text)
    rs.sis_grade, rs.sis_grade_by_freq(LexicalStats(text).mean_ipm_content)
    # (-4.625384615384615, -3.106298290598293)
    ```

### get_stats

--8<-- "stats/readability_stats.md:ReadabilityStats-get_stats"

An example of computing text readability metrics:

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts import ReadabilityStats

    # Prepare the data
    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"

    # Compute the metrics
    rs = ReadabilityStats(text)
    rs.get_stats()
    ```

    _Result_:

    ``` bash
    {'flesch_kincaid_grade': -2.0633333333333326,
    'flesch_reading_easy': 87.16833333333334,
    'coleman_liau_index': 1.1700000000000053,
    'smog_index': 0.05,
    'automated_readability_index': 0.2941666666666656,
    'lix': 28.333333333333336,
    'rix': 2.0,
    'sis_grade': 1.5166666666666675,
    'matskovsky_index': 9.351,
    'dale_chall_index': 4.095000000000001,
    'gunning_fog_index': 6.0,
    'consensus_grade': 1.5,
    'reading_time': 0.08333333333333333}
    ```

### print_stats

--8<-- "stats/readability_stats.md:ReadabilityStats-print_stats"

To illustrate the method, we reuse the code from the previous example:

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed metrics
    rs.print_stats()
    ```

    _Result_:

    ``` bash
                       Метрика                   | Значение
    -------------------------------------------------------
    Тест Флеша-Кинкайда                          |  -2.06
    Индекс удобочитаемости Флеша                 |  87.17
    Индекс Колман-Лиау                           |   1.17
    Индекс SMOG                                  |   0.05
    Автоматический индекс удобочитаемости        |   0.29
    Индекс удобочитаемости LIX                   |  28.33
    Индекс удобочитаемости RIX                   |   2.00
    Формула Соловьёва, Иванова, Солнышкиной      |   1.52
    Формула Мацковского                          |   9.35
    Индекс Дейла-Чейла                           |   4.10
    Индекс Ганнинга                              |   6.00
    Сводный класс                                |   1.50
    Время чтения (мин.)                          |   0.08
    ```
