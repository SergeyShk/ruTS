# Russian Texts Statistics (ruTS) [![README_RU](https://raw.githubusercontent.com/gosquared/flags/master/flags/flags/flat/24/Russia.png)](https://github.com/SergeyShk/ruTS/blob/master/README.md) ![README_EN](https://raw.githubusercontent.com/gosquared/flags/master/flags/flags/flat/24/United-Kingdom.png)

![Version](https://img.shields.io/pypi/v/ruTS?logo=pypi&logoColor=FFE873)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/ruts.svg?logo=python&logoColor=FFE873)](https://pypi.org/project/ruts/)
![Downloads](https://img.shields.io/pypi/dm/ruTS)
[![Build Status](https://travis-ci.com/SergeyShk/ruTS.svg?branch=master)](https://travis-ci.com/SergeyShk/ruTS)
[![codecov](https://codecov.io/gh/SergeyShk/ruTS/branch/master/graph/badge.svg)](https://codecov.io/gh/SergeyShk/ruTS)
![Status](https://img.shields.io/pypi/status/ruts)
[![License](https://img.shields.io/github/license/sergeyshk/ruts.svg)](LICENSE.txt)
![Repo size](https://img.shields.io/github/repo-size/SergeyShk/ruTS)
![Codacy grade](https://img.shields.io/codacy/grade/5e1cef0e2fa64bdc835f7bfcb7996edc.svg?logo=codacy)

<p align="center"> 
<img src="https://clipartart.com/images/free-tree-roots-clipart-black-and-white-2.png">
</p>

Library for statistics extraction from texts in Russian.

## Installation

Run the following command:

```bash
$ pip install ruts
```

Dependencies:

*   python 3.8+
*   nltk
*   pymorphy2
*   razdel
*   scipy
*   spaCy
*   numpy
*   pandas
*   matplotlib
*   graphviz

## Usage

The main functions are based on the [textacy](https://github.com/chartbeat-labs/textacy) statistics adapted to Russian language. The library allows working both with raw texts and Doc-objects of the [spaCy](https://github.com/explosion/spaCy) library.

[API](https://ruts-api.herokuapp.com/docs) to explore the available functions.

### Object extraction

The library allows creating your own tools for sentence and word extraction from a text, which can be further employed for counting statistics.

Example:

```python
import re
from nltk.corpus import stopwords
from ruts import SentsExtractor, WordsExtractor
text = "Не имей 100 рублей, а имей 100 друзей"
se = SentsExtractor(tokenizer=re.compile(r', '))
se.extract(text)

    ('Не имей 100 рублей', 'а имей 100 друзей')

we = WordsExtractor(use_lexemes=True, stopwords=stopwords.words('russian'), filter_nums=True, ngram_range=(1, 2))
we.extract(text)

    ('иметь', 'рубль', 'иметь', 'друг', 'иметь_рубль', 'рубль_иметь', 'иметь_друг')
   
we.get_most_common(3)

    [('иметь', 2), ('рубль', 1), ('друг', 1)]
```

### Basic statistics

The library allows extracting the following statistics from a text:

*   the number of sentences
*   the number of words
*   the number of unique words
*   the number of long words
*   the number of complex words
*   the number of simple words
*   the number of monosyllabic words
*   the number of polysyllabic words
*   the number of symbols
*   the number of letters
*   the number of spaces
*   the number of syllables
*   the number of punctuation marks
*   word distribution by the number of letters
*   word distribution by the number of syllables

Example:

```python
from ruts import BasicStats
text = "Существуют три вида лжи: ложь, наглая ложь и статистика"
bs = BasicStats(text)
bs.get_stats()

    {'c_letters': {1: 1, 3: 2, 4: 3, 6: 1, 10: 2},
    'c_syllables': {1: 5, 2: 1, 3: 1, 4: 2},
    'n_chars': 55,
    'n_complex_words': 2,
    'n_letters': 45,
    'n_long_words': 3,
    'n_monosyllable_words': 5,
    'n_polysyllable_words': 4,
    'n_punctuations': 2,
    'n_sents': 1,
    'n_simple_words': 7,
    'n_spaces': 8,
    'n_syllables': 18,
    'n_unique_words': 8,
    'n_words': 9}

bs.print_stats()

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

### Readability metrics

The library allows counting the following readability metrics:

*   Flesch Reading Ease
*   Flesch-Kincaid Grade Level
*   Coleman-Liau Index
*   SMOG Index
*   Automated Readability Index
*   LIX readability measure

Coefficients for Russian language were borrowed from the [Plain Russian Language](https://github.com/infoculture/plainrussian) project dedicated to counting readability coefficients based on a special corpus of texts with age labels.

Example:

```python
from ruts import ReadabilityStats
text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
rs = ReadabilityStats(text)
rs.get_stats()

    {'automated_readability_index': 0.2941666666666656,
    'coleman_liau_index': 0.2941666666666656,
    'flesch_kincaid_grade': 3.4133333333333304,
    'flesch_reading_easy': 83.16166666666666,
    'lix': 48.333333333333336,
    'smog_index': 0.05}

rs.print_stats()

                    Метрика                 | Значение 
    --------------------------------------------------
    Тест Флеша-Кинкайда                     |   3.41   
    Индекс удобочитаемости Флеша            |  83.16   
    Индекс Колман-Лиау                      |   0.29   
    Индекс SMOG                             |   0.05   
    Автоматический индекс удобочитаемости   |   0.29   
    Индекс удобочитаемости LIX              |  48.33  
```

### Lexical diversity metrics

The library allows counting the following lexical diversity metrics for a text:

*   Type-Token Ratio (TTR)
*   Root Type-Token Ratio (RTTR)
*   Corrected Type-Token Ratio (CTTR)
*   Herdan Type-Token Ratio (HTTR)
*   Summer Type-Token Ratio (STTR)
*   Mass Type-Token Ratio (MTTR)
*   Dugast Type-Token Ratio (DTTR)
*   Moving Average Type-Token Ratio (MATTR)
*   Mean Segmental Type-Token Ratio (MSTTR)
*   Measure of Textual Lexical Diversity (MTLD)
*   Moving Average Measure of Textual Lexical Diversity (MAMTLD)
*   Hypergeometric Distribution D (HD-D)
*   Simpson's Diversity Index
*   Hapax Legomena Index

Some of the implementations were borrowed from the [lexical_diversity](https://github.com/kristopherkyle/lexical_diversity) project.

Example:

```python
from ruts import DiversityStats
text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
ds = DiversityStats(text)
ds.get_stats()

    {'ttr': 0.7333333333333333,
    'rttr': 2.840187787218772,
    'cttr': 2.008316044185609,
    'httr': 0.8854692840710253,
    'sttr': 0.2500605793160845,
    'mttr': 0.0973825075623254,
    'dttr': 10.268784661968104,
    'mattr': 0.7333333333333333,
    'msttr': 0.7333333333333333,
    'mtld': 15.0,
    'mamtld': 11.875,
    'hdd': -1,
    'simpson_index': 21.0,
    'hapax_index': 431.2334616537499}

ds.print_stats()

                              Метрика                           | Значение 
    ----------------------------------------------------------------------
    Type-Token Ratio (TTR)                                      |   0.92   
    Root Type-Token Ratio (RTTR)                                |   7.17   
    Corrected Type-Token Ratio (CTTR)                           |   5.07   
    Herdan Type-Token Ratio (HTTR)                              |   0.98   
    Summer Type-Token Ratio (STTR)                              |   0.96   
    Mass Type-Token Ratio (MTTR)                                |   0.01   
    Dugast Type-Token Ratio (DTTR)                              |  85.82   
    Moving Average Type-Token Ratio (MATTR)                     |   0.91   
    Mean Segmental Type-Token Ratio (MSTTR)                     |   0.94   
    Measure of Textual Lexical Diversity (MTLD)                 |  208.38  
    Moving Average Measure of Textual Lexical Diversity (MTLD)  |   1.00   
    Hypergeometric Distribution D (HD-D)                        |   0.94   
    Индекс Симпсона                                             |  305.00  
    Гапакс-индекс                                               | 2499.46  
```

### Morphological statistics

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

Morphological analysis is made using [pymorphy2](https://github.com/kmike/pymorphy2). Descriptions of morphological features were borrowed from [OpenCorpora](http://opencorpora.org/dict.php?act=gram).

Example:

```python
from ruts import MorphStats
text = "Постарайтесь получить то, что любите, иначе придется полюбить то, что получили"
ms = MorphStats(text)
ms.pos

    ('VERB', 'INFN', 'CONJ', 'CONJ', 'VERB', 'ADVB', 'VERB', 'INFN', 'CONJ', 'CONJ', 'VERB')

ms.get_stats()

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

ms.explain_text(filter_none=True)

    (('Постарайтесь',
        {'aspect': 'perf',
        'involvement': 'excl',
        'mood': 'impr',
        'number': 'plur',
        'pos': 'VERB',
        'transitivity': 'intr'}),
    ('получить', {'aspect': 'perf', 'pos': 'INFN', 'transitivity': 'tran'}),
    ('то', {'pos': 'CONJ'}),
    ('что', {'pos': 'CONJ'}),
    ('любите',
        {'aspect': 'impf',
        'mood': 'indc',
        'number': 'plur',
        'person': '2per',
        'pos': 'VERB',
        'tense': 'pres',
        'transitivity': 'tran'}),
    ('иначе', {'pos': 'ADVB'}),
    ('придется',
        {'aspect': 'perf',
        'mood': 'indc',
        'number': 'sing',
        'person': '3per',
        'pos': 'VERB',
        'tense': 'futr',
        'transitivity': 'intr'}),
    ('полюбить', {'aspect': 'perf', 'pos': 'INFN', 'transitivity': 'tran'}),
    ('то', {'pos': 'CONJ'}),
    ('что', {'pos': 'CONJ'}),
    ('получили',
        {'aspect': 'perf',
        'mood': 'indc',
        'number': 'plur',
        'pos': 'VERB',
        'tense': 'past',
        'transitivity': 'tran'}))

ms.print_stats('pos', 'tense')

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

### Datasets

Library allows working with a number of  preprocessed datasets:

*   sov_chrest_lit - soviet reading-books for literature classes
*   stalin_works - the collected works of Stalin

One can work solely with texts (without title info) or texts with metadata. There is also an opportunity to filter texts on different criteria.

Example:

```python
from ruts.datasets import SovChLit
sc = SovChLit()
sc.info

    {'description': 'Корпус советских хрестоматий по литературе',
    'url': 'https://dataverse.harvard.edu/file.xhtml?fileId=3670902&version=DRAFT',
    'Наименование': 'sov_chrest_lit'}

for i in sc.get_records(max_len=100, category='Весна', limit=1):
    pprint(i)

    {'author': 'Е. Трутнева',
    'book': 'Родная речь. Книга для чтения в I классе начальной школы',
    'category': 'Весна',
    'file': PosixPath('../ruTS/ruts_data/texts/sov_chrest_lit/grade_1/155'),
    'grade': 1,
    'subject': 'Дождик',
    'text': 'Дождик, дождик, поливай, будет хлеба каравай!\n'
            'Дождик, дождик, припусти, дай гороху подрасти!',
    'type': 'Стихотворение',
    'year': 1963}

for i in sc.get_texts(text_type='Басня', limit=1):
    pprint(i)

    ('— Соседка, слышала ль ты добрую молву? — вбежавши, крысе мышь сказала:\n'
    '— Ведь кошка, говорят, попалась в когти льву. Вот отдохнуть и нам пора '
    'настала!\n'
    '— Не радуйся, мой свет,— ей крыса говорит в ответ,— и не надейся '
    'по-пустому.\n'
    'Коль до когтей у них дойдёт, то, верно, льву не быть живому: сильнее кошки '
    'зверя нет.')
```

### Visualization

Library allows visualizing text with the help of the following graphs:

*   Zipf's law
*   Literature Fingerprinting
*   Word Tree

Example:

```python
from collections import Counter
from nltk.corpus import stopwords
from ruts import WordsExtractor
from ruts.datasets import SovChLit
from ruts.visualizers import zipf

sc = SovChLit()
text = '\n'.join([text for text in sc.get_texts(limit=100)])
we = WordsExtractor(use_lexemes=True, stopwords=stopwords.words('russian'), filter_nums=True)
tokens_with_count = Counter(we.extract(text))
zipf(tokens_with_count, num_words=100, num_labels=10, log=False, show_theory=True, alpha=1.1)
```

### Components

Library allows creating the following classes of spaCy components:

*   BasicStats
*   DiversityStats
*   MorphStats
*   ReadabilityStats

Russian-language spaCy model can be downloaded by running the command:

```bash
$ python -m spacy download ru_core_news_sm
```

Example:

```python
import ruts
import spacy
nlp = spacy.load('ru_core_news_sm')
nlp.add_pipe('basic', last=True)
doc = nlp("Существуют три вида лжи: ложь, наглая ложь и статистика")
doc._.basic.c_letters

    {1: 1, 3: 2, 4: 3, 6: 1, 10: 2}

doc._.basic.get_stats()

    {'c_letters': {1: 1, 3: 2, 4: 3, 6: 1, 10: 2},
    'c_syllables': {1: 5, 2: 1, 3: 1, 4: 2},
    'n_chars': 55,
    'n_complex_words': 2,
    'n_letters': 45,
    'n_long_words': 3,
    'n_monosyllable_words': 5,
    'n_polysyllable_words': 4,
    'n_punctuations': 2,
    'n_sents': 1,
    'n_simple_words': 7,
    'n_spaces': 8,
    'n_syllables': 18,
    'n_unique_words': 8,
    'n_words': 9}
```

## Project structure

*   **docs** - project documentation
*   **ruts**:
    *   basic_stats.py - basic text statistics
    *   components.py - spaCy components
    *   constants.py - main constants
    *   diversity_stats.py - lexical diversity metrics
    *   extractors.py - tools for object extraction from a text
    *   morph_stats.py - morphological statistics 
    *   readability_stats.py - readability metrics
    *   utils.py - subsidiary tools
    *   **datasets**:
        *   dataset.py - basic class for working with datasets
        *   sov_chrest_lit.py - soviet reading-books for literature classes
        *   stalin_works.py - the collected works of Stalin
    *   **visualizers** - tools for text visualization:
        *   fingerprinting.py - Literature Fingerprinting
        *   word_tree.py - Word Tree
        *   zipf.py - Zipf's law
*   **tests**:
    *   test_basic_stats.py - tests for basic text statistics
    *   test_components.py - tests for spaCy components
    *   test_diversity_stats.py - tests for lexical diversity metrics
    *   test_extractors.py - tests for object extraction tools
    *   test_morph_stats - tests for morphological statistics
    *   test_readability_stats.py - tests for readability metrics
    *   **datasets** - tests for datasets:
        *   test_dataset.py - tests for basic class for working with datasets
        *   test_sov_chrest_lit.py - tests for dataset soviet reading-books for literature classes
        *   test_stalin_works.py - tests for dataset the collected works of Stalin
    *   **visualizers** - tests for tools for text visualization:
        *   test_fingerprinting.py - tests for visualization Literature Fingerprinting
        *   test_word_tree.py - tests for visualization Word Tree
        *   test_zipf.py - tests for visualization Zipf's law

## Authors

*   Sergey Shkarin (kouki.sergey@gmail.com)
*   Ekaterina Smirnova (ekanerina@yandex.ru)

## Attribution

Please use the following BibTeX entry for citing **ruTS** if you use it in your research or software.
Citations are helpful for the continued development and maintenance of this library.

```
@software{ruTS,
  author = {Sergey Shkarin},
  title = {{ruTS, a library for statistics extraction from texts in Russian}},
  year = 2022,
  publisher = {Moscow},
  url = {https://github.com/SergeyShk/ruTS}
}
```