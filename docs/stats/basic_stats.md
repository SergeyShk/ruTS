# Базовые статистики

``` {.python .signature}
BasicStats(source, sents_extractor=None, words_extractor=None, normalize=False, complex_syl_factor=4, long_word_letter_factor=6)
```

<!-- core: stats/basic_stats.md:BasicStats b417be1 -->
Базовые статистики текста: количество его предложений, слов, символов, слогов и знаков препинания и распределения его слов. Источник данных - текст или объект `Doc` библиотеки [spaCy](https://github.com/explosion/spaCy). Буквы считаются по `str.isalpha`, поэтому цифры, дефисы и знаки внутри слова буквами не являются.

Слова и предложения строки дают экстракторы. `Doc` дает словами свои токены без знаков препинания и символов вроде `€` или `%`, предложениями - свои границы или, если их нет или они частичные (`has_sents`), границы экстрактора предложений; переданный экстрактор вместо этого применяется к его тексту. Пустая строка завершает предложение строки и `Doc` без границ; `Doc` с границами - если в его пайплайне до парсера, `senter` или `sentencizer` стоит `start_sents_after_blank_lines` (библиотека регистрирует компонент под своим именем). Предложение без слов, например из одних знаков препинания, не считается.

Исключения:

- `SourceTypeError` - источник, который не строка и не `Doc`, экстрактор другого типа;
- `SourceError` - источник без слов;
- `ParameterError` - порог, который не целое число не меньше единицы.

Класс расширяет `BasicStats` ядра [anyTS](https://sergeyshk.github.io/anyTS/stats/basic_stats/) крючками русского языка: слоги слова считает [`count_syllables`](../syllables.md#count_syllables), экстракторы по умолчанию - русские [`SentsExtractor`](../extractors/sentences.md) и [`WordsExtractor`](../extractors/words.md), знаки препинания - [`count_punctuations`](#count_punctuations) ruTS, а части дефисного слова, разрезанного spaCy, склеиваются (`во-первых` - одно слово). Компонент пустых строк в ruTS называется [`ruts_blank_lines`](../components.md#blank_lines): `nlp.add_pipe("ruts_blank_lines", before="parser")`. Знаки ударения и мягкие переносы не считаются ни символами, ни частями слов, а й и ё из двух символов - одна буква (`ruts.utils.strip_marks`): текст с ударениями дает те же статистики, что без них. Статистики вычисляются при создании объекта, таблица `print_stats` - по-русски.

=== "Код"

    ``` python
    from ruts import BasicStats

    text = "Существуют три вида лжи: ложь, наглая ложь и статистика"
    bs = BasicStats(text, normalize=True)
    bs.print_stats()
    ```

=== "Результат"

    ```
        Статистика     | Значение
    ------------------------------
    Предложения        |    1
    Слова              |    9
    Уникальные слова   |    8
    Длинные слова      |    3
    Сложные слова      |    2
    Простые слова      |    7
    Односложные слова  |    5
    Многосложные слова |    4
    Символы            |    55
    Буквы              |    45
    Пробелы            |    8
    Слоги              |    18
    Знаки препинания   |    2
    ```

## Параметры

<!-- core: stats/basic_stats.md:BasicStats-parameters 362b585 -->
| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `source` | `str` / `Doc` | - | Источник данных (строка или объект Doc) |
| `sents_extractor` | `SentsExtractor` | `None` | Инструмент для извлечения предложений; для Doc применяется к его тексту |
| `words_extractor` | `WordsExtractor` | `None` | Инструмент для извлечения слов; для Doc применяется к его тексту |
| `normalize` | `bool` | `False` | Вычислять нормализованные статистики |
| `complex_syl_factor` | `int` | `COMPLEX_SYL_FACTOR` | Минимальное количество слогов в сложном слове |
| `long_word_letter_factor` | `int` | `LONG_WORD_LETTER_FACTOR` | Минимальное количество букв в длинном слове |

Объект хранит `normalize`, `complex_syl_factor` и `long_word_letter_factor` под их именами.

В ruTS сложное слово - от четырех слогов, длинное - от шести букв: `COMPLEX_SYL_FACTOR = 4` и `LONG_WORD_LETTER_FACTOR = 6` из `ruts.constants`.

## Статистики

<!-- core: stats/basic_stats.md:BasicStats-attributes 2687b35 -->
| Статистика | Тип | Описание | Нормализованная |
| :--------- | :-- | :------- | :-------------- |
| `c_letters` | `dict[int, int]` | Распределение слов по количеству букв | - |
| `c_syllables` | `dict[int, int]` | Распределение слов по количеству слогов | - |
| `n_sents` | `int` | Количество предложений со словами | - |
| `n_words` | `int` | Количество слов | - |
| `n_unique_words` | `int` | Количество уникальных слов без учета регистра | `p_unique_words` |
| `n_long_words` | `int` | Количество длинных слов, не меньше чем из `long_word_letter_factor` букв | `p_long_words` |
| `n_complex_words` | `int` | Количество сложных слов, не меньше чем из `complex_syl_factor` слогов | `p_complex_words` |
| `n_simple_words` | `int` | Количество простых слов: со слогом, но не сложных | `p_simple_words` |
| `n_monosyllable_words` | `int` | Количество односложных слов | `p_monosyllable_words` |
| `n_polysyllable_words` | `int` | Количество многосложных слов, от двух слогов | `p_polysyllable_words` |
| `n_chars` | `int` | Количество символов без переносов строк | - |
| `n_letters` | `int` | Количество букв | `p_letters` |
| `n_spaces` | `int` | Количество пробелов Unicode (категория Zs), например неразрывных, и табуляций | `p_spaces` |
| `n_syllables` | `int` | Количество слогов | - |
| `n_punctuations` | `int` | Количество знаков препинания | `p_punctuations` |
| `c_punctuations` | `dict[str, int]` | Распределение знаков препинания по типам ([`count_punctuations`](#count_punctuations)) | - |

С `normalize=True` у объекта есть и нормализованные статистики типа `float`: количества слов, деленные на число слов, количества символов - на число символов.

## Методы

<!-- core: stats/basic_stats.md:BasicStats-count_words_by abc6821 -->
`count_words_by_syllables(min_syllables)` и `count_words_by_letters(min_letters)` возвращают количество слов не меньше чем с заданным числом слогов или букв; минимум, который не целое число, дает `ParameterError`.

Методы пересчитывают сложные и длинные слова с порогом, отличным от заданного при создании объекта: так класс [`ReadabilityStats`](readability_stats.md) считает индекс SMOG (сложное слово - от 5 слогов) и LIX (длинное слово - от 7 букв).

<!-- core: stats/basic_stats.md:BasicStats-get_stats f52c936 -->
`get_stats(flat)` возвращает справочник с распределениями `c_letters` и `c_syllables`, количествами из `stats_desc`, распределением `c_punctuations` и, с `normalize=True`, нормализованными количествами - копию: ее правка не меняет объект. С `flat=True` распределения дают по ключу на каждое значение, которое есть в тексте, например `c_letters_3` и `c_punctuations_comma`.

<!-- core: stats/basic_stats.md:BasicStats-print_stats da79e92 -->
`print_stats()` выводит таблицу с количествами из `stats_desc`, их описаниями и заголовками из `stats_headers`.

Нормализованных статистик `p_*` в таблице нет.

<!-- core: stats/stats.md:Stats-to_dataframe fb70c9b -->
`to_dataframe()` возвращает плоские статистики, `get_stats(flat=True)`, таблицей `DataFrame` библиотеки [pandas](https://pandas.pydata.org/) из одной строки со столбцом на каждый ключ. Статистика-справочник дает столбцы только для ключей, которые есть у текста, поэтому в таблицах нескольких текстов, объединенных `pandas.concat`, количество, которого у текста нет, - `NaN`. Нулями можно заполнять только такие столбцы: в остальных `NaN` - неопределенное значение.

Метод `describe` - из [интерфейса статистик](https://sergeyshk.github.io/anyTS/stats/stats/) ядра anyTS; шкал у базовых статистик нет, поэтому он всегда возвращает `None`.

=== "Код"

    ``` python
    bs.count_words_by_syllables(5), bs.count_words_by_letters(7)
    bs.get_stats()
    ```

=== "Результат"

    ```
    (0, 2)
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
     'c_punctuations': {'comma': 1,
                        'period': 0,
                        'question': 0,
                        'exclamation': 0,
                        'ellipsis': 0,
                        'colon': 1,
                        'semicolon': 0,
                        'dash': 0,
                        'hyphen': 0,
                        'angle_quotes': 0,
                        'straight_quotes': 0,
                        'parentheses': 0,
                        'other': 0},
     'p_unique_words': 0.8888888888888888,
     'p_long_words': 0.3333333333333333,
     'p_complex_words': 0.2222222222222222,
     'p_simple_words': 0.7777777777777778,
     'p_monosyllable_words': 0.5555555555555556,
     'p_polysyllable_words': 0.4444444444444444,
     'p_letters': 0.8181818181818182,
     'p_spaces': 0.14545454545454545,
     'p_punctuations': 0.03636363636363636}
    ```

## Знаки препинания { #count_punctuations }

<!-- core: stats/basic_stats.md:count_punctuations b982de2 -->
``` {.python .signature}
count_punctuations(text, marks=PUNCTUATION_MARKS, dash_pattern=DASH_PATTERN)
```

Считает знаки препинания по типам - распределение `c_punctuations`: запятые, точки, вопросительные и восклицательные знаки, многоточия, двоеточия, точки с запятой, тире, дефисы, кавычки-елочки, кавычки, скобки и прочие знаки. Сначала считаются тире, набранные дефисами (`dash_pattern`), затем многоточия - `…`, три и более точек или две после `?` и `!`, один знак, точки которого в точки не входят (`Кто там?..` - вопрос и многоточие), - затем каждый знак по его типу в `marks`; любой другой символ категорий Unicode P и S - прочий знак (`§`, `€`, `°`).

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `str` | - | Строка текста |
| `marks` | `dict[str, str]` | `PUNCTUATION_MARKS` | Тип каждого знака из `PUNCTUATION_TYPES` |
| `dash_pattern` | `Pattern` | `DASH_PATTERN` | Тире, набранные дефисами |

Знак `marks`, который не один символ или имеет неизвестный тип, дает `ParameterError`; текст, который не строка, `marks`, которые не словарь, и `dash_pattern`, который не скомпилированное регулярное выражение, дают `SourceTypeError`.

В ruTS `PUNCTUATION_MARKS` и `DASH_PATTERN` модуля `ruts.basic_stats` - знаки ядра с нижней кавычкой `„` в роли кавычки и шаблон тире, при котором висячий дефис перед `и`, `или`, `либо` или запятой остается дефисом (`двух- и трёхкомнатные`, `сорока-, пятидесятилетние`), а тире реплики, набранное дефисом, - тире (`- Ушли, - сказал он`).

=== "Код"

    ``` python
    from ruts.basic_stats import count_punctuations

    text = "Кот — «зверь»... Пёс, конечно, - друг; а кто-то (тот, что ещё жив) — нет!"
    {kind: count for kind, count in count_punctuations(text).items() if count}
    ```

=== "Результат"

    ```
    {'comma': 3,
     'exclamation': 1,
     'ellipsis': 1,
     'semicolon': 1,
     'dash': 3,
     'hyphen': 1,
     'angle_quotes': 2,
     'parentheses': 2}
    ```

## Тире, набранные дефисами { #dash_pattern }

<!-- core: stats/basic_stats.md:dash_pattern 9d635ac -->
``` {.python .signature}
dash_pattern(conjunctions=(), hanging_before_comma=False)
```

Строит `dash_pattern` для `count_punctuations`. Висячий дефис, приклеенный к букве или цифре и отнесенный к следующему слову (`до- и послевоенный`, `5- и 10-летний`), остается дефисом перед пробелами строки и одним из союзов `conjunctions` без учета регистра, а с `hanging_before_comma` - и перед запятой (`двух-, трех- и четырехлетний`). Язык, в диалоге которого строку закрывает дефис перед запятой (`-Come -he said-, and left`), оставляет `hanging_before_comma` выключенным. Без параметров шаблон - `DASH_PATTERN`.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `conjunctions` | `Collection[str]` | `()` | Союзы после висячего дефиса |
| `hanging_before_comma` | `bool` | `False` | Считать дефис между буквой и запятой висячим |

Союзы, которые не набор строк, дают `SourceTypeError`, а пустой союз - `ParameterError`.

Без параметров получается `DASH_PATTERN` ядра (`anyts.basic_stats`), а `DASH_PATTERN` модуля `ruts.basic_stats` - `dash_pattern(("и", "или", "либо"), hanging_before_comma=True)`.

=== "Код"

    ``` python
    from ruts.basic_stats import count_punctuations, dash_pattern

    text = "Двух- и трёхкомнатные, сорока-, пятидесятилетние - сказал он"
    counts = count_punctuations(text)
    counts["dash"], counts["hyphen"]
    counts = count_punctuations(text, dash_pattern=dash_pattern())
    counts["dash"], counts["hyphen"]
    ```

=== "Результат"

    ```
    (1, 2)
    (3, 0)
    ```

## Профиль пунктуации { #punctuation }

``` {.python .signature}
punctuation_profile(text, n_words=None)
```

Частоты знаков препинания по типам (`count_punctuations`) на 1000 слов и `yo_share` - доля буквы ё среди букв е и ё, то есть пишет ли автор ё. Без слов или без букв е и ё значения - `nan`. Текст, который не строка, дает `SourceTypeError`, количество слов, которое не целое неотрицательное число, - `ParameterError`.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `str` | - | Строка текста |
| `n_words` | `int` | `None` | Количество слов; без него слова извлекает `WordsExtractor` |

Профиль - редакторский и стилометрический признак: у Чехова многоточий и восклицаний в разы больше, чем у Толстого (см. [сравнение корпусов](../corpus/compare.md)). Он зависит от оформления текста - типографских кавычек и тире, буквы ё - и легко подделывается, поэтому его стоит смотреть отдельно от лингвистических признаков.

=== "Код"

    ``` python
    from ruts.basic_stats import punctuation_profile

    text = "Кот — «зверь»... Пёс, конечно, - друг; а кто-то (тот, что ещё жив) — нет!"
    profile = punctuation_profile(text)
    round(profile["dash"], 1), round(profile["yo_share"], 2)
    ```

=== "Результат"

    ```
    (250.0, 0.33)
    ```
