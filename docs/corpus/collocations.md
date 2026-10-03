# Коллокации

!!! info ""
    **ruts.corpus.collocations()**, **ruts.corpus.Collocation**

## Описание

<!-- core: corpus/collocations.md:collocations 90cd7f5 -->
Поиск коллокаций - пар слов, которые встречаются вместе чаще, чем дала бы независимость: устойчивые сочетания, терминология, сочетаемость слова. Меры ассоциации те же, что в [Sketch Engine](https://www.sketchengine.eu/wp-content/uploads/ske-statistics.pdf) и [`nltk.metrics.association`](https://www.nltk.org/api/nltk.metrics.association.html).

Пары слов упорядочены, как в NLTK: правое слово встречается не дальше `window` слов после левого, каждая пара позиций учитывается один раз; `window=1` дает биграммы. В мере частота пары делится на размер окна (Church и Hanks 1990, так же в NLTK), чтобы ожидаемая частота не зависела от окна, а Dice и минимальная чувствительность не превышали единицы; поле `freq_pair` хранит частоту без деления. Поэтому при `window > 1` шкала Dice-мер сдвигается: пара, всегда стоящая рядом, получает logDice $14 - \log_2 window$ (13 при окне 2), а не 14, как в Sketch Engine, где берется сырое число совстречаемостей; 14 достигает только пара, встречающаяся на каждом расстоянии в окне. Параметр `node` оставляет пары с заданным словом слева или справа - сочетаемость одного слова.

Слова сравниваются как есть: регистр, лемматизация и стоп-слова - на стороне экстрактора слов; для устойчивых сочетаний подходят леммы, для грамматических конструкций - словоформы.

Модуль `ruts.corpus.collocations` реэкспортирует функцию и меры ядра [anyTS](https://sergeyshk.github.io/anyTS/corpus/collocations/) (`from ruts.corpus.collocations import calc_logdice`). Слова извлекает [`WordsExtractor`](../extractors/words.md); для русских устойчивых сочетаний вроде «точка зрения» или «рабочий класс» берут его леммы (`use_lexemes=True`).

## Меры

<!-- core: corpus/collocations.md:collocations-measures fb0a1f7 -->
Для пары слов с частотами $f_a$ и $f_b$, частотой пары $f_{ab}$ и числом слов $N$:

| Мера | Ключ | Формула | Описание |
| :--- | :--- | :------ | :------- |
| Взаимная информация | `mi` | $\log_2 \frac{f_{ab} N}{f_a f_b}$ | Church и Hanks (1990); завышает редкие пары |
| MI³ | `mi3` | $\log_2 \frac{f_{ab}^3 N}{f_a f_b}$ | Oakes (1998); отдает предпочтение частым парам |
| t-критерий | `t_score` | $\frac{f_{ab} - f_a f_b / N}{\sqrt{f_{ab}}}$ | Church и др. (1991); отдает предпочтение частым парам |
| Коэффициент Дайса | `dice` | $\frac{2 f_{ab}}{f_a + f_b}$ | не зависит от размера текста |
| logDice | `logdice` | $14 + \log_2 \frac{2 f_{ab}}{f_a + f_b}$ | [Rychlý (2008)](https://www.sketchengine.eu/glossary/logdice/); не зависит от размера текста, максимум 14, ниже нуля - слабая связь; мера по умолчанию, как в Sketch Engine |
| Логарифм правдоподобия | `log_likelihood` | $G^2 = 2 \sum O \ln \frac{O}{E}$ | Dunning (1993); по таблице сопряженности 2×2, `nan`, если одно из слов занимает весь текст |
| NPMI | `npmi` | $\frac{MI}{-\log_2 (f_{ab} / N)}$ | Bouma (2009); от −1 до 1, единица - слова встречаются только вместе |
| Минимальная чувствительность | `min_sensitivity` | $\min(\frac{f_{ab}}{f_a}, \frac{f_{ab}}{f_b})$ | Pedersen (1998); от 0 до 1 |

Меры доступны как функции `calc_mi`, `calc_mi3`, `calc_t_score`, `calc_dice`, `calc_logdice`, `calc_log_likelihood`, `calc_npmi` и `calc_min_sensitivity` с аргументами `(freq_a, freq_b, freq_ab, n)` из модуля `anyts.corpus.collocations`; их названия и описания - в `anyts.constants.COLLOCATION_MEASURES`.

## Параметры

<!-- core: corpus/collocations.md:collocations-parameters 459ab39 -->
| Параметр | Тип | По умолчанию | Описание |
| :------: | :-: | :----------: | :------: |
| `words` | list[str] | `-` | Слова текста по порядку |
| `window` | int | `5` | Наибольшее расстояние между словами пары |
| `measure` | str | `logdice` | Мера из `anyts.constants.COLLOCATION_MEASURES` |
| `min_freq` | int | `2` | Минимальная частота пары |
| `node` | str | `None` | Слово, сочетаемость которого нужна; `None` - все пары |
| `top_n` | int | `None` | Количество коллокаций; `None` - все |

## Результат

<!-- core: corpus/collocations.md:Collocation 77925e6 -->
Список именованных кортежей `Collocation` по убыванию меры и частоты пары (при равенстве - по алфавиту); `pd.DataFrame(found)` дает таблицу.

| Поле | Тип | Описание |
| :--: | :-: | :------- |
| `left` | str | Левое слово |
| `right` | str | Правое слово, встречается в окне после левого |
| `freq_left` | int | Частота левого слова |
| `freq_right` | int | Частота правого слова |
| `freq_pair` | int | Частота совместной встречаемости |
| `score` | float | Значение выбранной меры |

## Пример

!!! example "Пример"

    ``` python
    from ruts import WordsExtractor
    from ruts.corpus import collocations

    words = WordsExtractor(use_lexemes=True, lowercase=True).extract(
        "Кот сидел на окне и смотрел на птиц. Птицы улетели, и кот уснул на окне. "
        "Завтра кот снова будет сидеть на окне и смотреть на птиц."
    )

    collocations(words, window=2, top_n=1)
    # [Collocation(left='птица', right='улететь', freq_left=3, freq_right=1, freq_pair=2, score=13.0)]

    [
        (c.left, c.right, round(c.score, 2))
        for c in collocations(words, window=1, node="кот", min_freq=1, measure="mi")[:2]
    ]
    # [('завтра', 'кот', 3.12), ('кот', 'снова', 3.12)]
    ```
