# Sentence extraction

``` {.python .signature}
SentsExtractor(tokenizer=None, min_len=0, max_len=0)
```

--8<-- "extractors/sentences.md:SentsExtractor"

The class extends the `SentsExtractor` of the [anyTS](https://sergeyshk.github.io/anyTS/extractors/sentences/) core with the hook of Russian: its default tokenizer, the method `sentenize(text)`, is the `sentenize` function of the [razdel](https://github.com/natasha/razdel) library.

=== "Code"

    ``` python
    from ruts import SentsExtractor

    text = "Не имей 100 рублей, а имей 100 друзей. Так говорил проф. Иванов... А вы?"
    SentsExtractor().extract(text)
    ```

=== "Result"

    ```
    ('Не имей 100 рублей, а имей 100 друзей.', 'Так говорил проф. Иванов...', 'А вы?')
    ```

## Parameters

--8<-- "extractors/sentences.md:SentsExtractor-parameters"

--8<-- "extractors/sentences.md:SentsExtractor-pipeline"

## Methods

--8<-- "extractors/sentences.md:SentsExtractor-extract"

=== "Code"

    ``` python
    import re

    SentsExtractor().extract("Что нового\n\nБыстрый импорт\nМеньше ошибок\n\nСпасибо за внимание!")
    SentsExtractor(tokenizer=re.compile(r", ")).extract("Не имей 100 рублей, а имей 100 друзей")
    ```

=== "Result"

    ```
    ('Что нового', 'Быстрый импорт\nМеньше ошибок', 'Спасибо за внимание!')
    ('Не имей 100 рублей', 'а имей 100 друзей')
    ```
