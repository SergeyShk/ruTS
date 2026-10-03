# Statistic functions

## CV pattern { #cv_pattern }

!!! info ""
    **ruts.phon_stats.cv_pattern()**

Getting the CV pattern of a word or syllable: vowels are marked `V`, consonants `C`, ь and ъ are skipped, other characters are ignored.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word or syllable |

## Open syllable { #is_open_syllable }

!!! info ""
    **ruts.phon_stats.is_open_syllable()**

Checking whether a syllable is open - ends with a vowel; ь and ъ after a vowel do not close the syllable.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `syllable` | str | `-` | Syllable |

## Consonant clusters { #calc_consonant_clusters }

!!! info ""
    **ruts.phon_stats.calc_consonant_clusters()**

Computation of the distribution of consonant clusters by length. A cluster is a sequence of consonants inside a word; ь and ъ do not break a cluster; clusters of length 1 are single consonants between vowels or at word edges. `PhonStats` derives from the distribution the share of clusters of 3 or more consonants (`p_heavy_clusters`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |

## Vowel hiatuses { #calc_hiatus }

!!! info ""
    **ruts.phon_stats.calc_hiatus()**

Computation of the number of vowel hiatuses - two or more vowels in a row inside a word: аэропорт, аист, поэзия (о-э). The iotated е, ё, ю, я after a vowel denote [j] plus a vowel and do not form a hiatus: заяц, моя, красивая, читает - otherwise adjective and verb endings would account for four fifths of all hiatuses. `PhonStats` divides the number of hiatuses by the number of words (`p_hiatus`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |

## CV pattern entropy { #calc_cv_entropy }

!!! info ""
    **ruts.phon_stats.calc_cv_entropy()**

Computation of the Shannon entropy of the distribution of words by CV pattern in bits: the higher the value, the more diverse the phonetic shape of the text's words. Words without vowels and consonants (numbers, Latin script) are ignored; if there are no other words at all, the function returns `nan`.

Formula:

$$
H = -\sum_k p_k \log_2 p_k
$$

where $p_k$ is the share of words with pattern $k$.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |

## Hardness { #hardness }

The `hardness` attribute of `PhonStats` is the ratio of the number of voiceless obstruents to the number of vowels and sonorants. The higher the value, the "harder" the text sounds. Undefined for texts without vowels and sonorants.

Formula:

$$
\frac{\textrm{Voiceless obstruents}}{\textrm{Vowels}+\textrm{Sonorants}}
$$

## Alliteration index { #calc_alliteration }

!!! info ""
    **ruts.phon_stats.calc_alliteration()**

The index is `calc_repetition_index` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/phonetics/) core over the consonant letters of the words:

--8<-- "stats/phonetics.md:calc_repetition_index"

Letters are compared, not sounds: devoicing is not accounted for.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `window_len` | int | `3` | Window size in words |

## Assonance index { #calc_assonance }

!!! info ""
    **ruts.phon_stats.calc_assonance()**

Computation of the assonance index - the same quantity as the [alliteration index](#calc_alliteration), but for vowels. Computed over all vowel letters without accounting for stress and reduction.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `window_len` | int | `3` | Window size in words |
