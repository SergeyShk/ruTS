# Examples

Jupyter notebooks in the [examples/](https://github.com/SergeyShk/ruTS/tree/master/examples) directory of the repository. Each opens in Google Colab with a button and installs the library and the spaCy model itself; the outputs of all cells are stored in the files, so the notebooks can be read without running.

## Text walkthrough

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb)

[01_text_walkthrough.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb) - Chekhov's short story "The Death of a Government Clerk" through every tool of the library in turn: sentence and word extraction, basic statistics, readability with coefficient presets, lexical diversity and windowed computation, morphology, SEO style metrics on fiction and on officialese, phonostatistics, syntax and cohesion from the spaCy parse, lexical sophistication by the frequency dictionary, highlighting, Zipf's law and the sentence length curve. At the end all statistics are attached as spaCy components, and a single `nlp.pipe` pass over the `TextsByGrade` dataset yields a table of statistics by text grade. The notebook is in Russian.

## Running locally

``` bash
uv sync --all-groups
uv run jupyter lab examples/
```

`make notebooks` executes all notebooks and writes the outputs into the files; the `examples.yml` workflow runs the same on a schedule and on demand.
