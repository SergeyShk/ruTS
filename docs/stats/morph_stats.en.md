# Morphological statistics

``` {.python .signature}
MorphStats(source, words_extractor=None)
```

--8<-- "stats/morph_stats.md:MorphStats"

In ruTS the data source is a text or a `Doc` with or without part-of-speech annotation. A source that is neither a string nor a `Doc` and an extractor of another type raise `SourceTypeError`, and only a source without words raises `SourceError`.

The class extends the `MorphStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/morph_stats/) core with the Russian analysis of the words and the [markers of the verb forms](#markers). The words of a string are extracted by the Russian [`WordsExtractor`](../extractors/words.md) or by a given extractor; the words of a `Doc` without an extractor are its tokens with the parts of a hyphenated word joined: муж-то, скажи-ка are one word in a `Doc` and two in a string. The `print_stats` and `print_markers` tables and the error messages are in Russian (`MORPHOLOGY_STATS_DESC`, `MORPHOLOGY_MARKERS_DESC` and `CORE_MESSAGES` of `ruts.constants`).

=== "Code"

    ``` python
    from ruts import MorphStats

    text = "Постарайтесь получить то, что любите, иначе придется полюбить то, что получили"
    ms = MorphStats(text)
    ms.print_stats("pos", "tense", "number", "person", filter_none=True)
    ```

=== "Result"

    ```
    ---------------Часть речи---------------
    Глагол                        |    6
    Местоимение-существительное   |    4
    Наречие                       |    1

    -----------------Время------------------
    Настоящее                     |    1
    Будущее                       |    1
    Прошедшее                     |    1

    -----------------Число------------------
    Единственное                  |    5
    Множественное                 |    3

    ------------------Лицо------------------
    2                             |    2
    3                             |    1
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Data source |
| `words_extractor` | `WordsExtractor` | `None` | Word extraction tool; used for a `Doc` too, on its text |

## Attributes

--8<-- "stats/morph_stats.md:MorphStats-attributes"

ruTS also has the attribute `lemmas` (`tuple[str]`) - the lemmas of the words by the ruMorph analysis.

## Statistics

The statistics are the part of speech `pos` and the features of the table below (`MORPHOLOGY_FEATURES` of `ruts.constants`). For a `Doc` with part-of-speech annotation the values are taken from `token.pos_` and `token.morph`, for a string from the analysis of the [ruMorph](https://github.com/SergeyShk/ruMorph) morphological analyzer in the context of the sentence (UD parts of speech and features by the conventions of the SynTagRus corpus), for a `Doc` without annotation the same in the sentences whose words are those of the string. The other words, as with a words extractor given, get the first analysis without their neighbours.

| Statistic | Feature | Values |
| :-------- | :------ | :----- |
| [`pos`](#pos) | Part of speech | `NOUN`, `PROPN`, `VERB`, `AUX`, `ADJ`, `DET`, `PRON`, `NUM`, `ADV`, `ADP`, `CCONJ`, `SCONJ`, `PART`, `INTJ`, `X` |
| `animacy` | Animacy | `Anim`, `Inan` |
| `aspect` | Aspect | `Perf`, `Imp` |
| `case` | Case | `Nom`, `Gen`, `Dat`, `Acc`, `Ins`, `Loc`, `Par`, `Voc` |
| [`degree`](#derived) | Degree of comparison | `Pos`, `Cmp`, `Sup` |
| `gender` | Gender | `Masc`, `Fem`, `Neut`, `Com` |
| [`involvement`](#opencorpora) | Clusivity | `In`, `Ex` |
| `mood` | Mood | `Ind`, `Imp`, `Cnd` |
| `number` | Number | `Sing`, `Plur` |
| `person` | Person | `1`, `2`, `3` |
| [`polarity`](#derived) | Negation | `Neg` |
| [`style_variant`](#derived) | Short form | `Short` |
| `tense` | Tense | `Past`, `Pres`, `Fut` |
| [`transitivity`](#opencorpora) | Transitivity | `Tran`, `Intr` |
| `verb_form` | Verb form | `Fin`, `Inf`, `Part`, `Conv` |
| `voice` | Voice | `Act`, `Pass`, `Mid` |

For a `Doc` of the [recommended pipeline](../components.md#load_pipeline) the values are those of the string: ruMorph annotates it. With a plain spaCy model they may differ: it resolves homonymy with its own model and in places by other conventions (it gives the existential нет the present tense).

<div class="metric-card" markdown>

### Part of speech { #pos }

`pos` · [UD](https://universaldependencies.org/u/pos/)
{ .metric-meta }

The parts of speech of a string: predicatives (надо, the existential нет) - `VERB` without a verb form, который - `DET`, parenthetical words (конечно) - `ADV`, the auxiliary быть - `AUX`, proper nouns - `PROPN` with regard to case (Вера, but вера). A homonym is analyzed by its neighbours: стали in Мы стали ждать is a verb, in Нож сделан из стали a noun.

</div>

<div class="metric-card" markdown>

### Degree, negation and short form { #derived }

`degree` · `polarity` · `style_variant`
{ .metric-meta }

Adjectives (except pronominal ones) and adverbs have a degree: `Cmp` for the comparative, `Sup` for the superlative (красивейший), `Pos` for the others. не, ни and нет carry the negation. Short adjectives and participles (рад, прочитана) carry the short form, the feature `Variant=Short`.

=== "Code"

    ``` python
    from ruts import MorphStats

    ms = MorphStats("Нет, я не рад: книга прочитана быстрее красивейшей сказки")
    ms.explain_text("degree", "polarity", "style_variant", filter_none=True)
    ```

=== "Result"

    ```
    (('Нет', {'polarity': 'Neg'}),
     ('я', {}),
     ('не', {'polarity': 'Neg'}),
     ('рад', {'degree': 'Pos', 'style_variant': 'Short'}),
     ('книга', {}),
     ('прочитана', {'style_variant': 'Short'}),
     ('быстрее', {'degree': 'Cmp'}),
     ('красивейшей', {'degree': 'Sup'}),
     ('сказки', {}))
    ```

</div>

<div class="metric-card" markdown>

### Transitivity and clusivity { #opencorpora }

`transitivity` · `involvement` · [OpenCorpora](http://opencorpora.org/dict.php?act=gram)
{ .metric-meta }

OpenCorpora features absent from Russian UD: transitivity (`Tran`, `Intr`) and clusivity (`In` - the speaker is included in the action, `Ex` - not included). They are taken from the labels of the ruMorph analysis of verbs and appear in the `tags` feature string as `Subcat` and `Clusivity`.

=== "Code"

    ``` python
    from ruts import MorphStats

    ms = MorphStats("Постарайтесь получить то, что любите")
    ms.tags[0]
    ms.transitivity, ms.involvement
    ```

=== "Result"

    ```
    'Aspect=Perf|Clusivity=Ex|Mood=Imp|Number=Plur|Person=2|Subcat=Intr|VerbForm=Fin|Voice=Mid'
    (('Intr', 'Tran', None, None, 'Tran'), ('Ex', None, None, None, None))
    ```

</div>

<div class="metric-card" markdown>

### Verb forms { #markers }

`get_markers()` · `print_markers()`
{ .metric-meta }

The shares of the grammatical forms of the verb (the words with the part of speech `VERB` and `AUX`), each of its own base; a share with an empty base is `nan`.

| Marker | Share | Base |
| :----- | :---- | :--- |
| `p_indicative`, `p_imperative`, `p_conditional` | of the indicative, imperative and conditional mood | finite forms |
| `p_infinitive`, `p_participle`, `p_converb` | of infinitives, participles and converbs | all verb forms |
| `p_perfective` | of the perfective aspect | verb forms with aspect |
| `p_passive` | of passive participles | all verb forms |
| `p_reflexive` | of reflexive forms in -ся, -сь | all verb forms |

The conditional mood is detected by the particle бы (б), so the words extractor must not drop particles.

=== "Code"

    ``` python
    from ruts import MorphStats

    ms = MorphStats("Если бы я знал, я бы пришел за книгами, прочитанными вчера")
    ms.get_markers()
    ```

=== "Result"

    ```
    {'p_indicative': 0.0,
     'p_imperative': 0.0,
     'p_conditional': 1.0,
     'p_infinitive': 0.0,
     'p_participle': 0.3333333333333333,
     'p_converb': 0.0,
     'p_perfective': 0.6666666666666666,
     'p_passive': 0.3333333333333333,
     'p_reflexive': 0.0}
    ```

</div>

## Methods

--8<-- "stats/morph_stats.md:MorphStats-get_stats"

--8<-- "stats/morph_stats.md:MorphStats-explain_text"

--8<-- "stats/morph_stats.md:MorphStats-print_stats"

=== "Code"

    ``` python
    from ruts import MorphStats

    text = "Постарайтесь получить то, что любите, иначе придется полюбить то, что получили"
    ms = MorphStats(text)
    ms.get_stats("pos", "tense", "number", "person", filter_none=True)
    ms.get_stats("pos", "tense", flat=True)
    ms.explain_text("pos", "tense", "number", "person", filter_none=True)
    ```

=== "Result"

    ```
    {'pos': {'VERB': 6, 'PRON': 4, 'ADV': 1},
     'tense': {'Pres': 1, 'Fut': 1, 'Past': 1},
     'number': {'Plur': 3, 'Sing': 5},
     'person': {'2': 2, '3': 1}}
    {'pos_VERB': 6, 'pos_PRON': 4, 'pos_ADV': 1, 'tense_Pres': 1, 'tense_Fut': 1, 'tense_Past': 1}
    (('Постарайтесь', {'pos': 'VERB', 'number': 'Plur', 'person': '2'}),
     ('получить', {'pos': 'VERB'}),
     ('то', {'pos': 'PRON', 'number': 'Sing'}),
     ('что', {'pos': 'PRON', 'number': 'Sing'}),
     ('любите', {'pos': 'VERB', 'tense': 'Pres', 'number': 'Plur', 'person': '2'}),
     ('иначе', {'pos': 'ADV'}),
     ('придется', {'pos': 'VERB', 'tense': 'Fut', 'number': 'Sing', 'person': '3'}),
     ('полюбить', {'pos': 'VERB'}),
     ('то', {'pos': 'PRON', 'number': 'Sing'}),
     ('что', {'pos': 'PRON', 'number': 'Sing'}),
     ('получили', {'pos': 'VERB', 'tense': 'Past', 'number': 'Plur'}))
    ```

--8<-- "stats/stats.md:Stats-to_dataframe"

=== "Code"

    ``` python
    ms.to_dataframe().iloc[:, :4]
    ```

=== "Result"

    ```
       pos_VERB  pos_PRON  pos_ADV  animacy_Inan
    0         6         4        1             4
    ```

--8<-- "stats/morph_stats.md:MorphStats-markers"

In ruTS the markers are the [shares of the verb forms](#markers).

=== "Code"

    ``` python
    from ruts import MorphStats

    MorphStats("Если бы я знал, я бы пришел за книгами, прочитанными вчера").print_markers()
    ```

=== "Result"

    ```
                        Маркер                     | Значение
    ----------------------------------------------------------
    Изъявительное наклонение среди личных форм     |   0.00
    Повелительное наклонение среди личных форм     |   0.00
    Сослагательное наклонение среди личных форм    |   1.00
    Инфинитив среди форм глагола                   |   0.00
    Причастие среди форм глагола                   |   0.33
    Деепричастие среди форм глагола                |   0.00
    Совершенный вид среди форм глагола с видом     |   0.67
    Страдательные причастия среди форм глагола     |   0.33
    Возвратные формы (-ся, -сь) среди форм глагола |   0.00
    ```

The `describe` method of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core gives `None` for the statistics of `get_stats`: the morphological statistics have no scales.

--8<-- "stats/morph_stats.md:MorphWord"

In ruTS `MorphWord` is imported from `ruts.morph_stats` too.
