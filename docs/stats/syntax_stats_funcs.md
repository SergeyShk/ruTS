# Функции вычисления статистик

Все функции работают с объектами `Token` библиотеки spaCy: функции `calc_*` принимают последовательность токенов (`Doc`, `Span` или список), функции `is_*` и `count_*` - отдельный токен. Функции дерева зависимостей взяты из ядра [anyTS](https://sergeyshk.github.io/anyTS/stats/syntax_stats_funcs/), функции русских конструкций - собственные функции ruTS. Синтаксические отношения и морфологические признаки берутся из разметки [Universal Dependencies](https://universaldependencies.org/u/dep/); подтипы отношений (`acl:relcl`, `nsubj:pass`, `nummod:gov`) учитываются по базовому отношению там, где это указано.

Определения признаков следуют работе [Иванова, Солнышкиной и Соловьёва (2018)](https://dialogue-conf.org/media/4302/ivanovvv.pdf); в скобках указаны исходные названия признаков и коэффициенты корреляции с классом учебника из этой работы.

## Дефисные слова { #hyphenated-words }

<!-- core: stats/syntax_stats_funcs.md:hyphenated_words 2598bfe -->
Токенизатор может разрезать слово по дефисам (`во-первых` на `во`, `-`, `первых`), и тогда парсер вешает каждую часть на свою вершину. С `join_hyphens=True` функции дерева считают одним словом вместе с дефисами слово, части которого склеивает `anyts.utils.joins_previous`. У слова, которое держит вершину предложения, вершины нет; вершина другого слова - вершина его части, которая висит вне слова и ближе всех к корню (при равенстве - слова, а не дефиса). Зависимые слова - слова, чья часть, висящая вне слова, висит на одном из его токенов; каждое представлено этой частью (или своей первой частью, если наружу висит дефис). Поддерево слова - само слово и слова, которые висят на нем прямо или через знаки препинания. Так у каждого слова одна зависимость, и зависит оно от одного слова.

`SyntaxStats` и функции русских конструкций всегда склеивают дефисные слова (`во-первых` - одно слово). Функции ядра, в том числе `is_predicate`, `count_noun_modifiers`, `is_passive`, `has_agent` и `is_agentless`, по умолчанию принимают `join_hyphens=False`: значения `SyntaxStats` они дают с `join_hyphens=True`.

## Длины зависимостей { #calc_dependency_distances }

!!! info ""
    **ruts.syntax_stats.calc_dependency_distances()**

<!-- core: stats/syntax_stats_funcs.md:calc_dependency_distances b2a2296 -->
Длины зависимостей (Liu 2008): расстояние между словом и его вершиной в позициях слов без учета знаков препинания, в порядке слов. Вершина предложения и слово, вершина которого лежит вне последовательности, пропускаются.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `tokens` | Doc/Span/list[Token] | `-` | Последовательность токенов |
| `join_hyphens` | bool | `False` | Считать дефисное слово одной позицией |

Класс `SyntaxStats` считает по длинам среднее (`mean_dependency_distance`), стандартное отклонение по всем зависимостям текста (`std_dependency_distance`), максимум в предложении, усредненный по предложениям с зависимостями (`max_dependency_distance`), и долю смежных связей длины 1 (`p_adjacent_dependencies`); предложения из одного слова ни в одну из статистик не входят. Средняя длина зависимости растет с длиной предложения, максимальная длина - лучший из древесных признаков на уровне отдельного предложения.

!!! example "Пример"

    ``` python
    import spacy
    from ruts.syntax_stats import calc_dependency_distances

    nlp = spacy.load("ru_core_news_sm")
    calc_dependency_distances(
        nlp("Повышение эффективности использования ресурсов предприятия обсуждалось на совещании.")
    )
    # [5, 1, 1, 1, 1, 1, 2]
    ```

## Глубина дерева { #calc_tree_depth }

!!! info ""
    **ruts.syntax_stats.calc_tree_depth()**

<!-- core: stats/syntax_stats_funcs.md:calc_tree_depth 822909b -->
Глубина дерева зависимостей: самый длинный путь от вершины предложения до листа в связях между словами; для нескольких предложений - максимум, для предложения из одного слова - 0. С `join_hyphens` дефисное слово - одно слово, а слова, которые висят на любой из его частей, - на уровень ниже него.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `tokens` | Doc/Span/list[Token] | `-` | Последовательность токенов |
| `join_hyphens` | bool | `False` | Считать дефисное слово одним словом |

Глубина - признак `LONGEST_PATH` из работы (r = 0.84); класс `SyntaxStats` усредняет ее по предложениям (`tree_depth`).

## Листья, поддеревья и ветвление { #count_children }

!!! info ""
    **ruts.syntax_stats.count_children()**

<!-- core: stats/syntax_stats_funcs.md:count_children eb744e8 -->
`count_children(token, join_hyphens=False)` считает зависимые слова токена.

Слово без зависимых - лист (`LEAVES_NUMBER`, r = 0.84), слово с зависимыми - вершина поддерева (`PATH_NUMBER`, r = 0.87). Класс `SyntaxStats` считает число листьев и поддеревьев на предложение (`leaves_per_sent`, `subtrees_per_sent`), отношение числа слов к числу листьев (`AVERAGE_PATH`, r = 0.84; `nodes_per_leaf`) и распределение слов по числу зависимых - профиль ветвления (`c_children`).

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `token` | Token | `-` | Токен |
| `join_hyphens` | bool | `False` | Считать дефисное слово одним словом |

## Валентность { #calc_valency }

!!! info ""
    **ruts.syntax_stats.calc_valency()**

<!-- core: stats/syntax_stats_funcs.md:calc_valency 8e430d0 -->
Валентность токена: число его зависимых слов без связей `cc`, `conj`, `parataxis` и `punct` (`anyts.constants.VALENCY_IGNORED_DEPS`); `calc_valency(token, join_hyphens=True)` считает дефисное зависимое один раз, поэтому у `пришел` в `Кто-то пришел` одно зависимое, а не два.

Класс `SyntaxStats` усредняет валентность по финитным формам глаголов (`VERBS_DEP`, r = 0.43; `verb_valency`), см. [`is_finite_verb`](#is_finite_verb).

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `token` | Token | `-` | Токен |
| `join_hyphens` | bool | `False` | Считать дефисное слово одним словом |

## Сочинительные цепочки { #calc_coordination_chains }

!!! info ""
    **ruts.syntax_stats.calc_coordination_chains()**

<!-- core: stats/syntax_stats_funcs.md:calc_coordination_chains e22b7f0 -->
Длины сочинительных цепочек в порядке их первых слов. Цепочка - группа слов, связанных `conj`, к какому бы слову ни присоединялся каждый однородный член: Universal Dependencies вешает каждый однородный член на первый (`груши → яблоки`, `сливы → яблоки`), ClearNLP - на предыдущий (`груши → яблоки`, `сливы → груши`); в обоих случаях `яблоки, груши и сливы` - одна цепочка из трех слов. Вложенное сочинение (`кошки и собаки, или птицы`) и перечисление, разбитое между несколькими вершинами, - тоже одна цепочка. Длина цепочки - число ее слов; однородный член, вершина которого лежит вне последовательности, с ней не связывается. С `join_hyphens` дефисное слово - один однородный член, связанный отношением `conj` любой своей части (`членом совета и вице-губернатором` - цепочка из двух слов).

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `tokens` | Doc/Span/list[Token] | `-` | Последовательность токенов |
| `join_hyphens` | bool | `False` | Считать дефисное слово одним словом |

Число цепочек на предложение (`SOCHIN_NUMBER`, r = 0.93) и их средняя длина (`AVERAGE_SOCHIN_LENGTH`, r = 0.87) - сильнейшие синтаксические предикторы сложности учебника.

## Клаузы { #is_clause_head }

!!! info ""
    **ruts.syntax_stats.is_clause_head()**, **ruts.syntax_stats.is_subordinate_clause_head()**, **ruts.syntax_stats.is_predicate()**

Проверка, является ли токен вершиной клаузы. Клаузу возглавляет вершина предложения или слово со связью `ccomp`, `advcl`, `acl`, `acl:relcl`, `csubj` или `csubj:pass`, кроме полных причастий, деепричастий и инфинитивов при существительном («желание уйти»): причастные и деепричастные обороты считаются отдельно. Вставная конструкция (`parataxis`) и однородное сказуемое (связь `conj` от вершины клаузы) образуют свою клаузу, только если могут быть сказуемым (`is_predicate`): «Он сказал: „Уходи“» и «думала, что он умен» - клаузы, а вводные слова «например», «конечно», «во-первых», на которые модели spaCy тоже вешают `parataxis`, - нет.

<!-- core: stats/syntax_stats_funcs.md:is_predicate f282b52 -->
`is_predicate(token, join_hyphens=False)` проверяет, может ли слово быть сказуемым своей клаузы: глагол (`VERB`, `AUX`) или слово с собственным подлежащим (`nsubj`, `csubj` и их подтипы, `anyts.constants.SUBJECT_DEPS`), поэтому именное сказуемое в `он высок` проходит, а вводное слово - нет.

Придаточная клауза - клауза со связью `ccomp`, `advcl`, `acl`, `acl:relcl`, `csubj` или `csubj:pass`, а также однородное сказуемое придаточной клаузы (`PODCHIN_RATE`, r = 0.64). Класс `SyntaxStats` считает клаузы и придаточные на предложение (`clauses_per_sent`, `subordinate_clauses_per_sent`), среднюю длину клаузы в словах (`mean_clause_len`) и долю предложений хотя бы с одной придаточной (`PODCHIN_NUMBER`, r = 0.62; `p_complex_sents`).

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `token` | Token | `-` | Токен |

## Модификаторы именной группы { #count_noun_modifiers }

!!! info ""
    **ruts.syntax_stats.count_noun_modifiers()**

<!-- core: stats/syntax_stats_funcs.md:count_noun_modifiers ebeb7ce -->
`count_noun_modifiers(token, join_hyphens=False)` считает модификаторы именной группы: зависимые со связями `amod`, `det`, `nmod`, `nummod`, `acl` и их подтипами (`anyts.constants.NOUN_MODIFIER_DEPS`); `conj` и `appos` модификаторами не являются.

Класс `SyntaxStats` усредняет число модификаторов по существительным и именам собственным (`NOUNS_DEP`, r = 0.88; `modifiers_per_noun`).

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `token` | Token | `-` | Токен |
| `join_hyphens` | bool | `False` | Считать дефисное слово одним словом |

## Цепочки родительных падежей { #calc_genitive_chains }

!!! info ""
    **ruts.syntax_stats.calc_genitive_chains()**, **ruts.syntax_stats.is_genitive_modifier()**, **ruts.syntax_stats.calc_modifier_chains()**

Вычисление длин цепочек родительных падежей - цепочек `calc_modifier_chains`, модификаторы которых - беспредложные определения в родительном падеже (`is_genitive_modifier`): слова со связью `nmod` в родительном падеже без зависимого предлога (`case`), «дом отца», но не «дом у дороги». Класс `SyntaxStats` считает число цепочек на предложение (`genitive_chains_per_sent`) и максимальную длину по тексту (`max_genitive_chain_len`).

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `tokens` | Doc/Span/list[Token] | `-` | Последовательность токенов |

!!! example "Пример"

    ``` python
    import spacy
    from ruts.syntax_stats import calc_genitive_chains

    nlp = spacy.load("ru_core_news_sm")
    calc_genitive_chains(nlp("Повышение эффективности использования ресурсов обсуждалось долго."))
    # [3]
    ```

### calc_modifier_chains

<!-- core: stats/syntax_stats_funcs.md:calc_modifier_chains 1efd5c8 -->
Длины цепочек вложенных модификаторов в порядке слов. Цепочка - два и более модификатора, каждый из которых висит на предыдущем, как дополнения в `повышение эффективности использования ресурсов` (длина 3); что считать модификатором (дополнение с предлогом, существительное в родительном падеже), решает проверка языка `is_modifier`. Цепочка начинается с модификатора, вершина которого модификатором не является, а ее длина - число модификаторов в самой длинной ветви. Связи - те же, что у `get_children`: знак препинания связью не является, а с `join_hyphens` дефисное слово - одно звено. Проверка, которую нельзя вызвать, дает `SourceTypeError`.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `tokens` | Doc/Span/list[Token] | `-` | Последовательность токенов |
| `is_modifier` | Callable[[Token], bool] | `-` | Является ли слово модификатором цепочки |
| `join_hyphens` | bool | `False` | Считать дефисное слово одним словом |

## Причастные и деепричастные обороты { #is_participle_clause }

!!! info ""
    **ruts.syntax_stats.is_participle_clause()**, **ruts.syntax_stats.is_converb_clause()**, **ruts.syntax_stats.subtree_len()**

Проверка, является ли токен вершиной причастного или деепричастного оборота: полное причастие ([`is_participle`](#is_finite_verb)) или деепричастие ([`is_converb`](#is_finite_verb)) хотя бы с одним зависимым словом, не считая сочинительных и вставных связей. Краткие причастия («дом построен») - сказуемые, а не определения, и оборотов не образуют. Длина оборота - число слов в поддереве вместе с самим причастием или деепричастием ([`subtree_len`](#helpers)). Класс `SyntaxStats` считает обороты на предложение (`PRICH_RATE`, r = 0.91; `DEEPRICH_RATE`, r = 0.44) и их среднюю длину (`PRICH_V`, `DEEPRICH_V`).

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `token` | Token | `-` | Токен |

## Пассив { #is_passive }

!!! info ""
    **ruts.syntax_stats.is_passive()**, **ruts.syntax_stats.has_agent()**, **ruts.syntax_stats.is_agentless()**

<!-- core: stats/syntax_stats_funcs.md:is_passive 245c390 -->
`is_passive(token, join_hyphens=False)` проверяет, является ли слово пассивной глагольной формой: глаголом с `Voice=Pass` или с зависимым `nsubj:pass`, `csubj:pass`, `aux:pass` либо `nsubjpass`, `csubjpass`, `auxpass` ClearNLP (`PASSIVE_DEPS`).

<!-- core: stats/syntax_stats_funcs.md:has_agent c8688cc -->
`has_agent(token, join_hyphens=False)` проверяет, есть ли у слова агенс: зависимое `obl:agent` или `agent` ClearNLP (`AGENT_DEPS`).

<!-- core: stats/syntax_stats_funcs.md:is_agentless e5f35a6 -->
`is_agentless(token, join_hyphens=False)` проверяет, является ли слово пассивной формой (`is_passive`) без агенса (`has_agent`).

В русском языке пассив - страдательные причастия и возвратный пассив («обсуждалось»), форма без агенса - «дом построен», но не «дом построен рабочими». Класс `SyntaxStats` считает долю пассивных форм среди всех глагольных форм (`p_passive`) и долю форм без агенса среди пассивных (`p_agentless_passive`).

## Формы глагола { #is_finite_verb }

!!! info ""
    **ruts.syntax_stats.is_finite_verb()**, **ruts.syntax_stats.is_participle()**, **ruts.syntax_stats.is_converb()**, **ruts.syntax_stats.is_infinitive()**

<!-- core: utils/spacy.md:is_finite_verb a18bc4d -->
`is_finite_verb(token)` проверяет, является ли токен финитным глаголом: часть речи `VERB` с `VerbForm=Fin`, поэтому финитный вспомогательный глагол (`AUX`) им не является.

<!-- core: utils/spacy.md:is_infinitive e246e15 -->
`is_infinitive(token)` проверяет, является ли токен инфинитивом: `VerbForm=Inf` при любой части речи.

`is_participle(token)` проверяет, является ли токен полным причастием (`VerbForm=Part` без `Variant=Short`), `is_converb(token)` - деепричастием (`VerbForm=Conv`). Класс `SyntaxStats` считает инфинитивы на предложение (`infinitives_per_sent`).

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `token` | Token | `-` | Токен |

## Отрицания { #is_negation }

!!! info ""
    **ruts.syntax_stats.is_negation()**

Проверка, является ли токен отрицательной частицей - частицей (`PART`) с признаком `Polarity=Neg` или частицей «не», «ни». Союз «ни» в конструкции «ни… ни» отрицанием не считается. Класс `SyntaxStats` считает отрицания на предложение (`NEG`, r = 0.70; `negations_per_sent`).

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `token` | Token | `-` | Токен |

## Расщепленные сказуемые { #find_split_predicates }

!!! info ""
    **ruts.syntax_stats.find_split_predicates()**, **ruts.syntax_stats.is_light_verb()**, **ruts.syntax_stats.is_reflexive()**, **ruts.syntax_stats.is_split_predicate_noun()**

Поиск расщепленных сказуемых - маркера канцелярита: легкий глагол с леммой из `LIGHT_VERBS` (осуществлять, производить, проводить, обеспечивать, оказывать, принимать, иметь и их возвратный пассив проводиться, приниматься, вестись) с именной частью - существительным с отглагольной леммой (`ruts.utils.is_verbal_noun`) или леммой из `SPLIT_PREDICATE_NOUNS` (роль, работа, помощь, мера) при глаголе своего оборота (оказать помощь, принять меры, но не получить работу): осуществлять проверку, оказать помощь, принято решение, проверка проводится. У глагола берется не больше одной именной части в порядке предпочтения `obj`, `nsubj:pass`, `nsubj` (только у возвратного или пассивного глагола, `is_reflexive`), `iobj`, `nmod`, `obl`; предложные обстоятельства и агенс пассива (`obl:agent`, творительный `obl`) не учитываются. Лемма глагола проверяется и по spaCy, и по pymorphy3 (`get_lemma`, `ruts.utils.lemmatize`). Класс `SyntaxStats` считает расщепленные сказуемые на предложение (`split_predicates_per_sent`) и хранит найденные пары в `split_predicates`; отношение существительных к глагольным формам (`noun_verb_ratio`) считается по счетчикам класса.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `tokens` | Doc/Span/list[Token] | `-` | Последовательность токенов |

## Вспомогательные функции { #helpers }

!!! info ""
    **ruts.syntax_stats.is_word()**, **ruts.syntax_stats.get_words()**, **ruts.syntax_stats.is_root()**, **ruts.syntax_stats.base_dep()**, **ruts.syntax_stats.get_children()**, **ruts.syntax_stats.subtree_len()**, **ruts.syntax_stats.has_feature()**, **ruts.syntax_stats.get_lemma()**

### is_word

<!-- core: utils/spacy.md:is_word 96b556c -->
Проверяет, является ли токен словом: не пробелом и не токеном `is_punctuation`, поэтому символы вроде `%`, `€`, `+` и невидимые знаки тоже не слова. Такие токены - слова `iter_doc_tokens` и узлы дерева зависимостей синтаксических статистик.

### get_words

<!-- core: stats/syntax_stats_funcs.md:get_words d13c538 -->
`get_words(tokens, join_hyphens=False)` возвращает слова последовательности токенов в их порядке; с `join_hyphens=True` слово, разрезанное токенизатором по дефисам, - одно слово, представленное частью, которая держит его связь, как у зависимых `get_children` (`губернатор` в `Он вице-губернатор`), или первой частью, если связь держит дефис.

### is_root

<!-- core: stats/syntax_stats_funcs.md:is_root bf00a5c -->
Проверяет, является ли токен вершиной своего предложения: его вершина - он сам.

### base_dep

<!-- core: stats/syntax_stats_funcs.md:base_dep d13b0d6 -->
Отношение токена без подтипа, который Universal Dependencies отделяет двоеточием: `nsubj:pass` дает `nsubj`, `expl:pass` - `expl`.

### get_children, subtree_len

<!-- core: stats/syntax_stats_funcs.md:get_children ed9bc9f -->
`get_children(token, join_hyphens=False)` возвращает зависимые слова токена без знаков препинания и пробелов; с `join_hyphens=True` - зависимые всего дефисного слова, к которому относится токен.

<!-- core: stats/syntax_stats_funcs.md:subtree_len ed743e0 -->
`subtree_len(token, join_hyphens=False)` - число слов в поддереве токена: сам токен и все его прямые и косвенные зависимые.

### has_feature

<!-- core: utils/spacy.md:has_feature a4a6f6c -->
Проверяет, есть ли у токена морфологический признак с заданным значением: `has_feature(token, "VerbForm", "Fin")`.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `token` | Token | `-` | Токен |
| `field` | str | `-` | Название признака |
| `value` | str | `-` | Значение признака |

### get_lemma

`get_lemma(token)` возвращает лемму токена в нижнем регистре из pymorphy3 по части речи токена.
