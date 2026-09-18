# Collected works of Stalin

!!! info ""
    **ruts.datasets.StalinWorks**

## Description

A module for working with the dataset of the complete collected works of J.V. Stalin.

The dataset is built from the 16 main volumes of the digitized complete collected works:

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

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `data_dir` | str | `DEFAULT_DATA_DIR.joinpath("texts")` | Path to the dataset directory |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `labels` | tuple[str] | Tuple of volume numbers |

## Methods

### download

Downloads the dataset from the network and extracts the files.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `force` | bool | `-` | Download the dataset even if it is already downloaded |

An example of downloading the dataset and printing its information:

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts.datasets import StalinWorks

    # Create the dataset object
    sw = StalinWorks(data_dir=".")

    # Download the dataset
    sw.download(force=True)

    # Show the dataset information
    sw.info
    ```

    _Result_:

    ``` bash
    {'Наименование': 'stalin_works',
    'url': 'https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/JMPSDM',
    'description': 'Полное собрание сочинений И.В. Сталина',
    'author': 'Шкарин С.С.'}
    ```

### get_texts

Extracts texts (without headers) from the dataset.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `volume` | int | `-` | Volume number |
| `year` | int | `-` | Year of writing |
| `text_type` | str | `-` | Text type |
| `is_translation` | bool | `-` | Translation flag |
| `source` | str | `-` | Original source of the texts |
| `subject` | str | `-` | Text title |
| `topic` | str | `-` | Text subsection title |
| `min_len` | int | `-` | Minimum text length (in characters) |
| `max_len` | int | `-` | Maximum text length (in characters) |
| `limit` | int | `-` | Number of texts |

An example of extracting texts from the dataset, taking only one letter of 1937:

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts.datasets import StalinWorks

    # Create the dataset object
    sw = StalinWorks()

    # Show the extracted texts
    for i in sw.get_texts(year=1937, text_type="Письмо", limit=1):
        print(i)
    ```

    _Result_:

    ``` bash
    Маме – моей привет!
    Как живет, как чувствует себя мама – моя? Передают, что ты здорова и бодра. Правда это? Если это правда, то я бесконечно рад этому. Наш род, видимо, крепкий род.
    Я здоров.
    Мои дети тоже чувствуют себя хорошо.
    Желаю здоровья, живи долгие годы, мама – моя.
    Твой Coco.
    10. III.37 г.
    ```

### get_records

Extracts records (with headers) from the dataset.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `volume` | int | `-` | Volume number |
| `year` | int | `-` | Year of writing |
| `text_type` | str | `-` | Text type |
| `is_translation` | bool | `-` | Translation flag |
| `source` | str | `-` | Original source of the texts |
| `subject` | str | `-` | Text title |
| `topic` | str | `-` | Text subsection title |
| `min_len` | int | `-` | Minimum text length (in characters) |
| `max_len` | int | `-` | Maximum text length (in characters) |
| `limit` | int | `-` | Number of texts |

An example of extracting records from the dataset, taking only one letter of 1937:

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts.datasets import StalinWorks

    # Create the dataset object
    sw = StalinWorks()

    # Show the extracted records
    for i in sw.get_records(year=1937, text_type="Письмо", limit=1):
        print(i)
    ```

    _Result_:

    ``` bash
    {'file': PosixPath('../ruTS/ruts_data/texts/stalin_works/volume_14/59'),
    'is_translation': False,
    'source': 'Книга "Иосиф Сталин в объятиях семьи"',
    'subject': 'Письмо матери 10 марта 1937 года',
    'text': 'Маме – моей привет!\n'
            'Как живет, как чувствует себя мама – моя? Передают, что ты здорова и '
            'бодра. Правда это? Если это правда, то я бесконечно рад этому. Наш '
            'род, видимо, крепкий род.\n'
            'Я здоров.\n'
            'Мои дети тоже чувствуют себя хорошо.\n'
            'Желаю здоровья, живи долгие годы, мама – моя.\n'
            'Твой Coco.\n'
            '10.\xa0III.37\xa0г.',
    'topic': '',
    'type': 'Письмо',
    'volume': 14,
    'year': 1937}
    ```
