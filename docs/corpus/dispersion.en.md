# Word dispersion

!!! info ""
    **ruts.corpus.dispersion()**, **ruts.corpus.Dispersion**

## Description

Word dispersion is how evenly a word is spread across the parts of a text or corpus. Frequency does not distinguish a word occurring once in every chapter from a word concentrated in one; dispersion measures ([Gries 2008](https://www.stgries.info/research/2008_STG_Dispersion_IJCL.pdf), [2020](https://www.stgries.info/research/2020_STG_Dispersion_PHCL.pdf)) complement frequency and are used to select vocabulary for dictionaries and learner word lists.

The text is divided into parts: `parts` is the number of parts of roughly equal size or the sizes of the parts in order (sentences, paragraphs, chapters, corpus documents), summing to the number of words. For every word the frequencies by part and six measures are computed; Gries recommends DP as the primary one.

Words are compared as they are: case and lemmatization are up to [`WordsExtractor`](../extractors/words.md).

## Measures

For $n$ parts with shares $s_i$ of the text, word frequencies by part $v_i$ and total frequency $f = \sum v_i$; $p_i = v_i / n_i$ is the relative frequency in a part of size $n_i$:

| Measure | Field | Formula | Values |
| :------ | :---- | :------ | :----- |
| Deviation of proportions DP | `dp` | $\frac{1}{2} \sum \left\lvert \frac{v_i}{f} - s_i \right\rvert$ | 0 - proportional to part sizes, tends to 1 - in one part; Gries (2008) |
| Normalized DP | `dp_norm` | $\frac{DP}{1 - \min s_i}$ | the maximum equals one for any division; Lijffijt and Gries (2012) |
| Juilland's D | `juilland_d` | $1 - \frac{V}{\sqrt{n - 1}}$, $V = \frac{\sigma(p)}{\mu(p)}$ | 1 - even, 0 - in one part; Juilland and Chang-Rodríguez (1964) |
| Carroll's D2 | `carroll_d2` | $\frac{H(p)}{\log_2 n}$ | entropy of the distribution $p_i$; 1 - even, 0 - in one part; Carroll (1970) |
| Rosengren's S | `rosengren_s` | $\frac{(\sum \sqrt{s_i v_i})^2}{f}$ | 1 - proportional, tends to $1/n$ when concentrated in one of equal parts; Rosengren (1971) |
| Kullback-Leibler divergence | `kl_divergence` | $\sum \frac{v_i}{f} \log_2 \frac{v_i / f}{s_i}$ | in bits; 0 - proportional, grows when concentrated in small parts; Gries (2020) |

The measures are available as functions `calc_dp`, `calc_dp_norm`, `calc_juilland_d`, `calc_carroll_d2`, `calc_rosengren_s`, `calc_kl_divergence` with arguments `(frequencies, sizes)` - the word frequencies by part and the part sizes - from the module `ruts.corpus.dispersion` (`from ruts.corpus.dispersion import calc_dp`); names are in `ruts.constants.DISPERSION_STATS_DESC`. For a word with zero frequency all measures are `nan`. The `dispersion` function computes the same measures for all words at once over the non-zero cells of the word × part matrix, so memory is linear in the number of words and splitting by sentences is cheap: 260 thousand words, 13 thousand lexemes and 15 thousand sentences - 0.13 s and 28 MB.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `words` | list[str] | `-` | Words of the text in order |
| `parts` | int/list[int] | `10` | Number of parts (from 2 to the number of words) or part sizes |
| `word` | str | `None` | The word whose dispersion is wanted; `None` - all words |
| `min_freq` | int | `1` | Minimum word frequency |

## Result

A list of `Dispersion` named tuples in descending frequency order: `word`, `freq` and the six measures from the table; `pd.DataFrame(result)` gives a table.

## Example

!!! example "Example"

    ``` python
    from ruts import SentsExtractor, WordsExtractor
    from ruts.corpus import dispersion

    text = (
        "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне. "
        "Завтра кот снова будет сидеть на окне и смотреть на птиц."
    )
    we = WordsExtractor(use_lexemes=True, lowercase=True)
    words = we.extract(text)
    sizes = [len(we.extract(sent)) for sent in SentsExtractor().extract(text)]
    sizes
    # [8, 7, 11]

    dispersion(words, parts=sizes, word="кот")
    # [Dispersion(word='кот', freq=3, dp=0.08974358974358973, dp_norm=0.12280701754385961,
    #  juilland_d=0.8725780285943102, carroll_d2=0.984770130157433,
    #  rosengren_s=0.9907464277073554, kl_divergence=0.0265483705216355)]

    # Three equal parts: «птица» only in the first and the last
    [(d.word, round(d.dp, 2)) for d in dispersion(words, parts=3, min_freq=3)]
    # [('на', 0.15), ('кот', 0.32), ('окно', 0.03), ('и', 0.03), ('птица', 0.35)]
    ```
