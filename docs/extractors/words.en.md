# Word extraction

!!! info ""
    **ruts.extractors.WordsExtractor**

## Description

A module for extracting words from a text. It allows using different tokenizers, filtering stop words, numbers and punctuation, lemmatizing, building N-grams, and setting the minimum and maximum length of extracted words.

!!! note "Note"
    The default tokenizer is the `tokenize` function of the [razdel](https://github.com/natasha/razdel) library.

!!! note "Note"
    The default morphological analyzer for lemmatization is the `MorphAnalyzer` class of the [pymorphy3](https://github.com/no-plagiarism/pymorphy3) library.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `tokenizer` | Pattern/Callable | `None` | Tokenizer or regular expression |
| `filter_punct` | bool | `True` | Filter punctuation marks |
| `filter_nums` | bool | `False` | Filter numbers, including ranges, fractions and ordinals (2020-2021, 5.5, 1,5, 3-й) |
| `use_lexemes` | bool | `False` | Use word lemmas |
| `stopwords` | List[str] | `None` | List of stop words |
| `lowercase` | bool | `False` | Convert words to lower case |
| `ngram_range` | Tuple[int, int] | `(1, 1)` | Lower and upper bound of the N-gram size |
| `min_len` | int | `0` | Minimum length of an extracted word |
| `max_len` | int | `0` | Maximum length of an extracted word |

!!! note "Note"
    The filters are applied in order: punctuation, numbers, lemmatization, lower case, stop words, word length. Stop words are compared after lowercasing, so with `lowercase=True` the stop word list only needs to be in lower case. A punctuation mark is a token consisting entirely of marks and symbols, including multi-character ones: `?!`, `!..`, `--`, `…`.

## Methods

### extract

Extracts words from a text.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | str | `-` | Text string |

An example of word extraction with bigrams as tokens, after filtering stop words and lemmatizing:

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import re
    from nltk.corpus import stopwords
    from ruts import WordsExtractor

    # Prepare the data
    text = "Не имей 100 рублей, а имей 100 друзей"

    # Extract words
    we = WordsExtractor(
        use_lexemes=True, stopwords=stopwords.words("russian"), filter_nums=True, ngram_range=(1, 2)
    )
    we.extract(text)
    ```

    _Result_:

    ``` bash
    ('иметь', 'рубль', 'иметь', 'друг', 'иметь_рубль', 'рубль_иметь', 'иметь_друг')
    ```

!!! warning "Warning"
    This example requires the [nltk](https://github.com/nltk/nltk) stop word list to be downloaded to the local machine beforehand. Run the following code to do so:

    ``` python
    import nltk

    nltk.download("stopwords")
    ```

### get_most_common

Returns a counter of the top words of the text. It takes the number of top words to return as a parameter.

To illustrate the method, we reuse the code from the previous example:

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the top words
    we.get_most_common(3)
    ```

    _Result_:

    ``` bash
    [('иметь', 2), ('рубль', 1), ('друг', 1)]
    ```

!!! warning "Warning"
    The method must be called after words have been extracted with `extract`.
