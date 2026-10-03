# Vocabulary growth and frequency spectrum

!!! info ""
    **ruts.visualizers.heaps_plot()**, **ruts.visualizers.frequency_spectrum_plot()**

## Description

Two plots about the word distribution of a text complementing [Zipf's law](zipf.md): vocabulary growth with text length by Heaps' law and the frequency spectrum - how many lexemes occur exactly once, twice, three times. Both plots exist in zipfR (`plot.vgc`, `plot.spc`). The functions take axes `ax` and return `Axes`.

The functions are those of the [anyTS](https://sergeyshk.github.io/anyTS/visualizers/vocabulary/) core with the Russian labels of `ruts.constants.VISUALIZER_LABELS` by default; `labels` puts the given labels over them. The fit of Heaps' law is described in [`fit_heaps`](../stats/diversity_stats_funcs.md#heaps_beta) and the spectrum in [`calc_frequency_spectrum`](../stats/diversity_stats_funcs.md#frequency_spectrum).

## Heaps' law { #heaps_plot }

--8<-- "visualizers/vocabulary.md:heaps_plot"

## Frequency spectrum { #frequency_spectrum_plot }

--8<-- "visualizers/vocabulary.md:frequency_spectrum_plot"

## Usage example

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import matplotlib.pyplot as plt
    from ruts import WordsExtractor
    from ruts.datasets import StalinWorks
    from ruts.visualizers import frequency_spectrum_plot, heaps_plot

    # Prepare the data
    sw = StalinWorks()
    we = WordsExtractor(use_lexemes=True, lowercase=True, filter_nums=True)
    lemmas = [lemma for text in sw.get_texts(limit=12) for lemma in we.extract(text)]

    # Plot
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 4.5))
    heaps_plot(lemmas, ax=left)
    frequency_spectrum_plot(lemmas, ax=right)
    ```

    _Result_:

    ![ruts](../img/vocabulary.png){: .center }
