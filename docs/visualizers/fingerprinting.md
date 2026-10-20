# Литературная дактилоскопия

``` {.python .signature}
fingerprinting(texts, segment_len=10, metric=None, x_size=800, y_size=600, cmap='PuOr', ax=None, labels=None)
```

<!-- core: visualizers/fingerprinting.md:fingerprinting 3fb4965 -->
Визуализация литературной дактилоскопии ([Keim и Oelke 2007](https://www.uni-konstanz.de/mmsp/pubsys/publishedFiles/KeOe07.pdf)).

Каждый текст режется на сегменты по `segment_len` слов со скользящим шагом в десятую часть сегмента, и для каждого сегмента считается мера лексического разнообразия. Все сегменты длиной `segment_len` слов, поэтому значения сопоставимы: если шаг оставляет слова после последнего сегмента, еще один заканчивается вместе с текстом, а текст не длиннее сегмента - один сегмент.

Текст - блок квадратов в порядке его сегментов, по строкам, высотой 8 строк или в один столбец, если сегментов не больше 8; блок шире области визуализации переносится на строки этой ширины. Блоки идут слева направо и переносятся в пределах области шириной `2 · x_size`, которая растет вниз от `2 · y_size`, если блокам нужно больше высоты. Цветовая шкала - от наименьшего до наибольшего конечного значения по всем текстам; неопределенные значения (`nan` на слишком коротких для меры сегментах) и пустые клетки блока - светло-серые, в отличие от любого значения, включая ноль.

Это функция ядра [anyTS](https://sergeyshk.github.io/anyTS/visualizers/fingerprinting/) с русским заголовком из `ruts.constants.VISUALIZER_LABELS` по умолчанию, `labels` заменяет его; в роли `metric` выступают меры [лексического разнообразия](../stats/diversity_stats.md) ruTS - функции списка слов, например `calc_ttr` или `calc_simpson_index`.

Визуализация 100 текстов набора данных [SovChLit](../datasets/sovchlit.md):

``` python
from ruts import WordsExtractor
from ruts.datasets import SovChLit
from ruts.diversity_stats import calc_simpson_index
from ruts.visualizers import fingerprinting

we = WordsExtractor(lowercase=True)
words = [we.extract(text) for text in SovChLit().get_texts(limit=100)]
ax = fingerprinting(words, metric=calc_simpson_index, x_size=1000, y_size=800)
ax.figure.savefig("fingerprinting.png")
```

![ruts](../img/fingerprinting.png){: .center }

## Параметры

<!-- core: visualizers/fingerprinting.md:fingerprinting-parameters 4116a43 -->
| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `texts` | `list[list[str]]` | - | Список списков слов |
| `segment_len` | `int` | `10` | Размер сегмента |
| `metric` | `Callable` | `None` | Функция меры лексического разнообразия; по умолчанию `calc_ttr` |
| `x_size` | `int` | `800` | Половина ширины области визуализации, больше 25 (отступа между блоками) |
| `y_size` | `int` | `600` | Половина высоты области визуализации, которая растет, если блокам нужно больше |
| `cmap` | `str` | `'viridis'` | Цветовая карта |
| `ax` | `Axes` | `None` | Оси matplotlib для графика; если не заданы, создается фигура 15×10 |
| `labels` | `dict[str, str]` | `None` | Подписи поверх подписей по умолчанию: `title` |

Функция возвращает оси `Axes` с визуализацией в равном масштабе осей, чтобы квадраты оставались квадратами; фигура - `ax.figure`. Тексты, которые не список списков строк, и `metric`, которую нельзя вызвать, дают `SourceTypeError`, список без текстов или текст без слов - `SourceError`. `segment_len` или `y_size`, который не целое число больше нуля, `x_size`, который не целое число больше 25, неизвестная `cmap`, подписи, которые отвергает `merge_labels`, и `ax`, который не `Axes` matplotlib, дают `ParameterError`.

!!! note "Примечание"
    В ruTS цветовая карта по умолчанию - `PuOr`.
