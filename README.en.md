<p align="center">
  <img src="https://raw.githubusercontent.com/SergeyShk/ruTS/master/docs/img/ruts.png" alt="ruTS" width="360">
</p>

<h1 align="center">ruTS</h1>

<p align="center">
  <b>Russian Texts Statistics</b> - a library for statistics extraction from texts in Russian
</p>

<p align="center">
  <a href="https://sergeyshk.github.io/ruTS/">Documentation</a> ·
  <a href="https://pypi.org/project/ruts/">PyPI</a> ·
  <a href="https://github.com/SergeyShk/ruTS/blob/master/README.md">Русский</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/ruts/"><img src="https://img.shields.io/pypi/v/ruTS?logo=pypi&logoColor=FFE873" alt="Version"></a>
  <a href="https://pypi.org/project/ruts/"><img src="https://img.shields.io/pypi/pyversions/ruts.svg?logo=python&logoColor=FFE873" alt="Supported Python versions"></a>
  <a href="https://github.com/SergeyShk/ruTS/actions/workflows/ci.yml"><img src="https://github.com/SergeyShk/ruTS/actions/workflows/ci.yml/badge.svg" alt="Build"></a>
  <a href="https://codecov.io/gh/SergeyShk/ruTS"><img src="https://codecov.io/gh/SergeyShk/ruTS/branch/master/graph/badge.svg" alt="Coverage"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="LICENSE.txt"><img src="https://img.shields.io/github/license/sergeyshk/ruts.svg" alt="License"></a>
  <img src="https://img.shields.io/pypi/dm/ruTS" alt="Downloads">
</p>

---

**ruTS** computes for Russian texts what usually requires assembling several separate tools: basic statistics, readability and lexical diversity metrics, morphological features. The main functions are based on the [textacy](https://github.com/chartbeat-labs/textacy) statistics adapted to the Russian language.

The library works both with raw strings and with `Doc` objects of [spaCy](https://github.com/explosion/spaCy) - every statistic is available both as a standalone class and as a spaCy pipeline component.

* **[Object extraction](https://sergeyshk.github.io/ruTS/extractors/words/)** - configurable word and sentence tokenizers
* **[Basic statistics](https://sergeyshk.github.io/ruTS/stats/basic_stats/)** - counts of words, sentences, syllables, punctuation marks and their distributions
* **[Readability metrics](https://sergeyshk.github.io/ruTS/stats/readability_stats/)** - Flesch-Kincaid, SMOG, LIX and others, with coefficients for Russian
* **[Lexical diversity metrics](https://sergeyshk.github.io/ruTS/stats/diversity_stats/)** - TTR and its variations, MTLD, HD-D, Simpson's and Yule's indices, entropy, Zipf's and Heaps' laws
* **[Morphological statistics](https://sergeyshk.github.io/ruTS/stats/morph_stats/)** - part of speech, case, mood, transitivity and other features
* **[Datasets](https://sergeyshk.github.io/ruTS/datasets/sovchlit/)** - ready-to-use preprocessed corpora with filtering
* **[Visualization](https://sergeyshk.github.io/ruTS/visualizers/zipf/)** - Zipf's law, Literature Fingerprinting, Word Tree
* **[spaCy components](https://sergeyshk.github.io/ruTS/components/)** - plug any statistic into a pipeline

## Installation

Requires Python 3.11 or newer.

```bash
pip install ruts
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add ruts
```

Working with spaCy components requires the Russian-language model:

```bash
python -m spacy download ru_core_news_sm
```

## Quick start

```python
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
 'n_punctuations': 2}

>>> ReadabilityStats(text).flesch_reading_easy
74.93500000000003

>>> DiversityStats(text).ttr
0.8888888888888888
```

## Features

### Object extraction

The library allows creating your own tools for sentence and word extraction from a text, which can be further employed for counting statistics.

```python
>>> import re
>>> from nltk.corpus import stopwords
>>> from ruts import SentsExtractor, WordsExtractor

>>> text = "Не имей 100 рублей, а имей 100 друзей"

>>> se = SentsExtractor(tokenizer=re.compile(r', '))
>>> se.extract(text)
('Не имей 100 рублей', 'а имей 100 друзей')

>>> we = WordsExtractor(use_lexemes=True, stopwords=stopwords.words('russian'), filter_nums=True, ngram_range=(1, 2))
>>> we.extract(text)
('иметь', 'рубль', 'иметь', 'друг', 'иметь_рубль', 'рубль_иметь', 'иметь_друг')

>>> we.get_most_common(3)
[('иметь', 2), ('рубль', 1), ('друг', 1)]
```

See the docs for [words](https://sergeyshk.github.io/ruTS/extractors/words/) and [sentences](https://sergeyshk.github.io/ruTS/extractors/sentences/).

<details>
<summary><b>Basic statistics</b></summary>

<br>

The library allows extracting the following statistics from a text:

*   the number of sentences
*   the number of words
*   the number of unique words
*   the number of long words
*   the number of complex words
*   the number of simple words
*   the number of monosyllable words
*   the number of polysyllable words
*   the number of characters
*   the number of letters
*   the number of spaces
*   the number of syllables
*   the number of punctuation marks
*   the distribution of words by the number of letters
*   the distribution of words by the number of syllables

Any statistic can be printed in a readable form:

```python
>>> from ruts import BasicStats

>>> text = "Существуют три вида лжи: ложь, наглая ложь и статистика"
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

More in the [documentation](https://sergeyshk.github.io/ruTS/stats/basic_stats/).

</details>

<details>
<summary><b>Readability metrics</b></summary>

<br>

The library allows counting the following readability metrics:

*   Flesch Reading Ease
*   Flesch-Kincaid Grade Level
*   Coleman-Liau Index
*   SMOG Index
*   Automated Readability Index
*   LIX readability measure
*   RIX readability measure
*   Solovyev-Ivanov-Solnyshkina formula
*   Matskovsky formula
*   Dale-Chall Index
*   Gunning Fog Index

An interpretation layer works on top of the formulas: a consensus grade as the median of the grade formulas, mapping of the grade to the reader's age by the plainrussian table, and reading time.

Coefficients of the formulas adapted for Russian are selected by the `preset` argument: by default the library uses the coefficients of the [Plain Russian Language](https://github.com/infoculture/plainrussian) project obtained on texts with grade labels (`plainrussian`); Oborneva's coefficients for fiction (`fiction`) and the Kazan group's (Solovyev, Ivanov, Solnyshkina) coefficients for academic texts (`academic`) are also available.

```python
>>> from pprint import pprint
>>> from ruts import ReadabilityStats

>>> text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
>>> rs = ReadabilityStats(text)

>>> pprint(rs.get_stats())
{'automated_readability_index': 0.2941666666666656,
 'coleman_liau_index': 1.1700000000000053,
 'consensus_grade': 1.5,
 'dale_chall_index': 4.095000000000001,
 'flesch_kincaid_grade': -2.0633333333333326,
 'flesch_reading_easy': 87.16833333333334,
 'gunning_fog_index': 6.0,
 'lix': 28.333333333333336,
 'matskovsky_index': 9.351,
 'reading_time': 0.08333333333333333,
 'rix': 2.0,
 'sis_grade': 1.5166666666666675,
 'smog_index': 0.05}

>>> rs.print_stats()
                   Метрика                   | Значение
-------------------------------------------------------
Тест Флеша-Кинкайда                          |  -2.06
Индекс удобочитаемости Флеша                 |  87.17
Индекс Колман-Лиау                           |   1.17
Индекс SMOG                                  |   0.05
Автоматический индекс удобочитаемости        |   0.29
Индекс удобочитаемости LIX                   |  28.33
Индекс удобочитаемости RIX                   |   2.00
Формула Соловьёва, Иванова, Солнышкиной      |   1.52
Формула Мацковского                          |   9.35
Индекс Дейла-Чейла                           |   4.10
Индекс Ганнинга                              |   6.00
Сводный класс                                |   1.50
Время чтения (мин.)                          |   0.08

>>> rs.describe_grade()
'1-3-й класс (6-8 лет)'
```

More in the [documentation](https://sergeyshk.github.io/ruTS/stats/readability_stats/).

</details>

<details>
<summary><b>Lexical diversity metrics</b></summary>

<br>

The library allows counting the following lexical diversity metrics for a text:

*   Type-Token Ratio (TTR)
*   Root Type-Token Ratio (RTTR)
*   Corrected Type-Token Ratio (CTTR)
*   Herdan Type-Token Ratio (HTTR)
*   Summer Type-Token Ratio (STTR)
*   Maas Type-Token Ratio (MTTR)
*   Dugast Type-Token Ratio (DTTR)
*   Moving Average Type-Token Ratio (MATTR)
*   Mean Segmental Type-Token Ratio (MSTTR)
*   Measure of Textual Lexical Diversity (MTLD)
*   Moving Average Measure of Textual Lexical Diversity (MA-MTLD)
*   MTLD with a moving window and wrap-around (MTLD-W)
*   Hypergeometric Distribution D (HD-D)
*   Simpson's Diversity Index (D), Inverse Simpson Index (1/D) and Gini-Simpson Index (1-D)
*   Hapax Legomena Index (Honoré's R), hapax ratio, Baayen's P and α₂
*   Yule's K and I, Herdan's Vm, Sichel's S, Michéa's M, Brunet's W and Dugast's k
*   Shannon entropy, evenness and perplexity
*   Zipf's law slope (α) and Heaps' law exponent (β)

Windows, thresholds and the logarithm base are parameters of `DiversityStats`; any measure can be computed over windows with a confidence interval via the `windowed` method. Some of the implementations were borrowed from the [lexical_diversity](https://github.com/kristopherkyle/lexical_diversity) project, the frequency-spectrum measures were checked against Tweedie and Baayen (1998), zipfR and quanteda.

```python
>>> from pprint import pprint
>>> from ruts import DiversityStats

>>> text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"

>>> pprint(DiversityStats(text).get_stats())
{'alpha2': 0.5,
 'baayen_p': 0.5333333333333333,
 'brunet_w': 6.00637847898991,
 'cttr': 2.008316044185609,
 'dttr': 10.268784661968118,
 'dugast_k': 14.783895126869226,
 'entropy': 3.3232314287976203,
 'evenness': 0.9606293157795304,
 'gini_simpson_index': 0.9523809523809523,
 'hapax_index': 992.9517404041437,
 'hapax_ratio': 0.7272727272727273,
 'hdd': nan,
 'heaps_beta': 0.8366147342060046,
 'herdan_vm': 0.1421338109037403,
 'httr': 0.8854692840710255,
 'inverse_simpson_index': 21.0,
 'mamtld': 12.0,
 'mattr': 0.7333333333333333,
 'michea_m': 5.5,
 'msttr': 0.7333333333333333,
 'mtld': 15.0,
 'mtldw': 13.25,
 'mttr': 0.09738250756232528,
 'perplexity': 10.009038104159247,
 'rttr': 2.840187787218772,
 'sichel_s': 0.18181818181818182,
 'simpson_index': 0.047619047619047616,
 'sttr': 0.2500605793160848,
 'ttr': 0.7333333333333333,
 'yule_i': 8.642857142857142,
 'yule_k': 444.44444444444446,
 'zipf_alpha': 0.4884512334695912}

>>> DiversityStats(text).windowed("ttr", window_len=5)
WindowStats(mean=0.9333333333333332, std=0.11547005383792512, lower=0.6464898180167025, upper=1.220176848649964, n_windows=3)
```

More in the [documentation](https://sergeyshk.github.io/ruTS/stats/diversity_stats/).

</details>

<details>
<summary><b>Morphological statistics</b></summary>

<br>

The library allows extracting the following morphological features:

*   part of speech
*   animacy
*   aspect
*   case
*   gender
*   involvement
*   mood
*   number
*   person
*   tense
*   transitivity
*   voice

Morphological analysis is made using [pymorphy3](https://github.com/no-plagiarism/pymorphy3). Descriptions of morphological features were borrowed from [OpenCorpora](http://opencorpora.org/dict.php?act=gram).

```python
>>> from pprint import pprint
>>> from ruts import MorphStats

>>> text = "Постарайтесь получить то, что любите, иначе придется полюбить то, что получили"
>>> ms = MorphStats(text)

>>> ms.pos
('VERB', 'INFN', 'CONJ', 'CONJ', 'VERB', 'ADVB', 'VERB', 'INFN', 'CONJ', 'CONJ', 'VERB')

>>> pprint(ms.get_stats())
{'animacy': {None: 11},
 'aspect': {None: 5, 'impf': 1, 'perf': 5},
 'case': {None: 11},
 'gender': {None: 11},
 'involvement': {None: 10, 'excl': 1},
 'mood': {None: 7, 'impr': 1, 'indc': 3},
 'number': {None: 7, 'plur': 3, 'sing': 1},
 'person': {None: 9, '2per': 1, '3per': 1},
 'pos': {'ADVB': 1, 'CONJ': 4, 'INFN': 2, 'VERB': 4},
 'tense': {None: 8, 'futr': 1, 'past': 1, 'pres': 1},
 'transitivity': {None: 5, 'intr': 2, 'tran': 4},
 'voice': {None: 11}}

>>> ms.print_stats('pos', 'tense')
---------------Часть речи---------------
Глагол (личная форма)         |    4
Союз                          |    4
Глагол (инфинитив)            |    2
Наречие                       |    1

-----------------Время------------------
Неизвестно                    |    8
Настоящее                     |    1
Будущее                       |    1
Прошедшее                     |    1
```

Individual words can be analysed with decoded features via `ms.explain_text(filter_none=True)`.

More in the [documentation](https://sergeyshk.github.io/ruTS/stats/morph_stats/).

</details>

<details>
<summary><b>Datasets</b></summary>

<br>

The library allows working with a number of preprocessed datasets:

*   [sov_chrest_lit](https://sergeyshk.github.io/ruTS/datasets/sovchlit/) - soviet reading-books for literature classes
*   [stalin_works](https://sergeyshk.github.io/ruTS/datasets/stalinworks/) - the collected works of Stalin

One can work solely with texts (without title info) or texts with metadata. There is also an opportunity to filter texts on different criteria.

```python
>>> from pprint import pprint
>>> from ruts.datasets import SovChLit

>>> sc = SovChLit()
>>> sc.info
{'Наименование': 'sov_chrest_lit',
 'url': 'https://dataverse.harvard.edu/file.xhtml?fileId=3670902&version=DRAFT',
 'description': 'Корпус советских хрестоматий по литературе',
 'author': 'Шкарин С.С.'}

>>> for record in sc.get_records(max_len=100, category='Весна', limit=1):
...     pprint(record)
{'author': 'Е. Трутнева',
 'book': 'Родная речь. Книга для чтения в I классе начальной школы',
 'category': 'Весна',
 'file': PosixPath('.../ruts_data/texts/sov_chrest_lit/grade_1/155'),
 'grade': 1,
 'subject': 'Дождик',
 'text': 'Дождик, дождик, поливай, будет хлеба каравай!\n'
         'Дождик, дождик, припусти, дай гороху подрасти!',
 'type': 'Стихотворение',
 'year': 1963}
```

A dataset is downloaded on first access and cached locally.

</details>

<details>
<summary><b>Visualization</b></summary>

<br>

The library allows visualizing text with the help of the following graphs:

*   [Zipf's law](https://sergeyshk.github.io/ruTS/visualizers/zipf/)
*   [Literature Fingerprinting](https://sergeyshk.github.io/ruTS/visualizers/fingerprinting/)
*   [Word Tree](https://sergeyshk.github.io/ruTS/visualizers/word_tree/)

```python
>>> from collections import Counter
>>> from nltk.corpus import stopwords
>>> from ruts import WordsExtractor
>>> from ruts.datasets import SovChLit
>>> from ruts.visualizers import zipf

>>> sc = SovChLit()
>>> text = "\n".join(text for text in sc.get_texts(limit=100))
>>> we = WordsExtractor(use_lexemes=True, stopwords=stopwords.words("russian"), filter_nums=True)
>>> tokens_with_count = Counter(we.extract(text))
>>> zipf(tokens_with_count, num_words=100, num_labels=10, log=False, show_theory=True, alpha=1.1)
```

<p align="center">
  <img src="https://raw.githubusercontent.com/SergeyShk/ruTS/master/docs/img/zipf.png" alt="Zipf's law" width="520">
</p>

</details>

<details>
<summary><b>spaCy components</b></summary>

<br>

The library allows creating the following classes of spaCy components:

*   `BasicStats`
*   `DiversityStats`
*   `MorphStats`
*   `ReadabilityStats`

```python
>>> import ruts
>>> import spacy

>>> nlp = spacy.load('ru_core_news_sm')
>>> nlp.add_pipe('basic', last=True)

>>> doc = nlp("Существуют три вида лжи: ложь, наглая ложь и статистика")
>>> doc._.basic.c_letters
{1: 3, 3: 2, 4: 3, 6: 1, 10: 2}

>>> doc._.basic.n_words
11
```

The values differ from the example above: spaCy emits punctuation marks as separate tokens, and they are counted as words.

More in the [documentation](https://sergeyshk.github.io/ruTS/components/).

</details>

## Development

The project uses [uv](https://docs.astral.sh/uv/) for dependency management and [ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
git clone https://github.com/SergeyShk/ruTS.git
cd ruTS

make deps        # create the environment and install dependencies
make nltk-data   # download the NLTK data required by the tests
make test        # run the tests
make lint        # ruff + mypy
```

Run `make help` for the full list of commands.

Before submitting changes, install the hooks that run the linters on commit and the tests on push:

```bash
uv run pre-commit install
```

## Contributing

Bug reports, ideas and pull requests are welcome - [issues](https://github.com/SergeyShk/ruTS/issues) are open. Before submitting a pull request, please make sure that `make lint` and `make test` pass.

<details>
<summary><b>Project structure</b></summary>

<br>

*   **docs** - project documentation
*   **ruts**:
    *   basic_stats.py - basic text statistics
    *   components.py - spaCy components
    *   constants.py - main constants
    *   diversity_stats.py - lexical diversity metrics
    *   extractors.py - tools for object extraction from a text
    *   morph_stats.py - morphological statistics
    *   readability_stats.py - readability metrics
    *   utils.py - helper tools
    *   **datasets** - datasets:
        *   dataset.py - base class for working with datasets
        *   sov_chrest_lit.py - soviet reading-books for literature classes
        *   stalin_works.py - the collected works of Stalin
    *   **visualizers** - tools for text visualization:
        *   fingerprinting.py - Literature Fingerprinting
        *   word_tree.py - Word Tree
        *   zipf.py - Zipf's law
*   **tests** - tests mirroring the package structure

</details>

## Authors

*   Sergey Shkarin (kouki.sergey@gmail.com)
*   Ekaterina Smirnova (ekanerina@yandex.ru)

## License

[MIT](LICENSE.txt)

## Citation

Please use the following BibTeX entry for citing **ruTS** if you use it in your research or software. Citations are helpful for the continued development and maintenance of this library.

```bibtex
@software{ruTS,
  author = {Sergey Shkarin},
  title = {{ruTS, a library for statistics extraction from texts in Russian}},
  year = 2026,
  publisher = {Moscow},
  url = {https://github.com/SergeyShk/ruTS}
}
```
