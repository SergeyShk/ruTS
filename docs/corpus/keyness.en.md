# Keywords

!!! info ""
    **ruts.corpus.keyness()**, **ruts.corpus.Keyword**, **ruts.corpus.FrequencyReference**

## Description

--8<-- "corpus/keyness.md:keyness"

The function wraps `keyness` of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/keyness/) core and also takes the [Lyashevskaya and Sharoff frequency dictionary](../datasets/freq2011.md) `FreqDict` as the reference; `FrequencyReference` is in `ruts.corpus` next to it, and the functions of the measures in `ruts.corpus.keyness` (`from ruts.corpus.keyness import calc_log_likelihood`). Words are extracted with [`WordsExtractor`](../extractors/words.md).

## Measures

--8<-- "corpus/keyness.md:keyness-measures"

## Parameters

--8<-- "corpus/keyness.md:keyness-parameters"

`reference` may also be `FreqDict`, and one more parameter tells what the target corpus is against it:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `lemmatize` | bool | `True` | The target corpus is word forms, `False` - lemmas (`FreqDict` only) |

## Reference by frequencies

--8<-- "corpus/keyness.md:FrequencyReference"

The frequency dictionary `FreqDict` passed as `reference` is turned into such a reference:

| Field | `FreqDict` |
| :---: | :--------- |
| `counts` | the ipm of the lemmas of `FreqDict.entries` converted to occurrences in the corpus of the dictionary |
| `size` | `CORPUS_SIZE` of `ruts.datasets.freq2011`, 92 million tokens of the modern subcorpus of the Russian National Corpus |
| `missing` | the least frequency of the dictionary `FreqDict.min_ipm`, 0.4 ipm (about 37 occurrences) |
| `key` | the lemma of the dictionary: a word form is lemmatized by pymorphy3 (with `lemmatize=False` it is taken as a lemma) and brought to the conventions of the dictionary by `ruts.lexical_stats.dictionary_lemma`, as in [`LexicalStats`](../stats/lexical_stats.md) |
| `keep` | the words of the Cyrillic letters of `ruts.lexical_stats.DICTIONARY_WORD`; numbers and words with Latin letters are left out |

Only a dictionary entry that some word is reduced to can be a negative keyword: the dictionary keeps separate entries «его», «ее», «их» (possessive pronouns) and «во», «со», while pymorphy3 reduces these words to «он», «она», «они», «в», «с», so they would have zero frequency in any text.

## Result

--8<-- "corpus/keyness.md:Keyword"

## Example

!!! example "Example"

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
    # [Keyword(word='кот', freq_target=3, freq_reference=0.0, ipm_target=115384.61538461539,
    #  ipm_reference=0.0, g2=2.8774384815713177, p_value=0.08982881315854577,
    #  log_ratio=1.8845227825800641, score=2.8774384815713177)]

    [(k.word, round(k.g2, 2)) for k in keyness(target, reference, positive=False, top_n=2)]
    # [('собака', -5.79), ('дремать', -3.86)]

    # Relative to the frequency dictionary (after FreqDict().download()) - by word forms
    from ruts.datasets import FreqDict

    words = WordsExtractor().extract(
        "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне. "
        "Завтра кот снова будет сидеть на окне и смотреть на птиц."
    )
    [(k.word, round(k.log_ratio, 1)) for k in keyness(words, FreqDict(), min_freq=3, top_n=2)]
    # [('кот', 11.5), ('птица', 10.3)]
    ```
