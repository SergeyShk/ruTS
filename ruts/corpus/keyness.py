from collections.abc import Callable, Mapping, Sequence
from functools import cache
from itertools import islice

import anyts.corpus
from anyts.corpus.keyness import (
    FrequencyReference as FrequencyReference,
    Keyword as Keyword,
    calc_bic as calc_bic,
    calc_chi2 as calc_chi2,
    calc_diff as calc_diff,
    calc_ell as calc_ell,
    calc_log_likelihood as calc_log_likelihood,
    calc_log_ratio as calc_log_ratio,
    calc_odds_ratio as calc_odds_ratio,
    calc_p_value as calc_p_value,
    check_keyness_params as check_keyness_params,
)

from ..datasets.freq2011 import CORPUS_SIZE, Entry, FreqDict
from ..lexical_stats import DICTIONARY_WORD, dictionary_lemma
from ..utils import normalize_yo, parse_all, parse_word


def keyness(
    target: Sequence[str] | Mapping[str, int],
    reference: Sequence[str] | Mapping[str, float] | FreqDict | FrequencyReference,
    measure: str = "log_likelihood",
    min_freq: int = 1,
    positive: bool = True,
    top_n: int | None = None,
    lemmatize: bool = True,
) -> list[Keyword]:
    """
    Поиск ключевых слов целевого корпуса относительно эталонного

    Описание:
        Слова сравниваются по частотам в двух корпусах: для каждого слова считаются
        логарифм правдоподобия G² с p-значением (значимость различия) и Log Ratio
        (размер эффекта), как рекомендуют Gabrielatos и Hardie, а также выбранная
        мера score, по которой список сортируется. Меры значимости (G², хи-квадрат,
        BIC, ELL) получают знак: отрицательный, если слово чаще в эталоне
        Эталоном может быть частотный словарь FreqDict: целевые словоформы (с
        lemmatize=False - леммы) приводятся к леммам словаря, как в LexicalStats,
        числа и латиница отбрасываются, частота в эталоне - ipm, умноженная
        на объем корпуса словаря (92 млн); слово вне словаря получает его
        наименьшую частоту (min_ipm) и бывает только положительным ключевым словом;
        отрицательным ключевым словом бывает только статья, к которой приводится
        хотя бы одна форма ее лексем pymorphy3: статьи «его», «во», «со», к которым
        не приводится ни одно слово (это формы лемм «он», «в», «с»), не выдаются
        Нулевая частота в одном из корпусов при расчете %DIFF, Log Ratio и отношения
        шансов заменяется на 0.5 (Hardie 2014)
        Положительные ключевые слова чаще в целевом корпусе, отрицательные -
        в эталонном; min_freq - наименьшая частота слова в том корпусе, где оно чаще

    Ссылки:
        https://ucrel.lancs.ac.uk/llwizard.html
        http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf
        http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/

    Аргументы:
        target (list[str]|dict[str, int]): Слова целевого корпуса или их частоты
        reference (list[str]|dict[str, float]|FreqDict|FrequencyReference): Слова
            эталонного корпуса, их частоты, частотный словарь или эталон по частотам
        measure (str): Мера из anyts.constants.KEYNESS_MEASURES для score и сортировки
        min_freq (int): Минимальная частота ключевого слова в своем корпусе
        positive (bool): Положительные ключевые слова (True) или отрицательные (False)
        top_n (int): Количество ключевых слов; None - все
        lemmatize (bool): Цель из словоформ, False - из лемм (только с FreqDict)

    Вывод:
        list[Keyword]: Ключевые слова по убыванию ключевости, при равенстве -
            по убыванию частоты и по алфавиту; слова с неопределенной мерой в конце

    Исключения:
        ParameterError: Если мера неизвестна или top_n меньше единицы
        SourceTypeError: Если слова не список строк
        SourceError: Если один из корпусов пуст
        DatasetNotFoundError: Если частотный словарь не загружен
    """
    if not isinstance(reference, FreqDict):
        return anyts.corpus.keyness(target, reference, measure, min_freq, positive, top_n)
    check_keyness_params(measure, min_freq, top_n, target)
    key = _dictionary_key(reference.entries, lemmatize)
    frequency = _frequency_reference(reference, key)
    if positive:
        return anyts.corpus.keyness(target, frequency, measure, min_freq, positive, top_n)
    found = anyts.corpus.keyness(target, frequency, measure, min_freq, positive)
    reachable = _reachable(key, lemmatize)
    return list(islice((keyword for keyword in found if reachable(keyword.word)), top_n))


def _dictionary_key(entries: Mapping[str, Entry], lemmatize: bool) -> Callable[[str], str]:
    """Статья словаря для слова цели: словоформы (lemmatize) или леммы"""

    @cache
    def key(word: str) -> str:
        lemma = parse_word(word).normal_form if lemmatize else word
        return dictionary_lemma(word, lemma, entries)

    return key


def _frequency_reference(freq_dict: FreqDict, key: Callable[[str], str]) -> FrequencyReference:
    """Эталон частотного словаря, как его описывает докстринг keyness"""
    size = float(CORPUS_SIZE)
    return FrequencyReference(
        {lemma: entry.ipm * size / 1e6 for lemma, entry in freq_dict.entries.items()},
        size,
        freq_dict.min_ipm * size / 1e6,
        key,
        _is_dictionary_word,
    )


def _reachable(key: Callable[[str], str], lemmatize: bool) -> Callable[[str], bool]:
    """Приводится ли к статье словаря хотя бы одна форма ее лексем (через лемму без lemmatize)"""

    def target(form: str) -> str:
        return form if lemmatize else parse_word(form).normal_form

    def reachable(entry: str) -> bool:
        if key(target(entry)) == entry:
            return True
        forms = {form.word for parse in parse_all(entry) for form in parse.lexeme}
        return any(
            key(target(spelling)) == entry
            for form in forms
            for spelling in {form, normalize_yo(form)}
        )

    return reachable


def _is_dictionary_word(word: str) -> bool:
    """Состоит ли слово из букв словаря (DICTIONARY_WORD)"""
    return DICTIONARY_WORD.fullmatch(word) is not None
