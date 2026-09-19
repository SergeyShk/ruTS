# Installation

The library can be installed with `pip` or by cloning the project repository with `git`.

## Dependencies

ruTS relies on the following third-party libraries:

*   `python` - 3.11 or newer
*   `nltk`
*   `pymorphy3`
*   `razdel`
*   `scipy`
*   `spaCy` - 3.7.0 or newer
*   `numpy`
*   `pandas`
*   `matplotlib`
*   `graphviz`

## Installing with `pip`

Run in the command line:

``` bash
pip install ruts
```

This installs the release version of the library with all dependencies.

!!! warning "Graphviz"
    The `graphviz` package among the dependencies is only a wrapper: rendering the [word tree](visualizers/word_tree.md) and the [collocation network](visualizers/corpus.md#collocation_network) requires the [Graphviz](https://graphviz.org/download/) executables (`brew install graphviz`, `apt install graphviz`, `conda install graphviz`), otherwise `render()` and displaying the graph in Jupyter fail with `ExecutableNotFound`. Nothing else needs them.

!!! tip "Fast morphological analysis"
    For corpora, install the library with the `fast` extra:

    ``` bash
    pip install "ruts[fast]"
    ```

    It adds the [DAWG2](https://github.com/pymorphy2-fork/DAWG) C extension for pymorphy3 (CPython only, wheels are available for Linux, macOS and Windows): word form analysis gets about 5x faster (175 vs 34 thousand word forms per second), `MorphStats` on a 70-thousand-word text about a third faster, because analyses are cached per word form and the rest of the time goes into counting. Without the extra the library works the same, just slower.

!!! tip "spaCy model"
    The [spaCy components](components.md), the [syntactic statistics](stats/syntax_stats.md) and the examples that start with `spacy.load("ru_core_news_sm")` need the Russian-language model; without it `spacy.load` fails with `OSError: [E050]`. The model is installed separately:

    ``` bash
    python -m spacy download ru_core_news_sm
    ```

!!! note "Datasets"
    The [datasets](datasets/sovchlit.md) are downloaded by default into the `ruts_data` directory next to the package (`DEFAULT_DATA_DIR` in `ruts.constants`): for an installation from a wheel that is `site-packages/ruts_data`, where writing may be forbidden for a system Python. In that case pass your own directory in the `data_dir` argument when creating a dataset.

!!! note "Note"
    A detailed guide to the `pip` package manager is available on its [website](https://pip.pypa.io/en/stable/).

## Installing with `git`

This way you get the latest version of the library straight from the project repository. Run the following commands:

1. Clone the repository into a local directory:

    ``` bash
    git clone https://github.com/SergeyShk/ruTS.git
    ```

2. Change into it:

    ``` bash
    cd ruTS
    ```

3. Install the library into the current environment:

    ``` bash
    pip install .
    ```

    For development it is more convenient to use [uv](https://docs.astral.sh/uv/), which creates an isolated environment and installs all dependencies, including the development tools:

    ``` bash
    uv sync --all-groups --no-group examples
    ```

    The `examples` group with Jupyter is needed only for the [example notebooks](examples.md).

!!! note "Note"
    A detailed guide to the `git` version control system is available on its [website](https://git-scm.com/).
