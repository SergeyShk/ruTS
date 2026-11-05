# KWIC concordance

``` {.python .signature}
kwic(source, keyword, window=5, by_lemma=False, ignore_case=True)
```

--8<-- "corpus/kwic.md:kwic"

The function calls the `kwic` of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/kwic/) core with the hooks of Russian: the words and the sentences of a string and of the keyword come from the [anySeg](https://github.com/SergeyShk/anySeg) segmenter, the lemmas from ruMorph in the context of the sentence (in a `Doc`, by the part of speech of the token), so «стали» is found by «сталь» or by «стать» depending on its neighbours; a word of the keyword has no context and matches by any lemma of its analyses (`стали` finds both). Stress marks and the period of an abbreviation do not count (`руб.` is found by `руб`), the word forms with `ignore_case` and the lemmas are compared in lower case with ё as е, and the parts of a hyphenated word that spaCy splits are joined (`кто-то` is one word).

=== "Code"

    ``` python
    from ruts.corpus import kwic, print_kwic

    text = (
        "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне. "
        "Завтра кот снова будет сидеть на окне и смотреть на птиц."
    )
    lines = kwic(text, "окно", by_lemma=True, window=3)
    lines[0]
    print_kwic(lines, width=20)

    [line.keyword for line in kwic(text, "смотреть на птица", by_lemma=True)]
    ```

=== "Result"

    ```
    Concordance(start=13, end=17, left='Кот сидел на', keyword='окне', right='и смотрел на')
            Кот сидел на  окне  и смотрел на
            кот уснул на  окне  . Завтра кот снова
         будет сидеть на  окне  и смотреть на
    ['смотрел на птиц', 'смотреть на птиц']
    ```

## Parameters

--8<-- "corpus/kwic.md:kwic-parameters"

## Result

--8<-- "corpus/kwic.md:Concordance"

## Aligned lines { #format_kwic }

--8<-- "corpus/kwic.md:format_kwic"

--8<-- "corpus/kwic.md:print_kwic"
