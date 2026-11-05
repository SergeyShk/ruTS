# Examples

Jupyter notebooks in the [examples/](https://github.com/SergeyShk/ruTS/tree/master/examples) directory of the repository, in Russian. The cell outputs are stored, so the notebooks can be read without running; the button opens a notebook in Google Colab, where it installs everything it needs itself.

## Text walkthrough

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb)

[01_text_walkthrough.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb) - Chekhov's short story "The Death of a Government Clerk" through every tool of the library in turn: extractors, every group of statistics, highlighting and plots. At the end the statistics are attached as spaCy components, and a single `nlp.pipe` pass over the `TextsByGrade` dataset yields a table of statistics by text grade.

## Text complexity by school grade

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/02_text_complexity_by_grade.ipynb)

[02_text_complexity_by_grade.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/02_text_complexity_by_grade.ipynb) - the 68 `TextsByGrade` texts labelled with grades 1 to 17 as a complexity axis onto which every group of statistics is laid in turn: readability formulas and coefficient presets, lexis, syntax and morphology, cohesion. At the end - a check on the independent first-grade reader `SovChLit`.

## Pairwise comparison of prose writers

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/03_prose_authors.ipynb)

[03_prose_authors.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/03_prose_authors.ipynb) - ten prose writers of `RussianLiterature`, up to 200 windows of 1000 words per writer, Cliff's delta over the `text_features` for 45 pairs: how Tolstoy and Dostoevsky differ, which features reflect the edition rather than the style, which ones separate every pair, the closeness of the writers by features and by Burrows's delta with a Mantel test, authorship attribution by frequent words, character trigrams and text features.

## Stalin's language over half a century

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/04_stalin_corpus.ipynb)

[04_stalin_corpus.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/04_stalin_corpus.ipynb) - corpus measures as tools of diachrony on `StalinWorks` (1243 texts from 1901 to 1952, four periods): keywords against the frequency dictionary and between the periods, collocates of the words «враг» (enemy) and «партия» (party) by period, dispersion of words over the volumes, the `kwic` concordance by lemma, Zipf's law and windowed MTLD.

## Verse and sound

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/05_poetry.ipynb)

[05_poetry.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/05_poetry.ipynb) - verse statistics and phonostatistics on `PoetryCorpus` (16,694 poems of the 18th-20th centuries): the Onegin stanza through `VerseStats`, meters and the number of feet by era and by author, the stress profile of the iambic tetrameter against Taranovsky's manual counts, rhyme schemes and line endings, stressed vowels and alliteration, a check of stresses and rhymes on the RIFMA dataset.

## Running locally

``` bash
uv sync --group examples
uv run jupyter lab examples/
```

`make notebooks` executes all notebooks, writes the outputs into the files and strips the execution metadata; the `examples.yml` workflow runs the notebooks on a schedule and on demand.
