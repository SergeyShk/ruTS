# Character N-gram extraction

``` {.python .signature}
CharNgramsExtractor(n=2, lowercase=False, within_words=False, tokenizer=None)
```

--8<-- "extractors/char_ngrams.md:CharNgramsExtractor"

The class extends the `CharNgramsExtractor` of the [anyTS](https://sergeyshk.github.io/anyTS/extractors/char_ngrams/) core with the hook of Russian: its default word tokenizer for `within_words`, the method `tokenize(text)`, is the default tokenizer of [`WordsExtractor`](words.md), the `tokenize` function of the [razdel](https://github.com/natasha/razdel) library with the dialogue dashes glued to words split off (`ruts.utils.iter_tokens`). Stress marks and soft hyphens are removed from the text before extraction (`ruts.utils.strip_marks`). The list of N-grams is passed to [`delta`](../corpus/stylometry.md) as text units instead of words.

=== "Code"

    ``` python
    from ruts import CharNgramsExtractor

    text = "Кот сидел  на окне, а пёс - на полу."

    ce = CharNgramsExtractor(n=3, lowercase=True)
    ce.extract(text)[:6]
    CharNgramsExtractor().extract(text)[:8]
    CharNgramsExtractor(n=3, lowercase=True, within_words=True).extract(text)
    ```

=== "Result"

    ```
    ('кот', 'от ', 'т с', ' си', 'сид', 'иде')
    ('Ко', 'от', 'т ', ' с', 'си', 'ид', 'де', 'ел')
    ('кот', 'сид', 'иде', 'дел', 'окн', 'кне', 'пёс', 'пол', 'олу')
    ```

## Parameters

--8<-- "extractors/char_ngrams.md:CharNgramsExtractor-parameters"

## Methods

--8<-- "extractors/char_ngrams.md:CharNgramsExtractor-extract"

--8<-- "extractors/char_ngrams.md:CharNgramsExtractor-get_most_common"

=== "Code"

    ``` python
    ce.get_most_common(2)
    ```

=== "Result"

    ```
    [(' на', 2), ('на ', 2)]
    ```
