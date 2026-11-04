# Components

``` {.python .signature}
StatsComponent(nlp, name)
```

--8<-- "components.md:StatsComponent"

The components of ruTS are subclasses of the `StatsComponent` of the [anyTS](https://sergeyshk.github.io/anyTS/components/) core, one for every class of statistics.

!!! note "Note"
    The examples below use the [recommended pipeline](#load_pipeline) on the `ru_core_news_sm` model, which is installed separately: `python -m spacy download ru_core_news_sm` (see [installation](installation.md)).

=== "Code"

    ``` python
    import ruts

    nlp = ruts.load_pipeline()
    nlp.add_pipe("ruts_basic", name="basic")
    nlp("мама мыла раму")._.basic.c_letters
    nlp("?!")._.basic is None
    ```

=== "Result"

    ```
    {4: 3}
    True
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `nlp` | `Language` | - | Pipeline the component is added to |
| `name` | `str` | - | Name of the component in the pipeline and of the extension |

spaCy sets both at `nlp.add_pipe(factory, name=...)`; the other parameters of a component are passed in the `config` dictionary of the same call.

## Names { #names }

The factories carry the prefix of the library: `ruts_basic`, `ruts_readability`, `ruts_unadapted_readability`, `ruts_diversity`, `ruts_morph`, `ruts_syntax`, `ruts_cohesion`, `ruts_lexical`, `ruts_style`, `ruts_phon`, `ruts_verse`, and the component of sentence boundaries [`ruts_blank_lines`](#blank_lines). They are declared as entry points of `spacy_factories`, so a pipeline saved with these components (`nlp.to_disk(path)`) loads with `spacy.load(path)` without `import ruts`. `import ruts` does not load the components while spaCy is not loaded - the entry points find them; from the sources without an installed package, `import ruts.components` comes before `add_pipe`.

--8<-- "components.md:StatsComponent-names"

In `ruts_lexical` a document of numbers alone passes untouched as well, and in `ruts_verse` a document without letters.

--8<-- "components.md:StatsComponent-serialization"

Adding a component extends the spaCy tokenizer of its pipeline with the rules for the dialogue dashes glued to words (`ruts.utils.add_dash_rules`), so that a `Doc` is split into words the same way as a string; for your own pipeline without ruTS components call this function yourself. The anySeg tokenizer of the [recommended pipeline](#load_pipeline) splits words as a string, and the components leave it as it is.

ruTS removes stress marks from the words of a `Doc`. They do not change the parts of speech and features of the [recommended pipeline](#load_pipeline), but the model sees a word with a mark as unknown and tags it worse: on a text after `accentuate` the tagger of `ru_core_news_sm` changes the part of speech of over half of the words, and the dependencies change in both pipelines. Pass a text with stresses to the pipeline without them - `nlp(ruts.utils.strip_marks(text))`.

## Recommended pipeline { #load_pipeline }

``` {.python .signature}
load_pipeline(model='ru_core_news_sm', exclude=(), **kwargs)
```

A spaCy pipeline in which a `Doc` is annotated the same way as a string (except the hyphenated words that anySeg splits into parts - муж-то, скажи-ка, два-три: they are one word in a `Doc`): the tokens and the sentences come from the [anySeg](https://github.com/SergeyShk/anySeg) segmenter, the parts of speech, features and lemmas from the [ruMorph](https://github.com/SergeyShk/ruMorph) morphological analyzer in the context of the sentence, and the model gives the dependency parser and the named entities. The function loads the model with the anySeg tokenizer, without its `morphologizer` and `lemmatizer`, and adds the `anyseg_sentencizer` and `rumorph` components first: ruMorph analyzes the words in the context of the anySeg sentences. A saved pipeline of this kind loads as it is. The same by hand:

``` python
nlp = spacy.load(
    "ru_core_news_sm",
    exclude=["morphologizer", "lemmatizer"],
    config={"nlp": {"tokenizer": {"@tokenizers": "anyseg.Tokenizer.v1"}}},
)
nlp.add_pipe("anyseg_sentencizer", first=True)
nlp.add_pipe("rumorph", after="anyseg_sentencizer")
```

On UD SynTagRus this pipeline is more accurate than the model itself: the part of speech is right for 97.3 % of the words against 93.3 %, the dependency with its relation (LAS) for 82.7 % against 82.1 %. A plain `spacy.load("ru_core_news_sm")` is supported too, but then the parts of speech, features and sentences come from the model, and the statistics of a `Doc` may differ from those of the string. ruTS does not work around the errors of its tagger: the model tags коли and ежели as a verb or a noun, the connector значит as a verb and т.е. as a punctuation mark, so these connectors are not found (15 of 5525 on TextsByGrade and SovChLit), and боишься, смеешься as an infinitive, so the subordinate clause with them counts as an infinitive clause.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `model` | `str` | `"ru_core_news_sm"` | Name or path of the spaCy model: `ru_core_news_sm`, `ru_core_news_md`, `ru_core_news_lg` |
| `exclude` | `str`, `list[str]` | `()` | More components of the model not to load, for example `ner` |
| `**kwargs` | - | - | Other parameters of `spacy.load`; the tokenizer in `config` is replaced with anySeg |

=== "Code"

    ``` python
    from ruts import load_pipeline

    pipeline = load_pipeline()
    pipeline.pipe_names
    [(token.text, token.pos_, token.lemma_) for token in pipeline("Нож из стали.")]
    ```

=== "Result"

    ```
    ['anyseg_sentencizer', 'rumorph', 'tok2vec', 'parser', 'attribute_ruler', 'ner']
    [('Нож', 'NOUN', 'нож'), ('из', 'ADP', 'из'), ('стали', 'NOUN', 'сталь'), ('.', 'PUNCT', '.')]
    ```

## Components of the classes of statistics { #class-components }

| Component | Factory | Class of statistics | Parameters |
| :-------- | :------ | :------------------ | :--------- |
| [`BasicStatsComponent`](#BasicStatsComponent) | `ruts_basic` | `BasicStats` | - |
| [`MorphStatsComponent`](#MorphStatsComponent) | `ruts_morph` | `MorphStats` | - |
| [`ReadabilityStatsComponent`](#ReadabilityStatsComponent) | `ruts_readability` | `ReadabilityStats` | `preset`, `basic` |
| [`UnadaptedReadabilityStatsComponent`](#UnadaptedReadabilityStatsComponent) | `ruts_unadapted_readability` | `UnadaptedReadabilityStats` | `basic` |
| [`DiversityStatsComponent`](#DiversityStatsComponent) | `ruts_diversity` | `DiversityStats` | `window_len`, `mtld_threshold`, `mtld_min_len`, `hdd_sample_size`, `log_base` |
| [`StyleStatsComponent`](#StyleStatsComponent) | `ruts_style` | `StyleStats` | `stopwords`, `top_n`, `nausea_stopwords`, `cliches` |
| [`PhonStatsComponent`](#PhonStatsComponent) | `ruts_phon` | `PhonStats` | `window_len` |
| [`SyntaxStatsComponent`](#SyntaxStatsComponent) | `ruts_syntax` | `SyntaxStats` | - |
| [`CohesionStatsComponent`](#CohesionStatsComponent) | `ruts_cohesion` | `CohesionStats` | `blank_lines` |
| [`LexicalStatsComponent`](#LexicalStatsComponent) | `ruts_lexical` | `LexicalStats` | `data_dir` |
| [`VerseStatsComponent`](#VerseStatsComponent) | `ruts_verse` | `VerseStats` | `data_dir` |

### Basic statistics { #BasicStatsComponent }

``` {.python .signature}
BasicStatsComponent(nlp, name)
```

--8<-- "components.md:BasicStatsComponent"

### Morphological statistics { #MorphStatsComponent }

``` {.python .signature}
MorphStatsComponent(nlp, name)
```

--8<-- "components.md:MorphStatsComponent"

In ruTS the parts of speech and the features are taken from the annotation of the pipeline (`token.pos_`, `token.morph`): ruMorph gives them in the [recommended pipeline](#load_pipeline), the `morphologizer` in a plain model, and in a pipeline without them they come from the ruMorph analysis by word.

=== "Code"

    ``` python
    nlp.add_pipe("ruts_morph", name="morph")
    nlp("мама мыла раму")._.morph.case
    ```

=== "Result"

    ```
    ('Nom', None, 'Acc')
    ```

### Readability metrics { #ReadabilityStatsComponent }

``` {.python .signature}
ReadabilityStatsComponent(nlp, name, preset=None, basic=None)
```

--8<-- "components.md:ReadabilityStatsComponent"

The [presets](stats/readability_stats.md#presets) of ruTS are `plainrussian`, `fiction` and `academic`, the preset of the class `plainrussian`. In ruTS the class of statistics and its `basic_stats_class` are set, so the errors of `stats_class` and `SourceTypeError` do not occur; the message of `SourceError` names the component `ruts_basic` (`basic_factory`) to add before it.

=== "Code"

    ``` python
    nlp.add_pipe("ruts_readability", name="readability")
    config = {"preset": "fiction", "basic": "basic"}
    nlp.add_pipe("ruts_readability", name="readability_fiction", config=config)
    doc = nlp("Кот сидел на окне и смотрел на птиц, которые летали над крышами домов.")
    doc._.readability.flesch_kincaid_grade
    doc._.readability_fiction.flesch_kincaid_grade
    ```

=== "Result"

    ```
    -0.1506153846153886
    6.41769230769231
    ```

### Formulas of other languages { #UnadaptedReadabilityStatsComponent }

``` {.python .signature}
UnadaptedReadabilityStatsComponent(nlp, name, basic=None)
```

--8<-- "components.md:UnadaptedReadabilityStatsComponent"

The formulas are those of [`UnadaptedReadabilityStats`](stats/unadapted_readability_stats.md), with their original coefficients and without a calibration for Russian. As for `ReadabilityStatsComponent`, the errors of `stats_class` and `SourceTypeError` do not occur in ruTS, and the message of `SourceError` names the component `ruts_basic` to add before it.

=== "Code"

    ``` python
    nlp.add_pipe("ruts_unadapted_readability", name="unadapted", config={"basic": "basic"})
    doc = nlp("Кот сидел на окне и смотрел на птиц, которые летали над крышами домов.")
    doc._.unadapted.gulpease, doc._.unadapted.forcast
    doc._.unadapted.bs is doc._.basic
    ```

=== "Result"

    ```
    (69.0, 13.076923076923077)
    True
    ```

### Lexical diversity metrics { #DiversityStatsComponent }

``` {.python .signature}
DiversityStatsComponent(nlp, name, window_len=50, mtld_threshold=0.72, mtld_min_len=10, hdd_sample_size=42, log_base=10)
```

--8<-- "components.md:DiversityStatsComponent"

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `window_len` | `int` | `50` | Window size for MATTR and segment size for MSTTR |
| `mtld_threshold` | `float` | `0.72` | TTR threshold for MTLD, MA-MTLD and MTLD-W |
| `mtld_min_len` | `int` | `10` | Minimum factor length for MTLD, MA-MTLD and MTLD-W |
| `hdd_sample_size` | `int` | `42` | Sample size for HD-D |
| `log_base` | `float` | `10` | Logarithm base for the Summer, Maas and Dugast metrics |

=== "Code"

    ``` python
    config = {"window_len": 100, "log_base": 2.718281828459045}
    nlp.add_pipe("ruts_diversity", name="diversity", config=config)
    nlp("мама мыла раму")._.diversity.rttr
    ```

=== "Result"

    ```
    1.7320508075688774
    ```

### SEO style metrics { #StyleStatsComponent }

``` {.python .signature}
StyleStatsComponent(nlp, name, stopwords=None, top_n=10, nausea_stopwords=None, cliches=None)
```

--8<-- "components.md:StyleStatsComponent"

Without the lists the water words and the stopwords of the nausea are determined by the ruMorph tags, and the cliches come from `OFFICIALESE_CLICHES`; `NAUSEA_TOP_N` is a constant of `anyts.constants`.

=== "Code"

    ``` python
    nlp.add_pipe("ruts_style", name="style", config={"stopwords": ["и", "в", "не"], "top_n": 5})
    nlp("мама мыла раму")._.style.water
    nlp.add_pipe("ruts_style", name="style_cliches", config={"cliches": ["в целях", "в рамках"]})
    nlp("В целях экономии в рамках проекта мы закрыли склад.")._.style_cliches.cliches
    ```

=== "Result"

    ```
    0.0
    22.22222222222222
    ```

### Phonostatistics { #PhonStatsComponent }

``` {.python .signature}
PhonStatsComponent(nlp, name, window_len=3)
```

--8<-- "components.md:PhonStatsComponent"

=== "Code"

    ``` python
    nlp.add_pipe("ruts_phon", name="phon", config={"window_len": 5})
    nlp("мама мыла раму")._.phon.p_open_syllables
    ```

=== "Result"

    ```
    1.0
    ```

### Syntactic statistics { #SyntaxStatsComponent }

``` {.python .signature}
SyntaxStatsComponent(nlp, name)
```

--8<-- "components.md:SyntaxStatsComponent"

The [recommended pipeline](#load_pipeline) and the `ru_core_news_sm`, `ru_core_news_md` and `ru_core_news_lg` models have a parser and the parts of speech.

Raises:

- `SourceError` - a document without a dependency parse or parts of speech, in a pipeline without a parser or `morphologizer`.

=== "Code"

    ``` python
    nlp.add_pipe("ruts_syntax", name="syntax")
    nlp("Дом, построенный рабочими в прошлом году, был продан")._.syntax.tree_depth
    ```

=== "Result"

    ```
    4.0
    ```

### Cohesion statistics { #CohesionStatsComponent }

``` {.python .signature}
CohesionStatsComponent(nlp, name, blank_lines=False)
```

`CohesionStatsComponent` puts the cohesion statistics into the extension. It needs no parser, and a `Doc` without sentence boundaries is split into sentences by the Russian [`SentsExtractor`](extractors/sentences.md); when annotation is present, parts of speech are taken from it, lemmas - from ruMorph by the token's part of speech, without annotation - from the ruMorph analysis, as for a string. With `blank_lines` the paragraphs start after the blank lines alone, as in `CohesionStats`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `blank_lines` | `bool` | `False` | Start the paragraphs after the blank lines alone, for a text whose lines are wrapped inside its paragraphs; a paragraph is a line by default |

Raises:

- `ParameterError` - a `blank_lines` that is not a `bool`.

=== "Code"

    ``` python
    nlp.add_pipe("ruts_cohesion", name="cohesion")
    nlp.add_pipe("ruts_cohesion", name="paragraphs", config={"blank_lines": True})
    doc = nlp("Кот сидел на окне. Он смотрел на птиц. Птицы улетели,\nи кот уснул.")
    (
        doc._.cohesion.noun_overlap_adjacent,
        doc._.cohesion.n_paragraphs,
        doc._.paragraphs.n_paragraphs,
    )
    ```

=== "Result"

    ```
    (0.5, 2, 1)
    ```

### Lexical sophistication statistics { #LexicalStatsComponent }

``` {.python .signature}
LexicalStatsComponent(nlp, name, data_dir=None)
```

`LexicalStatsComponent` puts the lexical sophistication statistics into the extension. The frequency dictionary metrics require a downloaded [`FreqDict`](datasets/freq2011.md); the bands and lexical density are computed without it.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `data_dir` | `str` | `None` | Path to the frequency dictionary directory; if not given, the default directory is used |

Raises:

- `DatasetNotFoundError` - the frequency dictionary metrics and `get_stats()` when `FreqDict` is not downloaded.

=== "Code"

    ``` python
    nlp.add_pipe("ruts_lexical", name="lexical")
    nlp("Кот сидел на окне и смотрел на птиц")._.lexical.p_top1000
    ```

=== "Result"

    ```
    0.75
    ```

### Verse statistics { #VerseStatsComponent }

``` {.python .signature}
VerseStatsComponent(nlp, name, data_dir=None)
```

`VerseStatsComponent` puts the verse statistics into the extension; it requires a downloaded [`StressDict`](datasets/stressdict.md) stress dictionary. The component works on the `Doc` text with line breaks, so pass the poem text to `nlp` as is, without joining the lines. A text with letters but without Russian words gives empty statistics, like `VerseStats`, so `nlp.pipe` over a corpus does not stop on it.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `data_dir` | `str` | `None` | Path to the stress dictionary directory; if not given, the default directory is used |

Raises:

- `DatasetNotFoundError` - the stress dictionary is not downloaded; the first document with letters raises it.

=== "Code"

    ``` python
    nlp.add_pipe("ruts_verse", name="verse")
    poem = (
        "Буря мглою небо кроет,\nВихри снежные крутя;\n"
        "То, как зверь, она завоет,\nТо заплачет, как дитя"
    )
    doc = nlp(poem)
    doc._.verse.meter, doc._.verse.n_feet
    ```

=== "Result"

    ```
    ('хорей', 4)
    ```

## Sentences after blank lines { #blank_lines }

--8<-- "components.md:start_sents_after_blank_lines"

In ruTS the component is registered as `ruts_blank_lines`. Without it the parser of the `ru_core_news_sm` model glues a paragraph without a final mark to the next sentence, and the statistics of a `Doc` differ from those of the same string. In the [recommended pipeline](#load_pipeline) the sentences are split by `anyseg_sentencizer`, and the component is not needed.

=== "Code"

    ``` python
    import spacy

    nlp = spacy.load("ru_core_news_sm")
    nlp.add_pipe("ruts_blank_lines", before="parser")
    [sent.text.strip() for sent in nlp("Что нового\n\nБыстрый импорт. Меньше ошибок").sents]
    ```

=== "Result"

    ```
    ['Что нового', 'Быстрый импорт.', 'Меньше ошибок']
    ```
