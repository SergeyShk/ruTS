# Collocations

!!! info ""
    **ruts.corpus.collocations()**, **ruts.corpus.Collocation**

## Description

Collocation extraction - pairs of words that occur together more often than expected under independence: fixed expressions («точка зрения», «рабочий класс»), terminology, the combinatorics of a word. The association measures are the same as in [Sketch Engine](https://www.sketchengine.eu/wp-content/uploads/ske-statistics.pdf) and [`nltk.metrics.association`](https://www.nltk.org/api/nltk.metrics.association.html).

Word pairs are ordered, as in NLTK: the right word occurs no further than `window` words after the left one, every pair of positions is counted once; `window=1` gives bigrams. In the measure the pair frequency is divided by the window size (Church and Hanks 1990, likewise in NLTK), so that the expected frequency does not depend on the window and Dice and minimum sensitivity do not exceed one; the `freq_pair` field holds the undivided frequency. Hence with `window > 1` the scale of the Dice measures is shifted: a pair that always stands adjacent («точка зрения») gets logDice $14 - \log_2 window$ - 13 with window 2, 11.68 with window 5, not 14 as for bigrams and in Sketch Engine, where logDice is computed from the raw co-occurrence count; the maximum of 14 is reachable only for a pair occurring at every distance within the window. The `node` parameter keeps pairs with the given word on the left or the right - the combinatorics of one word.

Words are compared as they are: case, lemmatization and stop words are up to [`WordsExtractor`](../extractors/words.md); lemmas are usual for fixed expressions, word forms for grammatical constructions.

## Measures

For a pair with word frequencies $f_a$, $f_b$, pair frequency $f_{ab}$ and number of words $N$:

| Measure | Key | Formula | Description |
| :------ | :-- | :------ | :---------- |
| Mutual information | `mi` | $\log_2 \frac{f_{ab} N}{f_a f_b}$ | Church and Hanks (1990); overrates rare pairs |
| MI³ | `mi3` | $\log_2 \frac{f_{ab}^3 N}{f_a f_b}$ | Oakes (1998); favors frequent pairs |
| t-score | `t_score` | $\frac{f_{ab} - f_a f_b / N}{\sqrt{f_{ab}}}$ | Church et al. (1991); favors frequent pairs |
| Dice coefficient | `dice` | $\frac{2 f_{ab}}{f_a + f_b}$ | independent of text size |
| logDice | `logdice` | $14 + \log_2 \frac{2 f_{ab}}{f_a + f_b}$ | [Rychlý (2008)](https://www.sketchengine.eu/glossary/logdice/); independent of text size, maximum 14 (for a window - $14 - \log_2 window$), below zero - weak association; the default measure, as in Sketch Engine |
| Log-likelihood | `log_likelihood` | $G^2 = 2 \sum O \ln \frac{O}{E}$ | Dunning (1993); over the 2×2 contingency table, `nan` if one of the words fills the whole text |
| NPMI | `npmi` | $\frac{MI}{-\log_2 (f_{ab} / N)}$ | Bouma (2009); from −1 to 1, one means the words occur only together |
| Minimum sensitivity | `min_sensitivity` | $\min(\frac{f_{ab}}{f_a}, \frac{f_{ab}}{f_b})$ | Pedersen (1998); from 0 to 1 |

The measures are available as functions `calc_mi`, `calc_mi3`, `calc_t_score`, `calc_dice`, `calc_logdice`, `calc_log_likelihood`, `calc_npmi`, `calc_min_sensitivity` with arguments `(freq_a, freq_b, freq_ab, n)` from the module `ruts.corpus.collocations` (`from ruts.corpus.collocations import calc_logdice`); names and descriptions are in `ruts.constants.COLLOCATION_MEASURES`.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `words` | list[str] | `-` | Words of the text in order |
| `window` | int | `5` | Maximum distance between the words of a pair |
| `measure` | str | `logdice` | Measure from `COLLOCATION_MEASURES` |
| `min_freq` | int | `2` | Minimum pair frequency |
| `node` | str | `None` | The word whose combinatorics is wanted; `None` - all pairs |
| `top_n` | int | `None` | Number of collocations; `None` - all |

## Result

A list of `Collocation` named tuples in descending order of the measure and pair frequency (ties broken alphabetically); `pd.DataFrame(found)` gives a table.

| Field | Type | Description |
| :---: | :--: | :---------- |
| `left` | str | Left word |
| `right` | str | Right word, occurring within the window after the left one |
| `freq_left` | int | Frequency of the left word |
| `freq_right` | int | Frequency of the right word |
| `freq_pair` | int | Co-occurrence frequency |
| `score` | float | Value of the chosen measure |

## Example

!!! example "Example"

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
