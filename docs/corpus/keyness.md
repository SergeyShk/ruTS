# Ключевые слова

!!! info ""
    **ruts.corpus.keyness()**, **ruts.corpus.Keyword**

## Описание

Поиск ключевых слов (keyness) целевого корпуса относительно эталонного: слова, которые в целевом корпусе встречаются значимо чаще, чем в эталонном. Стандартный инструмент корпусной лингвистики для сравнения жанров, авторов, переводов и периодов ([AntConc](https://www.laurenceanthony.net/software/antconc/), [Sketch Engine](https://www.sketchengine.eu/), quanteda `textstat_keyness`).

Для каждого слова считаются две величины, которые [Gabrielatos и Marchi](http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf) и [Hardie](http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/) рекомендуют смотреть вместе: логарифм правдоподобия $G^2$ с p-значением (значимость различия - есть ли оно) и Log Ratio (размер эффекта - насколько велико). Дополнительно считается выбранная мера `score`, по которой список сортируется. Меры значимости ($G^2$, хи-квадрат, BIC, ELL) получают знак: отрицательный, если слово чаще в эталоне; меры эффекта (%DIFF, Log Ratio, отношение шансов) направленные по построению.

Эталоном может быть [частотный словарь Ляшевской и Шарова](../datasets/freq2011.md) (`FreqDict`): целевые слова тогда должны быть леммами (`WordsExtractor(use_lexemes=True)`), они приводятся к нижнему регистру без буквы ё, а частота в эталоне - ipm, умноженная на объем корпуса словаря (92 млн словоупотреблений). Слова, которых в словаре нет, получают нулевую частоту в эталоне.

Слова сравниваются как есть: регистр, лемматизация и стоп-слова - на стороне [`WordsExtractor`](../extractors/words.md).

## Меры

Для слова с частотой $a$ в целевом корпусе объемом $c$ и частотой $b$ в эталонном корпусе объемом $d$, $N = c + d$:

| Мера | Ключ | Формула | Описание |
| :--- | :--- | :------ | :------- |
| Логарифм правдоподобия | `log_likelihood` | $G^2 = 2\,(a \ln \frac{a}{E_1} + b \ln \frac{b}{E_2})$, $E_1 = \frac{c\,(a+b)}{N}$, $E_2 = \frac{d\,(a+b)}{N}$ | [Rayson и Garside (2000)](https://ucrel.lancs.ac.uk/llwizard.html); критические значения `G2_CRITICAL_VALUES`: 3.84 для p < 0.05, 6.63 для p < 0.01, 10.83 для p < 0.001, 15.13 для p < 0.0001 |
| Хи-квадрат | `chi2` | $\chi^2 = \frac{N\,\max(\lvert a(d-b) - b(c-a) \rvert - N/2,\ 0)^2}{(a+b)(N-a-b)\,c\,d}$ | с поправкой Йейтса по таблице сопряженности 2×2; если поправка больше разности, статистика равна нулю |
| %DIFF | `diff` | $\frac{NF_a - NF_b}{NF_b} \cdot 100$ | [Gabrielatos и Marchi (2011)](http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf); $NF$ - частота на миллион слов |
| Log Ratio | `log_ratio` | $\log_2 \frac{NF_a}{NF_b}$ | [Hardie (2014)](http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/); единица - слово вдвое чаще в целевом корпусе |
| BIC | `bic` | $\operatorname{sign}(G^2) \cdot (\lvert G^2 \rvert - \ln N)$ | Wilson (2013); по модулю выше 2 - положительное свидетельство различия, выше 6 - сильное, выше 10 - очень сильное; отрицательное значение при $\lvert G^2 \rvert < \ln N$ означает отсутствие свидетельства, а не обратное направление |
| ELL | `ell` | $\frac{G^2}{N \ln \min(E_1, E_2)}$ | Johnson, Culpeper и Rayson (2007); размер эффекта для $G^2$ от 0 до 1, `nan` при минимальной ожидаемой частоте меньше $e$ - тогда $\ln \min(E_1, E_2) < 1$ и мера выходит за единицу |
| Отношение шансов | `odds_ratio` | $\frac{a / (c - a)}{b / (d - b)}$ | единица - шансы равны; `inf`, если слово занимает весь целевой корпус, 0 - если весь эталонный |

Нулевая частота в одном из корпусов при расчете %DIFF, Log Ratio и отношения шансов заменяется на 0.5 (Hardie 2014). p-значение $G^2$ считается по распределению хи-квадрат с одной степенью свободы (`calc_p_value`). Меры доступны как функции `calc_log_likelihood`, `calc_chi2`, `calc_diff`, `calc_log_ratio`, `calc_bic`, `calc_ell`, `calc_odds_ratio` с аргументами `(a, b, c, d)` из модуля `ruts.corpus.keyness` (`from ruts.corpus.keyness import calc_log_likelihood`; имя `ruts.corpus.keyness` в пакете занято одноименной функцией, поэтому импорт модуля целиком не работает); названия и описания - в `ruts.constants.KEYNESS_MEASURES`.

## Параметры

| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `target` | list[str]/dict[str, int] | `-` | Слова целевого корпуса или их частоты |
| `reference` | list[str]/dict[str, float]/FreqDict | `-` | Слова эталонного корпуса, их частоты или частотный словарь |
| `measure` | str | `log_likelihood` | Мера из `KEYNESS_MEASURES` для `score` и сортировки |
| `min_freq` | int | `1` | Минимальная частота ключевого слова в своем корпусе |
| `positive` | bool | `True` | Положительные ключевые слова (чаще в целевом корпусе) или отрицательные (чаще в эталонном) |
| `top_n` | int | `None` | Количество ключевых слов; `None` - все |

## Результат

Список именованных кортежей `Keyword` по убыванию ключевости (при равенстве - по убыванию частоты и по алфавиту, слова с неопределенной мерой в конце); `pd.DataFrame(keywords)` дает таблицу.

| Поле | Тип | Описание |
| :--: | :-: | :------- |
| `word` | str | Слово |
| `freq_target` | int | Частота в целевом корпусе |
| `freq_reference` | float | Частота в эталонном корпусе (по словарю - дробная) |
| `ipm_target` | float | Частота в целевом корпусе на миллион слов |
| `ipm_reference` | float | Частота в эталонном корпусе на миллион слов |
| `g2` | float | $G^2$ со знаком направления |
| `p_value` | float | p-значение $G^2$ |
| `log_ratio` | float | Log Ratio |
| `score` | float | Значение выбранной меры |

## Пример

!!! example "Пример"

    ``` python
    from ruts import WordsExtractor
    from ruts.corpus import keyness

    we = WordsExtractor(use_lexemes=True, lowercase=True)
    target = we.extract(
        "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне. "
        "Завтра кот снова будет сидеть на окне и смотреть на птиц."
    )
    reference = we.extract(
        "Собака лежала на полу и дремала. Потом собака ела и снова дремала. Завтра собака будет гулять."
    )

    keyness(target, reference, top_n=1)
    # [Keyword(word='кот', freq_target=3, freq_reference=0, ipm_target=115384.61538461539,
    #  ipm_reference=0.0, g2=2.8774384815713177, p_value=0.08982881315854577,
    #  log_ratio=1.8845227825800641, score=2.8774384815713177)]

    [(k.word, round(k.g2, 2)) for k in keyness(target, reference, positive=False, top_n=2)]
    # [('собака', -5.79), ('дремать', -3.86)]

    # Относительно частотного словаря (после FreqDict().download())
    from ruts.datasets import FreqDict

    [(k.word, round(k.log_ratio, 1)) for k in keyness(target, FreqDict(), min_freq=3, top_n=2)]
    # [('кот', 11.5), ('птица', 10.3)]
    ```
