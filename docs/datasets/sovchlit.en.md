# Soviet literature readers

``` {.python .signature}
SovChLit(data_dir=DEFAULT_DATASET_DIR)
```

The dataset of Soviet reading-books for literature classes. It is built from digitized editions of the ["School textbooks of the USSR"](https://sheba.spb.ru/shkola/) project:

*   Родная речь. Книга для чтения в I классе начальной школы. Е.Е. Соловьева, Л.А. Карпинская, Н.Н. Щепетова

Raises:

- `SourceTypeError` - a `data_dir` that is neither a string nor a `Path`.

=== "Code"

    ``` python
    from ruts.datasets import SovChLit

    sc = SovChLit()
    sc.download()
    sc.info
    ```

=== "Result"

    ```
    {'Наименование': 'sov_chrest_lit',
     'url': 'https://dataverse.harvard.edu/file.xhtml?fileId=3670902&version=DRAFT',
     'description': 'Корпус советских хрестоматий по литературе',
     'author': 'Шкарин С.С.'}
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `data_dir` | `str` / `Path` | `DEFAULT_DATASET_DIR` | Path to the dataset directory; `texts` in `DEFAULT_DATA_DIR` by default |

## Attributes

| Attribute | Type | Description |
| :-------- | :--- | :---------- |
| `labels` | `tuple[str]` | Tuple of text grade levels |
| `info` | `dict[str, str]` | Name of the dataset and reference information about it |

## Methods

`download(force=False)` downloads the archive `sov_chrest_lit_v1.tar.xz` from the network with checksum verification and extracts the files into the `sov_chrest_lit_v1` directory.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `force` | `bool` | `False` | Download the dataset even if it is already downloaded |

An archive that cannot be downloaded or fails the checksum twice raises `DownloadError`, an archive that cannot be extracted `DataFileError`.

`check_data()` checks that the dataset is downloaded completely and returns `True`; a dataset that is not downloaded or incomplete raises `DatasetNotFoundError` with the commands to download it.

`get_texts(grade=None, book=None, year=None, category=None, text_type=None, subject=None, author=None, min_len=None, max_len=None, limit=None)` extracts texts (without headers) from the dataset.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `grade` | `int` | `None` | Grade level of the texts (only 1) |
| `book` | `str` | `None` | Book title (substring, ignoring case and ё) |
| `year` | `int` | `None` | Year of publication |
| `category` | `str` | `None` | Text category (substring, ignoring case and ё) |
| `text_type` | `str` | `None` | Text type: `Рассказ`, `Стихотворение`, `Сказка`, `Пословица`, `Загадка`, `Песня`, `Басня`, `Совет` or `Шутка` |
| `subject` | `str` | `None` | Text title (substring, ignoring case and ё) |
| `author` | `str` | `None` | Text author (substring, ignoring case and ё) |
| `min_len` | `int` | `None` | Minimum text length (in characters) |
| `max_len` | `int` | `None` | Maximum text length (in characters) |
| `limit` | `int` | `None` | Number of texts |

An unknown grade level or text type, a `book`, `category`, `subject` or `author` that is not a string, a length bound that is not an integer of at least one, a minimum above the maximum and a `limit` that is not a non-negative integer raise `ParameterError`; a dataset that is not downloaded `DatasetNotFoundError`, a file a record cannot be extracted from `DataFileError`.

=== "Code"

    ``` python
    for text in sc.get_texts(max_len=100, category="Весна", limit=1):
        print(text)
    ```

=== "Result"

    ```
    Рыхлый снег темнеет в марте, тают льдинки на окне.
    Зайчик бегает по парте и по карте на стене.
    ```

`get_records` with the same parameters extracts records (with headers) from the dataset. Record fields: `grade` - grade level, `book` - book, `year` - year of publication, `category` - category, `type` - text type, `subject` - title, `author` - author, `text` - text, `file` - path to the file.

=== "Code"

    ``` python
    record = next(sc.get_records(max_len=100, category="Весна", limit=1))
    del record["file"]
    record
    ```

=== "Result"

    ```
    {'grade': 1,
     'book': 'Родная речь. Книга для чтения в I классе начальной школы',
     'year': 1963,
     'category': 'Весна',
     'type': 'Стихотворение',
     'subject': 'Март',
     'author': 'С. Маршак',
     'text': 'Рыхлый снег темнеет в марте, тают льдинки на окне.\n'
             'Зайчик бегает по парте и по карте на стене.'}
    ```
