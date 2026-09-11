# Метрики лексического разнообразия

!!! info ""
    **ruts.diversity_stats.DiversityStats**

## Описание

Модуль для вычисления основных метрик [лексического разнообразия](https://ru.wikipedia.org/wiki/%D0%9A%D0%BE%D1%8D%D1%84%D1%84%D0%B8%D1%86%D0%B8%D0%B5%D0%BD%D1%82_%D0%BB%D0%B5%D0%BA%D1%81%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%B3%D0%BE_%D1%80%D0%B0%D0%B7%D0%BD%D0%BE%D0%BE%D0%B1%D1%80%D0%B0%D0%B7%D0%B8%D1%8F) текста. В качестве источника данных может использоваться как непосредственно текст, так и объект класса `Doc` библиотеки [spaCy](https://github.com/explosion/spaCy).

В модуле реализована возможность использования предварительно созданного объекта класса [`WordsExtractor`](../extractors/words.md) для проведения необходимой токенизации слов перед вычислением статистик.

!!! note "Примечание"
    Вычисление метрик происходит посредством вызова соответствующего атрибута или метода `get_stats` объекта класса `DiversityStats`.

## Параметры

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `source` | str/Doc | `-` | Источник данных (строка или объект Doc) |
| `words_extractor` | WordsExtractor | `None` | Инструмент для извлечения слов |

## Атрибуты

| Атрибут | Тип | Описание |
| :-----: | :-: | :------: |
| `ttr` | float | Метрика Type-Token Ratio (TTR) |
| `rttr` | float | Метрика Root Type-Token Ratio (RTTR) |
| `cttr` | float | Метрика Corrected Type-Token Ratio (CTTR) |
| `httr` | float | Метрика Herdan Type-Token Ratio (HTTR) |
| `sttr` | float | Метрика Summer Type-Token Ratio (STTR) |
| `mttr` | float | Метрика Maas Type-Token Ratio (MTTR) |
| `dttr` | float | Метрика Dugast Type-Token Ratio (DTTR) |
| `mattr` | float | Метрика Moving Average Type-Token Ratio (MATTR) |
| `msttr` | float | Метрика Mean Segmental Type-Token Ratio (MSTTR) |
| `mtld` | float | Метрика Measure of Textual Lexical Diversity (MTLD) |
| `mamtld` | float | Метрика Moving Average Measure of Textual Lexical Diversity (MTLD) |
| `hdd` | float | Метрика Hypergeometric Distribution D (HD-D) |
| `simpson_index` | float | Индекс Симпсона (D) |
| `inverse_simpson_index` | float | Обратный индекс Симпсона (1/D) |
| `gini_simpson_index` | float | Индекс Джини-Симпсона (1-D) |
| `hapax_index` | float | Гапакс-индекс, он же Honoré's R |
| `honore_r` | float | Псевдоним для гапакс-индекса |

!!! note "Примечание"
    Каждую метрику можно вычислить отдельно, выполнив соответствующую функцию. Подробную информацию о метриках лексического разнообразия и функциях, используемых для их вычисления, можно узнать в соответствующем [разделе](diversity_stats_funcs.md).

## Методы

### get_stats

Возвращает справочник с вычисленными метриками лексического разнообразия текста.

Рассмотрим пример вычисления метрик лексического разнообразия текста:

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    from ruts import DiversityStats

    # Подготовка данных
    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"

    # Вычисление метрик
    ds = DiversityStats(text)
    ds.get_stats()
    ```

    _Результат_:

    ``` bash
    {'cttr': 2.008316044185609,
    'dttr': 10.268784661968121,
    'gini_simpson_index': 0.9523809523809523,
    'hapax_index': 992.9517404041437,
    'hdd': nan,
    'httr': 0.8854692840710255,
    'inverse_simpson_index': 21.0,
    'mamtld': 11.875,
    'mattr': 0.7333333333333333,
    'msttr': 0.7333333333333333,
    'mtld': 15.0,
    'mttr': 0.09738250756232525,
    'rttr': 2.840187787218772,
    'simpson_index': 0.047619047619047616,
    'sttr': 0.25006057931608583,
    'ttr': 0.7333333333333333}
    ```

### print_stats

Выводит на экран таблицу с вычисленными метриками лексического разнообразия текста.

Для иллюстрации работы метода воспользуемся кодом из предыдущего примера:

!!! example "Пример"

    _Код_:

    ``` python
    ...

    # Отображение таблицы вычисленных метрик
    ds.print_stats()
    ```

    _Результат_:

    ``` bash
                            Метрика                             | Значение
    ----------------------------------------------------------------------
    Type-Token Ratio (TTR)                                      |   0.73
    Root Type-Token Ratio (RTTR)                                |   2.84
    Corrected Type-Token Ratio (CTTR)                           |   2.01
    Herdan Type-Token Ratio (HTTR)                              |   0.89
    Summer Type-Token Ratio (STTR)                              |   0.25
    Maas Type-Token Ratio (MTTR)                                |   0.10
    Dugast Type-Token Ratio (DTTR)                              |  10.27
    Moving Average Type-Token Ratio (MATTR)                     |   0.73
    Mean Segmental Type-Token Ratio (MSTTR)                     |   0.73
    Measure of Textual Lexical Diversity (MTLD)                 |  15.00
    Moving Average Measure of Textual Lexical Diversity (MTLD)  |  11.88
    Hypergeometric Distribution D (HD-D)                        |   nan
    Индекс Симпсона (D)                                         |   0.05
    Обратный индекс Симпсона (1/D)                              |  21.00
    Индекс Джини-Симпсона (1-D)                                 |   0.95
    Гапакс-индекс (Honoré's R)                                  |  992.95
    ```
