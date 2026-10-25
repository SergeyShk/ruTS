# Компоненты

``` {.python .signature}
StatsComponent(nlp, name)
```

<!-- core: components.md:StatsComponent d49cea9 -->
Основа компонентов [spaCy](https://github.com/explosion/spaCy), которые кладут статистики текста в расширение `Doc`: компонент регистрирует расширение при добавлении в пайплайн и кладет статистики каждого документа в `doc._.<name>`. Разработка компонентов в целом описана в [документации spaCy](https://spacy.io/usage/processing-pipelines#custom-components).

Компоненты ruTS - подклассы `StatsComponent` ядра [anyTS](https://sergeyshk.github.io/anyTS/components/), по одному на каждый класс статистик.

!!! note "Примечание"
    Примеры ниже используют модель `ru_core_news_sm`, которая ставится отдельно: `python -m spacy download ru_core_news_sm` (см. [установку](installation.md)).

=== "Код"

    ``` python
    import ruts
    import spacy

    nlp = spacy.load("ru_core_news_sm")
    nlp.add_pipe("ruts_basic", name="basic")
    nlp("мама мыла раму")._.basic.c_letters
    nlp("?!")._.basic is None
    ```

=== "Результат"

    ```
    {4: 3}
    True
    ```

## Параметры

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `nlp` | `Language` | - | Пайплайн, в который добавляется компонент |
| `name` | `str` | - | Имя компонента в пайплайне и расширения |

Оба параметра задает spaCy при `nlp.add_pipe(factory, name=...)`, остальные параметры компонента передаются словарем `config` того же вызова.

## Имена { #names }

Фабрики носят префикс библиотеки: `ruts_basic`, `ruts_readability`, `ruts_diversity`, `ruts_morph`, `ruts_syntax`, `ruts_cohesion`, `ruts_lexical`, `ruts_style`, `ruts_phon`, `ruts_verse`, а также компонент границ предложений [`ruts_blank_lines`](#blank_lines). Они объявлены точками входа `spacy_factories`, поэтому пайплайн, сохраненный с этими компонентами (`nlp.to_disk(path)`), загружается через `spacy.load(path)` без `import ruts`. `import ruts` сам компоненты не грузит, пока spaCy не загружен, - их находят точки входа; из исходников без установки пакета перед `add_pipe` нужен `import ruts.components`.

<!-- core: components.md:StatsComponent-names 33ebb87 -->
Имя компонента в пайплайне - это имя расширения: `nlp.add_pipe(factory, name="basic")` кладет статистики в `doc._.basic`. Без `name` компонент и расширение получают имя фабрики. Расширение следует за компонентом, когда пайплайн переименовывает его (`nlp.rename_pipe`). Имя, занятое расширением другого пакета, дает `ParameterError` вместо замены: при `add_pipe` или на первом документе после `rename_pipe`, который переименовывает компонент раньше, чем тот узнает свое имя. Компонент, взятый из другого пайплайна (`add_pipe(name, source=other)`), - один и тот же объект в обоих, поэтому под новым именем он пишет и в то расширение в другом пайплайне; отдельный компонент дает фабрика, `add_pipe(factory, name=...)`. Один и тот же компонент можно добавить дважды под разными именами, с разными параметрами. Документ без слов - пустая строка, пробелы, одни знаки препинания - проходит компонент нетронутым, а его расширение остается `None`.

У `ruts_lexical` нетронутым проходит и документ из одних чисел, у `ruts_verse` - документ без букв.

<!-- core: components.md:StatsComponent-serialization a238412 -->
!!! warning "Сериализация"
    Компонент кладет в `doc._.<name>` объект класса статистик, который spaCy сериализовать не умеет: `Doc.to_bytes()`, `DocBin(store_user_data=True)` и `nlp.pipe(..., n_process>1)` с такими компонентами в пайплайне завершатся ошибкой. Для сохранения документа исключайте пользовательские данные (`doc.to_bytes(exclude=["user_data"])`) или сохраняйте `doc._.<name>.get_stats()` отдельно; для многопроцессной обработки считайте статистики в основном процессе после `nlp.pipe`, без компонентов.

Добавление компонента расширяет токенизатор его пайплайна правилами для приклеенных к словам тире реплик (`ruts.utils.add_dash_rules`), чтобы `Doc` делился на слова так же, как строка; для своего пайплайна без компонентов ruTS вызовите эту функцию сами.

Знаки ударения ruTS снимает со слов `Doc`, но части речи, признаки и зависимости дает модель, а она видит слово со знаком как незнакомое и размечает его хуже: на тексте после `accentuate` у модели `ru_core_news_sm` меняется часть речи больше половины слов. Текст с ударениями передавайте в пайплайн без них - `nlp(ruts.utils.strip_marks(text))`.

## Компоненты классов статистик { #class-components }

| Компонент | Фабрика | Класс статистик | Параметры |
| :-------- | :------ | :-------------- | :-------- |
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

### Основные статистики { #BasicStatsComponent }

``` {.python .signature}
BasicStatsComponent(nlp, name)
```

<!-- core: components.md:BasicStatsComponent 7b037d9 -->
`BasicStatsComponent` кладет основные статистики документа в его расширение.

### Морфологические статистики { #MorphStatsComponent }

``` {.python .signature}
MorphStatsComponent(nlp, name)
```

<!-- core: components.md:MorphStatsComponent 5d99bc4 -->
`MorphStatsComponent` кладет в расширение морфологические статистики; по умолчанию перед ним нужны части речи.

В ruTS части речи и признаки берутся из разметки модели (`token.pos_`, `token.morph`), а в пайплайне без `morphologizer` - из pymorphy3.

=== "Код"

    ``` python
    nlp.add_pipe("ruts_morph", name="morph")
    nlp("мама мыла раму")._.morph.case
    ```

=== "Результат"

    ```
    ('Nom', None, 'Acc')
    ```

### Метрики удобочитаемости { #ReadabilityStatsComponent }

``` {.python .signature}
ReadabilityStatsComponent(nlp, name, preset=None, basic=None)
```

<!-- core: components.md:ReadabilityStatsComponent 78d49ec -->
`ReadabilityStatsComponent` кладет в расширение метрики удобочитаемости, посчитанные по документу или, с `basic`, по основным статистикам, которые положил в него другой компонент. Библиотека задает `basic_factory` - фабрику своего компонента основных статистик, которую называет ошибка, если в том расширении их нет.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `preset` | `str` | `None` | Пресет коэффициентов, один из пресетов класса; если `None` - пресет класса по умолчанию |
| `basic` | `str` | `None` | Расширение компонента основных статистик, которые берутся вместо повторного подсчета |

Если `preset` оставлен `None`, конфигурация сохраненного пайплайна не содержит пресета, и загруженный пайплайн берет пресет класса по умолчанию; библиотека, которой нужно записать в конфигурацию свой пресет по умолчанию, задает его в сигнатуре своего подкласса.

Исключения:

- `ParameterError` - `stats_class`, который не конкретный класс, пресет, который не строка или не пресет класса, расширение, имя которого не строка;
- `SourceTypeError` - класс без `basic_stats_class` и без `basic`;
- `SourceError` - документ, в расширении `basic` которого нет основных статистик класса.

[Пресеты](stats/readability_stats.md#presets) ruTS - `plainrussian`, `fiction` и `academic`, пресет класса - `plainrussian`. В ruTS класс статистик и его `basic_stats_class` заданы, поэтому ошибок `stats_class` и `SourceTypeError` не бывает; сообщение `SourceError` называет компонент `ruts_basic` (`basic_factory`), который нужно добавить перед ним.

=== "Код"

    ``` python
    nlp.add_pipe("ruts_readability", name="readability")
    config = {"preset": "fiction", "basic": "basic"}
    nlp.add_pipe("ruts_readability", name="readability_fiction", config=config)
    doc = nlp("Кот сидел на окне и смотрел на птиц, которые летали над крышами домов.")
    doc._.readability.flesch_kincaid_grade
    doc._.readability_fiction.flesch_kincaid_grade
    ```

=== "Результат"

    ```
    -0.1506153846153886
    6.41769230769231
    ```

### Метрики лексического разнообразия { #DiversityStatsComponent }

``` {.python .signature}
DiversityStatsComponent(nlp, name, window_len=50, mtld_threshold=0.72, mtld_min_len=10, hdd_sample_size=42, log_base=10)
```

<!-- core: components.md:DiversityStatsComponent a13bd76 -->
`DiversityStatsComponent` кладет в расширение метрики лексического разнообразия, посчитанные классом библиотеки, который читает `Doc`. Его параметры - параметры `DiversityStats` с теми же значениями по умолчанию.

Исключения:

- `ParameterError` - неверный параметр (`check_params` разнообразия).

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `window_len` | `int` | `50` | Размер окна для MATTR и сегмента для MSTTR |
| `mtld_threshold` | `float` | `0.72` | Порог TTR для MTLD, MA-MTLD и MTLD-W |
| `mtld_min_len` | `int` | `10` | Минимальная длина фактора для MTLD, MA-MTLD и MTLD-W |
| `hdd_sample_size` | `int` | `42` | Размер выборки для HD-D |
| `log_base` | `float` | `10` | Основание логарифма для метрик Summer, Maas и Dugast |

=== "Код"

    ``` python
    config = {"window_len": 100, "log_base": 2.718281828459045}
    nlp.add_pipe("ruts_diversity", name="diversity", config=config)
    nlp("мама мыла раму")._.diversity.rttr
    ```

=== "Результат"

    ```
    1.7320508075688774
    ```

### SEO-метрики стиля { #StyleStatsComponent }

``` {.python .signature}
StyleStatsComponent(nlp, name, stopwords=None, top_n=10, nausea_stopwords=None, cliches=None)
```

<!-- core: components.md:StyleStatsComponent 0abace1 -->
`StyleStatsComponent` кладет в расширение метрики стиля.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `stopwords` | `list[str]` | `None` | Стоп-слова водности; если `None` - стоп-слова класса |
| `top_n` | `int` | `10` | Количество самых частых слов академической тошноты и естественности по закону Ципфа (`NAUSEA_TOP_N`) |
| `nausea_stopwords` | `list[str]` | `None` | Слова, исключаемые из самых частых слов академической тошноты; если `None` - слова класса |
| `cliches` | `list[str]` | `None` | Штампы; если `None` - штампы класса (`cliches_list`) |

Исключения:

- `SourceTypeError` - стоп-слова, стоп-слова тошноты или штампы, которые не список строк;
- `ParameterError` - `top_n`, который не целое число не меньше единицы.

Без списков слова «воды» и стоп-слова тошноты определяются по разметке pymorphy3, а штампы берутся из `OFFICIALESE_CLICHES`; `NAUSEA_TOP_N` - константа `anyts.constants`.

=== "Код"

    ``` python
    nlp.add_pipe("ruts_style", name="style", config={"stopwords": ["и", "в", "не"], "top_n": 5})
    nlp("мама мыла раму")._.style.water
    nlp.add_pipe("ruts_style", name="style_cliches", config={"cliches": ["в целях", "в рамках"]})
    nlp("В целях экономии в рамках проекта мы закрыли склад.")._.style_cliches.cliches
    ```

=== "Результат"

    ```
    0.0
    22.22222222222222
    ```

### Фоностатистики { #PhonStatsComponent }

``` {.python .signature}
PhonStatsComponent(nlp, name, window_len=3)
```

<!-- core: components.md:PhonStatsComponent 0e52eb9 -->
`PhonStatsComponent` кладет в расширение фонетические статистики; `window_len` (по умолчанию `PHON_WINDOW_LEN`) - окно в словах для аллитерации и ассонанса.

Исключения:

- `ParameterError` - `window_len`, который не целое число не меньше 2.

=== "Код"

    ``` python
    nlp.add_pipe("ruts_phon", name="phon", config={"window_len": 5})
    nlp("мама мыла раму")._.phon.p_open_syllables
    ```

=== "Результат"

    ```
    1.0
    ```

### Синтаксические статистики { #SyntaxStatsComponent }

``` {.python .signature}
SyntaxStatsComponent(nlp, name)
```

<!-- core: components.md:SyntaxStatsComponent f99599b -->
`SyntaxStatsComponent` кладет в расширение синтаксические статистики; перед ним нужны парсер и части речи.

Парсер и части речи есть в моделях `ru_core_news_sm`, `ru_core_news_md` и `ru_core_news_lg`.

Исключения:

- `SourceError` - документ без разбора зависимостей или частей речи, в пайплайне без парсера или `morphologizer`.

=== "Код"

    ``` python
    nlp.add_pipe("ruts_syntax", name="syntax")
    nlp("Дом, построенный рабочими в прошлом году, был продан")._.syntax.tree_depth
    ```

=== "Результат"

    ```
    4.0
    ```

### Статистики связности { #CohesionStatsComponent }

``` {.python .signature}
CohesionStatsComponent(nlp, name)
```

`CohesionStatsComponent` кладет в расширение статистики связности. Парсер ему не нужен, а `Doc` без границ предложений делится на предложения русским [`SentsExtractor`](extractors/sentences.md); при наличии разметки части речи берутся из нее, леммы - из pymorphy3 по части речи токена, без разметки - из первого разбора pymorphy3.

=== "Код"

    ``` python
    nlp.add_pipe("ruts_cohesion", name="cohesion")
    doc = nlp("Кот сидел на окне. Он смотрел на птиц. Птицы улетели, и кот уснул.")
    doc._.cohesion.noun_overlap_adjacent
    ```

=== "Результат"

    ```
    0.5
    ```

### Статистики лексической сложности { #LexicalStatsComponent }

``` {.python .signature}
LexicalStatsComponent(nlp, name, data_dir=None)
```

`LexicalStatsComponent` кладет в расширение статистики лексической сложности. Метрикам частотного словаря нужен загруженный [`FreqDict`](datasets/freq2011.md); полосы и лексическая плотность считаются и без него.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `data_dir` | `str` | `None` | Путь к директории с частотным словарем; если не задан, используется директория по умолчанию |

Исключения:

- `DatasetNotFoundError` - метрики частотного словаря и `get_stats()`, когда `FreqDict` не загружен.

=== "Код"

    ``` python
    nlp.add_pipe("ruts_lexical", name="lexical")
    nlp("Кот сидел на окне и смотрел на птиц")._.lexical.p_top1000
    ```

=== "Результат"

    ```
    0.75
    ```

### Стиховедческие статистики { #VerseStatsComponent }

``` {.python .signature}
VerseStatsComponent(nlp, name, data_dir=None)
```

`VerseStatsComponent` кладет в расширение стиховедческие статистики; ему нужен загруженный словарь ударений [`StressDict`](datasets/stressdict.md). Компонент работает по тексту `Doc` с переносами строк, поэтому текст стихотворения передается в `nlp` как есть, без склейки строк. Текст с буквами, но без русских слов дает пустые статистики, как `VerseStats`, поэтому `nlp.pipe` по корпусу на нем не останавливается.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `data_dir` | `str` | `None` | Путь к директории со словарем ударений; если не задан, используется директория по умолчанию |

Исключения:

- `DatasetNotFoundError` - словарь ударений не загружен; ошибку дает первый документ с буквами.

=== "Код"

    ``` python
    nlp.add_pipe("ruts_verse", name="verse")
    poem = (
        "Буря мглою небо кроет,\nВихри снежные крутя;\n"
        "То, как зверь, она завоет,\nТо заплачет, как дитя"
    )
    doc = nlp(poem)
    doc._.verse.meter, doc._.verse.n_feet
    ```

=== "Результат"

    ```
    ('хорей', 4)
    ```

## Предложения после пустых строк { #blank_lines }

<!-- core: components.md:start_sents_after_blank_lines b811493 -->
``` {.python .signature}
start_sents_after_blank_lines(doc)
```

Компонент ставит начало предложения на первый токен после пустой строки - перевода строки, необязательных пробельных символов и еще одного перевода строки, - чтобы заголовок, пункт списка или абзац без конечного знака были отдельным предложением, как в экстракторе предложений. Он ставится перед парсером, `senter` или `sentencizer`, а тот сохраняет его начала и расставляет остальные. Пробельные символы перед таким началом остаются в предыдущем предложении, а знаки, которые открывают абзац (тире реплики, `¡`, `«`), - при его первом слове. Сам по себе компонент предложения внутри абзаца не делит и ставит частичные границы (`has_sents`), поэтому статистики берут предложения такого документа из его текста. Разобранный документ, например повторно пропущенный через пайплайн, проходит нетронутым, потому что spaCy сохраняет его предложения. Языковая библиотека регистрирует компонент под своим префиксом: `Language.component("<prefix>_blank_lines", func=start_sents_after_blank_lines)`.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `doc` | `Doc` | - | Объект Doc |

В ruTS компонент зарегистрирован как `ruts_blank_lines`. Без него модель `ru_core_news_sm` склеивает абзац без конечного знака со следующим предложением, и статистики `Doc` расходятся со статистиками той же строки.

=== "Код"

    ``` python
    nlp = spacy.load("ru_core_news_sm")
    nlp.add_pipe("ruts_blank_lines", before="parser")
    [sent.text.strip() for sent in nlp("Что нового\n\nБыстрый импорт. Меньше ошибок").sents]
    ```

=== "Результат"

    ```
    ['Что нового', 'Быстрый импорт.', 'Меньше ошибок']
    ```
