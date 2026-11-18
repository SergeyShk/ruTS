# Corpus comparison

``` {.python .signature}
compare_corpora(a, b, window=1000, features=None, labels=('A', 'B'), n_bootstrap=1000, seed=0, min_words=None)
```

Compares two corpora of Russian texts by every feature of a text at once: which statistics tell authors, genres, translations, human and generated texts apart - and by how much. For single words [`keyness`](keyness.md) does the same, for the distances between texts - [`delta`](stylometry.md#delta).

The texts are cut into windows of `window` words by [`split_windows`](#split_windows), the features of every window come from [`text_features`](#text_features) or a function of one's own, and [`compare_features`](#compare_features) of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/compare/) core compares the tables of the two corpora.

Chekhov versus Tolstoy over the prose of the [`RussianLiterature`](../datasets/russianliterature.md) dataset: 75 and 42 works, 220 and 1339 windows of 1000 words, about a minute.

=== "Code"

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
    result.loc["sents_mean", ["n_Чехов", "n_Толстой", "n_texts_Чехов", "n_texts_Толстой"]].to_dict()
    ```

=== "Result"

    ```
                                            median_Чехов  median_Толстой  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    cohesion_content_overlap_2_sent                0.067           0.111  -0.049   -0.036   -1.467       -0.835  0.082     0.0
    cohesion_content_overlap_prop_all              0.015           0.027  -0.014   -0.009   -1.196       -0.791  0.104     0.0
    cohesion_noun_overlap_2_sent                   0.082           0.143  -0.071   -0.047   -1.315       -0.755  0.123     0.0
    cohesion_content_overlap_adjacent              0.201           0.346  -0.170   -0.113   -1.220       -0.717  0.141     0.0
    cohesion_content_overlap_all                   0.096           0.181  -0.114   -0.060   -1.108       -0.710  0.145     0.0
    punct_ellipsis                                12.000           2.000   4.000   21.000    2.040        0.704  0.852     0.0
    cohesion_content_overlap_prop_adjacent         0.039           0.061  -0.026   -0.017   -1.029       -0.654  0.173     0.0
    cohesion_noun_overlap_all                      0.048           0.097  -0.069   -0.032   -0.904       -0.648  0.176     0.0
    cohesion_noun_overlap_adjacent                 0.114           0.218  -0.129   -0.079   -1.001       -0.647  0.176     0.0
    cohesion_p_given                               0.312           0.368  -0.065   -0.034   -1.167       -0.638  0.181     0.0
    {'n_Чехов': 220, 'n_Толстой': 1339, 'n_texts_Чехов': 55, 'n_texts_Толстой': 41}
    ```

Cohesion sets the corpora apart most: Tolstoy repeats nouns and content words in adjacent and following sentences more often, and Chekhov has several times more ellipses and exclamations per 1000 words. The overlaps in adjacent and in all pairs of sentences partly repeat the sentence length (the Spearman ρ of `cohesion_content_overlap_all` with `sents_mean` over the windows is 0.86 for Chekhov and 0.76 for Tolstoy), while the share of the lemmas repeated in the next two sentences (`cohesion_content_overlap_2_sent`) repeats it only weakly (0.19 and 0.31). Twenty works of Chekhov and one of Tolstoy are shorter than a window, so the windows come from 55 and 41 works.

The p-values take the 1559 windows for independent (see the [warning](#statistics) below): 107 of the 145 features have a corrected p-value below 0.01, but only 20 show a large effect by Cliff's delta. The interval of the difference of the medians resamples whole works and is the safer guide: it excludes zero for 79 of those 107 features, and for the length of a sentence it spans −4.6 to −1.1 words, where the windows alone would give −3.7 to −2.4.

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `a` | `list[str]` | - | Texts of the first corpus |
| `b` | `list[str]` | - | Texts of the second corpus |
| `window` | `int` | `1000` | Window size in words; `None` - whole texts |
| `features` | `Callable` | `None` | Text feature function; `None` - `text_features` |
| `min_words` | `int` | `None` | Smallest number of words in a window, at most `window`; `None` - a whole window, one word with `window=None` |

`labels`, `n_bootstrap` and `seed` go on to [`compare_features`](#compare_features) and are checked before any text is processed.

Raises:

- `SourceTypeError` - texts that are not a list of strings, `features` that cannot be called;
- `SourceError` - a corpus without a window of `min_words` words or more;
- `ParameterError` - a `window` or `min_words` that is not an integer of at least one, `min_words` above `window`, labels, a number of samples or a seed that `check_comparison_params` rejects.

## Features { #text_features }

``` {.python .signature}
text_features(text, nlp=None)
```

Returns 145 features of a text prefixed by source, 190 with the pipeline `nlp`; an undefined feature is `nan`.

| Prefix | Features | Source |
| :----- | :------- | :----- |
| `basic_` | shares of long, complex, simple, mono- and polysyllabic words, letters, spaces and punctuation marks; letters and syllables per word | [`BasicStats`](../stats/basic_stats.md) |
| `readability_` | all readability formulas and the consensus grade | [`ReadabilityStats`](../stats/readability_stats.md) |
| `diversity_` | lexical diversity measures, but for Orlov's Z, MA-MTLD and MTLD-W, unstable on a window | [`DiversityStats`](../stats/diversity_stats.md) |
| `morph_` | shares of parts of speech and of single-valued features among the words (`morph_pos_NOUN`, `morph_polarity_Neg`) and shares of values within the other features (`morph_case_Gen`; one share for a two-valued feature, `morph_number_Plur`) | [`MorphStats`](../stats/morph_stats.md) by ruMorph |
| `sents_` | mean sentence length in words, standard deviation, coefficient of variation, autocorrelation of adjacent lengths ([`sentence_rhythm`](#sentence_rhythm)) | [`sentence_lengths`](../visualizers/sentences.md) |
| `punct_` | frequencies of punctuation marks by type per 1000 words and the share of the letter ё | [`punctuation_profile`](../stats/basic_stats.md#punctuation) |
| `cohesion_` | the overlap of the sentences, pronouns, givenness, temporal cohesion and connectors, without the overlaps between paragraphs (`*_para`) | [`CohesionStats`](../stats/cohesion_stats.md) by ruMorph |
| `syntax_` | all syntactic statistics of the parse, only with the pipeline `nlp`; the leaves, the subtrees, the longest dependency and the depth of the tree nearly repeat `sents_mean` | [`SyntaxStats`](../stats/syntax_stats.md) |

A 1000-word window takes about 0.04 s. The shares of spaces, letters and punctuation marks (`basic_p_spaces`, `basic_p_letters`, `basic_p_punctuations`) count the characters as they are, with the indents and double spaces of the edition; in a corpus from different sources collapse them beforehand, for example `re.sub(r"[^\S\n]+", " ", text)`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Text string |
| `nlp` | `Language` | `None` | spaCy pipeline with a parser and parts of speech for the `syntax_` features; `None` - without them |

Raises:

- `SourceTypeError` - a text that is not a string, an `nlp` that is not a spaCy `Language` object;
- `SourceError` - a text without words, a text longer than the `max_length` of the pipeline, a pipeline without a parser or parts of speech.

``` {.python .signature}
corpus_features(texts, window=1000, features=text_features, min_words=None)
```

Returns the feature matrix of the windows indexed by (text number, window number), for your own classifiers as well; texts without words and windows shorter than `min_words` are skipped. `compare_corpora` is `corpus_features` for each corpus followed by `compare_features`; apart they compute the features once to compare several pairs of corpora, for example all authors pairwise.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `texts` | `list[str]` | - | Texts of the corpus |
| `window` | `int` | `1000` | Window size in words; `None` - whole texts |
| `features` | `Callable` | `text_features` | Text feature function |
| `min_words` | `int` | `None` | Smallest number of words in a window, at most `window`; `None` - a whole window, one word with `window=None` |

Raises:

- `SourceTypeError` - texts that are not a list of strings, `features` that cannot be called;
- `SourceError` - a corpus without a window of `min_words` words or more;
- `ParameterError` - a `window` or `min_words` that is not an integer of at least one, `min_words` above `window`.

Features of your own go to `features` as a function of a text, `text_features` with a pipeline among them; with the parse the same comparison takes about five minutes:

=== "Code"

    ``` python
    from functools import partial

    from ruts import load_pipeline
    from ruts.corpus import compare_corpora, text_features

    nlp = load_pipeline()
    result = compare_corpora(
        chekhov,
        tolstoy,
        window=1000,
        features=partial(text_features, nlp=nlp),
        labels=("Чехов", "Толстой"),
    )
    result.filter(like="syntax_", axis=0)[columns].head(5).round(3)
    ```

=== "Result"

    ```
                                        median_Чехов  median_Толстой  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    syntax_converb_clauses_per_sent            0.111           0.217  -0.128   -0.092   -1.063       -0.633  0.184     0.0
    syntax_participle_clauses_per_sent         0.049           0.119  -0.093   -0.052   -0.815       -0.546  0.227     0.0
    syntax_nominal_chains_per_sent             0.087           0.164  -0.104   -0.053   -0.770       -0.531  0.235     0.0
    syntax_tree_depth                          3.096           3.657  -0.771   -0.348   -0.913       -0.524  0.238     0.0
    syntax_verb_phrases_per_t_unit             1.632           1.880  -0.349   -0.167   -0.818       -0.507  0.246     0.0
    ```

## Comparison of feature tables { #compare_features }

--8<-- "corpus/compare.md:compare_features"

--8<-- "corpus/compare.md:compare_features-parameters"

--8<-- "corpus/compare.md:check_comparison_params"

## Statistics { #statistics }

--8<-- "corpus/compare.md:compare_features-statistics"

## Functions of the statistics

The statistics of a row are available one by one from `ruts.corpus`:

--8<-- "corpus/compare.md:calc_cohen_d"

--8<-- "corpus/compare.md:calc_cliff_delta"

--8<-- "corpus/compare.md:bootstrap_median_diff"

--8<-- "corpus/compare.md:holm_correction"

=== "Code"

    ``` python
    from ruts.corpus import calc_cliff_delta, calc_cohen_d, holm_correction

    round(calc_cohen_d([2, 4, 6, 8], [1, 3, 5, 7]), 3)
    calc_cliff_delta([2, 4, 6, 8], [1, 3, 5, 7])
    holm_correction([0.01, 0.04, 0.03]).round(3).tolist()
    ```

=== "Result"

    ```
    0.387
    0.25
    [0.03, 0.06, 0.06]
    ```

## Windows of a text { #split_windows }

``` {.python .signature}
split_windows(text, window=1000, min_words=None)
```

Cuts a text into consecutive windows of exactly `window` words, the words of [`WordsExtractor`](../extractors/words.md), so the features that depend on length are comparable between texts. The rest is a window only with at least `min_words` words (by default a whole window, so it is dropped). A boundary goes before the first word of a window and the quotes, brackets and dashes that open it, so the punctuation stays with its phrase.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Text string |
| `window` | `int` | `1000` | Size of a window in words; `None` - the whole text |
| `min_words` | `int` | `None` | Smallest number of words in a window; `None` - a whole window, or one word without a window |

A text without words or shorter than `min_words` gives an empty list.

Raises:

- `SourceTypeError` - a text that is not a string;
- `ParameterError` - a `window` or `min_words` that is not an integer of at least one, `min_words` above the window.

=== "Code"

    ``` python
    from ruts.corpus import split_windows

    split_windows("Раз два три четыре пять", 2, min_words=1)
    split_windows("Он сказал: «Иди домой». Потом он вышел из комнаты", 4)
    ```

=== "Result"

    ```
    ['Раз два', 'три четыре', 'пять']
    ['Он сказал: «Иди домой».', 'Потом он вышел из']
    ```

## Rhythm of the sentences { #sentence_rhythm }

``` {.python .signature}
sentence_rhythm(lengths)
```

Gives the rhythm of the sentences from their lengths in words: the mean `sents_mean`, the standard deviation `sents_std`, the coefficient of variation `sents_cv` and the lag-1 autocorrelation of neighbouring lengths `sents_autocorr` (Yule, 1939). The deviation needs two sentences, the autocorrelation three of unequal lengths, the coefficient of variation a mean above zero; otherwise, and without sentences, a feature is `nan`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `lengths` | `list[int]` | - | Lengths of the sentences in words |

Raises:

- `SourceTypeError` - lengths that are not a list of integers;
- `ParameterError` - a negative length.

=== "Code"

    ``` python
    from ruts.corpus import sentence_rhythm

    {key: round(value, 3) for key, value in sentence_rhythm([4, 8, 2, 7]).items()}
    ```

=== "Result"

    ```
    {'sents_mean': 5.25, 'sents_std': 2.754, 'sents_cv': 0.525, 'sents_autocorr': -0.794}
    ```
