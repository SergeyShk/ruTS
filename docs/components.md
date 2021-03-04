# Компоненты

Набор модулей для создания компонентов [spaCy](https://github.com/explosion/spaCy). Каждый модуль представляет собой класс с двумя реализованными методами: `__init__` (добавляет новое расширение в пайплайн при инициализации) и `__call__` (принимает объект класса `Doc` и возвращает его модифицированную версию).

!!! note "Примечание"
    Подробную информацию о разработке пользовательских компонентов для spaCy можно узнать в соответствующем разделе [документации](https://spacy.io/usage/processing-pipelines#custom-components).

## BasicStatsComponent

!!! info ""
    **ruts.components.BasicStatsComponent**

Модуль для компонента основных текстовых статистик.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `nlp` | Language | `-` | Объект класса Language |
| `name` | str | `"basic"` | Наименование компонента в пайплайне |

Пример использования:

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    import ruts
    import spacy

    # Загрузка модели spaCy
    nlp = spacy.load('ru_core_news_sm')

    # Добавление компонента
    nlp.add_pipe('basic', last=True)

    # Доступ к посчитанным метрикам
    doc = nlp("мама мыла раму")
    doc._.basic.c_letters
    ```

    _Результат_:

    ``` bash
    {4: 3}
    ```

## MorphStatsComponent

!!! info ""
    **ruts.components.MorphStatsComponent**

Модуль для компонента морфологических статистик текста.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `nlp` | Language | `-` | Объект класса Language |
| `name` | str | `"morph"` | Наименование компонента в пайплайне |

Пример использования:

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    import ruts
    import spacy

    # Загрузка модели spaCy
    nlp = spacy.load('ru_core_news_sm')

    # Добавление компонента
    nlp.add_pipe('morph', last=True)

    # Доступ к посчитанным метрикам
    doc = nlp("мама мыла раму")
    doc._.morph.case
    ```

    _Результат_:

    ``` bash
    ('nomn', 'gent', 'datv')
    ```

## ReadabilityStatsComponent

!!! info ""
    **ruts.components.ReadabilityStatsComponent**

Модуль для компонента основных метрик удобочитаемости текста.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `nlp` | Language | `-` | Объект класса Language |
| `name` | str | `"readability"` | Наименование компонента в пайплайне |

Пример использования:

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    import ruts
    import spacy

    # Загрузка модели spaCy
    nlp = spacy.load('ru_core_news_sm')

    # Добавление компонента
    nlp.add_pipe('readability', last=True)

    # Доступ к посчитанным метрикам
    doc = nlp("мама мыла раму")
    doc._.readability.flesch_reading_easy
    ```

    _Результат_:

    ``` bash
    82.735
    ```

## DiversityStatsComponent

!!! info ""
    **ruts.components.DiversityStatsComponent**

Модуль для компонента основных метрик лексического разнообразия текста.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `nlp` | Language | `-` | Объект класса Language |
| `name` | str | `"diversity"` | Наименование компонента в пайплайне |

Пример использования:

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    import ruts
    import spacy

    # Загрузка модели spaCy
    nlp = spacy.load('ru_core_news_sm')

    # Добавление компонента
    nlp.add_pipe('diversity', last=True)

    # Доступ к посчитанным метрикам
    doc = nlp("мама мыла раму")
    doc._.diversity.rttr
    ```

    _Результат_:

    ``` bash
    1.7320508075688774
    ```