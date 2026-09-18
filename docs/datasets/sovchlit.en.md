# Soviet literature readers

!!! info ""
    **ruts.datasets.SovChLit**

## Description

A module for working with the dataset of Soviet reading-books for literature classes.

The dataset is built from digitized editions of the ["School textbooks of the USSR"](https://sheba.spb.ru/shkola/) project:

*   Родная речь. Книга для чтения в I классе начальной школы. Е.Е. Соловьева, Л.А. Карпинская, Н.Н. Щепетова

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `data_dir` | str | `DEFAULT_DATA_DIR.joinpath("texts")` | Path to the dataset directory |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `labels` | tuple[str] | Tuple of text grade levels |

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
    from ruts.datasets import SovChLit

    # Create the dataset object
    sc = SovChLit(data_dir=".")

    # Download the dataset
    sc.download(force=True)

    # Show the dataset information
    sc.info
    ```

    _Result_:

    ``` bash
    {'Наименование': 'sov_chrest_lit',
    'url': 'https://dataverse.harvard.edu/file.xhtml?fileId=3670902&version=DRAFT',
    'description': 'Корпус советских хрестоматий по литературе',
    'author': 'Шкарин С.С.'}
    ```

### get_texts

Extracts texts (without headers) from the dataset.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `grade` | int | `-` | Grade level of the texts |
| `book` | str | `-` | Book title |
| `year` | int | `-` | Year of publication |
| `category` | str | `-` | Text category |
| `text_type` | str | `-` | Text type |
| `subject` | str | `-` | Text title |
| `author` | str | `-` | Text author |
| `min_len` | int | `-` | Minimum text length (in characters) |
| `max_len` | int | `-` | Maximum text length (in characters) |
| `limit` | int | `-` | Number of texts |

An example of extracting texts from the dataset, taking only one text of the "Весна" (spring) category no longer than 100 characters:

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts.datasets import SovChLit

    # Create the dataset object
    sc = SovChLit()

    # Show the extracted texts
    for i in sc.get_texts(max_len=100, category="Весна", limit=1):
        print(i)
    ```

    _Result_:

    ``` bash
    Рыхлый снег темнеет в марте, тают льдинки на окне.
    Зайчик бегает по парте и по карте на стене.
    ```

### get_records

Extracts records (with headers) from the dataset.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `grade` | int | `-` | Grade level of the texts |
| `book` | str | `-` | Book title |
| `year` | int | `-` | Year of publication |
| `category` | str | `-` | Text category |
| `text_type` | str | `-` | Text type |
| `subject` | str | `-` | Text title |
| `author` | str | `-` | Text author |
| `min_len` | int | `-` | Minimum text length (in characters) |
| `max_len` | int | `-` | Maximum text length (in characters) |
| `limit` | int | `-` | Number of texts |

An example of extracting records from the dataset, taking only one record of the "Весна" (spring) category no longer than 100 characters:

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts.datasets import SovChLit

    # Create the dataset object
    sc = SovChLit()

    # Show the extracted records
    for i in sc.get_records(max_len=100, category="Весна", limit=1):
        print(i)
    ```

    _Result_:

    ``` bash
    {'author': 'С. Маршак',
    'book': 'Родная речь. Книга для чтения в I классе начальной школы',
    'category': 'Весна',
    'file': PosixPath('../ruTS/ruts_data/texts/sov_chrest_lit/grade_1/114'),
    'grade': 1,
    'subject': 'Март',
    'text': 'Рыхлый снег темнеет в марте, тают льдинки на окне.\n'
            'Зайчик бегает по парте и по карте на стене.',
    'type': 'Стихотворение',
    'year': 1963}
    ```
