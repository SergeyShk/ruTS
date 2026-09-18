# Metric functions

## Classic nausea { #calc_classic_nausea }

!!! info ""
    **ruts.style_stats.calc_classic_nausea()**

Computation of classic nausea ([Advego](https://advego.com/text/seo/)) - the square root of the number of occurrences of the most frequent word. It characterizes the intrusiveness of one word regardless of text length and therefore grows with the text. The Advego norm is at most 7, in practice 1-5.

Formula:

$$
\sqrt{\max_k n_k}
$$

where $n_k$ is the number of occurrences of word $k$.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |

## Academic nausea { #calc_academic_nausea }

!!! info ""
    **ruts.style_stats.calc_academic_nausea()**

Computation of academic nausea ([Advego](https://advego.com/text/seo/)) - the share of occurrences of the most frequent words in the text, in percent. The exact Advego formula is not published; it is implemented as the total frequency of the `top_n` most frequent words divided by the number of words. The Advego norm is 5-15%.

Formula:

$$
100\times\frac{\sum_{k \in \textrm{top}_n} n_k}{N}
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `top_n` | int | `10` | Number of the most frequent words |

## Water content { #calc_water }

!!! info ""
    **ruts.style_stats.calc_water()**

Computation of water content ([Text.ru](https://text.ru/seo)) - the share of insignificant words in the text, in percent. Insignificant words are stop words: conjunctions, particles, prepositions, pronominal nouns, interjections, predicatives (нет, надо, можно), pronominal adjectives (этот, такой, который, весь), parentheticals (конечно, например), demonstrative (там, тогда) and interrogative (где, почему) adverbs by pymorphy3 tags (the [`is_stopword`](#is_stopword) function) or words from the given stop word list.

Text.ru norms: up to 15% - natural content, 15-30% - excessive, above 30% - high.

!!! note "Note"
    Advego's "water" is a different indicator with a norm of 55-75%; it is not implemented here.

Formula:

$$
100\times\frac{\textrm{Number of stop words}}{\textrm{Number of words}}
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `stopwords` | list[str] | `None` | Stop word list; if not given, pymorphy3 tags are used |

## Stop word { #is_stopword }

!!! info ""
    **ruts.style_stats.is_stopword()**

Checking whether a word is a stop word by part of speech. Stop words are words with the part of speech `CONJ`, `PRCL`, `PREP`, `NPRO`, `INTJ`, `PRED` or with the grammemes `Apro`, `Prnt`, `Dmns`, `Ques` by pymorphy3 tags; the sets are defined in `ruts.constants.STOPWORD_POS` and `ruts.constants.STOPWORD_GRAMMEMES`. The analysis results are cached.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |

## Spam score { #calc_spam }

!!! info ""
    **ruts.style_stats.calc_spam()**

Computation of the spam score ([Text.ru](https://text.ru/seo)) - the share of word repeats in the text, in percent. Every occurrence of a word except the first counts as a repeat, so the spam score equals $100\times(1 - \textrm{TTR})$. To compute by lemmas, extract words with lemmatization.

Text.ru norms: up to 30% - natural content, 30-60% - SEO-optimized text, above 60% - spammed text.

Formula:

$$
100\times\frac{N - V}{N}
$$

where $N$ is the number of words, $V$ the number of lexemes.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |

## Naturalness by Zipf's law { #calc_zipf_naturalness }

!!! info ""
    **ruts.style_stats.calc_zipf_naturalness()**

Computation of the naturalness of a text by [Zipf's law](https://en.wikipedia.org/wiki/Zipf's_law) (pr-cy, megaindex) - the agreement of the frequencies of the most frequent words with the ideal distribution $f_r = f_1 / r$, where $f_1$ is the frequency of the most frequent word and $r$ the rank of a word. Computed as $100\times(1 - \bar{d})$, where $\bar{d}$ is the mean relative deviation of the frequencies from the ideal ones over ranks 2 to $n = \min(\textrm{top}_n, V, f_1)$: rank 1 matches the ideal by construction, and at ranks above $f_1$ the ideal frequency is below one and the deviation of hapaxes grows without bound. Negative values are clipped to 0. The service norm is at least 50%.

!!! warning "Warning"
    If there are no ranks to compare (all words are hapaxes, a single lexeme, or `top_n` below 2), the function returns `nan`.

Formula:

$$
100\times\left(1-\frac{1}{n-1}\sum_{r=2}^{n}\frac{|f_r - f_1 / r|}{f_1 / r}\right)
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `top_n` | int | `10` | Number of the most frequent words |

## Keyword density { #calc_keyword_density }

!!! info ""
    **ruts.style_stats.calc_keyword_density()**

Computation of keyword density ([Text.ru](https://text.ru/seo), Turgenev) - the frequency of every keyword per 100 words of the text. A multi-word key phrase separated by spaces is searched as a sequence of words; phrase occurrences may overlap. Words are compared ignoring case; to compare by lemmas, extract words with lemmatization and pass lemmas.

Formula:

$$
100\times\frac{\textrm{Number of keyword occurrences}}{\textrm{Number of words}}
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `keywords` | list[str] | `-` | Keywords or phrases |

## Verbal nouns { #calc_verbal_nouns }

!!! info ""
    **ruts.style_stats.calc_verbal_nouns()**

Computation of the share of nouns (by the first pymorphy3 analysis) whose lemma ends with a suffix from `VERBAL_NOUN_SUFFIXES` (-ние, -нье, -тие, -тье, -ствие, -ция) or belongs to `VERBAL_NOUN_LEMMAS` (производство, руководство, строительство; the `ruts.utils.is_verbal_noun` function), in percent of all nouns; `nan` for a text without nouns. The suffix -ство is not in the list: it is mostly non-verbal (правительство, общество, средство). The heuristic also catches non-verbal words with the same suffixes (здание).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |

## Phrase density { #calc_phrase_density }

!!! info ""
    **ruts.style_stats.calc_phrase_density()**

Computation of the number of occurrences of phrases from a list per 100 words. Phrases are searched by lowercased word forms with ё replaced by е (`ruts.utils.find_phrases`): at every position the longest one is taken, matches do not overlap, empty phrases are skipped. `StyleStats` counts this way the compound prepositions from the `COMPOUND_PREPOSITIONS` list (в целях, в связи с, в рамках, за счет, путем, посредством) and the clichés from the `OFFICIALESE_CLICHES` list (на сегодняшний день, в настоящее время, имеет место, в кратчайшие сроки, должным образом) or from the `cliches` parameter; the lists contain only invariable phrases. The computation goes over unfiltered word forms (`forms`), since lemmatization or stop word filtering breaks the phrases apart.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `phrases` | list[str] | `-` | Phrases with words separated by spaces |

## Parentheticals { #calc_parentheticals }

!!! info ""
    **ruts.style_stats.calc_parentheticals()**, **ruts.style_stats.is_parenthetical()**

Computation of the number of parentheticals per 100 words: phrases from `PARENTHETICALS` (таким образом, как правило, в частности, кроме того) plus single words with the pymorphy3 grammeme `Prnt` (конечно, например, впрочем; the `is_parenthetical` function) outside the matched phrases.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
