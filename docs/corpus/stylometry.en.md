# Stylometry

!!! info ""
    **ruts.corpus.delta()**, **ruts.corpus.delta_profiles()**, **ruts.corpus.frequency_table()**, **ruts.corpus.z_scores()**, **ruts.corpus.zeta()**, **ruts.corpus.kilgarriff_chi2()**, **ruts.corpus.mendenhall_curve()**, **ruts.corpus.mendenhall_distance()**, **ruts.corpus.function_words_profile()**

## Description

--8<-- "corpus/stylometry.md:stylometry"

The functions are those of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/stylometry/) core, with the [profile of the function words](#function_words_profile) of Russian added as a feature of an author. The units of a text come from [`WordsExtractor`](../extractors/words.md) - word forms and lemmas - and [`CharNgramsExtractor`](../extractors/char_ngrams.md).

## Burrows's Delta { #delta }

--8<-- "corpus/stylometry.md:frequency_table"

--8<-- "corpus/stylometry.md:z_scores"

--8<-- "corpus/stylometry.md:delta"

--8<-- "corpus/stylometry.md:delta_profiles"

!!! example "Example"

    ``` python
    from ruts import WordsExtractor
    from ruts.corpus import delta, delta_profiles, frequency_table

    texts = {
        "А": "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне.",
        "Б": "Собака лежала на полу и дремала. Потом собака ела и снова дремала на полу.",
        "В": "Завтра кот снова будет сидеть на окне и смотреть на птиц, а собака будет дремать.",
    }
    we = WordsExtractor(lowercase=True)
    corpus = {name: we.extract(text) for name, text in texts.items()}

    frequency_table(corpus, n_mfw=5).round(3)
    #       на      и  собака    кот   окне
    # А  0.200  0.133   0.000  0.133  0.133
    # Б  0.143  0.143   0.143  0.000  0.000
    # В  0.133  0.067   0.067  0.067  0.067

    delta(corpus, n_mfw=5).round(3)
    #        А      Б      В
    # А  0.000  1.563  1.277
    # Б  1.563  0.000  1.033
    # В  1.277  1.033  0.000

    delta(corpus, n_mfw=5, variant="cosine").round(3)
    #        А      Б      В
    # А  0.000  1.782  1.452
    # Б  1.782  0.000  1.202
    # В  1.452  1.202  0.000

    sample = {"?": we.extract("Кот проснулся на окне и снова смотрел на птиц.")}
    delta_profiles(corpus, sample, n_mfw=5).round(3)
    #        А     Б     В
    # ?  0.364  1.66  1.16
    ```

## Zeta { #zeta }

--8<-- "corpus/stylometry.md:zeta"

!!! example "Example"

    ``` python
    from ruts.corpus import zeta

    zeta(corpus["А"], corpus["Б"], segment_size=5, top_n=2)
    # [ZetaScore(word='кот', dp_target=0.6666666666666666, dp_comparison=0.0, zeta=0.6666666666666666, log_zeta=2.0),
    #  ZetaScore(word='окне', dp_target=0.6666666666666666, dp_comparison=0.0, zeta=0.6666666666666666, log_zeta=2.0)]

    zeta(corpus["А"], corpus["Б"], segment_size=5)[-1]
    # ZetaScore(word='собака', dp_target=0.0, dp_comparison=0.6666666666666666, zeta=-0.6666666666666666, log_zeta=-2.0)
    ```

## Kilgarriff's chi-square { #kilgarriff_chi2 }

--8<-- "corpus/stylometry.md:kilgarriff_chi2"

!!! example "Example"

    ``` python
    from ruts.corpus import kilgarriff_chi2

    round(kilgarriff_chi2(corpus["А"], corpus["Б"], n_mfw=5), 3)
    # 6.018
    ```

## Mendenhall curve { #mendenhall }

--8<-- "corpus/stylometry.md:mendenhall_curve"

--8<-- "corpus/stylometry.md:mendenhall_distance"

!!! example "Example"

    ``` python
    from ruts.corpus import mendenhall_curve, mendenhall_distance

    {length: round(share, 3) for length, share in mendenhall_curve(corpus["А"]).items()}
    # {1: 0.133, 2: 0.2, 3: 0.133, 4: 0.2, 5: 0.2, 7: 0.133}

    round(mendenhall_distance(corpus["А"], corpus["Б"]), 3)
    # 0.353
    ```

## Function word profile { #function_words_profile }

The shares of adpositions, coordinating and subordinating conjunctions, particles, pronouns, determiners and interjections (`ruts.constants.FUNCTION_UD_POS`: `ADP`, `CCONJ`, `SCONJ`, `PART`, `PRON`, `DET`, `INTJ`) among the words of the text - by the first pymorphy3 analysis for a list of words and by the annotation for a `Doc` with parts of speech; punctuation is not counted. Function words do not depend on the topic, so their profile is a classic authorship feature (the Marusenko school).

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | list[str]/Doc | `-` | Words of the text or Doc object |

!!! example "Example"

    ``` python
    from ruts.corpus import function_words_profile

    {pos: round(share, 3) for pos, share in function_words_profile(corpus["А"]).items()}
    # {'ADP': 0.2, 'CCONJ': 0.133, 'SCONJ': 0.0, 'PART': 0.0, 'PRON': 0.0, 'DET': 0.0, 'INTJ': 0.0}
    ```
