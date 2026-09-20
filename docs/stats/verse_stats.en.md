# Verse statistics

!!! info ""
    **ruts.verse_stats.VerseStats**

## Description

A module for computing verse statistics of a text: stress placement, meter and number of feet, pyrrhics and the stress profile, rhyme schemes, line ending types and stanzas. The data source can be either a text with line breaks or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

The text is split into lines and stanzas (by blank lines), the words are accented with the [`StressDict`](../datasets/stressdict.md) dictionary, then a syllabo-tonic meter is fitted with the algorithm of Barakhnin, Kozhemyakina and Kuznetsova and the remaining stress ambiguity is resolved; rhymes are found by the phonetic key of the line ending. The details of the algorithm and its accuracy on the RIFMA dataset are in the [functions](verse_stats_funcs.md) section.

The stress dictionary is downloaded once: `StressDict().download()` (10 MB). Without it the class raises `DatasetNotFoundError` with a hint.

!!! note "Note"
    The statistics are computed when the `VerseStats` object is initialized.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (string or Doc object) |
| `stress_dict` | StressDict | `None` | Stress dictionary; `StressDict()` if not given |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `lines` | tuple[str] | Lines with Russian words |
| `stanzas` | tuple[tuple[str, ...], ...] | Lines by stanza |
| `n_lines` | int | Number of lines |
| `n_stanzas` | int | Number of stanzas |
| `mean_line_len` | float | Mean line length in syllables |
| `meter` | str/None | Meter - ямб (iamb), хорей (trochee), дактиль (dactyl), амфибрахий (amphibrach), анапест (anapest) or `None` |
| `n_feet` | int/None | Prevailing number of feet per line |
| `c_feet` | dict[int, int] | Distribution of lines by number of feet |
| `p_deviations` | float | Share of polysyllabic word stresses on weak positions (deviations from the meter), `nan` without a meter |
| `p_pyrrhics` | float | Share of unstressed ictuses (pyrrhics in binary meters) |
| `stress_profile` | tuple[float, ...] | Share of stressed ictuses by position in the line |
| `stresses` | tuple[tuple[int, ...], ...] | Numbers of stressed syllables of each line |
| `patterns` | tuple[str, ...] | Line patterns of `c` (unstressed syllable) and `C` (stressed) |
| `rhyme_schemes` | tuple[str, ...] | Rhyme schemes of the stanzas |
| `p_rhymed` | float | Share of rhymed lines |
| `c_clausulas` | dict[str, int] | Distribution of line endings by type |
| `p_masculine` | float | Share of masculine endings (stress on the last syllable) |
| `p_feminine` | float | Share of feminine endings (one syllable after the stress) |
| `p_dactylic` | float | Share of dactylic endings (two syllables after the stress) |
| `c_stressed_vowels` | dict[str, int] | Distribution of stressed vowels |

The meter is not determined (`None`) if after fitting more than a tenth of the polysyllabic word stresses (`VERSE_MAX_DEVIATIONS`) remain on weak positions, or if more than 15% of the dictionary stresses had to be moved to an ictus (`VERSE_MAX_MOVED`) with four or more moves (`VERSE_MIN_MOVED`) - this filters out dolnik, accentual verse, syllabic verse, free verse and prose. A rhyme scheme is written with letters in order of appearance, unrhymed lines with a hyphen: `ABAB`, `-A-A`. Endings with three or more syllables after the stress count as hyperdactylic.

!!! note "Note"
    Stresses, meter and rhyme can be obtained separately with the corresponding functions. Detailed information about the algorithm and the functions is in the corresponding [section](verse_stats_funcs.md).

## Methods

### get_stats

Returns a dictionary with the computed verse statistics.

!!! example "Example"

    _Code_:

    ``` python
    # Loading libraries
    from ruts import VerseStats

    # Preparing data
    text = """Мой дядя самых честных правил,
    Когда не в шутку занемог,
    Он уважать себя заставил
    И лучше выдумать не мог."""

    # Computing statistics
    vs = VerseStats(text)
    vs.get_stats()
    ```

    _Result_:

    ``` bash
    {'n_lines': 4,
    'n_stanzas': 1,
    'meter': 'ямб',
    'n_feet': 4,
    'p_deviations': 0.0,
    'p_pyrrhics': 0.1875,
    'p_rhymed': 1.0,
    'p_masculine': 0.5,
    'p_feminine': 0.5,
    'p_dactylic': 0.0}
    ```

Line patterns, the stress profile and the distributions are available as attributes:

!!! example "Example"

    ``` python
    vs.patterns
    # ('cCcCcCcCc', 'cCcCcccC', 'cccCcCcCc', 'cCcCcccC')
    vs.stresses[1]
    # (1, 3, 7)
    vs.stress_profile
    # (0.75, 1.0, 0.5, 1.0)
    vs.rhyme_schemes, vs.c_clausulas
    # (('ABAB',), {'мужская': 2, 'женская': 2})
    vs.c_stressed_vowels
    # {'а': 5, 'я': 2, 'у': 2, 'о': 2, 'е': 1, 'ы': 1}
    ```

### print_stats

Prints a table with the computed verse statistics.

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Printing the table of computed statistics
    vs.print_stats()
    ```

    _Result_:

    ``` bash
                   Статистика               |  Значение
    ----------------------------------------------------
    Количество строк                        |     4
    Количество строф                        |     1
    Метр                                    |    ямб
    Число стоп                              |     4
    Доля отклонений от метра                |    0.00
    Доля пропущенных ударений на иктах      |    0.19
    Доля рифмованных строк                  |    1.00
    Доля мужских окончаний                  |    0.50
    Доля женских окончаний                  |    0.50
    Доля дактилических окончаний            |    0.00
    ```

### accentuate

Returns the text with stresses placed: an acute accent (U+0301) is put after the stressed vowel of every stressed word; unstressed words (clitics, monosyllables off the ictus) and words without a found stress stay unmarked. Only lines with words are returned (as in `lines`), stanzas are separated by a blank line.

!!! example "Example"

    _Code_:

    ``` python
    ...

    print(vs.accentuate())
    ```

    _Result_:

    ``` bash
    Мой дя́дя са́мых че́стных пра́вил,
    Когда́ не в шу́тку занемо́г,
    Он уважа́ть себя́ заста́вил
    И лу́чше вы́думать не мо́г.
    ```
