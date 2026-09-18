# Phonostatistics

!!! info ""
    **ruts.phon_stats.PhonStats**

## Description

A module for computing phonostatistics of a text: shares of sound classes, consonant clusters and hiatuses, CV pattern entropy, "hardness", alliteration and assonance indices, and syllable statistics. The data source can be either a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

The statistics are computed over letters without accounting for devoicing, reduction and stress. Letter classes are set by the `ruts.constants` constants:

| Class | Letters | Constant |
| :---: | :-----: | :------: |
| Vowels | а, е, и, о, у, ы, э, ю, я, ё | `RU_VOWELS` |
| Sonorant consonants | л, м, н, р, й | `RU_CONSONANTS_SONOR`, `RU_CONSONANTS_YET` |
| Voiced obstruents | б, в, г, д, ж, з | `RU_CONSONANTS_HIGH` |
| Voiceless obstruents | к, п, с, т, ф, х, ц, ч, ш, щ | `RU_CONSONANTS_LOW` |
| Signs | ь, ъ - not sounds, not counted in the shares | `RU_MARKS` |

Words are divided into syllables by the rising sonority rule (Avanesov), see the [`syllabify`](phon_stats_funcs.md#syllabify) function.

Syllables, CV patterns, clusters and hiatuses are computed once per word form and cached, letter classes - by a counter over the whole text, the alliteration and assonance indices - over a word × letter matrix with numpy, so on a corpus of 340 thousand words the statistics take 0.6 s - less than razdel needs to split it into words.

!!! note "Note"
    The statistics are computed when the `PhonStats` object is initialized.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `words_extractor` | WordsExtractor | `None` | Word extraction tool |
| `window_len` | int | `3` | Window size in words for alliteration and assonance |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `words` | tuple[str] | Tuple of extracted lowercased words |
| `syllables` | tuple[tuple[str, ...], ...] | Tuple of the syllables of each word |
| `n_vowels` | int | Number of vowels |
| `n_consonants` | int | Number of consonants |
| `n_sonorants` | int | Number of sonorant consonants |
| `n_voiced` | int | Number of voiced obstruents |
| `n_voiceless` | int | Number of voiceless obstruents |
| `n_marks` | int | Number of soft and hard signs |
| `c_clusters` | dict[int, int] | Distribution of consonant clusters by length |
| `c_syllable_patterns` | dict[str, int] | Distribution of syllables by CV pattern |
| `p_vowels` | float | Share of vowels among sounds |
| `p_sonorants` | float | Share of sonorant consonants among sounds |
| `p_voiced` | float | Share of voiced obstruents among sounds |
| `p_voiceless` | float | Share of voiceless obstruents among sounds |
| `consonant_vowel_ratio` | float | Consonant-to-vowel ratio |
| `p_heavy_clusters` | float | Share of clusters of 3 or more consonants |
| `p_hiatus` | float | Vowel hiatuses per word |
| `cv_entropy` | float | Entropy of word CV patterns in bits |
| `hardness` | float | Hardness - the ratio of voiceless obstruents to vowels and sonorants |
| `alliteration` | float | Alliteration index |
| `assonance` | float | Assonance index |
| `p_open_syllables` | float | Share of open syllables |
| `mean_syllable_len` | float | Mean syllable length in letters |

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
    'alliteration': 0.9149440867502556,
    'assonance': 0.802520508857449,
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

### print_stats

Prints a table with the computed phonostatistics.

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed statistics
    ps.print_stats()
    ```

    _Result_:

    ``` bash
                   Статистика               | Значение
    --------------------------------------------------
    Доля гласных                            |   0.40
    Доля сонорных согласных                 |   0.11
    Доля звонких шумных согласных           |   0.19
    Доля глухих шумных согласных            |   0.29
    Отношение согласных к гласным           |   1.48
    Доля кластеров из 3 и более согласных   |   0.03
    Зияний гласных на слово                 |   0.00
    Энтропия CV-шаблонов слов (бит)         |   3.14
    Жёсткость                               |   0.56
    Индекс аллитерации                      |   0.91
    Индекс ассонанса                        |   0.80
    Доля открытых слогов                    |   0.76
    Средняя длина слога (букв)              |   2.60
    ```
