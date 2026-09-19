# Примеры

Ноутбуки Jupyter в директории [examples/](https://github.com/SergeyShk/ruTS/tree/master/examples) репозитория. Каждый открывается в Google Colab кнопкой и ставит библиотеку с моделью spaCy сам; выводы всех ячеек сохранены в файлах, поэтому ноутбуки можно читать и без запуска.

## Сквозной разбор текста

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb)

[01_text_walkthrough.ipynb](https://github.com/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb) - рассказ Чехова «Смерть чиновника» через все инструменты библиотеки по порядку: извлечение предложений и слов, базовые статистики, удобочитаемость с пресетами коэффициентов, лексическое разнообразие и оконный расчет, морфология, SEO-метрики стиля на художественном тексте и канцелярите, фоностатистика, синтаксис и связность по разбору spaCy, лексическая сложность по частотному словарю, подсветка, закон Ципфа и кривая длин предложений. В конце все статистики подключаются компонентами spaCy, и один проход `nlp.pipe` по набору `TextsByGrade` дает таблицу статистик по классам текста.

## Запуск локально

``` bash
uv sync --all-groups
uv run jupyter lab examples/
```

Команда `make notebooks` выполняет все ноутбуки и записывает выводы в файлы; она же запускается workflow `examples.yml` по расписанию и вручную.
