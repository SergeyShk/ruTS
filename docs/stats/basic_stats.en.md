# Basic statistics

!!! info ""
    **ruts.basic_stats.BasicStats**

## Description

--8<-- "stats/basic_stats.md:BasicStats"

Stress marks and soft hyphens count neither as characters nor as parts of words, and й and ё of two characters are one letter (`ruts.utils.strip_marks`): a text with stresses gives the same statistics as without them.

!!! note "Note"
    The statistics are computed when the `BasicStats` object is initialized.

## Language hooks

The class extends the `BasicStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/basic_stats/) core with the hooks of Russian: the syllables of a word are counted by [`count_syllables`](../syllables.md#count_syllables), the default extractors are the Russian [`SentsExtractor`](../extractors/sentences.md) and [`WordsExtractor`](../extractors/words.md), and the parts of a hyphenated word that spaCy splits are joined (`во-первых` is one word). A `Doc` without sentence boundaries (`spacy.blank`, a pipeline without `parser` and `senter`) takes its sentences from the text by `SentsExtractor`.

## Parameters

--8<-- "stats/basic_stats.md:BasicStats-parameters"

!!! note "Note"
    In ruTS a complex word has four or more syllables and a long word six or more letters: `COMPLEX_SYL_FACTOR = 4` and `LONG_WORD_LETTER_FACTOR = 6` of `ruts.constants`.

## Attributes

--8<-- "stats/basic_stats.md:BasicStats-attributes"

## Methods

### count_words_by_syllables, count_words_by_letters

--8<-- "stats/basic_stats.md:BasicStats-count_words_by"

!!! note "Note"
    These methods recount complex and long words with a threshold different from the one set at initialization. For instance, [`ReadabilityStats`](readability_stats.md) uses them for the SMOG index (a complex word has 5+ syllables) and the LIX index (a long word has 7+ letters).

### get_stats

--8<-- "stats/basic_stats.md:BasicStats-get_stats"

An example of computing basic text statistics with normalization:

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ruts import BasicStats

    # Prepare the data
    text = "Существуют три вида лжи: ложь, наглая ложь и статистика"

    # Compute the statistics
    bs = BasicStats(text, normalize=True)
    bs.get_stats()
    ```

    _Result_:

    ``` bash
    {'c_letters': {1: 1, 3: 2, 4: 3, 6: 1, 10: 2},
    'c_punctuations': {'comma': 1, 'period': 0, 'question': 0, 'exclamation': 0, 'ellipsis': 0, 'colon': 1, 'semicolon': 0, 'dash': 0, 'hyphen': 0, 'angle_quotes': 0, 'straight_quotes': 0, 'parentheses': 0, 'other': 0},
    'c_syllables': {1: 5, 2: 1, 3: 1, 4: 2},
    'n_chars': 55,
    'n_complex_words': 2,
    'n_letters': 45,
    'n_long_words': 3,
    'n_monosyllable_words': 5,
    'n_polysyllable_words': 4,
    'n_punctuations': 2,
    'n_sents': 1,
    'n_simple_words': 7,
    'n_spaces': 8,
    'n_syllables': 18,
    'n_unique_words': 8,
    'n_words': 9,
    'p_complex_words': 0.2222222222222222,
    'p_letters': 0.8181818181818182,
    'p_long_words': 0.3333333333333333,
    'p_monosyllable_words': 0.5555555555555556,
    'p_polysyllable_words': 0.4444444444444444,
    'p_punctuations': 0.03636363636363636,
    'p_simple_words': 0.7777777777777778,
    'p_spaces': 0.14545454545454545,
    'p_unique_words': 0.8888888888888888}
    ```

### print_stats

--8<-- "stats/basic_stats.md:BasicStats-print_stats"

To illustrate the method, we reuse the code from the previous example:

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed statistics
    bs.print_stats()
    ```

    _Result_:

    ``` bash
         Статистика     | Значение
    ------------------------------
    Предложения         |    1
    Слова               |    9
    Уникальные слова    |    8
    Длинные слова       |    3
    Сложные слова       |    2
    Простые слова       |    7
    Односложные слова   |    5
    Многосложные слова  |    4
    Символы             |    55
    Буквы               |    45
    Пробелы             |    8
    Слоги               |    18
    Знаки препинания    |    2
    ```

!!! warning "Warning"
    The method does not print the normalized statistics attributes `p_*`.

## Punctuation profile { #punctuation }

!!! info ""
    **ruts.basic_stats.count_punctuations()**, **ruts.basic_stats.punctuation_profile()**

--8<-- "stats/basic_stats.md:count_punctuations"

In ruTS `count_punctuations(text)` takes the marks of the core with the low quotation mark `„` as a quotation mark, and a hanging hyphen before `и`, `или`, `либо` or a comma stays a hyphen (`двух- и трёхкомнатные`, `сорока-, пятидесятилетние`), while a dialogue dash typed with a hyphen is a dash (`- Ушли, - сказал он`). `punctuation_profile(text, n_words=None)` turns the counts into frequencies per 1000 words and adds `yo_share` - the share of the letter ё among the letters е and ё, that is, whether the author writes ё.

The profile is an editorial and stylometric feature: Chekhov has several times more ellipses and exclamations than Tolstoy (see [corpus comparison](../corpus/compare.md)). It depends on text formatting - typographic quotation marks and dashes, the letter ё - and is easy to fake, so it is best read separately from linguistic features.

!!! example "Example"

    ``` python
    from ruts.basic_stats import count_punctuations, punctuation_profile

    text = "Кот — «зверь»... Пёс, конечно, - друг; а кто-то (тот, что ещё жив) — нет!"
    {kind: count for kind, count in count_punctuations(text).items() if count}
    # {'comma': 3, 'exclamation': 1, 'ellipsis': 1, 'semicolon': 1, 'dash': 3, 'hyphen': 1, 'angle_quotes': 2, 'parentheses': 2}

    round(punctuation_profile(text)["dash"], 1), round(punctuation_profile(text)["yo_share"], 2)
    # (250.0, 0.33)
    ```
