# Word extraction

``` {.python .signature}
WordsExtractor(tokenizer=None, filter_punct=True, filter_nums=False, use_lexemes=False, stopwords=None, lowercase=False, ngram_range=(1, 1), min_len=0, max_len=0)
```

--8<-- "extractors/words.md:WordsExtractor"

The class extends the `WordsExtractor` of the [anyTS](https://sergeyshk.github.io/anyTS/extractors/words/) core with the hooks of Russian: the tokenizer `tokenize(text)` is the `tokenize` function of the [razdel](https://github.com/natasha/razdel) library with the dialogue dashes glued to words split off (`ruts.utils.iter_tokens`), the lemma `lemmatize(word)` is the first parse of the `MorphAnalyzer` of the [pymorphy3](https://github.com/no-plagiarism/pymorphy3) library (`ruts.utils.parse_all`: «её» is parsed as «ее», since pymorphy3 has no parse of «её» as a personal pronoun, «нем» as «нём», «есть» as «быть»), and the number pattern `number_pattern` also matches ranges, fractions and ordinals: `2020-2021`, `5.5`, `1,5`, `3-й`, `90-х`. Before any tokenizer stress marks and soft hyphens are removed from the text, and й and ё of two characters are composed into one letter (`ruts.utils.strip_marks`).

=== "Code"

    ``` python
    from ruts import WordsExtractor

    text = "Не имей 100 рублей, а имей 100 друзей"

    we = WordsExtractor(use_lexemes=True, stopwords=["не", "а"], filter_nums=True, ngram_range=(1, 2))
    we.extract(text)
    ```

=== "Result"

    ```
    ('иметь', 'рубль', 'иметь', 'друг', 'иметь_рубль', 'рубль_иметь', 'иметь_друг')
    ```

## Parameters

--8<-- "extractors/words.md:WordsExtractor-parameters"

## Methods

--8<-- "extractors/words.md:WordsExtractor-extract"

--8<-- "extractors/words.md:WordsExtractor-get_most_common"

=== "Code"

    ``` python
    we.get_most_common(3)
    ```

=== "Result"

    ```
    [('иметь', 2), ('рубль', 1), ('друг', 1)]
    ```
