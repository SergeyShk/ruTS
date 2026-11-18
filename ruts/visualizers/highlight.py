from __future__ import annotations

import re
from collections.abc import Callable, Collection, Iterable, Mapping, Sequence
from typing import TYPE_CHECKING

import anyts.style_stats
import anyts.visualizers.highlight
from anyts.constants import ALLITERATION_MIN_WORD_LEN, ALLITERATION_THRESHOLD
from anyts.document import get_tree
from anyts.style_stats import WordFlags
from anyts.syntax_stats import get_subtree
from anyts.utils import check_words, has_words
from anyts.visualizers.highlight import (
    Highlight as Highlight,
    Sent as Sent,
    Word as Word,
    group_words_by_sents as group_words_by_sents,
    tokens_span,
)

from .. import style_stats
from ..cohesion_stats import CohesionStats, connector_pos
from ..constants import (
    ALLITERATION_IGNORED_LETTERS,
    COMPLEX_SYL_FACTOR,
    COMPOUND_PREPOSITIONS,
    CONNECTOR_CLASSES,
    CONNECTOR_TYPES,
    CORE_MESSAGES,
    HIGHLIGHT_ANNOTATION_NAMES,
    HIGHLIGHT_DEFAULT_LAYERS,
    HIGHLIGHT_LAYER_ANNOTATIONS,
    HIGHLIGHT_LAYER_STYLES,
    HIGHLIGHT_LAYERS_DESC,
    LONG_SENT_WORD_FACTOR,
    OFFICIALESE_CLICHES,
    PARENTHETICALS,
    RU_LETTER_FREQUENCIES,
)
from ..lexical_stats import get_rank
from ..style_stats import (
    _doc_flags,
    expand_phrases,
    is_parenthetical,
    is_stopword,
    is_water_word,
)
from ..syllables import CONSONANTS, LETTERS, VOWELS, count_syllables
from ..syntax_stats import (
    _find_split_predicates,
    _get_lemma,
    _is_converb_clause,
    _is_genitive_modifier,
    _is_participle_clause,
    get_children,
    get_words,
    is_agentless,
    is_passive,
    subtree_len,
)
from ..utils import (
    BYTE_ORDER_MARK,
    get_document,
    normalize_yo,
    parse_word,
    strip_marks,
    word_form,
)

if TYPE_CHECKING:
    from anyseg import Document
    from anyts.document import TreeWord
    from spacy.tokens import Doc

RUSSIAN_WORD = re.compile(r"[а-яёА-ЯЁ][а-яёА-ЯЁ-]+")
ALLITERATION_FREQUENCIES = {
    consonant: RU_LETTER_FREQUENCIES[consonant]
    for consonant in sorted(CONSONANTS - ALLITERATION_IGNORED_LETTERS)
}


class HighlightedText(anyts.visualizers.highlight.HighlightedText):
    """
    Класс для подсветки текста по слоям в стиле Главреда и Тургенева

    Описание:
        Каждый слой отмечает фрагменты, по которым считаются статистики библиотеки:
            long_sents - предложения с числом слов не меньше long_sent_word_factor
            complex_words - слова с числом слогов не меньше complex_syl_factor
            rare_words - слова с леммой вне 10 000 самых частых лемм
            passive - пассивные глагольные формы вместе со вспомогательным глаголом
            participle_clauses - причастные обороты
            converb_clauses - деепричастные обороты
            genitive_chains - цепочки родительных падежей с управляющим словом
            split_predicates - расщепленные сказуемые от глагола до именной части
            verbal_nouns - отглагольные существительные
            compound_prepositions - производные предлоги
            cliches - штампы
            stopwords - слова «воды»
            parentheticals - вводные слова и обороты
            connectors - коннекторы с классом и типом в подсказке
            alliteration - повторы согласной в соседних словах, маловероятные при
                частотах букв русского языка
        Синтаксические слои (от passive до split_predicates) доступны только для объекта
        Doc или Document с разбором зависимостей; строка и Doc без границ предложений
        делятся на предложения anySeg. Фрагменты разных слоев могут пересекаться. В Jupyter
        результат отображается как HTML с легендой

    Пример использования:
        >>> from ruts.visualizers import highlight
        >>> text = "Чуть слышно, бесшумно шуршат камыши. Повышение эффективности использования ресурсов обсуждалось."
        >>> ht = highlight(text)
        >>> ht.counts
        {'long_sents': 0, 'complex_words': 4, 'cliches': 0}
        >>> ht = highlight(text, layers="all")
        >>> ht.counts
        {'long_sents': 0, 'complex_words': 4, 'rare_words': 2, 'verbal_nouns': 2, 'compound_prepositions': 0, 'cliches': 0, 'stopwords': 0, 'parentheticals': 0, 'connectors': 0, 'alliteration': 1}
        >>> ht.highlights[0]
        Highlight(start=5, end=35, layer='alliteration', note='аллитерация на «ш»')
        >>> highlight(text, layers="alliteration").to_html(legend=False, css=False)
        '<div class="ruts-highlight"><div class="ruts-highlight-text">Чуть <span class="ruts-hl ruts-hl-alliteration" title="аллитерация на «ш»">слышно, бесшумно шуршат камыши</span>. ...'

    Аргументы:
        source (str|Doc|Document): Источник данных (строка, объект Doc или Document)
        layers (list[str]|str): Слои подсветки; если не заданы, включаются слои
            HIGHLIGHT_DEFAULT_LAYERS, доступные источнику; "all" - все доступные
        long_sent_word_factor (int): Минимальное количество слов в длинном предложении
        complex_syl_factor (int): Минимальное количество слогов в сложном слове
        stopwords (list[str]): Список слов «воды»; если не задан, они определяются
            по разбору ruMorph
        cliches (list[str]): Список штампов; если не задан, используется OFFICIALESE_CLICHES
        alliteration_threshold (float): Порог вероятности повтора согласной при независимом
            распределении букв, ниже которого повтор считается аллитерацией

    Атрибуты:
        text (str): Текст источника данных
        layers (tuple[str]): Включенные слои подсветки в порядке отрисовки
        highlights (tuple[Highlight]): Подсвеченные фрагменты в порядке появления в тексте
        counts (dict[str, int]): Количество фрагментов каждого слоя

    Методы:
        to_html: Получение HTML-разметки подсвеченного текста
        css: Получение стилей слоев

    Исключения:
        SourceTypeError: Если источник данных не строка, не объект Doc и не Document,
            а стоп-слова или штампы - набором строк
        SourceError: Если в источнике данных отсутствуют слова
        ParameterError: Если задан неизвестный или недоступный источнику слой
            или пороги слоев заданы некорректно
    """

    layers_desc = HIGHLIGHT_LAYERS_DESC
    default_layers = HIGHLIGHT_DEFAULT_LAYERS
    layer_annotations = HIGHLIGHT_LAYER_ANNOTATIONS
    layer_styles = HIGHLIGHT_LAYER_STYLES
    css_prefix = "ruts"
    annotation_names = HIGHLIGHT_ANNOTATION_NAMES
    messages = CORE_MESSAGES

    def __init__(
        self,
        source: str | Doc | Document,
        layers: Sequence[str] | str | None = None,
        long_sent_word_factor: int = LONG_SENT_WORD_FACTOR,
        complex_syl_factor: int = COMPLEX_SYL_FACTOR,
        stopwords: Collection[str] | None = None,
        cliches: Collection[str] | None = None,
        alliteration_threshold: float = ALLITERATION_THRESHOLD,
    ):
        anyts.visualizers.highlight.check_params(
            long_sent_word_factor,
            complex_syl_factor,
            alliteration_threshold,
            messages=self.messages,
        )
        if stopwords is not None:
            check_words(stopwords, "stopwords", ordered=False)
            stopwords = tuple(stopwords)
        if cliches is not None:
            check_words(cliches, "clichés", ordered=False)
            cliches = tuple(cliches)
        self._long_sent_word_factor = long_sent_word_factor
        self._complex_syl_factor = complex_syl_factor
        self._stopwords = stopwords
        self._cliches = cliches
        self._alliteration_threshold = alliteration_threshold
        self._flags: WordFlags | None = None
        super().__init__(source, layers)

    def parse(self, source: str | Doc | Document) -> Document:
        """Документ anySeg (ruts.utils.get_document)"""
        return get_document(source)

    def doc_words(self, document: Document) -> list[Word]:
        """Слова документа с позициями по get_doc_words"""
        return get_doc_words(document)

    def _doc_flags(self, doc: Document) -> WordFlags:
        """Флаги слов документа по разборам в контексте (ruts.style_stats._doc_flags), один раз"""
        if self._flags is None:
            self._flags = _doc_flags(doc)
        return self._flags

    def find(
        self, layer: str, words: Sequence[Word], sents: Sequence[Sent], doc: Document
    ) -> list[Highlight]:
        """
        Поиск фрагментов слоя

        Аргументы:
            layer (str): Слой подсветки
            words (list[Word]): Слова текста с позициями
            sents (list[Sent]): Предложения текста с позициями
            doc (Document): Документ источника (parse)

        Вывод:
            list[Highlight]: Фрагменты слоя
        """
        if layer in SYNTAX_FINDERS:
            return SYNTAX_FINDERS[layer](doc)
        finders: dict[str, Callable[[], list[Highlight]]] = {
            "long_sents": lambda: find_long_sents(sents, self._long_sent_word_factor),
            "complex_words": lambda: find_complex_words(words, self._complex_syl_factor),
            "rare_words": lambda: find_rare_words(words),
            "stopwords": lambda: find_stopwords(
                words, self._stopwords, flags=self._doc_flags(doc).water
            ),
            "verbal_nouns": lambda: find_verbal_nouns(words),
            "compound_prepositions": lambda: find_compound_prepositions(words),
            "cliches": lambda: find_cliches(words, self._cliches),
            "parentheticals": lambda: find_parentheticals(
                words, flags=self._doc_flags(doc).parenthetical
            ),
            "connectors": lambda: find_connector_highlights(words, sents, self.text),
            "alliteration": lambda: find_alliteration(words, self._alliteration_threshold, sents),
        }
        return finders[layer]()


def highlight(
    source: str | Doc | Document,
    layers: Sequence[str] | str | None = None,
    long_sent_word_factor: int = LONG_SENT_WORD_FACTOR,
    complex_syl_factor: int = COMPLEX_SYL_FACTOR,
    stopwords: Collection[str] | None = None,
    cliches: Collection[str] | None = None,
    alliteration_threshold: float = ALLITERATION_THRESHOLD,
) -> HighlightedText:
    """
    Подсветка текста по слоям в стиле Главреда и Тургенева

    Описание:
        Слои и их доступность описаны в классе HighlightedText

    Аргументы:
        source (str|Doc|Document): Источник данных (строка, объект Doc или Document)
        layers (list[str]|str): Слои подсветки; если не заданы, включаются слои
            HIGHLIGHT_DEFAULT_LAYERS, доступные источнику; "all" - все доступные
        long_sent_word_factor (int): Минимальное количество слов в длинном предложении
        complex_syl_factor (int): Минимальное количество слогов в сложном слове
        stopwords (list[str]): Список слов «воды»; если не задан, они определяются
            по разбору ruMorph
        cliches (list[str]): Список штампов; если не задан, используется OFFICIALESE_CLICHES
        alliteration_threshold (float): Порог вероятности повтора согласной при независимом
            распределении букв, ниже которого повтор считается аллитерацией

    Вывод:
        HighlightedText: Подсвеченный текст с HTML-представлением для Jupyter
    """
    return HighlightedText(
        source,
        layers,
        long_sent_word_factor=long_sent_word_factor,
        complex_syl_factor=complex_syl_factor,
        stopwords=stopwords,
        cliches=cliches,
        alliteration_threshold=alliteration_threshold,
    )


def get_doc_words(source: Doc | Document) -> list[Word]:
    """
    Извлечение слов с позициями из документа anySeg

    Описание:
        Токены с буквой или цифрой без знаков ударения, мягких переносов и точки
        сокращения (word_form); при разметке у слова есть часть речи UD и лемма

    Аргументы:
        source (Doc|Document): Объект Doc или документ anySeg (get_document)

    Вывод:
        list[Word]: Слова с позициями
    """
    words = []
    for token in get_document(source).tokens:
        text = token.text
        if not has_words(text):
            continue
        word = word_form(strip_marks(text).lstrip(BYTE_ORDER_MARK))
        start = token.start + len(text) - len(text.lstrip(BYTE_ORDER_MARK))
        first = token.words[0]
        words.append(Word(start, token.end, word, first.upos or None, first.lemma or None))
    return words


def plural(n: int, one: str, few: str, many: str) -> str:
    """
    Согласование существительного с числительным

    Аргументы:
        n (int): Число
        one (str): Форма для 1 (слово)
        few (str): Форма для 2-4 (слова)
        many (str): Форма для 5-20 (слов)

    Вывод:
        str: Число с существительным
    """
    if n % 10 == 1 and n % 100 != 11:
        form = one
    elif 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        form = few
    else:
        form = many
    return f"{n} {form}"


def find_long_sents(sents: Iterable[Sent], long_sent_word_factor: int) -> list[Highlight]:
    """
    Поиск длинных предложений

    Аргументы:
        sents (list[Sent]): Предложения с позициями и числом слов
        long_sent_word_factor (int): Минимальное количество слов в длинном предложении

    Вывод:
        list[Highlight]: Фрагменты слоя long_sents

    Исключения:
        ParameterError: Если количество слов не целое число или меньше единицы
    """
    return anyts.visualizers.highlight.find_long_sents(
        sents,
        long_sent_word_factor,
        lambda n: f"длинное предложение, {plural(n, 'слово', 'слова', 'слов')}",
    )


def find_complex_words(words: Iterable[Word], complex_syl_factor: int) -> list[Highlight]:
    """
    Поиск сложных слов

    Аргументы:
        words (list[Word]): Слова с позициями
        complex_syl_factor (int): Минимальное количество слогов в сложном слове

    Вывод:
        list[Highlight]: Фрагменты слоя complex_words

    Исключения:
        ParameterError: Если количество слогов не целое число или меньше единицы
    """
    return anyts.visualizers.highlight.find_complex_words(
        words,
        complex_syl_factor,
        count_syllables,
        lambda n: f"сложное слово, {plural(n, 'слог', 'слога', 'слогов')}",
    )


def find_stopwords(
    words: Sequence[Word],
    stopwords: Collection[str] | None = None,
    *,
    flags: Sequence[bool] | None = None,
) -> list[Highlight]:
    """
    Поиск слов «воды»

    Аргументы:
        words (list[Word]): Слова с позициями
        stopwords (list[str]): Список слов «воды», без учета регистра и буквы ё; если
            не задан, слова «воды» определяются флагами или по части речи (is_water_word)
        flags (list[bool]): Является ли «водой» каждое слово words

    Вывод:
        list[Highlight]: Фрагменты слоя stopwords
    """
    if stopwords is not None:
        chosen = {normalize_yo(word) for word in stopwords}
        return anyts.visualizers.highlight.find_words(
            words, lambda word: normalize_yo(word.text) in chosen, "stopwords", "стоп-слово"
        )
    if flags is not None:
        water = {word.start for word, flag in zip(words, flags, strict=True) if flag}
        return anyts.visualizers.highlight.find_words(
            words, lambda word: word.start in water, "stopwords", "стоп-слово"
        )
    return anyts.visualizers.highlight.find_words(
        words, lambda word: is_water_word(word.text.lower()), "stopwords", "стоп-слово"
    )


def find_rare_words(words: Iterable[Word]) -> list[Highlight]:
    """
    Поиск редких слов

    Описание:
        Слова, лемма которых вне 10 000 самых частых лемм (get_rank), как в доле
        p_beyond_top10000 класса LexicalStats; учитываются слова из русских букв
        длиной от двух букв, кроме стоп-слов

    Аргументы:
        words (list[Word]): Слова с позициями

    Вывод:
        list[Highlight]: Фрагменты слоя rare_words
    """
    return anyts.visualizers.highlight.find_words(
        words,
        lambda word: bool(
            RUSSIAN_WORD.fullmatch(word.text)
            and not is_stopword(word.text.lower())
            and get_rank(parse_word(word.text).lemma) is None
        ),
        "rare_words",
        "редкое слово: вне топ-10000",
    )


def find_verbal_nouns(words: Iterable[Word]) -> list[Highlight]:
    """
    Поиск отглагольных существительных

    Описание:
        Существительные ruts.style_stats.find_verbal_nouns

    Аргументы:
        words (list[Word]): Слова с позициями

    Вывод:
        list[Highlight]: Фрагменты слоя verbal_nouns
    """
    words = list(words)
    spans = style_stats.find_verbal_nouns([word.text for word in words])
    starts = {words[start].start for start, _ in spans}
    return anyts.visualizers.highlight.find_words(
        words, lambda word: word.start in starts, "verbal_nouns", "отглагольное существительное"
    )


def find_phrase_highlights(
    words: Sequence[Word], phrases: Collection[str] | Mapping[str, str], layer: str, label: str
) -> list[Highlight]:
    """
    Поиск словосочетаний из списка

    Описание:
        Словосочетания ищутся без учета регистра и буквы ё, фрагмент покрывает слова
        от первого до последнего; в подсказке - словарная форма словосочетания

    Аргументы:
        words (list[Word]): Слова с позициями
        phrases (list[str]|dict[str, str]): Словосочетания через пробел или варианты
            словосочетаний с их словарной формой (expand_phrases)
        layer (str): Слой подсветки
        label (str): Подпись фрагмента в подсказке

    Вывод:
        list[Highlight]: Фрагменты слоя

    Исключения:
        SourceTypeError: Если словосочетания не список строк или словарь вариантов
    """
    return anyts.visualizers.highlight.find_phrase_highlights(
        words, phrases, layer, lambda phrase: f"{label}: «{phrase}»", normalize_yo
    )


def find_compound_prepositions(words: Sequence[Word]) -> list[Highlight]:
    """
    Поиск производных предлогов по списку COMPOUND_PREPOSITIONS

    Аргументы:
        words (list[Word]): Слова с позициями

    Вывод:
        list[Highlight]: Фрагменты слоя compound_prepositions
    """
    return find_phrase_highlights(
        words, COMPOUND_PREPOSITIONS, "compound_prepositions", "производный предлог"
    )


def find_cliches(words: Sequence[Word], cliches: Collection[str] | None = None) -> list[Highlight]:
    """
    Поиск штампов

    Аргументы:
        words (list[Word]): Слова с позициями
        cliches (list[str]): Список штампов; если не задан, используется OFFICIALESE_CLICHES

    Вывод:
        list[Highlight]: Фрагменты слоя cliches
    """
    phrases = OFFICIALESE_CLICHES if cliches is None else cliches
    expanded = expand_phrases([word.text for word in words], phrases)
    return find_phrase_highlights(words, expanded, "cliches", "штамп")


def find_parentheticals(
    words: Sequence[Word], *, flags: Sequence[bool] | None = None
) -> list[Highlight]:
    """
    Поиск вводных слов

    Описание:
        Обороты из PARENTHETICALS и вводные слова, как в ruts.style_stats.find_parentheticals

    Аргументы:
        words (list[Word]): Слова с позициями
        flags (list[bool]): Является ли вводным каждое слово words; если не заданы -
            is_parenthetical

    Вывод:
        list[Highlight]: Фрагменты слоя parentheticals
    """
    highlights = find_phrase_highlights(words, PARENTHETICALS, "parentheticals", "вводный оборот")
    phrases = {highlight.start for highlight in highlights}
    for start, _ in anyts.style_stats.find_parentheticals(
        [word.text for word in words],
        PARENTHETICALS,
        is_parenthetical=is_parenthetical,
        flags=flags,
        expand=expand_phrases,
        normalize=normalize_yo,
    ):
        if words[start].start not in phrases:
            word = words[start]
            highlights.append(Highlight(word.start, word.end, "parentheticals", "вводное слово"))
    return sorted(highlights, key=lambda h: h.start)


def find_connector_highlights(
    words: Sequence[Word], sents: Sequence[Sent] | None, text: str | None = None
) -> list[Highlight]:
    """
    Поиск коннекторов

    Описание:
        Коннекторы CohesionStats ищутся внутри каждого предложения; однословные
        проверяются по части речи из разметки документа, а без нее - по ruMorph;
        в подсказке класс и тип коннектора

    Аргументы:
        words (list[Word]): Слова с позициями
        sents (list[Sent]): Предложения с позициями; None - весь текст одним предложением
        text (str): Текст слов; если задан, правила о соседних словах коннектора
            не действуют через знак препинания между ними

    Вывод:
        list[Highlight]: Фрагменты слоя connectors
    """
    return anyts.visualizers.highlight.find_connector_highlights(
        words,
        sents or None,
        CohesionStats.connector_matcher(),
        lambda connector: (
            f"коннектор «{connector.text}»: {CONNECTOR_CLASSES[connector.cls]}, "
            f"{CONNECTOR_TYPES[connector.kind]}"
        ),
        lambda word: word.pos or connector_pos(word.text),
        text,
    )


def get_stem(word: str) -> str:
    """
    Получение основы словоформы

    Описание:
        Основа - общая начальная часть словоформы и ее леммы по ruMorph (руках → рук);
        если она короче двух букв (шла → идти), основа - вся словоформа

    Аргументы:
        word (str): Словоформа в нижнем регистре

    Вывод:
        str: Основа словоформы
    """
    lemma = parse_word(word).lemma
    length = 0
    for letter, lemma_letter in zip(word, lemma, strict=False):
        if letter != lemma_letter:
            break
        length += 1
    return word[:length] if length >= 2 else word


def _stem_letters(word: str) -> list[str]:
    """Буквы основы слова (get_stem)"""
    return [letter for letter in get_stem(word) if letter in LETTERS]


def _is_transparent(word: str) -> bool:
    """Слово, которое не прерывает и не продолжает повтор: короткое, без гласных или стоп-слово"""
    letters = [letter for letter in word if letter in LETTERS]
    return (
        len(letters) < ALLITERATION_MIN_WORD_LEN
        or not any(letter in VOWELS for letter in letters)
        or is_stopword(word)
    )


def calc_alliteration_runs(
    text: Sequence[str], threshold: float = ALLITERATION_THRESHOLD
) -> list[tuple[int, int, str]]:
    """
    Поиск повторов согласной в соседних словах

    Описание:
        Согласная ищется в основе слова (get_stem), й не учитывается; слова короче
        трех букв, без гласных и стоп-слова повтор не прерывают и не продолжают
        (по полю плыл - повтор п); частоты согласных - RU_LETTER_FREQUENCIES

    Ссылки:
        https://ru.wikipedia.org/wiki/Частотность

    Аргументы:
        text (list[str]): Список слов
        threshold (float): Порог вероятности повтора согласной при независимом
            распределении букв, ниже которого повтор считается аллитерацией

    Вывод:
        list[tuple[int, int, str]]: Индексы первого и за последним словом цепочки
            и согласная в порядке появления в тексте

    Исключения:
        SourceTypeError: Если слова не список строк
        ParameterError: Если порог не лежит в интервале (0, 1]
    """
    return anyts.visualizers.highlight.calc_alliteration_runs(
        text, ALLITERATION_FREQUENCIES, threshold, _stem_letters, _is_transparent
    )


def find_alliteration(
    words: Sequence[Word],
    threshold: float = ALLITERATION_THRESHOLD,
    sents: Sequence[Sent] | None = None,
) -> list[Highlight]:
    """
    Поиск аллитераций

    Описание:
        Повторы calc_alliteration_runs ищутся внутри предложений

    Аргументы:
        words (list[Word]): Слова с позициями
        threshold (float): Порог вероятности повтора согласной, см. calc_alliteration_runs
        sents (list[Sent]): Предложения с позициями; если не заданы, текст считается
            одним предложением

    Вывод:
        list[Highlight]: Фрагменты слоя alliteration

    Исключения:
        ParameterError: Если порог не лежит в интервале (0, 1]
    """
    return anyts.visualizers.highlight.find_alliteration(
        words,
        sents,
        ALLITERATION_FREQUENCIES,
        threshold,
        _stem_letters,
        _is_transparent,
        lambda consonant: f"аллитерация на «{consonant}»",
    )


def find_passive(doc: Document) -> list[Highlight]:
    """
    Поиск пассивных глагольных форм

    Описание:
        Форма подсвечивается вместе со вспомогательным глаголом (был продан)

    Аргументы:
        doc (Document): Документ anySeg с разбором зависимостей

    Вывод:
        list[Highlight]: Фрагменты слоя passive
    """
    highlights = []
    for token in get_words(get_tree(doc).words):
        if is_passive(token):
            auxiliaries = [child for child in get_children(token) if child.deprel == "aux:pass"]
            start, end = tokens_span([token, *auxiliaries])
            note = "пассив без агенса" if is_agentless(token) else "пассив"
            highlights.append(Highlight(start, end, "passive", note))
    return highlights


def find_participle_clauses(doc: Document) -> list[Highlight]:
    """
    Поиск причастных оборотов

    Аргументы:
        doc (Document): Документ anySeg с разбором зависимостей

    Вывод:
        list[Highlight]: Фрагменты слоя participle_clauses
    """
    highlights = []
    for token in get_words(get_tree(doc).words):
        if _is_participle_clause(token):
            start, end = tokens_span(get_subtree(token))
            n_words = subtree_len(token)
            note = f"причастный оборот, {plural(n_words, 'слово', 'слова', 'слов')}"
            highlights.append(Highlight(start, end, "participle_clauses", note))
    return highlights


def find_converb_clauses(doc: Document) -> list[Highlight]:
    """
    Поиск деепричастных оборотов

    Аргументы:
        doc (Document): Документ anySeg с разбором зависимостей

    Вывод:
        list[Highlight]: Фрагменты слоя converb_clauses
    """
    highlights = []
    for token in get_words(get_tree(doc).words):
        if _is_converb_clause(token):
            start, end = tokens_span(get_subtree(token))
            n_words = subtree_len(token)
            note = f"деепричастный оборот, {plural(n_words, 'слово', 'слова', 'слов')}"
            highlights.append(Highlight(start, end, "converb_clauses", note))
    return highlights


def find_split_predicate_highlights(doc: Document) -> list[Highlight]:
    """
    Поиск расщепленных сказуемых

    Описание:
        Фрагмент покрывает пару легкий глагол - именная часть (find_split_predicates)
        от первого до последнего слова: осуществляет плановую проверку

    Аргументы:
        doc (Document): Документ anySeg с разбором зависимостей

    Вывод:
        list[Highlight]: Фрагменты слоя split_predicates
    """
    return anyts.visualizers.highlight.find_split_predicate_highlights(
        _find_split_predicates(get_tree(doc).words),
        lambda verb, noun: f"расщепленное сказуемое: {_get_lemma(verb)} {_get_lemma(noun)}",
    )


def _genitive_chain(token: TreeWord) -> tuple[list[TreeWord], int]:
    tokens = [token]
    depth = 1
    for child in get_children(token):
        if _is_genitive_modifier(child):
            child_tokens, child_depth = _genitive_chain(child)
            tokens += child_tokens
            depth = max(depth, child_depth + 1)
    return tokens, depth


def find_genitive_chains(doc: Document) -> list[Highlight]:
    """
    Поиск цепочек родительных падежей

    Описание:
        Цепочка - два и более вложенных беспредложных определения в родительном падеже;
        фрагмент покрывает управляющее слово и все определения цепочки (повышение
        эффективности использования ресурсов)

    Аргументы:
        doc (Document): Документ anySeg с разбором зависимостей

    Вывод:
        list[Highlight]: Фрагменты слоя genitive_chains
    """
    highlights = []
    for token in get_words(get_tree(doc).words):
        head = token.head or token
        if not _is_genitive_modifier(token) or _is_genitive_modifier(head):
            continue
        chain, depth = _genitive_chain(token)
        if depth < 2:
            continue
        start, end = tokens_span([head, *chain])
        note = f"цепочка из {plural(depth, 'родительного', 'родительных', 'родительных')}"
        highlights.append(Highlight(start, end, "genitive_chains", note))
    return highlights


SYNTAX_FINDERS: dict[str, Callable[[Document], list[Highlight]]] = {
    "passive": find_passive,
    "participle_clauses": find_participle_clauses,
    "converb_clauses": find_converb_clauses,
    "genitive_chains": find_genitive_chains,
    "split_predicates": find_split_predicate_highlights,
}
