# Исключения и логирование

## Исключения

Все исключения библиотеки наследуют базовый класс `RutsError` и один из встроенных классов Python, поэтому их можно ловить как по имени ruTS, так и по привычному встроенному типу - прежний код с `except ValueError` продолжает работать.

| Исключение | Встроенный класс | Когда поднимается |
| :--------- | :--------------- | :---------------- |
| `RutsError` | `Exception` | Базовый класс, сам не поднимается |
| `SourceTypeError` | `TypeError` | Источник данных не строка и не `Doc`, справочник не `Counter`, список текстов не список списков, путь не строка и не `Path`, токенизатор не вызываемый объект |
| `SourceError` | `ValueError` | В источнике нет слов, предложений, текстов или коллокаций, нет разбора зависимостей, текстов меньше, чем нужно мере, после отсева не осталось единиц |
| `ParameterError` | `ValueError` | Порог, окно, размер сегмента или число элементов вне допустимого диапазона; неизвестная мера, вариант, пресет, слой, ступень, категория набора данных |
| `UnknownStatError` | `ParameterError`, `KeyError` | По имени запрошена неизвестная статистика (`describe` классов статистик, `get_stats`, `print_stats` и `explain_text` у `MorphStats`, `DiversityStats.windowed`, `describe_level_norm`) |
| `DatasetNotFoundError` | `OSError` | Набор данных не загружен; текст подсказывает команду загрузки |
| `DataFileError` | `ValueError` | Файл набора данных поврежден, имеет неожиданный формат или не декодируется |
| `DownloadError` | `RuntimeError` | Файл не удалось скачать или он не прошел проверку контрольной суммы |

Классы доступны из `ruts` и из `ruts.exceptions`. Это классы ядра [anyTS](https://sergeyshk.github.io/anyTS/exceptions/) под теми же именами, а `RutsError` - его `anyts.exceptions.AnyTSError`: псевдонимы, а не подклассы, поэтому `except RutsError` ловит и ошибки, поднятые кодом ядра, а в трассировке стоит `anyts.exceptions.SourceError`. Сообщения ruTS - на русском, в том числе сообщения классов статистик, экстракторов, компонентов и подсветки, построенных на ядре (`ruts.constants.CORE_MESSAGES`). На английском остаются проверки типов аргументов в коде ядра (строка вместо числа и т. п.) и отдельные функции ядра.

=== "Код"

    ``` python
    from ruts import BasicStats, RutsError, SourceError
    from ruts.datasets import PoetryCorpus

    try:
        BasicStats("...")
    except SourceError as e:
        print(e)

    try:
        list(PoetryCorpus(data_dir="/nowhere").get_texts(limit=1))
    except RutsError as e:
        print(type(e).__name__)
    ```

=== "Результат"

    ```
    В источнике данных отсутствуют слова
    DatasetNotFoundError
    ```

## Логирование

Библиотека ничего не печатает сама: сообщения о загрузке и извлечении наборов данных (методы `download()`) ядро anyTS отправляет в логгер `anyts` уровня `INFO`. По умолчанию у логгера стоит `NullHandler`, и сообщения не видны; чтобы включить их, настройте логирование в приложении:

=== "Код"

    ``` python
    import logging

    from ruts.datasets import SovChLit

    logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
    SovChLit(data_dir="/tmp/ruts_data").download()
    ```

=== "Результат"

    ```
    anyts.datasets: Downloading the file https://github.com/SergeyShk/ruTS/raw/master/ruts/datasets/data/sov_chrest_lit_v1.tar.xz
    anyts.datasets: The file is downloaded: /tmp/ruts_data/sov_chrest_lit_v1.tar.xz
    anyts.datasets: Extracting the archive /tmp/ruts_data/sov_chrest_lit_v1.tar.xz
    ```

Методы `print_stats()` классов статистик и `print_kwic()` печатают в стандартный вывод по своему назначению, логирование их не касается.
