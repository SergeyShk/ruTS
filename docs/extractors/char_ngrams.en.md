# Character N-gram extraction

!!! info ""
    **ruts.extractors.CharNgramsExtractor**

## Description

A module for extracting character N-grams from a text - sequences of N characters taken with a sliding window over the string. Character N-grams are a standard feature of stylometry and authorship attribution (Stamatatos 2009): they capture morphology, punctuation and typical letter combinations without lemmatization. The list of N-grams is passed to [`delta`](../corpus/stylometry.md) as text units instead of words.

Whitespace runs are collapsed into a single space beforehand, punctuation marks are kept: a space or a mark inside an N-gram is a stylistic signal too. With `within_words=True` N-grams do not cross word boundaries: the text is split into words by the tokenizer, punctuation is dropped, and words shorter than N yield no N-grams.

!!! note "Note"
    The default word tokenizer for `within_words` is the `tokenize` function of the [razdel](https://github.com/natasha/razdel) library.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n` | int | `2` | N-gram length in characters |
| `lowercase` | bool | `False` | Convert the text to lower case |
| `within_words` | bool | `False` | Take N-grams only inside words |
| `tokenizer` | Pattern/Callable | `None` | Word tokenizer for `within_words` or a regular expression |

## Methods

### extract

Extracts N-grams from a text.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | str | `-` | Text string |

!!! example "Example"

    ``` python
    from ruts import CharNgramsExtractor

    text = "Кот сидел  на окне, а пёс - на полу."

    ce = CharNgramsExtractor()
    ce.extract(text)[:8]
    # ('Ко', 'от', 'т ', ' с', 'си', 'ид', 'де', 'ел')

    ce = CharNgramsExtractor(n=3, lowercase=True)
    ce.extract(text)[:6]
    # ('кот', 'от ', 'т с', ' си', 'сид', 'иде')

    CharNgramsExtractor(n=3, lowercase=True, within_words=True).extract(text)
    # ('кот', 'сид', 'иде', 'дел', 'окн', 'кне', 'пёс', 'пол', 'олу')
    ```

### get_most_common

Returns the most frequent N-grams of the last extraction.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n` | int | `10` | Number of N-grams |

!!! example "Example"

    ``` python
    ce = CharNgramsExtractor(n=3, lowercase=True)
    ce.extract(text)
    ce.get_most_common(2)
    # [(' на', 2), ('на ', 2)]
    ```
