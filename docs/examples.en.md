# Examples

Jupyter notebooks in the [examples/](https://github.com/SergeyShk/ruTS/tree/master/examples) directory of the repository. Each opens in Google Colab with a button and installs the library and the spaCy model itself; the outputs of all cells are stored in the files, so the notebooks can be read without running.

## Text walkthrough

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb)

[01_text_walkthrough.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb) - Chekhov's short story "The Death of a Government Clerk" through every tool of the library in turn: sentence and word extraction, basic statistics, readability with coefficient presets, lexical diversity and windowed computation, morphology, SEO style metrics on fiction and on officialese, phonostatistics, syntax and cohesion from the spaCy parse, lexical sophistication by the frequency dictionary, highlighting, Zipf's law and the sentence length curve. At the end all statistics are attached as spaCy components, and a single `nlp.pipe` pass over the `TextsByGrade` dataset yields a table of statistics by text grade. The notebook is in Russian.

## Text complexity by school grade

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/02_text_complexity_by_grade.ipynb)

[02_text_complexity_by_grade.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/02_text_complexity_by_grade.ipynb) - the 68 `TextsByGrade` texts labelled with grades 1 to 17 as a single complexity axis onto which every group of statistics is laid in turn: Spearman correlation of the eleven readability formulas with the label and their error in grades, three coefficient presets, lexical diversity (unrelated to grade) versus lexical sophistication by the frequency dictionary, syntax and morphology (nominal load, tree depth, passive, share of verbs), cohesion, distributions by school stage and a check on the independent first-grade reader `SovChLit`. The notebook is in Russian.

## Pairwise comparison of prose writers

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/03_prose_authors.ipynb)

[03_prose_authors.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/03_prose_authors.ipynb) - ten prose writers of `RussianLiterature`, 200 windows of 1000 words each, 130 `text_features` and Cliff's delta for 45 pairs: the three strongest features of every pair, a detailed look at Tolstoy and Dostoevsky (`compare_features`, feature distributions, keywords - speech against narration), the number of large-effect features as a distance (from 6 for Gogol-Turgenev to 67 for Herzen-Dostoevsky), edition features (quotes, the letter ё) that must be excluded, universal discriminators (semicolons, ellipses, word length, windowed diversity measures), dendrogram and multidimensional scaling by features and by Burrows's delta with a Mantel test, authorship attribution of 1000-word windows with held-out works (delta variants, number of frequent words, word forms against character trigrams, text features as a classifier, confusion matrix, Zeta markers). The notebook is in Russian.

## Running locally

``` bash
uv sync --group examples
uv run jupyter lab examples/
```

`make notebooks` executes all notebooks, writes the outputs into the files and strips the execution metadata; the `examples.yml` workflow runs the notebooks on a schedule and on demand.
