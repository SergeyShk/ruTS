# Извлечение символьных N-грамм

``` {.python .signature}
CharNgramsExtractor(n=2, lowercase=False, within_words=False, tokenizer=None)
```

<!-- core: extractors/char_ngrams.md:CharNgramsExtractor afcd43e -->
Класс для извлечения символьных N-грамм из текста - последовательностей из N символов, взятых окном по строке. Символьные N-граммы - стандартный признак стилометрии и атрибуции авторства (Stamatatos 2009), они могут заменять слова в мерах вроде дельты Барроуза.

Пробельные символы схлопываются в один пробел, знаки препинания сохраняются. При `within_words=True` N-граммы не пересекают границ слов: текст режется токенизатором на слова, знаки препинания отбрасываются, слова короче N N-грамм не дают.

Исключения:

- `ParameterError` - `n`, который не целое число не меньше единицы.

Класс расширяет `CharNgramsExtractor` ядра [anyTS](https://sergeyshk.github.io/anyTS/extractors/char_ngrams/) крючком русского языка: его токенизатор слов по умолчанию для `within_words`, метод `tokenize(text)`, - токенизатор по умолчанию [`WordsExtractor`](words.md), функция `tokenize` библиотеки [razdel](https://github.com/natasha/razdel) с отделением приклеенных к словам тире реплик (`ruts.utils.iter_tokens`). Перед извлечением из текста снимаются знаки ударения и мягкие переносы (`ruts.utils.strip_marks`). Список N-грамм подается в [`delta`](../corpus/stylometry.md) как единицы текста вместо слов.

=== "Код"

    ``` python
    from ruts import CharNgramsExtractor

    text = "Кот сидел  на окне, а пёс - на полу."

    ce = CharNgramsExtractor(n=3, lowercase=True)
    ce.extract(text)[:6]
    CharNgramsExtractor().extract(text)[:8]
    CharNgramsExtractor(n=3, lowercase=True, within_words=True).extract(text)
    ```

=== "Результат"

    ```
    ('кот', 'от ', 'т с', ' си', 'сид', 'иде')
    ('Ко', 'от', 'т ', ' с', 'си', 'ид', 'де', 'ел')
    ('кот', 'сид', 'иде', 'дел', 'окн', 'кне', 'пёс', 'пол', 'олу')
    ```

## Параметры

<!-- core: extractors/char_ngrams.md:CharNgramsExtractor-parameters 20eb078 -->
| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `n` | `int` | `2` | Длина N-граммы в символах |
| `lowercase` | `bool` | `False` | Конвертировать текст в нижний регистр |
| `within_words` | `bool` | `False` | Брать N-граммы только внутри слов |
| `tokenizer` | `Pattern` / `Callable` | `None` | Токенизатор слов для `within_words` или регулярное выражение; по умолчанию метод `tokenize` |

## Методы

<!-- core: extractors/char_ngrams.md:CharNgramsExtractor-extract 8089d17 -->
`extract(text)` извлекает N-граммы из текста.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `text` | `str` | - | Строка текста |

Текст, который не строка, дает `SourceTypeError`, как и, при `within_words`, токенизатор, который нельзя вызвать или который возвращает не строки.

<!-- core: extractors/char_ngrams.md:CharNgramsExtractor-get_most_common 660dfe8 -->
`get_most_common(n=10)` возвращает топ-N-граммы текста списком пар (N-грамма, частота), начиная с самой частой.

| Параметр | Тип | По умолчанию | Описание |
| :------- | :-- | :----------- | :------- |
| `n` | `int` | `10` | Количество топ-N-грамм |

Количество, которое не целое число не меньше единицы, дает `ParameterError`.

!!! warning "Предупреждение"
    Метод должен вызываться после извлечения N-грамм методом `extract`.

=== "Код"

    ``` python
    ce.get_most_common(2)
    ```

=== "Результат"

    ```
    [(' на', 2), ('на ', 2)]
    ```
