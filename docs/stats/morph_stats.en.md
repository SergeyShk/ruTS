# Morphological statistics

``` {.python .signature}
MorphStats(source, words_extractor=None)
```

The morphological statistics of a text: the part of speech and the grammatical features of every word in [Universal Dependencies](https://universaldependencies.org/u/feat/) terms and their distributions. The data source is a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library; the statistics are computed when the object is created.

The class is built on the `Stats` statistics interface of the [anyTS](https://sergeyshk.github.io/anyTS/stats/stats/) core. The words of a string are extracted by the Russian [`WordsExtractor`](../extractors/words.md) or by a given extractor, which for a `Doc` is applied to its text; without an extractor the words of a `Doc` come from its tokens, and the parts of a hyphenated word that spaCy splits are joined.

Raises:

- `SourceTypeError` - a source that is neither a string nor a `Doc`, an extractor of another type;
- `SourceError` - a source without words.

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
    Сочинительный союз            |    2
    Подчинительный союз           |    2
    Наречие                       |    1

    -----------------Время------------------
    Настоящее                     |    1
    Будущее                       |    1
    Прошедшее                     |    1

    -----------------Число------------------
    Множественное                 |    3
    Единственное                  |    1

    ------------------Лицо------------------
    2                             |    1
    3                             |    1
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Data source |
| `words_extractor` | `WordsExtractor` | `None` | Word extraction tool; used for a `Doc` too, on its text |

## Attributes

| Attribute | Type | Description |
| :-------- | :--- | :---------- |
| `words` | `tuple[str]` | Words |
| `lemmas` | `tuple[str]` | Lemmas of the words: pymorphy3 by the part of speech of the word |
| `tags` | `tuple[str]` | Grammatical features of the words as strings in CoNLL-U format (`Animacy=Inan|Case=Nom|Gender=Masc|Number=Sing`, `_` without features) |

## Statistics

Every statistic is an attribute of the object, a tuple of the values of a feature by word (`None` for a word without the feature), and `get_stats` gives the distributions of their values. For a `Doc` object with part-of-speech annotation the values are taken from `token.pos_` and `token.morph`, that is, by context (стали is a verb or a noun). For a string, a `Doc` without annotation and a `Doc` with a words extractor given the first [pymorphy3](https://github.com/no-plagiarism/pymorphy3) analysis is used: the [OpenCorpora](http://opencorpora.org/dict.php?act=gram) grammemes are mapped to UD by the `OPENCORPORA_TO_UD_POS` and `OPENCORPORA_TO_UD_GRAMMEMES` tables of `ruts.constants`, and a feature that pymorphy3 gives two values at once (the animacy of words in -кки) is undefined.

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

The Russian names of the values for `print_stats` are `MORPHOLOGY_STATS_DESC` of `ruts.constants`. The values for a string and for an annotated `Doc` may differ: spaCy assigns `Voice=Act` to finite forms and `Voice=Mid` to reflexive verbs, distinguishes `AUX` and resolves homonymy by context; pymorphy3 determines voice only for participles and takes the first analysis.

<div class="metric-card" markdown>

### Part of speech { #pos }

`pos` · [UD](https://universaldependencies.org/u/pos/)
{ .metric-meta }

For a string the OpenCorpora parts of speech are mapped to UD as follows:

| OpenCorpora | UD | Note |
| :---------- | :- | :--- |
| `NOUN` | `NOUN`, `PROPN` | first names, surnames, patronymics, toponyms and organizations by pymorphy3 tags - `PROPN`, but only for capitalized word forms: pymorphy3 ignores case and tags ordinary words as names (лев, роза, мороз) |
| `ADJF`, `ADJS`, `COMP` | `ADJ`, `DET`, `PRON`, `NUM` | pronominal adjectives (этот, мой, весь) - `DET`, «который» - `PRON`, «один» - `NUM`; a comparative without context counts as an adjective |
| `VERB`, `INFN`, `PRTF`, `PRTS`, `GRND` | `VERB` | the form goes into `verb_form`: `Fin`, `Inf`, `Part`, `Conv`; the auxiliary `AUX` is distinguished only by spaCy |
| `NUMR`, `NUMB`, `ROMN` | `NUM` | |
| `ADVB`, `PRED` | `ADV` | predicatives (надо, нельзя) - adverbs without tense, as in the Russian UD corpora; the existential нет and нету, which UD treats as verbs, have the present tense |
| `NPRO` | `PRON` | |
| `PREP` | `ADP` | |
| `CONJ` | `CCONJ`, `SCONJ` | subordinating conjunctions by the `SUBORDINATING_CONJUNCTIONS` list (что, чтобы, если, когда, хотя, потому) |
| `PRCL` | `PART` | |
| `INTJ` | `INTJ` | |
| `LATN`, `UNKN` | `X` | |

есть is taken for a form of быть, not of есть meaning to eat.

</div>

<div class="metric-card" markdown>

### Degree, negation and short form { #derived }

`degree` · `polarity` · `style_variant`
{ .metric-meta }

For a string these features are derived by the rules of Russian UD. Adjectives (except pronominal ones) and adverbs have a degree: `Cmp` for the comparative and for более, менее, выше, ниже, `Sup` for the superlative (красивейший), `Pos` for the others. The particles не, ни and the answer нет (Нет, не пойду, but not Денег нет) carry the negation. Short adjectives and participles (рад, прочитана) carry the short form, but not the forms in -о like неверно, нужно, so a string has fewer short forms than a `Doc` of a model.

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

OpenCorpora features absent from Russian UD: transitivity (`Tran`, `Intr`) and clusivity (`In` - the speaker is included in the action, `Ex` - not included). They are computed via pymorphy3 for verbs (for a `Doc` - from the analysis with the spaCy lemma) and appear in the `tags` feature string as `Subcat` and `Clusivity`.

=== "Code"

    ``` python
    from ruts import MorphStats

    ms = MorphStats("Постарайтесь получить то, что любите")
    ms.tags[0]
    ms.transitivity, ms.involvement
    ```

=== "Result"

    ```
    'Aspect=Perf|Clusivity=Ex|Mood=Imp|Number=Plur|Subcat=Intr|VerbForm=Fin'
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

`get_stats(*args, filter_none=False, flat=False)` returns the distributions of the values of the statistics as a dictionary of counts for each. The statistics are chosen by their names separated by commas, all of them without names; `filter_none=True` drops the words without the feature (`None`), and `flat=True` gives keys like `pos_NOUN` instead of nested dictionaries, also without the words lacking the feature. A name that is not a statistic raises `UnknownStatError` - here and in `print_stats` and `explain_text`.

`print_stats(*args, filter_none=False)` prints the distributions of the chosen statistics as tables, the frequent values first, and `explain_text(*args, filter_none=False)` returns the words of the text in order with the values of the chosen statistics.

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
    {'pos': {'VERB': 6, 'CCONJ': 2, 'SCONJ': 2, 'ADV': 1},
     'tense': {'Pres': 1, 'Fut': 1, 'Past': 1},
     'number': {'Plur': 3, 'Sing': 1},
     'person': {'2': 1, '3': 1}}
    {'pos_VERB': 6,
     'pos_CCONJ': 2,
     'pos_SCONJ': 2,
     'pos_ADV': 1,
     'tense_Pres': 1,
     'tense_Fut': 1,
     'tense_Past': 1}
    (('Постарайтесь', {'pos': 'VERB', 'number': 'Plur'}),
     ('получить', {'pos': 'VERB'}),
     ('то', {'pos': 'CCONJ'}),
     ('что', {'pos': 'SCONJ'}),
     ('любите', {'pos': 'VERB', 'tense': 'Pres', 'number': 'Plur', 'person': '2'}),
     ('иначе', {'pos': 'ADV'}),
     ('придется', {'pos': 'VERB', 'tense': 'Fut', 'number': 'Sing', 'person': '3'}),
     ('полюбить', {'pos': 'VERB'}),
     ('то', {'pos': 'CCONJ'}),
     ('что', {'pos': 'SCONJ'}),
     ('получили', {'pos': 'VERB', 'tense': 'Past', 'number': 'Plur'}))
    ```

--8<-- "stats/stats.md:Stats-to_dataframe"

=== "Code"

    ``` python
    ms.to_dataframe().iloc[:, :4]
    ```

=== "Result"

    ```
       pos_VERB  pos_CCONJ  pos_SCONJ  pos_ADV
    0         6          2          2        1
    ```

`get_markers()` returns the [shares of the verb forms](#markers) as a dictionary, and `print_markers()` prints them as a table.

=== "Code"

    ``` python
    from ruts import MorphStats

    MorphStats("Если бы я знал, я бы пришел за книгами, прочитанными вчера").print_markers()
    ```

=== "Result"

    ```
                          Маркер                      |  Значение
    ---------------------------------------------------------------
    Изъявительное наклонение среди личных форм        |    0.00
    Повелительное наклонение среди личных форм        |    0.00
    Сослагательное наклонение среди личных форм       |    1.00
    Инфинитив среди форм глагола                      |    0.00
    Причастие среди форм глагола                      |    0.33
    Деепричастие среди форм глагола                   |    0.00
    Совершенный вид среди форм глагола с видом        |    0.67
    Страдательные причастия среди форм глагола        |    0.33
    Возвратные формы (-ся, -сь) среди форм глагола    |    0.00
    ```

The `describe` method is that of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the morphological statistics have no scales, so it gives `None` for the statistics of `get_stats`.
