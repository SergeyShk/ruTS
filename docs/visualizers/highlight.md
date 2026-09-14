# Подсветка текста

!!! info ""
    **ruts.visualizers.highlight()**

## Описание

Подсветка фрагментов текста, по которым считаются статистики библиотеки, в стиле сервисов [Главред](https://glvrd.ru/) и [Тургенев](https://turgenev.ashmanov.com/): длинные предложения, сложные слова, стоп-слова, пассив, причастные и деепричастные обороты, цепочки родительных падежей, аллитерации. Одна картинка объясняет, из чего складываются значения метрик, лучше таблицы чисел. В качестве источника данных может использоваться как непосредственно текст, так и объект класса `Doc` библиотеки [spaCy](https://github.com/explosion/spaCy).

Функция возвращает объект `HighlightedText`, который в Jupyter отображается как HTML со стилями и легендой; метод `to_html` возвращает ту же разметку для документации и веб-приложений. Фрагменты хранятся в атрибуте `highlights` и доступны для собственной отрисовки.

Слои подсветки:

| Слой | Что отмечает | Статистика |
| :--: | :----------: | :--------: |
| `long_sents` | Предложения с числом слов не меньше `long_sent_word_factor` | [BasicStats](../stats/basic_stats.md), [ReadabilityStats](../stats/readability_stats.md) |
| `complex_words` | Слова с числом слогов не меньше `complex_syl_factor` | [BasicStats](../stats/basic_stats.md), [ReadabilityStats](../stats/readability_stats.md) |
| `stopwords` | Стоп-слова по части речи или переданному списку - «вода» текста | [StyleStats](../stats/style_stats.md) |
| `passive` | Пассивные глагольные формы вместе со вспомогательным глаголом | [SyntaxStats](../stats/syntax_stats.md) |
| `participle_clauses` | Причастные обороты | [SyntaxStats](../stats/syntax_stats.md) |
| `converb_clauses` | Деепричастные обороты | [SyntaxStats](../stats/syntax_stats.md) |
| `genitive_chains` | Цепочки родительных падежей вместе с управляющим словом | [SyntaxStats](../stats/syntax_stats.md) |
| `alliteration` | Повторы согласной в соседних словах, маловероятные при частотах букв русского языка | [PhonStats](../stats/phon_stats.md) |

Слои `passive`, `participle_clauses`, `converb_clauses` и `genitive_chains` считаются по дереву зависимостей и доступны только для объекта `Doc` с разбором зависимостей (модели `ru_core_news_sm`, `ru_core_news_md`, `ru_core_news_lg`); слой `long_sents` для `Doc` требует границ предложений. По умолчанию включаются все слои, доступные источнику.

!!! note "Примечание"
    Аллитерация ищется внутри предложения как цепочка из двух и более соседних слов, в основе каждого из которых есть одна и та же согласная буква. Основа - общая начальная часть словоформы и ее леммы по pymorphy3 (*крупных* → *крупны*, *руках* → *рука*): окончания согласуются с соседними словами и повторяют согласные по грамматике, а не по звучанию (*этих крупных*, *своим целям и нуждам*). Вероятность цепочки при независимом распределении букв - произведение по словам вероятностей встретить согласную среди букв основы, $1 - (1 - f)^n$, где $f$ - [частота согласной](https://ru.wikipedia.org/wiki/Частотность) в русских текстах, $n$ - число букв основы; цепочка подсвечивается, если вероятность ниже порога `alliteration_threshold`. На каждой позиции проверяется около двадцати согласных, поэтому порог строгий: на прозе при 0.001 подсвечено около 5% слов, при 0.01 - около 20%, в основном случайные совпадения частых букв. Повтор редкой согласной (*слышно, бесшумно шуршат камыши*) заметен в двух-трех словах, повтор частой в длинных словах ожидаем и не подсвечивается. Слова короче трех букв и слова без гласных цепочку не прерывают и не продолжают, буква *й* не учитывается, так как в именительном падеже входит в лемму прилагательного. Индекс аллитерации [PhonStats](../stats/phon_stats.md) измеряет сгруппированность повторов во всем тексте, подсветка показывает их места.

## Параметры

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `source` | str/Doc | `-` | Источник данных (строка или объект Doc) |
| `layers` | list[str] | `None` | Слои подсветки; если не заданы, включаются все доступные источнику |
| `long_sent_word_factor` | int | `20` | Минимальное количество слов в длинном предложении |
| `complex_syl_factor` | int | `4` | Минимальное количество слогов в сложном слове |
| `stopwords` | list[str] | `None` | Список стоп-слов; если не задан, стоп-слова определяются по части речи с помощью pymorphy3 |
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

    # Подсветка текста
    ht = highlight(nlp(text))
    ht.counts
    # {'long_sents': 1, 'complex_words': 26, 'stopwords': 17, 'passive': 4, 'participle_clauses': 2,
    #  'converb_clauses': 1, 'genitive_chains': 2, 'alliteration': 1}

    ht.highlights[:2]
    # (Highlight(start=8, end=32, layer='participle_clauses', note='причастный оборот, 3 слова'),
    #  Highlight(start=8, end=22, layer='complex_words', note='сложное слово, 5 слогов'))

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
.ruts-hl-long_sents, .ruts-hl-complex_words, .ruts-hl-stopwords, .ruts-hl-passive { color: #1f2328; border-radius: 2px; }
.ruts-hl-long_sents { background: #fef9c3; }
.ruts-hl-complex_words { background: #fed7aa; }
.ruts-hl-stopwords { background: #bae6fd; }
.ruts-hl-passive { background: #fecaca; }
.ruts-hl-participle_clauses { border-bottom: 2px solid #7c3aed; }
.ruts-hl-converb_clauses { border-bottom: 2px solid #0d9488; }
.ruts-hl-genitive_chains { border-bottom: 2px solid #b45309; }
.ruts-hl-alliteration { text-decoration-line: underline; text-decoration-style: dotted; text-decoration-color: #db2777; text-decoration-thickness: 2px; text-underline-offset: 3px; }
</style><div class="ruts-highlight-legend"><span><span class="ruts-hl ruts-hl-long_sents">Длинные предложения</span><span class="ruts-highlight-count">1</span></span><span><span class="ruts-hl ruts-hl-complex_words">Сложные слова</span><span class="ruts-highlight-count">26</span></span><span><span class="ruts-hl ruts-hl-stopwords">Стоп-слова</span><span class="ruts-highlight-count">17</span></span><span><span class="ruts-hl ruts-hl-passive">Пассив</span><span class="ruts-highlight-count">4</span></span><span><span class="ruts-hl ruts-hl-participle_clauses">Причастные обороты</span><span class="ruts-highlight-count">2</span></span><span><span class="ruts-hl ruts-hl-converb_clauses">Деепричастные обороты</span><span class="ruts-highlight-count">1</span></span><span><span class="ruts-hl ruts-hl-genitive_chains">Цепочки родительных</span><span class="ruts-highlight-count">2</span></span><span><span class="ruts-hl ruts-hl-alliteration">Аллитерация</span><span class="ruts-highlight-count">1</span></span></div><div class="ruts-highlight-text">Проект, <span class="ruts-hl ruts-hl-complex_words ruts-hl-passive ruts-hl-participle_clauses" title="сложное слово, 5 слогов; пассив без агенса; причастный оборот, 3 слова">подготовленный</span><span class="ruts-hl ruts-hl-participle_clauses" title="причастный оборот, 3 слова"> </span><span class="ruts-hl ruts-hl-stopwords ruts-hl-participle_clauses" title="стоп-слово; причастный оборот, 3 слова">за</span><span class="ruts-hl ruts-hl-participle_clauses" title="причастный оборот, 3 слова"> неделю</span>, <span class="ruts-hl ruts-hl-passive" title="пассив">был одобрен</span> советом <span class="ruts-hl ruts-hl-stopwords" title="стоп-слово">без</span> <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 5 слогов">обсуждения</span>. <span class="ruts-hl ruts-hl-complex_words ruts-hl-genitive_chains" title="сложное слово, 5 слогов; цепочка из 3 родительных">Повышение</span><span class="ruts-hl ruts-hl-genitive_chains" title="цепочка из 3 родительных"> </span><span class="ruts-hl ruts-hl-complex_words ruts-hl-genitive_chains" title="сложное слово, 5 слогов; цепочка из 3 родительных">эффективности</span><span class="ruts-hl ruts-hl-genitive_chains" title="цепочка из 3 родительных"> </span><span class="ruts-hl ruts-hl-complex_words ruts-hl-genitive_chains" title="сложное слово, 6 слогов; цепочка из 3 родительных">использования</span><span class="ruts-hl ruts-hl-genitive_chains" title="цепочка из 3 родительных"> бюджетных средств</span> <span class="ruts-hl ruts-hl-complex_words ruts-hl-passive" title="сложное слово, 4 слога; пассив без агенса">обсуждалось</span>, <span class="ruts-hl ruts-hl-stopwords ruts-hl-converb_clauses" title="стоп-слово; деепричастный оборот, 5 слов">не</span><span class="ruts-hl ruts-hl-converb_clauses" title="деепричастный оборот, 5 слов"> выходя </span><span class="ruts-hl ruts-hl-stopwords ruts-hl-converb_clauses" title="стоп-слово; деепричастный оборот, 5 слов">за</span><span class="ruts-hl ruts-hl-converb_clauses" title="деепричастный оборот, 5 слов"> рамки </span><span class="ruts-hl ruts-hl-complex_words ruts-hl-converb_clauses" title="сложное слово, 4 слога; деепричастный оборот, 5 слов">регламента</span>. <span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 4 слога">Участники</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов">, </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words ruts-hl-participle_clauses" title="длинное предложение, 26 слов; сложное слово, 5 слогов; причастный оборот, 3 слова">представлявшие</span><span class="ruts-hl ruts-hl-long_sents ruts-hl-participle_clauses" title="длинное предложение, 26 слов; причастный оборот, 3 слова"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words ruts-hl-participle_clauses" title="длинное предложение, 26 слов; сложное слово, 6 слогов; причастный оборот, 3 слова">региональные</span><span class="ruts-hl ruts-hl-long_sents ruts-hl-participle_clauses" title="длинное предложение, 26 слов; причастный оборот, 3 слова"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words ruts-hl-participle_clauses" title="длинное предложение, 26 слов; сложное слово, 4 слога; причастный оборот, 3 слова">министерства</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов">, </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-stopwords" title="длинное предложение, 26 слов; стоп-слово">не</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> смогли </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 4 слога">согласовать</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 4 слога">позиции</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-stopwords" title="длинное предложение, 26 слов; стоп-слово">по</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> вопросам </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 7 слогов">финансирования</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-stopwords" title="длинное предложение, 26 слов; стоп-слово">и</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 6 слогов">распределения</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 5 слогов">ответственности</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-stopwords" title="длинное предложение, 26 слов; стоп-слово">между</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 4 слога">ведомствами</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов">, </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-stopwords" title="длинное предложение, 26 слов; стоп-слово">поскольку</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-stopwords" title="длинное предложение, 26 слов; стоп-слово">каждое</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-stopwords" title="длинное предложение, 26 слов; стоп-слово">из</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-stopwords" title="длинное предложение, 26 слов; стоп-слово">них</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words" title="длинное предложение, 26 слов; сложное слово, 5 слогов">настаивало</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-stopwords" title="длинное предложение, 26 слов; стоп-слово">на</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов"> собственной </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-genitive_chains" title="длинное предложение, 26 слов; цепочка из 2 родительных">трактовке </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words ruts-hl-genitive_chains" title="длинное предложение, 26 слов; сложное слово, 4 слога; цепочка из 2 родительных">положений</span><span class="ruts-hl ruts-hl-long_sents ruts-hl-genitive_chains" title="длинное предложение, 26 слов; цепочка из 2 родительных"> </span><span class="ruts-hl ruts-hl-long_sents ruts-hl-complex_words ruts-hl-genitive_chains" title="длинное предложение, 26 слов; сложное слово, 5 слогов; цепочка из 2 родительных">соглашения</span><span class="ruts-hl ruts-hl-long_sents" title="длинное предложение, 26 слов">.</span> Споры стихли, <span class="ruts-hl ruts-hl-stopwords" title="стоп-слово">в</span> <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 4 слога">кулуарах</span> <span class="ruts-hl ruts-hl-alliteration" title="аллитерация на «ш»">шумно шептались </span><span class="ruts-hl ruts-hl-stopwords ruts-hl-alliteration" title="стоп-слово; аллитерация на «ш»">и</span><span class="ruts-hl ruts-hl-alliteration" title="аллитерация на «ш»"> </span><span class="ruts-hl ruts-hl-complex_words ruts-hl-alliteration" title="сложное слово, 4 слога; аллитерация на «ш»">шушукались</span><span class="ruts-hl ruts-hl-alliteration" title="аллитерация на «ш»">, </span><span class="ruts-hl ruts-hl-stopwords ruts-hl-alliteration" title="стоп-слово; аллитерация на «ш»">а</span><span class="ruts-hl ruts-hl-alliteration" title="аллитерация на «ш»"> </span><span class="ruts-hl ruts-hl-complex_words ruts-hl-alliteration" title="сложное слово, 4 слога; аллитерация на «ш»">решение</span> <span class="ruts-hl ruts-hl-passive" title="пассив без агенса">было </span><span class="ruts-hl ruts-hl-complex_words ruts-hl-passive" title="сложное слово, 4 слога; пассив без агенса">отложено</span> <span class="ruts-hl ruts-hl-stopwords" title="стоп-слово">до</span> <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 5 слогов">следующего</span> <span class="ruts-hl ruts-hl-complex_words" title="сложное слово, 5 слогов">заседания</span>.</div></div>

Подсветка по строке без модели spaCy включает четыре слоя: длинные предложения, сложные слова, стоп-слова и аллитерации.

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
