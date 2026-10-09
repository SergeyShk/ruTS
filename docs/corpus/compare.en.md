# Corpus comparison

!!! info ""
    **ruts.corpus.compare_corpora()**, **ruts.corpus.compare_features()**, **ruts.corpus.check_comparison_params()**, **ruts.corpus.corpus_features()**, **ruts.corpus.text_features()**, **ruts.corpus.split_windows()**, **ruts.corpus.sentence_rhythm()**, **ruts.corpus.calc_cohen_d()**, **ruts.corpus.calc_cliff_delta()**, **ruts.corpus.bootstrap_median_diff()**, **ruts.corpus.holm_correction()**

## Description

`compare_corpora` compares two corpora of Russian texts by every feature of a text at once: which statistics tell authors, genres, translations, human and generated texts apart - and by how much. For single words [`keyness`](keyness.md) does the same, for the distances between texts - [`delta`](stylometry.md#delta). It builds the tables of the features of the windows of both corpora and compares them with the `compare_features` of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/compare/) core:

--8<-- "corpus/compare.md:compare_features"

The texts are cut in a row into windows of exactly `window` words by `split_windows`, so the windows of all texts have one length; an incomplete remainder at the end of a text and a text shorter than a window are dropped unless `min_words` allows shorter windows. The features of every window are computed by `text_features` or a function of one's own.

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
| `min_words` | int | `None` | Smallest number of words in a window; `None` - a whole window, one word with `window=None` |

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

Chekhov versus Tolstoy over the prose of the [`RussianLiterature`](../datasets/russianliterature.md) dataset: 77 and 42 works, 249 and 1423 windows of 1000 words, under a minute.

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
    punct_ellipsis                       14.000           2.000   5.000   25.000    1.869        0.707  0.853     0.0
    punct_exclamation                    14.000           4.000   7.000   13.000    1.670        0.658  0.829     0.0
    morph_verb_form_Fin                   0.756           0.695   0.037    0.100    1.123        0.573  0.786     0.0
    punct_yo_share                        0.007           0.000   0.002    0.010    1.026        0.533  0.766     0.0
    readability_gunning_fog_index         6.088           7.962  -2.881   -1.007   -0.934       -0.521  0.240     0.0
    readability_dale_chall_index          5.280           6.702  -2.378   -0.833   -0.914       -0.518  0.241     0.0
    readability_smog_index                5.880           7.314  -2.447   -0.936   -0.883       -0.508  0.246     0.0
    readability_matskovsky_index          8.660          11.281  -4.101   -1.178   -0.910       -0.503  0.249     0.0
    sents_mean                           11.236          15.152  -6.141   -1.669   -0.902       -0.501  0.250     0.0
    readability_sis_grade                 0.974           3.478  -3.858   -1.138   -0.879       -0.499  0.251     0.0

    {'n_Чехов': 249, 'n_Толстой': 1423, 'n_texts_Чехов': 57, 'n_texts_Толстой': 41}
    ```

Chekhov has several times more ellipses and exclamations per 1000 words, shorter sentences and a higher share of finite verb forms; Tolstoy is harder by every readability formula. Twenty stories of Chekhov are shorter than 1000 words and give no window, so his windows come from 57 works; with a smaller window they would be compared too.

The p-values take the 1672 windows for independent (see the warning above): 84 of the 108 features have a corrected p-value below 0.01, but only 14 show a large effect by Cliff's delta. The interval of the difference of the medians resamples whole works and is the safer guide: it excludes zero for 63 of those 84 features, and for the length of a sentence it spans −6.1 to −1.7 words, where the windows alone would give −4.6 to −3.2. For the ellipses it spans 5 to 25 per 1000 words: the works of Chekhov differ in them a lot, on average from a fraction of one to 84 per 1000 words.

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
