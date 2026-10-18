# Phonostatistics

!!! info ""
    **ruts.phon_stats.PhonStats**

## Description

--8<-- "stats/phon_stats.md:PhonStats"

The computation time grows linearly with text length.

!!! note "Note"
    The statistics are computed when the `PhonStats` object is initialized.

## Language hooks

The class extends the `PhonStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/phon_stats/) core with the hooks of Russian: the sounds are the letters of a word in the classes of the table below, without devoicing, reduction and stress; the iotated е, ё, ю, я after a vowel make no hiatus, and a word is divided into syllables by the rising sonority rule (Avanesov) of the [`syllabify`](../syllables.md#syllabify) function. Stress marks are dropped from the words of a text and of a `Doc`, and the parts of a hyphenated word that spaCy splits are joined (`во-первых` is one word). The `print_stats` table has Russian headers and the Russian descriptions of `ruts.constants.PHON_STATS_DESC`, and the messages of the errors are in Russian, `ruts.constants.CORE_MESSAGES`.

| Class | Letters | Constant |
| :---: | :-----: | :------: |
| Vowels | а, е, и, о, у, ы, э, ю, я, ё | `RU_VOWELS` |
| Sonorant consonants | л, м, н, р, й | `RU_CONSONANTS_SONOR`, `RU_CONSONANTS_YET` |
| Voiced obstruents | б, в, г, д, ж, з | `RU_CONSONANTS_HIGH` |
| Voiceless obstruents | к, п, с, т, ф, х, ц, ч, ш, щ | `RU_CONSONANTS_LOW` |
| Signs | ь, ъ - not sounds: not counted in the shares and do not break a consonant cluster | `RU_MARKS` |

## Parameters

--8<-- "stats/phon_stats.md:PhonStats-parameters"

The window is checked on its own by `ruts.phon_stats.check_params(window_len)`.

## Attributes

--8<-- "stats/phon_stats.md:PhonStats-attributes"

In ruTS `mean_syllable_len` counts the letters of a syllable, ь and ъ included, and the `n_marks` attribute (int) is the number of ь and ъ.

!!! note "Note"
    Every statistic can be computed separately by calling the corresponding function. Detailed information on the phonostatistics and the functions used to compute them is available in the corresponding [section](phon_stats_funcs.md).

## Methods

### get_stats

Returns a dictionary with the computed phonostatistics.

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts import PhonStats

    # Prepare the data
    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"

    # Compute the statistics
    ps = PhonStats(text)
    ps.get_stats()
    ```

    _Result_:

    ``` bash
    {'p_vowels': 0.4032258064516129,
    'p_sonorants': 0.11290322580645161,
    'p_voiced': 0.1935483870967742,
    'p_voiceless': 0.2903225806451613,
    'consonant_vowel_ratio': 1.48,
    'p_heavy_clusters': 0.034482758620689655,
    'p_hiatus': 0.0,
    'cv_entropy': 3.1395722619867223,
    'hardness': 0.5625,
    'alliteration': 1.0916179337231968,
    'assonance': 0.8305084745762712,
    'p_open_syllables': 0.76,
    'mean_syllable_len': 2.6}
    ```

Syllables and distributions are available as attributes:

!!! example "Example"

    ``` python
    ps.syllables[:4]
    # (('ног',), ('нет',), ('а',), ('хо', 'жу'))
    ps.c_clusters
    # {1: 22, 2: 6, 3: 1}
    ps.c_syllable_patterns
    # {'CCCV': 1, 'CCV': 5, 'CCVC': 1, 'CV': 11, 'CVC': 5, 'V': 2}
    ```

`to_dataframe` returns the same statistics as a one-row `pandas.DataFrame`, and `describe` returns `None` for each of them: the phonostatistics have no interpretation scales.

### print_stats

--8<-- "stats/stats.md:Stats-print_stats"

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed statistics
    ps.print_stats()
    ```

    _Result_:

    ``` bash
                  Статистика              | Значение
    -------------------------------------------------
    Доля гласных                          |   0.40
    Доля сонорных согласных               |   0.11
    Доля звонких шумных согласных         |   0.19
    Доля глухих шумных согласных          |   0.29
    Отношение согласных к гласным         |   1.48
    Доля кластеров из 3 и более согласных |   0.03
    Зияний гласных на слово               |   0.00
    Энтропия CV-шаблонов слов (бит)       |   3.14
    Жёсткость                             |   0.56
    Индекс аллитерации                    |   1.09
    Индекс ассонанса                      |   0.83
    Доля открытых слогов                  |   0.76
    Средняя длина слога (букв)            |   2.60
    ```
