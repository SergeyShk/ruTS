# Морфологические статистики

``` {.python .signature}
MorphStats(source, words_extractor=None)
```

<!-- core: stats/morph_stats.md:MorphStats 002c663 -->
Морфологические статистики текста: часть речи и признаки [Universal Dependencies](https://universaldependencies.org/u/feat/) каждого слова, посчитанные по значениям или данные по словам. По умолчанию источник данных - объект `Doc` библиотеки [spaCy](https://github.com/explosion/spaCy) с частями речи, которые читаются по `token.pos_` и `token.morph`; строку или `Doc` без них языковая библиотека читает по-своему.

Исключения:

- `SourceTypeError` - источник, который не `Doc`, `analyze`, который дает не объекты `MorphWord`;
- `SourceError` - источник без частей речи или без слов.

В ruTS источник данных - текст или `Doc` с разметкой частей речи или без нее, а статистики вычисляются при создании объекта. `SourceTypeError` дают источник, который не строка и не `Doc`, и экстрактор другого типа, а `SourceError` - только источник без слов.

Класс расширяет `MorphStats` ядра [anyTS](https://sergeyshk.github.io/anyTS/stats/morph_stats/) русским разбором слов и [маркерами форм глагола](#markers). Слова строки извлекает русский [`WordsExtractor`](../extractors/words.md) или заданный экстрактор, который для `Doc` применяется к его тексту; без экстрактора слова `Doc` берутся из его токенов, а части дефисного слова, разрезанного spaCy, склеиваются. Таблицы `print_stats` и `print_markers` и сообщения об ошибках - по-русски (`MORPHOLOGY_STATS_DESC`, `MORPHOLOGY_MARKERS_DESC` и `CORE_MESSAGES` из `ruts.constants`).

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

<!-- core: stats/morph_stats.md:MorphStats-attributes d3e609d -->
| Атрибут | Тип | Описание |
| :------ | :-- | :------- |
| `words` | `tuple[str]` | Слова текста |
| `tags` | `tuple[str]` | Признаки каждого слова в формате CoNLL-U (`Case=Nom|Number=Plur`), `_` у слова без них |
| `pos` | `tuple[str / None]` | Часть речи каждого слова |
| `animacy`, `aspect`, ..., `voice` | `tuple[str / None]` | Значение статистики у каждого слова, `None` у слова без признака |

В ruTS есть и атрибут `lemmas` (`tuple[str]`) - леммы слов, которые pymorphy3 дает по части речи слова.

## Статистики

Статистики - часть речи `pos` и признаки из таблицы ниже (`MORPHOLOGY_FEATURES` из `ruts.constants`). Для объекта `Doc` с разметкой частей речи значения берутся из `token.pos_` и `token.morph`, то есть с учетом контекста (стали - глагол или существительное). Для строки, `Doc` без разметки и `Doc` с заданным экстрактором слов используется первый разбор [pymorphy3](https://github.com/no-plagiarism/pymorphy3): граммемы [OpenCorpora](http://opencorpora.org/dict.php?act=gram) переводятся в UD по таблицам `OPENCORPORA_TO_UD_POS` и `OPENCORPORA_TO_UD_GRAMMEMES` из `ruts.constants`, а признак, которому pymorphy3 дает два значения сразу (одушевленность слов на -кки), не определен.

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

Значения для строки и для `Doc` с разметкой могут отличаться: spaCy проставляет `Voice=Act` личным формам и `Voice=Mid` возвратным глаголам, выделяет `AUX` и снимает омонимию по контексту; pymorphy3 определяет залог только у причастий и берет первый разбор.

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

<!-- core: stats/morph_stats.md:MorphStats-get_stats 31a94da -->
`get_stats(*stats, filter_none=False, flat=False)` дает количество слов по значениям каждой выбранной статистики, по умолчанию всех, в порядке первых появлений; `None` считает слова без признака, а `filter_none` их отбрасывает. С `flat` ключи - `статистика_значение`, например `pos_NOUN`, без слов без признака, как в `to_dataframe`. Неизвестная статистика дает `UnknownStatError`.

<!-- core: stats/morph_stats.md:MorphStats-explain_text 037565e -->
`explain_text(*stats, filter_none=False)` дает каждое слово со значениями выбранных статистик; `filter_none` отбрасывает те, которых у слова нет. Неизвестная статистика дает `UnknownStatError`.

<!-- core: stats/morph_stats.md:MorphStats-print_stats a935578 -->
`print_stats(*stats, filter_none=False)` выводит таблицу для каждой выбранной статистики: описания ее значений, начиная с самого частого, с количеством слов. Значение из нескольких соединяет описания своих частей косой чертой. Неизвестная статистика дает `UnknownStatError`.

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

<!-- core: stats/morph_stats.md:MorphStats-markers a7e33d7 -->
`get_markers()` дает маркеры языка, вычисленные по признакам, - доли грамматических форм, каждая от своей базы, - по именам `markers_desc`, а `print_markers()` выводит их с описаниями. Маркеры вычисляет библиотека; по умолчанию их нет.

В ruTS маркеры - [доли форм глагола](#markers).

=== "Код"

    ``` python
    from ruts import MorphStats

    MorphStats("Если бы я знал, я бы пришел за книгами, прочитанными вчера").print_markers()
    ```

=== "Результат"

    ```
                        Маркер                     | Значение
    ----------------------------------------------------------
    Изъявительное наклонение среди личных форм     |   0.00
    Повелительное наклонение среди личных форм     |   0.00
    Сослагательное наклонение среди личных форм    |   1.00
    Инфинитив среди форм глагола                   |   0.00
    Причастие среди форм глагола                   |   0.33
    Деепричастие среди форм глагола                |   0.00
    Совершенный вид среди форм глагола с видом     |   0.67
    Страдательные причастия среди форм глагола     |   0.33
    Возвратные формы (-ся, -сь) среди форм глагола |   0.00
    ```

Метод `describe` - из [интерфейса статистик](https://sergeyshk.github.io/anyTS/stats/stats/) ядра anyTS; шкал у морфологических статистик нет, поэтому он для статистик `get_stats` возвращает `None`.

<!-- core: stats/morph_stats.md:MorphWord 7a841ee -->
`MorphWord` - слово `analyze`: его текст `word`, часть речи `pos` (`None`, если она неизвестна) и признаки `features` - значения признаков Universal Dependencies по их названиям (`{"Case": "Nom"}`), значение из нескольких - через запятую.

В ruTS `MorphWord` импортируется и из `ruts.morph_stats`.
