from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping, Sequence
from functools import cached_property, lru_cache
from math import nan
from typing import TYPE_CHECKING, ClassVar

import anyts
import anyts.morph_stats
import rumorph
from anyts.morph_stats import MorphWord as MorphWord
from anyts.utils import has_pos, is_doc, iter_doc_units, safe_divide, source_type_error

from .constants import (
    ANSWER_PARTICLE_NEXT,
    ANSWER_PARTICLE_PREV,
    ANSWER_PARTICLE_PREV_MARKS,
    CONDITIONAL_PARTICLES,
    CORE_MESSAGES,
    MORPHOLOGY_FEATURES,
    MORPHOLOGY_MARKERS_DESC,
    MORPHOLOGY_STATS_DESC,
    UD_PERSONS,
)
from .exceptions import SourceTypeError
from .utils import (
    BYTE_ORDER_MARK,
    analyze_text,
    analyze_words,
    lemmatize,
    parse_all,
    parse_word,
    strip_marks,
)

if TYPE_CHECKING:
    from spacy.tokens import Doc, Token

# «нет» вне дефисных слов (нет-нет, нет‑с) с дефисами, которые склеивает токенизатор
ANSWER_NET = re.compile(r"(?<!\w)(?<!\w[-‐‑‒])нет(?![\w\-‐‑‒])", re.IGNORECASE)
# Окно поиска соседнего знака или слова
ANSWER_CONTEXT = 40
VERBAL_POS = frozenset({"VERB", "AUX"})
REFLEXIVE_ENDINGS = ("ся", "сь")
# Признаки OpenCorpora, которых нет в русском UD: у ruMorph это пометы разбора
LABEL_FEATURES = {
    "transitivity": {"tran": "Tran", "intr": "Intr"},
    "involvement": {"incl": "In", "excl": "Ex"},
}


class MorphStats(anyts.morph_stats.MorphStats):
    """
    Класс для вычисления морфологических статистик текста

    Описание:
        Расширяет MorphStats ядра anyTS русским разбором слов (analyze) и маркерами
        форм глагола. Части речи и грамматические признаки выдаются в терминах Universal Dependencies:
        pos - NOUN, VERB, ADJ, PRON, DET и другие, case - Nom, Gen, Dat, Acc, Ins, Loc,
        так же animacy, aspect, degree, gender, mood, number, person, polarity, tense,
        voice, verb_form и краткая форма style_variant
        Для объекта Doc с разметкой частей речи значения берутся из token.pos_
        и token.morph, для строки - из разбора ruMorph в контексте предложения, то есть
        с учетом соседних слов (стали - глагол или существительное); для Doc без
        разметки - так же в предложениях, слова которых те же, что у строки, иначе
        и с заданным экстрактором слов используется первый разбор ruMorph
        Переходность (transitivity) и совместность (involvement) - признаки OpenCorpora,
        которых в русском UD нет; они берутся из помет разбора ruMorph для глаголов
        и в строке признаков tags записываются как Subcat и Clusivity

    Ссылки:
        https://universaldependencies.org/u/feat/
        https://github.com/SergeyShk/ruMorph

    Пример использования:
        >>> from ruts import MorphStats
        >>> text = "Постарайтесь получить то, что любите, иначе придется полюбить то, что получили"
        >>> ms = MorphStats(text)
        >>> ms.get_stats()
        {'pos': {'VERB': 6, 'PRON': 4, 'ADV': 1},
        'animacy': {None: 7, 'Inan': 4},
        'aspect': {'Perf': 5, None: 5, 'Imp': 1},
        'case': {None: 7, 'Acc': 4},
        'degree': {None: 10, 'Pos': 1},
        'gender': {None: 7, 'Neut': 4},
        'involvement': {'Ex': 1, None: 10},
        'mood': {'Imp': 1, None: 7, 'Ind': 3},
        'number': {'Plur': 3, None: 3, 'Sing': 5},
        'person': {'2': 2, None: 8, '3': 1},
        'polarity': {None: 11},
        'style_variant': {None: 11},
        'tense': {None: 8, 'Pres': 1, 'Fut': 1, 'Past': 1},
        'transitivity': {'Intr': 2, 'Tran': 4, None: 5},
        'verb_form': {'Fin': 4, 'Inf': 2, None: 5},
        'voice': {'Mid': 2, 'Act': 4, None: 5}}
        >>> ms.tags[0]
        'Aspect=Perf|Clusivity=Ex|Mood=Imp|Number=Plur|Person=2|Subcat=Intr|VerbForm=Fin|Voice=Mid'

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        words_extractor (WordsExtractor): Инструмент для извлечения слов;
            если задан, применяется и к тексту Doc

    Атрибуты:
        words (tuple[str]): Кортеж извлеченных слов
        lemmas (tuple[str]): Кортеж лемм слов: ruMorph с учетом части речи слова
        tags (tuple[str]): Кортеж строк грамматических признаков в формате CoNLL-U
        pos (tuple[str]): Кортеж значений части речи
        animacy (tuple[str]): Кортеж значений одушевленности
        aspect (tuple[str]): Кортеж значений вида
        case (tuple[str]): Кортеж значений падежа
        degree (tuple[str]): Кортеж значений степени сравнения
        gender (tuple[str]): Кортеж значений рода
        involvement (tuple[str]): Кортеж значений совместности
        mood (tuple[str]): Кортеж значений наклонения
        number (tuple[str]): Кортеж значений числа
        person (tuple[str]): Кортеж значений лица
        polarity (tuple[str]): Кортеж значений отрицания
        style_variant (tuple[str]): Кортеж значений краткой формы
        tense (tuple[str]): Кортеж значений времени
        transitivity (tuple[str]): Кортеж значений переходности
        verb_form (tuple[str]): Кортеж значений формы глагола
        voice (tuple[str]): Кортеж значений залога

    Методы:
        analyze: Слова источника с частью речи и признаками UD
        get_stats: Получение вычисленных морфологических статистик текста
        to_dataframe: Получение статистик таблицей из одной строки
        describe: Прочтение статистики по шкале; у морфологии шкал нет - None
        explain_text: Разбор текста по морфологическим статистикам
        print_stats: Отображение вычисленных морфологических статистик текста с описанием на экран
        get_markers: Получение долей грамматических форм глагола
        print_markers: Отображение долей грамматических форм глагола с описанием на экран

    Исключения:
        SourceTypeError: Если передаваемое значение не является строкой или объектом Doc
        SourceError: Если в источнике данных отсутствуют слова
    """

    feature_names = MORPHOLOGY_FEATURES
    stats_desc: ClassVar[Mapping[str, str]] = {
        stat: desc["name"] for stat, desc in MORPHOLOGY_STATS_DESC.items()
    }
    values_desc: ClassVar[Mapping[str, Mapping[str, str]]] = {
        stat: desc["values"] for stat, desc in MORPHOLOGY_STATS_DESC.items()
    }
    unknown_value = "Неизвестно"
    markers_desc = MORPHOLOGY_MARKERS_DESC
    markers_headers = ("Маркер", "Значение")
    messages = CORE_MESSAGES
    # Русские признаки поверх признаков ядра по умолчанию
    involvement: tuple[str | None, ...]
    style_variant: tuple[str | None, ...]
    transitivity: tuple[str | None, ...]

    def __init__(self, source: str | Doc, words_extractor: anyts.WordsExtractor | None = None):
        if words_extractor is not None and not isinstance(words_extractor, anyts.WordsExtractor):
            raise SourceTypeError(self.messages["words_extractor_type"])
        self._words_extractor = words_extractor
        super().__init__(source)

    def analyze(self, source: str | Doc) -> list[MorphWord]:
        """
        Слова источника с частью речи и признаками UD

        Описание:
            Для Doc с разметкой частей речи - token.pos_ и token.morph (token_to_ud),
            дефисные слова склеиваются; для строки - разбор ruMorph в контексте
            предложения (analyze_text), для Doc без разметки - тоже в предложениях,
            слова которых те же, что у строки (analyze_words), а для остальных слов
            и с заданным экстрактором слов (он применяется к тексту Doc) - первый разбор
            ruMorph

        Аргументы:
            source (str|Doc): Источник данных

        Вывод:
            list[MorphWord]: Слова с частью речи и признаками

        Исключения:
            SourceTypeError: Если источник данных не строка и не объект Doc
        """
        features: list[dict[str, str | None]]
        extractor = self._words_extractor
        if is_doc(source) and extractor is not None:
            source = source.text
        if is_doc(source):
            units = list(iter_doc_units(source, join_hyphens=True))
            words: Sequence[str] = [
                strip_marks("".join(token.text for token in unit)).lstrip(BYTE_ORDER_MARK)
                for unit in units
            ]
            if has_pos(source):
                # Токены одной словоформы с одной разметкой получают один словарь, как в _word_to_ud
                known: dict[tuple[int, str, str, int], dict[str, str | None]] = {}
                features = []
                for unit, word in zip(units, words, strict=True):
                    if len(unit) > 1:
                        features.append(_word_to_ud(word))
                        continue
                    token = unit[0]
                    key = (token.pos, str(token.morph), token.text, token.lemma)
                    if (cached := known.get(key)) is None:
                        cached = known[key] = token_to_ud(token)
                    features.append(cached)
            else:
                positions = [(unit[0].idx, word) for unit, word in zip(units, words, strict=True)]
                features = _words_to_ud(words, source.text, analyze_words(positions, source.text))
        elif isinstance(source, str):
            if extractor is None:
                pairs = analyze_text(source)
                words = [word for word, _ in pairs]
                features = [_analysis_to_ud(analysis) for _, analysis in pairs]
            else:
                words = extractor.extract(source)
                features = _words_to_ud(words, source)
        else:
            raise source_type_error(self.messages, source)
        # Признаки одной словоформы - общий словарь кэша _word_to_ud: ядро читает его один раз
        names: dict[int, dict[str, str]] = {}
        for found in features:
            if id(found) not in names:
                names[id(found)] = {
                    name: value
                    for stat, name in MORPHOLOGY_FEATURES.items()
                    if (value := found[stat])
                }
        return [
            MorphWord(word, found["pos"], names[id(found)])
            for word, found in zip(words, features, strict=True)
        ]

    @cached_property
    def lemmas(self) -> tuple[str, ...]:
        """Леммы слов: ruMorph с учетом части речи слова"""
        return tuple(
            lemmatize(word, pos or "") for word, pos in zip(self.words, self.pos, strict=True)
        )

    def get_markers(self) -> dict[str, float]:
        """
        Получение долей грамматических форм глагола

        Описание:
            Доли форм глагола (VERB и AUX), каждая от своей базы: наклонения - от личных
            форм, совершенный вид - от форм с видом, остальные - от всех форм глагола;
            доля с пустой базой - nan; признак из нескольких значений (Mood=Ind,Imp)
            входит в долю каждого. Сослагательное наклонение определяется по частице
            бы, поэтому экстрактор слов не должен отбрасывать частицы

        Вывод:
            dict[str, float]: Словарь долей в порядке MORPHOLOGY_MARKERS_DESC

        Пример использования:
            >>> from ruts import MorphStats
            >>> ms = MorphStats("Если бы я знал, я бы пришел за книгами, прочитанными вчера")
            >>> ms.get_markers()["p_conditional"], ms.get_markers()["p_passive"]
            (1.0, 0.3333333333333333)
        """
        verbs = [
            index
            for index, pos in enumerate(self.pos)
            if pos in VERBAL_POS and self.verb_form[index]
        ]
        forms = Counter(value for index in verbs for value in _values(self.verb_form[index]))
        finite = [index for index in verbs if "Fin" in _values(self.verb_form[index])]
        moods = Counter(value for index in finite for value in _values(self.mood[index]))
        aspects = Counter(value for index in verbs for value in _values(self.aspect[index]))
        n_forms = len(verbs)
        n_finite = len(finite)
        n_particles = sum(
            word.lower() in CONDITIONAL_PARTICLES and word != "Б" for word in self.words
        )
        n_past = sum(
            "Ind" in _values(self.mood[index]) and "Past" in _values(self.tense[index])
            for index in finite
        )
        n_conditional = min(n_particles, n_past)
        n_passive = sum(
            "Part" in _values(self.verb_form[index]) and "Pass" in _values(self.voice[index])
            for index in verbs
        )
        n_reflexive = sum(self.words[index].lower().endswith(REFLEXIVE_ENDINGS) for index in verbs)
        return {
            "p_indicative": safe_divide(moods["Ind"] - n_conditional, n_finite, nan),
            "p_imperative": safe_divide(moods["Imp"], n_finite, nan),
            "p_conditional": safe_divide(moods["Cnd"] + n_conditional, n_finite, nan),
            "p_infinitive": safe_divide(forms["Inf"], n_forms, nan),
            "p_participle": safe_divide(forms["Part"], n_forms, nan),
            "p_converb": safe_divide(forms["Conv"], n_forms, nan),
            "p_perfective": safe_divide(
                aspects["Perf"], sum(1 for index in verbs if self.aspect[index]), nan
            ),
            "p_passive": safe_divide(n_passive, n_forms, nan),
            "p_reflexive": safe_divide(n_reflexive, n_forms, nan),
        }


def _values(value: str | None) -> list[str]:
    """Значения признака из нескольких значений через запятую, без признака - ни одного"""
    return value.split(",") if value else []


def analysis_to_ud(analysis: rumorph.Analysis) -> dict[str, str | None]:
    """
    Перевод разбора ruMorph в признаки по ключам MORPHOLOGY_STATS_DESC

    Описание:
        Часть речи и признаки UD - как у разбора; краткая форма - Variant=Short;
        переходность и совместность - пометы tran, intr и incl, excl (LABEL_FEATURES)

    Аргументы:
        analysis (Analysis): Разбор ruMorph

    Вывод:
        dict[str, str|None]: Признаки по ключам MORPHOLOGY_STATS_DESC
    """
    feats = analysis.feats
    features: dict[str, str | None] = {"pos": analysis.pos or None}
    for stat, feature in MORPHOLOGY_FEATURES.items():
        features[stat] = feats.get(feature)
    features["style_variant"] = "Short" if feats.get("Variant") == "Short" else None
    labels = analysis.labels
    for stat, values in LABEL_FEATURES.items():
        features[stat] = next((value for label, value in values.items() if label in labels), None)
    return features


def word_to_ud(word: str) -> dict[str, str | None]:
    """
    Получение признаков Universal Dependencies слова по первому разбору ruMorph

    Аргументы:
        word (str): Слово

    Вывод:
        dict[str, str|None]: Признаки по ключам MORPHOLOGY_STATS_DESC
    """
    return dict(_word_to_ud(word))


@lru_cache(maxsize=131072)
def _word_to_ud(word: str) -> dict[str, str | None]:
    """Признаки word_to_ud с кэшем по словоформе; словарь общий, менять его нельзя"""
    return _analysis_to_ud(parse_word(word))


@lru_cache(maxsize=131072)
def _analysis_to_ud(analysis: rumorph.Analysis) -> dict[str, str | None]:
    """Признаки analysis_to_ud с кэшем по разбору; словарь общий, менять его нельзя"""
    return analysis_to_ud(analysis)


@lru_cache(maxsize=1024)
def _particle_to_ud(word: str) -> dict[str, str | None]:
    """Признаки слова по разбору частицей (ответное «нет»); словарь общий, менять его нельзя"""
    analyses = parse_all(word)
    particle = next((analysis for analysis in analyses if analysis.pos == "PART"), analyses[0])
    return analysis_to_ud(particle)


def _words_to_ud(
    words: Sequence[str],
    text: str,
    analyses: Sequence[rumorph.Analysis | None] | None = None,
) -> list[dict[str, str | None]]:
    """
    Получение признаков Universal Dependencies слов текста по первому разбору ruMorph

    Описание:
        Как word_to_ud, но ответное «нет» (find_answer_particles) - частица, а не
        бытийное «нет»; слово с заданным разбором (в контексте, analyze_words) -
        по нему

    Аргументы:
        words (list[str]): Слова текста
        text (str): Текст, из которого извлечены слова
        analyses (list[Analysis|None]|None): Разборы слов; None - разбор по слову

    Вывод:
        list[dict[str, str|None]]: Признаки слов; словари общие, менять их нельзя
    """
    particles = answer_particles(words, text)
    found = analyses or [None] * len(words)
    return [
        _analysis_to_ud(analysis)
        if analysis is not None
        else _particle_to_ud(word)
        if particle
        else _word_to_ud(word)
        for word, particle, analysis in zip(words, particles, found, strict=True)
    ]


def find_answer_particles(text: str) -> list[bool]:
    """
    Поиск ответных «нет» в тексте

    Описание:
        Для каждого «нет» текста по порядку - частица ли это (Нет, не пойду; Или нет?),
        а не бытийный предикатив (Денег нет): частица стоит в начале текста, после знака
        или слова ANSWER_PARTICLE_PREV(_MARKS) и перед знаком, концом текста или словом
        ANSWER_PARTICLE_NEXT

    Аргументы:
        text (str): Текст

    Вывод:
        list[bool]: Частица ли каждое «нет» текста

    Пример использования:
        >>> from ruts.morph_stats import find_answer_particles
        >>> find_answer_particles("Нет, денег нет. Или нет?")
        [True, False, True]
    """
    text = strip_marks(text)
    flags = []
    for match in ANSWER_NET.finditer(text):
        before = text[max(match.start() - ANSWER_CONTEXT, 0) : match.start()].rstrip()
        after = text[match.end() : match.end() + ANSWER_CONTEXT].lstrip()
        prev = re.search(r"\w+$", before)
        starts = not before or before[-1] in ANSWER_PARTICLE_PREV_MARKS
        if prev:
            starts = prev.group().lower() in ANSWER_PARTICLE_PREV
        following = re.match(r"\w+", after)
        ends = not following or following.group().lower() in ANSWER_PARTICLE_NEXT
        flags.append(starts and ends)
    return flags


def answer_particles(words: Sequence[str], text: str) -> list[bool]:
    """Ответные «нет» среди слов текста; если «нет» в словах и в тексте не совпали - ни одного"""
    indices = [i for i, word in enumerate(words) if word.lower() == "нет"]
    flags = [False] * len(words)
    found = find_answer_particles(text) if indices else []
    if len(found) == len(indices):
        for i, particle in zip(indices, found, strict=True):
            flags[i] = particle
    return flags


@lru_cache(maxsize=131072)
def parse_verb(word: str, lemma: str = "") -> rumorph.Analysis | None:
    """
    Получение глагольного разбора словоформы ruMorph

    Описание:
        Среди всех разборов словоформы выбирается глагольный (VERB, AUX) с заданной
        леммой, а при ее отсутствии - первый глагольный: для «стали» с леммой «стать»
        это глагол, а не существительное «сталь»

    Аргументы:
        word (str): Словоформа
        lemma (str): Лемма, которой отдается предпочтение

    Вывод:
        Analysis|None: Разбор словоформы, None если глагольных разборов нет
    """
    verbs = [analysis for analysis in parse_all(word) if analysis.pos in VERBAL_POS]
    if not verbs:
        return None
    return next((analysis for analysis in verbs if analysis.lemma == lemma), verbs[0])


def token_to_ud(token: Token) -> dict[str, str | None]:
    """
    Получение признаков Universal Dependencies токена spaCy

    Описание:
        Часть речи и признаки берутся из token.pos_ и token.morph (признак из нескольких
        значений - через запятую, как в разметке); лицо First, Second,
        Third моделей ru_core_news переводится в 1, 2, 3; краткая форма - StyleVariant
        моделей ru_core_news или Variant=Short разметки русского UD
        Переходность и совместность, которых в русском UD нет, для глаголов (VERB, AUX)
        берутся из помет глагольного разбора ruMorph с леммой spaCy

    Аргументы:
        token (Token): Токен

    Вывод:
        dict[str, str|None]: Признаки по ключам MORPHOLOGY_STATS_DESC
    """
    features: dict[str, str | None] = {"pos": token.pos_ or None}
    morph = token.morph.to_dict()
    for stat, feature in MORPHOLOGY_FEATURES.items():
        value = morph.get(feature)
        features[stat] = value or None
    features["person"] = UD_PERSONS.get(features["person"] or "", features["person"])
    if features["style_variant"] is None and "Short" in morph.get("Variant", "").split(","):
        features["style_variant"] = "Short"
    verb = parse_verb(token.text, token.lemma_) if token.pos_ in VERBAL_POS else None
    labels = verb.labels if verb else frozenset()
    for stat, values in LABEL_FEATURES.items():
        features[stat] = next((value for label, value in values.items() if label in labels), None)
    return features
