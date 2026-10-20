# Закон Ципфа

<!-- core: visualizers/zipf.md:zipf a98a76b -->
``` {.python .signature}
zipf(counter, num_words=None, num_labels=10, log=True, show_theory=False, alpha=1.5, show_fit=False, ax=None, labels=None)
```

Построение графика [закона Ципфа](https://ru.wikipedia.org/wiki/%D0%97%D0%B0%D0%BA%D0%BE%D0%BD_%D0%A6%D0%B8%D0%BF%D1%84%D0%B0) по справочнику частотности слов.

!!! quote "Определение"

    Зако́н Ци́пфа («ранг-частота») - эмпирическая закономерность частоты слов естественного языка: если слова языка или достаточно длинного текста упорядочить по убыванию частоты, частота n-го слова окажется приблизительно обратно пропорциональной его рангу n. Второе по частоте слово встречается примерно в два раза реже первого, третье - в три раза реже, и так далее.

Это функции ядра [anyTS](https://sergeyshk.github.io/anyTS/visualizers/zipf/) с русскими подписями из `ruts.constants.VISUALIZER_LABELS` по умолчанию; `labels` задает подписи поверх них, например `labels={"title": "Закон Ципфа в SovChLit"}`.

График по 100 текстам набора данных [SovChLit](../datasets/sovchlit.md):

``` python
from collections import Counter

from ruts import WordsExtractor
from ruts.datasets import SovChLit
from ruts.style_stats import is_stopword
from ruts.visualizers import zipf

text = "\n".join(SovChLit().get_texts(limit=100))
we = WordsExtractor(use_lexemes=True, filter_nums=True)
counts = Counter(word for word in we.extract(text) if not is_stopword(word))
ax = zipf(counts, num_words=100, num_labels=10, log=False, show_theory=True, alpha=1.1)
ax.figure.savefig("zipf.png")
```

![ruts](../img/zipf.png){: .center }

## Параметры

<!-- core: visualizers/zipf.md:zipf-parameters c030ff5 -->
| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `counter` | `Counter` | - | Справочник частотности слов |
| `num_words` | `int` | `None` | Количество самых частотных слов |
| `num_labels` | `int` | `10` | Количество слов, подписанных на графике |
| `log` | `bool` | `True` | Использовать логарифмическую шкалу |
| `show_theory` | `bool` | `False` | Отображать теоретический закон Ципфа |
| `alpha` | `float` | `1.5` | Показатель α теоретического закона Ципфа, больше нуля |
| `show_fit` | `bool` | `False` | Отображать кривую подгонки закона Ципфа-Мандельброта $f(r) = C / (r + q)^s$ по `fit_zipf_mandelbrot` |
| `ax` | `Axes` | `None` | Оси matplotlib для графика; если не заданы, создается новая фигура |
| `labels` | `dict[str, str]` | `None` | Подписи графика поверх подписей по умолчанию: `title`, `xlabel`, `ylabel`, `experimental` и `theoretical` (кривые), `fit` (строка формата с `q` и `s`) |

Функция возвращает оси `Axes` с графиком; `num_words` больше числа лексем не удлиняет кривые за пределы данных. Справочник, который не `Counter` строк, дает `SourceTypeError`, а пустой справочник или частота не больше нуля - `SourceError`. `num_words` меньше единицы, отрицательный `num_labels`, при `show_theory` показатель, который не конечное число больше нуля, подписи, которые отвергает `merge_labels`, и `ax`, который не `Axes` matplotlib, дают `ParameterError`. Все эти ошибки возникают до создания фигуры.

Подгонка закона Ципфа-Мандельброта описана в [`fit_zipf_mandelbrot`](../stats/diversity_stats.md#fit_zipf_mandelbrot).

## Теоретический закон { #zipf_theory }

<!-- core: visualizers/zipf.md:zipf_theory 20746c7 -->
``` {.python .signature}
zipf_theory(size, num_ranks, alpha=1.5, ax=None, labels=None)
```

Только теоретическая кривая, $f(r) = size \cdot r^{-\alpha}$ для рангов от 1 до `num_ranks`.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `size` | `int` / `float` | - | Частота первого ранга |
| `num_ranks` | `int` | - | Количество рангов |
| `alpha` | `float` | `1.5` | Показатель α |
| `ax` | `Axes` | `None` | Оси matplotlib для графика; если не заданы, создается новая фигура |
| `labels` | `dict[str, str]` | `None` | Подписи поверх подписей по умолчанию: `theoretical` (кривая) |

`size` или `alpha`, который не конечное число больше нуля, `num_ranks`, который не целое число не меньше единицы, подписи, которые отвергает `merge_labels`, и `ax`, который не `Axes` matplotlib, дают `ParameterError`.
