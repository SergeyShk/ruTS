from collections.abc import Callable, Mapping, Sequence
from functools import cache, lru_cache
from itertools import islice

import anyts.corpus
import rumorph
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

from ..constants import RESOURCES_DIR
from ..datasets.freq2011 import CORPUS_SIZE, Entry, FreqDict
from ..exceptions import ParameterError
from ..lexical_stats import DICTIONARY_WORD, dictionary_lemma
from ..utils import normalize_yo, parse_all, parse_word, strip_marks

UNREACHABLE_FILES = {
    True: RESOURCES_DIR / "freqrnc2011_unreachable_forms.txt",
    False: RESOURCES_DIR / "freqrnc2011_unreachable_lemmas.txt",
}


def keyness(
    target: Sequence[str] | Sequence[Sequence[str]] | Mapping[str, int],
    reference: Sequence[str]
    | Sequence[Sequence[str]]
    | Mapping[str, float]
    | FreqDict
    | FrequencyReference,
    measure: str = "log_likelihood",
    min_freq: int = 1,
    positive: bool = True,
    top_n: int | None = None,
    n: int = 1,
    lemmatize: bool = True,
) -> list[Keyword]:
    """
    Поиск ключевых слов целевого корпуса относительно эталонного

    Описание:
        Для каждого слова считаются логарифм правдоподобия G² с p-значением
        (значимость различия) и Log Ratio (размер эффекта), как рекомендуют Gabrielatos
        и Hardie, и мера score, по которой список сортируется. Меры значимости (G²,
        хи-квадрат, BIC, ELL) отрицательны, если слово чаще в эталоне. Нулевая частота
        при расчете %DIFF, Log Ratio и отношения шансов заменяется на 0.5 (Hardie 2014)
        С эталоном FreqDict слова цели приводятся к леммам словаря, как в LexicalStats,
        числа и латиница отбрасываются, частота в эталоне - ipm, умноженная на объем
        корпуса словаря (92 млн); слово вне словаря получает его наименьшую частоту
        (min_ipm) и бывает только положительным ключевым словом. Статья, которой нет
        в цели и к которой не приводится ни одна форма ее лексем ruMorph, отрицательным
        ключевым словом не бывает

    Ссылки:
        https://ucrel.lancs.ac.uk/llwizard.html
        http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf
        http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/

    Аргументы:
        target (list[str]|list[list[str]]|dict[str, int]): Слова целевого корпуса -
            одного текста или списка текстов - или их частоты
        reference (list[str]|list[list[str]]|dict[str, float]|FreqDict|FrequencyReference):
            Слова эталонного корпуса - одного текста или списка текстов, их частоты,
            частотный словарь или эталон по частотам
        measure (str): Мера из anyts.constants.KEYNESS_MEASURES для score и сортировки
        min_freq (int): Минимальная частота ключевого слова в корпусе, где оно чаще
        positive (bool): Положительные ключевые слова - чаще в целевом корпусе (True),
            или отрицательные - чаще в эталонном (False)
        top_n (int): Количество ключевых слов; None - все
        n (int): Длина N-грамм слов, не пересекающих границ текстов; 1 - слова
        lemmatize (bool): Цель из словоформ, False - из лемм (только с FreqDict)

    Вывод:
        list[Keyword]: Ключевые слова по убыванию ключевости, при равенстве -
            по убыванию частоты и по алфавиту; слова с неопределенной мерой в конце

    Исключения:
        ParameterError: Если мера неизвестна, top_n или n меньше единицы или n больше 1
            при эталоне по частотам или частотном словаре
        SourceTypeError: Если слова не список строк
        SourceError: Если один из корпусов пуст
        DatasetNotFoundError: Если частотный словарь не загружен
    """
    if not isinstance(reference, FreqDict):
        return anyts.corpus.keyness(target, reference, measure, min_freq, positive, top_n, n)
    check_keyness_params(measure, min_freq, top_n, target, n, positive)
    if n > 1:
        raise ParameterError(
            f"Частотный словарь хранит слова: N-граммам нужны слова обоих корпусов, а не n={n}"
        )
    key = _dictionary_key(reference.entries, lemmatize)
    frequency = _frequency_reference(reference, key)
    if positive:
        return anyts.corpus.keyness(target, frequency, measure, min_freq, positive, top_n)
    found = anyts.corpus.keyness(target, frequency, measure, min_freq, positive)
    unreachable = _unreachable_entries(lemmatize)
    kept = (keyword for keyword in found if keyword.freq_target or keyword.word not in unreachable)
    return list(islice(kept, top_n))


def _dictionary_key(entries: Mapping[str, Entry], lemmatize: bool) -> Callable[[str], str]:
    """Статья словаря для слова цели: словоформы (lemmatize) или леммы"""

    @cache
    def key(word: str) -> str:
        lemma = parse_word(word).lemma if lemmatize else word
        return dictionary_lemma(word, lemma, entries)

    return key


def _frequency_reference(freq_dict: FreqDict, key: Callable[[str], str]) -> FrequencyReference:
    """Эталон частотного словаря, как его описывает докстринг keyness"""
    size = float(CORPUS_SIZE)
    return FrequencyReference(
        {lemma: ipm * size / 1e6 for lemma, ipm in freq_dict.word_ipm.items()},
        size,
        freq_dict.min_ipm * size / 1e6,
        key,
        _is_dictionary_word,
    )


@cache
def _unreachable_entries(lemmatize: bool) -> frozenset[str]:
    """Недостижимые статьи частотного словаря из ресурса (_find_unreachable_entries)"""
    path = UNREACHABLE_FILES[lemmatize]
    return frozenset(path.read_text(encoding="utf-8").split())


def _find_unreachable_entries(freq_dict: FreqDict, lemmatize: bool) -> list[str]:
    """
    Поиск статей частотного словаря, к которым не приводится ни одна форма их лексем

    Описание:
        Медленный: результат хранится в ресурсах UNREACHABLE_FILES. Сравнительная
        степень и краткие формы прилагательных на -щий не считаются (обязаннее,
        действующ); у слов вне словаря ruMorph (Михайлыч) формы угаданы

    Аргументы:
        freq_dict (FreqDict): Частотный словарь
        lemmatize (bool): Цель из словоформ, False - из лемм

    Вывод:
        list[str]: Недостижимые статьи по алфавиту
    """
    key = _dictionary_key(freq_dict.entries, lemmatize)

    def target(form: str) -> str:
        return form if lemmatize else parse_word(form).lemma

    def counted(form: rumorph.Analysis, entry: str) -> bool:
        return form.feats.get("Degree") != "Cmp" and not (
            form.feats.get("Variant") == "Short" and entry.endswith("щий")
        )

    def reachable(entry: str) -> bool:
        if key(target(entry)) == entry:
            return True
        forms = {
            form.word
            for analysis in parse_all(entry)
            for form in analysis.forms()
            if counted(form, entry)
        }
        return any(
            key(target(spelling)) == entry
            for form in forms
            for spelling in {form, normalize_yo(form)}
        )

    return sorted(entry for entry in freq_dict.entries if not reachable(entry))


@lru_cache(maxsize=131072)
def _is_dictionary_word(word: str) -> bool:
    """Состоит ли слово из букв словаря (DICTIONARY_WORD)"""
    return DICTIONARY_WORD.fullmatch(strip_marks(word)) is not None
