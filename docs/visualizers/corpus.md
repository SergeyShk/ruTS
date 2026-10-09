# Корпусные графики

!!! info ""
    **ruts.visualizers.dispersion_plot()**, **ruts.visualizers.keyness_plot()**, **ruts.visualizers.collocation_network()**

## Описание

Графики к [корпусным мерам](../corpus/keyness.md): лексическая дисперсия - где в тексте встречается слово, диаграмма ключевых слов по результатам [`keyness`](../corpus/keyness.md) и сеть коллокаций по результатам [`collocations`](../corpus/collocations.md). Функции matplotlib принимают оси `ax` и возвращают `Axes`: без `ax` создается новая фигура, с `ax` график ложится в сетку пользователя; сеть коллокаций строится graphviz и возвращает `Graph`, как [дерево слов](word_tree.md).

Это функции ядра [anyTS](https://sergeyshk.github.io/anyTS/visualizers/corpus/) с русскими подписями графиков matplotlib из `ruts.constants.VISUALIZER_LABELS` по умолчанию; `labels` задает подписи поверх них, а пара строк, переданная `keyness_plot`, заменяет две подписи легенды, остальные остаются русскими. `dispersion_plot` снимает знаки ударения со слов и с `targets`.

## Лексическая дисперсия { #dispersion_plot }

<!-- core: visualizers/corpus.md:dispersion_plot 604b589 -->
Строка на каждое слово из `targets` и штрих на позиции каждого его вхождения в текст. Слова сравниваются как есть: регистр и лемматизация - на стороне извлечения слов.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `words` | list[str] | `-` | Слова текста по порядку |
| `targets` | list[str] | `-` | Слова, вхождения которых показываются |
| `ax` | Axes | `None` | Оси для графика |
| `labels` | dict[str, str] | `None` | Подписи поверх подписей по умолчанию: `title`, `xlabel` |

Слова извлекает [`WordsExtractor`](../extractors/words.md): в нижнем регистре - с `lowercase=True`, леммы - с `use_lexemes=True`.

## Диаграмма ключевых слов { #keyness_plot }

<!-- core: visualizers/corpus.md:keyness_plot e860f91 -->
Расходящиеся горизонтальные столбцы: слова из `positive` вправо, из `negative` - результата `keyness` с `positive=False` - влево, длина столбца - модуль значения поля `field` (`score`, `g2`, `log_ratio`), так что сторона задается списком, а не знаком меры; по `top_n` слов с каждой стороны, слова с неопределенным или бесконечным значением пропускаются. Для отношения шансов (`score` от 0 до бесконечности, единица - шансы равны) задайте `log=True`: откладывается модуль $\log_2$ значения, симметричный относительно единицы.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `positive` | list[Keyword] | `-` | Положительные ключевые слова |
| `negative` | list[Keyword] | `()` | Отрицательные ключевые слова |
| `top_n` | int | `20` | Количество слов с каждой стороны |
| `labels` | dict[str, str]/tuple[str, str] | `None` | Подписи поверх подписей по умолчанию: `title`, `xlabel` и `xlabel_log` (строки формата с `field`), `target` и `reference` (легенда); пара строк задает только легенду |
| `field` | str | `score` | Поле `Keyword`, значения которого откладываются |
| `log` | bool | `False` | Откладывать $\log_2$ значения - для отношения шансов |
| `ax` | Axes | `None` | Оси для графика |

## Сеть коллокаций { #collocation_network }

<!-- core: visualizers/corpus.md:collocation_network 080cdcf -->
Неориентированный граф: узлы - слова с размером шрифта по частоте, ребра - пары с толщиной и подписью по значению меры; раскладка `neato`. Пара слова с самим собой - слово, повторенное внутри окна, - была бы петлей и отбрасывается до того, как берутся `top_n` пар. Для отрисовки нужны исполняемые файлы [Graphviz](https://graphviz.org/download/); в Jupyter граф отображается сам, а `graph.render("network")` сохраняет файл png.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `collocations` | list[Collocation] | `-` | Коллокации |
| `top_n` | int | `None` | Количество пар с начала списка; `None` - все |

## Пример использования

Рассмотрим работу визуализаторов на примере 12 текстов из набора данных [StalinWorks](../datasets/stalinworks.md).

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    import matplotlib.pyplot as plt
    from ruts import WordsExtractor
    from ruts.corpus import collocations, keyness
    from ruts.datasets import FreqDict, StalinWorks
    from ruts.visualizers import collocation_network, dispersion_plot, keyness_plot

    # Подготовка данных
    sw = StalinWorks()
    texts = list(sw.get_texts(limit=12))
    we = WordsExtractor(use_lexemes=True, lowercase=True, filter_nums=True)
    lemmas = [lemma for text in texts for lemma in we.extract(text)]
    words = [word for text in texts for word in WordsExtractor(filter_nums=True).extract(text)]

    # Лексическая дисперсия
    dispersion_plot(lemmas, ["партия", "рабочий", "революция", "царь"])

    # Ключевые слова относительно частотного словаря
    freq_dict = FreqDict()
    keyness_plot(
        keyness(words, freq_dict, min_freq=5, top_n=10),
        keyness(words, freq_dict, positive=False, min_freq=5, top_n=10),
        labels=("тексты Сталина", "частотный словарь"),
    )

    # Сеть коллокаций
    graph = collocation_network(collocations(lemmas, window=3, min_freq=5, top_n=25))
    graph.render("network", format="png")
    ```

    _Результат_:

    ![ruts](../img/dispersion.png){: .center }

    ![ruts](../img/keyness.png){: .center }
