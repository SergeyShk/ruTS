# Sentence extraction

!!! info ""
    **ruts.extractors.SentsExtractor**

## Description

A module for extracting sentences from a text. It allows using different tokenizers and setting the minimum and maximum length of extracted sentences.

!!! note "Note"
    The default tokenizer is the `sentenize` function of the [razdel](https://github.com/natasha/razdel) library.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `tokenizer` | Pattern/Callable | `None` | Tokenizer or regular expression |
| `min_len` | int | `0` | Minimum length of an extracted sentence |
| `max_len` | int | `0` | Maximum length of an extracted sentence |

## Methods

### extract

Extracts sentences from a text.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | str | `-` | Text string |

An example of sentence extraction with a regular expression as the tokenizer:

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    import re
    from ruts import SentsExtractor

    # Prepare the data
    text = "Не имей 100 рублей, а имей 100 друзей"

    # Extract sentences
    se = SentsExtractor(tokenizer=re.compile(r", "))
    se.extract(text)
    ```

    _Result_:

    ``` bash
    ('Не имей 100 рублей', 'а имей 100 друзей')
    ```
