# Примеры

Ноутбуки с примерами работы библиотеки. Выводы ячеек сохранены, ноутбуки можно читать без запуска; кнопка открывает ноутбук в Google Colab, где он сам ставит библиотеку и модель spaCy.

| Ноутбук | О чем | Colab |
|---|---|---|
| [01_text_walkthrough.ipynb](01_text_walkthrough.ipynb) | Сквозной разбор рассказа Чехова всеми инструментами библиотеки и обработка корпуса компонентами spaCy | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb) |

Локально: `uv sync --group examples`, затем `uv run jupyter lab examples/`. `make notebooks` выполняет все ноутбуки заново, записывает выводы в файлы и убирает метаданные выполнения.
