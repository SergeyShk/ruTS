# Примеры

Ноутбуки Jupyter в директории [examples/](https://github.com/SergeyShk/ruTS/tree/master/examples) репозитория. Каждый открывается в Google Colab кнопкой и ставит библиотеку с моделью spaCy сам; выводы всех ячеек сохранены в файлах, поэтому ноутбуки можно читать и без запуска.

## Сквозной разбор текста

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb)

[01_text_walkthrough.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb) - рассказ Чехова «Смерть чиновника» через все инструменты библиотеки по порядку: извлечение предложений и слов, базовые статистики, удобочитаемость с пресетами коэффициентов, лексическое разнообразие и оконный расчет, морфология, SEO-метрики стиля на художественном тексте и канцелярите, фоностатистика, синтаксис и связность по разбору spaCy, лексическая сложность по частотному словарю, подсветка, закон Ципфа и кривая длин предложений. В конце все статистики подключаются компонентами spaCy, и один проход `nlp.pipe` по набору `TextsByGrade` дает таблицу статистик по классам текста.

## Сложность текста по ступеням обучения

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/02_text_complexity_by_grade.ipynb)

[02_text_complexity_by_grade.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/02_text_complexity_by_grade.ipynb) - 68 текстов `TextsByGrade` с меткой класса от 1 до 17 как одна ось сложности, на которую по очереди накладываются все группы статистик: корреляция Спирмена одиннадцати формул удобочитаемости с меткой и их ошибка в классах, три пресета коэффициентов, лексическое разнообразие (с классом не связано) против лексической сложности по частотному словарю, синтаксис и морфология (именная нагрузка, глубина дерева, пассив, доля глаголов), связность, распределения по ступеням обучения и проверка на независимой хрестоматии для первого класса `SovChLit`.

## Запуск локально

``` bash
uv sync --group examples
uv run jupyter lab examples/
```

Команда `make notebooks` выполняет все ноутбуки, записывает выводы в файлы и убирает метаданные выполнения; workflow `examples.yml` прогоняет ноутбуки по расписанию и вручную.
