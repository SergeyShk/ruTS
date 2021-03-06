# Морфологические статистики

!!! info ""
    **ruts.morph_stats.MorphStats**

## Описание

Модуль для вычисления морфологических статистик текста. В качестве источника данных может использоваться как непосредственно текст, так и объект класса `Doc` библиотеки [spaCy](https://github.com/explosion/spaCy).

В модуле реализована возможность использования предварительно созданного объекта класса [`WordsExtractor`](../extractors/words.md) для проведения необходимой токенизации слов перед вычислением статистик.

Для морфологического разбора текста используется библиотека [pymorphy2](https://github.com/kmike/pymorphy2). Описание статистик взяты из корпуса [OpenCorpora](http://opencorpora.org/dict.php?act=gram).

!!! note "Примечание"
    Вычисление статистик происходит в момент инициализации объекта класса `MorphStats`.

## Параметры

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `source` | str/Doc | `-` | Источник данных (строка или объект Doc) |
| `words_extractor` | WordsExtractor | `None` | Инструмент для извлечения слов |

## Атрибуты

| Атрибут | Тип | Описание |
| :-----: | :-: | :------: |
| `words` | tuple[str] | Кортеж извлеченных слов |
| `tags` | tuple[str] | Кортеж извлеченных тэгов OpenCorpora |
| `pos` | tuple[str] | Кортеж значений части речи |
| `animacy` | tuple[str] | Кортеж значений одушевленности |
| `aspect` | tuple[str] | Кортеж значений вида |
| `case` | tuple[str] | Кортеж значений падежа |
| `gender` | tuple[str] | Кортеж значений пола |
| `involvement` | tuple[str] | Кортеж значений совместности |
| `mood` | tuple[str] | Кортеж значений наклонения |
| `number` | tuple[str] | Кортеж значений числа |
| `person` | tuple[str] | Кортеж значений лица |
| `tense` | tuple[str] | Кортеж значений времени |
| `transitivity` | tuple[str] | Кортеж значений переходности |
| `voice` | tuple[str] | Кортеж значений залога |

## Методы

### get_stats

Возвращает справочник с вычисленными морфологическими статистиками.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `args` | tuple[str] | `-` | Перечень выбранных статистик |
| `filter_none` | bool | `False` | Фильтровать пустые значения |

!!! warning "Предупреждение"
    Для выбора необходимых статистик их наименования необходимо передавать в метод непосредственно через запятую.

Рассмотрим пример вычисления морфологических статистик, выбрав только часть речи, время, число и лицо, а также используя фильтрацию пустых значений:

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    from ruts import MorphStats

    # Подготовка данных
    text = "Постарайтесь получить то, что любите, иначе придется полюбить то, что получили"

    # Вычисление статистик
    ms = MorphStats(text)
    ms.get_stats(
        'pos', 'tense', 'number', 'person',
        filter_none=True
    )
    ```

    _Результат_:

    ``` bash
    {'number': {'plur': 3, 'sing': 1},
    'person': {'2per': 1, '3per': 1},
    'pos': {'ADVB': 1, 'CONJ': 4, 'INFN': 2, 'VERB': 4},
    'tense': {'futr': 1, 'past': 1, 'pres': 1}}
    ```

### print_stats

Выводит на экран таблицу с вычисленными морфологическими статистиками.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `args` | tuple[str] | `-` | Перечень выбранных статистик |
| `filter_none` | bool | `False` | Фильтровать пустые значения |

!!! warning "Предупреждение"
    Для выбора необходимых статистик их наименования необходимо передавать в метод непосредственно через запятую.

Для иллюстрации работы метода воспользуемся кодом из предыдущего примера:

!!! example "Пример"

    _Код_:

    ``` python
    ...
    
    # Отображение таблицы вычисленных статистик
    ms.print_stats(
        'pos', 'tense', 'number', 'person',
        filter_none=True
    )
    ```

    _Результат_:

    ``` bash
    ---------------Часть речи---------------
    Глагол (личная форма)         |    4     
    Союз                          |    4     
    Глагол (инфинитив)            |    2     
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

### explain_text

Выполняет разбор текста по морфологическим статистикам. Возвращает словарь, в котором ключами являются слова текста, а значениями - словарь их морфологических статистик.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `args` | tuple[str] | `-` | Перечень выбранных статистик |
| `filter_none` | bool | `False` | Фильтровать пустые значения |

!!! warning "Предупреждение"
    Для выбора необходимых статистик их наименования необходимо передавать в метод непосредственно через запятую.

Для иллюстрации работы метода воспользуемся кодом из предыдущего примера:

!!! example "Пример"

    _Код_:

    ``` python
    ...
    
    # Разбор текста по морфологическим статистикам
    ms.explain_text(
        'pos', 'tense', 'number', 'person',
        filter_none=True
    )
    ```

    _Результат_:

    ``` bash
    (('Постарайтесь', {'number': 'plur', 'pos': 'VERB'}),
    ('получить', {'pos': 'INFN'}),
    ('то', {'pos': 'CONJ'}),
    ('что', {'pos': 'CONJ'}),
    ('любите', {'number': 'plur', 'person': '2per', 'pos': 'VERB', 'tense': 'pres'}),
    ('иначе', {'pos': 'ADVB'}),
    ('придется', {'number': 'sing', 'person': '3per', 'pos': 'VERB', 'tense': 'futr'}),
    ('полюбить', {'pos': 'INFN'}),
    ('то', {'pos': 'CONJ'}),
    ('что', {'pos': 'CONJ'}),
    ('получили', {'number': 'plur', 'pos': 'VERB', 'tense': 'past'}))
    ```