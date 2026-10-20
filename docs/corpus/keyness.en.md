# Keywords

``` {.python .signature}
keyness(target, reference, measure='log_likelihood', min_freq=1, positive=True, top_n=None, lemmatize=True)
```

--8<-- "corpus/keyness.md:keyness"

The function wraps `keyness` of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/keyness/) core and also takes the [Lyashevskaya and Sharoff frequency dictionary](../datasets/freq2011.md) `FreqDict` as the reference; `FrequencyReference` is in `ruts.corpus` next to it. Words are extracted with [`WordsExtractor`](../extractors/words.md).

=== "Code"

    ``` python
    from ruts import WordsExtractor
    from ruts.corpus import keyness

    we = WordsExtractor(use_lexemes=True, lowercase=True)
    target = we.extract(
        "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне. "
        "Завтра кот снова будет сидеть на окне и смотреть на птиц."
    )
    reference = we.extract(
        "Собака лежала на полу и дремала. Потом собака ела и снова дремала. Завтра собака будет гулять."
    )

    keyness(target, reference, top_n=1)
    [(k.word, round(k.g2, 2)) for k in keyness(target, reference, positive=False, top_n=2)]
    ```

=== "Result"

    ```
    [Keyword(word='кот', freq_target=3, freq_reference=0.0, ipm_target=115384.61538461539, ipm_reference=0.0, g2=2.8774384815713177, p_value=0.08982881315854577, log_ratio=1.8845227825800641, score=2.8774384815713177)]
    [('собака', -5.79), ('дремать', -3.86)]
    ```

## Parameters

--8<-- "corpus/keyness.md:keyness-parameters"

`reference` may also be `FreqDict`, and one more parameter tells what the target corpus is against it:

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `lemmatize` | `bool` | `True` | The target corpus is word forms, `False` - lemmas (`FreqDict` only) |

A frequency dictionary that is not downloaded raises `DatasetNotFoundError`.

--8<-- "corpus/keyness.md:check_keyness_params"

## Reference by frequencies

--8<-- "corpus/keyness.md:FrequencyReference"

The frequency dictionary `FreqDict` passed as `reference` is turned into such a reference:

| Field | `FreqDict` |
| :---- | :--------- |
| `counts` | the frequencies of `FreqDict.word_ipm` converted to occurrences in the corpus of the dictionary |
| `size` | `CORPUS_SIZE` of `ruts.datasets.freq2011`, 92 million tokens of the modern subcorpus of the Russian National Corpus |
| `missing` | the least frequency of the dictionary `FreqDict.min_ipm`, 0.4 ipm (about 37 occurrences) |
| `key` | the lemma of the dictionary: a word form is lemmatized by pymorphy3 (with `lemmatize=False` it is taken as a lemma) and brought to the conventions of the dictionary by `ruts.lexical_stats.dictionary_lemma`, as in [`LexicalStats`](../stats/lexical_stats.md) |
| `keep` | the words of the Cyrillic letters of `ruts.lexical_stats.DICTIONARY_WORD`; numbers and words with Latin letters are left out |

A dictionary entry absent from the text can be a negative keyword only if some word form is reduced to it: the dictionary keeps separate entries «его», «ее», «их» (possessive pronouns) and «во», «со», while pymorphy3 reduces these word forms to «он», «она», «они», «в», «с», and without this rule they would be negative keywords of any text. Such entries - about 1,100 for word forms and 1,500 for lemmas - are listed in the resources of the package; words that pymorphy3 only predicts («Михайлыч», «дитё») are not seen by the rule.

With `lemmatize=False` the conventions of the dictionary cannot be recovered from a lemma: the short form, the plural and the spelling variant are lost («должный» instead of «должен», «деньга» instead of «деньги», «счастие» instead of «счастье»), and such entries come out as false keywords. Compare word forms with the dictionary.

=== "Code"

    ``` python
    from ruts import WordsExtractor
    from ruts.corpus import keyness
    from ruts.datasets import FreqDict

    # The dictionary is downloaded once with FreqDict().download()
    words = WordsExtractor().extract(
        "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне. "
        "Завтра кот снова будет сидеть на окне и смотреть на птиц."
    )
    [(k.word, round(k.log_ratio, 1)) for k in keyness(words, FreqDict(), min_freq=3, top_n=2)]
    ```

=== "Result"

    ```
    [('кот', 11.5), ('птица', 10.3)]
    ```

## Result

--8<-- "corpus/keyness.md:Keyword"

## Measures

--8<-- "corpus/keyness.md:keyness-measures"

The module `ruts.corpus.keyness` re-exports the functions of the measures (`from ruts.corpus.keyness import calc_log_likelihood`).

<div class="metric-card" markdown>

### Log-likelihood { #log_likelihood }

`log_likelihood` · `g2` · `p_value` · [Rayson and Garside (2000)](https://ucrel.lancs.ac.uk/llwizard.html)
{ .metric-meta }

--8<-- "corpus/keyness.md:calc_log_likelihood"

--8<-- "corpus/keyness.md:calc_p_value"

</div>

<div class="metric-card" markdown>

### Chi-square { #chi2 }

`chi2`
{ .metric-meta }

--8<-- "corpus/keyness.md:calc_chi2"

</div>

<div class="metric-card" markdown>

### %DIFF { #diff }

`diff` · [Gabrielatos and Marchi (2011)](http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf)
{ .metric-meta }

--8<-- "corpus/keyness.md:calc_diff"

</div>

<div class="metric-card" markdown>

### Log Ratio { #log_ratio }

`log_ratio` · [Hardie (2014)](http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/)
{ .metric-meta }

--8<-- "corpus/keyness.md:calc_log_ratio"

</div>

<div class="metric-card" markdown>

### BIC { #bic }

`bic` · Wilson (2013)
{ .metric-meta }

--8<-- "corpus/keyness.md:calc_bic"

</div>

<div class="metric-card" markdown>

### ELL { #ell }

`ell` · Johnston, Berry and Mielke (2006)
{ .metric-meta }

--8<-- "corpus/keyness.md:calc_ell"

</div>

<div class="metric-card" markdown>

### Odds ratio { #odds_ratio }

`odds_ratio`
{ .metric-meta }

--8<-- "corpus/keyness.md:calc_odds_ratio"

</div>
