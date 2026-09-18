# Sentence lengths

!!! info ""
    **ruts.visualizers.sentence_lengths_plot()**, **ruts.visualizers.sentence_lengths()**

## Description

The sentence length curve - the rhythm of a text: the length of every sentence in words in order, a moving average over a window of `window` sentences and an inset with the histogram of lengths. Alternation of short and long sentences is an editorial sign of lively text, a flat curve - of monotonous text. `sentence_lengths` extracts the lengths: sentences of a string - by razdel, of a `Doc` object - by sentence boundaries (without boundaries - from the text), ready lengths - any sequence of integers, including a numpy array and a Series - are used as they are; sentences without words are skipped. The function takes axes `ax` and returns `Axes`.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc/Iterable[int] | `-` | Text, Doc object or sentence lengths (list, numpy array, Series) |
| `window` | int | `10` | Moving average window in sentences |
| `inset` | bool | `True` | Show the histogram inset |
| `ax` | Axes | `None` | Axes for the plot |

## Usage example

!!! example "Example"

    _Code_:

    ``` python
    from ruts.datasets import StalinWorks
    from ruts.visualizers import sentence_lengths, sentence_lengths_plot

    text = next(StalinWorks().get_texts(limit=1))
    sentence_lengths(text)[:5]
    # [66, 9, 16, 9, 21]

    sentence_lengths_plot(text, window=10)
    ```

    _Result_:

    ![ruts](../img/sentences.png){: .center }
