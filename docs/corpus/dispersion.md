# Дисперсия слов

<!-- core: corpus/dispersion.md:dispersion f0bdceb -->
``` {.python .signature}
dispersion(words, parts=10, word=None, min_freq=1)
```

Дисперсия слова - насколько равномерно оно распределено по частям текста или корпуса. Частота не различает слово, встречающееся по разу в каждой главе, и слово, сосредоточенное в одной из них; меры дисперсии ([Gries 2008](https://www.stgries.info/research/2008_STG_Dispersion_IJCL.pdf), [2020](https://www.stgries.info/research/2020_STG_Dispersion_PHCL.pdf)) дополняют частоту.

`parts` - число частей примерно равного размера или размеры частей по порядку (предложения, абзацы, главы, документы корпуса), в сумме равные числу слов. По частотам каждого слова по частям считаются шесть мер; Gries рекомендует DP как основную.

Слова сравниваются как есть: регистр и лемматизация - на стороне экстрактора слов.

Модуль `ruts.corpus.dispersion` реэкспортирует функцию ядра [anyTS](https://sergeyshk.github.io/anyTS/corpus/dispersion/). Слова извлекает [`WordsExtractor`](../extractors/words.md); знаки ударения снимаются со слов и с `word`.

=== "Код"

    ``` python
    from ruts import SentsExtractor, WordsExtractor
    from ruts.corpus import dispersion

    text = (
        "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне. "
        "Завтра кот снова будет сидеть на окне и смотреть на птиц."
    )
    we = WordsExtractor(use_lexemes=True, lowercase=True)
    words = we.extract(text)
    sizes = [len(we.extract(sent)) for sent in SentsExtractor().extract(text)]
    sizes
    dispersion(words, parts=sizes, word="кот")

    # Три равные части: «птица» - только в первой и последней
    [(d.word, round(d.dp, 2)) for d in dispersion(words, parts=3, min_freq=3)]
    ```

=== "Результат"

    ```
    [8, 7, 11]
    [Dispersion(word='кот', freq=3, dp=0.08974358974358976, dp_norm=0.12280701754385966, juilland_d=0.8725780285943101, carroll_d2=0.984770130157433, rosengren_s=0.9907464277073554, kl_divergence=0.0265483705216355)]
    [('на', 0.15), ('кот', 0.32), ('окно', 0.03), ('и', 0.03), ('птица', 0.35)]
    ```

## Параметры

<!-- core: corpus/dispersion.md:dispersion-parameters 2fdf192 -->
| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `words` | `list[str]` | - | Слова текста по порядку |
| `parts` | `int` / `list[int]` | `10` | Число частей (от 2 до числа слов) или размеры частей |
| `word` | `str` | `None` | Слово, дисперсия которого нужна; `None` - все слова |
| `min_freq` | `int` | `1` | Минимальная частота слова |

Слова, которые не список строк, дают `SourceTypeError`, а отсутствие слов - `SourceError`. `parts`, который не целое число от 2 до числа слов и не два или более положительных целых числа, в сумме равных ему, `word`, который не строка, и `min_freq`, который не целое число, дают `ParameterError`.

## Результат

<!-- core: corpus/dispersion.md:Dispersion 536c09a -->
``` {.python .signature}
Dispersion(word, freq, dp, dp_norm, juilland_d, carroll_d2, rosengren_s, kl_divergence)
```

Список именованных кортежей `Dispersion` по убыванию частоты: слово, его частота и меры; `pd.DataFrame(result)` дает таблицу.

## Меры

<!-- core: corpus/dispersion.md:dispersion-measures dc6c36a -->
Меры - поля `Dispersion`, с названиями в `anyts.constants.DISPERSION_STATS_DESC`:

| Поле | Что измеряет | Диапазон | Чем больше, тем |
| :--- | :----------- | :------- | :-------------- |
| [`dp`](#dp) | Отклонение долей вхождений от долей частей | от 0 до $1 - \min s_i$ | неравномернее |
| [`dp_norm`](#dp_norm) | DP, деленное на наибольшее возможное значение | 0-1 | неравномернее |
| [`juilland_d`](#juilland_d) | Вариация относительных частот по частям | 0-1 | равномернее |
| [`carroll_d2`](#carroll_d2) | Энтропия относительных частот по частям | 0-1 | равномернее |
| [`rosengren_s`](#rosengren_s) | Разброс вхождений относительно размеров частей | от $\min s_i$ до 1 | равномернее |
| [`kl_divergence`](#kl_divergence) | Расхождение долей вхождений с долями частей, в битах | от 0 до $-\log_2 \min s_i$ | неравномернее |

Каждая мера - функция модуля `anyts.corpus.dispersion` от частот слова по частям и размеров частей. Для $n$ частей размерами $n_i$ с долями $s_i$ в тексте, частот слова по частям $v_i$ и общей частоты $f = \sum v_i$ относительная частота в части - $p_i = v_i / n_i$:

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `frequencies` | `list[int]` | - | Частоты слова по частям |
| `sizes` | `list[int]` | - | Размеры частей |

Для слова с нулевой частотой все меры `nan`.

Модуль `ruts.corpus.dispersion` реэкспортирует функции мер (`from ruts.corpus.dispersion import calc_dp`).

<div class="metric-card" markdown>

### Отклонение пропорций DP { #dp }

`dp` · [Gries (2008)](https://www.stgries.info/research/2008_STG_Dispersion_IJCL.pdf)
{ .metric-meta }

<!-- core: corpus/dispersion.md:calc_dp 6c51955 -->
``` {.python .signature}
calc_dp(frequencies, sizes)
```

Насколько доли вхождений слова по частям отличаются от долей частей: 0 - слово распределено пропорционально размерам частей, $1 - s_i$ - все вхождения в части $i$.

$$
DP = \frac{1}{2} \sum \left\lvert \frac{v_i}{f} - s_i \right\rvert
$$

</div>

<div class="metric-card" markdown>

### Нормированное DP { #dp_norm }

`dp_norm` · Lijffijt и Gries (2012)
{ .metric-meta }

<!-- core: corpus/dispersion.md:calc_dp_norm bab9d44 -->
``` {.python .signature}
calc_dp_norm(frequencies, sizes)
```

DP, деленное на наибольшее возможное значение, так что максимум равен единице при любом делении.

$$
\frac{DP}{1 - \min s_i}
$$

</div>

<div class="metric-card" markdown>

### D Жюйана { #juilland_d }

`juilland_d` · Juilland и Chang-Rodríguez (1964)
{ .metric-meta }

<!-- core: corpus/dispersion.md:calc_juilland_d c172dee -->
``` {.python .signature}
calc_juilland_d(frequencies, sizes)
```

Единица минус коэффициент вариации $V$ относительных частот $p_i$, деленный на его наибольшее значение $\sqrt{n - 1}$: 1 - равномерно, 0 - все в одной части. Стандартное отклонение $\sigma$ - генеральной совокупности, как в Gries (2020); Gries (2008) берет выборочное.

$$
1 - \frac{V}{\sqrt{n - 1}}, \quad V = \frac{\sigma(p)}{\mu(p)}
$$

</div>

<div class="metric-card" markdown>

### D2 Кэрролла { #carroll_d2 }

`carroll_d2` · Carroll (1970)
{ .metric-meta }

<!-- core: corpus/dispersion.md:calc_carroll_d2 82075b3 -->
``` {.python .signature}
calc_carroll_d2(frequencies, sizes)
```

Энтропия распределения относительных частот $p_i$ по частям, деленная на ее наибольшее значение: 1 - равномерно, 0 - все в одной части.

$$
\frac{H(p)}{\log_2 n}
$$

</div>

<div class="metric-card" markdown>

### S Розенгрена { #rosengren_s }

`rosengren_s` · Rosengren (1971)
{ .metric-meta }

<!-- core: corpus/dispersion.md:calc_rosengren_s 29fcb9c -->
``` {.python .signature}
calc_rosengren_s(frequencies, sizes)
```

1 - слово распределено пропорционально размерам частей; все вхождения в части $i$ дают $s_i$, то есть $1/n$ в одной из $n$ равных частей.

$$
\frac{(\sum \sqrt{s_i v_i})^2}{f}
$$

</div>

<div class="metric-card" markdown>

### Дивергенция Кульбака-Лейблера { #kl_divergence }

`kl_divergence` · [Gries (2020)](https://www.stgries.info/research/2020_STG_Dispersion_PHCL.pdf)
{ .metric-meta }

<!-- core: corpus/dispersion.md:calc_kl_divergence f5095d5 -->
``` {.python .signature}
calc_kl_divergence(frequencies, sizes)
```

Расхождение долей вхождений слова по частям с долями частей: 0 - пропорционально; растет, когда слово сосредоточено в малых частях.

$$
\sum \frac{v_i}{f} \log_2 \frac{v_i / f}{s_i}
$$

</div>
