# Длины предложений

!!! info ""
    **ruts.visualizers.sentence_lengths_plot()**, **ruts.visualizers.sentence_lengths()**

## Описание

<!-- core: visualizers/sentences.md:sentence_lengths_plot 85736ab -->
Кривая длин предложений - ритм текста: длина каждого предложения в словах по порядку, скользящее среднее по окну из `window` предложений и врезка с гистограммой длин. Чередование коротких и длинных предложений - редакторский признак живого текста, ровная кривая - монотонного. Функция принимает оси `ax` и возвращает `Axes`.

`sentence_lengths(source, sents_extractor=None, words_extractor=None)` извлекает длины: строка делится на предложения экстрактором предложений, каждое предложение - на слова экстрактором слов; предложения `Doc` берутся из его границ, а слова - из его токенов без знаков препинания и символов, причем части дефисного слова склеиваются (`во-первых` - одно слово); `Doc` без границ считается как его текст, экстракторами; предложения без слов пропускаются. Готовые длины - последовательность или итератор неотрицательных целых чисел - используются как есть; таблица, множество, словарь, байты или длина, которая не целое число, дают `SourceTypeError`, отрицательная длина - `SourceError`.

Это функции ядра [anyTS](https://sergeyshk.github.io/anyTS/visualizers/sentences/); для строки ruTS по умолчанию передает русские [`SentsExtractor`](../extractors/sentences.md) и [`WordsExtractor`](../extractors/words.md), параметры `sents_extractor` и `words_extractor` заменяют их. Подписи по умолчанию - русские из `ruts.constants.VISUALIZER_LABELS`; `labels` задает подписи поверх них.

## Параметры

<!-- core: visualizers/sentences.md:sentence_lengths_plot-parameters 5e37f4a -->
| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `source` | str/Doc/Iterable[int] | `-` | Текст, объект Doc или длины предложений (список, массив numpy, Series) |
| `window` | int | `10` | Окно скользящего среднего в предложениях |
| `inset` | bool | `True` | Показывать врезку с гистограммой |
| `ax` | Axes | `None` | Оси для графика |
| `labels` | dict[str, str] | `None` | Подписи поверх подписей по умолчанию: `title`, `xlabel`, `ylabel`, `length` (кривая), `average` (строка формата с `window`), `distribution` (врезка) |
| `sents_extractor` | SentsExtractor | `None` | Инструмент для извлечения предложений строки; по умолчанию экстрактор предложений библиотеки |
| `words_extractor` | WordsExtractor | `None` | Инструмент для извлечения слов предложения строки; по умолчанию экстрактор слов библиотеки |

## Пример использования

!!! example "Пример"

    _Код_:

    ``` python
    from ruts.datasets import StalinWorks
    from ruts.visualizers import sentence_lengths, sentence_lengths_plot

    text = next(StalinWorks().get_texts(limit=1))
    sentence_lengths(text)[:5]
    # [66, 9, 16, 9, 21]

    sentence_lengths_plot(text, window=10)
    ```

    _Результат_:

    ![ruts](../img/sentences.png){: .center }
