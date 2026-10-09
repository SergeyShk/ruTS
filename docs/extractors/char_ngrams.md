# Извлечение символьных N-грамм

!!! info ""
    **ruts.extractors.CharNgramsExtractor**

## Описание

<!-- core: extractors/char_ngrams.md:CharNgramsExtractor 1e07a7f -->
Класс для извлечения символьных N-грамм из текста - последовательностей из N символов, взятых окном по строке. Символьные N-граммы - стандартный признак стилометрии и атрибуции авторства (Stamatatos 2009), они могут заменять слова в роли единиц текста в мерах вроде дельты Барроуза.

Пробельные символы предварительно схлопываются в один пробел, знаки препинания сохраняются. При `within_words=True` N-граммы не пересекают границ слов: текст режется токенизатором на слова, знаки препинания отбрасываются, слова короче N N-грамм не дают.

Список N-грамм подается в [`delta`](../corpus/stylometry.md) как единицы текста вместо слов.

## Языковые крючки

Класс расширяет `CharNgramsExtractor` ядра [anyTS](https://sergeyshk.github.io/anyTS/extractors/char_ngrams/) крючком русского языка: его токенизатор слов по умолчанию для `within_words`, метод `tokenize(text)`, - токенизатор по умолчанию [`WordsExtractor`](words.md), функция `tokenize` библиотеки [razdel](https://github.com/natasha/razdel) с отделением приклеенных к словам тире реплик (`ruts.utils.iter_tokens`). Перед извлечением из текста снимаются знаки ударения и мягкие переносы (`ruts.utils.strip_marks`).

## Параметры

<!-- core: extractors/char_ngrams.md:CharNgramsExtractor-parameters 5154c6d -->
| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `n` | int | `2` | Длина N-граммы в символах |
| `lowercase` | bool | `False` | Конвертировать текст в нижний регистр |
| `within_words` | bool | `False` | Брать N-граммы только внутри слов |
| `tokenizer` | Pattern/Callable | `None` | Токенизатор слов для `within_words` или регулярное выражение; по умолчанию метод `tokenize` |

## Методы

### extract

<!-- core: extractors/char_ngrams.md:CharNgramsExtractor-extract a0b664c -->
Выполняет извлечение N-грамм из текста.

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `text` | str | `-` | Строка текста |

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

<!-- core: extractors/char_ngrams.md:CharNgramsExtractor-get_most_common 80bd729 -->
Возвращает топ-N-граммы текста списком пар (N-грамма, частота), начиная с самой частой.

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
