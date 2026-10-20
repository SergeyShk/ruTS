# Literature fingerprinting

``` {.python .signature}
fingerprinting(texts, segment_len=10, metric=None, x_size=800, y_size=600, cmap='PuOr', ax=None, labels=None)
```

--8<-- "visualizers/fingerprinting.md:fingerprinting"

The function is that of the [anyTS](https://sergeyshk.github.io/anyTS/visualizers/fingerprinting/) core with the Russian title of `ruts.constants.VISUALIZER_LABELS` by default, which `labels` replaces; the measures of [lexical diversity](../stats/diversity_stats.md) of ruTS, functions of a list of words such as `calc_ttr` or `calc_simpson_index`, serve as the `metric`.

The visualization of 100 texts of the [SovChLit](../datasets/sovchlit.md) dataset:

``` python
from ruts import WordsExtractor
from ruts.datasets import SovChLit
from ruts.diversity_stats import calc_simpson_index
from ruts.visualizers import fingerprinting

we = WordsExtractor(lowercase=True)
words = [we.extract(text) for text in SovChLit().get_texts(limit=100)]
ax = fingerprinting(words, metric=calc_simpson_index, x_size=1000, y_size=800)
ax.figure.savefig("fingerprinting.png")
```

![ruts](../img/fingerprinting.png){: .center }

## Parameters

--8<-- "visualizers/fingerprinting.md:fingerprinting-parameters"

!!! note "Note"
    In ruTS the colour map is `PuOr` by default.
