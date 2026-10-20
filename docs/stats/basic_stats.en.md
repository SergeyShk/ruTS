# Basic statistics

``` {.python .signature}
BasicStats(source, sents_extractor=None, words_extractor=None, normalize=False, complex_syl_factor=4, long_word_letter_factor=6)
```

--8<-- "stats/basic_stats.md:BasicStats"

The class extends the `BasicStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/basic_stats/) core with the hooks of Russian: the syllables of a word are counted by [`count_syllables`](../syllables.md#count_syllables), the default extractors are the Russian [`SentsExtractor`](../extractors/sentences.md) and [`WordsExtractor`](../extractors/words.md), the punctuation marks are counted by the [`count_punctuations`](#count_punctuations) of ruTS, and the parts of a hyphenated word that spaCy splits are joined (`во-первых` is one word). The blank line component of ruTS is called [`ruts_blank_lines`](../components.md#blank_lines): `nlp.add_pipe("ruts_blank_lines", before="parser")`. Stress marks and soft hyphens count neither as characters nor as parts of words, and й and ё of two characters are one letter (`ruts.utils.strip_marks`): a text with stresses gives the same statistics as without them. The statistics are computed when the object is created; the `print_stats` table is in Russian.

=== "Code"

    ``` python
    from ruts import BasicStats

    text = "Существуют три вида лжи: ложь, наглая ложь и статистика"
    bs = BasicStats(text, normalize=True)
    bs.print_stats()
    ```

=== "Result"

    ```
        Статистика     | Значение
    ------------------------------
    Предложения        |    1
    Слова              |    9
    Уникальные слова   |    8
    Длинные слова      |    3
    Сложные слова      |    2
    Простые слова      |    7
    Односложные слова  |    5
    Многосложные слова |    4
    Символы            |    55
    Буквы              |    45
    Пробелы            |    8
    Слоги              |    18
    Знаки препинания   |    2
    ```

## Parameters

--8<-- "stats/basic_stats.md:BasicStats-parameters"

In ruTS a complex word has four or more syllables and a long word six or more letters: `COMPLEX_SYL_FACTOR = 4` and `LONG_WORD_LETTER_FACTOR = 6` of `ruts.constants`.

## Statistics

--8<-- "stats/basic_stats.md:BasicStats-attributes"

## Methods

--8<-- "stats/basic_stats.md:BasicStats-count_words_by"

The methods recount complex and long words with a threshold other than the one set when the object was created: this is how [`ReadabilityStats`](readability_stats.md) computes the SMOG index (a complex word has 5 or more syllables) and LIX (a long word has 7 or more letters).

--8<-- "stats/basic_stats.md:BasicStats-get_stats"

--8<-- "stats/basic_stats.md:BasicStats-print_stats"

The normalized statistics `p_*` are not in the table.

--8<-- "stats/stats.md:Stats-to_dataframe"

The `describe` method is that of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the basic statistics have no scales, so it always gives `None`.

=== "Code"

    ``` python
    bs.count_words_by_syllables(5), bs.count_words_by_letters(7)
    bs.get_stats()
    ```

=== "Result"

    ```
    (0, 2)
    {'c_letters': {1: 1, 3: 2, 4: 3, 6: 1, 10: 2},
     'c_syllables': {1: 5, 2: 1, 3: 1, 4: 2},
     'n_sents': 1,
     'n_words': 9,
     'n_unique_words': 8,
     'n_long_words': 3,
     'n_complex_words': 2,
     'n_simple_words': 7,
     'n_monosyllable_words': 5,
     'n_polysyllable_words': 4,
     'n_chars': 55,
     'n_letters': 45,
     'n_spaces': 8,
     'n_syllables': 18,
     'n_punctuations': 2,
     'c_punctuations': {'comma': 1,
                        'period': 0,
                        'question': 0,
                        'exclamation': 0,
                        'ellipsis': 0,
                        'colon': 1,
                        'semicolon': 0,
                        'dash': 0,
                        'hyphen': 0,
                        'angle_quotes': 0,
                        'straight_quotes': 0,
                        'parentheses': 0,
                        'other': 0},
     'p_unique_words': 0.8888888888888888,
     'p_long_words': 0.3333333333333333,
     'p_complex_words': 0.2222222222222222,
     'p_simple_words': 0.7777777777777778,
     'p_monosyllable_words': 0.5555555555555556,
     'p_polysyllable_words': 0.4444444444444444,
     'p_letters': 0.8181818181818182,
     'p_spaces': 0.14545454545454545,
     'p_punctuations': 0.03636363636363636}
    ```

## Punctuation marks { #count_punctuations }

--8<-- "stats/basic_stats.md:count_punctuations"

In ruTS the `PUNCTUATION_MARKS` and `DASH_PATTERN` of `ruts.basic_stats` are the marks of the core with the low quotation mark `„` as a quotation mark and the pattern of dashes by which a hanging hyphen before `и`, `или`, `либо` or a comma stays a hyphen (`двух- и трёхкомнатные`, `сорока-, пятидесятилетние`), while a dialogue dash typed with a hyphen is a dash (`- Ушли, - сказал он`).

=== "Code"

    ``` python
    from ruts.basic_stats import count_punctuations

    text = "Кот — «зверь»... Пёс, конечно, - друг; а кто-то (тот, что ещё жив) — нет!"
    {kind: count for kind, count in count_punctuations(text).items() if count}
    ```

=== "Result"

    ```
    {'comma': 3,
     'exclamation': 1,
     'ellipsis': 1,
     'semicolon': 1,
     'dash': 3,
     'hyphen': 1,
     'angle_quotes': 2,
     'parentheses': 2}
    ```

## Dashes typed with hyphens { #dash_pattern }

--8<-- "stats/basic_stats.md:dash_pattern"

Without the parameters the pattern is the `DASH_PATTERN` of the core (`anyts.basic_stats`), while the `DASH_PATTERN` of `ruts.basic_stats` is `dash_pattern(("и", "или", "либо"), hanging_before_comma=True)`.

=== "Code"

    ``` python
    from ruts.basic_stats import count_punctuations, dash_pattern

    text = "Двух- и трёхкомнатные, сорока-, пятидесятилетние - сказал он"
    counts = count_punctuations(text)
    counts["dash"], counts["hyphen"]
    counts = count_punctuations(text, dash_pattern=dash_pattern())
    counts["dash"], counts["hyphen"]
    ```

=== "Result"

    ```
    (1, 2)
    (3, 0)
    ```

## Punctuation profile { #punctuation }

``` {.python .signature}
punctuation_profile(text, n_words=None)
```

The frequencies of the punctuation marks by type (`count_punctuations`) per 1000 words and `yo_share` - the share of the letter ё among the letters е and ё, that is, whether the author writes ё. Without words or without the letters е and ё the values are `nan`. A text that is not a string raises `SourceTypeError`, a number of words that is not a non-negative integer `ParameterError`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Text string |
| `n_words` | `int` | `None` | Number of words; without it the words are extracted by `WordsExtractor` |

The profile is an editorial and stylometric feature: Chekhov has several times more ellipses and exclamations than Tolstoy (see [corpus comparison](../corpus/compare.md)). It depends on text formatting - typographic quotation marks and dashes, the letter ё - and is easy to fake, so it is best read separately from linguistic features.

=== "Code"

    ``` python
    from ruts.basic_stats import punctuation_profile

    text = "Кот — «зверь»... Пёс, конечно, - друг; а кто-то (тот, что ещё жив) — нет!"
    profile = punctuation_profile(text)
    round(profile["dash"], 1), round(profile["yo_share"], 2)
    ```

=== "Result"

    ```
    (250.0, 0.33)
    ```
