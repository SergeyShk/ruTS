# Syllables and stress

!!! info ""
    **ruts.syllables**

## Description

A module that divides a Russian word into syllables and finds its stressed syllable: syllables by rules, the stress by the [`StressDict`](datasets/stressdict.md) dictionary. The basic, phonetic and verse statistics and the readability formulas are built on these functions.

## Syllabification { #syllabify }

!!! info ""
    **ruts.syllables.syllabify()**

Division of a word into syllables by the rising sonority rule (Avanesov): there are as many syllables as vowels, a word without vowels (в, к, с) has none. The syllable boundary follows these rules:

| Rule | Example |
| :--- | :-----: |
| a single consonant between vowels goes to the next syllable | ко-ро-ва, ра-йон |
| a cluster of obstruents, or an obstruent followed by a sonorant, goes to the next syllable | ко-шка, се-стра, о-ткрыть, по-зна-ко-мить |
| a sonorant before an obstruent goes to the previous syllable | кар-та, пол-ка |
| the boundary goes between two sonorants | вол-на, кар-ман |
| й before a consonant goes to the previous syllable | май-ка, вой-на |
| ь and ъ go with the preceding letter | боль-шой, по-дъезд |
| every vowel of a hiatus forms its own syllable | а-э-ро-порт, а-ист |

The division is orthographic, by letters, as in school phonetics; a compound word is divided part by part (`со-рок-во-ро-вка`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |

!!! example "Example"

    ``` python
    from ruts.syllables import syllabify

    syllabify("здравствуйте")
    # ['здра', 'вствуй', 'те']
    ```

## Syllable count { #count_syllables }

!!! info ""
    **ruts.syllables.count_syllables()**

The number of syllables of a word - the number of vowel letters.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |

!!! example "Example"

    ``` python
    from ruts.syllables import count_syllables

    count_syllables("здравствуйте")
    # 3
    ```

## Stressed syllable { #word_stress }

!!! info ""
    **ruts.syllables.word_stress()**

The number of the stressed syllable of a word by the dictionary, counting from zero.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |
| `stress_dict` | StressDict | `None` | Stress dictionary; `StressDict()` if not given |

Returns `None` if the word is not found or has no vowels.

!!! example "Example"

    ``` python
    from ruts.syllables import syllabify, word_stress

    word_stress("корова"), word_stress("ещё"), word_stress("желанье"), word_stress("кто-нибудь")
    # (1, 1, 1, 0)
    word_stress("хмурота")
    # None
    syllabify("корова")[word_stress("корова")]
    # 'ро'
    ```

## All stresses { #word_stresses }

!!! info ""
    **ruts.syllables.word_stresses()**

All stressed syllables of a word in ascending order. A hyphenated compound that the dictionary lacks as a whole gets the stress of every content part (`со-рок-во-ро-вка` - 0 and 3), the particles -то, -нибудь, -ка are unstressed.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |
| `stress_dict` | StressDict | `None` | Stress dictionary; `StressDict()` if not given |

Returns an empty list if the word is not found or has no vowels.

!!! example "Example"

    ``` python
    from ruts.syllables import word_stresses

    word_stresses("сорок-воровка"), word_stresses("северо-западный"), word_stresses("кто-нибудь")
    # ([0, 3], [3], [0])
    ```

## Ending type { #stress_type }

!!! info ""
    **ruts.syllables.stress_type()**

The type of the ending of a word by the position of its main stress. The names are those of verse clausulas (`VERSE_CLAUSULAS`):

| Type | Stress | Example |
| :--- | :----- | :-----: |
| мужская (masculine) | on the last syllable | зем-**ля** |
| женская (feminine) | on the penultimate syllable | ко-**ро**-ва |
| дактилическая (dactylic) | on the third syllable from the end | **зо**-ло-то |
| гипердактилическая (hyperdactylic) | earlier | **вы**-ско-чи-вший |

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |
| `stress_dict` | StressDict | `None` | Stress dictionary; `StressDict()` if not given |

Returns `None` if the word is not found or has no vowels.

!!! example "Example"

    ``` python
    from ruts.syllables import stress_type

    tuple(stress_type(word) for word in ("земля", "корова", "золото", "выскочивший"))
    # ('мужская', 'женская', 'дактилическая', 'гипердактилическая')
    ```
