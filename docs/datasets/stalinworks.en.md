# Collected works of Stalin

``` {.python .signature}
StalinWorks(data_dir=DEFAULT_DATASET_DIR)
```

The dataset of the complete collected works of J.V. Stalin. It is built from the 16 main volumes of the digitized complete collected works:

*   Volume 1. Works of 1901-1907
*   Volume 2. Works of 1907-1913
*   Volume 3. Works of 1917 (March-October)
*   Volume 4. Works of 1917-1920
*   Volume 5. Works of 1921-1923
*   Volume 6. Works of 1924
*   Volume 7. Works of 1925
*   Volume 8. Works of 1926
*   Volume 9. Works of 1926-1927
*   Volume 10. Works of 1927
*   Volume 11. Works of 1928-1929
*   Volume 12. Works of 1929-1930
*   Volume 13. Works of 1930-1934
*   Volume 14. Works of 1934-1940
*   Volume 15. Works of 1941-1945
*   Volume 16. Works of 1946-1952

Raises:

- `SourceTypeError` - a `data_dir` that is neither a string nor a `Path`.

=== "Code"

    ``` python
    from ruts.datasets import StalinWorks

    sw = StalinWorks()
    sw.download()
    sw.info
    ```

=== "Result"

    ```
    {'Наименование': 'stalin_works',
     'url': 'https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/JMPSDM',
     'description': 'Полное собрание сочинений И.В. Сталина',
     'author': 'Шкарин С.С.'}
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `data_dir` | `str` / `Path` | `DEFAULT_DATASET_DIR` | Path to the dataset directory; `texts` in `DEFAULT_DATA_DIR` by default |

## Attributes

| Attribute | Type | Description |
| :-------- | :--- | :---------- |
| `labels` | `tuple[str]` | Tuple of volume numbers |
| `info` | `dict[str, str]` | Name of the dataset and reference information about it |

## Methods

`download(force=False)` downloads the archive `stalin_works_v1.tar.xz` from the network with checksum verification and extracts the files into the `stalin_works_v1` directory.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `force` | `bool` | `False` | Download the dataset even if it is already downloaded |

An archive that cannot be downloaded or fails the checksum twice raises `DownloadError`, an archive that cannot be extracted `DataFileError`.

`check_data()` checks that the dataset is downloaded completely and returns `True`; a dataset that is not downloaded or incomplete raises `DatasetNotFoundError` with the commands to download it.

`get_texts(volume=None, year=None, text_type=None, is_translation=None, source=None, subject=None, topic=None, min_len=None, max_len=None, limit=None)` extracts texts (without headers) from the dataset.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `volume` | `int` | `None` | Volume number |
| `year` | `int` | `None` | Year of writing |
| `text_type` | `str` | `None` | Text type |
| `is_translation` | `bool` | `None` | Translation flag |
| `source` | `str` | `None` | Original source of the texts (substring, ignoring case and ё) |
| `subject` | `str` | `None` | Text title (substring, ignoring case and ё) |
| `topic` | `str` | `None` | Text subsection title (substring, ignoring case and ё) |
| `min_len` | `int` | `None` | Minimum text length (in characters) |
| `max_len` | `int` | `None` | Maximum text length (in characters) |
| `limit` | `int` | `None` | Number of texts |

A volume number outside 1-16, an unknown text type, a length bound that is not an integer of at least one, a minimum above the maximum and a `limit` that is not a non-negative integer raise `ParameterError`; a dataset that is not downloaded `DatasetNotFoundError`, a file a record cannot be extracted from `DataFileError`.

=== "Code"

    ``` python
    for text in sw.get_texts(year=1937, text_type="Письмо", limit=1):
        print(text)
    ```

=== "Result"

    ```
    Маме – моей привет!
    Как живет, как чувствует себя мама – моя? Передают, что ты здорова и бодра. Правда это? Если это правда, то я бесконечно рад этому. Наш род, видимо, крепкий род.
    Я здоров.
    Мои дети тоже чувствуют себя хорошо.
    Желаю здоровья, живи долгие годы, мама – моя.
    Твой Coco.
    10. III.37 г.
    ```

`get_records` with the same parameters extracts records (with headers) from the dataset. Record fields: `volume` - volume number, `year` - year of writing, `type` - text type, `is_translation` - translation flag, `source` - original source, `subject` - title, `topic` - subsection, `text` - text, `file` - path to the file.

=== "Code"

    ``` python
    record = next(sw.get_records(year=1937, text_type="Письмо", limit=1))
    del record["file"]
    record
    ```

=== "Result"

    ```
    {'volume': 14,
     'year': 1937,
     'type': 'Письмо',
     'is_translation': False,
     'source': 'Книга "Иосиф Сталин в объятиях семьи"',
     'subject': 'Письмо матери 10 марта 1937 года',
     'topic': '',
     'text': 'Маме – моей привет!\n'
             'Как живет, как чувствует себя мама – моя? Передают, что ты здорова и бодра. '
             'Правда это? Если это правда, то я бесконечно рад этому. Наш род, видимо, '
             'крепкий род.\n'
             'Я здоров.\n'
             'Мои дети тоже чувствуют себя хорошо.\n'
             'Желаю здоровья, живи долгие годы, мама – моя.\n'
             'Твой Coco.\n'
             '10.\xa0III.37\xa0г.'}
    ```
