# Подсветка текста

!!! info ""
    **ruts.visualizers.highlight()**

## Описание

Подсветка фрагментов текста, по которым считаются статистики библиотеки, в стиле сервисов [Главред](https://glvrd.ru/) и [Тургенев](https://turgenev.ashmanov.com/): длинные предложения, сложные и редкие слова, пассив, обороты, цепочки родительных падежей, расщепленные сказуемые, отглагольные существительные, производные предлоги, штампы, стоп-слова, вводные слова, коннекторы, аллитерации. Одна картинка объясняет, из чего складываются значения метрик, лучше таблицы чисел. В качестве источника данных может использоваться как непосредственно текст, так и объект класса `Doc` библиотеки [spaCy](https://github.com/explosion/spaCy).

Функция возвращает объект `HighlightedText`, который в Jupyter отображается как HTML со стилями и легендой; метод `to_html` возвращает ту же разметку для документации и веб-приложений. Фрагменты хранятся в атрибуте `highlights` и доступны для собственной отрисовки.

Слои подсветки:

| Группа | Слой | Что отмечает | Статистика |
| :----- | :--: | :----------: | :--------: |
| Читаемость | `long_sents` | Предложения с числом слов не меньше `long_sent_word_factor` | [BasicStats](../stats/basic_stats.md), [ReadabilityStats](../stats/readability_stats.md) |
| | `complex_words` | Слова с числом слогов не меньше `complex_syl_factor` | [BasicStats](../stats/basic_stats.md), [ReadabilityStats](../stats/readability_stats.md) |
| | `rare_words` | Слова с леммой вне вшитого списка топ-10000; числа, латиница, сокращения и стоп-слова не подсвечиваются | [LexicalStats](../stats/lexical_stats.md) |
| Синтаксис | `passive` | Пассивные глагольные формы вместе со вспомогательным глаголом | [SyntaxStats](../stats/syntax_stats.md) |
| | `participle_clauses` | Причастные обороты | [SyntaxStats](../stats/syntax_stats.md) |
| | `converb_clauses` | Деепричастные обороты | [SyntaxStats](../stats/syntax_stats.md) |
| | `genitive_chains` | Цепочки родительных падежей вместе с управляющим словом | [SyntaxStats](../stats/syntax_stats.md) |
| | `split_predicates` | Расщепленные сказуемые от глагола до именной части | [SyntaxStats](../stats/syntax_stats.md) |
| Канцелярит | `verbal_nouns` | Отглагольные существительные | [StyleStats](../stats/style_stats.md) |
| | `compound_prepositions` | Производные предлоги по списку `COMPOUND_PREPOSITIONS` | [StyleStats](../stats/style_stats.md) |
| | `cliches` | Штампы по списку `OFFICIALESE_CLICHES` или параметру `cliches` | [StyleStats](../stats/style_stats.md) |
| Стиль | `stopwords` | Стоп-слова по части речи или переданному списку - «вода» текста | [StyleStats](../stats/style_stats.md) |
| | `parentheticals` | Вводные слова и обороты | [StyleStats](../stats/style_stats.md) |
| | `connectors` | Коннекторы по части речи из разметки `Doc` или pymorphy3, в подсказке класс и тип | [CohesionStats](../stats/cohesion_stats.md) |
| Фоника | `alliteration` | Повторы согласной в соседних словах, маловероятные при частотах букв русского языка | [PhonStats](../stats/phon_stats.md) |

Группы заданы в `ruts.constants.HIGHLIGHT_LAYER_GROUPS`. Слои группы «Синтаксис» считаются по дереву зависимостей и доступны только для объекта `Doc` с разбором зависимостей (модели `ru_core_news_sm`, `ru_core_news_md`, `ru_core_news_lg`); слой `long_sents` для `Doc` требует границ предложений. По умолчанию включаются слои `HIGHLIGHT_DEFAULT_LAYERS` - длинные предложения, сложные слова, пассив, цепочки родительных, расщепленные сказуемые, штампы - из доступных источнику; `layers="all"` включает все доступные. Пятнадцать слоев сразу перекрывают друг друга (производный предлог состоит из стоп-слов, коннектор может быть вводным словом), поэтому выбирайте нужные.

!!! note "Примечание"
    Аллитерация ищется внутри предложения как цепочка из двух и более соседних слов, в основе каждого из которых есть одна и та же согласная буква. Основа - общая начальная часть словоформы и ее леммы по pymorphy3 (*крупных* → *крупны*, *руках* → *рука*): окончания согласуются с соседними словами и повторяют согласные по грамматике, а не по звучанию (*этих крупных*, *своим целям и нуждам*). Вероятность цепочки при независимом распределении букв - произведение по словам вероятностей встретить согласную среди букв основы, $1 - (1 - f)^n$, где $f$ - [частота согласной](https://ru.wikipedia.org/wiki/Частотность) в русских текстах, $n$ - число букв основы; цепочка подсвечивается, если вероятность ниже порога `alliteration_threshold`. На каждой позиции проверяется около двадцати согласных, поэтому порог строгий: на прозе при 0.001 подсвечено около 5% слов, при 0.01 - около 20%, в основном случайные совпадения частых букв. Повтор редкой согласной (*слышно, бесшумно шуршат камыши*) заметен в двух-трех словах, повтор частой в длинных словах ожидаем и не подсвечивается. Слова короче трех букв и слова без гласных цепочку не прерывают и не продолжают, буква *й* не учитывается, так как в именительном падеже входит в лемму прилагательного. Индекс аллитерации [PhonStats](../stats/phon_stats.md) измеряет сгруппированность повторов во всем тексте, подсветка показывает их места.

## Параметры

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `source` | str/Doc | `-` | Источник данных (строка или объект Doc) |
| `layers` | list[str]/str | `None` | Слои подсветки; если не заданы, включаются слои `HIGHLIGHT_DEFAULT_LAYERS`, доступные источнику; `"all"` - все доступные |
| `long_sent_word_factor` | int | `20` | Минимальное количество слов в длинном предложении |
| `complex_syl_factor` | int | `4` | Минимальное количество слогов в сложном слове |
| `stopwords` | list[str] | `None` | Список стоп-слов; если не задан, стоп-слова определяются по части речи с помощью pymorphy3 |
| `cliches` | list[str] | `None` | Список штампов; если не задан, используется `OFFICIALESE_CLICHES` |
| `alliteration_threshold` | float | `0.001` | Порог вероятности повтора согласной, ниже которого повтор считается аллитерацией |

## Атрибуты

| Атрибут | Тип | Описание |
| :-----: | :-: | :------: |
| `text` | str | Текст источника данных |
| `layers` | tuple[str] | Включенные слои подсветки в порядке отрисовки |
| `highlights` | tuple[Highlight] | Подсвеченные фрагменты в порядке появления в тексте |
| `counts` | dict[str, int] | Количество фрагментов каждого слоя |

Фрагмент `Highlight` - неизменяемый объект с полями `start` и `end` (позиции в тексте), `layer` (слой) и `note` (пояснение для всплывающей подсказки: число слов в предложении, слогов в слове, длина цепочки, согласная аллитерации).

## Методы

### to_html

Возвращает HTML-разметку подсвеченного текста: блок `div` с классом `ruts-highlight`, внутри легенда со счетчиками и текст, в котором подсвеченные отрезки обернуты в `span` с классами `ruts-hl` и `ruts-hl-<слой>`, пояснения выводятся в атрибут `title`. Пересекающиеся фрагменты разных слоев дают отрезки с несколькими классами. Переносы строк сохраняются как символьные ссылки, поэтому разметку можно вставлять в Markdown.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `legend` | bool | `True` | Добавлять легенду со счетчиками фрагментов |
| `css` | bool | `True` | Добавлять стили слоев |

## Пример использования

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    import spacy
    from ruts.visualizers import highlight

    # Подготовка данных
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

    # Подсветка текста слоями по умолчанию
    ht = highlight(nlp(text))
    ht.counts
    # {'long_sents': 1, 'complex_words': 26, 'passive': 4, 'genitive_chains': 2,
    #  'split_predicates': 0, 'cliches': 1}

    ht.highlights[:2]
    # (Highlight(start=8, end=22, layer='complex_words', note='сложное слово, 5 слогов'),
    #  Highlight(start=8, end=22, layer='passive', note='пассив без агенса'))

    # Все слои
    highlight(nlp(text), layers="all").counts
    # {'long_sents': 1, 'complex_words': 26, 'rare_words': 3, 'passive': 4, 'participle_clauses': 2,
    #  'converb_clauses': 1, 'genitive_chains': 2, 'split_predicates': 0, 'verbal_nouns': 10,
    #  'compound_prepositions': 0, 'cliches': 1, 'stopwords': 17, 'parentheticals': 0,
    #  'connectors': 4, 'alliteration': 1}

    # Отображение в Jupyter или сохранение разметки
    ht
    html = ht.to_html()
    ```

_Результат_ (наведите курсор на фрагмент, чтобы увидеть пояснение):

<div class="ruts-highlight"><style>.ruts-highlight { line-height: 1.7; }
.ruts-highlight-legend { display: flex; flex-wrap: wrap; gap: 0.4em 1.2em; margin-bottom: 0.8em; font-size: 0.9em; }
.ruts-highlight-legend .ruts-hl { padding: 0 0.3em; }
.ruts-highlight-count { opacity: 0.6; margin-left: 0.3em; }
.ruts-highlight-text { white-space: pre-wrap; }
.ruts-highlight .ruts-hl.ruts-hl-long_sents, .ruts-highlight .ruts-hl.ruts-hl-complex_words, .ruts-highlight .ruts-hl.ruts-hl-rare_words, .ruts-highlight .ruts-hl.ruts-hl-stopwords, .ruts-highlight .ruts-hl.ruts-hl-passive, .ruts-highlight .ruts-hl.ruts-hl-verbal_nouns, .ruts-highlight .ruts-hl.ruts-hl-compound_prepositions, .ruts-highlight .ruts-hl.ruts-hl-cliches, .ruts-highlight .ruts-hl.ruts-hl-parentheticals { color: #1f2328; border-radius: 2px; }
.ruts-hl-long_sents { background: #fef9c3; }
.ruts-hl-complex_words { background: #fed7aa; }
.ruts-hl-rare_words { background: #e5e7eb; }
.ruts-hl-passive { background: #fecaca; }
.ruts-hl-verbal_nouns { background: #e9d5ff; }
.ruts-hl-compound_prepositions { background: #a7f3d0; }
.ruts-hl-cliches { background: #fbcfe8; }
.ruts-hl-stopwords { background: #bae6fd; }
.ruts-hl-parentheticals { background: #d9f99d; }
.ruts-hl-participle_clauses { border-bottom: 2px solid #7c3aed; }
.ruts-hl-converb_clauses { border-bottom: 2px solid #0d9488; }
.ruts-hl-genitive_chains { border-bottom: 2px solid #b45309; }
.ruts-hl-split_predicates { border-bottom: 2px solid #dc2626; }
.ruts-hl-connectors { border-bottom: 2px dashed #2563eb; }
.ruts-hl-alliteration { text-decoration-line: underline; text-decoration-style: dotted; text-decoration-color: #db2777; text-decoration-thickness: 2px; text-underline-offset: 3px; }
</style><div class="ruts-highlight-legend"><span><span class="ruts-hl ruts-hl-long_sents">Длинные предложения</span><span class="ruts-highlight-count">1</span></span><span><span class="ruts-hl ruts-hl-complex_words">Сложные слова</span><span class="ruts-highlight-count">26</span></span><span><span class="ruts-hl ruts-hl-passive">Пассив</span><span class="ruts-highlight-count">4</span></span><span><span class="ruts-hl ruts-hl-genitive_chains">Цепочки родительных</span><span class="ruts-highlight-count">2</span></span><span><span class="ruts-hl ruts-hl-split_predicates">Расщеплённые сказуемые</span><span class="ruts-highlight-count">0</span></span><span><span class="ruts-hl ruts-hl-cliches">Штампы</span><span class="ruts-highlight-count">1</span></span></div><div class="ruts-highlight-text">Проект, <span class="ruts-hl ruts-hl-complex_words ruts-hl-passive" title="сложное слово, 5 слогов; пассив без агенса">подготовленный</span> за неделю, <span class="ruts-hl ruts-hl-passive" title="пассив">был одобрен</span> советом без <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 5 слогов">обсуждения</span>. <span class="ruts-hl ruts-hl-complex_words ruts-hl-genitive_chains" title="сложное слово, 5 слогов; цепочка из 3 родительных">Повышение</span><span class="ruts-hl ruts-hl-genitive_chains" title="цепочка из 3 родительных"> </span><span class="ruts-hl ruts-hl-complex_words ruts-hl-genitive_chains" title="сложное слово, 5 слогов; цепочка из 3 родительных">эффективности</span><span class="ruts-hl ruts-hl-genitive_chains" title="цепочка из 3 родительных"> </span><span class="ruts-hl ruts-hl-complex_words ruts-hl-genitive_chains" title="сложное слово, 6 слогов; цепочка из 3 родительных">использования</span><span class="ruts-hl ruts-hl-genitive_chains" title="цепочка из 3 родительных"> бюджетных средств</span> <span class="ruts-hl ruts-hl-complex_words ruts-hl-passive" title="сложное слово, 4 слога; пассив без агенса">обсуждалось</span>, не выходя за рамки <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 4 слога">регламента</span>. <span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 4 слога">Участники</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов">, </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 5 слогов">представлявшие</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 6 слогов">региональные</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 4 слога">министерства</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов">, не смогли </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 4 слога">согласовать</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 4 слога">позиции</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-cliches" title="длинное предложение, 26 слов; штамп: «по вопросам»">по вопросам</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 7 слогов">финансирования</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> и </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 6 слогов">распределения</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 5 слогов">ответственности</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> между </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 4 слога">ведомствами</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов">, поскольку каждое из них </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 5 слогов">настаивало</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> на собственной </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-genitive_chains" title="длинное предложение, 26 слов; цепочка из 2 родительных">трактовке </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words ruts-hl-genitive_chains" title="длинное предложение, 26 слов; сложное слово, 4 слога; цепочка из 2 родительных">положений</span><span class="ruts-hl ruts-hl-long_sents ruts-hl-genitive_chains" title="длинное предложение, 26 слов; цепочка из 2 родительных"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words ruts-hl-genitive_chains" title="длинное предложение, 26 слов; сложное слово, 5 слогов; цепочка из 2 родительных">соглашения</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов">.</span> Споры стихли, в <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 4 слога">кулуарах</span> шумно шептались и <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 4 слога">шушукались</span>, а <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 4 слога">решение</span> <span class="ruts-hl ruts-hl-passive" title="пассив без агенса">было </span><span class="ruts-hl ruts-hl-complex_words ruts-hl-passive" title="сложное слово, 4 слога; пассив без агенса">отложено</span> до <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 5 слогов">следующего</span> <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 5 слогов">заседания</span>.</div></div>

Подсветка по строке без модели spaCy включает все слои, кроме синтаксических: по умолчанию длинные предложения, сложные слова и штампы.

!!! example "Пример"

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
