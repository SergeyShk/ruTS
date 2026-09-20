# Koziev stress dictionary

!!! info ""
    **ruts.datasets.StressDict**

## Description

A module for working with Ilya Koziev's [stress dictionary](https://github.com/Koziev/NLP_Datasets#ударения) (all_accents): 1,680,535 word forms with the position of the primary stress. Data from Wikipedia and Wiktionary is extended with forms generated from the inflection tables of the author's grammar dictionary under the assumption that stress does not move in declension and conjugation, so forms with mobile stress (реки́ - ре́ки, воды́ - во́ды) get one of the variants, homographs (за́мок - замо́к) share one line, and the letter ё is replaced with е throughout.

The dictionary is distributed under the CC0 license and downloaded from the author's repository at a pinned commit (10.6 MB, a 77 MB file) with a SHA-256 checksum check. The file is read once per process and indexed in memory as a whole without parsing lines: a word form is found by binary search over the sorted file, so loading takes a fraction of a second and the dictionary occupies about 100 MB of memory.

The dictionary is used by [`VerseStats`](../stats/verse_stats.md) and by the accentuation functions [`word_stress`](../stats/verse_stats_funcs.md#word_stress) and [`accentuate`](../stats/verse_stats_funcs.md#accentuate): they correct known dictionary errors, restore stress from the letter ё and fit it to the meter.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `data_dir` | str | `DEFAULT_DATA_DIR.joinpath("dicts")` | Path to the dictionary directory |

## Methods

### download

Downloads the dictionary and extracts the file. The downloaded archive is checked against a SHA-256 checksum; a corrupted or replaced file is deleted with a `DownloadError` so that the next download is not skipped. If the archive exists but the dictionary file does not, the archive is extracted again.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `force` | bool | `-` | Download the dictionary even if it is already downloaded |

!!! example "Example"

    ``` python
    from ruts.datasets import StressDict

    sd = StressDict()
    sd.download()
    sd.info["license"]
    # 'CC0-1.0'
    ```

### lookup

Returns the zero-based number of the stressed syllable of a word form (syllables are counted by vowels), `None` for a form outside the dictionary or without a stress mark. The form is lowercased and ё is replaced with е, as in the dictionary.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word form |

!!! example "Example"

    ``` python
    sd.lookup("корова"), sd.lookup("ёжик"), sd.lookup("котоведение")
    # (1, 0, None)
    "корова" in sd, len(sd)
    # (True, 1680535)
    ```

### get_records

Returns a generator of dictionary records in file (alphabetical) order: the word form and the number of the stressed syllable.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `limit` | int | `None` | Number of records |

!!! example "Example"

    ``` python
    for record in sd.get_records(limit=2):
        print(record)
    # {'word': '-де', 'stress': 0}
    # {'word': '-ка', 'stress': 0}
    ```

### get_texts

Returns a generator of dictionary word forms with the same parameter as `get_records`.
