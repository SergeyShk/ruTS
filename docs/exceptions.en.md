# Exceptions and logging

!!! info ""
    **ruts.exceptions**

## Exceptions

All library exceptions inherit the base class `RutsError` and one of the built-in Python classes, so they can be caught both by their ruTS name and by the familiar built-in type - existing code with `except ValueError` keeps working.

| Exception | Built-in class | When raised |
| :-------- | :------------- | :---------- |
| `RutsError` | `Exception` | Base class, never raised itself |
| `SourceTypeError` | `TypeError` | The data source is neither a string nor a `Doc`, the frequency counter is not a `Counter`, the list of texts is not a list of lists, the path is neither a string nor a `Path`, the tokenizer is not callable |
| `SourceError` | `ValueError` | The source has no words, sentences, texts or collocations, lacks a dependency parse, has fewer texts than the measure needs, or nothing is left after culling |
| `ParameterError` | `ValueError` | A threshold, window, segment size or number of items is out of range; an unknown measure, variant, preset, layer, stage or dataset category |
| `UnknownStatError` | `ParameterError`, `KeyError` | An unknown statistic is requested from `MorphStats.explain_text` |
| `DatasetNotFoundError` | `OSError` | The dataset is not downloaded; the message shows the download command |
| `DataFileError` | `ValueError` | A dataset file is corrupted, has an unexpected format or cannot be decoded |
| `DownloadError` | `RuntimeError` | The file could not be downloaded or failed the checksum verification |

The classes are available from `ruts` and from `ruts.exceptions`.

!!! example "Example"

    ``` python
    from ruts import BasicStats, RutsError, SourceError
    from ruts.datasets import PoetryCorpus

    try:
        BasicStats("...")
    except SourceError as e:
        print(e)
    # В источнике данных отсутствуют слова

    try:
        list(PoetryCorpus(data_dir="/nowhere").get_texts(limit=1))
    except RutsError as e:
        print(type(e).__name__)
    # DatasetNotFoundError
    ```

## Logging

The library prints nothing on its own: messages about downloading and extracting datasets (`download_file`, `extract_archive`, the `download()` methods) go to the `ruts` logger at the `INFO` level. The logger has a `NullHandler` by default, so the messages are silent; to see them, configure logging in your application:

!!! example "Example"

    ``` python
    import logging

    from ruts.datasets import RussianLiterature

    logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
    RussianLiterature().download()
    # ruts.utils: Загрузка файла https://github.com/d0rj/RusLit/archive/....zip
    # ruts.utils: Файл загружен: .../ruts_data/texts/russian_literature.zip
    # ruts.utils: Извлечение файлов из архива .../ruts_data/texts/russian_literature.zip
    ```

The `print_stats()` methods of the statistics classes and `print_kwic()` write to standard output by design; logging does not affect them.
