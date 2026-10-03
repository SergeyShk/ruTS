# Word dispersion

!!! info ""
    **ruts.corpus.dispersion()**, **ruts.corpus.Dispersion**

## Description

--8<-- "corpus/dispersion.md:dispersion"

The module `ruts.corpus.dispersion` re-exports the function and the measures of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/dispersion/) core (`from ruts.corpus.dispersion import calc_dp`). Words are extracted with [`WordsExtractor`](../extractors/words.md).

## Measures

--8<-- "corpus/dispersion.md:dispersion-measures"

## Parameters

--8<-- "corpus/dispersion.md:dispersion-parameters"

## Result

--8<-- "corpus/dispersion.md:Dispersion"

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
    # [Dispersion(word='кот', freq=3, dp=0.08974358974358976, dp_norm=0.12280701754385966,
    #  juilland_d=0.8725780285943101, carroll_d2=0.984770130157433,
    #  rosengren_s=0.9907464277073554, kl_divergence=0.0265483705216355)]

    # Three equal parts: «птица» only in the first and the last
    [(d.word, round(d.dp, 2)) for d in dispersion(words, parts=3, min_freq=3)]
    # [('на', 0.15), ('кот', 0.32), ('окно', 0.03), ('и', 0.03), ('птица', 0.35)]
    ```
