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

Computation of the alliteration index - the ratio of the observed number of windows of `window_len` adjacent words in which the same consonant occurs in at least two words to the number expected if the words stood in random order (summed over all consonants). The expectation is computed from the consonant frequencies in the text itself, so the index shows whether repeats are clustered in adjacent words, not the overall frequency of a sound. A value around 1 - consonant repeats are random, noticeably above 1 - alliteration. Computed over letters without accounting for devoicing.

A window of shuffled words is a sample of them without replacement, so for a letter found in $K$ of the $N$ words of the text, a window of $w$ words holds it in at least two words with the hypergeometric probability

$$
P = 1 - \frac{\binom{N-K}{w} + K \binom{N-K}{w-1}}{\binom{N}{w}}
$$

and the expected number of windows is the sum of these probabilities over the letters times the $N - w + 1$ windows; the index equals $\sum O / \sum E$.

!!! warning "Warning"
    For texts shorter than the window and texts where no consonant occurs in two words the function returns `nan`.

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
