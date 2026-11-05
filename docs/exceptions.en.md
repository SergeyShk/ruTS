# Exceptions and logging

## Exceptions

All library exceptions inherit the base class `RutsError` and one of the built-in Python classes, so they can be caught both by their ruTS name and by the built-in type, for example `except ValueError`.

| Exception | Built-in class | When raised |
| :-------- | :------------- | :---------- |
| `RutsError` | `Exception` | Base class, never raised itself |
| `SourceTypeError` | `TypeError` | An argument of a wrong type: the data source is neither a string nor a `Doc`, the frequency counter is not a `Counter`, the tokenizer is not callable and the like |
| `SourceError` | `ValueError` | The source has no words, sentences, texts, collocations or dependency parse, has fewer texts than the measure needs, or nothing is left after culling |
| `ParameterError` | `ValueError` | A parameter value is out of range; an unknown measure, preset, layer, dataset category and the like |
| `UnknownStatError` | `ParameterError`, `KeyError` | An unknown statistic is requested by name (`describe`, `DiversityStats.windowed`, `MorphStats.get_stats` and others) |
| `DatasetNotFoundError` | `OSError` | The dataset is not downloaded; the message shows the download command |
| `DataFileError` | `ValueError` | A dataset file is corrupted, has an unexpected format or cannot be decoded |
| `DownloadError` | `RuntimeError` | The file could not be downloaded or failed the checksum verification |

The classes are available from `ruts` and `ruts.exceptions`. They are the very classes of the [anyTS](https://sergeyshk.github.io/anyTS/exceptions/) core (`RutsError` is its `AnyTSError`), not subclasses: `except RutsError` catches the errors of the core code too, and a traceback shows `anyts.exceptions.SourceError`. The messages are in Russian, except the argument type checks in the core code and some core functions.

=== "Code"

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

=== "Result"

    ```
    В источнике данных отсутствуют слова
    DatasetNotFoundError
    ```

## Logging

The anyTS core writes messages about downloading and extracting datasets (`download()`) to the `anyts` logger at the `INFO` level. They are silent by default; to see them, configure logging in your application:

=== "Code"

    ``` python
    import logging

    from ruts.datasets import SovChLit

    logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
    SovChLit(data_dir="/tmp/ruts_data").download()
    ```

=== "Result"

    ```
    anyts.datasets: Downloading the file https://github.com/SergeyShk/ruTS/raw/master/ruts/datasets/data/sov_chrest_lit_v1.tar.xz
    anyts.datasets: The file is downloaded: /tmp/ruts_data/sov_chrest_lit_v1.tar.xz
    anyts.datasets: Extracting the archive /tmp/ruts_data/sov_chrest_lit_v1.tar.xz
    ```

`print_stats()` and `print_kwic()` write to standard output; logging does not affect them.
