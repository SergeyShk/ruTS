<p align="center">
  <img src="https://raw.githubusercontent.com/SergeyShk/ruTS/master/docs/img/ruts.png" alt="ruTS" width="360">
</p>

<h1 align="center">ruTS</h1>

<p align="center">
  <b>Russian Texts Statistics</b> - библиотека для извлечения статистик из текстов на русском языке
</p>

<p align="center">
  <a href="https://sergeyshk.github.io/ruTS/">Документация</a> ·
  <a href="https://huggingface.co/spaces/SergeyShk/ruTS">Демо</a> ·
  <a href="https://pypi.org/project/ruts/">PyPI</a> ·
  <a href="https://github.com/SergeyShk/ruTS/blob/master/README.en.md">English</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/ruts/"><img src="https://img.shields.io/pypi/v/ruTS?logo=pypi&logoColor=FFE873" alt="Версия"></a>
  <a href="https://pypi.org/project/ruts/"><img src="https://img.shields.io/pypi/pyversions/ruts.svg?logo=python&logoColor=FFE873" alt="Поддерживаемые версии Python"></a>
  <a href="https://github.com/SergeyShk/ruTS/actions/workflows/ci.yml"><img src="https://github.com/SergeyShk/ruTS/actions/workflows/ci.yml/badge.svg" alt="Сборка"></a>
  <a href="https://codecov.io/gh/SergeyShk/ruTS"><img src="https://codecov.io/gh/SergeyShk/ruTS/branch/master/graph/badge.svg" alt="Покрытие"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="LICENSE.txt"><img src="https://img.shields.io/github/license/sergeyshk/ruts.svg" alt="Лицензия"></a>
  <img src="https://img.shields.io/pypi/dm/ruTS" alt="Загрузки">
  <a href="https://huggingface.co/spaces/SergeyShk/ruTS"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Spaces-демо-blue" alt="Демо на Hugging Face Spaces"></a>
</p>

---

**ruTS** считает по русскому тексту то, для чего обычно приходится собирать несколько разрозненных инструментов: базовые статистики, метрики удобочитаемости и лексического разнообразия, морфологические признаки. Функционал основан на адаптированных для русского языка статистиках библиотеки [textacy](https://github.com/chartbeat-labs/textacy).

Работать можно как с обычными строками, так и с готовыми `Doc`-объектами [spaCy](https://github.com/explosion/spaCy) - каждая статистика доступна и как отдельный класс, и как компонент пайплайна spaCy.

Попробовать без установки можно в [демо на Hugging Face Spaces](https://huggingface.co/spaces/SergeyShk/ruTS): вставьте текст и получите класс удобочитаемости, метрики, графики и подсветку фрагментов.

* **[Извлечение объектов](https://sergeyshk.github.io/ruTS/extractors/words/)** - настраиваемые токенизаторы слов и предложений
* **[Базовые статистики](https://sergeyshk.github.io/ruTS/stats/basic_stats/)** - количество слов, предложений, слогов, знаков препинания и их распределения
* **[Метрики удобочитаемости](https://sergeyshk.github.io/ruTS/stats/readability_stats/)** - тест Флеша-Кинкайда, индекс SMOG, LIX и другие, с коэффициентами для русского языка
* **[Метрики лексического разнообразия](https://sergeyshk.github.io/ruTS/stats/diversity_stats/)** - TTR и его вариации, MTLD, HD-D, индексы Симпсона и Юла, энтропия, законы Ципфа и Хипса
* **[Морфологические статистики](https://sergeyshk.github.io/ruTS/stats/morph_stats/)** - часть речи, падеж, наклонение, переходность и другие признаки в терминах Universal Dependencies
* **[SEO-метрики стиля](https://sergeyshk.github.io/ruTS/stats/style_stats/)** - тошнота, водность, заспамленность, естественность по Ципфу, плотность ключевых слов, лексические маркеры канцелярита
* **[Фоностатистики](https://sergeyshk.github.io/ruTS/stats/phon_stats/)** - классы звуков, кластеры, аллитерация и ассонанс, слоги по правилу восходящей звучности
* **[Синтаксические статистики](https://sergeyshk.github.io/ruTS/stats/syntax_stats/)** - длины зависимостей, глубина дерева, сочинительные цепочки, клаузы, обороты, пассив, цепочки родительных падежей, расщеплённые сказуемые и другие маркеры канцелярита по разбору spaCy
* **[Статистики связности](https://sergeyshk.github.io/ruTS/stats/cohesion_stats/)** - повторы существительных, аргументов и знаменательных слов между предложениями, данность, темпоральная связность, коннекторы по классам
* **[Статистики лексической сложности](https://sergeyshk.github.io/ruTS/stats/lexical_stats/)** - частотность слов по словарю Ляшевской и Шарова, частотные полосы, сюрпризал, лексическая плотность
* **[Корпусные меры](https://sergeyshk.github.io/ruTS/corpus/keyness/)** - ключевые слова относительно эталонного корпуса или частотного словаря, коллокации, дисперсия слов, конкорданс KWIC
* **[Наборы данных](https://sergeyshk.github.io/ruTS/datasets/sovchlit/)** - готовые предобработанные корпуса с фильтрацией
* **[Визуализация](https://sergeyshk.github.io/ruTS/visualizers/zipf/)** - закон Ципфа, литературная дактилоскопия, дерево слов, подсветка текста в стиле Главреда
* **[Компоненты spaCy](https://sergeyshk.github.io/ruTS/components/)** - встраивание любой статистики в пайплайн

## Установка

Требуется Python 3.11 или новее.

```bash
pip install ruts
```

Или с помощью [uv](https://docs.astral.sh/uv/):

```bash
uv add ruts
```

Для работы с компонентами spaCy и синтаксическими статистиками понадобится русскоязычная модель:

```bash
python -m spacy download ru_core_news_sm
```

## Быстрый старт

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

## Возможности

### Извлечение объектов

Библиотека позволяет создавать свои инструменты для извлечения предложений и слов из текста, которые затем можно использовать при вычислении статистик.

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

Подробнее - в документации: [слова](https://sergeyshk.github.io/ruTS/extractors/words/), [предложения](https://sergeyshk.github.io/ruTS/extractors/sentences/).

<details>
<summary><b>Базовые статистики</b></summary>

<br>

Библиотека позволяет извлекать из текста следующие статистические показатели:

*   количество предложений
*   количество слов
*   количество уникальных слов
*   количество длинных слов
*   количество сложных слов
*   количество простых слов
*   количество односложных слов
*   количество многосложных слов
*   количество символов
*   количество букв
*   количество пробелов
*   количество слогов
*   количество знаков препинания
*   распределение слов по количеству букв
*   распределение слов по количеству слогов

Любую статистику можно вывести на экран в читаемом виде:

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

Подробнее - в [документации](https://sergeyshk.github.io/ruTS/stats/basic_stats/).

</details>

<details>
<summary><b>Метрики удобочитаемости</b></summary>

<br>

Библиотека позволяет вычислять для текста следующие метрики удобочитаемости:

*   Тест Флеша-Кинкайда
*   Индекс удобочитаемости Флеша
*   Индекс Колман-Лиау
*   Индекс SMOG
*   Автоматический индекс удобочитаемости
*   Индекс удобочитаемости LIX
*   Индекс удобочитаемости RIX
*   Формула Соловьёва, Иванова, Солнышкиной
*   Формула Мацковского
*   Индекс Дейла-Чейла
*   Индекс Ганнинга

Поверх формул работает интерпретирующий слой: сводный класс по медиане формул класса, соответствие класса возрасту читателя по таблице plainrussian и время чтения.

Коэффициенты формул, адаптированных для русского языка, задаются пресетом `preset`: по умолчанию используются коэффициенты проекта [Plain Russian Language](https://github.com/infoculture/plainrussian), полученные на текстах с метками класса (`plainrussian`), доступны также коэффициенты Оборневой для художественных текстов (`fiction`) и казанской группы (Соловьёв, Иванов, Солнышкина) для учебных (`academic`).

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

Подробнее - в [документации](https://sergeyshk.github.io/ruTS/stats/readability_stats/).

</details>

<details>
<summary><b>Метрики лексического разнообразия</b></summary>

<br>

Библиотека позволяет вычислять для текста следующие метрики лексического разнообразия:

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
*   MTLD со скользящим окном и заворотом текста (MTLD-W)
*   Hypergeometric Distribution D (HD-D)
*   Индекс Симпсона (D), обратный индекс Симпсона (1/D) и индекс Джини-Симпсона (1-D)
*   Гапакс-индекс (Honoré's R), доля гапаксов, меры Баайена (P) и показатель α₂
*   Характеристики Юла (K и I), меры Хердана (Vm), Сишела (S), Мишеа (M), Брюне (W) и Дюга (k)
*   Энтропия Шеннона, выравненность и перплексия
*   Наклон закона Ципфа (α) и показатель закона Хипса (β)

Окна, пороги и основание логарифма вынесены в параметры `DiversityStats`, любую метрику можно посчитать по окнам с доверительным интервалом методом `windowed`. Часть реализаций метрик взята из проекта [lexical_diversity](https://github.com/kristopherkyle/lexical_diversity), формулы мер по спектру частот сверены с Tweedie и Baayen (1998), zipfR и quanteda.

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

Подробнее - в [документации](https://sergeyshk.github.io/ruTS/stats/diversity_stats/).

</details>

<details>
<summary><b>Морфологические статистики</b></summary>

<br>

Библиотека позволяет извлекать из текста следующие морфологические признаки:

*   часть речи
*   одушевленность
*   вид
*   падеж
*   род
*   совместность
*   наклонение
*   число
*   лицо
*   время
*   переходность
*   форма глагола
*   залог

Значения выдаются в терминах [Universal Dependencies](https://universaldependencies.org/u/feat/): для `Doc` spaCy с разметкой они берутся из `token.pos_` и `token.morph` с учётом контекста, для строки - из первого разбора [pymorphy3](https://github.com/no-plagiarism/pymorphy3) с переводом граммем OpenCorpora в UD.

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

Отдельные слова можно разобрать с расшифровкой признаков через `ms.explain_text(filter_none=True)`.

Подробнее - в [документации](https://sergeyshk.github.io/ruTS/stats/morph_stats/).

</details>

<details>
<summary><b>SEO-метрики стиля</b></summary>

<br>

Библиотека повторяет показатели сервисов [Advego](https://advego.com/text/seo/) и [Text.ru](https://text.ru/seo):

*   Классическая и академическая тошнота
*   Водность
*   Заспамленность
*   Естественность по закону Ципфа
*   Плотность ключевых слов и фраз
*   Лексические маркеры канцелярита: отглагольные существительные, производные предлоги, вводные слова, штампы

Точные формулы сервисов не опубликованы, поэтому реализованы общепринятые определения; стоп-слова для водности определяются по части речи с помощью pymorphy3 или задаются списком.

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

Подробнее - в [документации](https://sergeyshk.github.io/ruTS/stats/style_stats/).

</details>

<details>
<summary><b>Фоностатистики</b></summary>

<br>

Библиотека считает по буквам, без учета оглушения и ударения:

*   Доли гласных, сонорных, звонких и глухих согласных, отношение согласных к гласным
*   Консонантные кластеры и зияния гласных
*   Энтропию CV-шаблонов слов и «жёсткость»
*   Индексы аллитерации и ассонанса относительно ожидаемых повторов
*   Слоги по правилу восходящей звучности: доля открытых слогов, средняя длина слога, CV-шаблоны

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

Подробнее - в [документации](https://sergeyshk.github.io/ruTS/stats/phon_stats/).

</details>

<details>
<summary><b>Синтаксические статистики</b></summary>

<br>

Библиотека считает по дереву зависимостей spaCy (нужна модель с парсером):

*   Длины зависимостей, глубину дерева, число листьев и поддеревьев, валентность глаголов
*   Сочинительные цепочки, клаузы и придаточные
*   Модификаторы именной группы и цепочки родительных падежей
*   Причастные и деепричастные обороты, пассив, инфинитивы и отрицания
*   Синтаксические маркеры канцелярита: расщеплённые сказуемые («осуществлять проверку»), отношение существительных к глаголам

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

Подробнее - в [документации](https://sergeyshk.github.io/ruTS/stats/syntax_stats/).

</details>

<details>
<summary><b>Статистики связности</b></summary>

<br>

Библиотека считает по леммам (spaCy для `Doc` с разметкой, pymorphy3 для строки), разбор зависимостей не нужен:

*   Повторы существительных, аргументов и знаменательных слов между соседними предложениями и всеми парами предложений (бинарные и пропорциональные, как в Coh-Metrix)
*   Данность: доля местоимений, отношение местоимений к существительным, доля указательных и уже встречавшихся знаменательных слов
*   Темпоральную связность: повтор времени и вида глаголов в соседних предложениях
*   Плотность коннекторов на 1000 слов по классам (причинные, противительные, уступительные, временные, аддитивные, условные, переформулирующие) и типам по собственному словарю из 317 единиц

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

Подробнее - в [документации](https://sergeyshk.github.io/ruTS/stats/cohesion_stats/).

</details>

<details>
<summary><b>Статистики лексической сложности</b></summary>

<br>

Насколько слова текста редки относительно языка (lexical sophistication по образцу TAALES):

*   Средняя частотность, диапазон и дисперсия лемм по частотному словарю Ляшевской и Шарова (загружается один раз: `FreqDict().download()`)
*   Доли слов из частотных полос топ-1000, 2000, 5000 и 10000 по вшитому списку Шарова - работают без словаря
*   Сюрпризал и перплексия по униграммной модели словаря, покрытие словарём, лексическая плотность
*   Формула Соловьёва, Иванова, Солнышкиной с частотностью - `ReadabilityStats.sis_grade_by_freq`

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

Подробнее - в [документации](https://sergeyshk.github.io/ruTS/stats/lexical_stats/).

</details>

<details>
<summary><b>Корпусные меры</b></summary>

<br>

Инструменты корпусной лингвистики над списками слов - функции подпакета `ruts.corpus`, результаты - списки именованных кортежей (`pd.DataFrame(result)` даёт таблицу):

*   Ключевые слова относительно эталонного корпуса или частотного словаря Ляшевской и Шарова: G² с p-значением, Log Ratio, %DIFF, BIC, ELL, отношение шансов
*   Коллокации в окне по logDice, MI, MI³, t-score, Dice, G², NPMI, минимальной чувствительности; сочетаемость одного слова
*   Дисперсия слов по частям текста: DP Гриса, D Жюйана, D2 Кэрролла, S Розенгрена, дивергенция Кульбака-Лейблера
*   Конкорданс KWIC по словоформе или лемме; подгонка закона Ципфа-Мандельброта - `fit_zipf_mandelbrot` в `ruts.diversity_stats`

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

Подробнее - в [документации](https://sergeyshk.github.io/ruTS/corpus/keyness/).

</details>

<details>
<summary><b>Наборы данных</b></summary>

<br>

Библиотека позволяет работать с несколькими заранее предобработанными наборами данных:

*   [sov_chrest_lit](https://sergeyshk.github.io/ruTS/datasets/sovchlit/) - советские хрестоматии по литературе
*   [stalin_works](https://sergeyshk.github.io/ruTS/datasets/stalinworks/) - полное собрание сочинений И.В. Сталина
*   [freq2011](https://sergeyshk.github.io/ruTS/datasets/freq2011/) - частотный словарь Ляшевской и Шарова: 52 138 лемм с ipm, диапазоном и дисперсией по НКРЯ
*   [texts_by_grade](https://sergeyshk.github.io/ruTS/datasets/textsbygrade/) - тексты с метками класса проекта Plain Russian Language (CC0), на которых проверяются формулы удобочитаемости

Существует возможность работать как с чистыми текстами (без заголовочной информации), так и с записями, а также фильтровать их по различным критериям.

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

Набор данных скачивается методом `download()` и кэшируется локально, повторный вызов ничего не качает; до загрузки `get_texts()` и `get_records()` поднимают `OSError` с подсказкой.

</details>

<details>
<summary><b>Визуализация</b></summary>

<br>

Библиотека позволяет визуализировать тексты с помощью следующих видов графиков:

*   [Закон Ципфа](https://sergeyshk.github.io/ruTS/visualizers/zipf/) (Zipf's law)
*   [Литературная дактилоскопия](https://sergeyshk.github.io/ruTS/visualizers/fingerprinting/) (Literature Fingerprinting)
*   [Дерево слов](https://sergeyshk.github.io/ruTS/visualizers/word_tree/) (Word Tree)
*   [Подсветка текста](https://sergeyshk.github.io/ruTS/visualizers/highlight/) по 15 слоям в пяти группах: читаемость (длинные предложения, сложные и редкие слова), синтаксис (пассив, обороты, цепочки родительных, расщеплённые сказуемые), канцелярит (отглагольные существительные, производные предлоги, штампы), стиль (стоп-слова, вводные слова, коннекторы), фоника (аллитерации)

Подсветка возвращает объект, который отображается в Jupyter как HTML с легендой и всплывающими пояснениями; по умолчанию включены шесть слоёв, `layers="all"` включает все; синтаксические слои требуют `Doc` с разбором зависимостей:

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
>>> ht  # в Jupyter отобразится подсветка, разметка доступна через ht.to_html()
```

<p align="center">
  <img src="https://raw.githubusercontent.com/SergeyShk/ruTS/master/docs/img/highlight.png" alt="Подсветка текста" width="760">
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
  <img src="https://raw.githubusercontent.com/SergeyShk/ruTS/master/docs/img/zipf.png" alt="Закон Ципфа" width="520">
</p>

</details>

<details>
<summary><b>Компоненты spaCy</b></summary>

<br>

Библиотека позволяет создавать компоненты spaCy для следующих классов:

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

Значения совпадают с примером выше: знаки препинания и пробельные токены spaCy при подсчёте отфильтровываются.

Подробнее - в [документации](https://sergeyshk.github.io/ruTS/components/).

</details>

## Разработка

Проект использует [uv](https://docs.astral.sh/uv/) для управления зависимостями и [ruff](https://docs.astral.sh/ruff/) для линтинга и форматирования.

```bash
git clone https://github.com/SergeyShk/ruTS.git
cd ruTS

make deps        # создать окружение и установить зависимости
make nltk-data   # загрузить данные NLTK, нужные для тестов
make test        # запустить тесты
make lint        # ruff + mypy
```

Полный список команд - `make help`.

Перед отправкой изменений стоит установить хуки, которые прогонят линтеры на коммите и тесты на пуше:

```bash
uv run pre-commit install
```

## Участие в проекте

Баг-репорты, идеи и пул-реквесты приветствуются - [issues](https://github.com/SergeyShk/ruTS/issues) открыты. Перед отправкой пул-реквеста убедитесь, что `make lint` и `make test` проходят без ошибок.

<details>
<summary><b>Структура проекта</b></summary>

<br>

*   **docs** - документация по проекту
*   **ruts**:
    *   basic_stats.py - базовые текстовые статистики
    *   cohesion_stats.py - статистики связности текста
    *   components.py - компоненты spaCy
    *   constants.py - основные используемые константы
    *   diversity_stats.py - метрики лексического разнообразия текста
    *   extractors.py - инструменты для извлечения объектов из текста
    *   lexical_stats.py - статистики лексической сложности текста
    *   morph_stats.py - морфологические статистики
    *   phon_stats.py - фоностатистики текста
    *   readability_stats.py - метрики удобочитаемости текста
    *   style_stats.py - SEO-метрики стиля текста
    *   syntax_stats.py - синтаксические статистики текста
    *   utils.py - вспомогательные инструменты
    *   **corpus** - корпусные меры:
        *   collocations.py - коллокации и меры ассоциации
        *   dispersion.py - дисперсия слов по частям текста
        *   keyness.py - ключевые слова относительно эталонного корпуса
        *   kwic.py - конкорданс KWIC
    *   **datasets** - наборы данных:
        *   dataset.py - базовый класс для работы с наборами данных
        *   freq2011.py - частотный словарь Ляшевской и Шарова
        *   sov_chrest_lit.py - советские хрестоматии по литературе
        *   stalin_works.py - полное собрание сочинений И.В. Сталина
        *   texts_by_grade.py - тексты с метками класса проекта Plain Russian Language
    *   **resources** - вшитые лексические ресурсы (список самых частых лемм, словарь коннекторов)
    *   **visualizers** - инструменты для визуализации текстов:
        *   fingerprinting.py - Литературная дактилоскопия
        *   word_tree.py - Дерево слов
        *   zipf.py - Закон Ципфа
*   **tests** - тесты, повторяющие структуру пакета

</details>

## Авторы

*   Шкарин Сергей (kouki.sergey@gmail.com)
*   Смирнова Екатерина (ekanerina@yandex.ru)

## Лицензия

[MIT](LICENSE.txt)

## Цитирование

Пожалуйста, используйте следующую BibTeX нотацию для цитирования библиотеки **ruTS**, если вы используете ее в своих исследованиях или программах. Цитирование является очень полезным для дальнейшей разработки и поддержки данного проекта.

```bibtex
@software{ruTS,
  author = {Sergey Shkarin},
  title = {{ruTS, a library for statistics extraction from texts in Russian}},
  year = 2026,
  publisher = {Moscow},
  url = {https://github.com/SergeyShk/ruTS}
}
```
