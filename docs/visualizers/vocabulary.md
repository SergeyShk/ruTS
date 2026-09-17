# Рост словаря и спектр частот

!!! info ""
    **ruts.visualizers.heaps_plot()**, **ruts.visualizers.frequency_spectrum_plot()**

## Описание

Два графика о распределении слов текста, дополняющие [закон Ципфа](zipf.md): рост словаря с длиной текста по закону Хипса и спектр частот - сколько лексем встречается ровно один, два, три раза. Оба графика есть в zipfR (`plot.vgc`, `plot.spc`). Функции принимают оси `ax` и возвращают `Axes`.

## Закон Хипса { #heaps_plot }

Размер словаря $V$ после каждого слова текста и кривая подгонки $V(N) = K \cdot N^{\beta}$ по [`fit_heaps`](../stats/diversity_stats_funcs.md#heaps_beta) с параметрами в легенде. На корпусах в миллионы слов $\beta$ лежит в пределах 0.4-0.6, по всей кривой роста отдельного текста получается больше (0.6-0.9), так как в начале текста почти каждое слово новое; кривая зависит от порядка слов.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `words` | list[str] | `-` | Слова текста по порядку |
| `ax` | Axes | `None` | Оси для графика |

## Спектр частот { #frequency_spectrum_plot }

Число лексем $V(m)$, встретившихся ровно $m$ раз ([`calc_frequency_spectrum`](../stats/diversity_stats_funcs.md#frequency_spectrum)), в логарифмических координатах; левый край - гапаксы. По спектру считаются меры разнообразия Юла, Сишела, Мишеа и Honoré, а его форма показывает, насколько словарь текста «недобран».

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `words` | list[str] | `-` | Слова текста |
| `ax` | Axes | `None` | Оси для графика |

## Пример использования

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    import matplotlib.pyplot as plt
    from ruts import WordsExtractor
    from ruts.datasets import StalinWorks
    from ruts.visualizers import frequency_spectrum_plot, heaps_plot

    # Подготовка данных
    sw = StalinWorks()
    we = WordsExtractor(use_lexemes=True, lowercase=True, filter_nums=True)
    lemmas = [lemma for text in sw.get_texts(limit=12) for lemma in we.extract(text)]

    # Построение графиков
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 4.5))
    heaps_plot(lemmas, ax=left)
    frequency_spectrum_plot(lemmas, ax=right)
    ```

    _Результат_:

    ![ruts](../img/vocabulary.png){: .center }
