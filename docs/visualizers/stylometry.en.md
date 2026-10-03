# Stylometric plots

!!! info ""
    **ruts.visualizers.dendrogram_plot()**, **ruts.visualizers.pca_plot()**, **ruts.visualizers.mds_plot()**, **ruts.visualizers.mendenhall_plot()**

## Description

Plots for [stylometry](../corpus/stylometry.md): a dendrogram and multidimensional scaling from the [`delta`](../corpus/stylometry.md#delta) distance matrix, a principal component chart from the frequencies of the most frequent words and Mendenhall curves of several texts - the set used in stylo to look at the clustering of texts by author. The functions take axes `ax` and return `Axes`.

The functions are those of the [anyTS](https://sergeyshk.github.io/anyTS/visualizers/stylometry/) core with the Russian labels of `ruts.constants.VISUALIZER_LABELS` by default; `labels` puts the given labels over them. The frequencies of the principal components come from [`frequency_table`](../corpus/stylometry.md#delta) and the curves from [`mendenhall_curve`](../corpus/stylometry.md#mendenhall).

## Dendrogram { #dendrogram_plot }

--8<-- "visualizers/stylometry.md:dendrogram_plot"

## Principal components { #pca_plot }

--8<-- "visualizers/stylometry.md:pca_plot"

## Multidimensional scaling { #mds_plot }

--8<-- "visualizers/stylometry.md:mds_plot"

## Mendenhall curves { #mendenhall_plot }

--8<-- "visualizers/stylometry.md:mendenhall_plot"

## Usage example

Let us look at the visualizers on 8 texts of the [StalinWorks](../datasets/stalinworks.md) dataset.

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import matplotlib.pyplot as plt
    from ruts import WordsExtractor
    from ruts.corpus import delta
    from ruts.datasets import StalinWorks
    from ruts.visualizers import dendrogram_plot, mds_plot, mendenhall_plot, pca_plot

    # Prepare the data
    sw = StalinWorks()
    we = WordsExtractor(use_lexemes=True, lowercase=True, filter_nums=True)
    corpus = {f"текст {i + 1}": we.extract(text) for i, text in enumerate(sw.get_texts(limit=8))}
    distances = delta(corpus, n_mfw=100, variant="cosine")

    # Dendrogram and principal components on one figure
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5))
    dendrogram_plot(distances, ax=left)
    pca_plot(corpus, n_mfw=100, ax=right)

    # Multidimensional scaling and Mendenhall curves
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5))
    mds_plot(distances, ax=left)
    mendenhall_plot({name: corpus[name] for name in list(corpus)[:3]}, ax=right)
    ```

    _Result_:

    ![ruts](../img/stylometry.png){: .center }

    ![ruts](../img/mds_mendenhall.png){: .center }
