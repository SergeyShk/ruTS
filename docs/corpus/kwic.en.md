# KWIC concordance

!!! info ""
    **ruts.corpus.kwic()**, **ruts.corpus.format_kwic()**, **ruts.corpus.print_kwic()**, **ruts.corpus.Concordance**

## Description

--8<-- "corpus/kwic.md:kwic"

## Language hooks

The function calls the `kwic` of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/kwic/) core with the hooks of Russian: the words and the sentences of a string and of the keyword are those of [razdel](https://github.com/natasha/razdel), the lemma of a word is the pymorphy3 one, in a `Doc` with part-of-speech annotation taken with the part of speech of the token (`ruts.utils.lemmatize`), so «стали» is found by «сталь» or by «стать» depending on the annotation, and the word forms (with `ignore_case`) and the lemmas are compared in lower case with ё as е. The parts of a hyphenated word that spaCy splits are joined (`кто-то` is one word).

## Parameters

--8<-- "corpus/kwic.md:kwic-parameters"

--8<-- "corpus/kwic.md:format_kwic"

--8<-- "corpus/kwic.md:print_kwic"

## Result

--8<-- "corpus/kwic.md:Concordance"

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
