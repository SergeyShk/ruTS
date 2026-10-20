# Collocations

--8<-- "corpus/collocations.md:collocations"

The module `ruts.corpus.collocations` re-exports the function of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/collocations/) core. Words are extracted with [`WordsExtractor`](../extractors/words.md); for Russian fixed expressions such as «точка зрения» or «рабочий класс» take its lemmas (`use_lexemes=True`). Stress marks are stripped from the words and from `node`.

=== "Code"

    ``` python
    from ruts import WordsExtractor
    from ruts.corpus import collocations

    words = WordsExtractor(use_lexemes=True, lowercase=True).extract(
        "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне. "
        "Завтра кот снова будет сидеть на окне и смотреть на птиц."
    )

    collocations(words, window=2, top_n=1)
    [
        (c.left, c.right, round(c.score, 2))
        for c in collocations(words, window=1, node="кот", min_freq=1, measure="mi")[:2]
    ]
    ```

=== "Result"

    ```
    [Collocation(left='птица', right='улететь', freq_left=3, freq_right=1, freq_pair=2, score=13.0)]
    [('завтра', 'кот', 3.12), ('кот', 'снова', 3.12)]
    ```

## Parameters

--8<-- "corpus/collocations.md:collocations-parameters"

## Result

--8<-- "corpus/collocations.md:Collocation"

## Measures

--8<-- "corpus/collocations.md:collocations-measures"

The module `ruts.corpus.collocations` re-exports the functions of the measures (`from ruts.corpus.collocations import calc_logdice`).

<div class="metric-card" markdown>

### Mutual information { #mi }

`mi` · Church and Hanks (1990)
{ .metric-meta }

--8<-- "corpus/collocations.md:calc_mi"

</div>

<div class="metric-card" markdown>

### MI³ { #mi3 }

`mi3` · Oakes (1998)
{ .metric-meta }

--8<-- "corpus/collocations.md:calc_mi3"

</div>

<div class="metric-card" markdown>

### t-score { #t_score }

`t_score` · Church et al. (1991)
{ .metric-meta }

--8<-- "corpus/collocations.md:calc_t_score"

</div>

<div class="metric-card" markdown>

### Dice coefficient { #dice }

`dice`
{ .metric-meta }

--8<-- "corpus/collocations.md:calc_dice"

</div>

<div class="metric-card" markdown>

### logDice { #logdice }

`logdice` · [Rychlý (2008)](https://www.sketchengine.eu/glossary/logdice/)
{ .metric-meta }

--8<-- "corpus/collocations.md:calc_logdice"

</div>

<div class="metric-card" markdown>

### Log-likelihood { #log_likelihood }

`log_likelihood` · Dunning (1993)
{ .metric-meta }

--8<-- "corpus/collocations.md:calc_log_likelihood"

</div>

<div class="metric-card" markdown>

### NPMI { #npmi }

`npmi` · Bouma (2009)
{ .metric-meta }

--8<-- "corpus/collocations.md:calc_npmi"

</div>

<div class="metric-card" markdown>

### Minimum sensitivity { #min_sensitivity }

`min_sensitivity` · Pedersen (1998)
{ .metric-meta }

--8<-- "corpus/collocations.md:calc_min_sensitivity"

</div>
