# Statistic functions

## Algorithm { #algorithm }

Stresses and the meter are determined with the algorithm of Barakhnin, Kozhemyakina and Kuznetsova ([CEUR 2019](https://ceur-ws.org/Vol-2523/paper27.pdf)):

1.  **Dictionary stresses.** The stressed syllable of every word is looked up: by the letter ё, the only syllable of a monosyllable, otherwise the [`StressDict`](../datasets/stressdict.md) dictionary with the `STRESS_CORRECTIONS` fixes (erroneous and mobile dictionary stresses: ещё, себе́, пе́ред, зо́лото, леса́х). Hyphenated compounds are looked up as a whole, then by parts; poetic contractions (желанье - желание) and converbs (забыв - забывший) are looked up by the full form.
2.  **Meter fitting.** Each of the five meters has its own strong positions - ictuses: iamb `cC`, trochee `Cc`, dactyl `Ccc`, amphibrach `cCc`, anapest `ccC` (`VERSE_METERS`). The meter with the fewest dictionary stresses of polysyllabic words on weak positions wins, ties are broken by the number of stressed ictuses. A stress in the anacrusis - on the syllables before the first ictus of the line - does not count as a violation: it is common in ternary meters (*Ста́ли дни холоднее*).
3.  **Disambiguation.** Monosyllabic prepositions, conjunctions and particles (`VERSE_PROCLITICS`) are unstressed, other monosyllables are stressed only on an ictus; polysyllabic function words (`VERSE_WEAK_WORDS`: или, чтобы, перед, через, после) are stressed if the dictionary stress falls on an ictus. A dictionary stress of a polysyllabic word on a weak position is moved to the ictus if the word contains exactly one ictus, it is the only such word in the line or all of them are disyllabic (forms with mobile stress: воды́ - во́ды, реки́ - ре́ки), and no violations remain in the line after the move - otherwise the line is considered non-metrical. A word without a dictionary stress gets its only ictus; with several ictuses, the stress of the last word of a line is chosen by rhyme with the neighbouring lines, otherwise the last ictus.
4.  **Check.** If after fitting more than a tenth of the polysyllabic word stresses (`VERSE_MAX_DEVIATIONS`) remain on weak positions, the meter is not determined - the text is dolnik, accentual verse, free verse or prose; stresses are then placed by the dictionary.

Rhymes are searched within a window of `RHYME_WINDOW` (4) lines inside a stanza by the phonetic key of the ending - the tail of the line from the last stressed word: the stressed vowel (я/а, ё/о, ю/у, ы/и are merged; е is kept and rhymes with о to catch ё written as е), the consonant cluster after it (without ь and ъ, with final devoicing, simplification of unpronounceable clusters стн - сн, тс - ц, collapsing of doubled consonants and -ого/-его replaced with -ово/-ево) and the number of syllables after the stress. The supporting consonant of open masculine endings and the post-tonic vowels are not compared, so both exact and approximate rhymes are found (*пламя - память*, *много - снова*); endings with different consonant clusters (*ветер - вечер*) do not rhyme. A rhyme scheme is written with letters in order of appearance, unrhymed lines with a hyphen.

The accuracy was checked on the [RIFMA](https://github.com/Koziev/Rifma) dataset (5,121 stanzas with manual stress annotation and rhyme schemes, MIT): stresses agree with the annotation for 97% of words (97% for polysyllabic dictionary words, 75% for out-of-dictionary words), pairs of rhyming lines are found with 93% precision and 90% recall, the whole stanza scheme matches in 78% of cases; the meter is undetermined for 5% of stanzas.

## Stressed syllable { #word_stress }

!!! info ""
    **ruts.verse_stats.word_stress()**

Determines the stressed syllable of a word by the dictionary (step 1 of the algorithm). Syllables are counted by vowels from zero; the stressed syllable itself can be obtained by splitting the word with [`syllabify`](phon_stats_funcs.md#syllabify).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |
| `stress_dict` | StressDict | `None` | Stress dictionary; `StressDict()` if not given |

Returns `None` if the word is not found or has no vowels.

!!! example "Example"

    ``` python
    from ruts.phon_stats import syllabify
    from ruts.verse_stats import word_stress

    word_stress("корова"), word_stress("ещё"), word_stress("желанье"), word_stress("кто-нибудь")
    # (1, 1, 1, 0)
    word_stress("хмурота")
    # None
    syllabify("корова")[word_stress("корова")]
    # 'ро'
    ```

## Accentuation { #accentuate }

!!! info ""
    **ruts.verse_stats.accentuate()**

Places stresses in a text by the dictionary: an acute accent (U+0301) is put after the stressed vowel of every word; monosyllabic prepositions, conjunctions and particles and words without a found stress stay unmarked. The meter is not taken into account: for verse with stresses fitted to the meter use the [`VerseStats.accentuate`](verse_stats.md#accentuate) method.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | str | `-` | Text |
| `stress_dict` | StressDict | `None` | Stress dictionary; `StressDict()` if not given |

!!! example "Example"

    ``` python
    from ruts.verse_stats import accentuate

    accentuate("Уже поздно, замерли на полночь.")
    # 'Уже́ по́здно, за́мерли на по́лночь.'
    ```

## Meter { #detect_meter }

!!! info ""
    **ruts.verse_stats.detect_meter()**

Determines the meter of a poem: ямб (iamb), хорей (trochee), дактиль (dactyl), амфибрахий (amphibrach), анапест (anapest) or `None` if no syllabo-tonic meter fits.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | str | `-` | Text of the poem |
| `stress_dict` | StressDict | `None` | Stress dictionary; `StressDict()` if not given |

## Rhyme scheme { #rhyme_scheme }

!!! info ""
    **ruts.verse_stats.rhyme_scheme()**

Determines the rhyme scheme of a poem: stanza schemes separated by spaces, unrhymed lines marked with a hyphen.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | str | `-` | Text of the poem |
| `stress_dict` | StressDict | `None` | Stress dictionary; `StressDict()` if not given |

!!! example "Example"

    ``` python
    from ruts.verse_stats import detect_meter, rhyme_scheme

    text = """Тучки небесные, вечные странники!
    Степью лазурною, цепью жемчужною
    Мчитесь вы, будто как я же, изгнанники,
    С милого севера в сторону южную.

    Кто же вас гонит: судьбы ли решение?
    Зависть ли тайная? злоба ль открытая?
    Или на вас тяготит преступление?
    Или друзей клевета ядовитая?"""

    detect_meter(text), rhyme_scheme(text)
    # ('дактиль', 'ABAB ABAB')

    blok = """Девушка пела в церковном хоре
    О всех усталых в чужом краю,
    О всех кораблях, ушедших в море,
    О всех, забывших радость свою."""

    detect_meter(blok), rhyme_scheme(blok)
    # (None, 'ABAB')
    ```

## Stanzas { #split_stanzas }

!!! info ""
    **ruts.verse_stats.split_stanzas()**

Splits a text into stanzas and lines: stanzas are separated by blank lines, lines without Russian words (numbers, asterisks) are skipped.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | str | `-` | Text of the poem |

!!! example "Example"

    ``` python
    from ruts.verse_stats import split_stanzas

    split_stanzas("Буря мглою небо кроет,\nВихри снежные крутя;\n\n* * *\n\nТо, как зверь, она завоет,")
    # [['Буря мглою небо кроет,', 'Вихри снежные крутя;'], ['То, как зверь, она завоет,']]
    ```
