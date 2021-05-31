# Литературная дактилоскопия

!!! info ""
    **ruts.visualizers.fingerprinting()**

## Описание

Визуализация литературной дактилоскопии (Literature Fingerprinting).

!!! note "Примечание"
    Более подробно с литературной дактилоскопией можно ознакомиться в данной [публикации](https://www.uni-konstanz.de/mmsp/pubsys/publishedFiles/KeOe07.pdf).

## Параметры

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `texts` | List[List[str]] | `-` | Список списков слов |
| `segment_len` | int | `10` | Размер сегмента |
| `metric` | Callable | `None` | Функция для подсчета метрики [лексического разнообразия](../stats/diversity_stats.md) |
| `x_size` | int | `800` | Ширина области для визуализации |
| `y_size` | int | `600` | Высота области для визуализации |
| `cmap` | str | `'PuOr'` | Цветовая карта |
| `is_return` | str | `True` | Возвращать объект Figure |

## Пример использования

Рассмотрим работу визуализатора на примере 100 текстов из набора данных [SovChLit](../datasets/sovchlit.md).

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    from ruts import WordsExtractor
    from ruts.datasets import SovChLit
    from ruts.diversity_stats import calc_simpson_index
    from ruts.visualizers import fingerprinting

    # Подготовка данных
    sc = SovChLit()
    texts = [text for text in sc.get_texts(limit=100)]

    # Подготовка списка списков слов
    words = []
    words_extractor = WordsExtractor(lowercase=True)
    for text in texts:
        words.append(words_extractor.extract(text))

    # Построение графика
    fingerprinting(words, 
        metric=calc_simpson_index, 
        x_size=1000, 
        y_size=800,
        is_return=False
    )
    ```

    _Результат_:

    ![ruts](../img/fingerprinting.png){: .center }