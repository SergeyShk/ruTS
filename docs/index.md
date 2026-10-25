# Russian Texts Statistics (ruTS)

![ruTS](img/ruts.svg)

**ruTS** считает по русскому тексту то, для чего обычно приходится собирать несколько разрозненных инструментов: от базовых статистик, удобочитаемости и лексического разнообразия до морфологии, синтаксиса, связности, стилометрии и корпусных мер - по опубликованным формулам, адаптированным для русского языка.

Работать можно как с обычными строками, так и с готовыми `Doc`-объектами [spaCy](https://github.com/explosion/spaCy) - каждая статистика доступна и как отдельный класс, и как компонент пайплайна spaCy.

Попробовать без установки можно в [демо на Hugging Face Spaces](https://huggingface.co/spaces/SergeyShk/ruTS): вставьте текст и получите класс удобочитаемости, метрики, графики и подсветку фрагментов.

## Возможности

<div class="grid cards" markdown>

-   :material-scissors-cutting:{ .lg .middle } __Извлечение__

    ---

    Токенизаторы [слов](extractors/words.md), [предложений](extractors/sentences.md) и [символьных N-грамм](extractors/char_ngrams.md) с фильтрами, лемматизацией и N-граммами

    [:octicons-arrow-right-24: Извлечение объектов](extractors/sentences.md)

-   :material-format-letter-case:{ .lg .middle } __Слоги и ударение__

    ---

    Деление слов на слоги, количество слогов, ударный слог по словарю и тип окончания

    [:octicons-arrow-right-24: Слоги и ударение](syllables.md)

-   :material-counter:{ .lg .middle } __Базовые статистики__

    ---

    Количество слов, предложений, знаков препинания, слогов и другие базовые статистики текста

    [:octicons-arrow-right-24: Базовые статистики](stats/basic_stats.md)

-   :material-book-open-variant:{ .lg .middle } __Удобочитаемость__

    ---

    Тест Флеша-Кинкайда, индекс SMOG, индекс удобочитаемости LIX и другие метрики с коэффициентами для русского языка, а также формулы других языков с исходными коэффициентами

    [:octicons-arrow-right-24: Метрики удобочитаемости](stats/readability_stats.md)

-   :material-chart-bell-curve:{ .lg .middle } __Лексическое разнообразие__

    ---

    Type-Token Ratio, Measure of Textual Lexical Diversity, гапакс-индекс и другие метрики

    [:octicons-arrow-right-24: Метрики лексического разнообразия](stats/diversity_stats.md)

-   :material-alphabetical-variant:{ .lg .middle } __Морфология__

    ---

    Морфологические признаки в терминах Universal Dependencies: часть речи, падеж, наклонение, переходность и другие

    [:octicons-arrow-right-24: Морфологические статистики](stats/morph_stats.md)

-   :material-feather:{ .lg .middle } __Стиль__

    ---

    SEO-метрики: тошнота, водность, заспамленность, естественность по Ципфу, плотность ключевых слов

    [:octicons-arrow-right-24: SEO-метрики стиля](stats/style_stats.md)

-   :material-waveform:{ .lg .middle } __Фонетика__

    ---

    Доли классов звуков, консонантные кластеры, аллитерация и ассонанс, слоги

    [:octicons-arrow-right-24: Фоностатистики](stats/phon_stats.md)

-   :material-file-tree:{ .lg .middle } __Синтаксис__

    ---

    Статистики дерева зависимостей spaCy: длины зависимостей, глубина дерева, сочинительные цепочки, клаузы, индексы L2SCA, обороты, пассив, предложные цепочки и цепочки родительных падежей, порядок слов, схожесть соседних предложений

    [:octicons-arrow-right-24: Синтаксические статистики](stats/syntax_stats.md)

-   :material-link-variant:{ .lg .middle } __Связность__

    ---

    Повторы существительных, аргументов и знаменательных слов между предложениями и абзацами, данность, темпоральная связность, коннекторы по классам, меж- и внутрипредложенческие

    [:octicons-arrow-right-24: Статистики связности](stats/cohesion_stats.md)

-   :material-school:{ .lg .middle } __Лексическая сложность__

    ---

    Частотность слов по словарю Ляшевской и Шарова, частотные полосы, сюрпризал, лексическая плотность

    [:octicons-arrow-right-24: Статистики лексической сложности](stats/lexical_stats.md)

-   :material-music-note:{ .lg .middle } __Стиховедение__

    ---

    Ударения по словарю Козиева, метр и число стоп, пиррихии и профиль ударности, схемы рифмовки, окончания и строфы

    [:octicons-arrow-right-24: Стиховедческие статистики](stats/verse_stats.md)

-   :material-bookshelf:{ .lg .middle } __Корпусные меры__

    ---

    [Ключевые слова](corpus/keyness.md) относительно эталонного корпуса или частотного словаря, [коллокации](corpus/collocations.md), [дисперсия слов](corpus/dispersion.md) по частям текста, [конкорданс KWIC](corpus/kwic.md), меры [стилометрии](corpus/stylometry.md) (дельта Барроуза с вариантами и скользящая дельта вдоль текста, Zeta и доли ее маркеров в сегментах, хи-квадрат Килгарриффа, кривая Менденхолла, профиль служебных слов) и [сравнение корпусов](corpus/compare.md) по всем признакам сразу (критерий Манна-Уитни, d Коэна, дельта Клиффа, бутстрэп-интервалы, AUC)

    [:octicons-arrow-right-24: Корпусные меры](corpus/keyness.md)

-   :material-database:{ .lg .middle } __Наборы данных__

    ---

    [Советские христоматии по литературе](datasets/sovchlit.md), [Полное собрание сочинений И.В. Сталина](datasets/stalinworks.md), [Тексты с метками класса](datasets/textsbygrade.md), [Частотный словарь Ляшевской и Шарова](datasets/freq2011.md), [Корпус русской поэзии](datasets/poetrycorpus.md), [Русская классическая литература](datasets/russianliterature.md), [Словарь ударений Козиева](datasets/stressdict.md)

    [:octicons-arrow-right-24: Наборы данных](datasets/sovchlit.md)

-   :material-chart-scatter-plot:{ .lg .middle } __Визуализация__

    ---

    [Закон Ципфа](visualizers/zipf.md), [литературная дактилоскопия](visualizers/fingerprinting.md), [дерево слов](visualizers/word_tree.md), [подсветка текста](visualizers/highlight.md), [корпусные](visualizers/corpus.md) и [стилометрические](visualizers/stylometry.md) графики, [рост словаря и спектр частот](visualizers/vocabulary.md), [длины предложений](visualizers/sentences.md)

    [:octicons-arrow-right-24: Визуализации](visualizers/zipf.md)

-   :material-pipe:{ .lg .middle } __Компоненты__

    ---

    Компоненты для встраивания статистик в пайплайны spaCy

    [:octicons-arrow-right-24: Компоненты](components.md)

-   :material-alert-circle-outline:{ .lg .middle } __Исключения__

    ---

    Ошибки одной иерархии, классы которой одновременно встроенные исключения Python

    [:octicons-arrow-right-24: Исключения и логирование](exceptions.md)

</div>

## Установка

Требуется Python 3.11 или новее.

``` bash
pip install ruts
```

Подробнее о зависимостях и установке из репозитория - на странице [Установка](installation.md).

## Быстрый старт

=== "Код"

    ``` python
    from ruts import BasicStats, DiversityStats, ReadabilityStats

    text = "Существуют три вида лжи: ложь, наглая ложь и статистика"

    BasicStats(text).get_stats()
    ReadabilityStats(text).flesch_reading_easy
    DiversityStats(text).ttr
    ```

=== "Результат"

    ```
    {'c_letters': {1: 1, 3: 2, 4: 3, 6: 1, 10: 2},
     'c_syllables': {1: 5, 2: 1, 3: 1, 4: 2},
     'n_sents': 1,
     'n_words': 9,
     'n_unique_words': 8,
     'n_long_words': 3,
     'n_complex_words': 2,
     'n_simple_words': 7,
     'n_monosyllable_words': 5,
     'n_polysyllable_words': 4,
     'n_chars': 55,
     'n_letters': 45,
     'n_spaces': 8,
     'n_syllables': 18,
     'n_punctuations': 2,
     'c_punctuations': {'comma': 1,
                        'period': 0,
                        'question': 0,
                        'exclamation': 0,
                        'ellipsis': 0,
                        'colon': 1,
                        'semicolon': 0,
                        'dash': 0,
                        'hyphen': 0,
                        'angle_quotes': 0,
                        'straight_quotes': 0,
                        'parentheses': 0,
                        'other': 0}}
    74.93500000000003
    0.8888888888888888
    ```

Любую статистику можно вывести на экран в читаемом виде:

=== "Код"

    ``` python
    BasicStats(text).print_stats()
    ```

=== "Результат"

    ```
        Статистика     | Значение
    ------------------------------
    Предложения        |    1
    Слова              |    9
    Уникальные слова   |    8
    Длинные слова      |    3
    Сложные слова      |    2
    Простые слова      |    7
    Односложные слова  |    5
    Многосложные слова |    4
    Символы            |    55
    Буквы              |    45
    Пробелы            |    8
    Слоги              |    18
    Знаки препинания   |    2
    ```

Сквозной разбор одного рассказа всеми инструментами библиотеки - в ноутбуке [examples/01_text_walkthrough.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb), его можно открыть в [Colab](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb); остальные ноутбуки - на странице [примеров](examples.md).

??? note "Структура проекта"

    *   **docs** - документация по проекту
    *   **ruts**:
        *   basic_stats.py - базовые текстовые статистики
        *   cohesion_stats.py - статистики связности текста
        *   components.py - компоненты spaCy
        *   constants.py - основные используемые константы
        *   diversity_stats.py - метрики лексического разнообразия текста
        *   exceptions.py - исключения библиотеки
        *   extractors.py - инструменты для извлечения объектов из текста
        *   lexical_stats.py - статистики лексической сложности текста
        *   morph_stats.py - морфологические статистики
        *   phon_stats.py - фоностатистики текста
        *   readability_stats.py - метрики удобочитаемости текста
        *   style_stats.py - SEO-метрики стиля текста
        *   syllables.py - слоги и ударение
        *   syntax_stats.py - синтаксические статистики текста
        *   unadapted_readability_stats.py - формулы удобочитаемости других языков
        *   utils.py - вспомогательные инструменты
        *   verse_stats.py - стиховедческие статистики: ударения, метр, рифма, строфика
        *   **corpus** - корпусные меры:
            *   collocations.py - коллокации и меры ассоциации
            *   compare.py - сравнение корпусов по признакам текста
            *   dispersion.py - дисперсия слов по частям текста
            *   keyness.py - ключевые слова относительно эталонного корпуса
            *   kwic.py - конкорданс KWIC
            *   stylometry.py - дельта Барроуза, Zeta и другие меры стилометрии
        *   **datasets** - наборы данных:
            *   dataset.py - базовый класс для работы с наборами данных
            *   freq2011.py - частотный словарь Ляшевской и Шарова
            *   poetry_corpus.py - корпус русской поэзии PoetryCorpus
            *   russian_literature.py - собрание русской классической литературы RusLit
            *   sov_chrest_lit.py - советские хрестоматии по литературе
            *   stalin_works.py - полное собрание сочинений И.В. Сталина
            *   stress_dict.py - словарь ударений Козиева
            *   texts_by_grade.py - тексты с метками класса проекта Plain Russian Language
        *   **resources** - вшитые лексические ресурсы (список самых частых лемм, словарь коннекторов)
        *   **visualizers** - инструменты для визуализации текстов:
            *   corpus.py - Лексическая дисперсия, ключевые слова, сеть коллокаций
            *   fingerprinting.py - Литературная дактилоскопия
            *   highlight.py - Подсветка текста
            *   sentences.py - Длины предложений
            *   stylometry.py - Дендрограмма, главные компоненты, шкалирование, расстояния внутри и между авторами, скользящая дельта, маркеры Zeta, кривые Менденхолла
            *   vocabulary.py - Закон Хипса и спектр частот
            *   word_tree.py - Дерево слов
            *   zipf.py - Закон Ципфа
    *   **tests** - тесты, повторяющие структуру пакета
    *   **scripts** - скрипт загрузки страниц документации anyTS
    *   **examples** - ноутбуки с примерами
    *   **demo** - демонстрация на Gradio для Hugging Face Spaces
