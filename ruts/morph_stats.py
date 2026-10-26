from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping, Sequence
from functools import cached_property, lru_cache
from inspect import getattr_static
from math import nan
from typing import TYPE_CHECKING, ClassVar

import anyts
import anyts.morph_stats
import pymorphy3
from anyts.morph_stats import MorphWord as MorphWord
from anyts.utils import has_pos, is_doc, iter_doc_units, safe_divide, source_type_error

from .constants import (
    ANSWER_PARTICLE_NEXT,
    ANSWER_PARTICLE_PREV,
    ANSWER_PARTICLE_PREV_MARKS,
    COMPARATIVE_ADVERBS,
    CONDITIONAL_PARTICLES,
    CORE_MESSAGES,
    MORPHOLOGY_FEATURES,
    MORPHOLOGY_MARKERS_DESC,
    MORPHOLOGY_STATS_DESC,
    NEGATIVE_PARTICLES,
    OPENCORPORA_TO_UD_GRAMMEMES,
    OPENCORPORA_TO_UD_POS,
    OPENCORPORA_VERB_FORMS,
    PROPER_NOUN_GRAMMEMES,
    SUBORDINATING_CONJUNCTIONS,
    TENSED_PREDICATIVES,
    UD_PERSONS,
)
from .exceptions import SourceTypeError
from .extractors import WordsExtractor
from .utils import BYTE_ORDER_MARK, lemmatize, parse_all, parse_word, strip_marks

if TYPE_CHECKING:
    from spacy.tokens import Doc, Token

VERB_POS = frozenset(OPENCORPORA_VERB_FORMS)
# «нет» вне дефисных слов (нет-нет, нет‑с) с дефисами, которые склеивает токенизатор
ANSWER_NET = re.compile(r"(?<!\w)(?<!\w[-‐‑‒])нет(?![\w\-‐‑‒])", re.IGNORECASE)
# Окно поиска соседнего знака или слова
ANSWER_CONTEXT = 40
VERBAL_POS = frozenset({"VERB", "AUX"})
SHORT_FORM_POS = frozenset({"ADJS", "PRTS"})
REFLEXIVE_ENDINGS = ("ся", "сь")
# Признаки, которых нет среди граммем pymorphy3: выводятся из части речи и леммы в tag_to_ud
DERIVED_FEATURES = frozenset({"degree", "polarity", "style_variant", "verb_form"})
TAG_GRAMMEMES = {
    stat: getattr_static(pymorphy3.tagset.OpencorporaTag, stat).grammeme_set
    for stat in MORPHOLOGY_FEATURES
    if stat not in DERIVED_FEATURES
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
        и token.morph, то есть с учетом контекста (стали - глагол или существительное);
        для строки, Doc без разметки и Doc с заданным экстрактором слов используется
        первый разбор pymorphy3, граммемы OpenCorpora переводятся в UD по таблицам
        в constants
        Переходность (transitivity) и совместность (involvement) - признаки OpenCorpora,
        которых в русском UD нет; они считаются через pymorphy3 для глаголов
        и в строке признаков tags записываются как Subcat и Clusivity

    Ссылки:
        https://universaldependencies.org/u/feat/
        https://github.com/no-plagiarism/pymorphy3
        http://opencorpora.org/dict.php?act=gram

    Пример использования:
        >>> from ruts import MorphStats
        >>> text = "Постарайтесь получить то, что любите, иначе придется полюбить то, что получили"
        >>> ms = MorphStats(text)
        >>> ms.get_stats()
        {'pos': {'VERB': 6, 'CCONJ': 2, 'SCONJ': 2, 'ADV': 1},
        'animacy': {None: 11},
        'aspect': {'Perf': 5, None: 5, 'Imp': 1},
        'case': {None: 11},
        'degree': {None: 10, 'Pos': 1},
        'gender': {None: 11},
        'involvement': {'Ex': 1, None: 10},
        'mood': {'Imp': 1, None: 7, 'Ind': 3},
        'number': {'Plur': 3, None: 7, 'Sing': 1},
        'person': {None: 9, '2': 1, '3': 1},
        'polarity': {None: 11},
        'style_variant': {None: 11},
        'tense': {None: 8, 'Pres': 1, 'Fut': 1, 'Past': 1},
        'transitivity': {'Intr': 2, 'Tran': 4, None: 5},
        'verb_form': {'Fin': 4, 'Inf': 2, None: 5},
        'voice': {None: 11}}
        >>> ms.tags[0]
        'Aspect=Perf|Clusivity=Ex|Mood=Imp|Number=Plur|Subcat=Intr|VerbForm=Fin'

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        words_extractor (WordsExtractor): Инструмент для извлечения слов;
            если задан, применяется и к тексту Doc

    Атрибуты:
        words (tuple[str]): Кортеж извлеченных слов
        lemmas (tuple[str]): Кортеж лемм слов: pymorphy3 с учетом части речи слова
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
            дефисные слова склеиваются; для строки, Doc без разметки и Doc с заданным
            экстрактором слов (он применяется к тексту Doc) - первый разбор pymorphy3

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
                features = _words_to_ud(words, source.text)
        elif isinstance(source, str):
            words = (extractor or WordsExtractor()).extract(source)
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
        """Леммы слов: pymorphy3 с учетом части речи слова"""
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


def tag_to_ud_pos(tag: pymorphy3.tagset.OpencorporaTag, lemma: str, word: str = "") -> str | None:
    """
    Перевод части речи OpenCorpora в часть речи Universal Dependencies

    Описание:
        Формы глагола (VERB, INFN, PRTF, PRTS, GRND) сводятся к VERB, прилагательные
        и компаративы - к ADJ; существительные с пометами имени, фамилии, отчества,
        топонима или организации - PROPN, но только для словоформ с заглавной буквы:
        pymorphy3 не учитывает регистр, и первый разбор обычных слов (лев, роза, мороз,
        улей) тоже несет помету имени; местоименные прилагательные (Apro) - DET,
        кроме относительного «который» - PRON и числительного «один» (Apro и Anum) -
        NUM; союзы из SUBORDINATING_CONJUNCTIONS - SCONJ, остальные - CCONJ;
        предикативы (надо, нельзя) - ADV; числа и римские цифры - NUM, латиница
        и неизвестные слова - X
        Без контекста часть речи омонимов и роль союзов (что, как) определяются
        приблизительно

    Аргументы:
        tag (OpencorporaTag): Тэг OpenCorpora
        lemma (str): Лемма слова
        word (str): Словоформа; без нее имена собственные не выделяются

    Вывод:
        str|None: Часть речи UD, None если pymorphy3 не определил часть речи
    """
    grammemes = tag.grammemes
    if tag.POS == "NOUN" and PROPER_NOUN_GRAMMEMES & grammemes and word[:1].isupper():
        return "PROPN"
    if tag.POS == "ADJF" and "Apro" in grammemes:
        if "Anum" in grammemes:
            return "NUM"
        return "PRON" if lemma == "который" else "DET"
    if tag.POS == "CONJ" and lemma in SUBORDINATING_CONJUNCTIONS:
        return "SCONJ"
    for grammeme in (tag.POS, *grammemes):
        if grammeme in OPENCORPORA_TO_UD_POS:
            return OPENCORPORA_TO_UD_POS[grammeme]
    return None


def tag_to_ud(
    tag: pymorphy3.tagset.OpencorporaTag, lemma: str, word: str = ""
) -> dict[str, str | None]:
    """
    Перевод тэга OpenCorpora в признаки Universal Dependencies

    Описание:
        Граммемы переводятся по таблице OPENCORPORA_TO_UD_GRAMMEMES: падежи gen1, gen2,
        acc2, loc1, loc2 - в Gen, Par, Acc, Loc, Loc; лицо 1per, 2per, 3per - в 1, 2, 3;
        общий род ms-f (сирота, задира), который pymorphy3 не относит к роду, - в Com;
        форма глагола verb_form выводится из части речи OpenCorpora: VERB - Fin,
        INFN - Inf, PRTF и PRTS - Part, GRND - Conv; степень degree, отрицание
        polarity и краткая форма style_variant - по правилам русского UD
        (_derived_features)
        Время - у глагольных форм и бытийных «нет», «нету» (TENSED_PREDICATIVES), как
        в русском UD: остальным предикативам (надо, нельзя) pymorphy3 дает настоящее
        время, а в UD это наречия без времени
        Переходность и совместность переводятся в Tran, Intr и In, Ex

    Аргументы:
        tag (OpencorporaTag): Тэг OpenCorpora
        lemma (str): Лемма слова
        word (str): Словоформа; без нее имена собственные не выделяются

    Вывод:
        dict[str, str|None]: Признаки по ключам MORPHOLOGY_STATS_DESC
    """
    features: dict[str, str | None] = {"pos": tag_to_ud_pos(tag, lemma, word)}
    derived = _derived_features(tag, lemma)
    for stat in MORPHOLOGY_FEATURES:
        if stat in DERIVED_FEATURES:
            features[stat] = derived[stat]
        elif stat == "tense" and not _has_tense(tag, lemma):
            features[stat] = None
        else:
            found = TAG_GRAMMEMES[stat] & tag.grammemes
            # У слов на -кки pymorphy3 дает и anim, и inan: такой признак не определен
            features[stat] = (
                OPENCORPORA_TO_UD_GRAMMEMES.get(next(iter(found))) if len(found) == 1 else None
            )
    if "ms-f" in tag.grammemes:
        features["gender"] = OPENCORPORA_TO_UD_GRAMMEMES["ms-f"]
    return features


def _derived_features(tag: pymorphy3.tagset.OpencorporaTag, lemma: str) -> dict[str, str | None]:
    """
    Признаки UD, которых нет среди граммем pymorphy3

    Описание:
        Форма глагола - по части речи (OPENCORPORA_VERB_FORMS); степень сравнения,
        как в русском UD, есть у прилагательных и наречий: COMP и «более», «менее»,
        «выше», «ниже» (COMPARATIVE_ADVERBS) - Cmp, превосходная степень (Supr) - Sup, остальные
        прилагательные (кроме местоименных), наречия
        и предикативы (кроме бытийных «нет», «нету») - Pos; отрицание Neg - у частиц
        NEGATIVE_PARTICLES; краткая форма Short - у кратких прилагательных и причастий

    Аргументы:
        tag (OpencorporaTag): Тэг OpenCorpora
        lemma (str): Лемма слова

    Вывод:
        dict[str, str|None]: Значения признаков DERIVED_FEATURES
    """
    pos = tag.POS or ""
    degree = None
    if pos == "COMP" or (pos == "ADVB" and lemma in COMPARATIVE_ADVERBS):
        degree = "Cmp"
    elif "Supr" in tag.grammemes:
        degree = "Sup"
    elif (
        (pos in ("ADJF", "ADJS") and "Apro" not in tag.grammemes)
        or pos == "ADVB"
        or (pos == "PRED" and lemma not in TENSED_PREDICATIVES)
    ):
        degree = "Pos"
    return {
        "degree": degree,
        "polarity": "Neg" if pos == "PRCL" and lemma in NEGATIVE_PARTICLES else None,
        "style_variant": "Short" if pos in SHORT_FORM_POS else None,
        "verb_form": OPENCORPORA_VERB_FORMS.get(pos),
    }


def _has_tense(tag: pymorphy3.tagset.OpencorporaTag, lemma: str) -> bool:
    """Есть ли время у разбора: у глагольных форм и предикативов TENSED_PREDICATIVES"""
    return tag.POS in VERB_POS or lemma in TENSED_PREDICATIVES


def word_to_ud(word: str) -> dict[str, str | None]:
    """
    Получение признаков Universal Dependencies слова по первому разбору pymorphy3

    Аргументы:
        word (str): Слово

    Вывод:
        dict[str, str|None]: Признаки по ключам MORPHOLOGY_STATS_DESC
    """
    return dict(_word_to_ud(word))


@lru_cache(maxsize=131072)
def _word_to_ud(word: str) -> dict[str, str | None]:
    """Признаки word_to_ud с кэшем по словоформе; словарь общий, менять его нельзя"""
    parse = parse_word(word)
    return tag_to_ud(parse.tag, parse.normal_form, word)


@lru_cache(maxsize=1024)
def _particle_to_ud(word: str) -> dict[str, str | None]:
    """Признаки слова по разбору частицей (ответное «нет»); словарь общий, менять его нельзя"""
    parse = next(parse for parse in parse_all(word) if parse.tag.POS == "PRCL")
    return tag_to_ud(parse.tag, parse.normal_form, word)


def _words_to_ud(words: Sequence[str], text: str) -> list[dict[str, str | None]]:
    """
    Получение признаков Universal Dependencies слов текста по первому разбору pymorphy3

    Описание:
        Как word_to_ud, но ответное «нет» (find_answer_particles) - частица с отрицанием
        без времени, а не бытийный предикатив

    Аргументы:
        words (list[str]): Слова текста
        text (str): Текст, из которого извлечены слова

    Вывод:
        list[dict[str, str|None]]: Признаки слов; словари общие, менять их нельзя
    """
    particles = answer_particles(words, text)
    return [
        _particle_to_ud(word) if particle else _word_to_ud(word)
        for word, particle in zip(words, particles, strict=True)
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
def parse_verb(word: str, lemma: str = "") -> pymorphy3.analyzer.Parse | None:
    """
    Получение глагольного разбора словоформы pymorphy3

    Описание:
        Среди всех разборов словоформы выбирается глагольный (VERB, INFN, PRTF, PRTS,
        GRND) с заданной леммой, а при ее отсутствии - первый глагольный: для «стали»
        с леммой «стать» это глагол, а не существительное «сталь»

    Аргументы:
        word (str): Словоформа
        lemma (str): Лемма, которой отдается предпочтение

    Вывод:
        Parse|None: Разбор словоформы, None если глагольных разборов нет
    """
    parses = [parse for parse in parse_all(word) if parse.tag.POS in VERB_POS]
    if not parses:
        return None
    return next((parse for parse in parses if parse.normal_form == lemma), parses[0])


def token_to_ud(token: Token) -> dict[str, str | None]:
    """
    Получение признаков Universal Dependencies токена spaCy

    Описание:
        Часть речи и признаки берутся из token.pos_ и token.morph (признак из нескольких
        значений - через запятую, как в разметке); лицо First, Second,
        Third моделей ru_core_news переводится в 1, 2, 3; краткая форма - StyleVariant
        моделей ru_core_news или Variant=Short разметки русского UD
        Переходность и совместность, которых в русском UD нет, для глаголов (VERB, AUX)
        берутся из глагольного разбора pymorphy3 с леммой spaCy

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
    parse = parse_verb(token.text, token.lemma_) if token.pos_ in ("VERB", "AUX") else None
    tag = parse.tag if parse else None
    features["transitivity"] = OPENCORPORA_TO_UD_GRAMMEMES.get(tag.transitivity) if tag else None
    features["involvement"] = OPENCORPORA_TO_UD_GRAMMEMES.get(tag.involvement) if tag else None
    return features
