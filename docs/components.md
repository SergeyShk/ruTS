# Компоненты

<!-- core: components.md:StatsComponent e3962ed -->
Основа компонентов [spaCy](https://github.com/explosion/spaCy), которые кладут статистики текста в расширение `Doc`: компонент регистрирует расширение при добавлении в пайплайн, а для каждого документа вычисляет статистики и кладет их в `doc._.<name>`. Разработка компонентов в целом описана в [документации spaCy](https://spacy.io/usage/processing-pipelines#custom-components).

Компоненты ruTS - подклассы `StatsComponent` ядра [anyTS](https://sergeyshk.github.io/anyTS/components/), по одному на каждый класс статистик.

!!! note "Примечание"
    Примеры ниже используют модель `ru_core_news_sm`, которая ставится отдельно: `python -m spacy download ru_core_news_sm` (см. [установку](installation.md)).

## Имена { #names }

Фабрики носят префикс библиотеки: `ruts_basic`, `ruts_readability`, `ruts_diversity`, `ruts_morph`, `ruts_syntax`, `ruts_cohesion`, `ruts_lexical`, `ruts_style`, `ruts_phon`, `ruts_verse`. Они объявлены точками входа `spacy_factories`, поэтому пайплайн, сохраненный с этими компонентами (`nlp.to_disk(path)`), загружается через `spacy.load(path)` без `import ruts`.

<!-- core: components.md:StatsComponent-names 9314eeb -->
Имя компонента в пайплайне - это имя расширения: `nlp.add_pipe(factory, name="basic")` кладет статистики в `doc._.basic`. Без `name` компонент и расширение получают имя фабрики. Расширение следует за компонентом, когда пайплайн переименовывает его (`nlp.rename_pipe`), а имя, занятое расширением другого пакета, дает `ParameterError` вместо замены. Компонент, взятый из другого пайплайна (`add_pipe(name, source=other)`), - один и тот же объект в обоих, поэтому под новым именем он пишет и в то расширение в другом пайплайне; собственный компонент дает фабрика, `add_pipe(factory, name=...)`. Один и тот же компонент можно добавить дважды под разными именами, с разными параметрами. Документ без слов - пустая строка, пробелы, одни знаки препинания - проходит компонент нетронутым, а его расширение остается `None`.

У `ruts_lexical` нетронутым проходит и документ из одних чисел, у `ruts_verse` - документ без букв.

<!-- core: components.md:StatsComponent-serialization d6d5068 -->
!!! warning "Сериализация"
    Компонент кладет в `doc._.<name>` объект класса статистик, который spaCy сериализовать не умеет: `Doc.to_bytes()`, `DocBin(store_user_data=True)` и `nlp.pipe(..., n_process>1)` с такими компонентами в пайплайне завершатся ошибкой. Для сохранения документа исключайте пользовательские данные (`doc.to_bytes(exclude=["user_data"])`) или сохраняйте `doc._.<name>.get_stats()` отдельно; для многопроцессной обработки считайте статистики в основном процессе после `nlp.pipe`, без компонентов.

Добавление компонента расширяет токенизатор его пайплайна правилами для приклеенных к словам тире реплик (`ruts.utils.add_dash_rules`), чтобы `Doc` делился на слова так же, как строка; для своего пайплайна без компонентов ruTS вызовите эту функцию сами.

Знаки ударения ruTS снимает со слов `Doc`, но части речи, признаки и зависимости дает модель, а она видит слово со знаком как незнакомое и размечает его хуже: на тексте после `accentuate` у модели `ru_core_news_sm` меняется часть речи больше половины слов. Текст с ударениями передавайте в пайплайн без них - `nlp(ruts.utils.strip_marks(text))`.

## BasicStatsComponent

!!! info ""
    **ruts.components.BasicStatsComponent**

Модуль для компонента основных текстовых статистик.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `nlp` | Language | `-` | Объект класса Language |
| `name` | str | `"ruts_basic"` | Наименование компонента в пайплайне |

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
    nlp.add_pipe("ruts_basic", name="basic", last=True)

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

Модуль для компонента морфологических статистик текста. Части речи и признаки берутся из разметки модели (`token.pos_`, `token.morph`), в пайплайне без теггера - из pymorphy3.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `nlp` | Language | `-` | Объект класса Language |
| `name` | str | `"ruts_morph"` | Наименование компонента в пайплайне |

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
    nlp.add_pipe("ruts_morph", name="morph", last=True)

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
| `name` | str | `"ruts_readability"` | Наименование компонента в пайплайне |
| `preset` | str | `"plainrussian"` | [Пресет коэффициентов](stats/readability_stats.md#presets) (`plainrussian`, `fiction`, `academic`) |
| `basic` | str | `None` | Расширение компонента основных статистик, которые берутся вместо повторного подсчета |

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
    nlp.add_pipe("ruts_readability", name="readability", last=True)

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
    nlp.add_pipe(
        "ruts_readability", name="readability_fiction", config={"preset": "fiction"}, last=True
    )
    ```

## DiversityStatsComponent

!!! info ""
    **ruts.components.DiversityStatsComponent**

Модуль для компонента основных метрик лексического разнообразия текста.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `nlp` | Language | `-` | Объект класса Language |
| `name` | str | `"ruts_diversity"` | Наименование компонента в пайплайне |
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
    nlp.add_pipe("ruts_diversity", name="diversity", last=True)

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
    nlp.add_pipe(
        "ruts_diversity",
        name="diversity_ln",
        config={"window_len": 100, "log_base": 2.718281828459045},
        last=True,
    )
    ```

## StyleStatsComponent

!!! info ""
    **ruts.components.StyleStatsComponent**

Модуль для компонента SEO-метрик стиля текста.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `nlp` | Language | `-` | Объект класса Language |
| `name` | str | `"ruts_style"` | Наименование компонента в пайплайне |
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
    nlp.add_pipe("ruts_style", name="style", last=True)

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
    nlp.add_pipe(
        "ruts_style", name="style_short", config={"stopwords": ["и", "в", "не"], "top_n": 5}, last=True
    )
    ```

## PhonStatsComponent

!!! info ""
    **ruts.components.PhonStatsComponent**

Модуль для компонента фоностатистик текста.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `nlp` | Language | `-` | Объект класса Language |
| `name` | str | `"ruts_phon"` | Наименование компонента в пайплайне |
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
    nlp.add_pipe("ruts_phon", name="phon", last=True)

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
    nlp.add_pipe("ruts_phon", name="phon_windowed", config={"window_len": 5}, last=True)
    ```

## SyntaxStatsComponent

!!! info ""
    **ruts.components.SyntaxStatsComponent**

Модуль для компонента синтаксических статистик текста. Компонент работает по дереву зависимостей, поэтому в пайплайне должен быть парсер: модели `ru_core_news_sm`, `ru_core_news_md` или `ru_core_news_lg`; в пайплайне без парсера компонент вызывает исключение `SourceError`.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `nlp` | Language | `-` | Объект класса Language |
| `name` | str | `"ruts_syntax"` | Наименование компонента в пайплайне |

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
    nlp.add_pipe("ruts_syntax", name="syntax", last=True)

    # Доступ к посчитанным статистикам
    doc = nlp("Дом, построенный рабочими в прошлом году, был продан")
    doc._.syntax.tree_depth
    ```

    _Результат_:

    ``` bash
    4.0
    ```

## CohesionStatsComponent

!!! info ""
    **ruts.components.CohesionStatsComponent**

Модуль для компонента статистик связности текста. Компоненту нужны только границы предложений (модель или `sentencizer`); при наличии разметки части речи берутся из нее, леммы - из pymorphy3 по части речи токена.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `nlp` | Language | `-` | Объект класса Language |
| `name` | str | `"ruts_cohesion"` | Наименование компонента в пайплайне |

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
    nlp.add_pipe("ruts_cohesion", name="cohesion", last=True)

    # Доступ к посчитанным статистикам
    doc = nlp("Кот сидел на окне. Он смотрел на птиц. Птицы улетели, и кот уснул.")
    doc._.cohesion.noun_overlap_adjacent
    ```

    _Результат_:

    ``` bash
    0.5
    ```

## LexicalStatsComponent

!!! info ""
    **ruts.components.LexicalStatsComponent**

Модуль для компонента статистик лексической сложности текста. Метрики по частотному словарю требуют загруженного [`FreqDict`](datasets/freq2011.md), полосы и лексическая плотность считаются без него.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `nlp` | Language | `-` | Объект класса Language |
| `name` | str | `"ruts_lexical"` | Наименование компонента в пайплайне |
| `data_dir` | str | `None` | Путь к директории с частотным словарем; если не задан, используется директория по умолчанию |

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
    nlp.add_pipe("ruts_lexical", name="lexical", last=True)

    # Доступ к посчитанным статистикам
    doc = nlp("Кот сидел на окне и смотрел на птиц")
    doc._.lexical.p_top1000
    ```

    _Результат_:

    ``` bash
    0.75
    ```

Директория со словарем передается через `config`:

!!! example "Пример"

    ``` python
    nlp.add_pipe(
        "ruts_lexical", name="lexical_dicts", config={"data_dir": "/path/to/dicts"}, last=True
    )
    ```

## VerseStatsComponent

!!! info ""
    **ruts.components.VerseStatsComponent**

Модуль для компонента стиховедческих статистик текста. Требует загруженного словаря ударений [`StressDict`](datasets/stressdict.md); компонент работает по тексту `Doc` с переносами строк, поэтому текст стихотворения нужно передавать в `nlp` как есть, не склеивая строки. Текст с буквами, но без русских слов дает пустые статистики, как `VerseStats`, и `nlp.pipe` по корпусу на нем не прерывается.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `nlp` | Language | `-` | Объект класса Language |
| `name` | str | `"ruts_verse"` | Наименование компонента в пайплайне |
| `data_dir` | str | `None` | Путь к директории со словарем ударений; если не задан, используется директория по умолчанию |

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
    nlp.add_pipe("ruts_verse", name="verse", last=True)

    # Доступ к посчитанным статистикам
    doc = nlp(
        "Буря мглою небо кроет,\nВихри снежные крутя;\nТо, как зверь, она завоет,\nТо заплачет, как дитя"
    )
    doc._.verse.meter, doc._.verse.n_feet
    ```

    _Результат_:

    ``` bash
    ('хорей', 4)
    ```

Директория со словарем передается через `config`:

!!! example "Пример"

    ``` python
    nlp.add_pipe("ruts_verse", name="verse_dicts", config={"data_dir": "/path/to/dicts"}, last=True)
    ```
