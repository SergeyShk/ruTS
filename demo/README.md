---
title: ruTS
emoji: 📈
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.27.0
python_version: "3.11"
app_file: app.py
pinned: false
license: mit
short_description: Статистики русского текста и подсветка его фрагментов
---

# ruTS

Демонстрация библиотеки [ruTS](https://github.com/SergeyShk/ruTS): вставьте текст на русском языке и получите
класс удобочитаемости с возрастом читателя, метрики лексического разнообразия, морфологический и синтаксический
профиль по модели `ru_core_news_sm`, SEO-метрики стиля, фоностатистики, график закона Ципфа и подсветку фрагментов,
из которых складываются эти числа: длинные предложения, сложные слова, стоп-слова, пассив, обороты, цепочки
родительных падежей и аллитерации.

Документация библиотеки: <https://sergeyshk.github.io/ruTS/>. Код демонстрации лежит в папке
[`demo`](https://github.com/SergeyShk/ruTS/tree/master/demo) репозитория и обновляется при каждом релизе.

Запуск локально:

```bash
pip install -r demo/requirements.txt
python demo/app.py
```
