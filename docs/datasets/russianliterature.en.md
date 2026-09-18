# Russian classical literature

!!! info ""
    **ruts.datasets.RussianLiterature**

## Description

A module for working with the [RusLit](https://github.com/d0rj/RusLit) collection of Russian classical literature (on Kaggle - [russian-literature](https://www.kaggle.com/datasets/d0rj3228/russian-literature)): 373 works by 12 authors of the 19th - early 20th century, 39 million characters, three genres:

| Genre | Key | Authors | Works |
| :---- | :-- | :------ | :---: |
| Prose | `prose` | Chekhov (77), Tolstoy (42), Dostoevsky (33), Gorky (33), Bryusov (30), Gogol (16), Herzen (11), Pushkin (10), Turgenev (10), Blok (4), Lermontov (3) | 269 |
| Poetry | `poems` | Pushkin (35), Lermontov (18), Nekrasov (15), Blok (10) | 78 |
| Publicism | `publicism` | Tolstoy | 26 |

The texts are in the public domain (Kaggle states the PDDL license), collected from LitLib, Wikisource and Ilibrary. The year of writing is taken from the collection's `info.csv` files (`1825` or `1824-1825`); 28 works have none. The collection's folder names are in Latin script; records give authors by their Russian names from the `AUTHORS` table (`Chekhov` → «Антон Чехов»). The collection suits authorship attribution and genre comparison: texts of one author in different genres and of one genre by different authors.

The repository archive (20 MB) is downloaded at a pinned commit, verified against a SHA-256 checksum and extracted; texts are read one at a time, the single cp1251 file is decoded automatically.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `data_dir` | str | `DEFAULT_DATA_DIR.joinpath("texts")` | Path to the dataset directory |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `genres` | tuple[str] | Tuple of genres: `prose`, `poems`, `publicism` |
| `authors` | dict[str, str] | Russian author names by folder name |

## Methods

### download

Downloads the archive from the network with checksum verification and extracts the files.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `force` | bool | `-` | Download the dataset even if it is already downloaded |

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts.datasets import RussianLiterature

    # Create the dataset object
    rl = RussianLiterature(data_dir=".")

    # Download the dataset
    rl.download()

    # Show the dataset information
    rl.info
    ```

    _Result_:

    ``` bash
    {'Наименование': 'russian_literature',
    'author': 'd0rj',
    'description': 'Собрание русской классической литературы RusLit',
    'license': 'Общественное достояние (PDDL)',
    'url': 'https://github.com/d0rj/RusLit'}
    ```

### get_texts

Extracts texts (without headers) from the dataset.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `genre` | str | `-` | Genre: `prose`, `poems` or `publicism` |
| `author` | str | `-` | Author (case-insensitive substring of the Russian name) |
| `year_from` | int | `-` | Earliest year of writing |
| `year_to` | int | `-` | Latest year of writing |
| `min_len` | int | `-` | Minimum text length (in characters) |
| `max_len` | int | `-` | Maximum text length (in characters) |
| `limit` | int | `-` | Number of texts |

Works without a year do not pass the year filters.

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts.datasets import RussianLiterature

    # Create the dataset object
    rl = RussianLiterature()

    # Show the extracted texts
    for text in rl.get_texts(genre="poems", author="Пушкин", limit=1):
        print(text[:57])
    ```

    _Result_:

    ``` bash
    Роняет лес багряный свой убор,
    Сребрит мороз увянувшее по
    ```

!!! warning "Author name in the text"
    In the source most files begin with the author's name and the title («Александр Пушкин» and «19 ОКТЯБРЯ», «Валерий Брюсов. Бемоль», «Л.Н.Толстой», «Горький Максим»), which is a feature leak for authorship attribution. Such headers are stripped in unambiguous cases (`strip_header`): the first line is the record's author name in any of these forms, alone or with the record's title, the next line is the title; 288 of 373 texts are cleaned this way. The author's surname remains within the first 200 characters of 8 texts: headers in other forms («Антон Павлович Чехов. Палата No 6», «Горький Максим (Алексей Максимович Пешков)», «Лев Толстой. О НАУКЕ» with the title «О науке (Ответ крестьянину)») and dedications («Посвящается графине М. Н. Толстой»). For strict attribution check the beginnings of the texts or drop the first lines.

### get_records

Extracts records (with headers) from the dataset. Record fields: `genre` - genre, `author` - author, `title` - title, `year_from` and `year_to` - years of writing (`None` without a date), `text` - text without the author-and-title header, `file` - path to the file.

The parameters are the same as for `get_texts`.

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts.datasets import RussianLiterature

    # Create the dataset object
    rl = RussianLiterature()

    # Nekrasov's poems of the 1860s
    for record in rl.get_records(author="Некрасов", year_from=1860, year_to=1870):
        print(record["title"], record["year_from"], record["year_to"], len(record["text"]))
    ```

    _Result_:

    ``` bash
    Дедушка 1870 1870 11408
    Железная дорога 1864 1864 4952
    Мороз, красный нос 1862 1864 28773
    ```
