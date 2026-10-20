# Морфологические статистики

``` {.python .signature}
MorphStats(source, words_extractor=None)
```

Морфологические статистики текста: часть речи и грамматические признаки каждого слова в терминах [Universal Dependencies](https://universaldependencies.org/u/feat/) и их распределения. Источник данных - текст или объект `Doc` библиотеки [spaCy](https://github.com/explosion/spaCy); статистики вычисляются при создании объекта.

Класс построен на интерфейсе статистик `Stats` ядра [anyTS](https://sergeyshk.github.io/anyTS/stats/stats/). Слова строки извлекает русский [`WordsExtractor`](../extractors/words.md) или заданный экстрактор, который для `Doc` применяется к его тексту; без экстрактора слова `Doc` берутся из его токенов, а части дефисного слова, разрезанного spaCy, склеиваются.

Исключения:

- `SourceTypeError` - источник, который не строка и не `Doc`, экстрактор другого типа;
- `SourceError` - источник без слов.

=== "Код"

    ``` python
    from ruts import MorphStats

    text = "Постарайтесь получить то, что любите, иначе придется полюбить то, что получили"
    ms = MorphStats(text)
    ms.print_stats("pos", "tense", "number", "person", filter_none=True)
    ```

=== "Результат"

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

## Параметры

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `source` | `str` / `Doc` | - | Источник данных |
| `words_extractor` | `WordsExtractor` | `None` | Инструмент для извлечения слов; применяется и к `Doc`, к его тексту |

## Атрибуты

| Атрибут | Тип | Описание |
| :------ | :-- | :------- |
| `words` | `tuple[str]` | Слова |
| `lemmas` | `tuple[str]` | Леммы слов: pymorphy3 по части речи слова |
| `tags` | `tuple[str]` | Грамматические признаки слов строками в формате CoNLL-U (`Animacy=Inan|Case=Nom|Gender=Masc|Number=Sing`, `_` без признаков) |

## Статистики

Каждая статистика - атрибут объекта, кортеж значений признака по словам (`None` у слова без признака), а `get_stats` дает распределения их значений. Для объекта `Doc` с разметкой частей речи значения берутся из `token.pos_` и `token.morph`, то есть с учетом контекста (стали - глагол или существительное). Для строки, `Doc` без разметки и `Doc` с заданным экстрактором слов используется первый разбор [pymorphy3](https://github.com/no-plagiarism/pymorphy3): граммемы [OpenCorpora](http://opencorpora.org/dict.php?act=gram) переводятся в UD по таблицам `OPENCORPORA_TO_UD_POS` и `OPENCORPORA_TO_UD_GRAMMEMES` из `ruts.constants`, а признак, которому pymorphy3 дает два значения сразу (одушевленность слов на -кки), не определен.

| Статистика | Признак | Значения |
| :--------- | :------ | :------- |
| [`pos`](#pos) | Часть речи | `NOUN`, `PROPN`, `VERB`, `AUX`, `ADJ`, `DET`, `PRON`, `NUM`, `ADV`, `ADP`, `CCONJ`, `SCONJ`, `PART`, `INTJ`, `X` |
| `animacy` | Одушевленность | `Anim`, `Inan` |
| `aspect` | Вид | `Perf`, `Imp` |
| `case` | Падеж | `Nom`, `Gen`, `Dat`, `Acc`, `Ins`, `Loc`, `Par`, `Voc` |
| [`degree`](#derived) | Степень сравнения | `Pos`, `Cmp`, `Sup` |
| `gender` | Род | `Masc`, `Fem`, `Neut`, `Com` |
| [`involvement`](#opencorpora) | Совместность | `In`, `Ex` |
| `mood` | Наклонение | `Ind`, `Imp`, `Cnd` |
| `number` | Число | `Sing`, `Plur` |
| `person` | Лицо | `1`, `2`, `3` |
| [`polarity`](#derived) | Отрицание | `Neg` |
| [`style_variant`](#derived) | Краткая форма | `Short` |
| `tense` | Время | `Past`, `Pres`, `Fut` |
| [`transitivity`](#opencorpora) | Переходность | `Tran`, `Intr` |
| `verb_form` | Форма глагола | `Fin`, `Inf`, `Part`, `Conv` |
| `voice` | Залог | `Act`, `Pass`, `Mid` |

Русские названия значений для `print_stats` - `MORPHOLOGY_STATS_DESC` из `ruts.constants`. Значения для строки и для `Doc` с разметкой могут отличаться: spaCy проставляет `Voice=Act` личным формам и `Voice=Mid` возвратным глаголам, выделяет `AUX` и снимает омонимию по контексту; pymorphy3 определяет залог только у причастий и берет первый разбор.

<div class="metric-card" markdown>

### Часть речи { #pos }

`pos` · [UD](https://universaldependencies.org/u/pos/)
{ .metric-meta }

Для строки части речи OpenCorpora переводятся в UD так:

| OpenCorpora | UD | Примечание |
| :---------- | :- | :--------- |
| `NOUN` | `NOUN`, `PROPN` | имена, фамилии, отчества, топонимы и организации по пометам pymorphy3 - `PROPN`, но только у словоформ с заглавной буквы: pymorphy3 не учитывает регистр и дает помету имени обычным словам (лев, роза, мороз) |
| `ADJF`, `ADJS`, `COMP` | `ADJ`, `DET`, `PRON`, `NUM` | местоименные прилагательные (этот, мой, весь) - `DET`, «который» - `PRON`, «один» - `NUM`; компаратив без контекста считается прилагательным |
| `VERB`, `INFN`, `PRTF`, `PRTS`, `GRND` | `VERB` | форма записывается в `verb_form`: `Fin`, `Inf`, `Part`, `Conv`; вспомогательный `AUX` выделяет только spaCy |
| `NUMR`, `NUMB`, `ROMN` | `NUM` | |
| `ADVB`, `PRED` | `ADV` | предикативы (надо, нельзя) - наречия без времени, как в русских корпусах UD; у бытийных «нет» и «нету», которые UD считает глаголами, - настоящее время |
| `NPRO` | `PRON` | |
| `PREP` | `ADP` | |
| `CONJ` | `CCONJ`, `SCONJ` | подчинительные союзы по списку `SUBORDINATING_CONJUNCTIONS` (что, чтобы, если, когда, хотя, потому) |
| `PRCL` | `PART` | |
| `INTJ` | `INTJ` | |
| `LATN`, `UNKN` | `X` | |

«Есть» считается формой «быть», а не «кушать».

</div>

<div class="metric-card" markdown>

### Степень сравнения, отрицание и краткая форма { #derived }

`degree` · `polarity` · `style_variant`
{ .metric-meta }

Для строки эти признаки выводятся по правилам русского UD. Степень есть у прилагательных (кроме местоименных) и наречий: `Cmp` у сравнительной степени и у «более», «менее», «выше», «ниже», `Sup` у превосходной («красивейший»), `Pos` у остальных. Отрицание - у частиц «не», «ни» и ответного «нет» («Нет, не пойду», но не «Денег нет»). Краткая форма - у кратких прилагательных и причастий («рад», «прочитана»), но не у форм на -о вроде «неверно», «нужно», поэтому у строки она встречается реже, чем у `Doc` модели.

=== "Код"

    ``` python
    from ruts import MorphStats

    ms = MorphStats("Нет, я не рад: книга прочитана быстрее красивейшей сказки")
    ms.explain_text("degree", "polarity", "style_variant", filter_none=True)
    ```

=== "Результат"

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

### Переходность и совместность { #opencorpora }

`transitivity` · `involvement` · [OpenCorpora](http://opencorpora.org/dict.php?act=gram)
{ .metric-meta }

Признаки OpenCorpora, которых в русском UD нет: переходность (`Tran`, `Intr`) и совместность (`In` - говорящий включен в действие, `Ex` - не включен). Они считаются через pymorphy3 для глаголов (для `Doc` - по разбору с леммой spaCy) и в строке признаков `tags` записываются как `Subcat` и `Clusivity`.

=== "Код"

    ``` python
    from ruts import MorphStats

    ms = MorphStats("Постарайтесь получить то, что любите")
    ms.tags[0]
    ms.transitivity, ms.involvement
    ```

=== "Результат"

    ```
    'Aspect=Perf|Clusivity=Ex|Mood=Imp|Number=Plur|Subcat=Intr|VerbForm=Fin'
    (('Intr', 'Tran', None, None, 'Tran'), ('Ex', None, None, None, None))
    ```

</div>

<div class="metric-card" markdown>

### Формы глагола { #markers }

`get_markers()` · `print_markers()`
{ .metric-meta }

Доли грамматических форм глагола (слов с частью речи `VERB` и `AUX`), каждая от своей базы; доля с пустой базой - `nan`.

| Маркер | Доля | База |
| :----- | :--- | :--- |
| `p_indicative`, `p_imperative`, `p_conditional` | изъявительного, повелительного и сослагательного наклонения | личные формы |
| `p_infinitive`, `p_participle`, `p_converb` | инфинитивов, причастий и деепричастий | все формы глагола |
| `p_perfective` | совершенного вида | формы глагола с видом |
| `p_passive` | страдательных причастий | все формы глагола |
| `p_reflexive` | возвратных форм на -ся, -сь | все формы глагола |

Сослагательное наклонение определяется по частице «бы» («б»), поэтому экстрактор слов не должен отбрасывать частицы.

=== "Код"

    ``` python
    from ruts import MorphStats

    ms = MorphStats("Если бы я знал, я бы пришел за книгами, прочитанными вчера")
    ms.get_markers()
    ```

=== "Результат"

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

## Методы

`get_stats(*args, filter_none=False, flat=False)` возвращает распределения значений статистик справочником количеств по каждой. Статистики выбираются именами через запятую, без имен берутся все; `filter_none=True` отбрасывает слова без признака (`None`), а `flat=True` дает ключи вида `pos_NOUN` вместо вложенных справочников, тоже без слов без признака. Имя, которого нет среди статистик, дает `UnknownStatError` - здесь и в `print_stats` и `explain_text`.

`print_stats(*args, filter_none=False)` выводит распределения выбранных статистик таблицами, начиная с частых значений, а `explain_text(*args, filter_none=False)` возвращает слова текста по порядку со значениями выбранных статистик.

=== "Код"

    ``` python
    from ruts import MorphStats

    text = "Постарайтесь получить то, что любите, иначе придется полюбить то, что получили"
    ms = MorphStats(text)
    ms.get_stats("pos", "tense", "number", "person", filter_none=True)
    ms.get_stats("pos", "tense", flat=True)
    ms.explain_text("pos", "tense", "number", "person", filter_none=True)
    ```

=== "Результат"

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

<!-- core: stats/stats.md:Stats-to_dataframe fb70c9b -->
`to_dataframe()` возвращает плоские статистики, `get_stats(flat=True)`, таблицей `DataFrame` библиотеки [pandas](https://pandas.pydata.org/) из одной строки со столбцом на каждый ключ. Статистика-справочник дает столбцы только для ключей, которые есть у текста, поэтому в таблицах нескольких текстов, объединенных `pandas.concat`, количество, которого у текста нет, - `NaN`. Нулями можно заполнять только такие столбцы: в остальных `NaN` - неопределенное значение.

=== "Код"

    ``` python
    ms.to_dataframe().iloc[:, :4]
    ```

=== "Результат"

    ```
       pos_VERB  pos_CCONJ  pos_SCONJ  pos_ADV
    0         6          2          2        1
    ```

`get_markers()` возвращает [доли форм глагола](#markers) справочником, а `print_markers()` выводит их таблицей.

=== "Код"

    ``` python
    from ruts import MorphStats

    MorphStats("Если бы я знал, я бы пришел за книгами, прочитанными вчера").print_markers()
    ```

=== "Результат"

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

Метод `describe` - из [интерфейса статистик](https://sergeyshk.github.io/anyTS/stats/stats/) ядра anyTS; шкал у морфологических статистик нет, поэтому он для статистик `get_stats` возвращает `None`.
