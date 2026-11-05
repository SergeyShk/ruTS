# Примеры

Ноутбуки Jupyter в директории [examples/](https://github.com/SergeyShk/ruTS/tree/master/examples) репозитория. Выводы ячеек сохранены, ноутбуки можно читать без запуска; кнопка открывает ноутбук в Google Colab, где он сам ставит все нужное.

## Сквозной разбор текста

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb)

[01_text_walkthrough.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb) - рассказ Чехова «Смерть чиновника» через все инструменты библиотеки по порядку: экстракторы, все группы статистик, подсветка и графики. В конце статистики подключаются компонентами spaCy, и один проход `nlp.pipe` по набору `TextsByGrade` дает таблицу статистик по классам текста.

## Сложность текста по ступеням обучения

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/02_text_complexity_by_grade.ipynb)

[02_text_complexity_by_grade.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/02_text_complexity_by_grade.ipynb) - 68 текстов `TextsByGrade` с меткой класса от 1 до 17 как ось сложности, на которую по очереди накладываются все группы статистик: формулы удобочитаемости и пресеты коэффициентов, лексика, синтаксис и морфология, связность. В конце - проверка на независимой хрестоматии для первого класса `SovChLit`.

## Попарное сравнение прозаиков

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/03_prose_authors.ipynb)

[03_prose_authors.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/03_prose_authors.ipynb) - десять прозаиков `RussianLiterature`, до 200 окон в 1000 слов на автора, дельта Клиффа по признакам `text_features` для 45 пар: чем различаются Толстой и Достоевский, какие признаки отражают оформление издания, а не стиль, какие различают все пары, близость авторов по признакам и по дельте Барроуза с тестом Мантеля, атрибуция авторства по частым словам, символьным триграммам и признакам текста.

## Язык Сталина за полвека

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/04_stalin_corpus.ipynb)

[04_stalin_corpus.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/04_stalin_corpus.ipynb) - корпусные меры как инструменты диахронии на `StalinWorks` (1243 текста 1901-1952 годов, четыре периода): ключевые слова относительно частотного словаря и между периодами, сочетаемость слов «враг» и «партия» по периодам, дисперсия слов по томам, конкорданс `kwic` по леммам, закон Ципфа и MTLD по окнам.

## Стих и звук

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/05_poetry.ipynb)

[05_poetry.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/05_poetry.ipynb) - стиховедческие статистики и фоностатистики на `PoetryCorpus` (16 694 стихотворения XVIII-XX веков): онегинская строфа через `VerseStats`, метры и число стоп по эпохам и авторам, профиль ударности четырёхстопного ямба против ручных подсчётов Тарановского, схемы рифмовки и окончания строк, ударные гласные и аллитерация, проверка ударений и рифм на наборе RIFMA.

## Запуск локально

``` bash
uv sync --group examples
uv run jupyter lab examples/
```

`make notebooks` выполняет все ноутбуки, записывает выводы в файлы и убирает метаданные выполнения; workflow `examples.yml` прогоняет ноутбуки по расписанию и вручную.
