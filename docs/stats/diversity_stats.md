# Метрики лексического разнообразия

!!! info ""
    **ruts.diversity_stats.DiversityStats**

## Описание

<!-- core: stats/diversity_stats.md:DiversityStats 2e4dbf8 -->
Класс для вычисления основных метрик [лексического разнообразия](https://ru.wikipedia.org/wiki/%D0%9A%D0%BE%D1%8D%D1%84%D1%84%D0%B8%D1%86%D0%B8%D0%B5%D0%BD%D1%82_%D0%BB%D0%B5%D0%BA%D1%81%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%B3%D0%BE_%D1%80%D0%B0%D0%B7%D0%BD%D0%BE%D0%BE%D0%B1%D1%80%D0%B0%D0%B7%D0%B8%D1%8F) текста по его словам.

!!! note "Примечание"
    Вычисление метрик происходит посредством вызова соответствующего атрибута или метода `get_stats` объекта класса `DiversityStats`.

## Языковые крючки

Класс расширяет `DiversityStats` ядра [anyTS](https://sergeyshk.github.io/anyTS/stats/diversity_stats/): вместо списка слов он принимает текст или объект `Doc` библиотеки [spaCy](https://github.com/explosion/spaCy). Слова текста извлекает русский [`WordsExtractor`](../extractors/words.md) или заданный экстрактор, который для `Doc` применяется к его тексту; без экстрактора слова `Doc` берутся из его токенов, а части дефисного слова, разрезанного spaCy, склеиваются (`во-первых` - одно слово). Слова всегда приводятся к нижнему регистру. Таблица `print_stats` выводится с русскими заголовками и русскими описаниями метрик из `ruts.constants.DIVERSITY_STATS_DESC`.

## Параметры

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `source` | str/Doc | `-` | Источник данных (строка или объект Doc) |
| `words_extractor` | WordsExtractor | `None` | Инструмент для извлечения слов; для Doc применяется к его тексту, если задан |
| `window_len` | int | `50` | Размер окна для MATTR и сегмента для MSTTR |
| `mtld_threshold` | float | `0.72` | Порог TTR для MTLD, MA-MTLD и MTLD-W |
| `mtld_min_len` | int | `10` | Минимальная длина фактора для MTLD, MA-MTLD и MTLD-W |
| `hdd_sample_size` | int | `42` | Размер выборки для HD-D |
| `log_base` | float | `10` | Основание логарифма для метрик Summer, Maas и Dugast |

<!-- core: stats/diversity_stats.md:check_params 1ed1a29 -->
Параметры проверяет `check_params(window_len, mtld_threshold, mtld_min_len, hdd_sample_size, log_base)`: окно, размер выборки или минимальная длина фактора вне допустимых значений, порог вне интервала (0, 1) и основание логарифма не больше 1 дают `ParameterError`. Проверка выполняется до извлечения слов, поэтому о неверном параметре она сообщает раньше, чем о пустом тексте.

## Соглашения { #conventions }

<!-- core: stats/diversity_stats.md:DiversityStats-conventions a759359 -->
Значения части метрик зависят от соглашений, которые в разных библиотеках различаются. Все они, кроме сравнения с порогом MTLD, вынесены в параметры класса:

| Параметр | По умолчанию | Другие библиотеки |
| :------: | :----------: | :---------------: |
| Основание логарифма для Summer, Maas, Dugast's U и Dugast's k | 10 | LexicalRichness, textcomplexity и zipfR - натуральный |
| Окно MATTR и сегмент MSTTR | 50 | quanteda и koRpus - 100 |
| Порог TTR для MTLD | 0.72 | в литературе 0.66-0.75 |
| Сравнение с порогом MTLD | фактор закрывается при TTR ≤ 0.72 (McCarthy & Jarvis, 2010) | lexical-diversity и TAALED - строгое `<`; значения расходятся, когда TTR попадает ровно в порог |
| Минимальная длина фактора MTLD | 10 | koRpus применяет ее только к MTLD-MA и отбрасывает более короткие факторы, а не продлевает их, LexicalRichness и textcomplexity не применяют |
| Размер выборки HD-D | 42 | в литературе 35-50 |

По Zenker и Kyle (2021) MATTR, MTLD и HD-D стабильны на текстах от 50-200 слов, MTLD-W, MA-MTLD и Maas нестабильны на коротких текстах, семейство TTR не стабилизируется вовсе. Для сравнения текстов разной длины используйте [оконный расчет](#windowed) с доверительными интервалами.

## Атрибуты

<!-- core: stats/diversity_stats.md:DiversityStats-attributes 2bd9615 -->
| Атрибут | Тип | Описание |
| :-----: | :-: | :------: |
| `words` | tuple[str] | Кортеж слов |
| `window_len`, `mtld_threshold`, `mtld_min_len`, `hdd_sample_size`, `log_base` | int/float | Параметры метрик; их изменение у объекта меняет метрики |
| `frequency_spectrum` | dict[int, int] | Спектр частот - количество лексем с заданной частотой |
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
| `mamtld` | float | Метрика Moving Average Measure of Textual Lexical Diversity (MA-MTLD) |
| `mtldw` | float | Метрика MTLD со скользящим окном и заворотом текста (MTLD-W) |
| `hdd` | float | Метрика Hypergeometric Distribution D (HD-D) |
| `simpson_index` | float | Индекс Симпсона (D) |
| `inverse_simpson_index` | float | Обратный индекс Симпсона (1/D) |
| `gini_simpson_index` | float | Индекс Джини-Симпсона (1-D) |
| `hapax_index` | float | Гапакс-индекс, он же Honoré's R |
| `honore_r` | float | Псевдоним для гапакс-индекса |
| `yule_k` | float | Характеристика Юла (Yule's K) |
| `yule_i` | float | Обратная характеристика Юла (Yule's I) |
| `herdan_vm` | float | Мера Хердана (Herdan's Vm) |
| `sichel_s` | float | Мера Сишела (Sichel's S) |
| `michea_m` | float | Мера Мишеа (Michéa's M) |
| `brunet_w` | float | Мера Брюне (Brunet's W) |
| `dugast_k` | float | Мера Дюга (Dugast's k) |
| `baayen_p` | float | Мера Баайена (Baayen's P) |
| `hapax_ratio` | float | Доля гапаксов среди лексем |
| `alpha2` | float | Показатель α₂ |
| `entropy` | float | Энтропия Шеннона в битах |
| `evenness` | float | Выравненность - отношение энтропии к максимальной |
| `perplexity` | float | Перплексия |
| `zipf_alpha` | float | Наклон закона Ципфа |
| `heaps_beta` | float | Показатель закона Хипса |

!!! note "Примечание"
    Каждую метрику можно вычислить и ее функцией; метрики и их функции описаны в соответствующем [разделе](diversity_stats_funcs.md).

## Методы

### windowed

<!-- core: stats/diversity_stats.md:DiversityStats-windowed af6a479 -->
Оконный расчет метрики по ее названию, как в [`calc_windowed`](diversity_stats_funcs.md#calc_windowed): значение по последовательным окнам текста одинаковой длины, среднее, выборочное стандартное отклонение и доверительный интервал среднего по распределению Стьюдента. Краевые случаи (короткие тексты, значения `nan` и бесконечные значения) описаны там.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `stat` | str | `-` | Название метрики из `get_stats` |
| `window_len` | int | `100` | Размер окна |
| `step` | int | `None` | Шаг окна, по умолчанию равен размеру окна (окна не пересекаются) |
| `confidence` | float | `0.95` | Уровень доверия |

Возвращает именованный кортеж `WindowStats` с полями `mean`, `std`, `lower`, `upper` и `n_windows`. Неизвестное название метрики дает `UnknownStatError`.

!!! example "Пример"

    ``` python
    from ruts import DiversityStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    ds = DiversityStats(text)
    ds.windowed("ttr", window_len=5)
    # WindowStats(mean=0.9333333333333332, std=0.11547005383792512, lower=0.6464898180167025, upper=1.220176848649964, n_windows=3)
    ds.windowed("ttr", window_len=5, step=2).n_windows
    # 6
    ```

### get_stats

<!-- core: stats/diversity_stats.md:DiversityStats-get_stats b65013e -->
Возвращает справочник с вычисленными метриками лексического разнообразия.

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
    {'ttr': 0.7333333333333333,
    'rttr': 2.840187787218772,
    'cttr': 2.008316044185609,
    'httr': 0.8854692840710255,
    'sttr': 0.2500605793160848,
    'mttr': 0.09738250756232528,
    'dttr': 10.268784661968118,
    'mattr': 0.7333333333333333,
    'msttr': 0.7333333333333333,
    'mtld': 15.0,
    'mamtld': 12.0,
    'mtldw': 13.25,
    'hdd': nan,
    'simpson_index': 0.047619047619047616,
    'inverse_simpson_index': 21.0,
    'gini_simpson_index': 0.9523809523809523,
    'hapax_index': 992.9517404041437,
    'yule_k': 444.44444444444446,
    'yule_i': 8.642857142857142,
    'herdan_vm': 0.1421338109037403,
    'sichel_s': 0.18181818181818182,
    'michea_m': 5.5,
    'brunet_w': 6.00637847898991,
    'dugast_k': 14.783895126869226,
    'baayen_p': 0.5333333333333333,
    'hapax_ratio': 0.7272727272727273,
    'alpha2': 0.5,
    'entropy': 3.3232314287976203,
    'evenness': 0.9606293157795304,
    'perplexity': 10.009038104159247,
    'zipf_alpha': 0.4884512334695912,
    'heaps_beta': 0.8366147342060046}
    ```

### print_stats

<!-- core: stats/diversity_stats.md:DiversityStats-print_stats be91444 -->
Выводит таблицу с вычисленными метриками лексического разнообразия, их описаниями из `stats_desc` и заголовками из `stats_headers`.

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
                                      Метрика                                  | Значение
    -------------------------------------------------------------------------------------
    Type-Token Ratio (TTR)                                                     |   0.73
    Root Type-Token Ratio (RTTR)                                               |   2.84
    Corrected Type-Token Ratio (CTTR)                                          |   2.01
    Herdan Type-Token Ratio (HTTR)                                             |   0.89
    Summer Type-Token Ratio (STTR)                                             |   0.25
    Maas Type-Token Ratio (MTTR)                                               |   0.10
    Dugast Type-Token Ratio (DTTR)                                             |  10.27
    Moving Average Type-Token Ratio (MATTR)                                    |   0.73
    Mean Segmental Type-Token Ratio (MSTTR)                                    |   0.73
    Measure of Textual Lexical Diversity (MTLD)                                |  15.00
    Moving Average Measure of Textual Lexical Diversity (MA-MTLD)              |  12.00
    Moving Average Measure of Textual Lexical Diversity with Wrap (MTLD-W)     |  13.25
    Hypergeometric Distribution D (HD-D)                                       |   nan
    Индекс Симпсона (D)                                                        |   0.05
    Обратный индекс Симпсона (1/D)                                             |  21.00
    Индекс Джини-Симпсона (1-D)                                                |   0.95
    Гапакс-индекс (Honoré's R)                                                 |  992.95
    Характеристика Юла (Yule's K)                                              |  444.44
    Обратная характеристика Юла (Yule's I)                                     |   8.64
    Мера Хердана (Herdan's Vm)                                                 |   0.14
    Мера Сишела (Sichel's S)                                                   |   0.18
    Мера Мишеа (Michéa's M)                                                    |   5.50
    Мера Брюне (Brunet's W)                                                    |   6.01
    Мера Дюга (Dugast's k)                                                     |  14.78
    Мера Баайена (Baayen's P)                                                  |   0.53
    Доля гапаксов                                                              |   0.73
    Показатель α₂                                                              |   0.50
    Энтропия Шеннона (бит)                                                     |   3.32
    Выравненность                                                              |   0.96
    Перплексия                                                                 |  10.01
    Наклон закона Ципфа (α)                                                    |   0.49
    Показатель закона Хипса (β)                                                |   0.84
    ```
