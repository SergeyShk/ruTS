# Koziev stress dictionary

``` {.python .signature}
StressDict(data_dir=DEFAULT_DATASET_DIR)
```

Ilya Koziev's [stress dictionary](https://github.com/Koziev/NLP_Datasets#ударения) (all_accents): 1,680,535 word forms with the position of the primary stress. Data from Wikipedia and Wiktionary is extended with forms from the inflection tables of the author's grammar dictionary under the assumption that stress does not move in inflection: forms with mobile stress (воды́ - во́ды) get one variant, homographs (за́мок - замо́к) share one line, ё is replaced with е.

License - CC0. The dictionary is downloaded from the author's repository at a pinned commit (a 10.6 MB archive, a 77 MB file) and read once per process: loading takes a fraction of a second, the dictionary occupies about 100 MB of memory.

The dictionary is used by [`VerseStats`](../stats/verse_stats.md) and the accentuation functions [`word_stress`](../syllables.md#word_stress) and [`accentuate`](../stats/verse_stats.md#accentuate): they correct known dictionary errors and restore stress from ё, and `VerseStats` also fits it to the meter.

Raises:

- `SourceTypeError` - a `data_dir` that is neither a string nor a `Path`.

=== "Code"

    ``` python
    from ruts.datasets import StressDict

    sd = StressDict()
    sd.download()
    sd.info["license"]
    ```

=== "Result"

    ```
    'CC0-1.0'
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `data_dir` | `str` / `Path` | `DEFAULT_DATASET_DIR` | Path to the dictionary directory; `dicts` in `DEFAULT_DATA_DIR` by default |

## Attributes

| Attribute | Type | Description |
| :-------- | :--- | :---------- |
| `info` | `dict[str, str]` | Name of the dictionary and reference information about it |

## Methods

`download(force=False)` downloads the dictionary and extracts the file; if the archive exists but the dictionary file does not, the archive is extracted again. The archive is checked against a SHA-256 checksum, a corrupted or replaced file is deleted.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `force` | `bool` | `False` | Download the dictionary even if it is already downloaded |

A file that cannot be downloaded or fails the checksum raises `DownloadError`, an archive that cannot be extracted `DataFileError`.

`check_data()` checks that the dictionary file is in place and returns `True`; a dictionary that is not downloaded raises `DatasetNotFoundError` with the commands to download it, and so does a lookup in it.

`lookup(word)` returns the zero-based number of the stressed syllable of a word form in any case, with or without ё (syllables are counted by vowels), `None` for a form outside the dictionary or without a stress mark.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word form |

A word form that is not a string raises `SourceTypeError`.

=== "Code"

    ``` python
    sd.lookup("корова"), sd.lookup("ёжик"), sd.lookup("котоведение")
    "корова" in sd, len(sd)
    ```

=== "Result"

    ```
    (1, 0, None)
    (True, 1680535)
    ```

`get_records(limit=None)` returns a generator of dictionary records in file (alphabetical) order: the word form and the number of the stressed syllable; `get_texts` with the same parameter returns a generator of word forms.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `limit` | `int` | `None` | Number of records |

A `limit` that is not a non-negative integer raises `ParameterError`.

=== "Code"

    ``` python
    for record in sd.get_records(limit=2):
        print(record)
    list(sd.get_texts(limit=2))
    ```

=== "Result"

    ```
    {'word': '-де', 'stress': 0}
    {'word': '-ка', 'stress': 0}
    ['-де', '-ка']
    ```
