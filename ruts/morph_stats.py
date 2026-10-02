from collections import Counter, OrderedDict
from functools import cached_property, lru_cache
from math import nan

import anyts
import pymorphy3
from anyts.utils import iter_doc_units, safe_divide
from spacy.tokens import Doc, Token

from .constants import (
    CONDITIONAL_PARTICLES,
    MORPHOLOGY_FEATURES,
    MORPHOLOGY_MARKERS_DESC,
    MORPHOLOGY_STATS_DESC,
    OPENCORPORA_TO_UD_GRAMMEMES,
    OPENCORPORA_TO_UD_POS,
    OPENCORPORA_VERB_FORMS,
    PROPER_NOUN_GRAMMEMES,
    SUBORDINATING_CONJUNCTIONS,
    UD_PERSONS,
)
from .exceptions import SourceError, SourceTypeError, UnknownStatError
from .extractors import WordsExtractor
from .utils import get_morph_analyzer, lemmatize, parse_word

VERB_POS = frozenset(OPENCORPORA_VERB_FORMS)
VERBAL_POS = frozenset({"VERB", "AUX"})
REFLEXIVE_ENDINGS = ("ся", "сь")


class MorphStats:
    """
    Класс для вычисления морфологических статистик текста

    Описание:
        Части речи и грамматические признаки выдаются в терминах Universal Dependencies:
        pos - NOUN, VERB, ADJ, PRON, DET и другие, case - Nom, Gen, Dat, Acc, Ins, Loc,
        так же animacy, aspect, gender, mood, number, person, tense, voice и verb_form
        Для объекта Doc с разметкой частей речи значения берутся из token.pos_
        и token.morph, то есть с учетом контекста (стали - глагол или существительное);
        для строки и Doc без разметки используется первый разбор pymorphy3, граммемы
        OpenCorpora переводятся в UD по таблицам в constants
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
        'gender': {None: 11},
        'involvement': {'Ex': 1, None: 10},
        'mood': {'Imp': 1, None: 7, 'Ind': 3},
        'number': {'Plur': 3, None: 7, 'Sing': 1},
        'person': {None: 9, '2': 1, '3': 1},
        'tense': {None: 8, 'Pres': 1, 'Fut': 1, 'Past': 1},
        'transitivity': {'Intr': 2, 'Tran': 4, None: 5},
        'verb_form': {'Fin': 4, 'Inf': 2, None: 5},
        'voice': {None: 11}}
        >>> ms.tags[0]
        'Aspect=Perf|Clusivity=Ex|Mood=Imp|Number=Plur|Subcat=Intr|VerbForm=Fin'

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        words_extractor (WordsExtractor): Инструмент для извлечения слов

    Атрибуты:
        words (tuple[str]): Кортеж извлеченных слов
        lemmas (tuple[str]): Кортеж лемм слов: pymorphy3 с учетом части речи слова
        tags (tuple[str]): Кортеж строк грамматических признаков в формате CoNLL-U
        pos (tuple[str]): Кортеж значений части речи
        animacy (tuple[str]): Кортеж значений одушевленности
        aspect (tuple[str]): Кортеж значений вида
        case (tuple[str]): Кортеж значений падежа
        gender (tuple[str]): Кортеж значений рода
        involvement (tuple[str]): Кортеж значений совместности
        mood (tuple[str]): Кортеж значений наклонения
        number (tuple[str]): Кортеж значений числа
        person (tuple[str]): Кортеж значений лица
        tense (tuple[str]): Кортеж значений времени
        transitivity (tuple[str]): Кортеж значений переходности
        verb_form (tuple[str]): Кортеж значений формы глагола
        voice (tuple[str]): Кортеж значений залога

    Методы:
        get_stats: Получение вычисленных морфологических статистик текста
        explain_text: Разбор текста по морфологическим статистикам
        print_stats: Отображение вычисленных морфологических статистик текста с описанием на экран
        get_markers: Получение долей грамматических форм глагола
        print_markers: Отображение долей грамматических форм глагола с описанием на экран

    Исключения:
        SourceTypeError: Если передаваемое значение не является строкой или объектом Doc
        SourceError: Если в источнике данных отсутствуют слова
    """

    def __init__(self, source: str | Doc, words_extractor: WordsExtractor | None = None):
        if words_extractor is not None and not isinstance(words_extractor, anyts.WordsExtractor):
            raise SourceTypeError("Экстрактор слов должен быть WordsExtractor")
        features: list[dict[str, str | None]]
        if isinstance(source, Doc):
            units = list(iter_doc_units(source, join_hyphens=True))
            self.words = tuple("".join(token.text for token in unit) for unit in units)
            if source.has_annotation("POS"):
                features = [
                    token_to_ud(unit[0]) if len(unit) == 1 else word_to_ud(word)
                    for unit, word in zip(units, self.words, strict=True)
                ]
            else:
                features = [word_to_ud(word) for word in self.words]
        elif isinstance(source, str):
            if not words_extractor:
                words_extractor = WordsExtractor()
            self.words = words_extractor.extract(source)
            features = [word_to_ud(word) for word in self.words]
        else:
            raise SourceTypeError("Некорректный источник данных")
        if not self.words:
            raise SourceError("В источнике данных отсутствуют слова")

        self.tags = tuple(format_features(word_features) for word_features in features)
        self.pos = tuple(word_features["pos"] for word_features in features)
        self.animacy = tuple(word_features["animacy"] for word_features in features)
        self.aspect = tuple(word_features["aspect"] for word_features in features)
        self.case = tuple(word_features["case"] for word_features in features)
        self.gender = tuple(word_features["gender"] for word_features in features)
        self.involvement = tuple(word_features["involvement"] for word_features in features)
        self.mood = tuple(word_features["mood"] for word_features in features)
        self.number = tuple(word_features["number"] for word_features in features)
        self.person = tuple(word_features["person"] for word_features in features)
        self.tense = tuple(word_features["tense"] for word_features in features)
        self.transitivity = tuple(word_features["transitivity"] for word_features in features)
        self.verb_form = tuple(word_features["verb_form"] for word_features in features)
        self.voice = tuple(word_features["voice"] for word_features in features)

    @cached_property
    def lemmas(self) -> tuple[str, ...]:
        """Леммы слов: pymorphy3 с учетом части речи слова"""
        return tuple(
            lemmatize(word, pos or "") for word, pos in zip(self.words, self.pos, strict=True)
        )

    def get_stats(self, *args: str, filter_none: bool = False) -> dict[str, dict[str, int]]:
        """
        Получение вычисленных морфологических статистик текста

        Аргументы:
            args (tuple[str]): Кортеж выбранных статистик
            filter_none (bool): Фильтровать пустые значения

        Вывод:
            dict[str, dict[str, int]]: Справочник вычисленных морфологических статистик текста
        """
        if not args:
            args = tuple(MORPHOLOGY_STATS_DESC.keys())
        else:
            self.__check_stat(*args)
        stats: dict[str, dict[str, int]] = {}
        for arg in args:
            counts = dict(Counter(getattr(self, arg)))
            stats[arg] = {k: v for (k, v) in counts.items() if k} if filter_none else counts
        return stats

    def explain_text(
        self, *args: str, filter_none: bool = False
    ) -> tuple[tuple[str, dict[str, str]], ...]:
        """
        Разбор текста по морфологическим статистикам

        Аргументы:
            args (tuple[str]): Кортеж выбранных статистик
            filter_none (bool): Фильтровать пустые значения

        Вывод:
            tuple[str, dict[str, str]]: Кортеж слов текста с морфологическими статистиками
        """
        if not args:
            args = tuple(MORPHOLOGY_STATS_DESC.keys())
        else:
            self.__check_stat(*args)
        values = tuple(zip(*(getattr(self, arg) for arg in args), strict=False))
        if filter_none:
            explains = tuple(
                {k: v for (k, v) in dict(zip(args, value, strict=False)).items() if v}
                for value in values
            )
        else:
            explains = tuple(dict(zip(args, value, strict=False)) for value in values)
        return tuple(zip(self.words, explains, strict=False))

    def print_stats(self, *args: str, filter_none: bool = False) -> None:
        """
        Отображение вычисленных морфологических статистик текста с описанием на экран

        Аргументы:
            args (tuple[str]): Кортеж выбранных статистик
            filter_none (bool): Фильтровать пустые значения
        """
        if not args:
            args = tuple(MORPHOLOGY_STATS_DESC.keys())
        else:
            self.__check_stat(*args)
        stats = self.get_stats(*args)
        for stat, values in stats.items():
            stat_desc = MORPHOLOGY_STATS_DESC[stat]
            print(f"{stat_desc['name'].center(40, '-')}")
            value_desc = stat_desc["values"]
            for value, number in OrderedDict(
                sorted(values.items(), key=lambda x: x[1], reverse=True)
            ).items():
                if filter_none and not value:
                    continue
                print(
                    f"{value_desc.get(value, value) if value else 'Неизвестно':30}|{number!s:^10}"
                )
            print()

    def get_markers(self) -> dict[str, float]:
        """
        Получение долей грамматических форм глагола

        Описание:
            Доли форм глагола (VERB и AUX), каждая от своей базы: наклонения - от личных
            форм, совершенный вид - от форм с видом, остальные - от всех форм глагола;
            доля с пустой базой - nan. Сослагательное наклонение определяется по частице
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
        forms = Counter(self.verb_form[index] for index in verbs)
        moods = Counter(self.mood[index] for index in verbs if self.verb_form[index] == "Fin")
        aspects = Counter(self.aspect[index] for index in verbs if self.aspect[index])
        n_forms = len(verbs)
        n_finite = forms["Fin"]
        n_particles = sum(
            word.lower() in CONDITIONAL_PARTICLES and word != "Б" for word in self.words
        )
        n_past = sum(
            self.verb_form[index] == "Fin"
            and self.mood[index] == "Ind"
            and self.tense[index] == "Past"
            for index in verbs
        )
        n_conditional = min(n_particles, n_past)
        n_passive = sum(
            self.verb_form[index] == "Part" and self.voice[index] == "Pass" for index in verbs
        )
        n_reflexive = sum(self.words[index].lower().endswith(REFLEXIVE_ENDINGS) for index in verbs)
        return {
            "p_indicative": safe_divide(moods["Ind"] - n_conditional, n_finite, nan),
            "p_imperative": safe_divide(moods["Imp"], n_finite, nan),
            "p_conditional": safe_divide(moods["Cnd"] + n_conditional, n_finite, nan),
            "p_infinitive": safe_divide(forms["Inf"], n_forms, nan),
            "p_participle": safe_divide(forms["Part"], n_forms, nan),
            "p_converb": safe_divide(forms["Conv"], n_forms, nan),
            "p_perfective": safe_divide(aspects["Perf"], sum(aspects.values()), nan),
            "p_passive": safe_divide(n_passive, n_forms, nan),
            "p_reflexive": safe_divide(n_reflexive, n_forms, nan),
        }

    def print_markers(self) -> None:
        """
        Отображение долей грамматических форм глагола с описанием на экран

        Пример использования:
            >>> from ruts import MorphStats
            >>> MorphStats("Иди сюда и не спорь").print_markers()
                                Маркер                     | Значение
            ---------------------------------------------------------------
            Изъявительное наклонение среди личных форм       |   0.00
            Повелительное наклонение среди личных форм       |   1.00
            Сослагательное наклонение среди личных форм      |   0.00
            Инфинитив среди форм глагола                     |   0.00
            Причастие среди форм глагола                     |   0.00
            Деепричастие среди форм глагола                  |   0.00
            Совершенный вид среди форм глагола с видом       |   0.00
            Страдательные причастия среди форм глагола       |   0.00
            Возвратные формы (-ся, -сь) среди форм глагола   |   0.00
        """
        markers = self.get_markers()
        print(f"{'Маркер':^50}|{'Значение':^12}")
        print("-" * 63)
        for marker, desc in MORPHOLOGY_MARKERS_DESC.items():
            print(f"{desc:50}|{markers[marker]:^12.2f}")

    @staticmethod
    def __check_stat(*args: str) -> bool:
        """
        Проверка выбранных морфологических статистик

        Аргументы:
            args (tuple[str]): Кортеж выбранных статистик

        Вывод:
            bool: Результат проверки

        Исключения:
            UnknownStatError: Если выбранная статистика отсутствует в справочнике
        """
        for arg in args:
            if arg not in MORPHOLOGY_STATS_DESC:
                raise UnknownStatError(
                    f"{arg} отсутствует в справочнике морфологических статистик, "
                    f"доступны: {', '.join(MORPHOLOGY_STATS_DESC)}"
                )
        return True


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
        INFN - Inf, PRTF и PRTS - Part, GRND - Conv
        Переходность и совместность переводятся в Tran, Intr и In, Ex

    Аргументы:
        tag (OpencorporaTag): Тэг OpenCorpora
        lemma (str): Лемма слова
        word (str): Словоформа; без нее имена собственные не выделяются

    Вывод:
        dict[str, str|None]: Признаки по ключам MORPHOLOGY_STATS_DESC
    """
    features: dict[str, str | None] = {"pos": tag_to_ud_pos(tag, lemma, word)}
    for stat in MORPHOLOGY_FEATURES:
        if stat == "verb_form":
            features[stat] = OPENCORPORA_VERB_FORMS.get(tag.POS or "")
        else:
            features[stat] = OPENCORPORA_TO_UD_GRAMMEMES.get(getattr(tag, stat))
    if "ms-f" in tag.grammemes:
        features["gender"] = OPENCORPORA_TO_UD_GRAMMEMES["ms-f"]
    return features


def word_to_ud(word: str) -> dict[str, str | None]:
    """
    Получение признаков Universal Dependencies слова по первому разбору pymorphy3

    Аргументы:
        word (str): Слово

    Вывод:
        dict[str, str|None]: Признаки по ключам MORPHOLOGY_STATS_DESC
    """
    parse = parse_word(word)
    return tag_to_ud(parse.tag, parse.normal_form, word)


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
    parses = [parse for parse in get_morph_analyzer().parse(word) if parse.tag.POS in VERB_POS]
    if not parses:
        return None
    return next((parse for parse in parses if parse.normal_form == lemma), parses[0])


def token_to_ud(token: Token) -> dict[str, str | None]:
    """
    Получение признаков Universal Dependencies токена spaCy

    Описание:
        Часть речи и признаки берутся из token.pos_ и token.morph; лицо First, Second,
        Third моделей ru_core_news переводится в 1, 2, 3
        Переходность и совместность, которых в русском UD нет, для глаголов (VERB, AUX)
        берутся из глагольного разбора pymorphy3 с леммой spaCy

    Аргументы:
        token (Token): Токен

    Вывод:
        dict[str, str|None]: Признаки по ключам MORPHOLOGY_STATS_DESC
    """
    features: dict[str, str | None] = {"pos": token.pos_ or None}
    for stat, feature in MORPHOLOGY_FEATURES.items():
        values = token.morph.get(feature, [])
        features[stat] = values[0] if values else None
    features["person"] = UD_PERSONS.get(features["person"] or "", features["person"])
    parse = parse_verb(token.text, token.lemma_) if token.pos_ in ("VERB", "AUX") else None
    tag = parse.tag if parse else None
    features["transitivity"] = OPENCORPORA_TO_UD_GRAMMEMES.get(tag.transitivity) if tag else None
    features["involvement"] = OPENCORPORA_TO_UD_GRAMMEMES.get(tag.involvement) if tag else None
    return features


def format_features(features: dict[str, str | None]) -> str:
    """
    Запись признаков слова строкой в формате CoNLL-U

    Описание:
        Признаки перечисляются через | в алфавитном порядке названий UD
        (Animacy=Inan|Case=Nom|Gender=Masc|Number=Sing), часть речи не включается,
        переходность и совместность записываются как Subcat и Clusivity;
        для слова без признаков возвращается _

    Аргументы:
        features (dict[str, str|None]): Признаки по ключам MORPHOLOGY_STATS_DESC

    Вывод:
        str: Строка признаков
    """
    pairs = sorted(
        (feature, features[stat])
        for stat, feature in MORPHOLOGY_FEATURES.items()
        if features.get(stat)
    )
    return "|".join(f"{feature}={value}" for feature, value in pairs) or "_"
