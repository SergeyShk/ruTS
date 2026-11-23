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
    check_keyness_params as core_check_keyness_params,
)

from ..constants import RESOURCES_DIR
from ..datasets.freq2011 import CORPUS_SIZE, Entry, FreqDict
from ..exceptions import ParameterError
from ..lexical_stats import DICTIONARY_WORD, dictionary_lemma
from ..utils import (
    analyze_text,
    core_messages,
    get_morph_analyzer,
    normalize_yo,
    parse_all,
    parse_word,
    strip_marks,
    with_core_messages,
)

check_keyness_params = with_core_messages(core_check_keyness_params)
# ruMorph делит предложение на части по 256 слов: куски, кратные 256, разборов не меняют
KEYS_CHUNK = 256 * 64
UNREACHABLE_FILES = {
    True: RESOURCES_DIR / "freqrnc2011_unreachable_forms.txt",
    False: RESOURCES_DIR / "freqrnc2011_unreachable_lemmas.txt",
}


def keyness(
    target: str | Sequence[str] | Sequence[Sequence[str]] | Mapping[str, int],
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
    *,
    messages: Mapping[str, str] | None = None,
) -> list[Keyword]:
    """
    Поиск ключевых слов целевого корпуса относительно эталонного

    Описание:
        Для каждого слова считаются логарифм правдоподобия G² с p-значением
        (значимость различия) и Log Ratio (размер эффекта), как рекомендуют Gabrielatos
        и Hardie, и мера score, по которой список сортируется. Меры значимости (G²,
        хи-квадрат, BIC, ELL) отрицательны, если слово чаще в эталоне. Нулевая частота
        при расчете %DIFF, Log Ratio и отношения шансов заменяется на 0.5 (Hardie 2014)
        С эталоном FreqDict слова цели приводятся к леммам словаря, как в LexicalStats:
        слова текста - по разбору в контексте его предложений, список словоформ - в
        контексте списка, где без знаков препинания омонимы разбираются хуже («господа» -
        «господь»), частоты - по слову;
        числа и латиница отбрасываются, частота в эталоне - ipm, умноженная на объем
        корпуса словаря (92 млн); слово вне словаря получает его наименьшую частоту
        (min_ipm) и бывает только положительным ключевым словом. Сокращение сравнивается
        со своей статьей (ссср, млн), а без нее отбрасывается, если ruMorph раскрывает
        его в другое слово (т., г.). Статья, которой нет в цели и к которой не приводится
        ни одна форма ее лексем по первому разбору ruMorph, отрицательным ключевым словом
        не бывает

    Ссылки:
        https://ucrel.lancs.ac.uk/llwizard.html
        http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf
        http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/

    Аргументы:
        target (str|list[str]|list[list[str]]|dict[str, int]): Текст целевого корпуса,
            его слова - одного текста или списка текстов - или их частоты
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
        messages (dict[str, str]): Сообщения об ошибках по ключам; None - CORE_MESSAGES

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
    messages = core_messages(messages)
    context = None
    if isinstance(target, str):
        pairs = analyze_text(target)
        target = [word for word, _ in pairs]
        context = [analysis for _, analysis in pairs]
    if not isinstance(reference, FreqDict):
        return anyts.corpus.keyness(
            target, reference, measure, min_freq, positive, top_n, n, messages=messages
        )
    check_keyness_params(measure, min_freq, top_n, target, n, positive, messages=messages)
    if n > 1:
        raise ParameterError(
            f"Частотный словарь хранит слова: N-граммам нужны слова обоих корпусов, а не n={n}"
        )
    key = _dictionary_key(reference.entries, lemmatize)
    keys = _dictionary_keys(reference.entries, context) if lemmatize else None
    frequency = _frequency_reference(reference, key, keys)
    if positive:
        return anyts.corpus.keyness(
            target, frequency, measure, min_freq, positive, top_n, messages=messages
        )
    found = anyts.corpus.keyness(target, frequency, measure, min_freq, positive, messages=messages)
    unreachable = _unreachable_entries(lemmatize)
    kept = (keyword for keyword in found if keyword.freq_target or keyword.word not in unreachable)
    return list(islice(kept, top_n))


def _dictionary_key(entries: Mapping[str, Entry], lemmatize: bool) -> Callable[[str], str]:
    """Статья словаря для слова цели: словоформы (lemmatize) или леммы"""

    @cache
    def key(word: str) -> str:
        return _entry(word, parse_word(word), entries, lemmatize)

    return key


def _dictionary_keys(
    entries: Mapping[str, Entry], context: Sequence[rumorph.Analysis] | None = None
) -> Callable[[Sequence[str]], list[str]]:
    """Статьи словаря для словоформ текста цели по разборам ruMorph в контексте: разборам
    текста цели (context) или списка слов"""

    def keys(words: Sequence[str]) -> list[str]:
        analyses = context if context is not None else _list_analyses(tuple(words))
        return [
            _entry(word, analysis, entries, True)
            for word, analysis in zip(words, analyses, strict=True)
        ]

    return keys


@lru_cache(maxsize=1)
def _list_analyses(words: tuple[str, ...]) -> tuple[rumorph.Analysis, ...]:
    """Разборы ruMorph слов списка в контексте друг друга; последний список хранится, так что
    положительные и отрицательные ключевые слова одной цели разбирают ее один раз"""
    analyzer = get_morph_analyzer()
    found: list[rumorph.Analysis] = []
    for start in range(0, len(words), KEYS_CHUNK):
        chunk = words[start : start + KEYS_CHUNK]
        found += [
            options[0]
            for options in analyzer.analyze_sentence([strip_marks(word) for word in chunk])
        ]
    return tuple(found)


def _entry(
    word: str, analysis: rumorph.Analysis, entries: Mapping[str, Entry], lemmatize: bool
) -> str:
    """Статья словаря для слова цели с этим разбором: словоформы (lemmatize) или леммы"""
    if _abbreviated(analysis):
        return normalize_yo(word)
    return dictionary_lemma(word, analysis.lemma if lemmatize else word, entries)


def _frequency_reference(
    freq_dict: FreqDict,
    key: Callable[[str], str],
    keys: Callable[[Sequence[str]], list[str]] | None,
) -> FrequencyReference:
    """Эталон частотного словаря, как его описывает докстринг keyness"""
    size = float(CORPUS_SIZE)
    entries = freq_dict.entries

    def keep(word: str) -> bool:
        return _is_dictionary_word(word) and (key(word) in entries or not _is_expansion(word))

    return FrequencyReference(
        {lemma: ipm * size / 1e6 for lemma, ipm in freq_dict.word_ipm.items()},
        size,
        freq_dict.min_ipm * size / 1e6,
        key,
        keep,
        keys,
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
        Медленный: результат хранится в ресурсах UNREACHABLE_FILES. Цель из лемм
        дает лемма первого разбора формы или любого другого, кроме сокращений
        (предлог «со» - только «с»). Сравнительная степень
        и краткие формы прилагательных на -щий не считаются (обязаннее, действующ);
        у слов вне словаря ruMorph (Михайлыч) формы угаданы

    Аргументы:
        freq_dict (FreqDict): Частотный словарь
        lemmatize (bool): Цель из словоформ, False - из лемм

    Вывод:
        list[str]: Недостижимые статьи по алфавиту
    """
    key = _dictionary_key(freq_dict.entries, lemmatize)

    def targets(form: str) -> set[str]:
        if lemmatize:
            return {form}
        analyses = parse_all(form)
        return {analyses[0].lemma} | {
            analysis.lemma for analysis in analyses if not _abbreviated(analysis)
        }

    def counted(form: rumorph.Analysis, entry: str) -> bool:
        return form.feats.get("Degree") != "Cmp" and not (
            form.feats.get("Variant") == "Short" and entry.endswith("щий")
        )

    def reachable(entry: str) -> bool:
        forms = {entry} | {
            form.word
            for analysis in parse_all(entry)
            for form in analysis.forms()
            if counted(form, entry)
        }
        return any(
            key(target) == entry
            for form in forms
            for spelling in {form, normalize_yo(form)}
            for target in targets(spelling)
        )

    return sorted(entry for entry in freq_dict.entries if not reachable(entry))


def _abbreviated(analysis: rumorph.Analysis) -> bool:
    """Является ли разбор сокращением"""
    return analysis.feats.get("Abbr") == "Yes"


def _is_expansion(word: str) -> bool:
    """Раскрывает ли первый разбор сокращение в другое слово (т. - то), а не оставляет (вкп)"""
    analysis = parse_word(word)
    return _abbreviated(analysis) and normalize_yo(analysis.lemma) != normalize_yo(word)


@lru_cache(maxsize=131072)
def _is_dictionary_word(word: str) -> bool:
    """Состоит ли слово из букв словаря (DICTIONARY_WORD)"""
    return DICTIONARY_WORD.fullmatch(strip_marks(word)) is not None
