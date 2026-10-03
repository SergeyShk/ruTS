# Corpus comparison

!!! info ""
    **ruts.corpus.compare_corpora()**, **ruts.corpus.compare_features()**, **ruts.corpus.check_comparison_params()**, **ruts.corpus.corpus_features()**, **ruts.corpus.text_features()**, **ruts.corpus.split_windows()**, **ruts.corpus.sentence_rhythm()**, **ruts.corpus.calc_cohen_d()**, **ruts.corpus.calc_cliff_delta()**, **ruts.corpus.bootstrap_median_diff()**, **ruts.corpus.holm_correction()**

## Description

`compare_corpora` compares two corpora of Russian texts by every feature of a text at once: which statistics tell authors, genres, translations, human and generated texts apart - and by how much. For single words [`keyness`](keyness.md) does the same, for the distances between texts - [`delta`](stylometry.md#delta). It builds the tables of the features of the windows of both corpora and compares them with the `compare_features` of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/compare/) core:

--8<-- "corpus/compare.md:compare_features"

The texts are cut into windows of equal size by `split_windows`; windows of fewer than `min_words` words are dropped. The features of every window are computed by `text_features` or a function of one's own.

## Features

`text_features(text)` returns 108 features prefixed by source:

| Prefix | Features | Source |
| :----- | :------- | :----- |
| `basic_` | shares of long, complex, simple, mono- and polysyllabic words, letters, spaces and punctuation marks; letters and syllables per word | [`BasicStats`](../stats/basic_stats.md) |
| `readability_` | all readability formulas and the consensus grade | [`ReadabilityStats`](../stats/readability_stats.md) |
| `diversity_` | lexical diversity measures | [`DiversityStats`](../stats/diversity_stats.md) |
| `morph_` | shares of parts of speech among the words (`morph_pos_NOUN`) and shares of values within each feature (`morph_case_Gen`, `morph_tense_Past`; one share for a two-valued feature, `morph_number_Plur`) | [`MorphStats`](../stats/morph_stats.md) by pymorphy3 |
| `sents_` | mean sentence length in words, standard deviation, coefficient of variation, autocorrelation of adjacent lengths (`sentence_rhythm`) - the rhythm of the text | [`sentence_lengths`](../visualizers/sentences.md) |
| `punct_` | frequencies of punctuation marks by type per 1000 words and the share of the letter ё | [`punctuation_profile`](../stats/basic_stats.md#punctuation) |

A 1000-word window takes about 0.02 s. Features over the spaCy parse (`SyntaxStats`, `CohesionStats`) are not in the default set - the function works on strings; they can be added with your own feature function via `features`, see the example below.

`corpus_features(texts, window, features)` returns the feature matrix of the windows indexed by (text number, window number), for your own classifiers as well; the level `text` of the index is what the bootstrap of `compare_features` resamples. `compare_corpora` is `corpus_features` for each corpus followed by `compare_features`; the split is needed when the features are computed once for several corpora and pairs have to be compared, for example all authors pairwise.

The shares of spaces, letters and punctuation marks (`basic_p_spaces`, `basic_p_letters`, `basic_p_punctuations`) count characters as they are: line indents, double and non-breaking spaces in the files reflect the typesetting of the edition, not the text. In a corpus from different sources collapse them beforehand, for example `re.sub(r"[^\S\n]+", " ", text)`.

## Statistics

--8<-- "corpus/compare.md:compare_features-statistics"

## Parameters

Parameters of `compare_corpora`:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `a` | list[str] | `-` | Texts of the first corpus |
| `b` | list[str] | `-` | Texts of the second corpus |
| `window` | int | `1000` | Window size in words; `None` - whole texts |
| `features` | callable | `None` | Text feature function; `None` - `text_features` |
| `min_words` | int | `None` | Smallest number of words in a window; `None` - half a window, one word with `window=None` |

`labels`, `n_bootstrap` and `seed` go on to `compare_features`, whose parameters are:

--8<-- "corpus/compare.md:compare_features-parameters"

--8<-- "corpus/compare.md:check_comparison_params"

`compare_corpora` calls it first, so a wrong name of a corpus or seed fails before any text is processed.

## Functions of the statistics

The statistics of a row are available one by one from `ruts.corpus`:

--8<-- "corpus/compare.md:calc_cohen_d"

--8<-- "corpus/compare.md:calc_cliff_delta"

--8<-- "corpus/compare.md:bootstrap_median_diff"

--8<-- "corpus/compare.md:holm_correction"

## Usage example

Chekhov versus Tolstoy over the prose of the [`RussianLiterature`](../datasets/russianliterature.md) dataset: 77 and 42 works, 289 and 1444 windows of 1000 words, under a minute.

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

    result.loc["sents_mean", ["n_Чехов", "n_Толстой", "n_texts_Чехов", "n_texts_Толстой"]].to_dict()
    ```

    _Result_:

    ``` bash
                                   median_Чехов  median_Толстой  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    punct_ellipsis                       15.748           2.000   6.567   23.363    1.864        0.722  0.861     0.0
    punct_exclamation                    14.881           3.996   7.901   13.972    1.702        0.673  0.836     0.0
    morph_verb_form_Fin                   0.760           0.695   0.039    0.102    1.146        0.590  0.795     0.0
    punct_yo_share                        0.007           0.000   0.004    0.009    1.069        0.558  0.779     0.0
    readability_gunning_fog_index         6.011           7.970  -2.902   -1.240   -0.953       -0.535  0.232     0.0
    readability_matskovsky_index          8.609          11.234  -4.018   -1.703   -0.938       -0.526  0.237     0.0
    sents_mean                           11.172          15.136  -5.911   -2.385   -0.934       -0.526  0.237     0.0
    readability_dale_chall_index          5.200           6.676  -2.218   -0.940   -0.923       -0.523  0.239     0.0
    readability_sis_grade                 0.893           3.418  -3.610   -1.450   -0.901       -0.516  0.242     0.0
    readability_smog_index                5.746           7.294  -2.400   -0.972   -0.889       -0.512  0.244     0.0

    {'n_Чехов': 289, 'n_Толстой': 1444, 'n_texts_Чехов': 74, 'n_texts_Толстой': 42}
    ```

Chekhov has several times more ellipses and exclamations per 1000 words, shorter sentences and a higher share of finite verb forms; Tolstoy is harder by every readability formula. Three short works of Chekhov give no window, so his windows come from 74 works.

The p-values take the 1733 windows for independent (see the warning above): 87 of the 108 features have a corrected p-value below 0.01, but only 14 show a large effect by Cliff's delta. The interval of the difference of the medians resamples whole works and is the safer guide: it excludes zero for 65 of those 87 features, and for the length of a sentence it spans −5.9 to −2.4 words, where the windows alone would give −4.6 to −3.4. For the ellipses it spans 6.6 to 23.4 per 1000 words: the works of Chekhov differ in them a lot, from none to over a hundred per 1000 words.

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
