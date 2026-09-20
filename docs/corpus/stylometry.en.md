# Stylometry

!!! info ""
    **ruts.corpus.delta()**, **ruts.corpus.delta_profiles()**, **ruts.corpus.frequency_table()**, **ruts.corpus.z_scores()**, **ruts.corpus.zeta()**, **ruts.corpus.kilgarriff_chi2()**, **ruts.corpus.mendenhall_curve()**, **ruts.corpus.mendenhall_distance()**, **ruts.corpus.function_words_profile()**

## Description

Measures of stylometry and authorship attribution: distances between texts by the frequencies of the most frequent words (Burrows's Delta and its variants, as in [stylo](https://github.com/computationalstylistics/stylo)), markers of preferred and avoided words (Zeta), Kilgarriff's chi-square distance between corpora, the Mendenhall curve and the function word profile as author features. The functions work on lists of text units: lowercased word forms (the usual choice for Delta), lemmas or character N-grams ([`CharNgramsExtractor`](../extractors/char_ngrams.md)) - case and lemmatization are up to the extractor.

## Burrows's Delta { #delta }

A corpus is a dictionary "text name → units". `frequency_table` builds a table of relative frequencies: rows are texts, columns are the `n_mfw` most frequent units in descending order of mean relative frequency (ties broken alphabetically); `culling` keeps units occurring in at least the given share of texts, as in stylo. `z_scores` standardizes the columns with the sample standard deviation, like `scale()` in R; a column with identical frequencies in all texts gives zeros. `delta` computes a symmetric distance matrix from the z-scores (a `DataFrame` with text names) suitable for clustering and PCA; at least three texts are needed - with two, the z-scores degenerate to ±1 and all distances are equal.

Variants (`DELTA_VARIANTS`), formulas after the stylo sources, $n$ - number of units, $z_A$, $z_B$ - z-score vectors of the texts:

| Variant | Key | Formula | Source |
| :------ | :-- | :------ | :----- |
| Burrows's Delta | `burrows` | $\frac{1}{n} \sum_i \lvert z_{A,i} - z_{B,i} \rvert$ | Burrows (2002), `dist.delta` |
| Quadratic Delta | `quadratic` | $\frac{1}{n} \sqrt{\sum_i (z_{A,i} - z_{B,i})^2}$ | Argamon (2008), `dist.argamon` |
| Eder's Delta | `eder` | $\sum_i \frac{n - i + 2}{n} \lvert z_{A,i} - z_{B,i} \rvert$, $i$ - frequency rank of the unit | Eder, `dist.eder` |
| Cosine Delta | `cosine` | $1 - \frac{z_A \cdot z_B}{\lVert z_A \rVert \lVert z_B \rVert}$ | Smith and Aldridge (2011), [Evert et al. (2015)](https://aclanthology.org/W15-0709.pdf), `dist.wurzburg` |

Cosine Delta gives the best clustering quality by author in the experiments of Evert et al.; Burrows's Delta is the classic choice. The number of units is usually 100 to 500 most frequent words; for character N-grams - 100-200.

Parameters of `delta`:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `corpus` | dict[str, list[str]] | `-` | Units of the texts by text name |
| `n_mfw` | int | `100` | Number of the most frequent units; `None` - all |
| `variant` | str | `burrows` | Delta variant from `DELTA_VARIANTS` |
| `culling` | float | `0.0` | Minimum share of texts a unit must occur in |

`frequency_table(corpus, n_mfw=100, culling=0.0)` and `z_scores(table)` take the same parameters and the table.

For authorship attribution there is `delta_profiles(reference, samples, n_mfw, variant, culling, statistics)`: the most frequent units, culling and the statistics for the z-scores are taken from the reference texts `reference` (author profiles) or from a separate set `statistics` - for example, from the training windows when the profiles are concatenated from them and the profiles themselves are too few to estimate the spread of frequencies; the texts under test `samples` are described in the same units and normalized with the same statistics; the result is the distances from the tested texts to the reference ones, the nearest reference in a row is the presumed author. Unlike `delta` over a joint vocabulary, the tested texts affect neither the unit list nor the normalization, and the result for a text does not depend on which other texts are passed along with it.

!!! example "Example"

    ``` python
    from ruts import WordsExtractor
    from ruts.corpus import delta, delta_profiles, frequency_table

    texts = {
        "А": "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне.",
        "Б": "Собака лежала на полу и дремала. Потом собака ела и снова дремала на полу.",
        "В": "Завтра кот снова будет сидеть на окне и смотреть на птиц, а собака будет дремать.",
    }
    we = WordsExtractor(lowercase=True)
    corpus = {name: we.extract(text) for name, text in texts.items()}

    frequency_table(corpus, n_mfw=5).round(3)
    #       на      и  собака    кот   окне
    # А  0.200  0.133   0.000  0.133  0.133
    # Б  0.143  0.143   0.143  0.000  0.000
    # В  0.133  0.067   0.067  0.067  0.067

    delta(corpus, n_mfw=5).round(3)
    #        А      Б      В
    # А  0.000  1.563  1.277
    # Б  1.563  0.000  1.033
    # В  1.277  1.033  0.000

    delta(corpus, n_mfw=5, variant="cosine").round(3)
    #        А      Б      В
    # А  0.000  1.782  1.452
    # Б  1.782  0.000  1.202
    # В  1.452  1.202  0.000

    sample = {"?": we.extract("Кот проснулся на окне и снова смотрел на птиц.")}
    delta_profiles(corpus, sample, n_mfw=5).round(3)
    #        А     Б     В
    # ?  0.364  1.66  1.16
    ```

## Zeta { #zeta }

Markers of preferred and avoided words after Burrows (2007) and Craig and Kinney (2009). Every text of both corpora is divided into segments of about `segment_size` words (the number of segments is the rounded ratio of the length to the size, at least one); for a word the share of segments of each corpus in which it occurs ($DP$) is computed. Zeta is the difference of shares $DP_{target} - DP_{comparison}$ from −1 to 1 (`zeta.craig` in stylo notation; the classic Craig's Zeta $DP_{target} + (1 - DP_{comparison})$ is larger by one), logarithmic Zeta is $\log_2 \frac{DP_{target}}{DP_{comparison}}$ ([Schöch et al. 2018](https://zeta-project.eu/en/keyness-measures/burrows-zeta-logarithmic-zeta/)), a zero share is replaced with half a segment. The list starts with the words preferred by the target corpus and ends with the avoided ones.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `target` | list[str]/list[list[str]] | `-` | Words of the target corpus - one text or a list of texts |
| `comparison` | list[str]/list[list[str]] | `-` | Words of the comparison corpus |
| `segment_size` | int | `2000` | Segment size in words |
| `top_n` | int | `None` | Number of words from the start of the list; `None` - all |

The result is a list of `ZetaScore(word, dp_target, dp_comparison, zeta, log_zeta)` named tuples in descending Zeta order, ties broken by descending logarithmic Zeta and alphabetically.

!!! example "Example"

    ``` python
    from ruts.corpus import zeta

    zeta(corpus["А"], corpus["Б"], segment_size=5, top_n=2)
    # [ZetaScore(word='кот', dp_target=0.6666666666666666, dp_comparison=0.0, zeta=0.6666666666666666, log_zeta=2.0),
    #  ZetaScore(word='окне', dp_target=0.6666666666666666, dp_comparison=0.0, zeta=0.6666666666666666, log_zeta=2.0)]

    zeta(corpus["А"], corpus["Б"], segment_size=5)[-1]
    # ZetaScore(word='собака', dp_target=0.0, dp_comparison=0.6666666666666666, zeta=-0.6666666666666666, log_zeta=-2.0)
    ```

## Kilgarriff's chi-square { #kilgarriff_chi2 }

The distance between two corpora after [Kilgarriff (2001)](https://www.sketchengine.eu/wp-content/uploads/comparing_corpora_2001.pdf): for the `n_mfw` most frequent words of the joint corpus the expected frequencies in the corpora are proportional to their sizes, $\chi^2 = \sum (O - E)^2 / E$ over the words and both corpora. The larger the value, the more the corpora differ; the value grows with corpus size, so pairs of corpora are comparable with each other at equal sizes, as in Kilgarriff's experiments.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `words_a` | list[str] | `-` | Words of the first corpus |
| `words_b` | list[str] | `-` | Words of the second corpus |
| `n_mfw` | int | `500` | Number of the most frequent words of the joint corpus |

!!! example "Example"

    ``` python
    from ruts.corpus import kilgarriff_chi2

    round(kilgarriff_chi2(corpus["А"], corpus["Б"], n_mfw=5), 3)
    # 6.018
    ```

## Mendenhall curve { #mendenhall }

`mendenhall_curve(words)` - the shares of words of each length in characters (Mendenhall 1887), an author profile comparable between texts regardless of their size; `mendenhall_distance(words_a, words_b)` - the Jensen-Shannon distance with base 2 between the curves, from 0 (identical distributions) to 1.

!!! example "Example"

    ``` python
    from ruts.corpus import mendenhall_curve, mendenhall_distance

    {length: round(share, 3) for length, share in mendenhall_curve(corpus["А"]).items()}
    # {1: 0.133, 2: 0.2, 3: 0.133, 4: 0.2, 5: 0.2, 7: 0.133}

    round(mendenhall_distance(corpus["А"], corpus["Б"]), 3)
    # 0.353
    ```

## Function word profile { #function_words_profile }

The shares of adpositions, coordinating and subordinating conjunctions, particles, pronouns, determiners and interjections (`FUNCTION_UD_POS`: `ADP`, `CCONJ`, `SCONJ`, `PART`, `PRON`, `DET`, `INTJ`) among the words of the text - by the first pymorphy3 analysis for a list of words and by the annotation for a `Doc` with parts of speech. Function words do not depend on the topic, so their profile is a classic authorship feature (the Marusenko school).

!!! example "Example"

    ``` python
    from ruts.corpus import function_words_profile

    {pos: round(share, 3) for pos, share in function_words_profile(corpus["А"]).items()}
    # {'ADP': 0.2, 'CCONJ': 0.133, 'SCONJ': 0.0, 'PART': 0.0, 'PRON': 0.0, 'DET': 0.0, 'INTJ': 0.0}
    ```
