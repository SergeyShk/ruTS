# Collocations

!!! info ""
    **ruts.corpus.collocations()**, **ruts.corpus.Collocation**

## Description

--8<-- "corpus/collocations.md:collocations"

The module `ruts.corpus.collocations` re-exports the function and the measures of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/collocations/) core (`from ruts.corpus.collocations import calc_logdice`). Words are extracted with [`WordsExtractor`](../extractors/words.md); for Russian fixed expressions such as «точка зрения» or «рабочий класс» take its lemmas (`use_lexemes=True`). A `node` word with stress marks is looked for without them.

## Measures

--8<-- "corpus/collocations.md:collocations-measures"

## Parameters

--8<-- "corpus/collocations.md:collocations-parameters"

## Result

--8<-- "corpus/collocations.md:Collocation"

## Example

!!! example "Example"

    ``` python
    from ruts import WordsExtractor
    from ruts.corpus import collocations

    words = WordsExtractor(use_lexemes=True, lowercase=True).extract(
        "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне. "
        "Завтра кот снова будет сидеть на окне и смотреть на птиц."
    )

    collocations(words, window=2, top_n=1)
    # [Collocation(left='птица', right='улететь', freq_left=3, freq_right=1, freq_pair=2, score=13.0)]

    [
        (c.left, c.right, round(c.score, 2))
        for c in collocations(words, window=1, node="кот", min_freq=1, measure="mi")[:2]
    ]
    # [('завтра', 'кот', 3.12), ('кот', 'снова', 3.12)]
    ```
