# Components

A set of modules for building [spaCy](https://github.com/explosion/spaCy) components. Each module is a class with two implemented methods: `__init__` (adds a new extension to the pipeline on initialization) and `__call__` (takes a `Doc` object and returns its modified version).

!!! note "Note"
    Detailed information on developing custom spaCy components is available in the corresponding section of the [documentation](https://spacy.io/usage/processing-pipelines#custom-components). The examples below use the `ru_core_news_sm` model, which is installed separately: `python -m spacy download ru_core_news_sm` (see [installation](installation.md)).

!!! warning "Serialization"
    The components store a statistics object in `doc._.<name>`, which spaCy cannot serialize: `Doc.to_bytes()`, `DocBin(store_user_data=True)` and `nlp.pipe(..., n_process>1)` with such components fail. To save a document, exclude the user data (`doc.to_bytes(exclude=["user_data"])`) or store `doc._.<name>.get_stats()` separately; for multiprocessing compute the statistics in the main process after `nlp.pipe` without the ruTS components.

## BasicStatsComponent

!!! info ""
    **ruts.components.BasicStatsComponent**

A module for the basic text statistics component.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nlp` | Language | `-` | Language object |
| `name` | str | `"basic"` | Component name in the pipeline |

Usage example:

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import ruts
    import spacy

    # Load the spaCy model
    nlp = spacy.load("ru_core_news_sm")

    # Add the component
    nlp.add_pipe("basic", last=True)

    # Access the computed metrics
    doc = nlp("мама мыла раму")
    doc._.basic.c_letters
    ```

    _Result_:

    ``` bash
    {4: 3}
    ```

## MorphStatsComponent

!!! info ""
    **ruts.components.MorphStatsComponent**

A module for the morphological statistics component. Parts of speech and features are taken from the model annotation (`token.pos_`, `token.morph`), in a pipeline without a tagger - from pymorphy3.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nlp` | Language | `-` | Language object |
| `name` | str | `"morph"` | Component name in the pipeline |

Usage example:

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import ruts
    import spacy

    # Load the spaCy model
    nlp = spacy.load("ru_core_news_sm")

    # Add the component
    nlp.add_pipe("morph", last=True)

    # Access the computed metrics
    doc = nlp("мама мыла раму")
    doc._.morph.case
    ```

    _Result_:

    ``` bash
    ('Nom', None, 'Acc')
    ```

## ReadabilityStatsComponent

!!! info ""
    **ruts.components.ReadabilityStatsComponent**

A module for the readability metrics component.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nlp` | Language | `-` | Language object |
| `name` | str | `"readability"` | Component name in the pipeline |
| `preset` | str | `"plainrussian"` | [Coefficient preset](stats/readability_stats.md#presets) (`plainrussian`, `fiction`, `academic`) |

Usage example:

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import ruts
    import spacy

    # Load the spaCy model
    nlp = spacy.load("ru_core_news_sm")

    # Add the component
    nlp.add_pipe("readability", last=True)

    # Access the computed metrics
    doc = nlp("мама мыла раму")
    doc._.readability.flesch_reading_easy
    ```

    _Result_:

    ``` bash
    82.735
    ```

The coefficient preset is passed via `config`:

!!! example "Example"

    ``` python
    nlp.add_pipe("readability", config={"preset": "fiction"}, last=True)
    ```

## DiversityStatsComponent

!!! info ""
    **ruts.components.DiversityStatsComponent**

A module for the lexical diversity metrics component.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nlp` | Language | `-` | Language object |
| `name` | str | `"diversity"` | Component name in the pipeline |
| `window_len` | int | `50` | Window size for MATTR and segment size for MSTTR |
| `mtld_threshold` | float | `0.72` | TTR threshold for MTLD, MA-MTLD and MTLD-W |
| `mtld_min_len` | int | `10` | Minimum factor length for MTLD, MA-MTLD and MTLD-W |
| `hdd_sample_size` | int | `42` | Sample size for HD-D |
| `log_base` | float | `10` | Logarithm base for the Summer, Maas and Dugast metrics |

Usage example:

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import ruts
    import spacy

    # Load the spaCy model
    nlp = spacy.load("ru_core_news_sm")

    # Add the component
    nlp.add_pipe("diversity", last=True)

    # Access the computed metrics
    doc = nlp("мама мыла раму")
    doc._.diversity.rttr
    ```

    _Result_:

    ``` bash
    1.7320508075688774
    ```

Windows, thresholds and the logarithm base are passed via `config`:

!!! example "Example"

    ``` python
    nlp.add_pipe("diversity", config={"window_len": 100, "log_base": 2.718281828459045}, last=True)
    ```

## StyleStatsComponent

!!! info ""
    **ruts.components.StyleStatsComponent**

A module for the SEO style metrics component.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nlp` | Language | `-` | Language object |
| `name` | str | `"style"` | Component name in the pipeline |
| `stopwords` | list[str] | `None` | Stop word list for water content; if not given, pymorphy3 tags are used |
| `top_n` | int | `10` | Number of the most frequent words for academic nausea and naturalness by Zipf's law |

Usage example:

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import ruts
    import spacy

    # Load the spaCy model
    nlp = spacy.load("ru_core_news_sm")

    # Add the component
    nlp.add_pipe("style", last=True)

    # Access the computed metrics
    doc = nlp("мама мыла раму")
    doc._.style.water
    ```

    _Result_:

    ``` bash
    0.0
    ```

The stop word list and the number of the most frequent words are passed via `config`:

!!! example "Example"

    ``` python
    nlp.add_pipe("style", config={"stopwords": ["и", "в", "не"], "top_n": 5}, last=True)
    ```

## PhonStatsComponent

!!! info ""
    **ruts.components.PhonStatsComponent**

A module for the phonostatistics component.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nlp` | Language | `-` | Language object |
| `name` | str | `"phon"` | Component name in the pipeline |
| `window_len` | int | `3` | Window size in words for alliteration and assonance |

Usage example:

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import ruts
    import spacy

    # Load the spaCy model
    nlp = spacy.load("ru_core_news_sm")

    # Add the component
    nlp.add_pipe("phon", last=True)

    # Access the computed statistics
    doc = nlp("мама мыла раму")
    doc._.phon.p_open_syllables
    ```

    _Result_:

    ``` bash
    1.0
    ```

The window size is passed via `config`:

!!! example "Example"

    ``` python
    nlp.add_pipe("phon", config={"window_len": 5}, last=True)
    ```

## SyntaxStatsComponent

!!! info ""
    **ruts.components.SyntaxStatsComponent**

A module for the syntactic statistics component. The component works over the dependency tree, so the pipeline must have a parser: the `ru_core_news_sm`, `ru_core_news_md` or `ru_core_news_lg` models; in a pipeline without a parser the component raises `SourceError`.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nlp` | Language | `-` | Language object |
| `name` | str | `"syntax"` | Component name in the pipeline |

Usage example:

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import ruts
    import spacy

    # Load the spaCy model
    nlp = spacy.load("ru_core_news_sm")

    # Add the component
    nlp.add_pipe("syntax", last=True)

    # Access the computed statistics
    doc = nlp("Дом, построенный рабочими в прошлом году, был продан")
    doc._.syntax.tree_depth
    ```

    _Result_:

    ``` bash
    4.0
    ```

## CohesionStatsComponent

!!! info ""
    **ruts.components.CohesionStatsComponent**

A module for the cohesion statistics component. The component only needs sentence boundaries (a model or `sentencizer`); when annotation is present, parts of speech are taken from it, lemmas - from pymorphy3 by the token's part of speech.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nlp` | Language | `-` | Language object |
| `name` | str | `"cohesion"` | Component name in the pipeline |

Usage example:

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import ruts
    import spacy

    # Load the spaCy model
    nlp = spacy.load("ru_core_news_sm")

    # Add the component
    nlp.add_pipe("cohesion", last=True)

    # Access the computed statistics
    doc = nlp("Кот сидел на окне. Он смотрел на птиц. Птицы улетели, и кот уснул.")
    doc._.cohesion.noun_overlap_adjacent
    ```

    _Result_:

    ``` bash
    0.5
    ```

## LexicalStatsComponent

!!! info ""
    **ruts.components.LexicalStatsComponent**

A module for the lexical sophistication statistics component. The frequency dictionary metrics require a downloaded [`FreqDict`](datasets/freq2011.md); the bands and lexical density are computed without it.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nlp` | Language | `-` | Language object |
| `name` | str | `"lexical"` | Component name in the pipeline |
| `data_dir` | str | `None` | Path to the frequency dictionary directory; if not given, the default directory is used |

Usage example:

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import ruts
    import spacy

    # Load the spaCy model
    nlp = spacy.load("ru_core_news_sm")

    # Add the component
    nlp.add_pipe("lexical", last=True)

    # Access the computed statistics
    doc = nlp("Кот сидел на окне и смотрел на птиц")
    doc._.lexical.p_top1000
    ```

    _Result_:

    ``` bash
    0.75
    ```

The dictionary directory is passed via `config`:

!!! example "Example"

    ``` python
    nlp.add_pipe("lexical", config={"data_dir": "/path/to/dicts"}, last=True)
    ```

## VerseStatsComponent

!!! info ""
    **ruts.components.VerseStatsComponent**

A module for the verse statistics component. It requires a downloaded [`StressDict`](datasets/stressdict.md) stress dictionary; the component works on the `Doc` text with line breaks, so pass the poem text to `nlp` as is, without joining the lines. A text without Russian words gives empty statistics, like `VerseStats`, so `nlp.pipe` over a corpus does not stop on it.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nlp` | Language | `-` | Language object |
| `name` | str | `"verse"` | Component name in the pipeline |
| `data_dir` | str | `None` | Path to the stress dictionary directory; if not given, the default directory is used |

Usage example:

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import ruts
    import spacy

    # Load the spaCy model
    nlp = spacy.load("ru_core_news_sm")

    # Add the component
    nlp.add_pipe("verse", last=True)

    # Access the computed statistics
    doc = nlp(
        "Буря мглою небо кроет,\nВихри снежные крутя;\nТо, как зверь, она завоет,\nТо заплачет, как дитя"
    )
    doc._.verse.meter, doc._.verse.n_feet
    ```

    _Result_:

    ``` bash
    ('хорей', 4)
    ```

The dictionary directory is passed via `config`:

!!! example "Example"

    ``` python
    nlp.add_pipe("verse", config={"data_dir": "/path/to/dicts"}, last=True)
    ```
