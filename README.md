# Russian Texts Statistics (ruTS)

![Version](https://img.shields.io/pypi/v/ruTS?logo=pypi&logoColor=FFE873)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pypistats.svg?logo=python&logoColor=FFE873)](https://pypi.org/project/pypistats/)
![Downloads](https://img.shields.io/pypi/dm/ruTS)
![Status](https://img.shields.io/pypi/status/ruts)
[![License](https://img.shields.io/github/license/hugovk/pypistats.svg)](LICENSE.txt)
![Repo size](https://img.shields.io/github/repo-size/SergeyShk/ruTS)
![Codacy grade](https://img.shields.io/codacy/grade/5e1cef0e2fa64bdc835f7bfcb7996edc.svg?logo=codacy)

Библиотека для извлечения статистик из текстов на русском языке.

## Установка

Выполнить:

```bash
$ pip install ruts
```

Зависимости:

* python 3.6+
* nltk
* pymorphy2
* spacy

Библиотека по умолчанию использует токенизатор от nltk, который необходимо предварительно скачать:

```python
import nltk
nltk.download('punkt') 
```

## Функционал

Основной функционал базируется на адаптированных для русского языка статистиках библиотеки [textacy](https://github.com/chartbeat-labs/textacy) и позволяет работать как непосредственно с текстами, так и с подготовленными Doc-объектами библиотеки [spaCy](https://github.com/explosion/spaCy).

### Извлечение объектов

Библиотека позволяет создавать свои инструменты для извлечения предложений и слов из текста, которые затем можно использовать при вычислении статистик.

Пример:

```python
import re
from nltk.corpus import stopwords
from ruts import SentsExtractor, WordsExtractor
text = "Не имей 100 рублей, а имей 100 друзей"
se = SentsExtractor(text, tokenizer=re.compile(r', '))
se.extract()

    ('Не имей 100 рублей', 'а имей 100 друзей')

we = WordsExtractor(text, use_lexemes=True, stopwords=stopwords.words('russian'), filter_nums=True, ngram_range=(1, 2))
we.extract()

    ('иметь', 'рубль', 'иметь', 'друг', 'иметь_рубль', 'рубль_иметь', 'иметь_друг')
   
we.get_most_common(3)

    [('иметь', 2), ('рубль', 1), ('друг', 1)]
```

### Базовые статистики

Библиотека позволяет извлекать из текста следующие статистические показатели:

* количество предложений
* количество слов
* количество уникальных слов
* количество длинных слов
* количество сложных слов
* количество простых слов
* количество односложных слов
* количество многосложных слов
* количество символов
* количество букв
* количество пробелов
* количество слогов
* количество знаков препинания
* распределение слов по количеству букв
* распределение слов по количеству слогов

Пример:

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

### Метрики удобочитаемости

Библиотека позволяет вычислять для текста следующие метрики удобочитаемости:

* Тест Флеша-Кинкайда
* Индекс удобочитаемости Флеша
* Индекс Колман-Лиау
* Индекс SMOG
* Автоматический индекс удобочитаемости
* Индекс удобочитаемости LIX

Коэффициенты метрик для русского языка были взяты из работы исследователей проекта [Plain Russian Language](https://github.com/infoculture/plainrussian), которые получили их на основе специально подобранных текстов с предварительными возрастными пометками.

Пример:

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

### Морфологические статистики

Библиотека позволяет извлекать из текста следующие морфологические признаки:

* часть речи
* одушевленность
* вид
* падеж
* род
* совместность
* наклонение
* число
* лицо
* время
* переходность
* залог

Для морфологического разбора текста используется библиотека [pymorphy2](https://github.com/kmike/pymorphy2). Описание статистик взяты из корпуса [OpenCorpora](http://opencorpora.org/dict.php?act=gram).

Пример:

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

### Наборы данных

Библиотека позволяет работать с несколькими заранее предобработанными наборами данных:

* sov_chrest_lit - советские хрестоматии по литературе

Существует возможность работать как с чистыми текстами (без заголовочной информации), так и с записями, а также фильтровать их по различным критериям.

Пример:

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

## Структура проекта

* **ruts**:
    * basic_stats.py - базовые текстовые статистики
    * constants.py - основные используемые константы
    * extractors.py - инструменты для извлечения объектов из текста
    * morph_stats.py - морфологические статистики
    * readability_stats.py - метрики удобочитаемости текста
    * utils.py - вспомогательные инструменты
    * **datasets** - наборы данных
        * dataset.py - базовый класс для работы с наборами данных
        * sov_chrest_lit.py - советские хрестоматии по литературе
* **tests**:
    * test_basic_stats.py - тесты базовых текстовых статистик
    * test_extractors.py - тесты инструментов для извлечения объектов из текста
    * test_morph_stats - тесты морфологических статистик
    * test_readability_stats.py - тесты метрик удобочитаемости текста

## Авторы

* Шкарин Сергей (kouki.sergey@gmail.com)
* Смирнова Екатерина (ekanerina@yandex.ru)
