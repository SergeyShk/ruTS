<p align="center">
  <img src="https://raw.githubusercontent.com/SergeyShk/ruTS/master/docs/img/ruts.png" alt="ruTS" width="360">
</p>

<h1 align="center">ruTS</h1>

<p align="center">
  <b>Russian Texts Statistics</b> - a library for statistics extraction from texts in Russian
</p>

<p align="center">
  <a href="https://sergeyshk.github.io/ruTS/">Documentation</a> ·
  <a href="https://huggingface.co/spaces/SergeyShk/ruTS">Demo</a> ·
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
  <a href="https://huggingface.co/spaces/SergeyShk/ruTS"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Spaces-demo-blue" alt="Demo on Hugging Face Spaces"></a>
</p>

---

**ruTS** computes for Russian texts what usually requires assembling several separate tools: basic statistics, readability and lexical diversity metrics, morphological features. The main functions are based on the [textacy](https://github.com/chartbeat-labs/textacy) statistics adapted to the Russian language.

The library works both with raw strings and with `Doc` objects of [spaCy](https://github.com/explosion/spaCy) - every statistic is available both as a standalone class and as a spaCy pipeline component.

Try it without installing in the [demo on Hugging Face Spaces](https://huggingface.co/spaces/SergeyShk/ruTS): paste a text and get the readability grade, metrics, plots and highlighted fragments.

* **[Object extraction](https://sergeyshk.github.io/ruTS/extractors/words/)** - configurable word and sentence tokenizers
* **[Basic statistics](https://sergeyshk.github.io/ruTS/stats/basic_stats/)** - counts of words, sentences, syllables, punctuation marks and their distributions
* **[Readability metrics](https://sergeyshk.github.io/ruTS/stats/readability_stats/)** - Flesch-Kincaid, SMOG, LIX and others, with coefficients for Russian
* **[Lexical diversity metrics](https://sergeyshk.github.io/ruTS/stats/diversity_stats/)** - TTR and its variations, MTLD, HD-D, Simpson's and Yule's indices, entropy, Zipf's and Heaps' laws
* **[Morphological statistics](https://sergeyshk.github.io/ruTS/stats/morph_stats/)** - part of speech, case, mood, transitivity and other features in Universal Dependencies terms
* **[SEO style metrics](https://sergeyshk.github.io/ruTS/stats/style_stats/)** - nausea, water content, spam score, naturalness by Zipf's law, keyword density, lexical officialese markers
* **[Phonostatistics](https://sergeyshk.github.io/ruTS/stats/phon_stats/)** - sound classes, clusters, alliteration and assonance, syllables by the rising sonority rule
* **[Syntactic statistics](https://sergeyshk.github.io/ruTS/stats/syntax_stats/)** - dependency distances, tree depth, coordination chains, clauses, participial clauses, passive voice, genitive chains, split predicates and other officialese markers over the spaCy parse
* **[Cohesion statistics](https://sergeyshk.github.io/ruTS/stats/cohesion_stats/)** - noun, argument and content word overlap between sentences, givenness, temporal cohesion, connectives by class
* **[Lexical sophistication statistics](https://sergeyshk.github.io/ruTS/stats/lexical_stats/)** - word frequency by the Lyashevskaya-Sharoff dictionary, frequency bands, surprisal, lexical density
* **[Corpus measures](https://sergeyshk.github.io/ruTS/corpus/keyness/)** - keywords relative to a reference corpus or frequency dictionary, collocations, word dispersion, KWIC concordance
* **[Datasets](https://sergeyshk.github.io/ruTS/datasets/sovchlit/)** - ready-to-use preprocessed corpora with filtering
* **[Visualization](https://sergeyshk.github.io/ruTS/visualizers/zipf/)** - Zipf's law, Literature Fingerprinting, Word Tree, text highlighting by readability and style layers
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

Working with spaCy components and syntactic statistics requires the Russian-language model:

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
*   verb form
*   voice

Values follow [Universal Dependencies](https://universaldependencies.org/u/feat/): for a spaCy `Doc` with annotations they come from `token.pos_` and `token.morph`, context included; for a string, from the first [pymorphy3](https://github.com/no-plagiarism/pymorphy3) parse with OpenCorpora grammemes mapped to UD.

```python
>>> from pprint import pprint
>>> from ruts import MorphStats

>>> text = "Постарайтесь получить то, что любите, иначе придется полюбить то, что получили"
>>> ms = MorphStats(text)

>>> ms.pos
('VERB', 'VERB', 'CCONJ', 'SCONJ', 'VERB', 'ADV', 'VERB', 'VERB', 'CCONJ', 'SCONJ', 'VERB')

>>> pprint(ms.get_stats())
{'animacy': {None: 11},
 'aspect': {None: 5, 'Imp': 1, 'Perf': 5},
 'case': {None: 11},
 'gender': {None: 11},
 'involvement': {None: 10, 'Ex': 1},
 'mood': {None: 7, 'Imp': 1, 'Ind': 3},
 'number': {None: 7, 'Plur': 3, 'Sing': 1},
 'person': {None: 9, '2': 1, '3': 1},
 'pos': {'ADV': 1, 'CCONJ': 2, 'SCONJ': 2, 'VERB': 6},
 'tense': {None: 8, 'Fut': 1, 'Past': 1, 'Pres': 1},
 'transitivity': {None: 5, 'Intr': 2, 'Tran': 4},
 'verb_form': {None: 5, 'Fin': 4, 'Inf': 2},
 'voice': {None: 11}}

>>> ms.print_stats('pos', 'tense')
---------------Часть речи---------------
Глагол                        |    6
Сочинительный союз            |    2
Подчинительный союз           |    2
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
<summary><b>SEO style metrics</b></summary>

<br>

The library reproduces the indicators of the [Advego](https://advego.com/text/seo/) and [Text.ru](https://text.ru/seo) services:

*   Classic and academic nausea
*   Water content
*   Spam score
*   Naturalness by Zipf's law
*   Keyword and phrase density
*   Lexical officialese markers: verbal nouns, compound prepositions, parentheticals, clichés

The exact formulas of the services are not published, so the commonly accepted definitions are implemented; stop words for water content are detected by part of speech with pymorphy3 or passed as a list.

```python
>>> from pprint import pprint
>>> from ruts import StyleStats

>>> text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
>>> ss = StyleStats(text)

>>> pprint(ss.get_stats())
{'academic_nausea': 93.33333333333333,
 'classic_nausea': 1.7320508075688772,
 'cliches': 0.0,
 'compound_prepositions': 0.0,
 'parentheticals': 0.0,
 'spam': 26.666666666666668,
 'verbal_nouns': 0.0,
 'water': 46.666666666666664,
 'zipf_naturalness': 33.333333333333336}

>>> ss.keyword_density("когда", "нет а")
{'когда': 20.0, 'нет а': 13.333333333333334}

>>> ss = StyleStats("В целях повышения качества в кратчайшие сроки, как правило, проводится проверка")
>>> ss.verbal_nouns, ss.compound_prepositions, ss.parentheticals, ss.cliches
(16.666666666666664, 9.090909090909092, 9.090909090909092, 9.090909090909092)
```

More in the [documentation](https://sergeyshk.github.io/ruTS/stats/style_stats/).

</details>

<details>
<summary><b>Phonostatistics</b></summary>

<br>

The library counts by letters, without devoicing or stress:

*   Shares of vowels, sonorants, voiced and voiceless consonants, consonant-to-vowel ratio
*   Consonant clusters and vowel hiatus
*   Entropy of word CV patterns and "hardness"
*   Alliteration and assonance indices relative to expected repetitions
*   Syllables by the rising sonority rule: share of open syllables, mean syllable length, CV patterns

```python
>>> from pprint import pprint
>>> from ruts import PhonStats
>>> from ruts.phon_stats import syllabify

>>> text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
>>> ps = PhonStats(text)

>>> pprint(ps.get_stats())
{'alliteration': 0.9149440867502556,
 'assonance': 0.802520508857449,
 'consonant_vowel_ratio': 1.48,
 'cv_entropy': 3.1395722619867223,
 'hardness': 0.5625,
 'mean_syllable_len': 2.6,
 'p_heavy_clusters': 0.034482758620689655,
 'p_hiatus': 0.0,
 'p_open_syllables': 0.76,
 'p_sonorants': 0.11290322580645161,
 'p_voiced': 0.1935483870967742,
 'p_voiceless': 0.2903225806451613,
 'p_vowels': 0.4032258064516129}

>>> syllabify("здравствуйте")
['здра', 'вствуй', 'те']
```

More in the [documentation](https://sergeyshk.github.io/ruTS/stats/phon_stats/).

</details>

<details>
<summary><b>Syntactic statistics</b></summary>

<br>

The library counts over the spaCy dependency tree (a model with a parser is required):

*   Dependency distances, tree depth, numbers of leaves and subtrees, verb valency
*   Coordination chains, clauses and subordinate clauses
*   Noun phrase modifiers and genitive chains
*   Participial and adverbial participial clauses, passive voice, infinitives and negations
*   Syntactic officialese markers: split predicates ("осуществлять проверку"), noun-to-verb ratio

```python
>>> import spacy
>>> from ruts import SyntaxStats

>>> nlp = spacy.load('ru_core_news_sm')
>>> text = "Дом, построенный рабочими в прошлом году, был продан. Он сказал, что не придёт, и ушёл, хлопнув дверью."
>>> ss = SyntaxStats(nlp(text))

>>> ss.tree_depth, ss.mean_dependency_distance
(4.0, 1.9333333333333333)
>>> ss.clauses_per_sent, ss.subordinate_clauses_per_sent
(1.5, 0.5)
>>> ss.participle_clauses_per_sent, ss.converb_clauses_per_sent, ss.p_passive
(0.5, 0.5, 0.4)
```

More in the [documentation](https://sergeyshk.github.io/ruTS/stats/syntax_stats/).

</details>

<details>
<summary><b>Cohesion statistics</b></summary>

<br>

The library counts over lemmas (spaCy for an annotated `Doc`, pymorphy3 for a string), no dependency parse is needed:

*   Noun, argument and content word overlap between adjacent sentences and all sentence pairs (binary and proportional, as in Coh-Metrix)
*   Givenness: share of pronouns, pronoun-to-noun ratio, share of demonstratives and of content words already seen
*   Temporal cohesion: tense and aspect repetition in adjacent sentences
*   Connective density per 1000 words by class (causal, adversative, concessive, temporal, additive, conditional, reformulative) and type, by an own dictionary of 317 connectives

```python
>>> from ruts import CohesionStats

>>> text = "Кот сидел на окне. Он смотрел на птиц. Птицы улетели, и кот уснул. Завтра он снова будет сидеть на этом окне."
>>> cs = CohesionStats(text)

>>> cs.noun_overlap_adjacent, cs.noun_overlap_all
(0.3333333333333333, 0.5)
>>> cs.argument_overlap_all, cs.content_overlap_prop_adjacent
(0.6666666666666666, 0.1111111111111111)
>>> cs.p_pronouns, cs.p_given, cs.temporal_cohesion
(0.14285714285714285, 0.2857142857142857, 0.5)

>>> cs = CohesionStats("Кот ждал птиц, потому что был голоден. Однако птицы улетели, и всё же кот не ушёл.")
>>> cs.connectors_causal, cs.connectors_adversative, cs.connectors_concessive
(62.5, 62.5, 62.5)
```

More in the [documentation](https://sergeyshk.github.io/ruTS/stats/cohesion_stats/).

</details>

<details>
<summary><b>Lexical sophistication statistics</b></summary>

<br>

How rare the words of a text are relative to the language (lexical sophistication in the spirit of TAALES):

*   Mean frequency, range and dispersion of lemmas by the Lyashevskaya-Sharoff frequency dictionary (downloaded once: `FreqDict().download()`)
*   Shares of words from the top-1000, 2000, 5000 and 10000 frequency bands by the embedded Sharoff list - work without the dictionary
*   Surprisal and perplexity under the dictionary unigram model, dictionary coverage, lexical density
*   The Solovyev-Ivanov-Solnyshkina formula with frequency - `ReadabilityStats.sis_grade_by_freq`

```python
>>> from ruts import LexicalStats
>>> from ruts.datasets import FreqDict

>>> FreqDict().download()
>>> ls = LexicalStats("Кот сидел на окне и смотрел на птиц")

>>> ls.mean_ipm_content, ls.mean_log_ipm, ls.surprisal
(324.18, 3.0674194359404705, 9.74182176626998)
>>> ls.p_top1000, ls.p_top10000, ls.lexical_density
(0.75, 1.0, 0.625)

>>> LexicalStats("Фелинолог пребывал на подоконнике").p_beyond_top10000
0.25
```

More in the [documentation](https://sergeyshk.github.io/ruTS/stats/lexical_stats/).

</details>

<details>
<summary><b>Corpus measures</b></summary>

<br>

Corpus linguistics tools over word lists - functions of the `ruts.corpus` subpackage, results are lists of named tuples (`pd.DataFrame(result)` gives a table):

*   Keywords relative to a reference corpus or the Lyashevskaya-Sharoff frequency dictionary: G² with p-value, Log Ratio, %DIFF, BIC, ELL, odds ratio
*   Collocations within a window by logDice, MI, MI³, t-score, Dice, G², NPMI, minimum sensitivity; collocates of a single word
*   Dispersion of words across text parts: Gries's DP, Juilland's D, Carroll's D2, Rosengren's S, Kullback-Leibler divergence
*   KWIC concordance by word form or lemma; Zipf-Mandelbrot fit - `fit_zipf_mandelbrot` in `ruts.diversity_stats`

```python
>>> from ruts import WordsExtractor
>>> from ruts.corpus import keyness, collocations, dispersion, kwic, print_kwic

>>> we = WordsExtractor(use_lexemes=True, lowercase=True)
>>> text = "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне. Завтра кот снова будет сидеть на окне и смотреть на птиц."
>>> target = we.extract(text)
>>> reference = we.extract("Собака лежала на полу и дремала. Потом собака ела и снова дремала. Завтра собака будет гулять.")

>>> [(k.word, round(k.g2, 2), round(k.log_ratio, 2)) for k in keyness(target, reference, top_n=2)]
[('кот', 2.88, 1.88), ('окно', 2.88, 1.88)]
>>> [(c.left, c.right, c.freq_pair, round(c.score, 2)) for c in collocations(target, window=2, top_n=2)]
[('птица', 'улететь', 2, 13.0), ('и', 'смотреть', 2, 12.68)]
>>> [(d.word, round(d.dp, 2)) for d in dispersion(target, parts=3, min_freq=3)][:3]
[('на', 0.15), ('кот', 0.32), ('окно', 0.03)]
>>> print_kwic(kwic(text, "окно", by_lemma=True, window=2), width=16)
        сидел на  окне  и смотрел
        уснул на  окне  . Завтра кот
       сидеть на  окне  и смотреть
```

More in the [documentation](https://sergeyshk.github.io/ruTS/corpus/keyness/).

</details>

<details>
<summary><b>Datasets</b></summary>

<br>

The library allows working with a number of preprocessed datasets:

*   [sov_chrest_lit](https://sergeyshk.github.io/ruTS/datasets/sovchlit/) - soviet reading-books for literature classes
*   [stalin_works](https://sergeyshk.github.io/ruTS/datasets/stalinworks/) - the collected works of Stalin
*   [freq2011](https://sergeyshk.github.io/ruTS/datasets/freq2011/) - the Lyashevskaya-Sharoff frequency dictionary: 52,138 lemmas with ipm, range and dispersion over the Russian National Corpus
*   [texts_by_grade](https://sergeyshk.github.io/ruTS/datasets/textsbygrade/) - texts with grade labels from the Plain Russian Language project (CC0), used to validate the readability formulas

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

A dataset is downloaded by the `download()` method and cached locally, a repeated call downloads nothing; before the download `get_texts()` and `get_records()` raise `OSError` with a hint.

</details>

<details>
<summary><b>Visualization</b></summary>

<br>

The library allows visualizing text with the help of the following graphs:

*   [Zipf's law](https://sergeyshk.github.io/ruTS/visualizers/zipf/)
*   [Literature Fingerprinting](https://sergeyshk.github.io/ruTS/visualizers/fingerprinting/)
*   [Word Tree](https://sergeyshk.github.io/ruTS/visualizers/word_tree/)
*   [Text highlighting](https://sergeyshk.github.io/ruTS/visualizers/highlight/) by 15 layers in five groups: readability (long sentences, complex and rare words), syntax (passive voice, participial clauses, genitive chains, split predicates), officialese (verbal nouns, compound prepositions, clichés), style (stop words, parentheticals, connectives), phonics (alliteration)

Highlighting returns an object rendered in Jupyter as HTML with a legend and hover notes; six layers are on by default, `layers="all"` enables every layer; syntactic layers require a `Doc` with a dependency parse:

```python
>>> import spacy
>>> from ruts.visualizers import highlight

>>> nlp = spacy.load('ru_core_news_sm')
>>> text = (
...     "Проект, подготовленный за неделю, был одобрен советом без обсуждения. "
...     "Повышение эффективности использования бюджетных средств обсуждалось, не выходя за рамки регламента. "
...     "Участники, представлявшие региональные министерства, не смогли согласовать позиции по вопросам "
...     "финансирования и распределения ответственности между ведомствами, поскольку каждое из них "
...     "настаивало на собственной трактовке положений соглашения. "
...     "Споры стихли, в кулуарах шумно шептались и шушукались, а решение было отложено до следующего заседания."
... )
>>> ht = highlight(nlp(text))
>>> ht.counts
{'long_sents': 1, 'complex_words': 26, 'passive': 4, 'genitive_chains': 2, 'split_predicates': 0, 'cliches': 1}
>>> highlight(nlp(text), layers=["verbal_nouns", "connectors", "rare_words"]).counts
{'rare_words': 3, 'verbal_nouns': 10, 'connectors': 4}
>>> ht  # rendered as highlighted text in Jupyter, the markup is available via ht.to_html()
```

<p align="center">
  <img src="https://raw.githubusercontent.com/SergeyShk/ruTS/master/docs/img/highlight.png" alt="Text highlighting" width="760">
</p>

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
*   `CohesionStats`
*   `DiversityStats`
*   `LexicalStats`
*   `MorphStats`
*   `PhonStats`
*   `ReadabilityStats`
*   `StyleStats`
*   `SyntaxStats`

```python
>>> import ruts
>>> import spacy

>>> nlp = spacy.load('ru_core_news_sm')
>>> nlp.add_pipe('basic', last=True)

>>> doc = nlp("Существуют три вида лжи: ложь, наглая ложь и статистика")
>>> doc._.basic.c_letters
{1: 1, 3: 2, 4: 3, 6: 1, 10: 2}

>>> doc._.basic.n_words
9
```

The values match the example above: punctuation and whitespace tokens of spaCy are filtered out when counting.

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
    *   cohesion_stats.py - cohesion statistics
    *   components.py - spaCy components
    *   constants.py - main constants
    *   diversity_stats.py - lexical diversity metrics
    *   extractors.py - tools for object extraction from a text
    *   lexical_stats.py - lexical sophistication statistics
    *   morph_stats.py - morphological statistics
    *   phon_stats.py - phonostatistics
    *   readability_stats.py - readability metrics
    *   style_stats.py - SEO style metrics
    *   syntax_stats.py - syntactic statistics
    *   utils.py - helper tools
    *   **corpus** - corpus measures:
        *   collocations.py - collocations and association measures
        *   dispersion.py - word dispersion across text parts
        *   keyness.py - keywords relative to a reference corpus
        *   kwic.py - KWIC concordance
    *   **datasets** - datasets:
        *   dataset.py - base class for working with datasets
        *   freq2011.py - the Lyashevskaya-Sharoff frequency dictionary
        *   sov_chrest_lit.py - soviet reading-books for literature classes
        *   stalin_works.py - the collected works of Stalin
        *   texts_by_grade.py - texts with grade labels from the Plain Russian Language project
    *   **resources** - embedded lexical resources (the most frequent lemmas list, the connectives dictionary)
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
