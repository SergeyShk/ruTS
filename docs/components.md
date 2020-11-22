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
| `name` | str | `"bs"` | Наименование компонента в пайплайне |

Пример использования:

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    from ruts import BasicStatsComponent

    # Загрузка модели spaCy
    nlp = spacy.load('ru')

    # Добавление компонента
    bsc = BasicStatsComponent()
    nlp.add_pipe(bsc, 'basic', last=True)

    # Доступ к посчитанным метрикам
    doc = nlp("мама мыла раму")
    doc._.bs.c_letters
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
| `name` | str | `"ms"` | Наименование компонента в пайплайне |

Пример использования:

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    from ruts import MorphStatsComponent

    # Загрузка модели spaCy
    nlp = spacy.load('ru')

    # Добавление компонента
    msc = MorphStatsComponent()
    nlp.add_pipe(msc, 'morph', last=True)

    # Доступ к посчитанным метрикам
    doc = nlp("мама мыла раму")
    doc._.ms.case
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
| `name` | str | `"rs"` | Наименование компонента в пайплайне |

Пример использования:

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    from ruts import ReadabilityStatsComponent

    # Загрузка модели spaCy
    nlp = spacy.load('ru')

    # Добавление компонента
    rsc = ReadabilityStatsComponent()
    nlp.add_pipe(rsc, 'readability', last=True)

    # Доступ к посчитанным метрикам
    doc = nlp("мама мыла раму")
    doc._.rs.flesch_reading_easy
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
| `name` | str | `"ds"` | Наименование компонента в пайплайне |

Пример использования:

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    from ruts import DiversityStatsComponent

    # Загрузка модели spaCy
    nlp = spacy.load('ru')

    # Добавление компонента
    dsc = DiversityStatsComponent()
    nlp.add_pipe(dsc, 'diversity', last=True)

    # Доступ к посчитанным метрикам
    doc = nlp("мама мыла раму")
    doc._.ds.rttr
    ```

    _Результат_:

    ``` bash
    1.7320508075688774
    ```