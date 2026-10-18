import re
from collections.abc import Mapping, Sequence
from functools import cache, lru_cache

import anyts
import anyts.lexical_stats
import anyts.utils
import pymorphy3
from anyts.lexical_stats import LexicalWord
from anyts.utils import iter_doc_units
from spacy.tokens import Doc

from .cohesion_stats import WordInfo, unit_info, unit_text, word_info
from .constants import CORE_MESSAGES, LEXICAL_STATS_DESC, PROPER_NOUN_GRAMMEMES, RESOURCES_DIR
from .datasets.freq2011 import Entry, FreqDict
from .exceptions import SourceTypeError
from .extractors import NUMBER_PATTERN, WordsExtractor
from .utils import normalize_yo, parse_all, parse_word

TOP_LEMMAS_FILE = RESOURCES_DIR / "sharoff_top10000.txt"
DICTIONARY_WORD = re.compile(r"[а-яё'-]*[а-яё][а-яё'-]*", re.IGNORECASE)
ADJECTIVE_POS = frozenset({"a", "apro"})
RARE_IPM = 1.0
RARE_RATIO = 20


class LexicalStats(anyts.lexical_stats.LexicalStats):
    """
    Класс для вычисления статистик лексической сложности текста

    Описание:
        Расширяет LexicalStats ядра anyTS русским словарем и леммами: частотный словарь
        Ляшевской и Шарова (FreqDict), частотные полосы - по вшитому списку
        10 000 лемм Шарова, леммы pymorphy3 (для Doc с разметкой частей речи - разбор
        с частью речи токена), дефисные слова Doc склеиваются, числа (2020, 5.5, 3-й)
        словами не считаются. Метрики по частотному словарю требуют загруженного
        FreqDict, полосы и лексическая плотность считаются без него

    Ссылки:
        https://doi.org/10.3758/s13428-017-0924-4 (Kyle, Crossley, Berger 2018, TAALES)
        http://dict.ruslang.ru/freq.php

    Пример использования:
        >>> from ruts import LexicalStats
        >>> text = "Кот сидел на окне и смотрел на птиц"
        >>> ls = LexicalStats(text)
        >>> ls.get_stats()
        {'coverage': 1.0,
        'mean_ipm': 8645.5375,
        'mean_ipm_content': 324.18,
        'mean_log_ipm': 3.0674194359404705,
        'mean_log_ipm_content': 2.316850597556863,
        'mean_range': 99.75,
        'mean_dispersion': 95.125,
        'surprisal': 9.74182176626998,
        'perplexity': 856.2105288389297,
        'p_top1000': 0.75,
        'p_top2000': 0.875,
        'p_top5000': 1.0,
        'p_top10000': 1.0,
        'p_beyond_top10000': 0.0,
        'lexical_density': 0.625}
        >>> ls.band_coverage(unique=True)
        {1000: 0.7142857142857143, 2000: 0.8571428571428571, 5000: 1.0, 10000: 1.0}

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        words_extractor (WordsExtractor): Инструмент для извлечения слов;
            если задан, применяется и к тексту Doc
        freq_dict (FreqDict): Частотный словарь; если не задан, используется FreqDict()
            из директории по умолчанию

    Атрибуты:
        freq_dict (FreqDict): Частотный словарь
        words (tuple[str]): Кортеж извлеченных слов
        lemmas (tuple[str]): Кортеж лемм в нижнем регистре
        keys (tuple[str]): Кортеж лемм в частотном словаре (dictionary_lemma)
        entries (tuple[Entry|None]): Статьи частотного словаря, None для слов вне словаря
        n_words (int): Количество слов
        n_content_words (int): Количество знаменательных слов
        n_found (int): Количество слов, найденных в частотном словаре
        ranks (tuple[int|None]): Кортеж рангов лемм по вшитому списку, None вне топ-10000
        coverage (float): Доля слов, найденных в частотном словаре
        mean_ipm (float): Средняя частотность найденных слов
        mean_ipm_content (float): Средняя частотность знаменательных слов - FREQ2 формулы
            Соловьёва, Иванова, Солнышкиной 2023 года (в статье значения 200-1000)
        mean_log_ipm (float): Средний десятичный логарифм частотности найденных слов
        mean_log_ipm_content (float): То же по знаменательным словам
        mean_range (float): Средний диапазон R найденных слов
        mean_dispersion (float): Средняя дисперсия D найденных слов
        surprisal (float): Средний сюрпризал слов по униграммной модели словаря в битах
        perplexity (float): Униграммная перплексия - 2 в степени сюрпризала
        p_top1000 (float): Доля слов с леммой из топ-1000
        p_top2000 (float): Доля слов с леммой из топ-2000
        p_top5000 (float): Доля слов с леммой из топ-5000
        p_top10000 (float): Доля слов с леммой из топ-10000
        p_beyond_top10000 (float): Доля слов с леммой вне топ-10000
        lexical_density (float): Доля знаменательных слов

    Методы:
        band_coverage: Доли слов или лемм по частотным полосам
        get_stats: Получение вычисленных статистик лексической сложности текста
        print_stats: Отображение вычисленных статистик с описанием на экран

    Исключения:
        SourceTypeError: Если источник данных не строка и не объект Doc, экстрактор
            или частотный словарь другого типа
        SourceError: Если в источнике данных отсутствуют слова
        DatasetNotFoundError: При обращении к метрикам по словарю, если словарь не загружен
    """

    freq_dict: FreqDict
    freq_dict_class = FreqDict
    stats_desc = LEXICAL_STATS_DESC
    stats_headers = ("Статистика", "Значение")
    messages = CORE_MESSAGES

    def __init__(
        self,
        source: str | Doc,
        words_extractor: anyts.WordsExtractor | None = None,
        freq_dict: FreqDict | None = None,
    ):
        if words_extractor is not None and not isinstance(words_extractor, anyts.WordsExtractor):
            raise SourceTypeError(self.messages["words_extractor_type"])
        self._words_extractor = words_extractor
        super().__init__(source, freq_dict)

    def analyze(self, source: str | Doc) -> list[LexicalWord]:
        """Слова без чисел с леммами pymorphy3 и признаком знаменательного слова"""
        extractor = self._words_extractor
        infos: list[WordInfo]
        if isinstance(source, Doc) and extractor is not None:
            source = source.text
        if isinstance(source, Doc):
            units = [
                unit
                for unit in iter_doc_units(source, join_hyphens=True)
                if not is_number(unit_text(unit))
            ]
            words = [unit_text(unit) for unit in units]
            if source.has_annotation("POS"):
                infos = [unit_info(unit) for unit in units]
            else:
                infos = [word_info(word) for word in words]
        elif isinstance(source, str):
            words = [
                word
                for word in (extractor or WordsExtractor()).extract(source)
                if not is_number(word)
            ]
            infos = [word_info(word) for word in words]
        else:
            raise SourceTypeError(self.messages["source_type"])
        return [
            LexicalWord(word, info.lemma, info.content)
            for word, info in zip(words, infos, strict=True)
        ]

    def dictionary_keys(self) -> tuple[str, ...]:
        """Леммы слов в частотном словаре (dictionary_lemma)"""
        entries = self.freq_dict.entries
        return tuple(
            dictionary_lemma(word, lemma, entries)
            for word, lemma in zip(self.words, self.lemmas, strict=True)
        )

    def rank(self, lemma: str) -> int | None:
        """Ранг леммы по вшитому списку Шарова (get_rank)"""
        return get_rank(lemma)

    def top_size(self) -> int:
        """Последний ранг вшитого списка Шарова"""
        return max(load_top_lemmas().values())


def is_number(word: str) -> bool:
    """
    Проверка, является ли слово числом по шаблону NUMBER_PATTERN

    Аргументы:
        word (str): Слово

    Вывод:
        bool: Результат проверки
    """
    return anyts.utils.is_number(word, NUMBER_PATTERN)


@cache
def load_top_lemmas() -> dict[str, int]:
    """
    Загрузка вшитого списка самых частых лемм

    Описание:
        10 000 лемм интернет-корпуса Лидского университета (С. А. Шаров) в порядке
        убывания частоты, файл resources/sharoff_top10000.txt (CC BY 2.5); леммы
        приводятся к нижнему регистру без буквы ё, у дублей (еще, ещё) остается
        меньший ранг

    Вывод:
        dict[str, int]: Ранг каждой леммы, начиная с 1
    """
    with TOP_LEMMAS_FILE.open(encoding="utf-8") as file:
        lemmas = [normalize_yo(line.strip()) for line in file if line.strip()]
    ranks: dict[str, int] = {}
    for rank, lemma in enumerate(lemmas, 1):
        ranks.setdefault(lemma, rank)
    return ranks


def get_rank(lemma: str) -> int | None:
    """
    Получение ранга леммы по вшитому списку самых частых лемм

    Аргументы:
        lemma (str): Лемма в любом регистре, с ё или без

    Вывод:
        int|None: Ранг от 1 до 10 000, None если леммы в списке нет
    """
    return load_top_lemmas().get(normalize_yo(lemma))


def dictionary_lemma(word: str, lemma: str, entries: Mapping[str, Entry]) -> str:
    """
    Получение леммы слова в частотном словаре

    Описание:
        Лемма приводится к нижнему регистру без ё и к соглашениям словаря,
        лемматизированного не pymorphy3: краткая форма (должна - должен), множественное
        число (денег - деньги), написание слова (счастье и счастие - разные статьи),
        отчество своего рода (Ивановной - ивановна, Михайловичем - михайлович);
        лемма вне словаря или у его нижней границы (RARE_IPM) заменяется самой частотной
        леммой другого разбора (ночью - ночь, нашли - найти), имя собственное - только
        именем собственным

    Аргументы:
        word (str): Словоформа
        lemma (str): Лемма слова
        entries (dict[str, Entry]): Статьи словаря по леммам в нижнем регистре без ё

    Вывод:
        str: Лемма для поиска в словаре
    """
    key, short, plural = _form_lemmas(word, normalize_yo(lemma))
    if short and short in entries and ADJECTIVE_POS & set(entries[short].pos):
        return short
    if (
        plural
        and plural in entries
        and "s" in entries[plural].pos
        and entries[plural].ipm > _ipm(entries, key)
    ):
        return plural
    if key not in entries:
        candidates = [candidate for candidate, _ in _parse_lemmas(word) if candidate in entries]
    elif entries[key].ipm <= RARE_IPM and key == normalize_yo(lemma):
        parses = _parse_lemmas(word)
        pos = next((pos for candidate, pos in parses if candidate == key), None)
        least = entries[key].ipm * RARE_RATIO
        candidates = [
            candidate
            for candidate, candidate_pos in parses
            if candidate_pos == pos and candidate in entries and entries[candidate].ipm >= least
        ]
    else:
        return key
    return max(candidates, key=lambda candidate: entries[candidate].ipm, default=key)


def _ipm(entries: Mapping[str, Entry], lemma: str) -> float:
    entry = entries.get(lemma)
    return entry.ipm if entry else 0.0


@lru_cache(maxsize=131072)
def _form_lemmas(word: str, key: str) -> tuple[str, str | None, str | None]:
    """Лемма в написании слова, краткая форма и форма множественного числа по разбору леммы"""
    parse = parse_word(word)
    if normalize_yo(parse.normal_form) != key:
        parses = parse_all(word)
        found = next((parse for parse in parses if normalize_yo(parse.normal_form) == key), None)
        if found is None:
            return key, None, None
        parse = found
    if "Patr" in parse.tag.grammemes:
        form = parse.inflect({"nomn", "sing"})
        return normalize_yo(form.word) if form else key, None, None
    if parse.tag.POS == "ADJS":
        form = parse.inflect({"masc", "sing"})
        return key, normalize_yo(form.word) if form else None, None
    if parse.tag.POS != "NOUN":
        return key, None, None
    plural = None
    if parse.tag.number == "plur":
        form = parse.inflect({"nomn", "plur"})
        plural = normalize_yo(form.word) if form else None
    return _spelling(parse) or key, None, plural


def _spelling(parse: pymorphy3.analyzer.Parse) -> str | None:
    """Нормальная форма в варианте написания слова (V-ie, V-be и другие граммемы V-)"""
    normal = parse.normalized.tag.grammemes
    target = {g for g in normal if not g.startswith("V-")}
    target |= {g for g in parse.tag.grammemes if g.startswith("V-")}
    if target == normal:
        return None
    return next(
        (normalize_yo(form.word) for form in parse.lexeme if form.tag.grammemes == target), None
    )


@lru_cache(maxsize=131072)
def _parse_lemmas(word: str) -> tuple[tuple[str, str | None], ...]:
    """Леммы и части речи разборов pymorphy3, у имени собственного - только имен собственных"""
    parses = parse_all(word)
    if PROPER_NOUN_GRAMMEMES & parses[0].tag.grammemes:
        parses = tuple(parse for parse in parses if PROPER_NOUN_GRAMMEMES & parse.tag.grammemes)
    return tuple((normalize_yo(parse.normal_form), parse.tag.POS) for parse in parses)


def calc_surprisal(lemmas: Sequence[str], freq_dict: FreqDict) -> float:
    """
    Вычисление среднего сюрпризала слов по униграммной модели частотного словаря

    Описание:
        Среднее по словам −log2 P(w), где P(w) = ipm / 10⁶; слова вне словаря
        получают минимальную частоту словаря (0.4 ipm), поэтому сюрпризал определен
        для всех слов. Перплексия текста - 2 в степени сюрпризала

    Аргументы:
        lemmas (list[str]): Леммы слов
        freq_dict (FreqDict): Частотный словарь

    Вывод:
        float: Средний сюрпризал в битах, nan для пустого списка

    Исключения:
        SourceTypeError: Если леммы не список строк или словарь не FreqDict
    """
    if not isinstance(freq_dict, FreqDict):
        raise SourceTypeError(CORE_MESSAGES["freq_dict_type"].format(expected="FreqDict"))
    return anyts.lexical_stats.calc_surprisal(lemmas, freq_dict)
