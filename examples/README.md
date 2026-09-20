# Примеры

Ноутбуки с примерами работы библиотеки. Выводы ячеек сохранены, ноутбуки можно читать без запуска; кнопка открывает ноутбук в Google Colab, где он сам ставит библиотеку и модель spaCy.

| Ноутбук | О чем | Colab |
|---|---|---|
| [01_text_walkthrough.ipynb](01_text_walkthrough.ipynb) | Сквозной разбор рассказа Чехова всеми инструментами библиотеки и обработка корпуса компонентами spaCy | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/01_text_walkthrough.ipynb) |
| [02_text_complexity_by_grade.ipynb](02_text_complexity_by_grade.ipynb) | Формулы удобочитаемости, лексика, синтаксис, морфология и связность против метки класса на `TextsByGrade`, проверка на хрестоматии `SovChLit` | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/02_text_complexity_by_grade.ipynb) |
| [03_prose_authors.ipynb](03_prose_authors.ipynb) | Десять прозаиков `RussianLiterature` попарно: дельта Клиффа по 130 признакам, признаки оформления, близость авторов, сверка с дельтой Барроуза и атрибуция авторства | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/03_prose_authors.ipynb) |
| [04_stalin_corpus.ipynb](04_stalin_corpus.ipynb) | Корпусные меры как инструменты диахронии на `StalinWorks`: ключевые слова, коллокации по периодам, дисперсия, конкорданс, закон Ципфа | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/04_stalin_corpus.ipynb) |
| [05_poetry.ipynb](05_poetry.ipynb) | Метр, рифма и фоностатистика на `PoetryCorpus`: метры по эпохам и авторам, профиль ударности ямба против Тарановского, схемы рифмовки и окончания, ударные гласные и аллитерация, проверка на RIFMA | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/ruTS/blob/master/examples/05_poetry.ipynb) |

Локально: `uv sync --group examples`, затем `uv run jupyter lab examples/`. `make notebooks` выполняет все ноутбуки заново, записывает выводы в файлы и убирает метаданные выполнения.
