# KWIC concordance

!!! info ""
    **ruts.corpus.kwic()**, **ruts.corpus.format_kwic()**, **ruts.corpus.print_kwic()**, **ruts.corpus.Concordance**

## Description

A KWIC (keyword in context) concordance - all occurrences of a word or phrase with left and right context, as in [AntConc](https://www.laurenceanthony.net/software/antconc/) and textacy `keyword_in_context`. It shows how a word is used in the text: what it combines with, in which forms and senses.

Occurrences are searched among the words of the text by word form ignoring case and the letter ё, case-sensitively (`ignore_case=False`) or by pymorphy3 lemma (`by_lemma=True`: «кота», «коту» are found by «кот», a phrase is given by lemmas - «рабочий класс»); for a `Doc` with part-of-speech annotation the lemma of a word is taken with the token's part of speech, so «стали» is found by «сталь» or by «стать» depending on the annotation, while the keyword is lemmatized without a part of speech. The context is `window` words to the left and to the right as written in the text, with punctuation between them; whitespace runs are collapsed into a single space, occurrences do not overlap. The source is a string (razdel words) or a `Doc` object.

`format_kwic` aligns the lines on the keyword: the left context is truncated on the left and right-aligned, the right one is truncated on the right; `print_kwic` prints the result.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Text or Doc object |
| `keyword` | str | `-` | Word or phrase (words separated by spaces) |
| `window` | int | `5` | Number of context words on each side |
| `by_lemma` | bool | `False` | Compare lemmas instead of word forms |
| `ignore_case` | bool | `True` | Ignore case and the letter ё when comparing word forms |

`format_kwic(concordances, width=40)` and `print_kwic(concordances, width=40)`: `width` is the context width in characters, at least one; line breaks inside the keyword phrase are replaced with spaces.

## Result

A list of `Concordance` named tuples in text order.

| Field | Type | Description |
| :---: | :--: | :---------- |
| `start` | int | Position of the first character of the occurrence in the text |
| `end` | int | Position after the last character of the occurrence |
| `left` | str | Left context |
| `keyword` | str | The occurrence as in the text |
| `right` | str | Right context |

## Example

!!! example "Example"

    ``` python
    from ruts.corpus import kwic, print_kwic

    text = (
        "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне. "
        "Завтра кот снова будет сидеть на окне и смотреть на птиц."
    )
    lines = kwic(text, "окно", by_lemma=True, window=3)
    lines[0]
    # Concordance(start=13, end=17, left='Кот сидел на', keyword='окне', right='и смотрел на')

    print_kwic(lines, width=20)
    #         Кот сидел на  окне  и смотрел на
    #         кот уснул на  окне  . Завтра кот снова
    #      будет сидеть на  окне  и смотреть на

    [line.keyword for line in kwic(text, "смотреть на птица", by_lemma=True)]
    # ['смотрел на птиц', 'смотреть на птиц']
    ```
