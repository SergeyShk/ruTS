# Corpus plots

!!! info ""
    **ruts.visualizers.dispersion_plot()**, **ruts.visualizers.keyness_plot()**, **ruts.visualizers.collocation_network()**

## Description

Plots for the [corpus measures](../corpus/keyness.md): lexical dispersion - where in the text a word occurs, a keyness chart from the results of [`keyness`](../corpus/keyness.md) and a collocation network from the results of [`collocations`](../corpus/collocations.md). The matplotlib functions take axes `ax` and return `Axes`: without `ax` a new figure is created, with `ax` the plot goes into the user's grid; the collocation network is built by graphviz and returns a `Graph`, like the [word tree](word_tree.md).

The functions are those of the [anyTS](https://sergeyshk.github.io/anyTS/visualizers/corpus/) core with the Russian labels of the matplotlib plots of `ruts.constants.VISUALIZER_LABELS` by default; `labels` puts the given labels over them, and a pair of strings given to `keyness_plot` replaces the two labels of the legend, the others staying Russian. The `targets` words of `dispersion_plot` with stress marks are looked for without them.

## Lexical dispersion { #dispersion_plot }

--8<-- "visualizers/corpus.md:dispersion_plot"

The words are extracted by [`WordsExtractor`](../extractors/words.md): lower case with `lowercase=True`, lemmas with `use_lexemes=True`.

## Keyness chart { #keyness_plot }

--8<-- "visualizers/corpus.md:keyness_plot"

## Collocation network { #collocation_network }

--8<-- "visualizers/corpus.md:collocation_network"

## Usage example

Let us look at the visualizers on 12 texts of the [StalinWorks](../datasets/stalinworks.md) dataset.

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import matplotlib.pyplot as plt
    from ruts import WordsExtractor
    from ruts.corpus import collocations, keyness
    from ruts.datasets import FreqDict, StalinWorks
    from ruts.visualizers import collocation_network, dispersion_plot, keyness_plot

    # Prepare the data
    sw = StalinWorks()
    texts = list(sw.get_texts(limit=12))
    we = WordsExtractor(use_lexemes=True, lowercase=True, filter_nums=True)
    lemmas = [lemma for text in texts for lemma in we.extract(text)]
    words = [word for text in texts for word in WordsExtractor(filter_nums=True).extract(text)]

    # Lexical dispersion
    dispersion_plot(lemmas, ["партия", "рабочий", "революция", "царь"])

    # Keywords relative to the frequency dictionary
    freq_dict = FreqDict()
    keyness_plot(
        keyness(words, freq_dict, min_freq=5, top_n=10),
        keyness(words, freq_dict, positive=False, min_freq=5, top_n=10),
        labels=("тексты Сталина", "частотный словарь"),
    )

    # Collocation network
    graph = collocation_network(collocations(lemmas, window=3, min_freq=5, top_n=25))
    graph.render("network", format="png")
    ```

    _Result_:

    ![ruts](../img/dispersion.png){: .center }

    ![ruts](../img/keyness.png){: .center }
