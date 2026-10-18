# Извлечение символьных N-грамм

!!! info ""
    **ruts.extractors.CharNgramsExtractor**

## Описание

<!-- core: extractors/char_ngrams.md:CharNgramsExtractor bde0c17 -->
Класс для извлечения символьных N-грамм из текста - последовательностей из N символов, взятых окном по строке. Символьные N-граммы - стандартный признак стилометрии и атрибуции авторства (Stamatatos 2009), они могут заменять слова в мерах вроде дельты Барроуза.

Пробельные символы схлопываются в один пробел, знаки препинания сохраняются. При `within_words=True` N-граммы не пересекают границ слов: текст режется токенизатором на слова, знаки препинания отбрасываются, слова короче N N-грамм не дают.

Список N-грамм подается в [`delta`](../corpus/stylometry.md) как единицы текста вместо слов.

## Языковые крючки

Класс расширяет `CharNgramsExtractor` ядра [anyTS](https://sergeyshk.github.io/anyTS/extractors/char_ngrams/) крючком русского языка: его токенизатор слов по умолчанию для `within_words`, метод `tokenize(text)`, - токенизатор по умолчанию [`WordsExtractor`](words.md), функция `tokenize` библиотеки [razdel](https://github.com/natasha/razdel) с отделением приклеенных к словам тире реплик (`ruts.utils.iter_tokens`). Перед извлечением из текста снимаются знаки ударения и мягкие переносы (`ruts.utils.strip_marks`).

## Параметры

<!-- core: extractors/char_ngrams.md:CharNgramsExtractor-parameters eb715ea -->
| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `n` | int | `2` | Длина N-граммы в символах |
| `lowercase` | bool | `False` | Конвертировать текст в нижний регистр |
| `within_words` | bool | `False` | Брать N-граммы только внутри слов |
| `tokenizer` | Pattern/Callable | `None` | Токенизатор слов для `within_words` или регулярное выражение; по умолчанию метод `tokenize` |

`n`, который не целое число не меньше единицы, дает `ParameterError`.

## Методы

### extract

<!-- core: extractors/char_ngrams.md:CharNgramsExtractor-extract 2efd64a -->
Выполняет извлечение N-грамм из текста.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `text` | str | `-` | Строка текста |

Текст, который не строка, дает `SourceTypeError`, как и, при `within_words`, токенизатор, который нельзя вызвать или который возвращает не строки.

!!! example "Пример"

    ``` python
    from ruts import CharNgramsExtractor

    text = "Кот сидел  на окне, а пёс - на полу."

    ce = CharNgramsExtractor()
    ce.extract(text)[:8]
    # ('Ко', 'от', 'т ', ' с', 'си', 'ид', 'де', 'ел')

    ce = CharNgramsExtractor(n=3, lowercase=True)
    ce.extract(text)[:6]
    # ('кот', 'от ', 'т с', ' си', 'сид', 'иде')

    CharNgramsExtractor(n=3, lowercase=True, within_words=True).extract(text)
    # ('кот', 'сид', 'иде', 'дел', 'окн', 'кне', 'пёс', 'пол', 'олу')
    ```

### get_most_common

<!-- core: extractors/char_ngrams.md:CharNgramsExtractor-get_most_common 7e493b6 -->
Возвращает топ-N-граммы текста списком пар (N-грамма, частота), начиная с самой частой; количество, которое не целое число не меньше единицы, дает `ParameterError`.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `n` | int | `10` | Количество топ-N-грамм |

!!! warning "Предупреждение"
    Метод должен вызываться после извлечения N-грамм методом `extract`.

!!! example "Пример"

    ``` python
    ce = CharNgramsExtractor(n=3, lowercase=True)
    ce.extract(text)
    ce.get_most_common(2)
    # [(' на', 2), ('на ', 2)]
    ```
