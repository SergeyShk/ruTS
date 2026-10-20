# Sentence lengths

``` {.python .signature}
sentence_lengths_plot(source, window=10, inset=True, ax=None, labels=None, sents_extractor=None, words_extractor=None)
```

--8<-- "visualizers/sentences.md:sentence_lengths_plot"

The functions are those of the [anyTS](https://sergeyshk.github.io/anyTS/visualizers/sentences/) core; for a string ruTS passes its Russian [`SentsExtractor`](../extractors/sentences.md) and [`WordsExtractor`](../extractors/words.md) by default, and the `sents_extractor` and `words_extractor` parameters replace them. The default labels are the Russian ones of `ruts.constants.VISUALIZER_LABELS`; `labels` puts the given labels over them.

The curve of the first text of the [StalinWorks](../datasets/stalinworks.md) dataset:

``` python
from ruts.datasets import StalinWorks
from ruts.visualizers import sentence_lengths_plot

text = next(StalinWorks().get_texts(limit=1))
sentence_lengths_plot(text, window=10)
```

![ruts](../img/sentences.png){: .center }

## Parameters

--8<-- "visualizers/sentences.md:sentence_lengths_plot-parameters"

## Lengths of the sentences { #sentence_lengths }

``` {.python .signature}
sentence_lengths(source, sents_extractor=None, words_extractor=None)
```

The lengths of the sentences in words, in order: a string is split into sentences by the sentence extractor and every sentence into words by the word extractor; the sentences of a `Doc` come from its boundaries and its words from its tokens, punctuation and symbols left out and the parts of a hyphenated word joined (`во-первых` is one word), while a `Doc` without boundaries or with partial ones (`has_sents`) is counted as its text, by the extractors. Sentences without words are skipped. Ready lengths (non-negative integers in a sequence or an iterator) are used as they are. The arguments are those of `sentence_lengths_plot`.

A table, a set, a mapping, bytes, a length that is not an integer and an extractor of another type raise `SourceTypeError`, a negative length `SourceError`.

=== "Code"

    ``` python
    from ruts.visualizers import sentence_lengths

    sentence_lengths("Кот спит. Где пёс? - Ест, - сказала она.")
    sentence_lengths(text)[:5]
    ```

=== "Result"

    ```
    [2, 2, 3]
    [66, 9, 16, 9, 21]
    ```
