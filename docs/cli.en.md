# Command line

The command `ruts` counts the statistics of texts without Python code: it prints them as a table, JSON or CSV, for the whole text or its parts, writes an HTML report and downloads the dictionaries. It is installed with the library; `python -m ruts` is the same.

``` bash
ruts download
ruts stats текст.txt
ruts stats -f json глава1.txt глава2.txt
ruts stats -s basic,readability -p sentences -f csv -o предложения.csv текст.txt
cat текст.txt | ruts stats -f json
ruts report текст.txt -t "Мой текст" -o отчет.html
```

## Command { #Command }

--8<-- "cli.md:Command"

In ruTS anySeg splits the text (`get_document`), and the classes of `-s` are:

| Name | Class |
| :--- | :---- |
| `basic` | [`BasicStats`](stats/basic_stats.md) |
| `readability` | [`ReadabilityStats`](stats/readability_stats.md) |
| `unadapted_readability` | [`UnadaptedReadabilityStats`](stats/unadapted_readability_stats.md) |
| `diversity` | [`DiversityStats`](stats/diversity_stats.md) |
| `morph` | [`MorphStats`](stats/morph_stats.md) |
| `lexical` | [`LexicalStats`](stats/lexical_stats.md) |
| `style` | [`StyleStats`](stats/style_stats.md) |
| `phon` | [`PhonStats`](stats/phon_stats.md) |
| `cohesion` | [`CohesionStats`](stats/cohesion_stats.md) |
| `verse` | [`VerseStats`](stats/verse_stats.md), only by its name in `-s` |

The command has no syntactic statistics: `SyntaxStats` needs a `Doc` with a dependency parse. `ruts download` downloads the [frequency dictionary](datasets/freq2011.md) `freq2011` for `lexical` and the [stress dictionary](datasets/stressdict.md) `stress_dict` for `verse`; without its dictionary a class is not counted, and its error names this command.

## Report { #Report }

--8<-- "report.md:Report"

In ruTS `Report` is in `ruts.report`: its classes are `STATS_CLASSES` of the same module, the classes of the command but `verse`; the columns of the sentences are the characters, the words, the syllables, the Flesch reading ease and the water; the highlighting is [`HighlightedText`](visualizers/highlight.md) with its default layers.

=== "Code"

    ``` python
    from ruts.report import Report

    report = Report(
        "Кот спит на окне. Пёс громко лает во дворе.", title="Два предложения", skip_errors=True
    )
    report.save("отчет.html")
    report.stats["basic"].n_words, len(report.document.sentences)
    ```

=== "Result"

    ```
    (9, 2)
    ```
