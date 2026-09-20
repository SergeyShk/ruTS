# Примеры

Ноутбуки Jupyter в директории [examples/](https://github.com/SergeyShk/ruTS/tree/master/examples) репозитория. Каждый открывается в Google Colab кнопкой и ставит библиотеку с моделью spaCy сам; выводы всех ячеек сохранены в файлах, поэтому ноутбуки можно читать и без запуска.

## Сквозной разбор текста

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb)

[01_text_walkthrough.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb) - рассказ Чехова «Смерть чиновника» через все инструменты библиотеки по порядку: извлечение предложений и слов, базовые статистики, удобочитаемость с пресетами коэффициентов, лексическое разнообразие и оконный расчет, морфология, SEO-метрики стиля на художественном тексте и канцелярите, фоностатистика, синтаксис и связность по разбору spaCy, лексическая сложность по частотному словарю, подсветка, закон Ципфа и кривая длин предложений. В конце все статистики подключаются компонентами spaCy, и один проход `nlp.pipe` по набору `TextsByGrade` дает таблицу статистик по классам текста.

## Сложность текста по ступеням обучения

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/02_text_complexity_by_grade.ipynb)

[02_text_complexity_by_grade.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/02_text_complexity_by_grade.ipynb) - 68 текстов `TextsByGrade` с меткой класса от 1 до 17 как одна ось сложности, на которую по очереди накладываются все группы статистик: корреляция Спирмена одиннадцати формул удобочитаемости с меткой и их ошибка в классах, три пресета коэффициентов, лексическое разнообразие (с классом не связано) против лексической сложности по частотному словарю, синтаксис и морфология (именная нагрузка, глубина дерева, пассив, доля глаголов), связность, распределения по ступеням обучения и проверка на независимой хрестоматии для первого класса `SovChLit`.

## Попарное сравнение прозаиков

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/03_prose_authors.ipynb)

[03_prose_authors.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/03_prose_authors.ipynb) - десять прозаиков `RussianLiterature` по 200 окон в 1000 слов, 130 признаков `text_features` и дельта Клиффа для 45 пар: три сильнейших признака каждой пары, подробный разбор Толстого и Достоевского (`compare_features`, распределения признаков, ключевые слова - речь против повествования), число признаков с большим эффектом как расстояние (от 6 у Гоголя-Тургенева до 67 у Герцена-Достоевского), признаки оформления издания (кавычки, ё), которые надо исключать, универсальные различители (точка с запятой, многоточие, длина слова, оконные меры разнообразия), дендрограмма и многомерное шкалирование по признакам и по дельте Барроуза с тестом Мантеля, атрибуция авторства окон в 1000 слов с отложенными произведениями (варианты дельты, число частых слов, словоформы против символьных триграмм, признаки текста как классификатор, матрица ошибок, маркеры Zeta).

## Язык Сталина за полвека

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/04_stalin_corpus.ipynb)

[04_stalin_corpus.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/04_stalin_corpus.ipynb) - корпусные меры как инструменты диахронии на `StalinWorks` (1243 текста 1901-1952 годов, четыре периода): ключевые слова относительно частотного словаря и артефакты лемматизации при сравнении с внешним словарём, ключевые слова периодов и `keyness_plot` двух крайних периодов, сочетаемость слов «враг» и «партия» по периодам через `collocations` с `node`, дисперсия слов по томам и `dispersion_plot` как лента времени, конкорданс `kwic` по леммам, закон Ципфа и MTLD по окнам для каждого периода.

## Запуск локально

``` bash
uv sync --group examples
uv run jupyter lab examples/
```

Команда `make notebooks` выполняет все ноутбуки, записывает выводы в файлы и убирает метаданные выполнения; workflow `examples.yml` прогоняет ноутбуки по расписанию и вручную.
