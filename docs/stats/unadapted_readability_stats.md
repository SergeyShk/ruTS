# Формулы других языков

``` {.python .signature}
UnadaptedReadabilityStats(source, sents_extractor=None, words_extractor=None)
```

<!-- core: stats/unadapted_readability_stats.md:UnadaptedReadabilityStats 0fc386b -->
Формулы удобочитаемости, созданные для английского, немецкого или итальянского языка, считаются по базовым статистикам текста с опубликованными коэффициентами (Linsear Write - в форме textstat), без калибровки под язык текста. Их значения сравнивают тексты одного языка между собой, но классами обучения для другого языка не являются. Слово без слогов (число, предлог из одной согласной) в FORCAST и венских формулах считается односложным, а в Linsear Write - легким, как в textstat. Источник данных - текст, объект `Doc` библиотеки [spaCy](https://github.com/explosion/spaCy) или готовый объект `BasicStats`, как у `ReadabilityStats`.

Исключения:

- `SourceTypeError` - источник, который не строка, не `Doc` и не объект `BasicStats`, базовые статистики не того класса, экстрактор другого типа, строка или `Doc` для класса без `basic_stats_class`;
- `SourceError` - источник без слов или без предложений.

Класс расширяет `UnadaptedReadabilityStats` ядра [anyTS](https://sergeyshk.github.io/anyTS/stats/unadapted_readability_stats/) [базовыми статистиками](basic_stats.md) ruTS, которые считают слоги и буквы русских слов и по умолчанию берут русские [`SentsExtractor`](../extractors/sentences.md) и [`WordsExtractor`](../extractors/words.md). Таблица `print_stats` и сообщения об ошибках - по-русски (`UNADAPTED_READABILITY_STATS_DESC` и `CORE_MESSAGES` из `ruts.constants`).

Формулы не откалиброваны для русского языка. Их значения годятся, чтобы сравнивать русские тексты между собой и с расчетами этих формул в других инструментах, но класса российской школы не дают: на текстах 1-го класса набора [`TextsByGrade`](../datasets/textsbygrade.md) медиана FORCAST - 14.9, класса Пауэрса-Самнера-Керла - 8.2, Венской формулы 1 - 9.4. Поэтому шкал прочтения у этих формул нет, `describe` возвращает для них `None`, а в [сводный класс](readability_stats.md#consensus_grade) они не входят. Формулы с коэффициентами для русского языка - в [`ReadabilityStats`](readability_stats.md).

=== "Код"

    ``` python
    from ruts import UnadaptedReadabilityStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    urs = UnadaptedReadabilityStats(text)
    urs.print_stats()
    ```

=== "Результат"

    ```
                     Метрика                  | Значение
    -----------------------------------------------------
    Класс FORCAST                             |  13.00
    Класс Linsear Write                       |   8.50
    Класс Пауэрса-Самнера-Керла               |   6.55
    Индекс EFLAW Макалпайна                   |  21.00
    Венская формула 1 (Wiener Sachtextformel) |   4.42
    Венская формула 2 (Wiener Sachtextformel) |   4.25
    Венская формула 3 (Wiener Sachtextformel) |   5.69
    Венская формула 4 (Wiener Sachtextformel) |   5.95
    Индекс Дикеса-Штайвера                    |  42.20
    Индекс Gulpease                           |  65.67
    Индекс Фукса                              |  25.00
    Индекс Strain                             |   7.50
    Формула легкости на слух (ELF)            |  10.00
    Индекс Уилера-Смита                       |  80.00
    ```

## Параметры

<!-- core: stats/unadapted_readability_stats.md:UnadaptedReadabilityStats-parameters 2f3854b -->
| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `source` | `str` / `Doc` / `BasicStats` | - | Источник данных |
| `sents_extractor` | `SentsExtractor` | `None` | Инструмент для извлечения предложений, не используется для готовых базовых статистик |
| `words_extractor` | `WordsExtractor` | `None` | Инструмент для извлечения слов, не используется для готовых базовых статистик |

## Атрибуты

<!-- core: stats/unadapted_readability_stats.md:UnadaptedReadabilityStats-attributes 569ba31 -->
| Атрибут | Тип | Описание |
| :------ | :-- | :------- |
| `bs` | `BasicStats` | Базовые статистики текста |

Готовые базовые статистики можно взять у объекта [`ReadabilityStats`](readability_stats.md), чтобы не считать их второй раз:

=== "Код"

    ``` python
    from ruts import ReadabilityStats

    rs = ReadabilityStats(text)
    urs = UnadaptedReadabilityStats(rs.bs)
    urs.bs is rs.bs, urs.forcast
    ```

=== "Результат"

    ```
    (True, 13.0)
    ```

## Метрики

<!-- core: stats/unadapted_readability_stats.md:UnadaptedReadabilityStats-metrics 87d03dd -->
Каждая метрика - свойство объекта, которое вычисляется по `bs` при каждом обращении, а `get_stats` дает их все. Сложное слово - от `complex_syl_factor` слогов (3), длинное - от `long_word_letter_factor` букв (7).

| Метрика | Язык и читатели | Диапазон | Чем больше, тем |
| :------ | :-------------- | :------- | :-------------- |
| [`forcast`](#forcast) | английские технические тексты, класс | 5-20 | сложнее текст |
| [`linsear_write`](#linsear_write) | английский, класс | от −1 | сложнее текст |
| [`powers_sumner_kearl`](#powers_sumner_kearl) | английские тексты начальной школы, класс | любой | сложнее текст |
| [`eflaw`](#eflaw) | английский для изучающих его как иностранный | от 1 | сложнее текст |
| [`wiener_sachtextformel_1`](#wiener_sachtextformel) ... [`wiener_sachtextformel_4`](#wiener_sachtextformel) | немецкие нехудожественные тексты, класс от 4 до 15 | любой | сложнее текст |
| [`dickes_steiwer`](#dickes_steiwer) | немецкий, без слогов | любой | легче текст |
| [`gulpease`](#gulpease) | итальянский, по буквам | 0-100 у большинства текстов | легче текст |
| [`fucks`](#fucks) | немецкий, слоги на предложение | от 0 | сложнее текст |
| [`strain_index`](#strain_index) | английский | от 0 | сложнее текст |
| [`elf`](#elf) | английские тексты для чтения вслух | от 0 | сложнее текст |
| [`wheeler_smith`](#wheeler_smith) | английские тексты начальной школы | от 0 | сложнее текст |

Здесь ASL - среднее число слов в предложении, ASW - среднее число слогов в слове. Функции формул импортируются из `ruts.unadapted_readability_stats` и считают значение по количествам:

=== "Код"

    ``` python
    from ruts.unadapted_readability_stats import calc_forcast, calc_gulpease

    calc_forcast(n_monosyllable_words=30, n_words=150)
    calc_gulpease(n_letters=550, n_words=100, n_sents=8)
    ```

=== "Результат"

    ```
    17.0
    58.0
    ```

<div class="metric-card" markdown>

### FORCAST { #forcast }

`forcast` · Caylor et al., 1973
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_forcast f1c7568 -->
``` {.python .signature}
calc_forcast(n_monosyllable_words, n_words)
```

Класс для технических текстов (Caylor и др., 1973): 20 минус десятая часть односложных слов на 150 слов, от 5 (все слова односложные) до 20; `nan` без слов.

$$
\textrm{FORCAST} = 20 - \frac{150 \times \textrm{Количество односложных слов}}{10 \times \textrm{Количество слов}}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `n_monosyllable_words` | `int` | - | Количество односложных слов |
| `n_words` | `int` | - | Количество слов |

Количество, которое не целое неотрицательное число, и число односложных слов больше числа слов дают `ParameterError`.

</div>

<div class="metric-card" markdown>

### Linsear Write { #linsear_write }

`linsear_write`
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_linsear_write fe19083 -->
``` {.python .signature}
calc_linsear_write(n_easy_words, n_hard_words, n_sents)
```

Класс Linsear Write в форме textstat; формула Lensear Write (O'Hayre, 1966) - другая, по односложным словам и предложениям выборки из 100 слов. Легкое слово, не длиннее двух слогов, весит 1, а сложное - 3; их сумма на предложение $r$ больше 20 делится пополам, а иначе перед делением уменьшается на 2. Формула считается по всему тексту, а не по выборке из 100 слов; `nan` без предложений.

$$
r = \frac{\textrm{Количество легких слов} + 3 \times \textrm{Количество сложных слов}}{\textrm{Количество предложений}}, \quad \textrm{LW} = \begin{cases} r / 2 & r > 20 \\ (r - 2) / 2 & r \le 20 \end{cases}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `n_easy_words` | `int` | - | Количество слов из одного или двух слогов |
| `n_hard_words` | `int` | - | Количество слов от трех слогов |
| `n_sents` | `int` | - | Количество предложений |

Количество, которое не целое неотрицательное число, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Класс Пауэрса-Самнера-Керла { #powers_sumner_kearl }

`powers_sumner_kearl` · [Powers et al., 1958](https://doi.org/10.1037/h0043254)
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_powers_sumner_kearl 700718e -->
``` {.python .signature}
calc_powers_sumner_kearl(n_syllables, n_words, n_sents)
```

Пересчет формулы Флеша в класс для текстов начальной школы (Powers, Sumner и Kearl, 1958); `nan` без слов или предложений.

$$
\textrm{PSK} = 0.0778 \times \textrm{ASL} + 4.55 \times \textrm{ASW} - 2.2029
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `n_syllables` | `int` | - | Количество слогов |
| `n_words` | `int` | - | Количество слов |
| `n_sents` | `int` | - | Количество предложений |

Количество, которое не целое неотрицательное число, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Индекс EFLAW Макалпайна { #eflaw }

`eflaw` · McAlpine, 2005
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_eflaw d9e0be5 -->
``` {.python .signature}
calc_eflaw(n_mini_words, n_words, n_sents)
```

Оценка для читателей английского как иностранного (McAlpine, 2005): слова и мини-слова, из одной-трех букв (`mini_word_letters`), на предложение; 20 и ниже - очень легко, 30 и выше - запутанно. `nan` без предложений.

$$
\textrm{EFLAW} = \frac{\textrm{Количество слов} + \textrm{Количество мини-слов}}{\textrm{Количество предложений}}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `n_mini_words` | `int` | - | Количество слов из одной-трех букв |
| `n_words` | `int` | - | Количество слов |
| `n_sents` | `int` | - | Количество предложений |

Количество, которое не целое неотрицательное число, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Венская формула { #wiener_sachtextformel }

`wiener_sachtextformel_1` · `wiener_sachtextformel_2` · `wiener_sachtextformel_3` · `wiener_sachtextformel_4` · Bamberger and Vanecek, 1984
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_wiener_sachtextformel a66d708 -->
``` {.python .signature}
calc_wiener_sachtextformel(n_complex, n_long_words, n_monosyllable_words, n_words, n_sents, variant=1)
```

Четыре формулы для немецких нехудожественных текстов (Bamberger и Vanecek, 1984), класс от 4 до 15, по процентам слов от трех слогов (MS), длиннее шести букв (IW) и односложных (ES) и средней длине предложения (SL); `nan` без слов или предложений. Вариант, который не целое число от 1 до 4, дает `ParameterError`.

$$
\begin{aligned} \textrm{WSTF}_1 &= 0.1935 \cdot \textrm{MS} + 0.1672 \cdot \textrm{SL} + 0.1297 \cdot \textrm{IW} - 0.0327 \cdot \textrm{ES} - 0.875 \\ \textrm{WSTF}_2 &= 0.2007 \cdot \textrm{MS} + 0.1682 \cdot \textrm{SL} + 0.1373 \cdot \textrm{IW} - 2.779 \\ \textrm{WSTF}_3 &= 0.2963 \cdot \textrm{MS} + 0.1905 \cdot \textrm{SL} - 1.1144 \\ \textrm{WSTF}_4 &= 0.2744 \cdot \textrm{MS} + 0.2656 \cdot \textrm{SL} - 1.693 \end{aligned}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `n_complex` | `int` | - | Количество слов от трех слогов |
| `n_long_words` | `int` | - | Количество слов длиннее шести букв |
| `n_monosyllable_words` | `int` | - | Количество односложных слов |
| `n_words` | `int` | - | Количество слов |
| `n_sents` | `int` | - | Количество предложений |
| `variant` | `int` | `1` | Вариант формулы, от 1 до 4 |

Количество, которое не целое неотрицательное число, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Индекс Дикеса-Штайвера { #dickes_steiwer }

`dickes_steiwer` · Dickes and Steiwer, 1977
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_dickes_steiwer 0fea097 -->
``` {.python .signature}
calc_dickes_steiwer(n_letters, n_words, n_sents, n_types)
```

Краткая формула для немецкого языка (Dickes и Steiwer, 1977) в том виде, в каком ее приводят Bamberger и Vanecek (1984), по буквам на слово, словам на предложение и отношению числа разных слов к числу слов (TTR), без слогов; чем больше, тем легче текст. `nan` без слов или предложений.

$$
\textrm{DS} = 235.95993 - 73.021 \ln\left(\frac{\textrm{Количество букв}}{\textrm{Количество слов}} + 1\right) - 12.56438 \ln\left(\frac{\textrm{Количество слов}}{\textrm{Количество предложений}} + 1\right) - 50.03293 \cdot \textrm{TTR}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `n_letters` | `int` | - | Количество букв в словах |
| `n_words` | `int` | - | Количество слов |
| `n_sents` | `int` | - | Количество предложений |
| `n_types` | `int` | - | Количество разных слов |

Количество, которое не целое неотрицательное число, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Индекс Gulpease { #gulpease }

`gulpease` · Lucisano and Piemontese, 1988
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_gulpease 837f4d6 -->
``` {.python .signature}
calc_gulpease(n_letters, n_words, n_sents)
```

Индекс для итальянского языка (Lucisano и Piemontese, 1988) по буквам, а не по слогам: около 0 у самых сложных текстов и 100 у самых легких, за этими пределами - у крайних; ниже 80 текст труден для читателя с начальным образованием, ниже 40 - для читателя со средним. `nan` без слов.

$$
\textrm{Gulpease} = 89 + \frac{300 \times \textrm{Количество предложений} - 10 \times \textrm{Количество букв}}{\textrm{Количество слов}}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `n_letters` | `int` | - | Количество букв в словах |
| `n_words` | `int` | - | Количество слов |
| `n_sents` | `int` | - | Количество предложений |

Количество, которое не целое неотрицательное число, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Индекс Фукса { #fucks }

`fucks` · Fucks, 1955
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_fucks 17d3ed9 -->
``` {.python .signature}
calc_fucks(n_syllables, n_sents)
```

Характеристика стиля (Fucks, 1955): средняя длина слова в слогах, умноженная на среднюю длину предложения в словах, то есть слоги на предложение; `nan` без предложений.

$$
\textrm{Fucks} = \textrm{ASW} \times \textrm{ASL} = \frac{\textrm{Количество слогов}}{\textrm{Количество предложений}}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `n_syllables` | `int` | - | Количество слогов |
| `n_sents` | `int` | - | Количество предложений |

Количество, которое не целое неотрицательное число, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Индекс Strain { #strain_index }

`strain_index` · Nathaniel, 2009
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_strain_index d371c89 -->
``` {.python .signature}
calc_strain_index(n_syllables, n_sents)
```

Индекс (Nathaniel, 2009): число слогов в трех предложениях, деленное на 10, здесь - в среднем по всему тексту; `nan` без предложений.

$$
\textrm{Strain} = \frac{3 \times \textrm{Количество слогов}}{10 \times \textrm{Количество предложений}}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `n_syllables` | `int` | - | Количество слогов |
| `n_sents` | `int` | - | Количество предложений |

Количество, которое не целое неотрицательное число, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Формула легкости на слух { #elf }

`elf` · [Fang, 1966](https://doi.org/10.1080/08838156609363529)
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_elf 59941bf -->
``` {.python .signature}
calc_elf(n_syllables, n_syllabic_words, n_sents)
```

Формула для текстов, которые читают вслух (Fang, 1966): слоги сверх одного на слово в расчете на предложение, причем слово без слогов (число) ничего не добавляет; 12 и ниже - текст легко воспринимается на слух. `nan` без предложений.

$$
\textrm{ELF} = \frac{\textrm{Количество слогов} - \textrm{Количество слов от одного слога}}{\textrm{Количество предложений}}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `n_syllables` | `int` | - | Количество слогов |
| `n_syllabic_words` | `int` | - | Количество слов от одного слога |
| `n_sents` | `int` | - | Количество предложений |

Количество, которое не целое неотрицательное число, дает `ParameterError`.

</div>

<div class="metric-card" markdown>

### Индекс Уилера-Смита { #wheeler_smith }

`wheeler_smith` · Wheeler and Smith, 1954
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_wheeler_smith de9b424 -->
``` {.python .signature}
calc_wheeler_smith(n_polysyllable_words, n_sents)
```

Индекс для текстов начальной школы (Wheeler и Smith, 1954): средняя длина предложения, умноженная на долю слов от двух слогов и на 10, то есть десятикратное число таких слов на предложение; вместо единиц, которые в оригинале заканчивает любой конечный знак, берутся предложения. `nan` без предложений.

$$
\textrm{WS} = 10 \times \textrm{ASL} \times \frac{\textrm{Количество слов от двух слогов}}{\textrm{Количество слов}}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `n_polysyllable_words` | `int` | - | Количество слов от двух слогов |
| `n_sents` | `int` | - | Количество предложений |

Количество, которое не целое неотрицательное число, дает `ParameterError`.

</div>

## Методы

Методы `get_stats`, `to_dataframe`, `print_stats` и `describe` - из [интерфейса статистик](https://sergeyshk.github.io/anyTS/stats/stats/) ядра anyTS; шкал у формул нет, и `describe` возвращает `None` для любой из них.

=== "Код"

    ``` python
    from ruts import UnadaptedReadabilityStats

    text = "Ног нет, а хожу, рта нет, а скажу: когда спать, когда вставать, когда работу начинать"
    urs = UnadaptedReadabilityStats(text)
    urs.describe("forcast"), urs.describe("gulpease")
    urs.get_stats()
    ```

=== "Результат"

    ```
    (None, None)
    {'forcast': 13.0,
     'linsear_write': 8.5,
     'powers_sumner_kearl': 6.547433333333334,
     'eflaw': 21.0,
     'wiener_sachtextformel_1': 4.416333333333334,
     'wiener_sachtextformel_2': 4.250666666666667,
     'wiener_sachtextformel_3': 5.693766666666667,
     'wiener_sachtextformel_4': 5.949666666666667,
     'dickes_steiwer': 42.19782322089459,
     'gulpease': 65.66666666666667,
     'fucks': 25.0,
     'strain_index': 7.5,
     'elf': 10.0,
     'wheeler_smith': 80.0}
    ```
