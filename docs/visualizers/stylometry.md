# Стилометрические графики

!!! info ""
    **ruts.visualizers.dendrogram_plot()**, **ruts.visualizers.pca_plot()**, **ruts.visualizers.mds_plot()**, **ruts.visualizers.mendenhall_plot()**

## Описание

Графики к [стилометрии](../corpus/stylometry.md): дендрограмма и многомерное шкалирование по матрице расстояний [`delta`](../corpus/stylometry.md#delta), диаграмма главных компонент по частотам самых частых слов и кривые Менденхолла нескольких текстов - набор, которым в stylo смотрят на кластеризацию текстов по авторам. Функции принимают оси `ax` и возвращают `Axes`.

## Дендрограмма { #dendrogram_plot }

Иерархическая кластеризация `scipy.cluster.hierarchy` по матрице расстояний между текстами; метод Уорда по умолчанию, как в stylo и у [Evert и др. (2015)](https://aclanthology.org/W15-0709.pdf), подписи листьев - имена текстов из индекса матрицы.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `distances` | DataFrame | `-` | Симметричная матрица расстояний с именами текстов |
| `method` | str | `ward` | Метод объединения кластеров `scipy.cluster.hierarchy.linkage` |
| `ax` | Axes | `None` | Оси для графика |

## Главные компоненты { #pca_plot }

Метод главных компонент по z-оценкам относительных частот самых частых единиц ([`frequency_table`](../corpus/stylometry.md#delta), `z_scores`) через сингулярное разложение, как `pca.visualization` в stylo: тексты на плоскости двух первых компонент с подписями, в подписях осей - доля объясненной дисперсии.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `corpus` | dict[str, list[str]] | `-` | Единицы текстов по именам текстов |
| `n_mfw` | int | `100` | Число самых частых единиц; `None` - все |
| `culling` | float | `0.0` | Наименьшая доля текстов, в которых встречается единица |
| `ax` | Axes | `None` | Оси для графика |

## Многомерное шкалирование { #mds_plot }

Классическое многомерное шкалирование (Torgerson 1952) по любой матрице расстояний: двойное центрирование матрицы квадратов расстояний и два главных собственных вектора; расстояния между точками приближают расстояния матрицы.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `distances` | DataFrame | `-` | Симметричная матрица расстояний с именами текстов |
| `ax` | Axes | `None` | Оси для графика |

## Кривые Менденхолла { #mendenhall_plot }

Доли слов по длине в символах ([`mendenhall_curve`](../corpus/stylometry.md#mendenhall)) для каждого текста на одном графике - сравнение профилей авторов.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `corpus` | dict[str, list[str]] | `-` | Слова текстов по именам текстов |
| `ax` | Axes | `None` | Оси для графика |

## Пример использования

Рассмотрим работу визуализаторов на примере 8 текстов из набора данных [StalinWorks](../datasets/stalinworks.md).

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    import matplotlib.pyplot as plt
    from ruts import WordsExtractor
    from ruts.corpus import delta
    from ruts.datasets import StalinWorks
    from ruts.visualizers import dendrogram_plot, mds_plot, mendenhall_plot, pca_plot

    # Подготовка данных
    sw = StalinWorks()
    we = WordsExtractor(use_lexemes=True, lowercase=True, filter_nums=True)
    corpus = {f"текст {i + 1}": we.extract(text) for i, text in enumerate(sw.get_texts(limit=8))}
    distances = delta(corpus, n_mfw=100, variant="cosine")

    # Дендрограмма и главные компоненты на одной фигуре
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5))
    dendrogram_plot(distances, ax=left)
    pca_plot(corpus, n_mfw=100, ax=right)

    # Многомерное шкалирование и кривые Менденхолла
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5))
    mds_plot(distances, ax=left)
    mendenhall_plot({name: corpus[name] for name in list(corpus)[:3]}, ax=right)
    ```

    _Результат_:

    ![ruts](../img/stylometry.png){: .center }

    ![ruts](../img/mds_mendenhall.png){: .center }
