# Коллокации

<!-- core: corpus/collocations.md:collocations a019591 -->
``` {.python .signature}
collocations(words, window=5, measure='logdice', min_freq=2, node=None, top_n=None, side=None)
```

Поиск коллокаций - пар слов, которые встречаются вместе чаще, чем дала бы независимость: устойчивые сочетания, терминология, сочетаемость слова. Меры ассоциации те же, что в [Sketch Engine](https://www.sketchengine.eu/wp-content/uploads/ske-statistics.pdf) и [`nltk.metrics.association`](https://www.nltk.org/api/nltk.metrics.association.html).

Пары упорядочены, как в NLTK: правое слово встречается не дальше `window` слов после левого, каждая пара позиций учитывается один раз; `window=1` дает биграммы. Меры берут частоту пары, деленную на размер окна (Church и Hanks 1990, так же в NLTK), так что ожидаемая частота не зависит от окна, а Dice и минимальная чувствительность не превышают единицы; `freq_pair` остается без деления. Поэтому при `window > 1` пара, всегда стоящая рядом, получает logDice $14 - \log_2 window$ (13 при окне 2), а не 14, как в Sketch Engine с его сырым числом совстречаемостей; 14 достигает только пара, встречающаяся на каждом расстоянии в окне. `node` оставляет пары с заданным словом с любой стороны, а `side` - с одной из них: `"left"` - коллокаты перед этим словом, `"right"` - после него.

Слова сравниваются как есть: регистр, лемматизация и стоп-слова - на стороне экстрактора слов; для устойчивых сочетаний подходят леммы, для грамматических конструкций - словоформы.

Функция оборачивает `collocations` ядра [anyTS](https://sergeyshk.github.io/anyTS/corpus/collocations/) и снимает знаки ударения со слов и с `node`. Слова извлекает [`WordsExtractor`](../extractors/words.md); для русских устойчивых сочетаний вроде «точка зрения» или «рабочий класс» берут его леммы (`use_lexemes=True`).

=== "Код"

    ``` python
    from ruts import WordsExtractor
    from ruts.corpus import collocations

    words = WordsExtractor(use_lexemes=True, lowercase=True).extract(
        "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне. "
        "Завтра кот снова будет сидеть на окне и смотреть на птиц."
    )

    collocations(words, window=2, top_n=1)
    [
        (c.left, c.right, round(c.score, 2))
        for c in collocations(words, window=1, node="кот", min_freq=1, measure="mi")[:2]
    ]
    ```

=== "Результат"

    ```
    [Collocation(left='птица', right='улететь', freq_left=3, freq_right=1, freq_pair=2, score=13.0)]
    [('завтра', 'кот', 3.12), ('кот', 'снова', 3.12)]
    ```

## Параметры

<!-- core: corpus/collocations.md:collocations-parameters 09ebaf3 -->
| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `words` | `list[str]` | - | Слова текста по порядку |
| `window` | `int` | `5` | Наибольшее расстояние между словами пары |
| `measure` | `str` | `'logdice'` | Мера из `anyts.constants.COLLOCATION_MEASURES` |
| `min_freq` | `int` | `2` | Минимальная частота пары |
| `node` | `str` | `None` | Слово, сочетаемость которого нужна; `None` - все пары |
| `top_n` | `int` | `None` | Количество коллокаций; `None` - все |
| `side` | `str` | `None` | При заданном слове - сторона его коллокатов: `"left"` или `"right"`; `None` - обе |

Слова, которые не список строк, дают `SourceTypeError`, а отсутствие слов - `SourceError`. Неизвестная мера, `window` или `top_n`, который не целое число не меньше единицы, `min_freq`, который не целое число, `node`, который не строка, и `side`, который не `"left"` и не `"right"` или задан без `node`, дают `ParameterError`.

## Результат

<!-- core: corpus/collocations.md:Collocation f1761f5 -->
``` {.python .signature}
Collocation(left, right, freq_left, freq_right, freq_pair, score)
```

Список именованных кортежей `Collocation` по убыванию меры и частоты пары (при равенстве - по алфавиту); `pd.DataFrame(found)` дает таблицу.

| Поле | Тип | Описание |
| :--- | :-- | :------- |
| `left` | `str` | Левое слово |
| `right` | `str` | Правое слово, встречается в окне после левого |
| `freq_left` | `int` | Частота левого слова |
| `freq_right` | `int` | Частота правого слова |
| `freq_pair` | `int` | Частота совместной встречаемости |
| `score` | `float` | Значение выбранной меры |

## Меры

<!-- core: corpus/collocations.md:collocations-measures e3fd7a0 -->
Меры `measure` по ключам, с названиями и описаниями в `anyts.constants.COLLOCATION_MEASURES`:

| Ключ | Что измеряет | Диапазон | Чем больше, тем |
| :--- | :----------- | :------- | :-------------- |
| [`mi`](#mi) | Частота пары относительно ожидаемой, в битах | любое число | сильнее связь |
| [`mi3`](#mi3) | MI с частотой пары в кубе | любое число | сильнее связь |
| [`t_score`](#t_score) | Разность наблюдаемой и ожидаемой частоты пары | любое число | надежнее связь |
| [`dice`](#dice) | Доля пары во вхождениях двух слов | 0-1 | сильнее связь |
| [`logdice`](#logdice) | Коэффициент Дайса в логарифмической шкале | не больше 14 | сильнее связь |
| [`log_likelihood`](#log_likelihood) | Значимость связи | от 0, `nan`, если слово занимает весь текст или клетка отрицательна | значимее отклонение от независимости - и для притягивающихся, и для избегающих друг друга пар |
| [`npmi`](#npmi) | MI, нормированная на информацию пары | от −1 до 1 | сильнее связь |
| [`min_sensitivity`](#min_sensitivity) | Меньшая из долей пары во вхождениях каждого слова | 0-1 | сильнее связь |

Каждая мера - функция модуля `anyts.corpus.collocations` от частот слов и пары и числа слов:

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `freq_a` | `int` | - | Частота $f_a$ первого слова |
| `freq_b` | `int` | - | Частота $f_b$ второго слова |
| `freq_ab` | `float` | - | Частота $f_{ab}$ пары |
| `n` | `int` | - | Число слов $N$ текста |

Пара с нулевой частотой дает `nan` для MI, MI³, t-критерия, logDice и NPMI.

Модуль `ruts.corpus.collocations` реэкспортирует функции мер (`from ruts.corpus.collocations import calc_logdice`).

<div class="metric-card" markdown>

### Взаимная информация { #mi }

`mi` · Church и Hanks (1990)
{ .metric-meta }

<!-- core: corpus/collocations.md:calc_mi b0aa7c7 -->
``` {.python .signature}
calc_mi(freq_a, freq_b, freq_ab, n)
```

Поточечная взаимная информация двух слов; завышает редкие пары.

$$
\log_2 \frac{f_{ab} N}{f_a f_b}
$$

</div>

<div class="metric-card" markdown>

### MI³ { #mi3 }

`mi3` · Oakes (1998)
{ .metric-meta }

<!-- core: corpus/collocations.md:calc_mi3 92d7122 -->
``` {.python .signature}
calc_mi3(freq_a, freq_b, freq_ab, n)
```

Взаимная информация с частотой пары в кубе, которая отдает предпочтение частым парам.

$$
\log_2 \frac{f_{ab}^3 N}{f_a f_b}
$$

</div>

<div class="metric-card" markdown>

### t-критерий { #t_score }

`t_score` · Church и др. (1991)
{ .metric-meta }

<!-- core: corpus/collocations.md:calc_t_score f89d062 -->
``` {.python .signature}
calc_t_score(freq_a, freq_b, freq_ab, n)
```

Разность наблюдаемой и ожидаемой частоты пары, деленная на корень из наблюдаемой; отдает предпочтение частым парам.

$$
\frac{f_{ab} - f_a f_b / N}{\sqrt{f_{ab}}}
$$

</div>

<div class="metric-card" markdown>

### Коэффициент Дайса { #dice }

`dice`
{ .metric-meta }

<!-- core: corpus/collocations.md:calc_dice 7a8289e -->
``` {.python .signature}
calc_dice(freq_a, freq_b, freq_ab, n)
```

Доля пары во вхождениях двух слов; не зависит от размера текста.

$$
\frac{2 f_{ab}}{f_a + f_b}
$$

</div>

<div class="metric-card" markdown>

### logDice { #logdice }

`logdice` · [Rychlý (2008)](https://www.sketchengine.eu/glossary/logdice/)
{ .metric-meta }

<!-- core: corpus/collocations.md:calc_logdice a3020bb -->
``` {.python .signature}
calc_logdice(freq_a, freq_b, freq_ab, n)
```

Коэффициент Дайса в двоичной логарифмической шкале, мера по умолчанию, как в Sketch Engine. Не зависит от размера текста; ниже нуля - слабая связь.

$$
14 + \log_2 \frac{2 f_{ab}}{f_a + f_b}
$$

</div>

<div class="metric-card" markdown>

### Логарифм правдоподобия { #log_likelihood }

`log_likelihood` · Dunning (1993)
{ .metric-meta }

<!-- core: corpus/collocations.md:calc_log_likelihood 0ed2f9e -->
``` {.python .signature}
calc_log_likelihood(freq_a, freq_b, freq_ab, n)
```

$G^2$ по таблице сопряженности 2×2 двух слов: наблюдаемые частоты $O$ - $f_{ab}$, $f_a - f_{ab}$, $f_b - f_{ab}$ и $N - f_a - f_b + f_{ab}$ - относительно ожидаемых $E$ при независимости. Слово, которое занимает весь текст, или отрицательная клетка, как у слова в паре с самим собой при окне больше единицы, дает `nan`.

$$
G^2 = 2 \sum O \ln \frac{O}{E}
$$

</div>

<div class="metric-card" markdown>

### NPMI { #npmi }

`npmi` · Bouma (2009)
{ .metric-meta }

<!-- core: corpus/collocations.md:calc_npmi a88529b -->
``` {.python .signature}
calc_npmi(freq_a, freq_b, freq_ab, n)
```

Взаимная информация, нормированная на информацию пары: единица - слова встречаются только вместе. Пара с частотой, равной длине текста, дает `nan`.

$$
\frac{MI}{-\log_2 (f_{ab} / N)}
$$

</div>

<div class="metric-card" markdown>

### Минимальная чувствительность { #min_sensitivity }

`min_sensitivity` · Pedersen (1998)
{ .metric-meta }

<!-- core: corpus/collocations.md:calc_min_sensitivity e3bdac7 -->
``` {.python .signature}
calc_min_sensitivity(freq_a, freq_b, freq_ab, n)
```

Меньшая из долей пары во вхождениях каждого слова.

$$
\min\left(\frac{f_{ab}}{f_a}, \frac{f_{ab}}{f_b}\right)
$$

</div>
