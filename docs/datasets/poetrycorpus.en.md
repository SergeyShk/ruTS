# Russian poetry corpus

``` {.python .signature}
PoetryCorpus(data_dir=DEFAULT_DATASET_DIR)
```

The Russian poetry corpus [PoetryCorpus](https://github.com/IlyaGusev/PoetryCorpus) collected by Ilya Gusev for the [rupo](https://github.com/IlyaGusev/rupo) library: 16,694 poems by 195 authors of the 18th-20th centuries, 13 million characters. Every poem has an author and a title (or its first line), 12,857 have years of writing (from 1725 to 1996), 3,904 have themes, 20 themes in total:

| Theme | Poems | Theme | Poems |
| :---- | :---- | :---- | :---- |
| О любви (love) | 2,839 | О природе (nature) | 76 |
| Военные (war) | 724 | Патриотические (patriotic) | 72 |
| О дружбе (friendship) | 155 | Посвящения (dedications) | 38 |
| Детские (children's) | 106 | Спортивные (sports) | 36 |
| О животных (animals) | 78 | the other 11 themes | up to 21 each |

The most poems are by Vysotsky (539), Pushkin (401), Blok (286), Akhmatova (277) and Fet (251). The corpus is distributed under the [Apache-2.0](https://github.com/IlyaGusev/PoetryCorpus/blob/master/LICENSE) license and suits [stylometry](../corpus/stylometry.md) - comparing authors and periods, verse studies and model training.

The corpus file (27 MB) is downloaded from the repository at a pinned commit and verified against a SHA-256 checksum; it is read as a stream, so memory does not depend on the corpus size.

Raises:

- `SourceTypeError` - a `data_dir` that is neither a string nor a `Path`.

=== "Code"

    ``` python
    from ruts.datasets import PoetryCorpus

    pc = PoetryCorpus()
    pc.download()
    pc.info
    ```

=== "Result"

    ```
    {'Наименование': 'poetry_corpus',
     'url': 'https://github.com/IlyaGusev/PoetryCorpus',
     'description': 'Корпус русской поэзии PoetryCorpus',
     'author': 'Гусев И.О.',
     'license': 'Apache-2.0'}
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `data_dir` | `str` / `Path` | `DEFAULT_DATASET_DIR` | Path to the dataset directory; `texts` in `DEFAULT_DATA_DIR` by default |

## Attributes

| Attribute | Type | Description |
| :-------- | :--- | :---------- |
| `authors` | `Counter` | Number of poems per author |
| `themes` | `Counter` | Number of poems per theme |
| `info` | `dict[str, str]` | Name of the dataset and reference information about it |

## Methods

`download(force=False)` downloads the corpus file from the network with checksum verification; a corrupted or replaced file is deleted and downloaded again in the same call.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `force` | `bool` | `False` | Download the dataset even if it is already downloaded |

A file that cannot be downloaded or fails the checksum twice raises `DownloadError`.

`check_data()` checks that the corpus file is in place and returns `True`; a corpus that is not downloaded raises `DatasetNotFoundError` with the commands to download it.

`get_texts(author=None, theme=None, year_from=None, year_to=None, min_len=None, max_len=None, limit=None)` extracts texts (without headers) from the dataset.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `author` | `str` | `None` | Author (substring, ignoring case and ё) |
| `theme` | `str` | `None` | Theme (substring, ignoring case and ё) |
| `year_from` | `int` | `None` | Earliest year of writing |
| `year_to` | `int` | `None` | Latest year of writing |
| `min_len` | `int` | `None` | Minimum text length (in characters) |
| `max_len` | `int` | `None` | Maximum text length (in characters) |
| `limit` | `int` | `None` | Number of texts |

Poems without a year do not pass the year filters. An `author` or a `theme` that is not a string, an earliest year above the latest, a length bound that is not an integer of at least one, a minimum above the maximum and a `limit` that is not a non-negative integer raise `ParameterError`; a corpus that is not downloaded `DatasetNotFoundError`, a file the records cannot be extracted from `DataFileError`.

=== "Code"

    ``` python
    for text in pc.get_texts(author="Лермонтов", theme="О любви", limit=1):
        print(text[:60])
    ```

=== "Result"

    ```
    Благодарю!.. Вчера мое признанье
    И стих мой ты без смеха при
    ```

`get_records` with the same parameters extracts records (with headers) from the dataset. Record fields: `author` - author, `title` - title or first line, `themes` - tuple of themes (empty without annotation), `year_from` and `year_to` - years of writing (`None` without a date), `text` - text.

=== "Code"

    ``` python
    record = next(pc.get_records(author="Лермонтов", theme="О любви", limit=1))
    record["title"], record["themes"], record["year_from"], record["year_to"]
    ```

=== "Result"

    ```
    ('Благодарю!', ('О любви',), 1830, 1830)
    ```

Burrows's Delta between poets over all their poems:

=== "Code"

    ``` python
    from ruts import WordsExtractor
    from ruts.corpus import delta

    we = WordsExtractor(lowercase=True)
    corpus = {
        author: we.extract("\n".join(pc.get_texts(author=author)))
        for author in ("Александр Пушкин", "Михаил Лермонтов", "Анна Ахматова", "Владимир Высоцкий")
    }
    print(delta(corpus, n_mfw=200, variant="cosine").round(2).to_string())
    ```

=== "Result"

    ```
                       Александр Пушкин  Михаил Лермонтов  Анна Ахматова  Владимир Высоцкий
    Александр Пушкин               0.00              1.03           1.39               1.43
    Михаил Лермонтов               1.03              0.00           1.38               1.52
    Анна Ахматова                  1.39              1.38           0.00               1.23
    Владимир Высоцкий              1.43              1.52           1.23               0.00
    ```
