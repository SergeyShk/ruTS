# Installation

The library can be installed with `pip` or from the project repository with `git`.

## Dependencies

*   `python` - 3.11 or newer
*   [`anyts`](https://sergeyshk.github.io/anyTS/) - 0.4.6 or newer within 0.4, the language-independent core ruTS is built on
*   [`rumorph`](https://github.com/SergeyShk/ruMorph) - 0.5 or newer within 0.5, the morphological analyzer
*   [`anyseg`](https://github.com/SergeyShk/anySeg) - 0.2 or newer within 0.2, the segmenter into tokens and sentences
*   `scipy`
*   `spaCy` - 3.8.15 or newer
*   `numpy`
*   `pandas`
*   `matplotlib`
*   `graphviz`

## Installing with `pip`

The release version is installed with all dependencies:

``` bash
pip install ruts
```

!!! warning "Graphviz"
    Only the [word tree](visualizers/word_tree.md) and the [collocation network](visualizers/corpus.md#collocation_network) need the [Graphviz](https://graphviz.org/download/) executables (`brew install graphviz`, `apt install graphviz`, `conda install graphviz`): the `graphviz` package among the dependencies is just a wrapper, and without them `render()` and displaying the graph in Jupyter fail with `ExecutableNotFound`.

`import ruts` loads neither spaCy nor matplotlib nor pandas: they come on first use of a `Doc`, components, plots and corpus functions.

!!! tip "spaCy model"
    The [spaCy components](components.md), the [syntactic statistics](stats/syntax_stats.md) and the [recommended pipeline](components.md#load_pipeline) `ruts.load_pipeline()` need the Russian-language model, without it loading fails with `OSError: [E050]`. The model is installed separately:

    ``` bash
    python -m spacy download ru_core_news_sm
    ```

    The larger models `ru_core_news_md` and `ru_core_news_lg` (93 and 670 MB against 47) hardly change the ruTS statistics: on the gold Universal Dependencies annotation (Taiga and GSD) they are less than one UAS point more accurate than `sm`.

!!! note "Datasets"
    The [datasets](datasets/sovchlit.md) are downloaded by default into the `ruts_data` directory next to the package (`DEFAULT_DATA_DIR` in `ruts.constants`), for an installation from a wheel into `site-packages/ruts_data`, where writing may be forbidden for a system Python. Your own directory is set by the `data_dir` argument of a dataset or by the `RUTS_DATA_DIR` environment variable before the package is imported:

    ``` bash
    export RUTS_DATA_DIR=~/ruts_data
    ```

!!! note "Note"
    A guide to `pip` is on its [website](https://pip.pypa.io/en/stable/).

## Installing with `git`

The latest version is installed from the project repository:

1. Clone the repository:

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

    For development [uv](https://docs.astral.sh/uv/) is more convenient: it creates an isolated environment with all dependencies, including the development tools:

    ``` bash
    uv sync --all-groups --no-group examples
    ```

    The `examples` group with Jupyter is needed only for the [example notebooks](examples.md).

!!! note "Note"
    A guide to `git` is on its [website](https://git-scm.com/).
