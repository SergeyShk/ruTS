# Text highlighting

!!! info ""
    **ruts.visualizers.highlight()**, **ruts.visualizers.HighlightedText**, **ruts.visualizers.Highlight**

## Description

--8<-- "visualizers/highlight.md:HighlightedText"

The function `highlight` returns a `HighlightedText` object of ruTS with the layers in the style of the [Glavred](https://glvrd.ru/) and [Turgenev](https://turgenev.ashmanov.com/) services: long sentences, complex and rare words, passive voice, participial and adverbial clauses, genitive chains, split predicates, verbal nouns, compound prepositions, clichés, stop words, parentheticals, connectives, alliterations. One picture explains what the metric values are made of better than a table of numbers.

Highlighting layers:

| Group | Layer | What it marks | Statistic |
| :---- | :---: | :-----------: | :-------: |
| Readability | `long_sents` | Sentences with at least `long_sent_word_factor` words | [BasicStats](../stats/basic_stats.md), [ReadabilityStats](../stats/readability_stats.md) |
| | `complex_words` | Words with at least `complex_syl_factor` syllables | [BasicStats](../stats/basic_stats.md), [ReadabilityStats](../stats/readability_stats.md) |
| | `rare_words` | Words whose lemma is outside the embedded top-10000 list; numbers, Latin script, abbreviations and stop words are not highlighted | [LexicalStats](../stats/lexical_stats.md) |
| Syntax | `passive` | Passive verb forms together with the auxiliary verb | [SyntaxStats](../stats/syntax_stats.md) |
| | `participle_clauses` | Participial clauses | [SyntaxStats](../stats/syntax_stats.md) |
| | `converb_clauses` | Adverbial participle (converb) clauses | [SyntaxStats](../stats/syntax_stats.md) |
| | `genitive_chains` | Genitive chains together with the governing word | [SyntaxStats](../stats/syntax_stats.md) |
| | `split_predicates` | Split predicates from the verb to the nominal part | [SyntaxStats](../stats/syntax_stats.md) |
| Officialese | `verbal_nouns` | Verbal nouns | [StyleStats](../stats/style_stats.md) |
| | `compound_prepositions` | Compound prepositions from the `COMPOUND_PREPOSITIONS` list | [StyleStats](../stats/style_stats.md) |
| | `cliches` | Clichés from the `OFFICIALESE_CLICHES` list or the `cliches` parameter | [StyleStats](../stats/style_stats.md) |
| Style | `stopwords` | Stop words by part of speech or from the given list - the "water" of the text | [StyleStats](../stats/style_stats.md) |
| | `parentheticals` | Parenthetical words and phrases | [StyleStats](../stats/style_stats.md) |
| | `connectors` | Connectives by part of speech from the `Doc` annotation or pymorphy3, the tooltip shows the class and type | [CohesionStats](../stats/cohesion_stats.md) |
| Phonics | `alliteration` | Repeats of a consonant in adjacent words that are unlikely given Russian letter frequencies | [PhonStats](../stats/phon_stats.md) |

The groups are defined in `ruts.constants.HIGHLIGHT_LAYER_GROUPS`. The layers of the "Syntax" group are computed over the dependency tree and are available only for a `Doc` object with a dependency parse (the `ru_core_news_sm`, `ru_core_news_md`, `ru_core_news_lg` models). By default the `HIGHLIGHT_DEFAULT_LAYERS` layers are enabled - long sentences, complex words, passive voice, genitive chains, split predicates, clichés - among those available to the source; `layers="all"` enables all available ones. Fifteen layers at once overlap each other (a compound preposition consists of stop words, a connective may be a parenthetical), so pick the ones you need.

!!! note "Note"
    Alliteration is searched within a sentence as a chain of two or more adjacent words each of whose stems contains the same consonant letter. The stem is the common initial part of the word form and its pymorphy3 lemma (*крупных* → *крупны*, *руках* → *рука*): endings agree with neighboring words and repeat consonants by grammar rather than by sound (*этих крупных*, *своим целям и нуждам*). The probability of a chain under an independent letter distribution is the product over the words of the probabilities of meeting the consonant among the stem letters, $1 - (1 - f)^n$, where $f$ is the [frequency of the consonant](https://ru.wikipedia.org/wiki/Частотность) in Russian texts and $n$ the number of stem letters; a chain is highlighted if the probability is below the `alliteration_threshold`. About twenty consonants are checked at every position, so the threshold is strict: in prose about 5% of words are highlighted at 0.001, about 20% at 0.01, mostly random coincidences of frequent letters. A repeat of a rare consonant (*слышно, бесшумно шуршат камыши*) is noticeable in two or three words, a repeat of a frequent one in long words is expected and not highlighted. Words shorter than three letters, stop words and words without vowels neither break nor continue a chain, the letter *й* is not counted, since in the nominative case it is part of the adjective lemma. The alliteration index of [PhonStats](../stats/phon_stats.md) measures how clustered the repeats are across the whole text; the highlighting shows where they are.

## Language hooks

The class extends the `HighlightedText` of the [anyTS](https://sergeyshk.github.io/anyTS/visualizers/highlight/) core with the hooks of Russian from `ruts.constants`: the layers with their names in the legend are `HIGHLIGHT_LAYERS_DESC`, the layers on by default `HIGHLIGHT_DEFAULT_LAYERS`, the annotations of a `Doc` a layer needs `HIGHLIGHT_LAYER_ANNOTATIONS` (the syntactic layers need only a dependency parse, as the lemmas come from pymorphy3) and the styles of the layers `HIGHLIGHT_LAYER_STYLES`; the prefix of the CSS classes is `ruts`. The words of a string are split as by [`WordsExtractor`](../extractors/words.md) and its sentences by razdel; a `Doc` without sentence boundaries (`spacy.blank`, a pipeline without `parser` and `senter`) is split into sentences by razdel too, so the `long_sents` layer is available for it, and the parts of a hyphenated word of a `Doc` make one word.

## Parameters

--8<-- "visualizers/highlight.md:HighlightedText-parameters"

The parameters of the layers of ruTS:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `long_sent_word_factor` | int | `20` | Minimum number of words in a long sentence |
| `complex_syl_factor` | int | `4` | Minimum number of syllables in a complex word |
| `stopwords` | list[str]/set[str] | `None` | List or set of stop words; if not given, stop words are determined by part of speech with pymorphy3 |
| `cliches` | list[str]/set[str] | `None` | List or set of clichés; if not given, `OFFICIALESE_CLICHES` is used |
| `alliteration_threshold` | float | `0.001` | Probability threshold of a consonant repeat under an independent letter distribution, below which the repeat counts as alliteration |

A threshold that is not an integer of at least one or a probability outside (0, 1] raises `ParameterError`, stop words or clichés that are not strings `SourceTypeError`.

## Attributes

--8<-- "visualizers/highlight.md:HighlightedText-attributes"

--8<-- "visualizers/highlight.md:Highlight"

The note of a fragment gives the number of words in the sentence, of syllables in the word, the length of the chain or the consonant of the alliteration.

## Methods

### to_html

--8<-- "visualizers/highlight.md:HighlightedText-to_html"

### css

--8<-- "visualizers/highlight.md:HighlightedText-css"

## Usage example

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import spacy
    from ruts.visualizers import highlight

    # Prepare the data
    nlp = spacy.load("ru_core_news_sm")
    text = (
        "Проект, подготовленный за неделю, был одобрен советом без обсуждения. "
        "Повышение эффективности использования бюджетных средств обсуждалось, не выходя за рамки регламента. "
        "Участники, представлявшие региональные министерства, не смогли согласовать позиции по вопросам "
        "финансирования и распределения ответственности между ведомствами, поскольку каждое из них "
        "настаивало на собственной трактовке положений соглашения. "
        "Споры стихли, в кулуарах шумно шептались и шушукались, а решение было отложено "
        "до следующего заседания."
    )

    # Highlight the text with the default layers
    ht = highlight(nlp(text))
    ht.counts
    # {'long_sents': 1, 'complex_words': 26, 'passive': 4, 'genitive_chains': 2,
    #  'split_predicates': 0, 'cliches': 1}

    ht.highlights[:2]
    # (Highlight(start=8, end=22, layer='complex_words', note='сложное слово, 5 слогов'),
    #  Highlight(start=8, end=22, layer='passive', note='пассив без агенса'))

    # All layers
    highlight(nlp(text), layers="all").counts
    # {'long_sents': 1, 'complex_words': 26, 'rare_words': 3, 'passive': 4, 'participle_clauses': 2,
    #  'converb_clauses': 1, 'genitive_chains': 2, 'split_predicates': 0, 'verbal_nouns': 10,
    #  'compound_prepositions': 0, 'cliches': 1, 'stopwords': 17, 'parentheticals': 0,
    #  'connectors': 4, 'alliteration': 1}

    # Display in Jupyter or save the markup
    ht
    html = ht.to_html()
    ```

_Result_ (hover over a fragment to see the explanation):

<div class="ruts-highlight"><style>.ruts-highlight { line-height: 1.7; }
.ruts-highlight-legend { display: flex; flex-wrap: wrap; gap: 0.4em 1.2em; margin-bottom: 0.8em; font-size: 0.9em; }
.ruts-highlight-legend .ruts-hl { padding: 0 0.3em; }
.ruts-highlight-count { opacity: 0.6; margin-left: 0.3em; }
.ruts-highlight-text { white-space: pre-wrap; }
.ruts-highlight .ruts-hl.ruts-hl-long_sents, .ruts-highlight .ruts-hl.ruts-hl-stopwords, .ruts-highlight .ruts-hl.ruts-hl-complex_words, .ruts-highlight .ruts-hl.ruts-hl-rare_words, .ruts-highlight .ruts-hl.ruts-hl-passive, .ruts-highlight .ruts-hl.ruts-hl-verbal_nouns, .ruts-highlight .ruts-hl.ruts-hl-compound_prepositions, .ruts-highlight .ruts-hl.ruts-hl-cliches, .ruts-highlight .ruts-hl.ruts-hl-parentheticals { color: #1f2328; border-radius: 2px; }
.ruts-hl-long_sents { background: #fef9c3; }
.ruts-hl-stopwords { background: #bae6fd; }
.ruts-hl-complex_words { background: #fed7aa; }
.ruts-hl-rare_words { background: #e5e7eb; }
.ruts-hl-passive { background: #fecaca; }
.ruts-hl-verbal_nouns { background: #e9d5ff; }
.ruts-hl-compound_prepositions { background: #a7f3d0; }
.ruts-hl-cliches { background: #fbcfe8; }
.ruts-hl-parentheticals { background: #d9f99d; }
.ruts-hl-participle_clauses { border-bottom: 2px solid #7c3aed; }
.ruts-hl-converb_clauses { border-bottom: 2px solid #0d9488; }
.ruts-hl-genitive_chains { border-bottom: 2px solid #b45309; }
.ruts-hl-split_predicates { border-bottom: 2px solid #dc2626; }
.ruts-hl-connectors { border-bottom: 2px dashed #2563eb; }
.ruts-hl-alliteration { text-decoration-line: underline; text-decoration-style: dotted; text-decoration-color: #db2777; text-decoration-thickness: 2px; text-underline-offset: 3px; }
</style><div class="ruts-highlight-legend"><span><span class="ruts-hl ruts-hl-long_sents">Длинные предложения</span><span class="ruts-highlight-count">1</span></span><span><span class="ruts-hl ruts-hl-complex_words">Сложные слова</span><span class="ruts-highlight-count">26</span></span><span><span class="ruts-hl ruts-hl-passive">Пассив</span><span class="ruts-highlight-count">4</span></span><span><span class="ruts-hl ruts-hl-genitive_chains">Цепочки родительных</span><span class="ruts-highlight-count">2</span></span><span><span class="ruts-hl ruts-hl-split_predicates">Расщеплённые сказуемые</span><span class="ruts-highlight-count">0</span></span><span><span class="ruts-hl ruts-hl-cliches">Штампы</span><span class="ruts-highlight-count">1</span></span></div><div class="ruts-highlight-text">Проект, <span class="ruts-hl ruts-hl-complex_words ruts-hl-passive" title="сложное слово, 5 слогов; пассив без агенса">подготовленный</span> за неделю, <span class="ruts-hl ruts-hl-passive" title="пассив">был одобрен</span> советом без <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 5 слогов">обсуждения</span>. <span class="ruts-hl ruts-hl-complex_words ruts-hl-genitive_chains" title="сложное слово, 5 слогов; цепочка из 3 родительных">Повышение</span><span class="ruts-hl ruts-hl-genitive_chains" title="цепочка из 3 родительных"> </span><span class="ruts-hl ruts-hl-complex_words ruts-hl-genitive_chains" title="сложное слово, 5 слогов; цепочка из 3 родительных">эффективности</span><span class="ruts-hl ruts-hl-genitive_chains" title="цепочка из 3 родительных"> </span><span class="ruts-hl ruts-hl-complex_words ruts-hl-genitive_chains" title="сложное слово, 6 слогов; цепочка из 3 родительных">использования</span><span class="ruts-hl ruts-hl-genitive_chains" title="цепочка из 3 родительных"> бюджетных средств</span> <span class="ruts-hl ruts-hl-complex_words ruts-hl-passive" title="сложное слово, 4 слога; пассив без агенса">обсуждалось</span>, не выходя за рамки <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 4 слога">регламента</span>. <span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 4 слога">Участники</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов">, </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 5 слогов">представлявшие</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 6 слогов">региональные</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 4 слога">министерства</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов">, не смогли </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 4 слога">согласовать</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 4 слога">позиции</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-cliches" title="длинное предложение, 26 слов; штамп: «по вопросам»">по вопросам</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 7 слогов">финансирования</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> и </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 6 слогов">распределения</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 5 слогов">ответственности</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> между </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 4 слога">ведомствами</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов">, поскольку каждое из них </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 5 слогов">настаивало</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> на собственной </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-genitive_chains" title="длинное предложение, 26 слов; цепочка из 2 родительных">трактовке </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words ruts-hl-genitive_chains" title="длинное предложение, 26 слов; сложное слово, 4 слога; цепочка из 2 родительных">положений</span><span class="ruts-hl ruts-hl-long_sents ruts-hl-genitive_chains" title="длинное предложение, 26 слов; цепочка из 2 родительных"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words ruts-hl-genitive_chains" title="длинное предложение, 26 слов; сложное слово, 5 слогов; цепочка из 2 родительных">соглашения</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов">.</span> Споры стихли, в <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 4 слога">кулуарах</span> шумно шептались и <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 4 слога">шушукались</span>, а <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 4 слога">решение</span> <span class="ruts-hl ruts-hl-passive" title="пассив без агенса">было </span><span class="ruts-hl ruts-hl-complex_words ruts-hl-passive" title="сложное слово, 4 слога; пассив без агенса">отложено</span> до <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 5 слогов">следующего</span> <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 5 слогов">заседания</span>.</div></div>

Highlighting a string without a spaCy model enables all layers except the syntactic ones: by default long sentences, complex words and clichés.

!!! example "Example"

    ``` python
    from ruts.visualizers import highlight

    text = "Чуть слышно, бесшумно шуршат камыши. Повышение эффективности использования ресурсов обсуждалось."
    ht = highlight(text, layers=["complex_words", "alliteration"])
    ht.highlights
    # (Highlight(start=5, end=35, layer='alliteration', note='аллитерация на «ш»'),
    #  Highlight(start=37, end=46, layer='complex_words', note='сложное слово, 5 слогов'),
    #  Highlight(start=47, end=60, layer='complex_words', note='сложное слово, 5 слогов'),
    #  Highlight(start=61, end=74, layer='complex_words', note='сложное слово, 6 слогов'),
    #  Highlight(start=84, end=95, layer='complex_words', note='сложное слово, 4 слога'))
    ```
