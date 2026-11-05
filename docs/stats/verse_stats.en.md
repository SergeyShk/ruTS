# Verse statistics

``` {.python .signature}
VerseStats(source, stress_dict=None)
```

The verse statistics of a text: stresses, the meter and feet, rhyme, line endings and stanzas. The data source is a text with line breaks or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

Stanzas are separated by blank lines. The stresses are placed by the [`StressDict`](../datasets/stressdict.md) dictionary and fitted to the meter ([algorithm](#algorithm)). A stress mark in the text overrides the dictionary and is not moved to an ictus, so a text after the [`accentuate`](#accentuate) function, where the stresses are placed without a meter, gives other values than the same text without marks; a proclitic stressed by a mark takes away the stress of the word after it separated by a space (на́ сердце). The marks and soft hyphens themselves do not get into the lines.

The stress dictionary is downloaded once: `StressDict().download()` (10 MB). A text with letters but without Russian words (Latin script) gives empty statistics - `n_lines` 0, meter `None`, shares `nan`.

Raises:

- `SourceTypeError` - a source that is neither a string nor a `Doc`, a stress dictionary of another type;
- `SourceError` - a source without words (empty, digits and punctuation only);
- `DatasetNotFoundError` - the stress dictionary is not downloaded.

=== "Code"

    ``` python
    from ruts import VerseStats
    from ruts.datasets import StressDict

    StressDict().download()
    text = """Мой дядя самых честных правил,
    Когда не в шутку занемог,
    Он уважать себя заставил
    И лучше выдумать не мог."""
    vs = VerseStats(text)
    vs.print_stats()
    ```

=== "Result"

    ```
                Статистика             | Значение
    ----------------------------------------------
    Количество строк                   |    4
    Количество строф                   |    1
    Метр                               |   ямб
    Число стоп                         |    4
    Доля отклонений от метра           |   0.00
    Доля пропущенных ударений на иктах |   0.19
    Доля рифмованных строк             |   1.00
    Доля мужских окончаний             |   0.50
    Доля женских окончаний             |   0.50
    Доля дактилических окончаний       |   0.00
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Data source |
| `stress_dict` | `StressDict` | `None` | Stress dictionary; `StressDict()` by default |

## Attributes

| Attribute | Type | Description |
| :-------- | :--- | :---------- |
| `stress_dict` | `StressDict` | Stress dictionary |
| `lines` | `tuple[str]` | Lines with Russian words |
| `stanzas` | `tuple[tuple[str, ...], ...]` | Lines by stanza |
| `mean_line_len` | `float` | Mean line length in syllables |
| `stresses` | `tuple[tuple[int, ...], ...]` | Numbers of the stressed syllables of each line, counted from zero |
| `patterns` | `tuple[str, ...]` | Line patterns of `c` (unstressed syllable) and `C` (stressed) |
| `c_stressed_vowels` | `dict[str, int]` | Distribution of the stressed vowels |

=== "Code"

    ``` python
    vs.patterns
    vs.stresses[1]
    vs.c_stressed_vowels
    ```

=== "Result"

    ```
    ('cCcCcCcCc', 'cCcCcccC', 'cccCcCcCc', 'cCcCcccC')
    (1, 3, 7)
    {'а': 5, 'я': 2, 'у': 2, 'о': 2, 'е': 1, 'ы': 1}
    ```

## Metrics

Every metric is an attribute of the object, computed when it is created, and `get_stats` gives them all.

| Metric | Measures | Range | Higher means |
| :----- | :------- | :---- | :----------- |
| `n_lines`, `n_stanzas` | Number of the lines with words and of the stanzas | 0 and above | A longer text |
| [`meter`](#meter) | Syllabo-tonic meter | ямб (iamb), хорей (trochee), дактиль (dactyl), амфибрахий (amphibrach), анапест (anapest), `None` without a meter | - |
| [`n_feet`](#meter) | Prevailing number of feet per line | 1 and above, `None` without a meter | Longer lines |
| [`p_deviations`](#meter) | Share of the stresses of polysyllabic words on weak positions | 0-0.1, `nan` without a meter | Stresses further from the meter |
| [`p_pyrrhics`](#pyrrhics) | Share of the unstressed ictuses | 0-1, `nan` without a meter | More skipped stresses |
| [`p_rhymed`](#rhyme_scheme) | Share of the rhymed lines | 0-1, `nan` without lines | More rhymes |
| [`p_masculine`](#clausulas), [`p_feminine`](#clausulas), [`p_dactylic`](#clausulas) | Shares of the masculine, feminine and dactylic endings | 0-1, `nan` without endings | More endings of the type |

<div class="metric-card" markdown>

### Meter and feet { #meter }

`meter` · `n_feet` · `c_feet` · `p_deviations` · [Barakhnin et al., 2019](https://ceur-ws.org/Vol-2523/paper27.pdf)
{ .metric-meta }

``` {.python .signature}
detect_meter(text, stress_dict=None)
```

The meter of a poem by the [algorithm](#algorithm): ямб (iamb), хорей (trochee), дактиль (dactyl), амфибрахий (amphibrach), анапест (anapest) or `None` if no syllabo-tonic meter fits - this filters out dolnik, accentual verse, syllabic verse, free verse and prose. The number of feet of a line is the number of its ictuses, `c_feet` is the distribution of the lines by the number of feet, and `p_deviations` is counted after the stresses are fitted to the meter.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Text of the poem |
| `stress_dict` | `StressDict` | `None` | Stress dictionary; `StressDict()` by default |

The errors are those of `VerseStats`.

=== "Code"

    ``` python
    from ruts.verse_stats import detect_meter

    lermontov = """Тучки небесные, вечные странники!
    Степью лазурною, цепью жемчужною
    Мчитесь вы, будто как я же, изгнанники,
    С милого севера в сторону южную.

    Кто же вас гонит: судьбы ли решение?
    Зависть ли тайная? злоба ль открытая?
    Или на вас тяготит преступление?
    Или друзей клевета ядовитая?"""

    blok = """Девушка пела в церковном хоре
    О всех усталых в чужом краю,
    О всех кораблях, ушедших в море,
    О всех, забывших радость свою."""

    detect_meter(lermontov), detect_meter(blok)
    vs.c_feet
    ```

=== "Result"

    ```
    ('дактиль', None)
    {4: 4}
    ```

</div>

<div class="metric-card" markdown>

### Pyrrhics and the stress profile { #pyrrhics }

`p_pyrrhics` · `stress_profile`
{ .metric-meta }

The share of the unstressed ictuses (pyrrhics in binary meters) among all the ictuses of the lines; `stress_profile` is the share of the stressed ictuses by position in the line, from the first ictus to the last. Without a meter `p_pyrrhics` is `nan`, and the profile is empty.

$$
\frac{\textrm{Number of unstressed ictuses}}{\textrm{Number of ictuses}}
$$

=== "Code"

    ``` python
    vs.p_pyrrhics, vs.stress_profile
    ```

=== "Result"

    ```
    (0.1875, (0.75, 1.0, 0.5, 1.0))
    ```

</div>

<div class="metric-card" markdown>

### Rhyme { #rhyme_scheme }

`p_rhymed` · `rhyme_schemes` · [RIFMA](https://github.com/Koziev/Rifma)
{ .metric-meta }

``` {.python .signature}
rhyme_scheme(text, stress_dict=None)
```

The rhyme scheme of a poem: the stanza schemes separated by spaces, unrhymed lines marked with a hyphen (`ABAB`, `-A-A`, `AABB CC`). The object has the schemes by stanza in `rhyme_schemes`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Text of the poem |
| `stress_dict` | `StressDict` | `None` | Stress dictionary; `StressDict()` by default |

The errors are those of `VerseStats`.

=== "Code"

    ``` python
    from ruts.verse_stats import rhyme_scheme

    rhyme_scheme(lermontov), rhyme_scheme(blok)
    vs.rhyme_schemes, vs.p_rhymed
    ```

=== "Result"

    ```
    ('ABAB ABAB', 'ABAB')
    (('ABAB',), 1.0)
    ```

</div>

<div class="metric-card" markdown>

### Line endings { #clausulas }

`p_masculine` · `p_feminine` · `p_dactylic` · `c_clausulas`
{ .metric-meta }

The type of the ending (clausula) of a line by the number of syllables after the last stress: masculine - the stress on the last syllable, feminine - one syllable after the stress, dactylic - two, hyperdactylic - three or more (`VERSE_CLAUSULAS`, as [`stress_type`](../syllables.md#stress_type) of a word). `c_clausulas` is the distribution of the lines by type; the shares are taken over the lines whose last word has a known stress.

=== "Code"

    ``` python
    vs.c_clausulas
    ```

=== "Result"

    ```
    {'мужская': 2, 'женская': 2}
    ```

</div>

## Methods

`accentuate()` returns the text with an acute accent (U+0301) after the stressed vowels, with the stresses fitted to the meter; unstressed words (clitics, monosyllables off the ictus) and words without a found stress stay unmarked. Only the lines with words get into the text, and stanzas are separated by a blank line.

=== "Code"

    ``` python
    print(vs.accentuate())
    ```

=== "Result"

    ```
    Мой дя́дя са́мых че́стных пра́вил,
    Когда́ не в шу́тку занемо́г,
    Он уважа́ть себя́ заста́вил
    И лу́чше вы́думать не мо́г.
    ```

The other methods - `get_stats`, `to_dataframe`, `print_stats` and `describe` - are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the verse statistics have no scales, and `describe` gives `None` for them.

=== "Code"

    ``` python
    vs.get_stats()
    ```

=== "Result"

    ```
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

## Algorithm { #algorithm }

Stresses and the meter are determined with the algorithm of Barakhnin, Kozhemyakina and Kuznetsova ([CEUR 2019](https://ceur-ws.org/Vol-2523/paper27.pdf)):

1.  **Dictionary stresses.** The stressed syllable of a word is found by the letter ё, as the only syllable of a monosyllable, otherwise by the [`StressDict`](../datasets/stressdict.md) dictionary with the `STRESS_CORRECTIONS` fixes (erroneous and mobile dictionary stresses: себе́, зо́лото). A hyphenated compound is looked up as a whole, then by parts; poetic contractions (желанье - желание) and converbs (забыв - забывший) are looked up by the full form.
2.  **Meter fitting.** The strong positions (ictuses) of the five meters: iamb `cC`, trochee `Cc`, dactyl `Ccc`, amphibrach `cCc`, anapest `ccC` (`VERSE_METERS`). The meter with the fewest dictionary stresses of polysyllabic words on weak positions wins, ties are broken by the number of stressed ictuses. A stress in the anacrusis - on the syllables before the first ictus of the line - does not count as a violation (*Ста́ли дни холоднее*).
3.  **Disambiguation.** Monosyllabic prepositions, conjunctions and particles (`VERSE_PROCLITICS`) are unstressed, other monosyllables are stressed only on an ictus, polysyllabic function words (`VERSE_WEAK_WORDS`: или, чтобы) if the dictionary stress falls on an ictus. A dictionary stress of a polysyllabic word on a weak position is moved to the ictus if the word contains exactly one ictus, it is the only such word in the line or all of them are disyllabic (mobile stress: воды́ - во́ды), and no violations remain in the line after the move; a stress by the letter ё or in the anacrusis is never moved. A word without a dictionary stress gets its only ictus; with several ictuses, the stress of the last word of a line is chosen by rhyme with the neighbouring lines, otherwise the last ictus.
4.  **Check.** The meter is not determined if after fitting more than a tenth of the polysyllabic word stresses (`VERSE_MAX_DEVIATIONS`) remain on weak positions, or if more than 15% of their dictionary stresses were moved to an ictus (`VERSE_MAX_MOVED`) with four or more moves (`VERSE_MIN_MOVED`); stresses are then placed by the dictionary. The meter is also not fitted when there are fewer than six dictionary stresses of polysyllabic words (`VERSE_MIN_STRESSES`).

Rhymes are searched within a window of `RHYME_WINDOW` (4) lines inside a stanza by the phonetic key of the ending - the tail of the line from the last stressed word: the stressed vowel (я/а, ё/о, ю/у, ы/и are merged, е rhymes with о too), the consonant cluster after it as pronounced (with devoicing and simplification of clusters: стн - сн) and the number of syllables after the stress. The supporting consonant of open masculine endings and the post-tonic vowels are not compared, so both exact and approximate rhymes are found (*пламя - память*, *лето - одетой*); endings with different consonant clusters (*ветер - вечер*) do not rhyme. The letters of a rhyme scheme come in order of appearance: uppercase, then lowercase.

The accuracy was checked on the [RIFMA](https://github.com/Koziev/Rifma) dataset (5,121 stanzas with manual stress and rhyme annotation, MIT): stresses agree with the annotation for 97% of words (71% for out-of-dictionary words), pairs of rhyming lines are found with 94% precision and 90% recall, the whole stanza scheme matches in 78% of cases; the meter is undetermined for 8% of stanzas, including 3% because of the `VERSE_MIN_STRESSES` threshold. Part of the `STRESS_CORRECTIONS` fixes was collected from this very annotation, so the stress estimate is partly in-sample: the fixes collected from one half of the dataset add 0.1-0.2 percentage points on the other.

## Accentuation { #accentuate }

``` {.python .signature}
accentuate(text, stress_dict=None)
```

Places acute accents (U+0301) after the stressed vowels of a text by the dictionary, without the meter (the `VerseStats.accentuate` method fits the stresses to it); a stress mark already in the text is kept, while monosyllabic prepositions, conjunctions and particles and words without a found stress stay unmarked.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Text |
| `stress_dict` | `StressDict` | `None` | Stress dictionary; `StressDict()` by default |

Raises:

- `SourceTypeError` - a text that is not a string, a stress dictionary of another type;
- `DatasetNotFoundError` - the stress dictionary is not downloaded.

=== "Code"

    ``` python
    from ruts.verse_stats import accentuate

    accentuate("Уже поздно, замерли на полночь.")
    ```

=== "Result"

    ```
    'Уже́ по́здно, за́мерли на по́лночь.'
    ```

## Stanzas { #split_stanzas }

``` {.python .signature}
split_stanzas(text)
```

Splits a text into stanzas and lines: stanzas are separated by blank lines, lines without Russian words (numbers, asterisks) are skipped.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Text of the poem |

Raises:

- `SourceTypeError` - a text that is not a string.

=== "Code"

    ``` python
    from ruts.verse_stats import split_stanzas

    split_stanzas(
        "Буря мглою небо кроет,\nВихри снежные крутя;\n\n* * *\n\nТо, как зверь, она завоет,"
    )
    ```

=== "Result"

    ```
    [['Буря мглою небо кроет,', 'Вихри снежные крутя;'],
     ['То, как зверь, она завоет,']]
    ```
