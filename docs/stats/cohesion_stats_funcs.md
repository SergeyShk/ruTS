# Функции вычисления статистик

Функции повторов, данности и повтора признаков взяты из ядра [anyTS](https://sergeyshk.github.io/anyTS/stats/cohesion_stats_funcs/) и принимают элементы каждого предложения (леммы или значения признака глаголов) в порядке текста; признаки слов и словарь коннекторов - собственные функции ruTS, коннекторы ищет сопоставитель ядра с русскими крючками (`RussianConnectorMatcher`). В скобках указаны названия индексов [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664).

<!-- core: stats/cohesion_stats_funcs.md:cohesion-checks 47eaf98 -->
Список предложений, который является строкой, `Doc`, итератором, множеством или таблицей, дает `SourceTypeError`, как и предложение, которое не список строк (`check_words`), например список токенов spaCy. Функции повторов (`calc_overlap`, `calc_proportional_overlap`, `calc_overlaps`) принимают предложение и в виде множества; `count_given` и `calc_repetition` считают слова по порядку и множество не принимают.

## Бинарный повтор { #calc_overlap }

!!! info ""
    **ruts.cohesion_stats.calc_overlap()**

<!-- core: stats/cohesion_stats_funcs.md:calc_overlap c18fd34 -->
Бинарный повтор Coh-Metrix (CRFNO1, CRFAO1, CRFSO1 по соседним парам, CRFNOa, CRFAOa, CRFSOa по всем): доля пар предложений хотя бы с одним общим элементом; для текста короче двух предложений - `nan`. Все пары считаются, как в `calc_overlaps`, без их перебора.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `sets` | list[set[str]] | `-` | Элементы каждого предложения |
| `adjacent` | bool | `True` | Считать только соседние пары, иначе все пары |

Формула:

$$
\frac{|\{(i, j): S_i \cap S_j \neq \varnothing\}|}{|\{(i, j)\}|}
$$

где $S_i$ - множество элементов предложения $i$, пары $(i, j)$ - соседние или все.

!!! example "Пример"

    ``` python
    from ruts.cohesion_stats import calc_overlap

    sets = [{"кот", "окно"}, {"птица"}, {"птица", "кот"}, {"окно"}]
    calc_overlap(sets)
    # 0.3333333333333333
    calc_overlap(sets, adjacent=False)
    # 0.5
    ```

## Пропорциональный повтор { #calc_proportional_overlap }

!!! info ""
    **ruts.cohesion_stats.calc_proportional_overlap()**, **ruts.cohesion_stats.dice()**

<!-- core: stats/cohesion_stats_funcs.md:calc_proportional_overlap 52db9f1 -->
Пропорциональный повтор Coh-Metrix (CRFCWO1, CRFCWOa): коэффициент Дайса пары предложений, усредненный по парам; для текста короче двух предложений - `nan`. По всем парам сумма считается, как в `calc_overlaps`, без их перебора.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `sets` | list[set[str]] | `-` | Элементы каждого предложения |
| `adjacent` | bool | `True` | Считать только соседние пары, иначе все пары |

### dice

<!-- core: stats/cohesion_stats_funcs.md:dice f384eee -->
Коэффициент Дайса двух множеств:

$$
\frac{2 \times |A \cap B|}{|A| + |B|}
$$

и 0 для двух пустых множеств.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `first` | frozenset[str] | `-` | Первое множество |
| `second` | frozenset[str] | `-` | Второе множество |

## Все повторы за один расчет { #calc_overlaps }

!!! info ""
    **ruts.cohesion_stats.calc_overlaps()**, **ruts.cohesion_stats.Overlap**

<!-- core: stats/cohesion_stats_funcs.md:calc_overlaps 7f2c425 -->
Значения `calc_overlap` и `calc_proportional_overlap` по соседним и по всем парам сразу - именованный кортеж `Overlap` с полями `adjacent`, `all`, `prop_adjacent` и `prop_all`; без `proportional` последние два равны `nan`. Значения по всем парам вычисляются без перебора каждой пары: пары с общим элементом считаются по битовым маскам предложений, а сумма коэффициентов Дайса - по гистограммам длин предложений, в которых есть каждый элемент, и складывается `math.fsum`, чтобы не зависеть от порядка элементов.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `sets` | list[set[str]] | `-` | Элементы каждого предложения |
| `proportional` | bool | `True` | Вычислять и пропорциональный повтор |

Класс `CohesionStats` считает с ее помощью повторы существительных и аргументов без пропорциональных, а повторы знаменательных слов - с ними.

## Данность { #count_given }

!!! info ""
    **ruts.cohesion_stats.count_given()**

<!-- core: stats/cohesion_stats_funcs.md:count_given 1787dd3 -->
Количество данных элементов: элемент дан, если та же лемма уже встречалась раньше в любом предложении, включая текущее; первое вхождение - новое.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `sents` | list[list[str]] | `-` | Леммы каждого предложения в порядке текста |

Класс `CohesionStats` делит количество данных знаменательных слов на их общее число (`p_given`); доля местоимений `p_pronouns`, отношение местоимений к существительным `pronoun_noun_ratio` и доля указательных `p_demonstratives` считаются по счетчикам класса.

## Повтор времени и вида { #calc_repetition }

!!! info ""
    **ruts.cohesion_stats.calc_repetition()**, **ruts.cohesion_stats.dominant()**

<!-- core: stats/cohesion_stats_funcs.md:calc_repetition 113641f -->
Повтор времени и вида Coh-Metrix (SMTEMP): доля пар соседних предложений, у глаголов которых одинаковое преобладающее значение признака; пара, в которой у одного из предложений нет глагола с признаком, пропускается, а если ни одной пары не осталось, значение - `nan`.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `sents` | list[list[str]] | `-` | Значения признака глаголов каждого предложения |

Класс `CohesionStats` считает `tense_repetition`, `aspect_repetition` и их среднее `temporal_cohesion`.

### dominant

<!-- core: stats/cohesion_stats_funcs.md:dominant 85bab2d -->
Преобладающее значение: самое частое, из равно частых - первое; для пустого списка - `None`.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `values` | list[str] | `-` | Значения |

## Коннекторы { #find_connectors }

!!! info ""
    **ruts.cohesion_stats.find_connectors()**, **ruts.cohesion_stats.load_connectors()**, **ruts.cohesion_stats.RussianConnectorMatcher**, **ruts.cohesion_stats.Connector**, **ruts.cohesion_stats.connector_pos()**

<!-- core: stats/cohesion_stats_funcs.md:ConnectorMatcher cc8dc4a -->
`ConnectorMatcher(connectors)` находит коннекторы словаря (дискурсивные маркеры: *потому что*, *однако*, *с другой стороны*) в предложениях текста. Словарь задает класс каждого коннектора - причинный, противительный, уступительный, временной, аддитивный, условный или переформулирующий (`CONNECTOR_CLASSES`) - и его тип, первичный или вторичный (`CONNECTOR_KINDS`). Коннектор сопоставляется по нормализованным формам его слов: в каждой позиции берется самый длинный, найденные не пересекаются; точку и дефис внутри коннектора токенизатор может отделить (*т.е.* - `т`, `е`). Вхождение - `Connector`: номер предложения `sent`, позиции его слов `start` и `end`, коннектор `text` в написании словаря, его класс `cls` и тип `kind`.

Словарь, который не отображение словосочетания в пару строк, дает `SourceTypeError`, неизвестный класс или тип - `ParameterError`.

ruTS ищет коннекторы сопоставителем `RussianConnectorMatcher` - подклассом `ConnectorMatcher` ядра: слова и коннекторы сравниваются в нижнем регистре без буквы ё и знаков ударения (`normalize_yo`), однословному коннектору подходит часть речи из `CONNECTOR_POS` (`CCONJ`, `SCONJ`, `PART`, `ADV`, `ADP`, `INTJ`, `X`) или из `CONNECTOR_POS_EXTRA` для его формы (словом - `NOUN`, главное - `ADJ`, `NOUN`, допустим - `VERB`, точнее - `ADJ`, т.е. - `PUNCT`). Контекстные правила ядра - списки `ruts.constants`: слова после коннектора (`CONNECTOR_BLOCKED_AFTER`: *пока что*, *хоть бы*) и перед ним (`CONNECTOR_BLOCKED_BEFORE`: *ещё раз*, *и так далее*), с которыми он не коннектор, коннекторы, которые внутри предложения засчитываются только после отдельных слов (`CONNECTOR_ONLY_AFTER`: *и отсюда*) и не засчитываются в его начале (`CONNECTOR_NOT_AT_START`: вопросительное *отчего*), части речи слова после коннектора, с которыми он предлог или член предложения (`CONNECTOR_BLOCKED_AFTER_POS`: *после обеда*, *едва заметный*). Словарь `load_connectors()` читает `ruts/resources/connectors.tsv` - 317 коннекторов с классом из `CONNECTOR_CLASSES` и типом из `CONNECTOR_TYPES` модуля `ruts.constants`, составленных по классификации Криони, Никина и Филипповой (2008) со сверкой по списку маркеров [Ru-RSTreebank](https://rstreebank.ru/markersFull), базе [Рускон](https://ruslinkers.github.io/) и списку причинных маркеров Тольдовой и др. (2018). Однословные «и», «а», «но» входят в словарь, как в Coh-Metrix и TAACO; «что» и «как» коннекторами не считаются.

`find_connectors(words, connectors, sent_index, pos)` ищет коннекторы в предложении методом `find` сопоставителя `RussianConnectorMatcher` по словарю `connectors` (класс и тип по коннектору), по умолчанию - по словарю `load_connectors`:

<!-- core: stats/cohesion_stats_funcs.md:ConnectorMatcher-find 9315c84 -->
`find(words, sent_index, pos)` возвращает вхождения коннекторов в предложении в порядке слов. Слова - слова одного предложения без знаков препинания, первое из них - его начало. С частями речи однословный коннектор засчитывается только при части речи из `pos_tags` или из `pos_extra` для его формы, никогда - после части речи из `not_after_pos`, а с частью речи из `start_only_pos` - только в начале предложения; слово без части речи (`None`) проходит. Без частей речи правила, которые их читают, пропускаются.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `words` | list[str] | `-` | Слова предложения |
| `sent_index` | int | `0` | Номер предложения для записи во вхождения |
| `pos` | list[str] | `None` | Части речи слов |

Слова, которые не список строк, и части речи, которые не список строк и `None` (теги `token.pos_` spaCy, а не числа `token.pos`), дают `SourceTypeError`; номер предложения, который не целое число, и частей речи не столько, сколько слов, - `ParameterError`.

Класс `CohesionStats` передает части речи из разметки `Doc`, а для строки и `Doc` без разметки - части речи `connector_pos(word)`: первый разбор pymorphy3 с частью речи, подходящей коннектору (`CONNECTOR_POS` или `CONNECTOR_POS_EXTRA` для этого слова), иначе первый разбор. По вхождениям класс считает плотность коннекторов на 1000 слов - общую, по классам и по типам.

!!! example "Пример"

    ``` python
    from ruts.cohesion_stats import find_connectors

    find_connectors(["Затем", "иными", "словами", "он", "уснул"])
    # [Connector(sent=0, start=0, end=1, text='затем', cls='temporal', kind='primary'),
    #  Connector(sent=0, start=1, end=3, text='иными словами', cls='reformulative', kind='secondary')]
    find_connectors(["Раз", "он", "пришел"])
    # [Connector(sent=0, start=0, end=1, text='раз', cls='conditional', kind='primary')]
    find_connectors(["Раз", "он", "пришел"], pos=["NOUN", "PRON", "VERB"])
    # []
    ```

## Признаки слова { #word_info }

!!! info ""
    **ruts.cohesion_stats.word_info()**, **ruts.cohesion_stats.words_info()**, **ruts.cohesion_stats.token_info()**, **ruts.cohesion_stats.ud_info()**, **ruts.cohesion_stats.unit_info()**, **ruts.cohesion_stats.WordInfo**

Получение признаков слова для статистик связности - именованного кортежа `WordInfo`: `lemma`, `noun`, `pronoun`, `demonstrative`, `argument`, `content`, `tense` и `aspect` в значениях из таблицы на [странице класса](cohesion_stats.md). `word_info` берет их из первого разбора pymorphy3; `words_info` - так же для слов предложений текста, где ответное «нет» (Нет, не видел) - частица без времени. `token_info` берет их из разметки spaCy (`token.pos_`, `Tense`, `Aspect`), `ud_info` - из заданных части речи, времени и вида UD; лемма берется из разбора pymorphy3 с этой частью речи (`ruts.utils.lemmatize`), а не из `token.lemma_`. `unit_info` дает признаки слова по его токенам: отдельного токена - по `token_info`, дефисного слова из нескольких токенов (жили-были, назовите-ка) - по разбору pymorphy3 склеенного текста, переведенному в UD (`word_to_ud`).

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `word` | str | `-` | Слово (`word_info`, `ud_info`) |
| `sents` | list[list[str]] | `-` | Слова предложений текста (`words_info`) |
| `text` | str | `-` | Текст, из которого извлечены слова (`words_info`) |
| `token` | Token | `-` | Токен spaCy (`token_info`) |
| `pos`, `tense`, `aspect` | str | `-` | Часть речи, время и вид UD (`ud_info`) |
| `unit` | list[Token] | `-` | Токены слова (`unit_info`) |

!!! example "Пример"

    ``` python
    from ruts.cohesion_stats import word_info

    word_info("смотрел")
    # WordInfo(lemma='смотреть', noun=False, pronoun=False, demonstrative=False, argument=False, content=True, tense='past', aspect='impf')
    ```

## Слова Doc { #split_doc_units }

!!! info ""
    **ruts.cohesion_stats.split_doc_units()**, **ruts.cohesion_stats.unit_text()**, **ruts.cohesion_stats.unit_pos()**

<!-- core: utils/spacy.md:split_doc_units e7ebc45 -->
Разбивает слова `Doc` или `Span` по предложениям экстрактора предложений - для `Doc` без границ предложений или для того, который нужно разбить иначе: предложения находятся в его тексте по порядку, а слово `iter_doc_units` относится к предложению, в котором лежит его первый токен. Слова вне найденных предложений, отброшенных экстрактором, не учитываются, поэтому если ни одного предложения не найдено, слов нет.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `source` | Doc/Span | `-` | Объект Doc или Span |
| `sents_extractor` | SentsExtractor | `-` | Инструмент для извлечения предложений |
| `join_hyphens` | bool | `False` | Склеивать части дефисных слов |

Класс `CohesionStats` склеивает части дефисных слов (`во-первых` - одно слово), а функция - только с `join_hyphens=True`. `unit_text(unit)` дает текст слова по его токенам без метки порядка байтов, знаков ударения и мягких переносов (`ruts.utils.strip_marks`), `unit_pos(unit)` - его часть речи UD: для отдельного токена - часть речи токена, для дефисного слова из нескольких токенов - часть речи `connector_pos` склеенного текста.

!!! example "Пример"

    ``` python
    import spacy
    from ruts import SentsExtractor
    from ruts.cohesion_stats import split_doc_units, unit_text

    doc = spacy.blank("ru")("Жили-были дед да баба. Во-первых, кот спит.")
    units = split_doc_units(doc, SentsExtractor())
    [[unit_text(unit) for unit in sent] for sent in units]
    # [['Жили', 'были', 'дед', 'да', 'баба'], ['Во', 'первых', 'кот', 'спит']]
    units = split_doc_units(doc, SentsExtractor(), join_hyphens=True)
    [[unit_text(unit) for unit in sent] for sent in units]
    # [['Жили-были', 'дед', 'да', 'баба'], ['Во-первых', 'кот', 'спит']]
    ```

## Местоимение { #is_pronoun }

!!! info ""
    **ruts.cohesion_stats.is_pronoun()**

Проверка, является ли слово местоимением: `NPRO` (он, себя, кто) или `Apro` (этот, который, мой, весь) по разметке pymorphy3.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `word` | str | `-` | Слово |

## Знаменательное слово { #is_content_word }

!!! info ""
    **ruts.cohesion_stats.is_content_word()**

Проверка, является ли слово знаменательным: часть речи из `CONTENT_POS` (существительные, прилагательные, глаголы во всех формах, наречия) без граммем `STOPWORD_GRAMMEMES` (местоименные и вводные слова).

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `word` | str | `-` | Слово |
