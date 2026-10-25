# Phonostatistics

``` {.python .signature}
PhonStats(source, words_extractor=None, window_len=3)
```

--8<-- "stats/phon_stats.md:PhonStats"

The class extends the `PhonStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/phon_stats/) core with the hooks of Russian: the sounds are the letters of a word in the classes of the table below, without devoicing, reduction and stress; the iotated е, ё, ю, я after a vowel make no hiatus, and a word is divided into syllables by the rising sonority rule (Avanesov) of the [`syllabify`](../syllables.md#syllabify) function. Stress marks are dropped from the words of a text and of a `Doc`, and the parts of a hyphenated word that spaCy splits are joined (`во-первых` is one word). The `print_stats` table and the error messages are in Russian (`PHON_STATS_DESC` and `CORE_MESSAGES` of `ruts.constants`). The computation time grows linearly with the length of the text.

| Class | Letters | Constant |
| :---- | :------ | :------- |
| Vowels | а, е, и, о, у, ы, э, ю, я, ё | `RU_VOWELS` |
| Sonorant consonants | л, м, н, р, й | `RU_CONSONANTS_SONOR`, `RU_CONSONANTS_YET` |
| Voiced obstruents | б, в, г, д, ж, з | `RU_CONSONANTS_HIGH` |
| Voiceless obstruents | к, п, с, т, ф, х, ц, ч, ш, щ | `RU_CONSONANTS_LOW` |
| Signs | ь, ъ - no sounds: not counted in the shares and do not break a consonant cluster | `RU_MARKS` |

=== "Code"

    ``` python
    from ruts import PhonStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    ps = PhonStats(text)
    ps.print_stats()
    ```

=== "Result"

    ```
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
    Средняя длина слога (звуков)          |   2.48
    ```

## Parameters

--8<-- "stats/phon_stats.md:PhonStats-parameters"

``` {.python .signature}
check_params(window_len)
```

Checks the window of the alliteration and the assonance apart from the class: one that is not an integer of at least 2 raises `ParameterError`.

## Attributes

--8<-- "stats/phon_stats.md:PhonStats-attributes"

The ruTS attribute `n_marks` (`int`) is the number of ь and ъ.

=== "Code"

    ``` python
    ps.syllables[:4]
    ps.c_clusters
    ps.c_syllable_patterns
    ps.n_marks
    ```

=== "Result"

    ```
    (('ног',), ('нет',), ('а',), ('хо', 'жу'))
    {1: 22, 2: 6, 3: 1}
    {'CCCV': 1, 'CCV': 5, 'CCVC': 1, 'CV': 11, 'CVC': 5, 'V': 2}
    3
    ```

## Metrics

--8<-- "stats/phon_stats.md:PhonStats-metrics"

<div class="metric-card" markdown>

### Shares of the classes of the sounds { #sound_shares }

`p_vowels` · `p_sonorants` · `p_voiced` · `p_voiceless`
{ .metric-meta }

--8<-- "stats/phon_stats.md:PhonStats-sound_shares"

</div>

<div class="metric-card" markdown>

### Ratio of the consonants to the vowels { #consonant_vowel_ratio }

`consonant_vowel_ratio`
{ .metric-meta }

--8<-- "stats/phon_stats.md:PhonStats-consonant_vowel_ratio"

</div>

<div class="metric-card" markdown>

### Consonant clusters { #consonant_clusters }

`p_heavy_clusters` · `c_clusters`
{ .metric-meta }

``` {.python .signature}
calc_consonant_clusters(text)
```

The distribution of the consonant clusters of the words by length. A cluster is a run of consonants inside a word, a single consonant between vowels or at the edge of a word included; ь and ъ do not break a cluster.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |

</div>

<div class="metric-card" markdown>

### Hiatuses { #hiatus }

`p_hiatus`
{ .metric-meta }

``` {.python .signature}
calc_hiatus(text)
```

The number of the vowel hiatuses, two or more vowels in a row inside a word: аэропорт, аист, поэзия (о-э). The iotated е, ё, ю, я after a vowel denote [j] and a vowel and make no hiatus: заяц, моя, красивая, читает.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |

</div>

<div class="metric-card" markdown>

### Entropy of the CV patterns { #cv_entropy }

`cv_entropy`
{ .metric-meta }

--8<-- "stats/phon_stats.md:PhonStats-cv_entropy"

``` {.python .signature}
calc_cv_entropy(text)
```

The entropy of the CV patterns of a list of words: the higher the value, the more varied the phonetic shape of the words. Words without vowels and consonants (numbers, Latin script) are left out, and without other words the value is `nan`.

``` {.python .signature}
cv_pattern(word)
```

The CV pattern of a word or a syllable: vowels are marked `V`, consonants `C`, and ь, ъ and the other characters are left out.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words (`calc_cv_entropy`) |
| `word` | `str` | - | Word or syllable (`cv_pattern`) |

</div>

<div class="metric-card" markdown>

### Hardness { #hardness }

`hardness`
{ .metric-meta }

--8<-- "stats/phon_stats.md:PhonStats-hardness"

</div>

<div class="metric-card" markdown>

### Alliteration and assonance { #repetition_index }

`alliteration` · `assonance`
{ .metric-meta }

``` {.python .signature}
calc_alliteration(text, window_len=3)
```

``` {.python .signature}
calc_assonance(text, window_len=3)
```

The alliteration and assonance indices of a list of words: the repetition index `calc_repetition_index` over the consonant and over the vowel letters of the words. Letters are compared, not sounds: devoicing, stress and reduction are not taken into account.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |
| `window_len` | `int` | `3` | Window in words (`PHON_WINDOW_LEN`) |

--8<-- "stats/phon_stats.md:calc_repetition_index"

--8<-- "stats/phon_stats.md:calc_repetition_index-parameters"

</div>

<div class="metric-card" markdown>

### Syllables { #syllables }

`p_open_syllables` · `mean_syllable_len`
{ .metric-meta }

--8<-- "stats/phon_stats.md:PhonStats-syllables"

In ruTS the length of a syllable is the number of its letters without ь and ъ.

``` {.python .signature}
is_open_syllable(syllable)
```

Checks whether a syllable is open, that is ends in a vowel; ь and ъ after a vowel do not close it.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `syllable` | `str` | - | Syllable |

</div>

The functions of ruTS take words as strings and count by the Russian classes of letters of the table above. The `calc_*` functions check their arguments: words that are not a list of strings raise `SourceTypeError`, and a window that is not an integer of at least 2 `ParameterError`.

=== "Code"

    ``` python
    from ruts.phon_stats import (
        calc_alliteration,
        calc_consonant_clusters,
        calc_cv_entropy,
        calc_hiatus,
        cv_pattern,
        is_open_syllable,
    )

    words = ["слышно", "бесшумно", "шуршат", "камыши", "у", "поэта"]
    cv_pattern("всплеск"), is_open_syllable("съе")
    calc_consonant_clusters(words)
    calc_hiatus(words), calc_cv_entropy(words)
    calc_alliteration(words, window_len=2)
    ```

=== "Result"

    ```
    ('CCCCVCC', True)
    {1: 8, 2: 5}
    (1, 2.584962500721156)
    1.4999999999999998
    ```

## Methods

The methods `get_stats`, `to_dataframe`, `print_stats` and `describe` are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the phonostatistics have no scales, so `describe` gives `None` for the statistics of `get_stats`.

=== "Code"

    ``` python
    ps.get_stats()
    ```

=== "Result"

    ```
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
     'mean_syllable_len': 2.48}
    ```
