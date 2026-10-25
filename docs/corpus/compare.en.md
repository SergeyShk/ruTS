# Corpus comparison

``` {.python .signature}
compare_corpora(a, b, window=1000, features=None, labels=('A', 'B'), n_bootstrap=1000, seed=0, min_words=None)
```

Compares two corpora of Russian texts by every feature of a text at once: which statistics tell authors, genres, translations, human and generated texts apart - and by how much. For single words [`keyness`](keyness.md) does the same, for the distances between texts - [`delta`](stylometry.md#delta).

The texts are cut in a row into windows of exactly `window` words by [`split_windows`](#split_windows), so the windows of all texts have one length; an incomplete remainder at the end of a text and a text shorter than a window are dropped unless `min_words` allows shorter windows. The features of every window are computed by [`text_features`](#text_features) or a function of one's own, and the tables of the two corpora are compared by [`compare_features`](#compare_features) of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/compare/) core.

Chekhov versus Tolstoy over the prose of the [`RussianLiterature`](../datasets/russianliterature.md) dataset: 77 and 42 works, 249 and 1423 windows of 1000 words, under a minute.

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
    punct_ellipsis                       14.000           2.000   5.975   23.025    1.869        0.707  0.853     0.0
    punct_exclamation                    14.000           4.000   7.000   14.000    1.670        0.658  0.829     0.0
    morph_verb_form_Fin                   0.766           0.700   0.036    0.099    1.132        0.574  0.787     0.0
    punct_yo_share                        0.007           0.000   0.002    0.010    1.026        0.533  0.766     0.0
    morph_verb_form_Part                  0.043           0.077  -0.051   -0.018   -0.795       -0.492  0.254     0.0
    punct_other                           0.000           2.000  -4.000    0.000   -0.351       -0.489  0.256     0.0
    readability_dale_chall_index          5.280           6.566  -2.205   -0.757   -0.866       -0.488  0.256     0.0
    readability_gunning_fog_index         6.088           7.730  -2.592   -0.817   -0.864       -0.481  0.260     0.0
    readability_smog_index                5.876           7.174  -2.385   -0.877   -0.840       -0.480  0.260     0.0
    morph_verb_form_Conv                  0.055           0.082  -0.040   -0.017   -0.800       -0.464  0.268     0.0
    {'n_Чехов': 249, 'n_Толстой': 1423, 'n_texts_Чехов': 57, 'n_texts_Толстой': 41}
    ```

Chekhov has several times more ellipses and exclamations per 1000 words, shorter sentences, a higher share of finite verb forms and a lower one of participles and converbs; Tolstoy is harder by every readability formula. Twenty works of Chekhov and one of Tolstoy are shorter than 1000 words and give no window, so the windows come from 57 and 41 works; with a smaller window they would be compared too.

The p-values take the 1672 windows for independent (see the [warning](#statistics) below): 90 of the 116 features have a corrected p-value below 0.01, but only 9 show a large effect by Cliff's delta. The interval of the difference of the medians resamples whole works and is the safer guide: it excludes zero for 67 of those 90 features, and for the length of a sentence it spans −5.4 to −1.2 words, where the windows alone would give −4.0 to −2.7. For the ellipses it spans 6 to 23 per 1000 words: the works of Chekhov differ in them a lot, on average from a fraction of one to 84 per 1000 words.

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `a` | `list[str]` | - | Texts of the first corpus |
| `b` | `list[str]` | - | Texts of the second corpus |
| `window` | `int` | `1000` | Window size in words; `None` - whole texts |
| `features` | `Callable` | `None` | Text feature function; `None` - `text_features` |
| `min_words` | `int` | `None` | Smallest number of words in a window, at most `window`; `None` - a whole window, one word with `window=None` |

`labels`, `n_bootstrap` and `seed` go on to [`compare_features`](#compare_features). `compare_corpora` checks them with `check_comparison_params` first, so a wrong name of a corpus or seed fails before any text is processed.

Raises:

- `SourceTypeError` - texts that are not a list of strings, `features` that cannot be called;
- `SourceError` - a corpus without a window of `min_words` words or more;
- `ParameterError` - a `window` or `min_words` that is not an integer of at least one, `min_words` above `window`, labels, a number of samples or a seed that `check_comparison_params` rejects.

## Features { #text_features }

``` {.python .signature}
text_features(text)
```

Returns 116 features of a text prefixed by source; an undefined feature is `nan`.

| Prefix | Features | Source |
| :----- | :------- | :----- |
| `basic_` | shares of long, complex, simple, mono- and polysyllabic words, letters, spaces and punctuation marks; letters and syllables per word | [`BasicStats`](../stats/basic_stats.md) |
| `readability_` | all readability formulas and the consensus grade | [`ReadabilityStats`](../stats/readability_stats.md) |
| `diversity_` | lexical diversity measures | [`DiversityStats`](../stats/diversity_stats.md) |
| `morph_` | shares of parts of speech and of single-valued features among the words (`morph_pos_NOUN`, `morph_polarity_Neg`, `morph_style_variant_Short`) and shares of values within the other features (`morph_case_Gen`, `morph_tense_Past`, `morph_degree_Cmp`; one share for a two-valued feature, `morph_number_Plur`) | [`MorphStats`](../stats/morph_stats.md) by pymorphy3 |
| `sents_` | mean sentence length in words, standard deviation, coefficient of variation, autocorrelation of adjacent lengths ([`sentence_rhythm`](#sentence_rhythm)) - the rhythm of the text | [`sentence_lengths`](../visualizers/sentences.md) |
| `punct_` | frequencies of punctuation marks by type per 1000 words and the share of the letter ё | [`punctuation_profile`](../stats/basic_stats.md#punctuation) |

A 1000-word window takes about 0.02 s. Features over the spaCy parse (`SyntaxStats`, `CohesionStats`) are not in the default set - the function works on strings; they can be added with your own feature function via `features`, see the example below.

The shares of spaces, letters and punctuation marks (`basic_p_spaces`, `basic_p_letters`, `basic_p_punctuations`) count characters as they are: line indents, double and non-breaking spaces in the files reflect the typesetting of the edition, not the text. In a corpus from different sources collapse them beforehand, for example `re.sub(r"[^\S\n]+", " ", text)`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Text string |

Raises:

- `SourceTypeError` - a text that is not a string;
- `SourceError` - a text without words.

``` {.python .signature}
corpus_features(texts, window=1000, features=text_features, min_words=None)
```

Returns the feature matrix of the windows indexed by (text number, window number), for your own classifiers as well; the level `text` of the index is what the bootstrap of `compare_features` resamples. Texts without words and windows shorter than `min_words` are skipped. `compare_corpora` is `corpus_features` for each corpus followed by `compare_features`; the split is needed when the features are computed once for several corpora and pairs have to be compared, for example all authors pairwise.

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

Your own features, for example syntactic ones by spaCy, are passed as a function; with the parse the same comparison takes about eight minutes:

=== "Code"

    ``` python
    import spacy
    from ruts import SyntaxStats
    from ruts.corpus import compare_corpora, text_features

    nlp = spacy.load("ru_core_news_sm")


    def features(text):
        stats = SyntaxStats(nlp(text)).get_stats()
        return {**text_features(text), **{f"syntax_{key}": value for key, value in stats.items()}}


    result = compare_corpora(
        chekhov, tolstoy, window=1000, features=features, labels=("Чехов", "Толстой")
    )
    result.filter(like="syntax_", axis=0)[columns].head(5).round(3)
    ```

=== "Result"

    ```
                                        median_Чехов  median_Толстой  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    syntax_converb_clauses_per_sent            0.106           0.212  -0.142   -0.073   -0.970       -0.574  0.213     0.0
    syntax_participle_clauses_per_sent         0.054           0.135  -0.108   -0.052   -0.864       -0.566  0.217     0.0
    syntax_verb_phrases_per_t_unit             1.804           2.112  -0.495   -0.221   -0.835       -0.513  0.244     0.0
    syntax_mean_clause_len                     5.155           5.893  -1.162   -0.461   -0.833       -0.503  0.248     0.0
    syntax_modifiers_per_noun                  0.479           0.593  -0.181   -0.057   -0.968       -0.500  0.250     0.0
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

Cuts a text into consecutive windows of exactly `window` words, so the features that depend on length are comparable between texts. The rest is a window only with at least `min_words` words (by default a whole window, so it is dropped). A boundary goes before the first word of a window and its opening marks; a symmetric mark, such as a straight quote or the dash of an aside, closes the previous window when glued to its last word or after a closing mark. Windows are stripped of whitespace; `window=None` gives the whole text. The words are those of [`WordsExtractor`](../extractors/words.md), and the marks those of `ruts.constants`: quotes, brackets and dashes open a phrase (`OPENING_MARKS`), the straight and the English quotes and the dashes are symmetric (`SYMMETRIC_MARKS`), and the final marks, the comma, the semicolon, the closing brackets and guillemet close one (`CLOSING_MARKS`).

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
