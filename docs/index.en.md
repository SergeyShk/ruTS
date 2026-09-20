# Russian Texts Statistics (ruTS)

![ruts](img/ruts.png)

**ruTS** computes for Russian texts what usually requires assembling several separate tools: from basic statistics, readability and lexical diversity to morphology, syntax, cohesion, stylometry and corpus measures - by published formulas adapted to the Russian language.

The library works both with raw strings and with `Doc` objects of [spaCy](https://github.com/explosion/spaCy) - every statistic is available both as a standalone class and as a spaCy pipeline component.

Try it without installing in the [demo on Hugging Face Spaces](https://huggingface.co/spaces/SergeyShk/ruTS): paste a text and get the readability grade, metrics, plots and highlighted fragments.

## Features

*   build tokenizers for [words](extractors/words.md), [sentences](extractors/sentences.md) and [character N-grams](extractors/char_ngrams.md)
*   compute [basic text statistics](stats/basic_stats.md) (numbers of words, sentences, punctuation marks, syllables, etc.)
*   compute [readability metrics](stats/readability_stats.md) (Flesch-Kincaid test, SMOG index, LIX readability index, etc.)
*   compute [lexical diversity metrics](stats/diversity_stats.md) (Type-Token Ratio, Measure of Textual Lexical Diversity, hapax index, etc.)
*   extract [morphological features](stats/morph_stats.md) in Universal Dependencies terms (part of speech, case, mood, transitivity, etc.)
*   compute [SEO style metrics](stats/style_stats.md) (nausea, water content, spam score, naturalness by Zipf's law, keyword density)
*   compute [phonostatistics](stats/phon_stats.md) (shares of sound classes, consonant clusters, alliteration and assonance, syllables)
*   compute [syntactic statistics](stats/syntax_stats.md) over the spaCy dependency tree (dependency distances, tree depth, coordination chains, clauses, participial clauses, passive voice, genitive chains)
*   compute [cohesion statistics](stats/cohesion_stats.md) (noun, argument and content word overlap between sentences, givenness, temporal cohesion, connectives by class)
*   compute [lexical sophistication statistics](stats/lexical_stats.md) (word frequency by the Lyashevskaya-Sharoff dictionary, frequency bands, surprisal, lexical density)
*   compute [verse statistics](stats/verse_stats.md) (stresses by the Koziev dictionary, meter and number of feet, pyrrhics and stress profile, rhyme schemes, line endings and stanzas)
*   compute corpus measures ([keywords](corpus/keyness.md) relative to a reference corpus or a frequency dictionary, [collocations](corpus/collocations.md), [word dispersion](corpus/dispersion.md) across text parts, [KWIC concordance](corpus/kwic.md)) and [stylometry](corpus/stylometry.md) measures (Burrows's Delta with its variants, Zeta, Kilgarriff's chi-square, Mendenhall curve, function word profile), [compare corpora](corpus/compare.md) across all features at once (Mann-Whitney test, Cohen's d, Cliff's delta, bootstrap intervals, AUC)
*   work with ready-to-use text datasets ([Soviet literature readers](datasets/sovchlit.md), [Collected works of Stalin](datasets/stalinworks.md), [Texts with grade labels](datasets/textsbygrade.md), [Lyashevskaya and Sharoff frequency dictionary](datasets/freq2011.md), [Russian poetry corpus](datasets/poetrycorpus.md), [Russian classical literature](datasets/russianliterature.md), [Koziev stress dictionary](datasets/stressdict.md))
*   visualize text data ([Zipf's law](visualizers/zipf.md), [Literature Fingerprinting](visualizers/fingerprinting.md), [Word Tree](visualizers/word_tree.md), [text highlighting](visualizers/highlight.md), [corpus](visualizers/corpus.md) and [stylometric](visualizers/stylometry.md) plots, [vocabulary growth and frequency spectrum](visualizers/vocabulary.md), [sentence lengths](visualizers/sentences.md))
*   build [components](components.md) to plug into [spaCy](https://github.com/explosion/spaCy)

## Installation

Requires Python 3.11 or newer.

``` bash
pip install ruts
```

More on dependencies and installing from the repository - on the [Installation](installation.md) page.

## Quick start

``` python
>>> from ruts import BasicStats, DiversityStats, ReadabilityStats

>>> text = "Существуют три вида лжи: ложь, наглая ложь и статистика"

>>> BasicStats(text).get_stats()
{'c_letters': {1: 1, 3: 2, 4: 3, 6: 1, 10: 2},
 'c_syllables': {1: 5, 2: 1, 3: 1, 4: 2},
 'n_sents': 1,
 'n_words': 9,
 'n_unique_words': 8,
 'n_long_words': 3,
 'n_complex_words': 2,
 'n_simple_words': 7,
 'n_monosyllable_words': 5,
 'n_polysyllable_words': 4,
 'n_chars': 55,
 'n_letters': 45,
 'n_spaces': 8,
 'n_syllables': 18,
 'n_punctuations': 2,
 'c_punctuations': {'comma': 1, 'period': 0, 'question': 0, 'exclamation': 0,
                    'ellipsis': 0, 'colon': 1, 'semicolon': 0, 'dash': 0,
                    'hyphen': 0, 'angle_quotes': 0, 'straight_quotes': 0,
                    'parentheses': 0, 'other': 0}}

>>> ReadabilityStats(text).flesch_reading_easy
74.93500000000003

>>> DiversityStats(text).ttr
0.8888888888888888
```

Any statistic can be printed in a readable form:

``` python
>>> BasicStats(text).print_stats()
     Статистика     | Значение
------------------------------
Предложения         |    1
Слова               |    9
Уникальные слова    |    8
Длинные слова       |    3
Сложные слова       |    2
Простые слова       |    7
Односложные слова   |    5
Многосложные слова  |    4
Символы             |    55
Буквы               |    45
Пробелы             |    8
Слоги               |    18
Знаки препинания    |    2
```

A walkthrough of one short story with every tool of the library is in the notebook [examples/01_text_walkthrough.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb), which opens in [Colab](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb); the other notebooks are on the [examples](examples.md) page.

??? note "Project structure"

    *   **docs** - project documentation
    *   **ruts**:
        *   basic_stats.py - basic text statistics
        *   cohesion_stats.py - cohesion statistics
        *   components.py - spaCy components
        *   constants.py - main constants
        *   diversity_stats.py - lexical diversity metrics
        *   exceptions.py - library exceptions
        *   extractors.py - tools for object extraction from a text
        *   lexical_stats.py - lexical sophistication statistics
        *   morph_stats.py - morphological statistics
        *   phon_stats.py - phonostatistics
        *   readability_stats.py - readability metrics
        *   style_stats.py - SEO style metrics
        *   syntax_stats.py - syntactic statistics
        *   utils.py - helper tools
        *   verse_stats.py - verse statistics: stresses, meter, rhyme, stanzas
        *   **corpus** - corpus measures:
            *   collocations.py - collocations and association measures
            *   compare.py - corpus comparison by text features
            *   dispersion.py - word dispersion across text parts
            *   keyness.py - keywords relative to a reference corpus
            *   kwic.py - KWIC concordance
            *   stylometry.py - Burrows's Delta, Zeta and other stylometry measures
        *   **datasets** - datasets:
            *   dataset.py - base class for working with datasets
            *   freq2011.py - the Lyashevskaya-Sharoff frequency dictionary
            *   poetry_corpus.py - Ilya Gusev's PoetryCorpus
            *   russian_literature.py - the RusLit collection of Russian classics
            *   sov_chrest_lit.py - soviet reading-books for literature classes
            *   stalin_works.py - the collected works of Stalin
            *   stress_dict.py - the Koziev stress dictionary
            *   texts_by_grade.py - texts with grade labels from the Plain Russian Language project
        *   **resources** - embedded lexical resources (the most frequent lemmas list, the connectives dictionary)
        *   **visualizers** - tools for text visualization:
            *   corpus.py - lexical dispersion, keyness chart, collocation network
            *   fingerprinting.py - Literature Fingerprinting
            *   highlight.py - text highlighting
            *   sentences.py - sentence lengths
            *   stylometry.py - dendrogram, principal components, scaling, Mendenhall curves
            *   vocabulary.py - Heaps's law and frequency spectrum
            *   word_tree.py - Word Tree
            *   zipf.py - Zipf's law
    *   **tests** - tests mirroring the package structure
    *   **examples** - example notebooks
    *   **demo** - Gradio demo for Hugging Face Spaces
