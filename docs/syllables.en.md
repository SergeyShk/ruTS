# Syllables and stress

The `ruts.syllables` module divides a Russian word into syllables and finds its stressed syllable: syllables by rules, the stress by the [`StressDict`](datasets/stressdict.md) dictionary. The basic, phonetic and verse statistics and the readability formulas are built on these functions. Stress marks and soft hyphens are removed from the word (`ruts.utils.strip_marks`), and a stress given by a mark (за́мок, замо́к) overrides the dictionary.

## Syllabification { #syllabify }

``` {.python .signature}
syllabify(word)
```

Division of a word into syllables by the rising sonority rule (Avanesov): there are as many syllables as vowels, a word without vowels (в, к, с) has none. The syllable boundary follows these rules:

| Rule | Example |
| :--- | :------ |
| a single consonant between vowels goes to the next syllable | ко-ро-ва, ра-йон |
| a cluster of obstruents, or an obstruent followed by a sonorant, goes to the next syllable | ко-шка, се-стра, о-ткрыть, по-зна-ко-мить |
| a sonorant before an obstruent goes to the previous syllable | кар-та, пол-ка |
| the boundary goes between two sonorants | вол-на, кар-ман |
| й before a consonant goes to the previous syllable | май-ка, вой-на |
| ь and ъ go with the preceding letter | боль-шой, по-дъезд |
| every vowel of a hiatus forms its own syllable | а-э-ро-порт, а-ист |

The division is orthographic, by letters, as in school phonetics; a compound word is divided part by part (`со-рок-во-ро-вка`).

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word |

Raises:

- `SourceTypeError` - a word that is not a string.

=== "Code"

    ``` python
    from ruts.syllables import syllabify

    syllabify("здравствуйте")
    ```

=== "Result"

    ```
    ['здра', 'вствуй', 'те']
    ```

## Syllable count { #count_syllables }

``` {.python .signature}
count_syllables(word)
```

The number of syllables of a word - the number of vowel letters.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word |

Raises:

- `SourceTypeError` - a word that is not a string.

=== "Code"

    ``` python
    from ruts.syllables import count_syllables

    count_syllables("здравствуйте")
    ```

=== "Result"

    ```
    3
    ```

## Stressed syllable { #word_stress }

``` {.python .signature}
word_stress(word, stress_dict=None)
```

The number of the stressed syllable of a word, counting from zero: by the letter ё, the only syllable of a monosyllable, otherwise by the dictionary (step 1 of the [algorithm](stats/verse_stats.md#algorithm) of the verse statistics); for a compound word, the last of the stresses of [`word_stresses`](#word_stresses).

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word |
| `stress_dict` | `StressDict` | `None` | Stress dictionary; `StressDict()` by default |

Returns `None` if the word is not found or has no vowels.

Raises:

- `SourceTypeError` - a word that is not a string, a stress dictionary of another type;
- `DatasetNotFoundError` - the stress dictionary is not downloaded.

=== "Code"

    ``` python
    from ruts.syllables import syllabify, word_stress

    word_stress("корова"), word_stress("ещё"), word_stress("желанье"), word_stress("кто-нибудь")
    word_stress("за́мок"), word_stress("замо́к"), word_stress("сорок-воровка")
    word_stress("хмурота"), word_stress("в")
    syllabify("корова")[word_stress("корова")]
    ```

=== "Result"

    ```
    (1, 1, 1, 0)
    (0, 1, 3)
    (None, None)
    'ро'
    ```

## All stresses { #word_stresses }

``` {.python .signature}
word_stresses(word, stress_dict=None)
```

All stressed syllables of a word in ascending order. A hyphenated compound that the dictionary lacks as a whole gets the stress of every content part (`со-рок-во-ро-вка` - 0 and 3), the particles (-то, -либо, -нибудь and others) are unstressed.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word |
| `stress_dict` | `StressDict` | `None` | Stress dictionary; `StressDict()` by default |

Returns an empty list if the word is not found or has no vowels.

Raises:

- `SourceTypeError` - a word that is not a string, a stress dictionary of another type;
- `DatasetNotFoundError` - the stress dictionary is not downloaded.

=== "Code"

    ``` python
    from ruts.syllables import word_stresses

    word_stresses("сорок-воровка"), word_stresses("северо-западный"), word_stresses("кто-нибудь")
    ```

=== "Result"

    ```
    ([0, 3], [3], [0])
    ```

## Ending type { #stress_type }

``` {.python .signature}
stress_type(word, stress_dict=None)
```

The type of the ending of a word by the position of its main stress. The names are those of verse clausulas (`VERSE_CLAUSULAS`):

| Type | Stress | Example |
| :--- | :----- | :------ |
| мужская (masculine) | on the last syllable | зем-**ля** |
| женская (feminine) | on the penultimate syllable | ко-**ро**-ва |
| дактилическая (dactylic) | on the third syllable from the end | **зо**-ло-то |
| гипердактилическая (hyperdactylic) | earlier | **вы**-ско-чи-вший |

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word |
| `stress_dict` | `StressDict` | `None` | Stress dictionary; `StressDict()` by default |

Returns `None` if the word is not found or has no vowels.

Raises:

- `SourceTypeError` - a word that is not a string, a stress dictionary of another type;
- `DatasetNotFoundError` - the stress dictionary is not downloaded.

=== "Code"

    ``` python
    from ruts.syllables import stress_type

    tuple(stress_type(word) for word in ("земля", "корова", "золото", "выскочивший"))
    ```

=== "Result"

    ```
    ('мужская', 'женская', 'дактилическая', 'гипердактилическая')
    ```
