# Метрики лексического разнообразия

``` {.python .signature}
DiversityStats(source, words_extractor=None, window_len=50, mtld_threshold=0.72, mtld_min_len=10, hdd_sample_size=42, log_base=10)
```

<!-- core: stats/diversity_stats.md:DiversityStats 62610fe -->
Основные метрики [лексического разнообразия](https://ru.wikipedia.org/wiki/%D0%9A%D0%BE%D1%8D%D1%84%D1%84%D0%B8%D1%86%D0%B8%D0%B5%D0%BD%D1%82_%D0%BB%D0%B5%D0%BA%D1%81%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%B3%D0%BE_%D1%80%D0%B0%D0%B7%D0%BD%D0%BE%D0%BE%D0%B1%D1%80%D0%B0%D0%B7%D0%B8%D1%8F) текста, вычисляемые по его словам.

Исключения:

- `SourceTypeError` - источник, который не строка и не `Doc`, экстрактор другого типа;
- `SourceError` - источник без слов;
- `ParameterError` - параметр, который отвергает `check_params`.

Класс расширяет `DiversityStats` ядра [anyTS](https://sergeyshk.github.io/anyTS/stats/diversity_stats/): вместо списка слов он принимает текст или объект `Doc` библиотеки [spaCy](https://github.com/explosion/spaCy). Слова текста извлекает русский [`WordsExtractor`](../extractors/words.md) или заданный экстрактор, который для `Doc` применяется к его тексту; без экстрактора слова `Doc` берутся из его токенов без знаков ударения, а части дефисного слова, разрезанного spaCy, склеиваются (`во-первых` - одно слово). Слова всегда приводятся к нижнему регистру. Таблица `print_stats` выводится с русскими заголовками и русскими описаниями метрик из `ruts.constants.DIVERSITY_STATS_DESC`, а сообщения об ошибках - по-русски, из `ruts.constants.CORE_MESSAGES`.

=== "Код"

    ``` python
    from ruts import DiversityStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    ds = DiversityStats(text)
    ds.print_stats()
    ```

=== "Результат"

    ```
                                    Метрика                                | Значение
    ----------------------------------------------------------------------------------
    Type-Token Ratio (TTR)                                                 |   0.73
    Root Type-Token Ratio (RTTR)                                           |   2.84
    Corrected Type-Token Ratio (CTTR)                                      |   2.01
    Herdan Type-Token Ratio (HTTR)                                         |   0.89
    Summer Type-Token Ratio (STTR)                                         |   0.25
    Maas Type-Token Ratio (MTTR)                                           |   0.10
    Dugast Type-Token Ratio (DTTR)                                         |  10.27
    Moving Average Type-Token Ratio (MATTR)                                |   0.73
    Mean Segmental Type-Token Ratio (MSTTR)                                |   0.73
    Measure of Textual Lexical Diversity (MTLD)                            |  15.00
    Moving Average Measure of Textual Lexical Diversity (MA-MTLD)          |  12.00
    Moving Average Measure of Textual Lexical Diversity with Wrap (MTLD-W) |  13.25
    Hypergeometric Distribution D (HD-D)                                   |   nan
    Индекс Симпсона (D)                                                    |   0.05
    Обратный индекс Симпсона (1/D)                                         |  21.00
    Индекс Джини-Симпсона (1-D)                                            |   0.95
    Гапакс-индекс (Honoré's R)                                             |  992.95
    Характеристика Юла (Yule's K)                                          |  444.44
    Обратная характеристика Юла (Yule's I)                                 |   8.64
    Мера Хердана (Herdan's Vm)                                             |   0.14
    Мера Сишела (Sichel's S)                                               |   0.18
    Мера Мишеа (Michéa's M)                                                |   5.50
    Мера Брюне (Brunet's W)                                                |   6.01
    Мера Дюга (Dugast's k)                                                 |  14.78
    Мера Баайена (Baayen's P)                                              |   0.53
    Доля гапаксов                                                          |   0.73
    Показатель α₂                                                          |   0.50
    Энтропия Шеннона (бит)                                                 |   3.32
    Выравненность                                                          |   0.96
    Перплексия                                                             |  10.01
    Наклон закона Ципфа (α)                                                |   0.49
    Показатель закона Хипса (β)                                            |   0.84
    ```

## Параметры

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `source` | `str` / `Doc` | - | Источник данных |
| `words_extractor` | `WordsExtractor` | `None` | Инструмент для извлечения слов; для `Doc` применяется к его тексту |
| `window_len` | `int` | `50` | Размер окна для MATTR и сегмента для MSTTR (`MATTR_WINDOW_LEN`) |
| `mtld_threshold` | `float` | `0.72` | Порог TTR для MTLD, MA-MTLD и MTLD-W (`MTLD_TTR_THRESHOLD`) |
| `mtld_min_len` | `int` | `10` | Минимальная длина фактора для MTLD, MA-MTLD и MTLD-W (`MTLD_MIN_LEN`) |
| `hdd_sample_size` | `int` | `42` | Размер выборки для HD-D (`HDD_SAMPLE_SIZE`) |
| `log_base` | `float` | `10` | Основание логарифма для метрик Summer, Maas и Dugast (`DIVERSITY_LOG_BASE`) |

Константы умолчаний в скобках, здесь и в карточках, - из `anyts.constants`.

<!-- core: stats/diversity_stats.md:DiversityStats-attributes 2e73f9a -->
Объект хранит слова в `words`, кортежем, и пять параметров под их именами, изменяемые у объекта. `frequency_spectrum` - спектр частот слов (`calc_frequency_spectrum`), а `honore_r` - псевдоним `hapax_index`.

``` {.python .signature}
check_params(window_len=50, mtld_threshold=0.72, mtld_min_len=10, hdd_sample_size=42, log_base=10, *, messages=CORE_MESSAGES)
```

<!-- core: stats/diversity_stats.md:check_params 84612a6 -->
Проверка параметров метрик: `window_len` или `hdd_sample_size`, которые не целое число не меньше единицы, `mtld_min_len`, который не целое неотрицательное число, `mtld_threshold`, который не число в интервале (0, 1), и `log_base`, который не конечное число больше 1, дают `ParameterError`. Проверка выполняется до извлечения слов, поэтому о неверном параметре она сообщает раньше, чем о пустом тексте.

## Соглашения { #conventions }

<!-- core: stats/diversity_stats.md:DiversityStats-conventions 22cd78d -->
Часть метрик зависит от соглашений, которые в разных библиотеках различаются. Все они, кроме сравнения с порогом MTLD, вынесены в параметры класса:

| Параметр | По умолчанию | Другие библиотеки |
| :------- | :----------- | :---------------- |
| Основание логарифма для Summer, Maas, Dugast's U и Dugast's k | `10` | LexicalRichness, textcomplexity и zipfR - натуральный |
| Окно MATTR и сегмент MSTTR | `50` | quanteda и koRpus - 100 |
| Порог TTR для MTLD | `0.72` | в литературе 0.66-0.75 |
| Сравнение с порогом MTLD | фактор закрывается при TTR ≤ 0.72 (McCarthy & Jarvis, 2010) | lexical-diversity и TAALED - строгое `<`; значения расходятся, когда TTR попадает ровно в порог |
| Минимальная длина фактора MTLD | `10` | koRpus - только в MTLD-MA, с отбрасыванием более коротких факторов вместо их продления; LexicalRichness и textcomplexity - не применяется |
| Размер выборки HD-D | `42` | в литературе 35-50 |

По Zenker и Kyle (2021) MATTR, MTLD и HD-D стабильны на текстах от 50-200 слов, MTLD-W, MA-MTLD и Maas нестабильны на коротких текстах, а семейство TTR не стабилизируется вовсе. Тексты разной длины сравниваются [оконным расчетом](#windowed) с доверительными интервалами.

## Метрики

<!-- core: stats/diversity_stats.md:DiversityStats-metrics bc5ee7c -->
Каждая метрика - свойство объекта, которое вычисляется при каждом обращении функцией из ее карточки с параметрами объекта, а `get_stats` дает их все.

| Метрика | Что измеряет | Диапазон | Чем больше, тем |
| :------ | :----------- | :------- | :-------------- |
| [`ttr`](#ttr) | Доля лексем среди слов | 0-1 | богаче словарь |
| [`rttr`](#rttr) | Лексемы относительно квадратного корня из числа слов | от 0 | богаче словарь |
| [`cttr`](#cttr) | Лексемы относительно квадратного корня из удвоенного числа слов | от 0 | богаче словарь |
| [`httr`](#httr) | Лексемы относительно слов в логарифмах | 0-1 | богаче словарь |
| [`sttr`](#sttr) | Лексемы относительно слов в двойных логарифмах | до 1, `nan` для одной лексемы или текста не длиннее основания | богаче словарь |
| [`mttr`](#mttr) | Повторяемость слов в логарифмах | от 0 | беднее словарь |
| [`dttr`](#dttr) | Обратная величина к метрике Maas | от 0, `inf` без повторяющихся слов | богаче словарь |
| [`mattr`](#mattr) | Средний TTR скользящего окна | 0-1 | богаче словарь |
| [`msttr`](#msttr) | Средний TTR последовательных сегментов | 0-1 | богаче словарь |
| [`mtld`](#mtld) | Слов на фактор - отрезок, на котором TTR опускается до порога | больше 0, `inf` без повторяющихся слов | богаче словарь |
| [`mamtld`](#mamtld) | Средняя длина факторов, начинающихся с каждого слова | до числа слов, `nan`, если ни один фактор не завершен | богаче словарь |
| [`mtldw`](#mtldw) | Средняя длина факторов, начинающихся с каждого слова, с заворотом текста | до числа слов, `nan`, если ни один фактор не завершен | богаче словарь |
| [`hdd`](#hdd) | Ожидаемый TTR случайной выборки | 0-1, `nan` для текста короче 50 слов или размера выборки | богаче словарь |
| [`simpson_index`](#simpson_index) | Вероятность того, что два слова - одна лексема | 0-1, `nan` для текста короче двух слов | беднее словарь |
| [`inverse_simpson_index`](#inverse_simpson_index) | Эффективное число лексем второго порядка | от 1, `inf` без повторяющихся слов, `nan` для текста короче двух слов | богаче словарь |
| [`gini_simpson_index`](#gini_simpson_index) | Вероятность того, что два слова - разные лексемы | 0-1, `nan` для текста короче двух слов | богаче словарь |
| [`hapax_index`](#hapax_index) | Доля гапаксов среди лексем относительно длины текста | от 0, `inf` без повторяющихся слов, `nan` для текста короче двух слов | богаче словарь |
| [`yule_k`](#yule_k) | Повторяемость слов | 0-10 000, `nan` для текста короче двух слов | беднее словарь |
| [`yule_i`](#yule_i) | Величина, обратная Yule's K | больше 0, `inf` без повторяющихся слов, `nan` для текста короче двух слов | богаче словарь |
| [`herdan_vm`](#herdan_vm) | Неравномерность частот | 0-1, `nan` для текста короче двух слов | беднее словарь |
| [`sichel_s`](#sichel_s) | Доля дислегоменов среди лексем | 0-1 | больше лексем, встретившихся дважды |
| [`michea_m`](#michea_m) | Лексем на дислегомен | от 1, `inf` без дислегоменов | меньше лексем, встретившихся дважды |
| [`brunet_w`](#brunet_w) | Слова относительно лексем | от 1 до числа слов | беднее словарь |
| [`dugast_k`](#dugast_k) | Лексемы относительно слов в логарифмах | от 0, `nan` для текста не длиннее основания | богаче словарь |
| [`baayen_p`](#baayen_p) | Доля гапаксов среди слов | 0-1 | быстрее растет словарь |
| [`hapax_ratio`](#hapax_ratio) | Доля гапаксов среди лексем | 0-1 | больше лексем, встретившихся один раз |
| [`alpha2`](#alpha2) | Форма нижней части спектра частот | до 1, `nan` без гапаксов | больше гапаксов относительно дислегоменов |
| [`entropy`](#entropy) | Информация на слово в битах | от 0 | богаче словарь |
| [`evenness`](#evenness) | Энтропия относительно ее максимума | 0-1, `nan` для одной лексемы | равномернее частоты |
| [`perplexity`](#perplexity) | Эффективное число лексем | от 1 до числа лексем | богаче словарь |
| [`zipf_alpha`](#zipf_alpha) | Падение частоты с рангом | от 0, `nan` для одной лексемы | быстрее падают частоты |
| [`heaps_beta`](#heaps_beta) | Рост словаря с длиной текста | от 0, `nan` для текста короче двух слов | быстрее растет словарь |

Функции и именованные кортежи карточек импортируются из `ruts.diversity_stats`.

<div class="metric-card" markdown>

### Type-Token Ratio (TTR) { #ttr }

`ttr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_ttr 4982ca2 -->
``` {.python .signature}
calc_ttr(text)
```

Самая простая мера лексического разнообразия, без поправки на длину текста.

$$
\frac{\textrm{Количество лексем}}{\textrm{Количество слов}}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Root Type-Token Ratio (RTTR) { #rttr }

`rttr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_rttr 565f2bc -->
``` {.python .signature}
calc_rttr(text)
```

Модификация метрики TTR (Guiraud, 1960).

$$
\frac{\textrm{Количество лексем}}{\sqrt{\textrm{(Количество слов)}}}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Corrected Type-Token Ratio (CTTR) { #cttr }

`cttr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_cttr 06c97ca -->
``` {.python .signature}
calc_cttr(text)
```

Модификация метрики TTR (Carroll, 1964).

$$
\frac{\textrm{Количество лексем}}{\sqrt{2\times\textrm{(Количество слов)}}}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Herdan Type-Token Ratio (HTTR) { #httr }

`httr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_httr 42487d4 -->
``` {.python .signature}
calc_httr(text)
```

Логарифмическая модификация метрики TTR (Herdan, 1960).

$$
\frac{\log_{10} {\textrm{(Количество лексем)}}}{\log_{10} {{\textrm{(Количество слов)}}}}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Summer Type-Token Ratio (STTR) { #sttr }

`sttr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_sttr 1847a8d -->
``` {.python .signature}
calc_sttr(text, base=10)
```

Логарифмическая модификация метрики TTR (Summer, 1966). Значение зависит от основания логарифма (см. [соглашения](#conventions)). Оно равно `nan` для текста из одной лексемы, где числитель не определен, и для текста не длиннее основания ($\log \log N \le 0$), в том числе для таких окон `calc_windowed`.

$$
\frac{\log_{10} {\log_{10} {\textrm{(Количество лексем)}}}}{\log_{10} {\log_{10} {{\textrm{(Количество слов)}}}}}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |
| `base` | `float` | `10` | Основание логарифма (`DIVERSITY_LOG_BASE`) |

`base`, который не конечное число больше 1, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Maas Type-Token Ratio (MTTR) { #mttr }

`mttr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_mttr 4d5f1b1 -->
``` {.python .signature}
calc_mttr(text, base=10)
```

Логарифмическая модификация метрики TTR (Maas, 1972). Значение зависит от основания логарифма (см. [соглашения](#conventions)).

$$
\frac{\log_{10} {\textrm{(Количество слов)}}-\log_{10} {\textrm{(Количество лексем)}}}{\log_{10} {{\textrm{(Количество слов)}}}^2}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |
| `base` | `float` | `10` | Основание логарифма (`DIVERSITY_LOG_BASE`) |

`base`, который не конечное число больше 1, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Dugast Type-Token Ratio (DTTR) { #dttr }

`dttr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_dttr 654db67 -->
``` {.python .signature}
calc_dttr(text, base=10)
```

Логарифмическая модификация метрики TTR (Dugast, 1978), обратная величина к метрике Maas. Значение зависит от основания логарифма (см. [соглашения](#conventions)). У текста без повторяющихся слов значение бесконечно.

$$
\frac{\log_{10} {{\textrm{(Количество слов)}}}^2}{\log_{10} {\textrm{(Количество слов)}}-\log_{10} {\textrm{(Количество лексем)}}}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |
| `base` | `float` | `10` | Основание логарифма (`DIVERSITY_LOG_BASE`) |

`base`, который не конечное число больше 1, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Moving Average Type-Token Ratio (MATTR) { #mattr }

`mattr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_mattr e57be40 -->
``` {.python .signature}
calc_mattr(text, window_len=50)
```

Модификация метрики TTR со скользящей средней (Covington & McFall, 2010), не зависящая от длины текста: окно фиксированного размера скользит по тексту, и TTR всех окон усредняется. Для текстов короче окна возвращается TTR всего текста.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |
| `window_len` | `int` | `50` | Размер окна (`MATTR_WINDOW_LEN`) |

`window_len`, который не целое число не меньше единицы, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Mean Segmental Type-Token Ratio (MSTTR) { #msttr }

`msttr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_msttr 21799ac -->
``` {.python .signature}
calc_msttr(text, segment_len=50)
```

Модификация метрики TTR с сегментированием (Johnson, 1944), не зависящая от длины текста: текст делится на сегменты фиксированного размера, и TTR всех сегментов усредняется; неполный последний сегмент отбрасывается. Для текстов короче сегмента возвращается TTR всего текста.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |
| `segment_len` | `int` | `50` | Размер сегмента (`MATTR_WINDOW_LEN`) |

`segment_len`, который не целое число не меньше единицы, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Measure of Textual Lexical Diversity (MTLD) { #mtld }

`mtld`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_mtld 427e11b -->
``` {.python .signature}
calc_mtld(text, min_len=10, threshold=0.72)
```

Модификация метрики MSTTR (McCarthy, 2005), не зависящая от длины текста: количество слов, деленное на количество факторов - отрезков, на которых TTR опускается до порога (`TTR <= threshold`, см. [соглашения](#conventions)). Незавершенный последний фактор учитывается пропорционально тому, насколько его TTR приблизился к порогу. Значение - среднее двух проходов, в прямом и обратном порядке (McCarthy & Jarvis, 2010). Минимальная длина фактора нестандартна (lexical-diversity Кайла), а `min_len`, равный 0, ее отключает. Если ни один фактор не завершен и TTR не опускается ниже 1, значение равно бесконечности.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |
| `min_len` | `int` | `10` | Минимальная длина фактора (`MTLD_MIN_LEN`) |
| `threshold` | `float` | `0.72` | Порог TTR для завершения фактора (`MTLD_TTR_THRESHOLD`) |

`min_len`, который не целое неотрицательное число, и `threshold`, который не число в интервале (0, 1), дают `ParameterError`.

</div>

<div class="metric-card" markdown>

### Moving Average Measure of Textual Lexical Diversity (MA-MTLD) { #mamtld }

`mamtld`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_mamtld c845458 -->
``` {.python .signature}
calc_mamtld(text, min_len=10, threshold=0.72)
```

Модификация метрики MTLD со скользящим окном по образцу MTLD-MA из koRpus: фактор начинается с каждой позиции текста, а значение - средняя длина завершенных факторов по двум проходам, в прямом и обратном порядке. koRpus делает только прямой проход, закрывает фактор при TTR строго ниже порога и отбрасывает факторы короче минимальной длины, а не продлевает их. Если ни один фактор не завершен, значение равно `nan`. Метрика нестабильна на коротких текстах.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |
| `min_len` | `int` | `10` | Минимальная длина фактора (`MTLD_MIN_LEN`) |
| `threshold` | `float` | `0.72` | Порог TTR для завершения фактора (`MTLD_TTR_THRESHOLD`) |

`min_len`, который не целое неотрицательное число, и `threshold`, который не число в интервале (0, 1), дают `ParameterError`.

</div>

<div class="metric-card" markdown>

### MTLD со скользящим окном и заворотом текста (MTLD-W) { #mtldw }

`mtldw`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_mtldw 6e0e9fe -->
``` {.python .signature}
calc_mtldw(text, min_len=10, threshold=0.72)
```

Модификация метрики MA-MTLD по образцу `mtld_ma_wrap` из lexical-diversity и TAALED: факторы, не завершенные до конца текста, продолжаются с его начала, поэтому все позиции получают равный вес. Фактор не может быть длиннее текста. Если ни один фактор не завершен, потому что текст короче `min_len` или TTR не опускается до порога ни с одного начала, значение равно `nan`. Метрика нестабильна на текстах короче 100 слов.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |
| `min_len` | `int` | `10` | Минимальная длина фактора (`MTLD_MIN_LEN`) |
| `threshold` | `float` | `0.72` | Порог TTR для завершения фактора (`MTLD_TTR_THRESHOLD`) |

`min_len`, который не целое неотрицательное число, и `threshold`, который не число в интервале (0, 1), дают `ParameterError`.

</div>

<div class="metric-card" markdown>

### Hypergeometric Distribution D (HD-D) { #hdd }

`hdd`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_hdd 44ad1ca -->
``` {.python .signature}
calc_hdd(text, sample_size=42)
```

Альтернатива vocd-D (McCarthy & Jarvis, 2010): точный ожидаемый TTR случайной выборки из `sample_size` слов, без отбора выборок. Гипергеометрическое распределение дает вероятность того, что каждая лексема попадет в выборку хотя бы раз; HD-D - сумма этих вероятностей, деленная на размер выборки. Для текстов короче 50 слов или короче размера выборки метрика не определена, и значение равно `nan`.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |
| `sample_size` | `int` | `42` | Размер выборки в словах (`HDD_SAMPLE_SIZE`) |

`sample_size`, который не целое число не меньше единицы, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Индекс Симпсона (D) { #simpson_index }

`simpson_index` · [Википедия](https://en.wikipedia.org/wiki/Diversity_index#Simpson_index)
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_simpson_index 5c0c871 -->
``` {.python .signature}
calc_simpson_index(text)
```

Вероятность того, что два слова, случайно извлеченные из текста без возвращения, окажутся одной лексемой; $n$ - количество вхождений лексемы в текст. Для текстов короче двух слов индекс не определен, и значение равно `nan`; то же относится к обратному индексу Симпсона и индексу Джини-Симпсона.

$$
\frac{\sum n\times(n-1)}{\textrm{(Количество слов)}\times(\textrm{Количество слов}-1)}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Обратный индекс Симпсона (1/D) { #inverse_simpson_index }

`inverse_simpson_index` · [Википедия](https://en.wikipedia.org/wiki/Diversity_index#Inverse_Simpson_index)
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_inverse_simpson_index 370880d -->
``` {.python .signature}
calc_inverse_simpson_index(text)
```

Оценка числа Хилла второго порядка ($1/\sum_k p_k^2$) по парам слов, извлеченным без возвращения. Если все слова текста уникальны, индекс Симпсона равен 0, а обратный индекс - бесконечности.

$$
\frac{1}{D}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Индекс Джини-Симпсона (1-D) { #gini_simpson_index }

`gini_simpson_index` · [Википедия](https://en.wikipedia.org/wiki/Diversity_index#Gini–Simpson_index)
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_gini_simpson_index 00e1184 -->
``` {.python .signature}
calc_gini_simpson_index(text)
```

Вероятность того, что два случайно выбранных слова текста окажутся разными.

$$
1-D
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Гапакс-индекс (Honoré's R) { #hapax_index }

`hapax_index` · `honore_r` · [Википедия](https://ru.wikipedia.org/wiki/Гапакс)
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_hapax_index debfb9b -->
``` {.python .signature}
calc_hapax_index(text)
```

Гапакс (греч. ἅπαξ λεγόμενον - «только раз названное») - слово, встретившееся в корпусе только один раз: *baciyelmo*, словечко Санчо Пансы для цирюльничьего тазика, который Дон Кихот принимает за шлем, - гапакс Сервантеса (глава 44 первой части «Дон Кихота»). Индекс совпадает с мерой Оноре (1979) и использует натуральный логарифм. Если все слова текста - гапаксы, индекс равен бесконечности; для текстов короче двух слов он не определен, и значение равно `nan`. `calc_honore_r` - та же функция.

$$
100\times\frac{\ln {\textrm{(Количество слов)}}}{1-\frac{\textrm{Количество гапаксов}}{\textrm{Количество лексем}}}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

Русский пример: боливар («шляпа определённого фасона») - гапакс языка Пушкина: слово встречается только в знаменитом месте из «Евгения Онегина».

</div>

<div class="metric-card" markdown>

### Спектр частот { #frequency_spectrum }

`frequency_spectrum`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_frequency_spectrum 5ca9622 -->
``` {.python .signature}
calc_frequency_spectrum(text)
```

Количество лексем $V_i$, встретившихся в тексте ровно $i$ раз, справочником по частоте $i$ в порядке возрастания. Из него по формулам Tweedie и Baayen (1998) вычисляются гапакс-индекс, характеристики Юла K и I, меры Хердана Vm, Сишела S, Мишеа M и Баайена P, доля гапаксов и показатель α₂.

Обозначения: $N$ - количество слов, $V$ - количество лексем, $V_i$ - количество лексем с частотой $i$, $V_1$ - гапаксы, $V_2$ - дислегомены, $p_k$ - относительная частота лексемы.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Характеристика Юла (Yule's K) { #yule_k }

`yule_k`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_yule_k baaaa5a -->
``` {.python .signature}
calc_yule_k(text)
```

Характеристика Юла (Yule, 1944) - одна из немногих мер, теоретически не зависящих от длины текста (Tweedie & Baayen, 1998); на практике она сходится с ростом текста. Пропорциональна индексу Симпсона: $K \approx 10^4 \cdot D$. Для текстов короче двух слов значение равно `nan`.

$$
K = 10^4\times\frac{\sum_i i^2 V_i - N}{N^2}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Обратная характеристика Юла (Yule's I) { #yule_i }

`yule_i`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_yule_i e6ed7d8 -->
``` {.python .signature}
calc_yule_i(text)
```

Обратная характеристика Юла. Если все слова текста уникальны, значение равно бесконечности; для текстов короче двух слов - `nan`.

$$
I = \frac{V^2}{\sum_i i^2 V_i - V}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Мера Хердана (Herdan's Vm) { #herdan_vm }

`herdan_vm`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_herdan_vm a9088dd -->
``` {.python .signature}
calc_herdan_vm(text)
```

Мера Хердана (Herdan, 1955), теоретически не зависящая от длины текста. Для текстов короче двух слов значение равно `nan`.

$$
V_m = \sqrt{\sum_i V_i \left(\frac{i}{N}\right)^2 - \frac{1}{V}}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Мера Сишела (Sichel's S) { #sichel_s }

`sichel_s`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_sichel_s 5485001 -->
``` {.python .signature}
calc_sichel_s(text)
```

Мера Сишела (Sichel, 1975) - доля дислегоменов, лексем с частотой 2, среди всех лексем. Стабильна на текстах разной длины.

$$
S = \frac{V_2}{V}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Мера Мишеа (Michéa's M) { #michea_m }

`michea_m`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_michea_m 8e3f6f5 -->
``` {.python .signature}
calc_michea_m(text)
```

Мера Мишеа (Michéa, 1969) - обратная величина к мере Сишела. Если в тексте нет дислегоменов, значение равно бесконечности.

$$
M = \frac{V}{V_2}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Мера Брюне (Brunet's W) { #brunet_w }

`brunet_w`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_brunet_w 2ac7def -->
``` {.python .signature}
calc_brunet_w(text, a=0.172)
```

Мера Брюне (Brunet, 1978). Значения для текстов обычно лежат в пределах 10-20.

$$
W = N^{V^{-a}}, \quad a = 0.172
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |
| `a` | `float` | `0.172` | Показатель степени (`BRUNET_W_EXPONENT`) |

`a`, который не конечное число, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Мера Дюга (Dugast's k) { #dugast_k }

`dugast_k`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_dugast_k a8d476b -->
``` {.python .signature}
calc_dugast_k(text, base=10)
```

Мера Дюга (Dugast, 1979), не путать с Dugast's U - метрикой [DTTR](#dttr). Значение зависит от основания логарифма. Для текстов не длиннее основания ($\log N \le 1$) мера не определена, и значение равно `nan`.

$$
k = \frac{\log V}{\log \log N}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |
| `base` | `float` | `10` | Основание логарифма (`DIVERSITY_LOG_BASE`) |

`base`, который не конечное число больше 1, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Мера Баайена (Baayen's P) { #baayen_p }

`baayen_p`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_baayen_p 3754bfb -->
``` {.python .signature}
calc_baayen_p(text)
```

Мера Баайена (Baayen, 1991) - доля гапаксов среди всех слов текста. Равна наклону кривой роста словаря в конце текста: вероятности того, что следующее слово окажется новым (Evert, 2004).

$$
P = \frac{V_1}{N}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Доля гапаксов { #hapax_ratio }

`hapax_ratio`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_hapax_ratio d3c3e24 -->
``` {.python .signature}
calc_hapax_ratio(text)
```

Доля гапаксов среди всех лексем текста.

$$
\frac{V_1}{V}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Показатель α₂ { #alpha2 }

`alpha2`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_alpha2 69486ad -->
``` {.python .signature}
calc_alpha2(text)
```

Оценка параметра Ципфа-Мандельброта по нижней части спектра частот (Evert, 2004). Если в тексте нет гапаксов, значение равно `nan`.

$$
\alpha_2 = 1 - \frac{2 V_2}{V_1}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Энтропия Шеннона { #entropy }

`entropy` · [Википедия](https://en.wikipedia.org/wiki/Diversity_index#Shannon_index)
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_entropy 507c0b8 -->
``` {.python .signature}
calc_entropy(text)
```

Энтропия распределения лексем в битах. Число Хилла первого порядка равно $2^H$ ([перплексия](#perplexity)), нулевого - $V$; число второго порядка оценивает [обратный индекс Симпсона](#inverse_simpson_index).

$$
H = -\sum_k p_k \log_2 p_k
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Выравненность { #evenness }

`evenness`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_evenness d6817c3 -->
``` {.python .signature}
calc_evenness(text)
```

Выравненность Пиелу - отношение энтропии Шеннона к ее максимуму при данном количестве лексем. Для текстов из одной лексемы она не определена, и значение равно `nan`.

$$
\frac{H}{\log_2 V}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Перплексия { #perplexity }

`perplexity`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_perplexity b5c954f -->
``` {.python .signature}
calc_perplexity(text)
```

Число Хилла первого порядка, эффективное количество лексем текста.

$$
2^H
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Наклон закона Ципфа { #zipf_alpha }

`zipf_alpha` · [Википедия](https://en.wikipedia.org/wiki/Zipf's_law)
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_zipf_alpha a63837a -->
``` {.python .signature}
calc_zipf_alpha(text)
```

Показатель $\alpha$ закона Ципфа $f(r) \propto r^{-\alpha}$, где $r$ - ранг лексемы по частоте, оцененный линейной регрессией логарифма частоты по логарифму ранга. Для естественных текстов $\alpha$ близка к 1. Оценка по рангам методом наименьших квадратов смещена, метод максимального правдоподобия точнее. Для текстов из одной лексемы значение равно `nan`.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

</div>

<div class="metric-card" markdown>

### Подгонка закона Ципфа-Мандельброта { #fit_zipf_mandelbrot }

[Википедия](https://en.wikipedia.org/wiki/Zipf–Mandelbrot_law)
{ .metric-meta }

<!-- core: stats/diversity_stats.md:fit_zipf_mandelbrot 41b2359 -->
``` {.python .signature}
fit_zipf_mandelbrot(text)
```

Подгонка закона Ципфа-Мандельброта $f(r) = C / (r + q)^s$ к распределению частот по рангам. При $q = 0$ это закон Ципфа с показателем $s$; сдвиг $q$ передает выполаживание кривой на самых частых словах. Параметры подбираются методом наименьших квадратов в логарифмических координатах при $q \ge 0$, $s \ge 0$; лексемы с нулевой частотой в счетчике не учитываются. Результат - именованный кортеж `ZipfMandelbrot` с полями `c`, `q`, `s` и `r2` - коэффициентом детерминации подгонки в логарифмических координатах. Все поля равны `nan` для текстов из менее чем трех лексем, при одинаковых частотах всех лексем или при расходящейся подгонке. На коротких текстах параметры неустойчивы: закон описывает большие корпуса.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` / `Counter` | - | Список слов или счетчик их частот |

Счетчик, слова которого не строки или частоты не числа, дает `SourceTypeError`, а отрицательная, `nan` или бесконечная частота - `SourceError` (`check_counts`).

Визуализатор [закона Ципфа](../visualizers/zipf.md) строит эту подгонку при `show_fit=True`.

=== "Код"

    ``` python
    from ruts.diversity_stats import fit_zipf_mandelbrot

    # частоты 12, 6, 4, 3 в точности следуют закону f = 12 / r
    words = ["а"] * 12 + ["б"] * 6 + ["в"] * 4 + ["г"] * 3
    fit = fit_zipf_mandelbrot(words)
    round(fit.c, 3), round(fit.q, 3), round(fit.s, 3), round(fit.r2, 3)
    ```

=== "Результат"

    ```
    (12.001, 0.0, 1.0, 1.0)
    ```

</div>

<div class="metric-card" markdown>

### Показатель закона Хипса { #heaps_beta }

`heaps_beta` · [Википедия](https://en.wikipedia.org/wiki/Heaps'_law)
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_heaps_beta 6aaa64a -->
``` {.python .signature}
calc_heaps_beta(text)
```

Показатель $\beta$ закона Хипса $V(N) = K \cdot N^{\beta}$ роста словаря с ростом длины текста, оцененный линейной регрессией логарифма размера словаря по логарифму длины текста вдоль кривой роста. На корпусах в миллионы слов $\beta$ лежит в пределах 0.4-0.6, на отдельном тексте - в пределах 0.6-0.9, поэтому значения сравнимы только между текстами близкой длины. Значение зависит от порядка слов и требует от нескольких сотен слов. Для текстов короче двух слов значение равно `nan`.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |

<!-- core: stats/diversity_stats.md:vocabulary_growth d1f1d6d -->
``` {.python .signature}
vocabulary_growth(text)
```

Кривая роста словаря списка слов: размер словаря после каждого слова текста.

<!-- core: stats/diversity_stats.md:fit_heaps eefb450 -->
``` {.python .signature}
fit_heaps(text)
```

Подгонка закона Хипса по кривой роста словаря списка слов, как в `calc_heaps_beta`. Возвращает именованный кортеж `HeapsFit` с параметрами `k`, `beta` и коэффициентом детерминации `r2`, все `nan` для текстов короче двух слов; `r2` равен `nan` и для текста из одной лексемы.

По `fit_heaps` строится график [закона Хипса](../visualizers/vocabulary.md).

</div>

<div class="metric-card" markdown>

### Оконный расчет { #windowed }

`windowed(stat)`
{ .metric-meta }

``` {.python .signature}
calc_windowed(text, func, window_len=100, step=None, confidence=0.95, *, messages=CORE_MESSAGES)
```

<!-- core: stats/diversity_stats.md:calc_windowed 40fa4f2 -->
Значения метрики по последовательным окнам одинаковой длины дают их среднее, выборочное стандартное отклонение и доверительный интервал среднего по распределению Стьюдента. Стандартный способ сравнения текстов разной длины; стандартизированный TTR Кубата и Милички (не STTR Summer) - оконный TTR с окном 1000 слов и 95% интервалом. Текст короче окна - единственное окно; окна со значением `nan` не учитываются. Если окон с определенным значением меньше двух, отклонение и интервал равны `nan`, а если таких окон нет - и среднее. Метрика, бесконечная хотя бы в одном окне (например, обратный индекс Симпсона на окне из уникальных слов), делает среднее бесконечным, а отклонение и интервал - `nan`. Результат - именованный кортеж `WindowStats` с полями `mean`, `std`, `lower`, `upper` и `n_windows` - числом окон с определенным значением.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `list[str]` | - | Список слов |
| `func` | `Callable` | - | Функция вычисления метрики по списку слов |
| `window_len` | `int` | `100` | Размер окна |
| `step` | `int` | `None` | Шаг окна; по умолчанию равен размеру окна, и окна не пересекаются |
| `confidence` | `float` | `0.95` | Уровень доверия |
| `messages` | `dict[str, str]` | `CORE_MESSAGES` | Сообщения об ошибках по ключам |

`func`, который нельзя вызвать, дает `SourceTypeError`; `window_len` или `step`, которые не целое число не меньше единицы, и `confidence`, который не число в интервале (0, 1), дают `ParameterError`.

</div>

<!-- core: stats/diversity_stats.md:diversity-checks 518d85e -->
Каждая функция проверяет слова с помощью `check_words`: `text`, который является строкой, `Doc`, итератором, множеством или таблицей или слова которого не строки, дает `SourceTypeError`; `fit_zipf_mandelbrot` принимает и счетчик.

## Методы

<!-- core: stats/diversity_stats.md:DiversityStats-windowed da979e4 -->
`windowed(stat, window_len=100, step=None, confidence=0.95)` вычисляет метрику из `get_stats` по ее названию в окнах: `calc_windowed` с функцией метрики и параметрами объекта. Остальные аргументы, результат и ошибки - как у `calc_windowed`; неизвестное название дает `UnknownStatError`.

=== "Код"

    ``` python
    ds.windowed("ttr", window_len=5)
    ds.windowed("ttr", window_len=5, step=2).n_windows
    ```

=== "Результат"

    ```
    WindowStats(mean=0.9333333333333332, std=0.11547005383792512, lower=0.6464898180167025, upper=1.220176848649964, n_windows=3)
    6
    ```

<!-- core: stats/diversity_stats.md:DiversityStats-get_stats fa25bfe -->
`get_stats()` возвращает справочник вычисленных метрик из `stats_desc`.

<!-- core: stats/diversity_stats.md:DiversityStats-print_stats 8d60982 -->
`print_stats()` выводит таблицу вычисленных метрик с их описаниями из `stats_desc` под заголовками из `stats_headers`.

=== "Код"

    ``` python
    ds.get_stats()
    ```

=== "Результат"

    ```
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

Остальные методы - `to_dataframe` и `describe` - из [интерфейса статистик](https://sergeyshk.github.io/anyTS/stats/stats/) ядра anyTS; шкал у метрик лексического разнообразия нет, поэтому `describe` для метрик `get_stats` возвращает `None`.
