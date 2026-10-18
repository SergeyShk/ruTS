# Metric functions

The norms of the services for the metrics are given in the [service norms](style_stats.md#norms) section.

## Classic nausea { #calc_classic_nausea }

!!! info ""
    **ruts.style_stats.calc_classic_nausea()**

--8<-- "stats/style_stats_funcs.md:calc_classic_nausea"

## Academic nausea { #calc_academic_nausea }

!!! info ""
    **ruts.style_stats.calc_academic_nausea()**

Computation of the academic nausea (Advego): the share of the occurrences of the most frequent significant words ([`find_nausea_words`](#find_nausea_words)) among all the words, in percent.

Formula:

$$
100 \cdot \frac{\sum_{w \in \textrm{top}_n} f_w}{\textrm{Number of words}}
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `top_n` | int | `10` | Number of the most frequent words |
| `stopwords` | list[str] | `None` | Stop words; without them [`is_stopword`](#is_stopword) decides |

## Academic nausea words { #find_nausea_words }

!!! info ""
    **ruts.style_stats.find_nausea_words()**

The `top_n` most frequent words without the stop words, with their occurrences, the most frequent first. A stop word is a word of `stopwords`, compared ignoring case and the letter ё, or, without the list, a word of [`is_stopword`](#is_stopword).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `top_n` | int | `10` | Number of the most frequent words |
| `stopwords` | list[str] | `None` | Stop words |

!!! example "Example"

    ``` python
    from ruts.style_stats import find_nausea_words

    find_nausea_words(["кот", "и", "кот", "и", "пес"], top_n=1)
    # {'кот': 2}
    ```

## Water content { #calc_water }

!!! info ""
    **ruts.style_stats.calc_water()**

Computation of the water content (Text.ru): the share of the words without content, in percent - the words of `stopwords`, compared ignoring case and the letter ё, or, without the list, the words of [`is_water_word`](#is_water_word). Advego's "water" is a different indicator; it is not implemented here.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `stopwords` | list[str] | `None` | Water words |

## Water word { #is_water_word }

!!! info ""
    **ruts.style_stats.is_water_word()**

Checking whether a word is "water" by part of speech - for the [water content](#calc_water) and the `stopwords` layer of the highlighting: conjunctions, particles, pronominal nouns and interjections by pymorphy3 tags (`CONJ`, `PRCL`, `NPRO`, `INTJ`; the `ruts.constants.WATER_POS` set). pymorphy3 tags the parenthetical words конечно and например as conjunctions, so they are water too. Prepositions, pronominal adjectives and predicatives, unlike in [`is_stopword`](#is_stopword), are not water.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |

## Stop word { #is_stopword }

!!! info ""
    **ruts.style_stats.is_stopword()**

Checking whether a word is a stop word by part of speech - insignificant for the [academic nausea](#calc_academic_nausea): conjunctions, particles, prepositions, pronominal nouns, interjections and predicatives (`CONJ`, `PRCL`, `PREP`, `NPRO`, `INTJ`, `PRED`) and the words with the grammemes `Apro`, `Prnt`, `Dmns`, `Ques` - pronominal adjectives, parenthetical words, demonstrative and interrogative adverbs - by pymorphy3 tags; the sets are `ruts.constants.STOPWORD_POS` and `ruts.constants.STOPWORD_GRAMMEMES`.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |

## Spam score { #calc_spam }

!!! info ""
    **ruts.style_stats.calc_spam()**

--8<-- "stats/style_stats_funcs.md:calc_spam"

## Naturalness by Zipf's law { #calc_zipf_naturalness }

!!! info ""
    **ruts.style_stats.calc_zipf_naturalness()**

Computation of the naturalness by [Zipf's law](https://en.wikipedia.org/wiki/Zipf's_law) (pr-cy, megaindex): the agreement of the frequencies of the most frequent words with the ideal distribution $f_r = f_1 / r$, where $f_1$ is the frequency of the most frequent word and $r$ the rank. The ranks run from 2 to $R = \min(\textrm{top}_n, V, f_1)$, where $V$ is the number of lexemes; negative values are cut to 0, and without ranks to compare - all the words hapaxes, one lexeme or `top_n` below 2 - the value is `nan`.

Formula:

$$
100 \cdot \left(1 - \frac{1}{R - 1} \sum_{r=2}^{R} \frac{|r \cdot f_r - f_1|}{f_1}\right)
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `top_n` | int | `10` | Number of the most frequent words |

## Keyword density { #calc_keyword_density }

!!! info ""
    **ruts.style_stats.calc_keyword_density()**

--8<-- "stats/style_stats_funcs.md:calc_keyword_density"

## Verbal nouns { #calc_verbal_nouns }

!!! info ""
    **ruts.style_stats.calc_verbal_nouns()**, **ruts.style_stats.find_verbal_nouns()**

Computation of the share of the verbal nouns among the nouns (by the first pymorphy3 analysis), in percent; `nan` for a text without nouns. A noun is verbal when its lemma ends with a suffix of `VERBAL_NOUN_SUFFIXES` (-ние, -нье, -тие, -тье, -ствие, -ция) or belongs to `VERBAL_NOUN_LEMMAS` (производство, руководство, строительство) - the `ruts.utils.is_verbal_noun` function; the heuristic also catches non-verbal words with the same suffixes (здание). The `find_verbal_nouns` function returns the bounds of the words found as slices of the list.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |

## Phrase density { #calc_phrase_density }

!!! info ""
    **ruts.style_stats.calc_phrase_density()**, **ruts.style_stats.expand_phrases()**

Computation of the occurrences of the phrases of a list per 100 words. The phrases are compared ignoring case and the letter ё, and a phrase starting with an infinitive, alone or after «не», is found in any form of its verb, participles and gerunds included («имело место», «доведено до сведения»): the `expand_phrases` function adds these variants from the text, each with its phrase. So `StyleStats` counts over the word forms (`forms`) the compound prepositions of `COMPOUND_PREPOSITIONS` (в целях, в связи с, в рамках, за счет) and the cliches of `OFFICIALESE_CLICHES` (на сегодняшний день, в настоящее время, иметь место) or of the `cliches` parameter.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `phrases` | list[str] | `-` | Phrases with words separated by spaces |

## Parentheticals { #calc_parentheticals }

!!! info ""
    **ruts.style_stats.calc_parentheticals()**, **ruts.style_stats.find_parentheticals()**, **ruts.style_stats.is_parenthetical()**

Computation of the number of parenthetical words per 100 words: the phrases of `PARENTHETICALS` (таким образом, как правило, в частности, кроме того) and, outside them, the single words with the pymorphy3 grammeme `Prnt` (конечно, например, впрочем; the `is_parenthetical` function). The `find_parentheticals` function returns the bounds of the words and phrases found as slices of the list.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
