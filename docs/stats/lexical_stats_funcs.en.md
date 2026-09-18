# Statistic functions

## Dictionary frequency { #frequency }

The `coverage`, `mean_ipm`, `mean_ipm_content`, `mean_log_ipm`, `mean_log_ipm_content`, `mean_range` and `mean_dispersion` attributes of `LexicalStats` are computed from the [`FreqDict`](../datasets/freq2011.md) entries for the text lemmas (`entries`): the means are taken over words found in the dictionary, over all of them or only over content words. The mean frequency in ipm is sensitive to function words (и - 35,000 ipm, в - 31,000), so for comparing texts the log frequency or the mean over content words is more convenient; the latter corresponds to the FREQ2 feature of the 2023 Solovyev, Ivanov and Solnyshkina formula, whose values in the paper lie within 200-1000 ([`calc_sis_grade_freq`](readability_stats_funcs.md#calc_sis_grade_freq)).

## Surprisal and perplexity { #calc_surprisal }

!!! info ""
    **ruts.lexical_stats.calc_surprisal()**

Computation of the mean word surprisal by the unigram model of the frequency dictionary. Words outside the dictionary get the dictionary's minimum frequency (0.4 ipm), so surprisal is defined for all words; the more rare words in the text, the higher it is. The text perplexity `perplexity` is $2^{H}$.

Formula:

$$
H = -\frac{1}{N} \sum_{i=1}^{N} \log_2 \frac{\mathrm{ipm}(w_i)}{10^6}
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `lemmas` | list[str] | `-` | Word lemmas |
| `freq_dict` | FreqDict | `-` | Frequency dictionary |

## Frequency bands { #get_rank }

!!! info ""
    **ruts.lexical_stats.get_rank()**, **ruts.lexical_stats.load_top_lemmas()**

Getting the rank of a lemma by the embedded list of the 10,000 most frequent lemmas of the Leeds internet corpus (S. A. Sharoff, mirror [hingston/russian](https://github.com/hingston/russian), CC BY 2.5, the file `ruts/resources/sharoff_top10000.txt`), `None` for a lemma outside the list. Lemmas are lowercased with ё replaced by е; duplicates keep the smaller rank. `LexicalStats` derives from the ranks the shares of words from the top-1000, 2000, 5000 and 10000 (`FREQUENCY_BANDS`) and outside the top-10000 - a frequency band profile modeled on the Lexical Frequency Profile; the `band_coverage` method gives the shares for any bounds and over unique lemmas.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `lemma` | str | `-` | Lemma |

!!! example "Example"

    ``` python
    from ruts.lexical_stats import get_rank

    get_rank("и"), get_rank("кот"), get_rank("фелинолог")
    # (1, 2009, None)
    ```

## Lexical density { #lexical_density }

The `lexical_density` attribute of `LexicalStats` is the share of content words (nouns, adjectives, verbs, adverbs without pronominal and parenthetical words) among all words; a content word is defined by [`is_content_word`](cohesion_stats_funcs.md#is_content_word) for a string and by `CONTENT_UD_POS` for an annotated `Doc`.
