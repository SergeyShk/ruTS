# Zipf's law

!!! info ""
    **ruts.visualizers.zipf()**, **ruts.visualizers.zipf_theory()**

## Description

--8<-- "visualizers/zipf.md:zipf"

The functions are those of the [anyTS](https://sergeyshk.github.io/anyTS/visualizers/zipf/) core with the Russian labels of `ruts.constants.VISUALIZER_LABELS` by default; `labels` puts the given labels over them, for instance `labels={"title": "Закон Ципфа в SovChLit"}`.

## Parameters

--8<-- "visualizers/zipf.md:zipf-parameters"

The Zipf-Mandelbrot fit is described in [`fit_zipf_mandelbrot`](../stats/diversity_stats_funcs.md#fit_zipf_mandelbrot).

--8<-- "visualizers/zipf.md:zipf_theory"

## Usage example

Let us look at the visualizer on 100 texts of the [SovChLit](../datasets/sovchlit.md) dataset.

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    from collections import Counter
    from ruts import WordsExtractor
    from ruts.datasets import SovChLit
    from ruts.style_stats import is_stopword
    from ruts.visualizers import zipf

    # Prepare the data
    sc = SovChLit()
    texts = [text for text in sc.get_texts(limit=100)]
    text = "\n".join(texts)

    # Count word frequencies
    we = WordsExtractor(use_lexemes=True, filter_nums=True)
    tokens_with_count = Counter(word for word in we.extract(text) if not is_stopword(word))

    # Plot
    ax = zipf(tokens_with_count, num_words=100, num_labels=10, log=False, show_theory=True, alpha=1.1)
    ax.figure.savefig("zipf.png")
    ```

    _Result_:

    ![ruts](../img/zipf.png){: .center }
