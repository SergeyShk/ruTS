# Sentence extraction

!!! info ""
    **ruts.extractors.SentsExtractor**

## Description

--8<-- "extractors/sentences.md:SentsExtractor"

## Language hooks

The class extends the `SentsExtractor` of the [anyTS](https://sergeyshk.github.io/anyTS/extractors/sentences/) core with the hook of Russian: its default tokenizer, the method `sentenize(text)`, is the `sentenize` function of the [razdel](https://github.com/natasha/razdel) library.

--8<-- "extractors/sentences.md:SentsExtractor-pipeline"

## Parameters

--8<-- "extractors/sentences.md:SentsExtractor-parameters"

## Methods

### extract

--8<-- "extractors/sentences.md:SentsExtractor-extract"

An example of sentence extraction with the default tokenizer:

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts import SentsExtractor

    # Prepare the data
    text = "Не имей 100 рублей, а имей 100 друзей. Так говорил проф. Иванов... А вы?"

    # Extract sentences
    se = SentsExtractor()
    se.extract(text)
    ```

    _Result_:

    ``` bash
    ('Не имей 100 рублей, а имей 100 друзей.', 'Так говорил проф. Иванов...', 'А вы?')
    ```

An example of sentence extraction with a regular expression as the tokenizer:

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
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
