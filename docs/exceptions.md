# Исключения и логирование

## Исключения

Все исключения библиотеки наследуют базовый класс `RutsError` и один из встроенных классов Python, так что их можно ловить и по имени ruTS, и по встроенному типу, например `except ValueError`.

| Исключение | Встроенный класс | Когда поднимается |
| :--------- | :--------------- | :---------------- |
| `RutsError` | `Exception` | Базовый класс, сам не поднимается |
| `SourceTypeError` | `TypeError` | Аргумент не того типа: источник данных не строка и не `Doc`, справочник не `Counter`, токенизатор не вызываемый объект и т. п. |
| `SourceError` | `ValueError` | В источнике нет слов, предложений, текстов, коллокаций или разбора зависимостей, текстов меньше, чем нужно мере, после отсева ничего не осталось |
| `ParameterError` | `ValueError` | Значение параметра вне допустимого диапазона; неизвестная мера, пресет, слой, категория набора данных и т. п. |
| `UnknownStatError` | `ParameterError`, `KeyError` | По имени запрошена неизвестная статистика (`describe`, `DiversityStats.windowed`, `MorphStats.get_stats` и другие) |
| `DatasetNotFoundError` | `OSError` | Набор данных не загружен; текст подсказывает команду загрузки |
| `DataFileError` | `ValueError` | Файл набора данных поврежден, имеет неожиданный формат или не декодируется |
| `DownloadError` | `RuntimeError` | Файл не удалось скачать или он не прошел проверку контрольной суммы |

Классы доступны из `ruts` и `ruts.exceptions`. Это сами классы ядра [anyTS](https://sergeyshk.github.io/anyTS/exceptions/) (`RutsError` - его `AnyTSError`), а не подклассы: `except RutsError` ловит и ошибки кода ядра, а в трассировке стоит `anyts.exceptions.SourceError`. Сообщения - на русском, кроме проверок типов аргументов в коде ядра и отдельных функций ядра.

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

Сообщения о загрузке и извлечении наборов данных (`download()`) ядро anyTS пишет в логгер `anyts` с уровнем `INFO`. По умолчанию они не видны; чтобы их увидеть, настройте логирование в приложении:

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

`print_stats()` и `print_kwic()` печатают в стандартный вывод, логирование на них не влияет.
