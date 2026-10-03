# Word extraction

!!! info ""
    **ruts.extractors.WordsExtractor**

## Description

--8<-- "extractors/words.md:WordsExtractor"

## Language hooks

The class extends the `WordsExtractor` of the [anyTS](https://sergeyshk.github.io/anyTS/extractors/words/) core with the hooks of Russian: the tokenizer `tokenize(text)` is the `tokenize` function of the [razdel](https://github.com/natasha/razdel) library with the dialogue dashes glued to words split off (`ruts.utils.iter_tokens`), the lemma `lemmatize(word)` is the first parse of the `MorphAnalyzer` of the [pymorphy3](https://github.com/no-plagiarism/pymorphy3) library, and the number pattern `number_pattern` also matches ranges, fractions and ordinals: `2020-2021`, `5.5`, `1,5`, `3-й`, `90-х`.

## Parameters

--8<-- "extractors/words.md:WordsExtractor-parameters"

## Methods

### extract

--8<-- "extractors/words.md:WordsExtractor-extract"

An example of word extraction with bigrams as tokens, after filtering stop words and numbers and lemmatizing:

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts import WordsExtractor

    # Prepare the data
    text = "Не имей 100 рублей, а имей 100 друзей"

    # Extract words
    we = WordsExtractor(
        use_lexemes=True, stopwords=["не", "а"], filter_nums=True, ngram_range=(1, 2)
    )
    we.extract(text)
    ```

    _Result_:

    ``` bash
    ('иметь', 'рубль', 'иметь', 'друг', 'иметь_рубль', 'рубль_иметь', 'иметь_друг')
    ```

### get_most_common

--8<-- "extractors/words.md:WordsExtractor-get_most_common"

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
