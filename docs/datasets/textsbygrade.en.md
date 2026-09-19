# Texts with grade labels

!!! info ""
    **ruts.datasets.TextsByGrade**

## Description

A module for working with the dataset of grade-labeled texts from Ivan Begtin's [Plain Russian Language](https://github.com/infoculture/plainrussian) project. The dataset contains 68 texts from the project repository distributed under the [CC0 1.0](https://github.com/infoculture/plainrussian/blob/master/LICENSE) license: 55 from the `TEXT_LIST` list, on which the coefficients of the Russian readability formulas of the `plainrussian` preset of [`ReadabilityStats`](../stats/readability_stats.md#presets) were fitted, and 13 from repository folders not included in the list. The label is the school grade or the year of study:

| Label | Texts | Count |
| :---: | :---: | :---: |
| 1 | fairy tales, Bianki, Gaidar, Tolstoy | 11 |
| 3-4 | Troepolsky, Paustovsky, Rybakov, Korolenko, Grigorovich | 10 |
| 5-9 | Carroll, Shukshin, Kaverin, Tolstoy, Astafyev, Solzhenitsyn | 12 |
| 10-11 | Korolenko, Bunin, Kuprin, Platonov, Gorky, Rasputin, Dovlatov | 18 |
| 12 | Wikipedia article | 1 |
| 15 | newspaper article | 1 |
| 17 | regulatory and business documents: laws, regulations, government news | 15 |

Labels 12-14 correspond to years 1-3 of university, 15-17 - to years 4-6, as in the [`grade_to_age`](../stats/readability_stats_funcs.md#grade_to_age) table. Paragraphs are separated by line breaks; the hard line breaks of the original lib.ru files are removed.

## Readability formula checks

The dataset is used in the library tests to check the readability formulas: the Spearman correlation of formula values with the grade labels over all 68 texts must be at least 0.7, and that of the consensus grade at least 0.8. Values with the default coefficients:

| Formula | Spearman's ρ | Mean absolute error, grades |
| :-----: | :----------: | :-------------------------: |
| Flesch-Kincaid test | 0.79 | 4.1 |
| Flesch reading ease | −0.79 | - |
| Coleman-Liau index | 0.78 | 3.0 |
| SMOG index | 0.81 | 4.2 |
| Automated readability index | 0.80 | 4.0 |
| LIX readability index | 0.80 | - |
| RIX readability index | 0.78 | - |
| Solovyev, Ivanov and Solnyshkina formula | 0.77 | 4.9 |
| Matskovsky formula | 0.75 | - |
| Dale-Chall index | 0.82 | 3.9 |
| Gunning fog index | 0.80 | 4.1 |
| Consensus grade | 0.81 | 3.7 |

A breakdown over all groups of statistics - coefficient presets, lexis, syntax, morphology, cohesion and a check on the `SovChLit` reader - is in the notebook [02_text_complexity_by_grade.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/02_text_complexity_by_grade.ipynb).

The mean consensus grade grows with the label: 3.2 for grade 1, 5.8 for grades 3-4, 6.6 for 5-9, 7.4 for 10-11 and 22.4 for documents labeled 12-17. The large error on documents is expected: the grade formulas are calibrated on school texts, and label 17 is nominal.

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

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts.datasets import TextsByGrade

    # Create the dataset object
    tbg = TextsByGrade(data_dir=".")

    # Download the dataset
    tbg.download(force=True)

    # Show the dataset information
    tbg.info
    ```

    _Result_:

    ``` bash
    {'Наименование': 'texts_by_grade',
    'author': 'Бегтин И.В.',
    'description': 'Тексты с метками класса проекта Plain Russian Language',
    'license': 'CC0 1.0',
    'url': 'https://github.com/infoculture/plainrussian'}
    ```

### get_texts

Extracts texts (without headers) from the dataset.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `grade` | int | `-` | Grade level of the texts (1, 3-12, 15, 17) |
| `subject` | str | `-` | Text title |
| `min_len` | int | `-` | Minimum text length (in characters) |
| `max_len` | int | `-` | Maximum text length (in characters) |
| `limit` | int | `-` | Number of texts |

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts.datasets import TextsByGrade

    # Create the dataset object
    tbg = TextsByGrade()

    # Show the extracted texts
    for i in tbg.get_texts(grade=1, subject="Ряба", limit=1):
        print(i[:105])
    ```

    _Result_:

    ``` bash
    Жил себе дед да баба, у них была курочка Ряба; снесла под полом яичко - пестро, востро, костяно, мудрено!
    ```

### get_records

Extracts records (with headers) from the dataset. Record fields: `grade` - grade level, `subject` - text title, `source` - source URL (an empty string for the two texts whose address is not published: "Золотой ключик" and the State Council report), `text` - text, `file` - path to the file.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `grade` | int | `-` | Grade level of the texts (1, 3-12, 15, 17) |
| `subject` | str | `-` | Text title |
| `min_len` | int | `-` | Minimum text length (in characters) |
| `max_len` | int | `-` | Maximum text length (in characters) |
| `limit` | int | `-` | Number of texts |

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    from ruts import ReadabilityStats
    from ruts.datasets import TextsByGrade

    # Create the dataset object
    tbg = TextsByGrade()

    # Consensus grade for level 17 texts
    for record in tbg.get_records(grade=17, limit=3):
        print(record["subject"][:40], round(ReadabilityStats(record["text"]).consensus_grade, 1))
    ```

    _Result_:

    ``` bash
    «Об утверждении Административного реглам 28.0
    Доклад Рабочей группы Государственного с 21.5
    Закон о ФКС 34.5
    ```
