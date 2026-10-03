# Исключения и логирование

!!! info ""
    **ruts.exceptions**

## Исключения

Все исключения библиотеки наследуют базовый класс `RutsError` и один из встроенных классов Python, поэтому их можно ловить как по имени ruTS, так и по привычному встроенному типу - прежний код с `except ValueError` продолжает работать.

| Исключение | Встроенный класс | Когда поднимается |
| :--------- | :--------------- | :---------------- |
| `RutsError` | `Exception` | Базовый класс, сам не поднимается |
| `SourceTypeError` | `TypeError` | Источник данных не строка и не `Doc`, справочник не `Counter`, список текстов не список списков, путь не строка и не `Path`, токенизатор не вызываемый объект |
| `SourceError` | `ValueError` | В источнике нет слов, предложений, текстов или коллокаций, нет разбора зависимостей, текстов меньше, чем нужно мере, после отсева не осталось единиц |
| `ParameterError` | `ValueError` | Порог, окно, размер сегмента или число элементов вне допустимого диапазона; неизвестная мера, вариант, пресет, слой, ступень, категория набора данных |
| `UnknownStatError` | `ParameterError`, `KeyError` | По имени запрошена неизвестная статистика (`MorphStats.explain_text`, `DiversityStats.windowed`) |
| `DatasetNotFoundError` | `OSError` | Набор данных не загружен; текст подсказывает команду загрузки |
| `DataFileError` | `ValueError` | Файл набора данных поврежден, имеет неожиданный формат или не декодируется |
| `DownloadError` | `RuntimeError` | Файл не удалось скачать или он не прошел проверку контрольной суммы |

Классы доступны из `ruts` и из `ruts.exceptions`. Это классы ядра [anyTS](https://sergeyshk.github.io/anyTS/exceptions/) под теми же именами, а `RutsError` - его `anyts.exceptions.AnyTSError`: псевдонимы, а не подклассы, поэтому `except RutsError` ловит и ошибки, поднятые кодом ядра, а в трассировке стоит `anyts.exceptions.SourceError`. Сообщения кода ядра - на английском, кода ruTS - на русском.

!!! example "Пример"

    ``` python
    from ruts import BasicStats, RutsError, SourceError
    from ruts.datasets import PoetryCorpus

    try:
        BasicStats("...")
    except SourceError as e:
        print(e)
    # The data source has no words

    try:
        list(PoetryCorpus(data_dir="/nowhere").get_texts(limit=1))
    except RutsError as e:
        print(type(e).__name__)
    # DatasetNotFoundError
    ```

## Логирование

Библиотека ничего не печатает сама: сообщения о загрузке и извлечении наборов данных (методы `download()`) ядро anyTS отправляет в логгер `anyts` уровня `INFO`. По умолчанию у логгера стоит `NullHandler`, и сообщения не видны; чтобы включить их, настройте логирование в приложении:

!!! example "Пример"

    ``` python
    import logging

    from ruts.datasets import RussianLiterature

    logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
    RussianLiterature().download()
    # anyts.datasets: Downloading the file https://github.com/d0rj/RusLit/archive/....zip
    # anyts.datasets: The file is downloaded: .../ruts_data/texts/russian_literature.zip
    # anyts.datasets: Extracting the archive .../ruts_data/texts/russian_literature.zip
    ```

Методы `print_stats()` классов статистик и `print_kwic()` печатают в стандартный вывод по своему назначению, логирование их не касается.
