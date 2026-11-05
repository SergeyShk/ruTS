# Установка

Библиотеку можно установить через `pip` или из репозитория проекта через `git`.

## Зависимости

*   `python` - 3.11 и выше
*   [`anyts`](https://sergeyshk.github.io/anyTS/) - 0.4.6 и выше в пределах 0.4, независимое от языка ядро, на котором построен ruTS
*   [`rumorph`](https://github.com/SergeyShk/ruMorph) - 0.5 и выше в пределах 0.5, морфологический анализатор
*   [`anyseg`](https://github.com/SergeyShk/anySeg) - 0.2 и выше в пределах 0.2, сегментатор на токены и предложения
*   `scipy`
*   `spaCy` - 3.8.15 и выше
*   `numpy`
*   `pandas`
*   `matplotlib`
*   `graphviz`

## Установка с помощью `pip`

Релизная версия ставится со всеми зависимостями:

``` bash
pip install ruts
```

!!! warning "Graphviz"
    Только [дереву слов](visualizers/word_tree.md) и [сети коллокаций](visualizers/corpus.md#collocation_network) нужны исполняемые файлы [Graphviz](https://graphviz.org/download/) (`brew install graphviz`, `apt install graphviz`, `conda install graphviz`): пакет `graphviz` из зависимостей - лишь обертка, без них `render()` и показ графа в Jupyter завершатся ошибкой `ExecutableNotFound`.

`import ruts` не загружает spaCy, matplotlib и pandas: они подключаются при первом обращении к `Doc`, компонентам, графикам и корпусным функциям.

!!! tip "Модель spaCy"
    [Компонентам spaCy](components.md), [синтаксическим статистикам](stats/syntax_stats.md) и [рекомендуемому конвейеру](components.md#load_pipeline) `ruts.load_pipeline()` нужна русскоязычная модель, без нее загрузка завершится ошибкой `OSError: [E050]`. Модель устанавливается отдельно:

    ``` bash
    python -m spacy download ru_core_news_sm
    ```

    Большие модели `ru_core_news_md` и `ru_core_news_lg` (93 и 670 МБ против 47) статистики ruTS почти не меняют: на золотой разметке Universal Dependencies (Taiga и GSD) они точнее `sm` меньше чем на пункт UAS.

!!! note "Наборы данных"
    [Наборы данных](datasets/sovchlit.md) по умолчанию загружаются в директорию `ruts_data` рядом с пакетом (`DEFAULT_DATA_DIR` в `ruts.constants`), при установке из колеса - в `site-packages/ruts_data`, куда у системного Python запись может быть запрещена. Свою директорию задает аргумент `data_dir` набора данных или переменная окружения `RUTS_DATA_DIR` до импорта пакета:

    ``` bash
    export RUTS_DATA_DIR=~/ruts_data
    ```

!!! note "Примечание"
    Руководство по `pip` - на [сайте разработчика](https://pip.pypa.io/en/stable/).

## Установка с помощью `git`

Последняя версия устанавливается из репозитория проекта:

1. Склонировать репозиторий:

    ``` bash
    git clone https://github.com/SergeyShk/ruTS.git
    ```

2. Перейти в неё:

    ``` bash
    cd ruTS
    ```

3. Установить библиотеку в текущее окружение:

    ``` bash
    pip install .
    ```

    Для разработки удобнее [uv](https://docs.astral.sh/uv/): он создаст изолированное окружение со всеми зависимостями, включая инструменты разработки:

    ``` bash
    uv sync --all-groups --no-group examples
    ```

    Группа `examples` с Jupyter нужна только для [ноутбуков с примерами](examples.md).

!!! note "Примечание"
    Руководство по `git` - на [сайте разработчика](https://git-scm.com/).
