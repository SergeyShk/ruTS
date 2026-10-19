# SEO-метрики стиля

!!! info ""
    **ruts.style_stats.StyleStats**

## Описание

<!-- core: stats/style_stats.md:StyleStats 5f3bc42 -->
Метрики стиля текста: SEO-метрики Advego и Text.ru - классическая и академическая тошнота, водность, заспамленность, естественность по закону Ципфа и плотность ключевых слов - и маркеры канцелярита: отглагольные существительные, производные предлоги, вводные слова и штампы. Формулы сервисов не опубликованы, поэтому взяты общепринятые определения, как их дают функции метрик. Источник данных - текст или объект `Doc` библиотеки [spaCy](https://github.com/explosion/spaCy).

SEO-метрики считаются по словам экстрактора слов, по умолчанию в нижнем регистре, или по токенам `Doc`; явно переданный экстрактор применяется к тексту `Doc`. Маркеры считаются по словоформам в нижнем регистре (`forms`) независимо от экстрактора.

Источник, который не строка и не `Doc`, экстрактор другого типа и список, который не список строк, дают `SourceTypeError`, источник без слов - `SourceError`, `top_n`, который не целое число не меньше единицы, - `ParameterError`.

Определения и формулы метрик - в разделе [функций](style_stats_funcs.md). Слова по умолчанию не лемматизируются, поэтому формы одного слова считаются разными словами, как в Advego; для расчета по леммам передайте объект [`WordsExtractor`](../extractors/words.md) с параметрами `use_lexemes=True` и `lowercase=True`.

## Языковые крючки

Класс расширяет `StyleStats` ядра [anyTS](https://sergeyshk.github.io/anyTS/stats/style_stats/) крючками русского языка: слова строки извлекает русский [`WordsExtractor`](../extractors/words.md), стоп-слова академической тошноты и слова «воды» определяются по части речи с помощью pymorphy3 ([`is_stopword`](style_stats_funcs.md#is_stopword), [`is_water_word`](style_stats_funcs.md#is_water_word)), одиночные вводные слова - по граммеме `Prnt` pymorphy3 ([`is_parenthetical`](style_stats_funcs.md#calc_parentheticals)), существительные и их леммы - по pymorphy3, отглагольные среди них - по `is_verbal_noun` ([`calc_verbal_nouns`](style_stats_funcs.md#calc_verbal_nouns)). Переданные списки слов и словосочетания сравниваются без буквы ё (`normalize_yo`), а словосочетание находится в любой форме своего глагола ([`expand_phrases`](style_stats_funcs.md#calc_phrase_density)). Списки словосочетаний - `COMPOUND_PREPOSITIONS`, `PARENTHETICALS` и `OFFICIALESE_CLICHES` из `ruts.constants`, нормы сервисов - `STYLE_NORMS` ([ниже](#norms)); таблица `print_stats` выводится с русскими заголовками и описаниями из `STYLE_STATS_DESC`, сообщения об ошибках - по-русски (`CORE_MESSAGES`). Слова `Doc` берутся без знаков ударения, а части дефисного слова, разрезанного spaCy, склеиваются (`во-первых` - одно слово).

## Параметры

<!-- core: stats/style_stats.md:StyleStats-parameters c25a31b -->
| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `source` | str/Doc | `-` | Источник данных |
| `words_extractor` | WordsExtractor | `None` | Инструмент для извлечения слов; применяется и к `Doc`, к его тексту |
| `stopwords` | list[str] | `None` | Слова «воды»; без них решает `is_water_word` |
| `top_n` | int | `10` | Количество самых частых слов академической тошноты и естественности по закону Ципфа (`NAUSEA_TOP_N`) |
| `cliches` | list[str] | `None` | Штампы; по умолчанию `cliches_list` класса |
| `nausea_stopwords` | list[str] | `None` | Стоп-слова академической тошноты; без них решает `is_stopword` |

Множество слов берется в отсортированном порядке.

## Атрибуты

<!-- core: stats/style_stats.md:StyleStats-attributes e6af723 -->
| Атрибут | Тип | Описание |
| :-----: | :-: | :------: |
| `words` | tuple[str] | Слова SEO-метрик |
| `forms` | tuple[str] | Словоформы в нижнем регистре, по ним считаются маркеры |
| `classic_nausea` | float | Классическая тошнота |
| `academic_nausea` | float | Академическая тошнота в процентах |
| `water` | float | Водность в процентах |
| `spam` | float | Заспамленность в процентах |
| `zipf_naturalness` | float | Естественность по закону Ципфа в процентах |
| `verbal_nouns` | float | Доля отглагольных существительных среди существительных в процентах |
| `compound_prepositions` | float | Производных предлогов на 100 слов |
| `parentheticals` | float | Вводных слов на 100 слов |
| `cliches` | float | Штампов на 100 слов |

Метрики - свойства, которые вычисляются при каждом обращении. Вводное слово - словосочетание из `parentheticals_list` или слово `is_parenthetical` вне этих словосочетаний; словосочетания трех списков находятся вместе с их вариантами (`expand_phrases`).

## Нормы сервисов { #norms }

Метод [`describe`](#describe) читает метрику по полосам норм [Advego](https://advego.com/text/seo/), [Text.ru](https://text.ru/seo), pr-cy и megaindex; у маркеров канцелярита норм нет. Нормы - ориентиры сервисов для текстов сайтов в несколько сотен слов: на коротких текстах значения тошноты и заспамленности неинформативны, к художественной прозе нормы неприменимы.

| Метрика | Значение | Прочтение |
| :-----: | :------: | :-------: |
| `classic_nausea` | `(7; ∞)` | выше нормы Advego |
| `classic_nausea` | `(5; 7]` | у верхней границы нормы Advego |
| `classic_nausea` | `[0; 5]` | норма Advego |
| `academic_nausea` | `(15; 100]` | выше нормы Advego |
| `academic_nausea` | `[5; 15]` | норма Advego |
| `academic_nausea` | `[0; 5)` | ниже нормы Advego |
| `water` | `(30; 100]` | высокая водность по Text.ru |
| `water` | `[15; 30]` | избыточная водность по Text.ru |
| `water` | `[0; 15)` | естественная водность по Text.ru |
| `spam` | `(60; 100]` | заспамленный текст по Text.ru |
| `spam` | `[30; 60]` | SEO-оптимизированный текст по Text.ru |
| `spam` | `[0; 30)` | естественный текст по Text.ru |
| `zipf_naturalness` | `[50; 100]` | норма pr-cy и megaindex |
| `zipf_naturalness` | `[0; 50)` | ниже нормы pr-cy и megaindex |

## Методы

### keyword_density, nausea_words

<!-- core: stats/style_stats.md:StyleStats-keyword_density 5d9b0bc -->
`keyword_density(*keywords)` дает плотность ключевых слов и фраз в процентах (`calc_keyword_density` с `normalize` класса), `nausea_words()` - самые частые значимые слова академической тошноты с числом вхождений (`find_nausea_words`).

!!! example "Пример"

    ``` python
    from ruts import StyleStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    StyleStats(text).keyword_density("когда", "нет а")
    # {'когда': 20.0, 'нет а': 13.333333333333334}

    text = "Кот ловит мышей, кот спит, а мыши бегают вокруг кота"
    StyleStats(text, top_n=2).nausea_words()
    # {'кот': 2, 'ловит': 1}
    ```

### markers

<!-- core: stats/style_stats.md:StyleStats-markers 2e8c1de -->
Возвращает найденные маркеры канцелярита по метрикам - `verbal_nouns`, `compound_prepositions`, `parentheticals`, `cliches` - так, как они записаны в словоформах, в порядке текста.

!!! example "Пример"

    ``` python
    from ruts import StyleStats

    text = "В целях повышения качества в кратчайшие сроки, как правило, проводится проверка"
    StyleStats(text).markers()
    # {'verbal_nouns': ('повышения',),
    #  'compound_prepositions': ('в целях',),
    #  'parentheticals': ('как правило',),
    #  'cliches': ('в кратчайшие сроки',)}
    ```

### describe

<!-- core: stats/stats.md:Stats-describe 82d29b7 -->
Возвращает полосу шкалы статистики (`level_scale`) и `None` для статистики без шкалы, с неопределенным значением (nan) или для ключа плоских статистик (`get_stats(flat=True)`). Имя, которого нет ни в `stat_names`, ни среди открытых свойств класса, дает `UnknownStatError`.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `stat` | str | `-` | Название статистики |

!!! example "Пример"

    ``` python
    from ruts import StyleStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    ss = StyleStats(text)
    ss.describe("water")
    # 'высокая водность по Text.ru'
    ss.describe("cliches")
    # None
    ```

### get_stats

Возвращает справочник с вычисленными метриками стиля текста.

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    from ruts import StyleStats

    # Подготовка данных
    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"

    # Вычисление метрик
    ss = StyleStats(text)
    ss.get_stats()
    ```

    _Результат_:

    ``` bash
    {'classic_nausea': 1.7320508075688772,
    'academic_nausea': 53.333333333333336,
    'water': 33.333333333333336,
    'spam': 26.666666666666668,
    'zipf_naturalness': 33.333333333333336,
    'verbal_nouns': 0.0,
    'compound_prepositions': 0.0,
    'parentheticals': 0.0,
    'cliches': 0.0}
    ```

### to_dataframe

Возвращает вычисленные метрики как таблицу `pandas.DataFrame` из одной строки со столбцом на каждую метрику.

### print_stats

<!-- core: stats/stats.md:Stats-print_stats d798c21 -->
Выводит таблицу статистик из `stats_desc` с их описаниями под заголовками из `stats_headers`, дробные числа - с двумя знаками после запятой; каждый столбец шириной в свой самый длинный текст.

Для иллюстрации работы метода воспользуемся кодом из примера `get_stats`:

!!! example "Пример"

    _Код_:

    ``` python
    ...

    # Отображение таблицы вычисленных метрик
    ss.print_stats()
    ```

    _Результат_:

    ``` bash
                         Метрика                     | Значение
    ------------------------------------------------------------
    Классическая тошнота                             |   1.73
    Академическая тошнота (%)                        |  53.33
    Водность (%)                                     |  33.33
    Заспамленность (%)                               |  26.67
    Естественность по Ципфу (%)                      |  33.33
    Отглагольные существительные (% существительных) |   0.00
    Производные предлоги (на 100 слов)               |   0.00
    Вводные слова (на 100 слов)                      |   0.00
    Штампы (на 100 слов)                             |   0.00
    ```
