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
    nlp = spacy.load("ru_core_news_sm")

    # Добавление компонента
    nlp.add_pipe("basic", last=True)

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

Модуль для компонента морфологических статистик текста. Части речи и признаки берутся из разметки модели (`token.pos_`, `token.morph`) в терминах Universal Dependencies; в пайплайне без теггера используется pymorphy3.

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
    nlp = spacy.load("ru_core_news_sm")

    # Добавление компонента
    nlp.add_pipe("morph", last=True)

    # Доступ к посчитанным метрикам
    doc = nlp("мама мыла раму")
    doc._.morph.case
    ```

    _Результат_:

    ``` bash
    ('Nom', None, 'Acc')
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
| `preset` | str | `"plainrussian"` | [Пресет коэффициентов](stats/readability_stats.md#presets) (`plainrussian`, `fiction`, `academic`) |

Пример использования:

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    import ruts
    import spacy

    # Загрузка модели spaCy
    nlp = spacy.load("ru_core_news_sm")

    # Добавление компонента
    nlp.add_pipe("readability", last=True)

    # Доступ к посчитанным метрикам
    doc = nlp("мама мыла раму")
    doc._.readability.flesch_reading_easy
    ```

    _Результат_:

    ``` bash
    82.735
    ```

Пресет коэффициентов передается через `config`:

!!! example "Пример"

    ``` python
    nlp.add_pipe("readability", config={"preset": "fiction"}, last=True)
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
| `window_len` | int | `50` | Размер окна для MATTR и сегмента для MSTTR |
| `mtld_threshold` | float | `0.72` | Порог TTR для MTLD, MA-MTLD и MTLD-W |
| `mtld_min_len` | int | `10` | Минимальная длина фактора для MTLD, MA-MTLD и MTLD-W |
| `hdd_sample_size` | int | `42` | Размер выборки для HD-D |
| `log_base` | float | `10` | Основание логарифма для метрик Summer, Maas и Dugast |

Пример использования:

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    import ruts
    import spacy

    # Загрузка модели spaCy
    nlp = spacy.load("ru_core_news_sm")

    # Добавление компонента
    nlp.add_pipe("diversity", last=True)

    # Доступ к посчитанным метрикам
    doc = nlp("мама мыла раму")
    doc._.diversity.rttr
    ```

    _Результат_:

    ``` bash
    1.7320508075688774
    ```

Окна, пороги и основание логарифма передаются через `config`:

!!! example "Пример"

    ``` python
    nlp.add_pipe("diversity", config={"window_len": 100, "log_base": 2.718281828459045}, last=True)
    ```

## StyleStatsComponent

!!! info ""
    **ruts.components.StyleStatsComponent**

Модуль для компонента SEO-метрик стиля текста.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `nlp` | Language | `-` | Объект класса Language |
| `name` | str | `"style"` | Наименование компонента в пайплайне |
| `stopwords` | list[str] | `None` | Список стоп-слов для водности; если не задан, используется разметка pymorphy3 |
| `top_n` | int | `10` | Количество самых частых слов для академической тошноты и естественности по Ципфу |

Пример использования:

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    import ruts
    import spacy

    # Загрузка модели spaCy
    nlp = spacy.load("ru_core_news_sm")

    # Добавление компонента
    nlp.add_pipe("style", last=True)

    # Доступ к посчитанным метрикам
    doc = nlp("мама мыла раму")
    doc._.style.water
    ```

    _Результат_:

    ``` bash
    0.0
    ```

Список стоп-слов и количество самых частых слов передаются через `config`:

!!! example "Пример"

    ``` python
    nlp.add_pipe("style", config={"stopwords": ["и", "в", "не"], "top_n": 5}, last=True)
    ```

## PhonStatsComponent

!!! info ""
    **ruts.components.PhonStatsComponent**

Модуль для компонента фоностатистик текста.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `nlp` | Language | `-` | Объект класса Language |
| `name` | str | `"phon"` | Наименование компонента в пайплайне |
| `window_len` | int | `3` | Размер окна в словах для аллитерации и ассонанса |

Пример использования:

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    import ruts
    import spacy

    # Загрузка модели spaCy
    nlp = spacy.load("ru_core_news_sm")

    # Добавление компонента
    nlp.add_pipe("phon", last=True)

    # Доступ к посчитанным статистикам
    doc = nlp("мама мыла раму")
    doc._.phon.p_open_syllables
    ```

    _Результат_:

    ``` bash
    1.0
    ```

Размер окна передается через `config`:

!!! example "Пример"

    ``` python
    nlp.add_pipe("phon", config={"window_len": 5}, last=True)
    ```

## SyntaxStatsComponent

!!! info ""
    **ruts.components.SyntaxStatsComponent**

Модуль для компонента синтаксических статистик текста. Компонент работает по дереву зависимостей, поэтому в пайплайне должен быть парсер: модели `ru_core_news_sm`, `ru_core_news_md` или `ru_core_news_lg`; в пайплайне без парсера компонент вызывает исключение `ValueError`.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `nlp` | Language | `-` | Объект класса Language |
| `name` | str | `"syntax"` | Наименование компонента в пайплайне |

Пример использования:

!!! example "Пример"

    _Код_:

    ``` python
    # Загрузка библиотек
    import ruts
    import spacy

    # Загрузка модели spaCy
    nlp = spacy.load("ru_core_news_sm")

    # Добавление компонента
    nlp.add_pipe("syntax", last=True)

    # Доступ к посчитанным статистикам
    doc = nlp("Дом, построенный рабочими в прошлом году, был продан")
    doc._.syntax.tree_depth
    ```

    _Результат_:

    ``` bash
    4.0
    ```
