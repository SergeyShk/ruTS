# Стилометрия

!!! info ""
    **ruts.corpus.delta()**, **ruts.corpus.frequency_table()**, **ruts.corpus.z_scores()**, **ruts.corpus.zeta()**, **ruts.corpus.kilgarriff_chi2()**, **ruts.corpus.mendenhall_curve()**, **ruts.corpus.mendenhall_distance()**, **ruts.corpus.function_words_profile()**

## Описание

Меры стилометрии и атрибуции авторства: расстояния между текстами по частотам самых частых слов (дельта Барроуза и ее варианты, как в [stylo](https://github.com/computationalstylistics/stylo)), маркеры предпочитаемых и избегаемых слов (Zeta), расстояние хи-квадрат Килгарриффа между корпусами, кривая Менденхолла и профиль служебных слов как признаки автора. Функции работают со списками единиц текста: словоформ в нижнем регистре (обычный выбор для дельты), лемм или символьных N-грамм ([`CharNgramsExtractor`](../extractors/char_ngrams.md)) - регистр и лемматизация на стороне экстрактора.

## Дельта Барроуза { #delta }

Корпус - словарь «имя текста → единицы». `frequency_table` строит таблицу относительных частот: строки - тексты, столбцы - `n_mfw` самых частых единиц по убыванию средней относительной частоты (при равенстве - по алфавиту); `culling` оставляет единицы, встречающиеся хотя бы в заданной доле текстов, как в stylo. `z_scores` стандартизирует столбцы с выборочным стандартным отклонением, как `scale()` в R; столбец с одинаковыми частотами во всех текстах дает нули. `delta` считает по z-оценкам симметричную матрицу расстояний (`DataFrame` с именами текстов), пригодную для кластеризации и PCA; нужно не меньше трех текстов - на двух z-оценки вырождаются в ±1 и все расстояния одинаковы.

Варианты (`DELTA_VARIANTS`), формулы по исходникам stylo, $n$ - число единиц, $z_A$, $z_B$ - векторы z-оценок текстов:

| Вариант | Ключ | Формула | Источник |
| :------ | :--- | :------ | :------- |
| Дельта Барроуза | `burrows` | $\frac{1}{n} \sum_i \lvert z_{A,i} - z_{B,i} \rvert$ | Burrows (2002), `dist.delta` |
| Квадратичная дельта | `quadratic` | $\frac{1}{n} \sqrt{\sum_i (z_{A,i} - z_{B,i})^2}$ | Argamon (2008), `dist.argamon` |
| Дельта Эдера | `eder` | $\sum_i \frac{n - i + 2}{n} \lvert z_{A,i} - z_{B,i} \rvert$, $i$ - ранг единицы по частоте | Eder, `dist.eder` |
| Косинусная дельта | `cosine` | $1 - \frac{z_A \cdot z_B}{\lVert z_A \rVert \lVert z_B \rVert}$ | Smith и Aldridge (2011), [Evert и др. (2015)](https://aclanthology.org/W15-0709.pdf), `dist.wurzburg` |

Косинусная дельта дает лучшее качество кластеризации по авторам в экспериментах Evert и др.; дельта Барроуза - классический выбор. Число единиц берут от 100 до 500 самых частых слов; для символьных N-грамм - 100-200.

Параметры `delta`:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `corpus` | dict[str, list[str]] | `-` | Единицы текстов по именам текстов |
| `n_mfw` | int | `100` | Число самых частых единиц; `None` - все |
| `variant` | str | `burrows` | Вариант дельты из `DELTA_VARIANTS` |
| `culling` | float | `0.0` | Наименьшая доля текстов, в которых встречается единица |

`frequency_table(corpus, n_mfw=100, culling=0.0)` и `z_scores(table)` принимают те же параметры и таблицу.

!!! example "Пример"

    ``` python
    from ruts import WordsExtractor
    from ruts.corpus import delta, frequency_table

    texts = {
        "А": "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне.",
        "Б": "Собака лежала на полу и дремала. Потом собака ела и снова дремала на полу.",
        "В": "Завтра кот снова будет сидеть на окне и смотреть на птиц, а собака будет дремать.",
    }
    we = WordsExtractor(lowercase=True)
    corpus = {name: we.extract(text) for name, text in texts.items()}

    frequency_table(corpus, n_mfw=5).round(3)
    #       на      и  собака    кот   окне
    # А  0.200  0.133   0.000  0.133  0.133
    # Б  0.143  0.143   0.143  0.000  0.000
    # В  0.133  0.067   0.067  0.067  0.067

    delta(corpus, n_mfw=5).round(3)
    #        А      Б      В
    # А  0.000  1.563  1.277
    # Б  1.563  0.000  1.033
    # В  1.277  1.033  0.000

    delta(corpus, n_mfw=5, variant="cosine").round(3)
    #        А      Б      В
    # А  0.000  1.782  1.452
    # Б  1.782  0.000  1.202
    # В  1.452  1.202  0.000
    ```

## Zeta { #zeta }

Маркеры предпочитаемых и избегаемых слов по Burrows (2007) и Craig и Kinney (2009). Каждый текст обоих корпусов делится на сегменты примерно по `segment_size` слов (число сегментов - округленное отношение длины к размеру, не меньше одного); для слова считается доля сегментов каждого корпуса, в которых оно встречается ($DP$). Zeta - разность долей $DP_{target} - DP_{comparison}$ от −1 до 1 (в записи stylo `zeta.craig`; классическая Zeta Крейга $DP_{target} + (1 - DP_{comparison})$ больше на единицу), логарифмическая Zeta - $\log_2 \frac{DP_{target}}{DP_{comparison}}$ ([Schöch и др. 2018](https://zeta-project.eu/en/keyness-measures/burrows-zeta-logarithmic-zeta/)), нулевая доля заменяется на половину сегмента. В начале списка слова, предпочитаемые целевым корпусом, в конце - избегаемые.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `target` | list[str]/list[list[str]] | `-` | Слова целевого корпуса - один текст или список текстов |
| `comparison` | list[str]/list[list[str]] | `-` | Слова корпуса сравнения |
| `segment_size` | int | `2000` | Размер сегмента в словах |
| `top_n` | int | `None` | Количество слов с начала списка; `None` - все |

Результат - список именованных кортежей `ZetaScore(word, dp_target, dp_comparison, zeta, log_zeta)` по убыванию Zeta, при равенстве - по убыванию логарифмической Zeta и по алфавиту.

!!! example "Пример"

    ``` python
    from ruts.corpus import zeta

    zeta(corpus["А"], corpus["Б"], segment_size=5, top_n=2)
    # [ZetaScore(word='кот', dp_target=0.6666666666666666, dp_comparison=0.0, zeta=0.6666666666666666, log_zeta=2.0),
    #  ZetaScore(word='окне', dp_target=0.6666666666666666, dp_comparison=0.0, zeta=0.6666666666666666, log_zeta=2.0)]

    zeta(corpus["А"], corpus["Б"], segment_size=5)[-1]
    # ZetaScore(word='собака', dp_target=0.0, dp_comparison=0.6666666666666666, zeta=-0.6666666666666666, log_zeta=-2.0)
    ```

## Хи-квадрат Килгарриффа { #kilgarriff_chi2 }

Расстояние между двумя корпусами по [Kilgarriff (2001)](https://www.sketchengine.eu/wp-content/uploads/comparing_corpora_2001.pdf): для `n_mfw` самых частых слов объединенного корпуса ожидаемые частоты в корпусах пропорциональны их объемам, $\chi^2 = \sum (O - E)^2 / E$ по словам и обоим корпусам. Чем больше значение, тем сильнее корпуса различаются; величина растет с объемом корпусов, поэтому пары корпусов сравнимы между собой при равных объемах, как в экспериментах Килгарриффа.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `words_a` | list[str] | `-` | Слова первого корпуса |
| `words_b` | list[str] | `-` | Слова второго корпуса |
| `n_mfw` | int | `500` | Число самых частых слов объединенного корпуса |

!!! example "Пример"

    ``` python
    from ruts.corpus import kilgarriff_chi2

    round(kilgarriff_chi2(corpus["А"], corpus["Б"], n_mfw=5), 3)
    # 6.018
    ```

## Кривая Менденхолла { #mendenhall }

`mendenhall_curve(words)` - доли слов каждой длины в символах (Mendenhall 1887), профиль автора, сравнимый между текстами независимо от их объема; `mendenhall_distance(words_a, words_b)` - расстояние Йенсена-Шеннона с основанием 2 между кривыми, от 0 (распределения совпадают) до 1.

!!! example "Пример"

    ``` python
    from ruts.corpus import mendenhall_curve, mendenhall_distance

    {length: round(share, 3) for length, share in mendenhall_curve(corpus["А"]).items()}
    # {1: 0.133, 2: 0.2, 3: 0.133, 4: 0.2, 5: 0.2, 7: 0.133}

    round(mendenhall_distance(corpus["А"], corpus["Б"]), 3)
    # 0.353
    ```

## Профиль служебных слов { #function_words_profile }

Доли предлогов, сочинительных и подчинительных союзов, частиц, местоимений, детерминативов и междометий (`FUNCTION_UD_POS`: `ADP`, `CCONJ`, `SCONJ`, `PART`, `PRON`, `DET`, `INTJ`) среди слов текста - по первому разбору pymorphy3 для списка слов и по разметке для `Doc` с частями речи. Служебные слова не зависят от темы, поэтому их профиль - классический признак авторства (школа Марусенко).

!!! example "Пример"

    ``` python
    from ruts.corpus import function_words_profile

    {pos: round(share, 3) for pos, share in function_words_profile(corpus["А"]).items()}
    # {'ADP': 0.2, 'CCONJ': 0.133, 'SCONJ': 0.0, 'PART': 0.0, 'PRON': 0.0, 'DET': 0.0, 'INTJ': 0.0}
    ```
