# Сравнение корпусов

!!! info ""
    **ruts.corpus.compare_corpora()**, **ruts.corpus.corpus_features()**, **ruts.corpus.text_features()**, **ruts.corpus.split_windows()**, **ruts.corpus.sentence_rhythm()**

## Описание

Сравнение двух корпусов по всем признакам текста сразу: какие статистики различают авторов, жанры, переводы, человеческие и сгенерированные тексты - и насколько. Для отдельных слов то же делает [`keyness`](keyness.md), для расстояний между текстами - [`delta`](stylometry.md#delta).

Тексты обоих корпусов режутся на окна одинакового размера (`split_windows`: число окон - округленное отношение числа слов к размеру окна, не меньше одного, части равные), чтобы убрать зависимость признаков от длины текста. Для каждого окна считаются признаки (`text_features` или своя функция), для каждого признака сравниваются два набора значений. Результат - `DataFrame` признак × статистики, отсортированный по убыванию модуля дельты Клиффа.

## Признаки

`text_features(text)` возвращает около 100 признаков с префиксом по источнику:

| Префикс | Признаки | Источник |
| :------ | :------- | :------- |
| `basic_` | доли уникальных, длинных, сложных, простых, одно- и многосложных слов, букв, пробелов и знаков препинания; буквы и слоги на слово, слова на предложение | [`BasicStats`](../stats/basic_stats.md) |
| `readability_` | все формулы удобочитаемости, сводный класс, время чтения | [`ReadabilityStats`](../stats/readability_stats.md) |
| `diversity_` | все меры лексического разнообразия | [`DiversityStats`](../stats/diversity_stats.md) |
| `morph_` | доли частей речи от числа слов (`morph_pos_NOUN`) и доли значений внутри каждого признака (`morph_case_Gen`, `morph_tense_Past`) | [`MorphStats`](../stats/morph_stats.md) по pymorphy3 |
| `sents_` | средняя длина предложения в словах, стандартное отклонение, коэффициент вариации, автокорреляция соседних длин (`sentence_rhythm`) - ритм текста | [`sentence_lengths`](../visualizers/sentences.md) |
| `punct_` | частоты знаков по типам на 1000 слов и доля буквы ё | [`punctuation_profile`](../stats/basic_stats.md#punctuation) |

На окно в 1000 слов уходит около 0.1 с. Признаки по разбору spaCy (`SyntaxStats`, `CohesionStats`) в набор по умолчанию не входят - функция работает по строкам; их можно добавить своей функцией признаков через `features`, см. пример ниже. `corpus_features(texts, window, features)` отдает матрицу признаков окон с индексом (номер текста, номер окна) - для своих классификаторов.

## Статистики

Для признака со значениями $x_1 \dots x_{n_A}$ в корпусе A и $y_1 \dots y_{n_B}$ в корпусе B (неопределенные и бесконечные значения отброшены; при менее чем двух значениях на стороне - `nan`):

| Столбец | Описание |
| :------ | :------- |
| `mean_A`, `mean_B`, `median_A`, `median_B` | средние и медианы |
| `median_diff`, `ci_low`, `ci_high` | разность медиан и ее перцентильный бутстрэп-интервал 95%: оба набора пересэмплируются `n_bootstrap` раз (`bootstrap_median_diff`) |
| `cohen_d` | $d = (\bar{x} - \bar{y}) / s$, $s$ - объединенное стандартное отклонение; 0.2 - малый эффект, 0.5 - средний, 0.8 - большой (`calc_cohen_d`) |
| `cliff_delta` | $\delta = P(x > y) - P(x < y)$ от −1 до 1; $\lvert\delta\rvert$ < 0.147 - пренебрежимый эффект, < 0.33 - малый, < 0.474 - средний, иначе большой (Romano и др. 2006; `calc_cliff_delta`) |
| `auc` | признак как одиночный классификатор: доля пар окон, где значение в A больше, чем в B, ничьи за половину; $\delta = 2 \cdot AUC - 1$, 0.5 - признак не различает корпуса |
| `u`, `p_value` | U-критерий Манна-Уитни и двустороннее p-значение (`scipy.stats.mannwhitneyu`) |
| `p_holm` | p-значение с поправкой Холма на число признаков (`holm_correction`): таблица из сотни строк без поправки приглашает к ложным открытиям |
| `n_A`, `n_B` | число окон с определенным значением |

Дельта Клиффа и AUC считаются из той же U-статистики, поэтому согласованы между собой; d Коэна чувствителен к выбросам и ненормальности, его стоит смотреть рядом с дельтой.

## Параметры

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `a` | list[str] | `-` | Тексты первого корпуса |
| `b` | list[str] | `-` | Тексты второго корпуса |
| `window` | int | `1000` | Размер окна в словах; `None` - тексты целиком |
| `features` | callable | `None` | Функция признаков текста; `None` - `text_features` |
| `labels` | tuple[str, str] | `("A", "B")` | Имена корпусов для столбцов |
| `n_bootstrap` | int | `1000` | Число выборок бутстрэпа |
| `seed` | int | `0` | Зерно генератора случайных чисел; `None` - случайное |

## Пример использования

Чехов против Толстого по прозе из набора [`RussianLiterature`](../datasets/russianliterature.md): 77 и 42 произведения, 292 и 1444 окна по 1000 слов, около двух минут.

!!! example "Пример"

    _Код_:

    ``` python
    from ruts.corpus import compare_corpora
    from ruts.datasets import RussianLiterature

    rl = RussianLiterature()
    chekhov = list(rl.get_texts(genre="prose", author="Чехов"))
    tolstoy = list(rl.get_texts(genre="prose", author="Толстой"))

    result = compare_corpora(chekhov, tolstoy, window=1000, labels=("Чехов", "Толстой"))
    columns = ["median_Чехов", "median_Толстой", "ci_low", "ci_high", "cohen_d", "cliff_delta", "auc", "p_holm"]
    result[columns].head(10).round(3)
    ```

    _Результат_:

    ``` bash
                                   median_Чехов  median_Толстой  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    punct_ellipsis                       15.842           2.000  10.938   17.920    1.861        0.719  0.860     0.0
    punct_exclamation                    14.881           3.996   9.210   12.371    1.704        0.670  0.835     0.0
    morph_verb_form_Fin                   0.761           0.695   0.056    0.076    1.161        0.594  0.797     0.0
    punct_yo_share                        0.007           0.000   0.007    0.008    1.065        0.557  0.778     0.0
    readability_gunning_fog_index         5.995           7.963  -2.278   -1.677   -0.960       -0.540  0.230     0.0
    sents_mean                           11.122          15.136  -4.599   -3.411   -0.943       -0.531  0.235     0.0
    basic_words_per_sent                 11.122          15.129  -4.595   -3.400   -0.942       -0.530  0.235     0.0
    readability_matskovsky_index          8.600          11.227  -3.147   -2.321   -0.946       -0.530  0.235     0.0
    readability_dale_chall_index          5.187           6.676  -1.776   -1.229   -0.930       -0.527  0.237     0.0
    readability_smog_index                5.711           7.294  -1.899   -1.322   -0.895       -0.516  0.242     0.0
    ```

У Чехова в разы больше многоточий и восклицаний на 1000 слов, короче предложения и выше доля личных форм глагола; Толстой сложнее по всем формулам удобочитаемости. Из 130 признаков у 94 поправленное p-значение ниже 0.01, но большой эффект по дельте Клиффа только у 14 - на тысячах окон значимость дешева, размер эффекта важнее.

Свои признаки, например синтаксические по spaCy, передаются функцией:

!!! example "Пример"

    ``` python
    import spacy
    from ruts import SyntaxStats
    from ruts.corpus import compare_corpora, text_features

    nlp = spacy.load("ru_core_news_sm")

    def features(text):
        stats = SyntaxStats(nlp(text)).get_stats()
        return {**text_features(text), **{f"syntax_{key}": value for key, value in stats.items()}}

    compare_corpora(chekhov, tolstoy, window=1000, features=features, labels=("Чехов", "Толстой"))
    ```
