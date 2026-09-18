# Basic statistics

!!! info ""
    **ruts.basic_stats.BasicStats**

## Description

A module for computing basic text statistics. The data source can be either a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

The module allows using pre-built [`SentsExtractor`](../extractors/sentences.md) and [`WordsExtractor`](../extractors/words.md) objects for the sentence and word tokenization needed before computing the statistics.

For a `Doc` object words are taken from the tokens (hyphenated words split by spaCy are glued back), sentences - from the annotation; without sentence boundaries (`spacy.blank`, a pipeline without `parser` and `senter`) sentences are extracted from the text by `SentsExtractor`.

!!! note "Note"
    The statistics are computed when the `BasicStats` object is initialized.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `sents_extractor` | SentsExtractor | `None` | Sentence extraction tool |
| `words_extractor` | WordsExtractor | `None` | Word extraction tool |
| `normalize` | bool | `False` | Compute normalized statistics |
| `complex_syl_factor` | int | `4` | Minimum number of syllables in a complex word |
| `long_word_letter_factor` | int | `6` | Minimum number of letters in a long word |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `c_letters` | dict[int, int] | Distribution of words by number of letters |
| `c_syllables` | dict[int, int] | Distribution of words by number of syllables |
| `n_sents` | int | Number of sentences |
| `n_words` | int | Number of words |
| `n_unique_words` | int | Number of unique words |
| `n_long_words` | int | Number of long words |
| `n_complex_words` | int | Number of complex words |
| `n_simple_words` | int | Number of simple words |
| `n_monosyllable_words` | int | Number of monosyllabic words |
| `n_polysyllable_words` | int | Number of polysyllabic words |
| `n_chars` | int | Number of characters |
| `n_letters` | int | Number of letters |
| `n_spaces` | int | Number of spaces |
| `n_syllables` | int | Number of syllables |
| `n_punctuations` | int | Number of punctuation marks |
| `c_punctuations` | dict[str, int] | Distribution of punctuation marks by type |
| `p_unique_words` | float | Normalized number of unique words |
| `p_long_words` | float | Normalized number of long words |
| `p_complex_words` | float | Normalized number of complex words |
| `p_simple_words` | float | Normalized number of simple words |
| `p_monosyllable_words` | float | Normalized number of monosyllabic words |
| `p_polysyllable_words` | float | Normalized number of polysyllabic words |
| `p_letters` | float | Normalized number of letters |
| `p_spaces` | float | Normalized number of spaces |
| `p_punctuations` | float | Normalized number of punctuation marks |

!!! warning "Warning"
    The normalized statistics attributes `p_*` are available only when the object is initialized with `normalize=True`.

## Methods

### count_words_by_syllables

Returns the number of words with at least the given number of syllables.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `min_syllables` | int | `-` | Minimum number of syllables in a word |

### count_words_by_letters

Returns the number of words with at least the given number of letters.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `min_letters` | int | `-` | Minimum number of letters in a word |

!!! note "Note"
    These methods recount complex and long words with a threshold different from the one set at initialization. For instance, [`ReadabilityStats`](readability_stats.md) uses them for the SMOG index (a complex word has 5+ syllables) and the LIX index (a long word has 7+ letters).

### get_stats

Returns a dictionary with the computed text statistics.

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

Prints a table with the computed text statistics.

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

`count_punctuations(text)` counts punctuation marks by the types of `PUNCTUATION_TYPES` - the same distribution lives in the `c_punctuations` attribute: commas, periods, question and exclamation marks, ellipses (the `…` character, three or more periods, or two periods after `?` and `!` - one mark whose periods do not count as periods: «Кто там?..» is a question and an ellipsis), colons, semicolons, dashes (`—` and `–`, as well as a hyphen with spaces on both sides or at the start of a line, the way dashes are typed in text corpora: «- Ушли, - сказал он»), hyphens between letters («кто-то»), guillemets `«»`, straight and curly quotation marks `"„“”`, brackets and the other marks of `PUNCTUATIONS`. `punctuation_profile(text, n_words=None)` turns them into frequencies per 1000 words and adds `yo_share` - the share of the letter ё among the letters е and ё, that is, whether the author writes ё.

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
