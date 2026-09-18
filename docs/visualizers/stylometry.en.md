# Stylometric plots

!!! info ""
    **ruts.visualizers.dendrogram_plot()**, **ruts.visualizers.pca_plot()**, **ruts.visualizers.mds_plot()**, **ruts.visualizers.mendenhall_plot()**

## Description

Plots for [stylometry](../corpus/stylometry.md): a dendrogram and multidimensional scaling from the [`delta`](../corpus/stylometry.md#delta) distance matrix, a principal component chart from the frequencies of the most frequent words and Mendenhall curves of several texts - the set used in stylo to look at the clustering of texts by author. The functions take axes `ax` and return `Axes`.

## Dendrogram { #dendrogram_plot }

Hierarchical clustering by `scipy.cluster.hierarchy` from the distance matrix between texts; Ward's method by default, as in stylo and [Evert et al. (2015)](https://aclanthology.org/W15-0709.pdf), leaf labels are the text names from the matrix index.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `distances` | DataFrame | `-` | Symmetric distance matrix with text names |
| `method` | str | `ward` | Cluster linkage method of `scipy.cluster.hierarchy.linkage` |
| `ax` | Axes | `None` | Axes for the plot |

## Principal components { #pca_plot }

Principal component analysis of the z-scores of the relative frequencies of the most frequent units ([`frequency_table`](../corpus/stylometry.md#delta), `z_scores`) via singular value decomposition, like `pca.visualization` in stylo: the texts on the plane of the first two components with labels, the axis labels show the share of explained variance.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `corpus` | dict[str, list[str]] | `-` | Units of the texts by text name |
| `n_mfw` | int | `100` | Number of the most frequent units; `None` - all |
| `culling` | float | `0.0` | Minimum share of texts a unit must occur in |
| `ax` | Axes | `None` | Axes for the plot |

## Multidimensional scaling { #mds_plot }

Classical multidimensional scaling (Torgerson 1952) from any distance matrix: double centering of the squared distance matrix and the two leading eigenvectors; the distances between the points approximate the distances of the matrix.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `distances` | DataFrame | `-` | Symmetric distance matrix with text names |
| `ax` | Axes | `None` | Axes for the plot |

## Mendenhall curves { #mendenhall_plot }

The shares of words by length in characters ([`mendenhall_curve`](../corpus/stylometry.md#mendenhall)) for every text on one plot - a comparison of author profiles.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `corpus` | dict[str, list[str]] | `-` | Words of the texts by text name |
| `ax` | Axes | `None` | Axes for the plot |

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
