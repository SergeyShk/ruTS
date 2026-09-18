# Keywords

!!! info ""
    **ruts.corpus.keyness()**, **ruts.corpus.Keyword**

## Description

Keyword extraction (keyness) for a target corpus relative to a reference corpus: words that occur significantly more often in the target corpus than in the reference. A standard corpus linguistics tool for comparing genres, authors, translations and periods ([AntConc](https://www.laurenceanthony.net/software/antconc/), [Sketch Engine](https://www.sketchengine.eu/), quanteda `textstat_keyness`).

For every word two values are computed that [Gabrielatos and Marchi](http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf) and [Hardie](http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/) recommend reading together: the log-likelihood $G^2$ with its p-value (significance of the difference - whether it exists) and Log Ratio (effect size - how large it is). Additionally the chosen measure `score` is computed and used for sorting. Significance measures ($G^2$, chi-square, BIC, ELL) are signed: negative if the word is more frequent in the reference; effect measures (%DIFF, Log Ratio, odds ratio) are directional by construction.

The reference can be the [Lyashevskaya and Sharoff frequency dictionary](../datasets/freq2011.md) (`FreqDict`): the target words must then be lemmas (`WordsExtractor(use_lexemes=True)`), they are lowercased with ё replaced by е, and the reference frequency is ipm multiplied by the dictionary corpus size (92 million tokens). Words absent from the dictionary get zero reference frequency.

Words are compared as they are: case, lemmatization and stop words are up to [`WordsExtractor`](../extractors/words.md).

## Measures

For a word with frequency $a$ in a target corpus of size $c$ and frequency $b$ in a reference corpus of size $d$, $N = c + d$:

| Measure | Key | Formula | Description |
| :------ | :-- | :------ | :---------- |
| Log-likelihood | `log_likelihood` | $G^2 = 2\,(a \ln \frac{a}{E_1} + b \ln \frac{b}{E_2})$, $E_1 = \frac{c\,(a+b)}{N}$, $E_2 = \frac{d\,(a+b)}{N}$ | [Rayson and Garside (2000)](https://ucrel.lancs.ac.uk/llwizard.html); critical values `G2_CRITICAL_VALUES`: 3.84 for p < 0.05, 6.63 for p < 0.01, 10.83 for p < 0.001, 15.13 for p < 0.0001 |
| Chi-square | `chi2` | $\chi^2 = \frac{N\,\max(\lvert a(d-b) - b(c-a) \rvert - N/2,\ 0)^2}{(a+b)(N-a-b)\,c\,d}$ | with Yates's correction over the 2×2 contingency table; if the correction exceeds the difference, the statistic is zero |
| %DIFF | `diff` | $\frac{NF_a - NF_b}{NF_b} \cdot 100$ | [Gabrielatos and Marchi (2011)](http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf); $NF$ - frequency per million words |
| Log Ratio | `log_ratio` | $\log_2 \frac{NF_a}{NF_b}$ | [Hardie (2014)](http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/); one means the word is twice as frequent in the target corpus |
| BIC | `bic` | $\operatorname{sign}(G^2) \cdot (\lvert G^2 \rvert - \ln N)$ | Wilson (2013); in absolute value above 2 - positive evidence of a difference, above 6 - strong, above 10 - very strong; a negative value with $\lvert G^2 \rvert < \ln N$ means no evidence, not the opposite direction |
| ELL | `ell` | $\frac{G^2}{N \ln \min(E_1, E_2)}$ | Johnson, Culpeper and Rayson (2007); effect size for $G^2$ from 0 to 1, `nan` when the minimum expected frequency is below $e$ - then $\ln \min(E_1, E_2) < 1$ and the measure exceeds one |
| Odds ratio | `odds_ratio` | $\frac{a / (c - a)}{b / (d - b)}$ | one means equal odds; `inf` if the word fills the whole target corpus, 0 - the whole reference |

A zero frequency in one of the corpora is replaced with 0.5 when computing %DIFF, Log Ratio and the odds ratio (Hardie 2014). The p-value of $G^2$ is computed from the chi-square distribution with one degree of freedom (`calc_p_value`). The measures are available as functions `calc_log_likelihood`, `calc_chi2`, `calc_diff`, `calc_log_ratio`, `calc_bic`, `calc_ell`, `calc_odds_ratio` with arguments `(a, b, c, d)` from the module `ruts.corpus.keyness` (`from ruts.corpus.keyness import calc_log_likelihood`; the name `ruts.corpus.keyness` in the package is taken by the function of the same name, so importing the whole module does not work); names and descriptions are in `ruts.constants.KEYNESS_MEASURES`.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `target` | list[str]/dict[str, int] | `-` | Words of the target corpus or their frequencies |
| `reference` | list[str]/dict[str, float]/FreqDict | `-` | Words of the reference corpus, their frequencies or a frequency dictionary |
| `measure` | str | `log_likelihood` | Measure from `KEYNESS_MEASURES` for `score` and sorting |
| `min_freq` | int | `1` | Minimum frequency of a keyword in its own corpus |
| `positive` | bool | `True` | Positive keywords (more frequent in the target corpus) or negative (more frequent in the reference) |
| `top_n` | int | `None` | Number of keywords; `None` - all |

## Result

A list of `Keyword` named tuples in descending keyness order (ties broken by descending frequency and alphabetically, words with an undefined measure last); `pd.DataFrame(keywords)` gives a table.

| Field | Type | Description |
| :---: | :--: | :---------- |
| `word` | str | Word |
| `freq_target` | int | Frequency in the target corpus |
| `freq_reference` | float | Frequency in the reference corpus (fractional for a dictionary) |
| `ipm_target` | float | Frequency in the target corpus per million words |
| `ipm_reference` | float | Frequency in the reference corpus per million words |
| `g2` | float | Signed $G^2$ |
| `p_value` | float | p-value of $G^2$ |
| `log_ratio` | float | Log Ratio |
| `score` | float | Value of the chosen measure |

## Example

!!! example "Example"

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

    # Relative to the frequency dictionary (after FreqDict().download())
    from ruts.datasets import FreqDict

    [(k.word, round(k.log_ratio, 1)) for k in keyness(target, FreqDict(), min_freq=3, top_n=2)]
    # [('кот', 11.5), ('птица', 10.3)]
    ```
