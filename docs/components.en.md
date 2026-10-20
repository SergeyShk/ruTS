# Components

``` {.python .signature}
StatsComponent(nlp, name)
```

--8<-- "components.md:StatsComponent"

The components of ruTS are subclasses of the `StatsComponent` of the [anyTS](https://sergeyshk.github.io/anyTS/components/) core, one for every class of statistics.

!!! note "Note"
    The examples below use the `ru_core_news_sm` model, which is installed separately: `python -m spacy download ru_core_news_sm` (see [installation](installation.md)).

=== "Code"

    ``` python
    import ruts
    import spacy

    nlp = spacy.load("ru_core_news_sm")
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

The factories carry the prefix of the library: `ruts_basic`, `ruts_readability`, `ruts_diversity`, `ruts_morph`, `ruts_syntax`, `ruts_cohesion`, `ruts_lexical`, `ruts_style`, `ruts_phon`, `ruts_verse`, and the component of sentence boundaries [`ruts_blank_lines`](#blank_lines). They are declared as entry points of `spacy_factories`, so a pipeline saved with these components (`nlp.to_disk(path)`) loads with `spacy.load(path)` without `import ruts`. `import ruts` does not load the components while spaCy is not loaded - the entry points find them; from the sources without an installed package, `import ruts.components` comes before `add_pipe`.

--8<-- "components.md:StatsComponent-names"

In `ruts_lexical` a document of numbers alone passes untouched as well, and in `ruts_verse` a document without letters.

--8<-- "components.md:StatsComponent-serialization"

Adding a component extends the tokenizer of its pipeline with the rules for the dialogue dashes glued to words (`ruts.utils.add_dash_rules`), so that a `Doc` is split into words the same way as a string; for your own pipeline without ruTS components call this function yourself.

ruTS removes stress marks from the words of a `Doc`, but the parts of speech, features and dependencies come from the model, which sees a word with a mark as unknown and tags it worse: on a text after `accentuate` the `ru_core_news_sm` model changes the part of speech of over half of the words. Pass a text with stresses to the pipeline without them - `nlp(ruts.utils.strip_marks(text))`.

## Components of the classes of statistics { #class-components }

| Component | Factory | Class of statistics | Parameters |
| :-------- | :------ | :------------------ | :--------- |
| [`BasicStatsComponent`](#BasicStatsComponent) | `ruts_basic` | `BasicStats` | - |
| [`MorphStatsComponent`](#MorphStatsComponent) | `ruts_morph` | `MorphStats` | - |
| [`ReadabilityStatsComponent`](#ReadabilityStatsComponent) | `ruts_readability` | `ReadabilityStats` | `preset`, `basic` |
| [`DiversityStatsComponent`](#DiversityStatsComponent) | `ruts_diversity` | `DiversityStats` | `window_len`, `mtld_threshold`, `mtld_min_len`, `hdd_sample_size`, `log_base` |
| [`StyleStatsComponent`](#StyleStatsComponent) | `ruts_style` | `StyleStats` | `stopwords`, `top_n`, `nausea_stopwords`, `cliches` |
| [`PhonStatsComponent`](#PhonStatsComponent) | `ruts_phon` | `PhonStats` | `window_len` |
| [`SyntaxStatsComponent`](#SyntaxStatsComponent) | `ruts_syntax` | `SyntaxStats` | - |
| [`CohesionStatsComponent`](#CohesionStatsComponent) | `ruts_cohesion` | `CohesionStats` | - |
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

`MorphStatsComponent` puts the morphological statistics into the extension. Parts of speech and features are taken from the model annotation (`token.pos_`, `token.morph`), in a pipeline without a tagger - from pymorphy3.

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

The [presets](stats/readability_stats.md#presets) of ruTS are `plainrussian`, `fiction` and `academic`, the preset of the class `plainrussian`; `basic_factory` is `ruts_basic`.

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

Without the lists the water words and the stopwords of the nausea are determined by the pymorphy3 tags, and the cliches come from `OFFICIALESE_CLICHES`.

=== "Code"

    ``` python
    nlp.add_pipe("ruts_style", name="style", config={"stopwords": ["и", "в", "не"], "top_n": 5})
    nlp("мама мыла раму")._.style.water
    ```

=== "Result"

    ```
    0.0
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

The `ru_core_news_sm`, `ru_core_news_md` and `ru_core_news_lg` models have a parser; in a pipeline without a parser the component raises `SourceError`.

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
CohesionStatsComponent(nlp, name)
```

`CohesionStatsComponent` puts the cohesion statistics into the extension. The component only needs sentence boundaries (a model or `sentencizer`); when annotation is present, parts of speech are taken from it, lemmas - from pymorphy3 by the token's part of speech.

=== "Code"

    ``` python
    nlp.add_pipe("ruts_cohesion", name="cohesion")
    doc = nlp("Кот сидел на окне. Он смотрел на птиц. Птицы улетели, и кот уснул.")
    doc._.cohesion.noun_overlap_adjacent
    ```

=== "Result"

    ```
    0.5
    ```

### Lexical sophistication statistics { #LexicalStatsComponent }

``` {.python .signature}
LexicalStatsComponent(nlp, name, data_dir=None)
```

`LexicalStatsComponent` puts the lexical sophistication statistics into the extension. The frequency dictionary metrics require a downloaded [`FreqDict`](datasets/freq2011.md); the bands and lexical density are computed without it.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `data_dir` | `str` | `None` | Path to the frequency dictionary directory; if not given, the default directory is used |

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

In ruTS the component is registered as `ruts_blank_lines`. Without it the `ru_core_news_sm` model glues a paragraph without a final mark to the next sentence, and the statistics of a `Doc` differ from those of the same string.

=== "Code"

    ``` python
    nlp = spacy.load("ru_core_news_sm")
    nlp.add_pipe("ruts_blank_lines", before="parser")
    [sent.text.strip() for sent in nlp("Что нового\n\nБыстрый импорт. Меньше ошибок").sents]
    ```

=== "Result"

    ```
    ['Что нового', 'Быстрый импорт.', 'Меньше ошибок']
    ```
