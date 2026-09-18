# Corpus comparison

!!! info ""
    **ruts.corpus.compare_corpora()**, **ruts.corpus.corpus_features()**, **ruts.corpus.text_features()**, **ruts.corpus.split_windows()**, **ruts.corpus.sentence_rhythm()**

## Description

Comparison of two corpora across all text features at once: which statistics distinguish authors, genres, translations, human and generated texts - and by how much. For individual words [`keyness`](keyness.md) does the same, for distances between texts - [`delta`](stylometry.md#delta).

The texts of both corpora are cut into windows of equal size (`split_windows`: the number of windows is the rounded ratio of the number of words to the window size, at least one, the parts are equal; a boundary goes before the opening marks of the first word of a window - dashes, quotation marks, brackets - so that punctuation is not lost) to remove the dependence of the features on text length. For every window the features are computed (`text_features` or your own function), for every feature the two sets of values are compared. The result is a `DataFrame` feature × statistics sorted by descending absolute Cliff's delta.

## Features

`text_features(text)` returns 130 features prefixed by source:

| Prefix | Features | Source |
| :----- | :------- | :----- |
| `basic_` | shares of unique, long, complex, simple, mono- and polysyllabic words, letters, spaces and punctuation marks; letters and syllables per word, words per sentence | [`BasicStats`](../stats/basic_stats.md) |
| `readability_` | all readability formulas, consensus grade, reading time | [`ReadabilityStats`](../stats/readability_stats.md) |
| `diversity_` | all lexical diversity measures | [`DiversityStats`](../stats/diversity_stats.md) |
| `morph_` | shares of parts of speech among the words (`morph_pos_NOUN`) and shares of values within each feature (`morph_case_Gen`, `morph_tense_Past`) | [`MorphStats`](../stats/morph_stats.md) by pymorphy3 |
| `sents_` | mean sentence length in words, standard deviation, coefficient of variation, autocorrelation of adjacent lengths (`sentence_rhythm`) - the rhythm of the text | [`sentence_lengths`](../visualizers/sentences.md) |
| `punct_` | frequencies of punctuation marks by type per 1000 words and the share of the letter ё | [`punctuation_profile`](../stats/basic_stats.md#punctuation) |

A 1000-word window takes about 0.1 s. Features over the spaCy parse (`SyntaxStats`, `CohesionStats`) are not in the default set - the function works on strings; they can be added with your own feature function via `features`, see the example below. `corpus_features(texts, window, features)` returns the feature matrix of the windows indexed by (text number, window number) - for your own classifiers.

## Statistics

For a feature with values $x_1 \dots x_{n_A}$ in corpus A and $y_1 \dots y_{n_B}$ in corpus B (undefined and infinite values dropped; with fewer than two values on a side - `nan`):

| Column | Description |
| :----- | :---------- |
| `mean_A`, `mean_B`, `median_A`, `median_B` | means and medians |
| `median_diff`, `ci_low`, `ci_high` | the difference of medians and its 95% percentile bootstrap interval: both sets are resampled `n_bootstrap` times (`bootstrap_median_diff`) |
| `cohen_d` | $d = (\bar{x} - \bar{y}) / s$, $s$ - pooled standard deviation; 0.2 - small effect, 0.5 - medium, 0.8 - large (`calc_cohen_d`) |
| `cliff_delta` | $\delta = P(x > y) - P(x < y)$ from −1 to 1; $\lvert\delta\rvert$ < 0.147 - negligible effect, < 0.33 - small, < 0.474 - medium, otherwise large (Romano et al. 2006; `calc_cliff_delta`) |
| `auc` | the feature as a single-feature classifier: the share of window pairs where the value in A is larger than in B, ties count as half; $\delta = 2 \cdot AUC - 1$, 0.5 - the feature does not distinguish the corpora |
| `u`, `p_value` | the Mann-Whitney U statistic and the two-sided p-value (`scipy.stats.mannwhitneyu`) |
| `p_holm` | the p-value with Holm's correction for the number of features (`holm_correction`): a table of a hundred rows without correction invites false discoveries |
| `n_A`, `n_B` | number of windows with a defined value |

Cliff's delta and AUC are computed from the same U statistic and are therefore consistent with each other; Cohen's d is sensitive to outliers and non-normality, so it is best read next to delta.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `a` | list[str] | `-` | Texts of the first corpus |
| `b` | list[str] | `-` | Texts of the second corpus |
| `window` | int | `1000` | Window size in words; `None` - whole texts |
| `features` | callable | `None` | Text feature function; `None` - `text_features` |
| `labels` | tuple[str, str] | `("A", "B")` | Corpus names for the columns |
| `n_bootstrap` | int | `1000` | Number of bootstrap samples |
| `seed` | int | `0` | Random number generator seed; `None` - random |

## Usage example

Chekhov versus Tolstoy over the prose of the [`RussianLiterature`](../datasets/russianliterature.md) dataset: 77 and 42 works, 292 and 1444 windows of 1000 words, about two minutes.

!!! example "Example"

    _Code_:

    ``` python
    from ruts.corpus import compare_corpora
    from ruts.datasets import RussianLiterature

    rl = RussianLiterature()
    chekhov = list(rl.get_texts(genre="prose", author="Чехов"))
    tolstoy = list(rl.get_texts(genre="prose", author="Толстой"))

    result = compare_corpora(chekhov, tolstoy, window=1000, labels=("Чехов", "Толстой"))
    columns = [
        "median_Чехов",
        "median_Толстой",
        "ci_low",
        "ci_high",
        "cohen_d",
        "cliff_delta",
        "auc",
        "p_holm",
    ]
    result[columns].head(10).round(3)
    ```

    _Result_:

    ``` bash
                                   median_Чехов  median_Толстой  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    punct_ellipsis                       15.842           2.000  10.940   18.013    1.861        0.719  0.860     0.0
    punct_exclamation                    14.881           3.996   9.145   12.378    1.704        0.670  0.835     0.0
    morph_verb_form_Fin                   0.761           0.695   0.056    0.076    1.161        0.594  0.797     0.0
    punct_yo_share                        0.007           0.000   0.007    0.008    1.065        0.557  0.778     0.0
    readability_gunning_fog_index         5.995           7.970  -2.283   -1.681   -0.961       -0.540  0.230     0.0
    readability_matskovsky_index          8.600          11.232  -3.148   -2.324   -0.947       -0.531  0.235     0.0
    basic_words_per_sent                 11.122          15.136  -4.595   -3.400   -0.943       -0.531  0.235     0.0
    sents_mean                           11.122          15.136  -4.636   -3.417   -0.943       -0.531  0.235     0.0
    readability_dale_chall_index          5.187           6.676  -1.776   -1.229   -0.930       -0.527  0.237     0.0
    readability_smog_index                5.711           7.294  -1.903   -1.322   -0.895       -0.516  0.242     0.0
    ```

Chekhov has several times more ellipses and exclamations per 1000 words, shorter sentences and a higher share of finite verb forms; Tolstoy is harder by every readability formula. Of the 130 features, 100 have a corrected p-value below 0.01, but only 14 show a large effect by Cliff's delta - with thousands of windows significance is cheap, the effect size matters more.

Your own features, for example syntactic ones by spaCy, are passed as a function:

!!! example "Example"

    ``` python
    import spacy
    from ruts import SyntaxStats
    from ruts.corpus import compare_corpora, text_features

    nlp = spacy.load("ru_core_news_sm")


    def features(text):
        stats = SyntaxStats(nlp(text)).get_stats()
        return {**text_features(text), **{f"syntax_{key}": value for key, value in stats.items()}}


    compare_corpora(chekhov, tolstoy, window=1000, features=features, labels=("Чехов", "Толстой"))
    ```
