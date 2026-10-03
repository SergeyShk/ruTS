# Дерево слов

!!! info ""
    **ruts.visualizers.wordtree()**

## Описание

<!-- core: visualizers/word_tree.md:wordtree 7b85f86 -->
Построение [дерева слов](https://www.weblyzard.com/word-tree/), которое показывает контексты ключевого слова в тексте: в каждом списке слов - например, в предложении - считаются N-граммы длиной до `max_n` слов, которые начинаются или заканчиваются ключевым словом. Каждый уровень дерева сохраняет `max_per_n` самых частых N-грамм, продолжающих сохраненную более короткую, при равенстве - по алфавиту. Сохраненные N-граммы объединяются в два дерева, слов после ключевого слова и перед ним, с размером шрифта по частоте ([Wattenberg и Viégas 2008](https://www.cg.tuwien.ac.at/courses/InfoVis/HallOfFame/2011/Gruppe05/Homepage/Paper/wordtree-paper-wattenberg.pdf)). Для отрисовки нужны исполняемые файлы [Graphviz](https://graphviz.org/download/).

Это функция ядра [anyTS](https://sergeyshk.github.io/anyTS/visualizers/word_tree/).

## Параметры

<!-- core: visualizers/word_tree.md:wordtree-parameters d32a474 -->
| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `texts` | list[list[str]] | `-` | Список списков слов |
| `keyword` | str | `-` | Ключевое слово, контексты которого показываются |
| `max_n` | int | `5` | Наибольший размер контекста |
| `max_per_n` | int | `8` | Наибольшее число примеров для каждого размера контекста |
| `**kwargs` | - | `-` | Параметры отрисовки: `max_font_size` (по умолчанию `30`), `min_font_size` (`12`), `font_interp` - функция относительной частоты узла (его частоты к наибольшей, в интервале (0, 1]), которая дает долю диапазона от `min_font_size` до `max_font_size`, от 0 до 1; по умолчанию кубический корень |

Функция возвращает `Digraph` библиотеки graphviz.

## Пример использования

Рассмотрим работу визуализатора на примере предложений 50 текстов из набора данных [StalinWorks](../datasets/stalinworks.md).

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    from ruts import SentsExtractor, WordsExtractor
    from ruts.datasets import StalinWorks
    from ruts.visualizers import wordtree

    # Подготовка данных
    sw = StalinWorks()
    se = SentsExtractor()
    we = WordsExtractor(min_len=3)
    texts = [text for text in sw.get_texts(limit=50)]

    # Подготовка списка списков слов
    words = []
    for text in texts:
        sents = se.extract(text)
        for sent in sents:
            words.append(we.extract(sent))

    # Построение графика
    g = wordtree(words, "рабочий", max_n=6)

    # Сохранение визуализации на диск
    g.render("wordtree", format="png")
    ```

    _Результат_:

    ![ruts](../img/wordtree.png){: .center }
