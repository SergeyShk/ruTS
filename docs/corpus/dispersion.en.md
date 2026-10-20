# Word dispersion

--8<-- "corpus/dispersion.md:dispersion"

The function wraps `dispersion` of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/dispersion/) core and strips stress marks from the words and from `word`. Words are extracted with [`WordsExtractor`](../extractors/words.md).

=== "Code"

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
    dispersion(words, parts=sizes, word="кот")

    # Three equal parts: «птица» only in the first and the last
    [(d.word, round(d.dp, 2)) for d in dispersion(words, parts=3, min_freq=3)]
    ```

=== "Result"

    ```
    [8, 7, 11]
    [Dispersion(word='кот', freq=3, dp=0.08974358974358976, dp_norm=0.12280701754385966, juilland_d=0.8725780285943101, carroll_d2=0.984770130157433, rosengren_s=0.9907464277073554, kl_divergence=0.0265483705216355)]
    [('на', 0.15), ('кот', 0.32), ('окно', 0.03), ('и', 0.03), ('птица', 0.35)]
    ```

## Parameters

--8<-- "corpus/dispersion.md:dispersion-parameters"

## Result

--8<-- "corpus/dispersion.md:Dispersion"

## Measures

--8<-- "corpus/dispersion.md:dispersion-measures"

The module `ruts.corpus.dispersion` re-exports the functions of the measures (`from ruts.corpus.dispersion import calc_dp`).

<div class="metric-card" markdown>

### Deviation of proportions DP { #dp }

`dp` · [Gries (2008)](https://www.stgries.info/research/2008_STG_Dispersion_IJCL.pdf)
{ .metric-meta }

--8<-- "corpus/dispersion.md:calc_dp"

</div>

<div class="metric-card" markdown>

### Normalized DP { #dp_norm }

`dp_norm` · Lijffijt and Gries (2012)
{ .metric-meta }

--8<-- "corpus/dispersion.md:calc_dp_norm"

</div>

<div class="metric-card" markdown>

### Juilland's D { #juilland_d }

`juilland_d` · Juilland and Chang-Rodríguez (1964)
{ .metric-meta }

--8<-- "corpus/dispersion.md:calc_juilland_d"

</div>

<div class="metric-card" markdown>

### Carroll's D2 { #carroll_d2 }

`carroll_d2` · Carroll (1970)
{ .metric-meta }

--8<-- "corpus/dispersion.md:calc_carroll_d2"

</div>

<div class="metric-card" markdown>

### Rosengren's S { #rosengren_s }

`rosengren_s` · Rosengren (1971)
{ .metric-meta }

--8<-- "corpus/dispersion.md:calc_rosengren_s"

</div>

<div class="metric-card" markdown>

### Kullback-Leibler divergence { #kl_divergence }

`kl_divergence` · [Gries (2020)](https://www.stgries.info/research/2020_STG_Dispersion_PHCL.pdf)
{ .metric-meta }

--8<-- "corpus/dispersion.md:calc_kl_divergence"

</div>
