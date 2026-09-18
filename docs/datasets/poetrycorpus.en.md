# Russian poetry corpus

!!! info ""
    **ruts.datasets.PoetryCorpus**

## Description

A module for working with the Russian poetry corpus [PoetryCorpus](https://github.com/IlyaGusev/PoetryCorpus) collected by Ilya Gusev for the [rupo](https://github.com/IlyaGusev/rupo) library: 16,694 poems by 195 authors of the 18th-20th centuries, 13 million characters. Every poem has an author and a title (or its first line), 12,857 have years of writing (from 1725 to 1996), 3,904 have themes, 20 themes in total:

| Theme | Poems | Theme | Poems |
| :---- | :---: | :---- | :---: |
| О любви (love) | 2,839 | О природе (nature) | 76 |
| Военные (war) | 724 | Патриотические (patriotic) | 72 |
| О дружбе (friendship) | 155 | Посвящения (dedications) | 38 |
| Детские (children's) | 106 | the other 13 themes | up to 30 each |
| О животных (animals) | 78 | | |

The most poems are by Vysotsky (539), Pushkin (401), Blok (286), Akhmatova (277) and Fet (251). The corpus is distributed under the [Apache-2.0](https://github.com/IlyaGusev/PoetryCorpus/blob/master/LICENSE) license and suits [stylometry](../corpus/stylometry.md) - comparing authors and periods, verse studies and model training.

The corpus file (27 MB) is downloaded from the repository at a pinned commit and verified against a SHA-256 checksum; it is read as a stream, so memory does not depend on the corpus size.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `data_dir` | str | `DEFAULT_DATA_DIR.joinpath("texts")` | Path to the dataset directory |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `authors` | Counter | Number of poems per author |
| `themes` | Counter | Number of poems per theme |

## Methods

### download

Downloads the corpus file from the network with checksum verification.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `force` | bool | `-` | Download the dataset even if it is already downloaded |

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts.datasets import PoetryCorpus

    # Create the dataset object
    pc = PoetryCorpus(data_dir=".")

    # Download the dataset
    pc.download()

    # Show the dataset information
    pc.info
    ```

    _Result_:

    ``` bash
    {'Наименование': 'poetry_corpus',
    'author': 'Гусев И.О.',
    'description': 'Корпус русской поэзии PoetryCorpus',
    'license': 'Apache-2.0',
    'url': 'https://github.com/IlyaGusev/PoetryCorpus'}
    ```

### get_texts

Extracts texts (without headers) from the dataset.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `author` | str | `-` | Author (case-insensitive substring) |
| `theme` | str | `-` | Theme (case-insensitive substring) |
| `year_from` | int | `-` | Earliest year of writing |
| `year_to` | int | `-` | Latest year of writing |
| `min_len` | int | `-` | Minimum text length (in characters) |
| `max_len` | int | `-` | Maximum text length (in characters) |
| `limit` | int | `-` | Number of texts |

Poems without a year do not pass the year filters.

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts.datasets import PoetryCorpus

    # Create the dataset object
    pc = PoetryCorpus()

    # Show the extracted texts
    for text in pc.get_texts(author="Лермонтов", theme="О любви", limit=1):
        print(text[:60])
    ```

    _Result_:

    ``` bash
    Благодарю!.. Вчера мое признанье
    И стих мой ты без смеха при
    ```

### get_records

Extracts records (with headers) from the dataset. Record fields: `author` - author, `title` - title or first line, `themes` - tuple of themes (empty without annotation), `year_from` and `year_to` - years of writing (`None` without a date), `text` - text.

The parameters are the same as for `get_texts`.

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    from ruts import WordsExtractor
    from ruts.corpus import delta
    from ruts.datasets import PoetryCorpus

    # Create the dataset object
    pc = PoetryCorpus()

    # Burrows's Delta between poets over all their poems
    we = WordsExtractor(lowercase=True)
    corpus = {
        author: we.extract("\n".join(pc.get_texts(author=author)))
        for author in ("Александр Пушкин", "Михаил Лермонтов", "Анна Ахматова", "Владимир Высоцкий")
    }
    delta(corpus, n_mfw=200, variant="cosine").round(2)
    ```

    _Result_:

    ``` bash
                       Александр Пушкин  Михаил Лермонтов  Анна Ахматова  Владимир Высоцкий
    Александр Пушкин               0.00              1.03           1.39               1.43
    Михаил Лермонтов               1.03              0.00           1.38               1.52
    Анна Ахматова                  1.39              1.38           0.00               1.23
    Владимир Высоцкий              1.43              1.52           1.23               0.00
    ```
