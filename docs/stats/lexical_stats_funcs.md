# Функции вычисления статистик

## Частотность по словарю { #frequency }

Атрибуты `coverage`, `mean_ipm`, `mean_ipm_content`, `mean_log_ipm`, `mean_log_ipm_content`, `mean_range` и `mean_dispersion` класса `LexicalStats` считаются по статьям [`FreqDict`](../datasets/freq2011.md) для ключей слов (`keys`, `entries`): средние берутся по словам, найденным в словаре, по всем или только по знаменательным. Средняя частотность в ipm чувствительна к служебным словам (и - 35 000 ipm, в - 31 000), поэтому для сравнения текстов удобнее логарифм частотности или средняя по знаменательным словам; последняя соответствует признаку FREQ2 формулы Соловьёва, Иванова, Солнышкиной 2023 года, значения которого в статье лежат в пределах 200-1000 ([`calc_sis_grade_freq`](readability_stats_funcs.md#calc_sis_grade_freq)).

## Сюрпризал и перплексия { #calc_surprisal }

!!! info ""
    **ruts.lexical_stats.calc_surprisal()**

<!-- core: stats/lexical_stats.md:calc_surprisal 2e9fd1c -->
Средний сюрпризал слов по униграммной модели частотного словаря в битах; слово вне словаря получает его наименьшую частоту `min_ipm`. Перплексия - 2 в его степени.

Формула:

$$
\frac{1}{N} \sum_{w} -\log_2 \frac{\max(\textrm{ipm}_w, \textrm{min\_ipm})}{10^6}
$$

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `lemmas` | list[str] | `-` | Ключи слов в словаре |
| `freq_dict` | FrequencyDictionary | `-` | Частотный словарь |

Без слов результат - `nan`; ключи, которые не список строк, и словарь без `ipm` и `min_ipm` дают `SourceTypeError`, наименьшая частота не больше нуля - `ParameterError`.

В ruTS словарь - [`FreqDict`](../datasets/freq2011.md) с наименьшей частотой 0.4 ipm: словарь другого класса дает `SourceTypeError`.

## Частотные полосы { #get_rank }

!!! info ""
    **ruts.lexical_stats.get_rank()**, **ruts.lexical_stats.load_top_lemmas()**

Получение ранга леммы по вшитому списку 10 000 самых частых лемм интернет-корпуса Лидского университета (С. А. Шаров, зеркало [hingston/russian](https://github.com/hingston/russian), CC BY 2.5, файл `ruts/resources/sharoff_top10000.txt`), `None` для леммы вне списка. Леммы приводятся к нижнему регистру без буквы ё, у дублей остается меньший ранг. Класс `LexicalStats` считает по рангам доли слов из топ-1000, 2000, 5000 и 10000 (`FREQUENCY_BANDS`) и вне топ-10000 - профиль частотных полос по образцу Lexical Frequency Profile; метод `band_coverage` дает доли по любым границам и по уникальным леммам.

Параметры:

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `lemma` | str | `-` | Лемма |

!!! example "Пример"

    ``` python
    from ruts.lexical_stats import get_rank

    get_rank("и"), get_rank("кот"), get_rank("фелинолог")
    # (1, 2009, None)
    ```

## Лексическая плотность { #lexical_density }

Атрибут `lexical_density` класса `LexicalStats` - доля знаменательных слов (существительные, прилагательные, глаголы, наречия без местоименных и вводных слов) среди всех слов; определение знаменательного слова - [`is_content_word`](cohesion_stats_funcs.md#is_content_word) для строки и `CONTENT_UD_POS` для `Doc` с разметкой.
