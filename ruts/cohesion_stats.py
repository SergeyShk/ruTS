from __future__ import annotations

import re
from collections.abc import Collection, Iterable, Mapping, Sequence
from functools import cache, lru_cache
from itertools import islice
from typing import TYPE_CHECKING, NamedTuple

import anyts
import anyts.cohesion_stats
import rumorph
from anyts.cohesion_stats import (
    CohesionWord,
    Connector as Connector,
    ConnectorMatcher,
    Overlap as Overlap,
    calc_forward_overlap as calc_forward_overlap,
    calc_overlap as calc_overlap,
    calc_overlaps as calc_overlaps,
    calc_proportional_overlap as calc_proportional_overlap,
    calc_repetition as calc_repetition,
    count_given as count_given,
    dice as dice,
    dominant as dominant,
)
from anyts.constants import CONNECTOR_POS, CONTENT_UD_POS
from anyts.utils import (
    BLANK_LINE,
    LINE_BREAK,
    find_marks,
    find_paragraph_starts,
    find_unit_marks,
    find_unit_paragraph_starts,
    has_pos,
    has_sents,
    is_doc,
    source_type_error,
    split_doc_units as split_doc_units,
)

from .constants import (
    COHESION_STATS_DESC,
    CONNECTOR_BLOCKED_AFTER,
    CONNECTOR_BLOCKED_AFTER_POS,
    CONNECTOR_BLOCKED_BEFORE,
    CONNECTOR_NOT_AT_START,
    CONNECTOR_ONLY_AFTER,
    CONNECTOR_PARCELLATION,
    CONNECTOR_POS_EXTRA,
    CONNECTOR_READ_THROUGH_MARKS,
    CONNECTOR_SPLIT_BY_MARKS,
    CONNECTOR_SUBORDINATORS,
    CORE_MESSAGES,
    DEMONSTRATIVE_LEMMAS,
    RESOURCES_DIR,
)
from .exceptions import SourceTypeError
from .extractors import SentsExtractor, WordsExtractor
from .morph_stats import answer_particles, word_to_ud
from .utils import (
    BYTE_ORDER_MARK,
    analyze_sents,
    analyze_words,
    is_predicative,
    is_pronominal,
    lemmatize,
    normalize_yo,
    parse_all,
    parse_word,
    strip_marks,
)

if TYPE_CHECKING:
    from spacy.tokens import Doc, Token

# Римское число - номер главы, который модели размечают прилагательным или существительным
ROMAN_NUMERAL = re.compile(r"(?=[MDCLXVI])M{0,3}(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3})")

CONNECTORS_FILE = RESOURCES_DIR / "connectors.tsv"


class WordInfo(NamedTuple):
    """
    Признаки слова, нужные для статистик связности

    Атрибуты:
        lemma (str): Лемма в нижнем регистре
        noun (bool): Существительное
        pronoun (bool): Местоимение, включая указательные
        demonstrative (bool): Указательное местоимение
        argument (bool): Аргумент - существительное или местоимение-существительное
        content (bool): Знаменательное слово
        tense (str|None): Время глагольной формы
        aspect (str|None): Вид глагольной формы
    """

    lemma: str
    noun: bool
    pronoun: bool
    demonstrative: bool
    argument: bool
    content: bool
    tense: str | None
    aspect: str | None


class RussianConnectorMatcher(ConnectorMatcher):
    """
    Сопоставитель коннекторов ядра anyTS с русскими крючками

    Описание:
        Коннекторы и слова сравниваются в нижнем регистре без буквы ё (normalize_yo);
        однословному коннектору, кроме частей речи CONNECTOR_POS, подходят части речи
        CONNECTOR_POS_EXTRA для отдельных слов (например, словом, главное, допустим, точнее,
        значит, ежели, коли); контекстные правила - списки CONNECTOR_BLOCKED_AFTER,
        CONNECTOR_BLOCKED_BEFORE, CONNECTOR_ONLY_AFTER, CONNECTOR_NOT_AT_START
        и CONNECTOR_BLOCKED_AFTER_POS (после обеда, пока что, ещё раз, не правда ли),
        через знак препинания - только у CONNECTOR_READ_THROUGH_MARKS (не знал, отчего),
        а знак внутри коннектора CONNECTOR_SPLIT_BY_MARKS его разделяет (так, как);
        многословные подчинительные союзы и предлоги и однословные союзы, которые
        модели или ruMorph размечают не SCONJ, - CONNECTOR_SUBORDINATORS (так как,
        после того как, несмотря на, ежели); союзы CONNECTOR_PARCELLATION (ибо)
        в начале предложения связывают его с предыдущим
    """

    pos_extra = CONNECTOR_POS_EXTRA
    blocked_after = CONNECTOR_BLOCKED_AFTER
    blocked_before = CONNECTOR_BLOCKED_BEFORE
    only_after = CONNECTOR_ONLY_AFTER
    not_at_start = CONNECTOR_NOT_AT_START
    blocked_after_pos = CONNECTOR_BLOCKED_AFTER_POS
    read_through_marks = CONNECTOR_READ_THROUGH_MARKS
    split_by_marks = CONNECTOR_SPLIT_BY_MARKS
    subordinators = CONNECTOR_SUBORDINATORS
    parcellation = CONNECTOR_PARCELLATION
    messages = CORE_MESSAGES

    def normalize(self, text: str) -> str:
        """Нижний регистр без буквы ё и знаков ударения (normalize_yo)"""
        return normalize_yo(text)


class CohesionStats(anyts.cohesion_stats.CohesionStats):
    """
    Класс для вычисления статистик связности текста

    Описание:
        Расширяет CohesionStats ядра anyTS крючками русского языка: леммы, части речи,
        время и вид - для Doc с разметкой частей речи по token.pos_ и token.morph
        с леммой разбора ruMorph с частью речи токена (lemmatize), для строки -
        по разбору ruMorph в контексте предложения, для Doc без разметки - так же
        в предложениях, слова которых те же, что у строки, а для остальных слов
        и с заданным экстрактором слов - по первому разбору ruMorph; дефисные слова
        склеиваются; словарь коннекторов - resources/connectors.tsv с классами
        по Криони, Никину и Филипповой (2008), сопоставитель - RussianConnectorMatcher.
        Источником данных может быть строка, в отличие от ядра

    Ссылки:
        https://doi.org/10.1017/CBO9780511894664 (McNamara и др. 2014, Coh-Metrix)
        https://doi.org/10.3758/s13428-015-0651-7 (Crossley и др. 2016, TAACO)

    Пример использования:
        >>> from ruts import CohesionStats
        >>> text = "Кот сидел на окне. Он смотрел на птиц. Птицы улетели, и кот уснул. Завтра он снова будет сидеть на этом окне."
        >>> cs = CohesionStats(text)
        >>> cs.get_stats()
        {'noun_overlap_adjacent': 0.3333333333333333,
        'noun_overlap_all': 0.5,
        'argument_overlap_adjacent': 0.3333333333333333,
        'argument_overlap_all': 0.6666666666666666,
        'content_overlap_adjacent': 0.3333333333333333,
        'content_overlap_all': 0.5,
        'content_overlap_prop_adjacent': 0.1111111111111111,
        'content_overlap_prop_all': 0.19841269841269837,
        'noun_overlap_2_sent': 0.6666666666666666,
        'argument_overlap_2_sent': 0.75,
        'content_overlap_2_sent': 0.4,
        'noun_overlap_para': nan,
        'argument_overlap_para': nan,
        'content_overlap_para': nan,
        'p_pronouns': 0.14285714285714285,
        'pronoun_noun_ratio': 0.5,
        'p_demonstratives': 0.047619047619047616,
        'p_given': 0.3076923076923077,
        'tense_repetition': 0.6666666666666666,
        'aspect_repetition': 0.3333333333333333,
        'temporal_cohesion': 0.5,
        'connectors': 47.61904761904762,
        'connectors_inter': 0.0,
        'connectors_intra': 47.61904761904762,
        'connectors_causal': 0.0,
        'connectors_adversative': 0.0,
        'connectors_concessive': 0.0,
        'connectors_temporal': 0.0,
        'connectors_additive': 47.61904761904762,
        'connectors_conditional': 0.0,
        'connectors_reformulative': 0.0,
        'connectors_primary': 47.61904761904762,
        'connectors_secondary': 0.0}
        >>> cs.lemmas[1]
        ('он', 'смотреть', 'на', 'птица')
        >>> cs.connector_spans
        (Connector(sent=2, start=2, end=3, text='и', cls='additive', kind='primary'),)

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        sents_extractor (SentsExtractor): Инструмент для извлечения предложений;
            если задан, применяется и к тексту Doc
        words_extractor (WordsExtractor): Инструмент для извлечения слов;
            если задан, применяется и к тексту Doc
        connectors (dict[str, tuple[str, str]]): Словарь коннекторов - класс и тип
            по коннектору; если не задан, используется словарь из resources
        blank_lines (bool): Абзацы только после пустых строк - для текста, строки
            которого переносятся внутри абзаца; по умолчанию абзац - строка

    Атрибуты:
        words (tuple[tuple[str, ...], ...]): Кортеж слов каждого предложения
        lemmas (tuple[tuple[str, ...], ...]): Кортеж лемм каждого предложения
        n_sents (int): Количество предложений, содержащих слова
        n_words (int): Количество слов
        n_nouns (int): Количество существительных
        n_pronouns (int): Количество местоимений
        n_demonstratives (int): Количество указательных местоимений
        n_content_words (int): Количество знаменательных слов
        n_given (int): Количество знаменательных слов, лемма которых встречалась ранее
        n_connectors (int): Количество коннекторов
        n_inter_connectors (int): Количество межпредложенческих коннекторов
        n_paragraphs (int): Количество абзацев - строк текста со знаменательными словами
            (частей между пустыми строками с blank_lines); строка без них, например номер
            главы, присоединяется к следующей
        connector_spans (tuple[Connector]): Кортеж вхождений коннекторов
        c_connectors (dict[str, int]): Распределение вхождений по коннекторам
        noun_overlap_adjacent (float): Доля пар соседних предложений с общим существительным
        noun_overlap_all (float): Доля всех пар предложений с общим существительным
        argument_overlap_adjacent (float): Доля пар соседних предложений с общим существительным или местоимением
        argument_overlap_all (float): Доля всех пар предложений с общим существительным или местоимением
        content_overlap_adjacent (float): Доля пар соседних предложений с общим знаменательным словом
        content_overlap_all (float): Доля всех пар предложений с общим знаменательным словом
        content_overlap_prop_adjacent (float): Средняя доля общих знаменательных слов в соседних предложениях
        content_overlap_prop_all (float): Средняя доля общих знаменательных слов во всех парах предложений
        noun_overlap_2_sent (float): Доля существительных предложения, повторенных в одном из двух следующих
        argument_overlap_2_sent (float): Доля аргументов предложения, повторенных в одном из двух следующих
        content_overlap_2_sent (float): Доля знаменательных слов предложения, повторенных в одном из двух следующих
        noun_overlap_para (float): Доля существительных абзаца, повторенных в следующем
        argument_overlap_para (float): Доля аргументов абзаца, повторенных в следующем
        content_overlap_para (float): Доля знаменательных слов абзаца, повторенных в следующем
        p_pronouns (float): Доля местоимений среди слов
        pronoun_noun_ratio (float): Отношение числа местоимений к числу существительных
        p_demonstratives (float): Доля указательных местоимений среди слов
        p_given (float): Доля знаменательных слов, лемма которых встречалась ранее в тексте
        tense_repetition (float): Доля пар соседних предложений с одинаковым преобладающим временем
        aspect_repetition (float): Доля пар соседних предложений с одинаковым преобладающим видом
        temporal_cohesion (float): Среднее повтора времени и вида
        connectors (float): Коннекторов на 1000 слов
        connectors_inter (float): Межпредложенческих коннекторов на 1000 слов: открывают
            предложение и не подчинительный союз (is_subordinator сопоставителя)
        connectors_intra (float): Внутрипредложенческих коннекторов на 1000 слов
        connectors_causal (float): Причинных коннекторов на 1000 слов
        connectors_adversative (float): Противительных коннекторов на 1000 слов
        connectors_concessive (float): Уступительных коннекторов на 1000 слов
        connectors_temporal (float): Временных коннекторов на 1000 слов
        connectors_additive (float): Аддитивных коннекторов на 1000 слов
        connectors_conditional (float): Условных коннекторов на 1000 слов
        connectors_reformulative (float): Переформулирующих коннекторов на 1000 слов
        connectors_primary (float): Первичных коннекторов на 1000 слов
        connectors_secondary (float): Вторичных коннекторов на 1000 слов

    Методы:
        get_stats: Получение вычисленных статистик связности текста
        to_dataframe: Получение статистик таблицей из одной строки
        describe: Прочтение статистики по шкале; шкал нет - None
        print_stats: Отображение вычисленных статистик связности текста с описанием на экран

    Исключения:
        SourceTypeError: Если источник данных не строка и не объект Doc, экстрактор
            другого типа или словарь коннекторов задан неверно
        SourceError: Если в источнике данных отсутствуют слова
        ParameterError: Если в словаре коннекторов неизвестный класс или тип или
            blank_lines не bool
    """

    sents_extractor_class = SentsExtractor
    connector_matcher_class = RussianConnectorMatcher
    join_hyphens = True
    stats_desc = COHESION_STATS_DESC
    stats_headers = ("Статистика", "Значение")
    messages = CORE_MESSAGES

    def __init__(
        self,
        source: str | Doc,
        sents_extractor: anyts.SentsExtractor | None = None,
        words_extractor: anyts.WordsExtractor | None = None,
        connectors: Mapping[str, tuple[str, str]] | None = None,
        blank_lines: bool = False,
    ):
        if words_extractor is not None and not isinstance(words_extractor, anyts.WordsExtractor):
            raise SourceTypeError(self.messages["words_extractor_type"])
        self.words_extractor = words_extractor
        super().__init__(source, sents_extractor, connectors, blank_lines)  # type: ignore[arg-type]

    @classmethod
    def load_connectors(cls) -> dict[str, tuple[str, str]]:
        """Словарь коннекторов resources/connectors.tsv (load_connectors)"""
        return load_connectors()

    def analyze(self, source: str | Doc) -> list[list[CohesionWord]]:
        """
        Слова предложений с признаками по разметке Doc или по ruMorph

        Описание:
            Без экстрактора слов слова Doc берутся из токенов (doc_units), признаки -
            по разметке частей речи (unit_info, unit_pos), а без разметки - по разбору
            ruMorph в контексте в предложениях, слова которых те же, что у строки
            (analyze_words), и по слову в остальных (words_info, connector_pos). Для
            строки и Doc с экстрактором слов предложения - границы Doc или экстрактор
            предложений; слова и признаки строки без экстрактора слов - по разбору
            ruMorph в контексте (analyze_sents), с экстрактором - по слову. Знаки
            препинания между словами - по
            токенам Doc (find_unit_marks) или по тексту предложения (find_marks),
            начала абзацев после перевода строки (пустой строки с blank_lines) - по
            токенам Doc (find_unit_paragraph_starts) или по тексту (find_paragraph_starts)
        """
        if is_doc(source) and self.words_extractor is None:
            units = self.doc_units(source)
            marks = [find_unit_marks(sent) for sent in units]
            starts = find_unit_paragraph_starts(
                [unit for sent in units for unit in sent], self.blank_lines
            )
            if has_pos(source):
                positions = _positions(units)
                return [
                    [
                        _cohesion_word(
                            unit_text(unit),
                            unit_info(unit),
                            unit_pos(unit),
                            i in sent_marks,
                            position in starts,
                        )
                        for i, (unit, position) in enumerate(
                            zip(sent, sent_positions, strict=True)
                        )
                    ]
                    for sent, sent_marks, sent_positions in zip(
                        units, marks, positions, strict=True
                    )
                ]
            sents = [[unit_text(unit) for unit in sent] for sent in units]
            found = iter(
                analyze_words(
                    [(unit[0].idx, unit_text(unit)) for sent in units for unit in sent],
                    source.text,
                )
            )
            by_sent = [[next(found) for _ in sent] for sent in sents]
            return _cohesion_words(sents, source.text, marks, starts, by_sent)
        texts: Iterable[str]
        if isinstance(source, str):
            text = source
            texts = (self.sents_extractor or self.sents_extractor_class()).extract(text)
        elif is_doc(source):
            text = source.text
            if has_sents(source) and not self.sents_extractor:
                texts = tuple(sent.text for sent in source.sents)
            else:
                texts = (self.sents_extractor or self.sents_extractor_class()).extract(text)
        else:
            raise source_type_error(self.messages, source)
        extractor = self.words_extractor or WordsExtractor()
        texts = tuple(texts)
        # Слова строки с экстрактором по умолчанию разбираются в контексте предложения
        analyses = None
        if isinstance(source, str) and self.words_extractor is None:
            sent_pairs = analyze_sents(texts)
            sent_words = [tuple(word for word, _ in pairs) for pairs in sent_pairs]
            analyses = [[analysis for _, analysis in pairs] for pairs in sent_pairs]
        else:
            sent_words = [tuple(extractor.extract(sent)) for sent in texts]
        marks = [
            find_marks(*_searchable(sent, words))
            for sent, words in zip(texts, sent_words, strict=True)
        ]
        starts = _paragraph_starts(text, texts, sent_words, extractor, self.blank_lines)
        return _cohesion_words(sent_words, text, marks, starts, analyses)


def _cohesion_word(
    word: str,
    info: WordInfo,
    pos: str | None,
    break_before: bool = False,
    paragraph_start: bool = False,
) -> CohesionWord:
    """Слово с признаками для каркаса ядра, наклонение не учитывается"""
    return CohesionWord(
        word,
        info.lemma,
        pos,
        info.noun,
        info.pronoun,
        info.demonstrative,
        info.argument,
        info.content,
        info.tense,
        None,
        info.aspect,
        break_before,
        paragraph_start=paragraph_start,
    )


def _searchable(sent: str, words: Sequence[str]) -> tuple[str, list[str]]:
    """Текст и слова для поиска слов в тексте: экстрактор снимает знаки ударения (комбинирующий
    знак не отличить от препинания) и может привести слова к нижнему регистру"""
    return strip_marks(sent).lower(), [strip_marks(word).lower() for word in words]


def _paragraph_starts(
    text: str,
    texts: Sequence[str],
    sent_words: Sequence[Sequence[str]],
    extractor: anyts.WordsExtractor,
    blank_lines: bool,
) -> frozenset[int]:
    """Сквозные номера слов, с которых начинается абзац: между предложениями - в промежутке
    между ними (find_paragraph_starts по текстам предложений), внутри текста предложения -
    по числу слов экстрактора в его частях между переводами строк (пустыми строками
    с blank_lines); абзац, который начинается частью без слов, открывает первое слово следующей"""
    pattern = BLANK_LINE if blank_lines else LINE_BREAK
    after_break = find_paragraph_starts(
        strip_marks(text), [strip_marks(sent) for sent in texts], blank_lines
    )
    starts: set[int] = set()
    position = 0
    pending = False
    for index, (sent, words) in enumerate(zip(texts, sent_words, strict=True)):
        pending = pending or index in after_break
        parts = pattern.split(sent)
        counts = (
            [len(words)] if len(parts) == 1 else [len(extractor.extract(part)) for part in parts]
        )
        worded = [i for i, count in enumerate(counts) if count]
        # N-граммы через пустую строку: внутренние границы неизвестны, края - по частям без слов
        if sum(counts) != len(words) and worded:
            counts = [0] * worded[0] + [len(words)] + [0] * (len(counts) - 1 - worded[-1])
        for i, count in enumerate(counts):
            pending = pending or i > 0
            if count:
                if pending and position:
                    starts.add(position)
                pending = False
                position += count
    return frozenset(starts)


def _positions(sents: Sequence[Sequence[object]]) -> list[range]:
    """Номера слов каждого предложения в сквозной нумерации слов источника"""
    positions = []
    start = 0
    for sent in sents:
        positions.append(range(start, start + len(sent)))
        start += len(sent)
    return positions


def _cohesion_words(
    sents: Sequence[Sequence[str]],
    text: str,
    marks: Sequence[Collection[int]],
    starts: Collection[int] = frozenset(),
    analyses: Sequence[Sequence[rumorph.Analysis | None]] | None = None,
) -> list[list[CohesionWord]]:
    """Слова предложений с признаками по ruMorph, знаками и началами абзацев по сквозным
    номерам слов: по разборам в контексте, а слова без них - по слову (words_info,
    connector_pos)"""
    found = analyses or [[None] * len(sent) for sent in sents]
    infos = words_info(sents, text, found)
    poses = [
        [
            analysis.pos if analysis is not None else connector_pos(word)
            for word, analysis in zip(sent, row, strict=True)
        ]
        for sent, row in zip(sents, found, strict=True)
    ]
    return [
        [
            _cohesion_word(word, info, pos, i in sent_marks, position in starts)
            for i, (word, info, pos, position) in enumerate(
                zip(sent, sent_infos, sent_poses, sent_positions, strict=True)
            )
        ]
        for sent, sent_infos, sent_poses, sent_marks, sent_positions in zip(
            sents, infos, poses, marks, _positions(sents), strict=True
        )
    ]


@cache
def load_connectors() -> dict[str, tuple[str, str]]:
    """
    Загрузка словаря коннекторов

    Описание:
        Файл resources/connectors.tsv: коннектор, класс из CONNECTOR_CLASSES
        и тип из CONNECTOR_TYPES; 316 коннекторов по классификации Криони, Никина
        и Филипповой (2008) со сверкой по маркерам Ru-RSTreebank, базе Рускон
        и списку причинных маркеров Тольдовой и др. (2018)

    Вывод:
        dict[str, tuple[str, str]]: Класс и тип по коннектору
    """
    connectors: dict[str, tuple[str, str]] = {}
    with CONNECTORS_FILE.open(encoding="utf-8") as file:
        next(file)
        for line in file:
            connector, cls, kind = line.rstrip("\n").split("\t")
            connectors[connector] = (cls, kind)
    return connectors


def find_connectors(
    words: Sequence[str],
    connectors: Mapping[str, tuple[str, str]] | None = None,
    sent_index: int = 0,
    pos: Sequence[str | None] | None = None,
    breaks: Collection[int] | None = None,
    blocked: Collection[int] | None = None,
) -> list[Connector]:
    """
    Поиск коннекторов в предложении

    Описание:
        Коннекторы ищутся сопоставителем RussianConnectorMatcher по словоформам
        в нижнем регистре без буквы ё: в каждой позиции берется самый длинный
        («и все же» не распадается на «и»), найденные не пересекаются; дефис и точка
        внутри коннектора (во-первых, т.е.) могут быть отделены токенизатором. Если
        переданы части речи UD, однословный коннектор засчитывается только при части
        речи из CONNECTOR_POS или из CONNECTOR_POS_EXTRA для этого слова. Правила
        о словах до и после коннектора не действуют через знак препинания (breaks);
        со слова из blocked коннектор не начинается

    Аргументы:
        words (list[str]): Слова предложения
        connectors (dict[str, tuple[str, str]]): Словарь коннекторов - класс и тип
            по коннектору; если не задан, используется словарь из resources
        sent_index (int): Номер предложения для записи во вхождения
        pos (list[str]): Части речи UD слов предложения; без них части речи не проверяются
        breaks (list[int]): Номера слов, перед которыми стоит знак препинания (find_marks)
        blocked (set[int]): Номера слов, с которых не начинается коннектор; без них
            коннектор может начаться с любого слова

    Вывод:
        list[Connector]: Вхождения коннекторов в порядке слов

    Исключения:
        SourceTypeError: Если слова не список строк, словарь коннекторов, части речи,
            номера слов со знаком или запрещенных слов заданы неверно
        ParameterError: Если в словаре встречается неизвестный класс или тип, номер
            предложения не целое число, частей речи не столько, сколько слов, номер
            слова со знаком или запрещенного слова не целое число или вне предложения
    """
    matcher = (
        CohesionStats.connector_matcher()
        if connectors is None
        else RussianConnectorMatcher(connectors)
    )
    return matcher.find(words, sent_index, pos, breaks, blocked)


def _is_connector_pos(word: str, pos: str | None) -> bool:
    return pos in CONNECTOR_POS or pos in CONNECTOR_POS_EXTRA.get(word, frozenset())


@lru_cache(maxsize=131072)
def connector_pos(word: str) -> str | None:
    """
    Часть речи UD слова по ruMorph для проверки коннектора

    Описание:
        Из разборов ruMorph берется первый с частью речи, подходящей коннектору
        (CONNECTOR_POS или CONNECTOR_POS_EXTRA для этого слова), иначе часть речи
        первого разбора: у «раз» первый разбор - существительное, подходящий -
        следующий (подчинительный союз). Результаты кэшируются по словоформе

    Аргументы:
        word (str): Слово

    Вывод:
        str|None: Часть речи UD
    """
    normalized = normalize_yo(word)
    poses = [analysis.pos for analysis in parse_all(word)]
    return next((pos for pos in poses if _is_connector_pos(normalized, pos)), poses[0])


def word_info(word: str) -> WordInfo:
    """
    Получение признаков слова по первому разбору ruMorph

    Описание:
        Существительное - NOUN или PROPN, местоимение - PRON, DET или лемма
        из DEMONSTRATIVE_LEMMAS, аргумент - NOUN, PROPN или PRON, знаменательное
        слово - по is_content_word, кроме указательных, время и вид - признаки
        Tense и Aspect разбора

    Аргументы:
        word (str): Слово

    Вывод:
        WordInfo: Признаки слова
    """
    return analysis_info(parse_word(word))


def analysis_info(analysis: rumorph.Analysis) -> WordInfo:
    """
    Получение признаков слова по разбору ruMorph

    Описание:
        Как word_info, но по заданному разбору, например выбранному по контексту
        (ruts.utils.analyze_sentence)

    Аргументы:
        analysis (Analysis): Разбор ruMorph

    Вывод:
        WordInfo: Признаки слова
    """
    demonstrative = analysis.lemma in DEMONSTRATIVE_LEMMAS
    return WordInfo(
        lemma=analysis.lemma,
        noun=analysis.pos in ("NOUN", "PROPN"),
        pronoun=demonstrative or analysis.pos in ("PRON", "DET"),
        demonstrative=demonstrative,
        argument=analysis.pos in ("NOUN", "PROPN", "PRON"),
        content=not demonstrative and _is_content_analysis(analysis),
        tense=analysis.feats.get("Tense"),
        aspect=analysis.feats.get("Aspect"),
    )


def words_info(
    sents: Sequence[Sequence[str]],
    text: str,
    analyses: Sequence[Sequence[rumorph.Analysis | None]] | None = None,
) -> list[list[WordInfo]]:
    """
    Получение признаков слов текста по первому разбору ruMorph

    Описание:
        Как word_info, но ответное «нет» (find_answer_particles) - частица, а не
        бытийное «нет»; слово с заданным разбором (в контексте, analyze_words) -
        по нему (analysis_info)

    Аргументы:
        sents (list[list[str]]): Слова предложений текста
        text (str): Текст, из которого извлечены слова
        analyses (list[list[Analysis|None]]|None): Разборы слов; None - разбор по слову

    Вывод:
        list[list[WordInfo]]: Признаки слов предложений
    """
    particles = iter(answer_particles([word for sent in sents for word in sent], text))
    found = analyses or [[None] * len(sent) for sent in sents]
    return [
        [
            analysis_info(analysis)
            if analysis is not None
            else ud_info(word, "PART", None, None)
            if particle
            else word_info(word)
            for word, analysis, particle in zip(
                sent, row, islice(particles, len(sent)), strict=True
            )
        ]
        for sent, row in zip(sents, found, strict=True)
    ]


def token_info(token: Token) -> WordInfo:
    """
    Получение признаков токена spaCy по разметке Universal Dependencies

    Описание:
        Существительное - NOUN или PROPN, местоимение - PRON, DET или лемма
        из DEMONSTRATIVE_LEMMAS, аргумент - NOUN, PROPN или PRON, знаменательное слово -
        NOUN, PROPN, ADJ, VERB, ADV (CONTENT_UD_POS), кроме указательных, время и вид -
        признаки Tense и Aspect
        Лемма берется из разбора ruMorph с частью речи токена (lemmatize), а не
        из token.lemma_: лемматизатор моделей ru_core_news возвращает словоформу
        для AUX и при расхождении признаков теггера и словаря (были, них, стихли)

    Аргументы:
        token (Token): Токен

    Вывод:
        WordInfo: Признаки слова
    """
    tense = token.morph.get("Tense", [])
    aspect = token.morph.get("Aspect", [])
    return ud_info(
        token.text, token.pos_, tense[0] if tense else None, aspect[0] if aspect else None
    )


def ud_info(word: str, pos: str, tense: str | None, aspect: str | None) -> WordInfo:
    """
    Получение признаков слова по части речи и признакам Universal Dependencies

    Описание:
        Как в token_info: лемма - из разбора ruMorph с частью речи (lemmatize);
        римское число (ROMAN_NUMERAL) - числительное

    Аргументы:
        word (str): Слово
        pos (str): Часть речи UD
        tense (str): Время UD
        aspect (str): Вид UD

    Вывод:
        WordInfo: Признаки слова
    """
    if ROMAN_NUMERAL.fullmatch(word):
        pos = "NUM"
    lemma = lemmatize(word, pos)
    demonstrative = lemma in DEMONSTRATIVE_LEMMAS
    return WordInfo(
        lemma=lemma,
        noun=pos in ("NOUN", "PROPN"),
        pronoun=demonstrative or pos in ("PRON", "DET"),
        demonstrative=demonstrative,
        argument=pos in ("NOUN", "PROPN", "PRON"),
        content=not demonstrative and pos in CONTENT_UD_POS,
        tense=tense,
        aspect=aspect,
    )


def unit_text(unit: Sequence[Token]) -> str:
    """
    Текст слова из токенов iter_doc_units

    Аргументы:
        unit (list[Token]): Токены слова

    Вывод:
        str: Текст слова без BOM, знаков ударения и мягких переносов (strip_marks)
    """
    return strip_marks("".join(token.text for token in unit)).lstrip(BYTE_ORDER_MARK)


def unit_pos(unit: Sequence[Token]) -> str | None:
    """
    Часть речи UD слова из токенов iter_doc_units

    Описание:
        Обычное слово - по разметке токена, дефисное слово из нескольких токенов -
        по разбору ruMorph склеенного текста (connector_pos)

    Аргументы:
        unit (list[Token]): Токены слова

    Вывод:
        str|None: Часть речи UD
    """
    if len(unit) == 1:
        return unit[0].pos_ or None
    return connector_pos(unit_text(unit))


def unit_info(unit: Sequence[Token]) -> WordInfo:
    """
    Получение признаков слова из токенов iter_doc_units

    Описание:
        Обычное слово - по разметке токена (token_info), дефисное слово из нескольких
        токенов - по разбору ruMorph склеенного текста (word_to_ud), чтобы время
        и вид сравнивались с разметкой остальных слов

    Аргументы:
        unit (list[Token]): Токены слова

    Вывод:
        WordInfo: Признаки слова
    """
    if len(unit) == 1:
        return token_info(unit[0])
    text = unit_text(unit)
    features = word_to_ud(text)
    return ud_info(text, features["pos"] or "", features["tense"], features["aspect"])


def is_pronoun(word: str) -> bool:
    """
    Проверка, является ли слово местоимением

    Описание:
        Местоимения-существительные (PRON: он, себя, кто, это) и определительные
        местоимения (DET: этот, который, мой, весь, каждый) по разметке ruMorph

    Аргументы:
        word (str): Слово

    Вывод:
        bool: Результат проверки
    """
    return parse_word(word).pos in ("PRON", "DET")


def is_content_word(word: str) -> bool:
    """
    Проверка, является ли слово знаменательным

    Описание:
        Существительные, имена собственные, прилагательные, глаголы во всех формах
        и наречия (CONTENT_UD_POS) по разметке ruMorph, кроме местоименных (там, тогда,
        где; is_pronominal), вводных (конечно, например, помета Prnt) слов,
        предикативов (надо, можно; is_predicative) и чисел цифрами (2020, 2020-й, XII -
        порядковые прилагательные, признак NumForm)

    Аргументы:
        word (str): Слово

    Вывод:
        bool: Результат проверки
    """
    return _is_content_analysis(parse_word(word))


def _is_content_analysis(analysis: rumorph.Analysis) -> bool:
    """Знаменательное ли слово по разбору (is_content_word)"""
    return (
        analysis.pos in CONTENT_UD_POS
        and not is_pronominal(analysis)
        and "Prnt" not in analysis.labels
        and not is_predicative(analysis)
        and "NumForm" not in analysis.feats
    )
