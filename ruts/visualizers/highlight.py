import re
from collections.abc import Callable, Collection, Iterable, Iterator, Mapping, Sequence

import anyts.visualizers.highlight
from anyts.utils import check_integer, check_number, check_words, iter_doc_units
from anyts.visualizers.highlight import (
    Highlight as Highlight,
    Sent,
    Word,
    group_words_by_sents,
    tokens_span,
)
from spacy.tokens import Doc, Token

from .. import style_stats
from ..cohesion_stats import connector_pos, find_connectors, unit_pos, unit_text
from ..constants import (
    ALLITERATION_IGNORED_LETTERS,
    ALLITERATION_MIN_WORD_LEN,
    ALLITERATION_THRESHOLD,
    COMPLEX_SYL_FACTOR,
    COMPOUND_PREPOSITIONS,
    CONNECTOR_CLASSES,
    CONNECTOR_TYPES,
    HIGHLIGHT_DEFAULT_LAYERS,
    HIGHLIGHT_LAYER_ANNOTATIONS,
    HIGHLIGHT_LAYER_STYLES,
    HIGHLIGHT_LAYERS_DESC,
    LONG_SENT_WORD_FACTOR,
    OFFICIALESE_CLICHES,
    PARENTHETICALS,
    RU_LETTER_FREQUENCIES,
)
from ..exceptions import ParameterError
from ..lexical_stats import get_rank
from ..style_stats import expand_phrases, is_stopword
from ..syllables import CONSONANTS, LETTERS, VOWELS, count_syllables
from ..syntax_stats import (
    find_split_predicates,
    get_children,
    get_lemma,
    get_words,
    is_agentless,
    is_converb_clause,
    is_genitive_modifier,
    is_participle_clause,
    is_passive,
    subtree_len,
)
from ..utils import (
    BYTE_ORDER_MARK,
    find_phrases,
    iter_text_sents,
    iter_text_words,
    normalize_yo,
    parse_word,
)

RUSSIAN_WORD = re.compile(r"[а-яёА-ЯЁ][а-яёА-ЯЁ-]+")


class HighlightedText(anyts.visualizers.highlight.HighlightedText):
    """
    Класс для подсветки текста по слоям в стиле Главреда и Тургенева

    Описание:
        Каждый слой отмечает фрагменты, по которым считаются статистики библиотеки:
            long_sents - предложения с числом слов не меньше long_sent_word_factor (BasicStats, ReadabilityStats)
            complex_words - слова с числом слогов не меньше complex_syl_factor (BasicStats, ReadabilityStats)
            rare_words - слова с леммой вне вшитого списка топ-10000 (LexicalStats)
            passive - пассивные глагольные формы вместе со вспомогательным глаголом (SyntaxStats)
            participle_clauses - причастные обороты (SyntaxStats)
            converb_clauses - деепричастные обороты (SyntaxStats)
            genitive_chains - цепочки родительных падежей с управляющим словом (SyntaxStats)
            split_predicates - расщепленные сказуемые от глагола до именной части (SyntaxStats)
            verbal_nouns - отглагольные существительные (StyleStats)
            compound_prepositions - производные предлоги (StyleStats)
            cliches - штампы по списку OFFICIALESE_CLICHES или переданному (StyleStats)
            stopwords - стоп-слова по части речи или переданному списку, «вода» текста (StyleStats)
            parentheticals - вводные слова и обороты (StyleStats)
            connectors - коннекторы с классом и типом в подсказке (CohesionStats)
            alliteration - повторы согласной в соседних словах, маловероятные при частотах букв русского языка (PhonStats)
        Слои сгруппированы в HIGHLIGHT_LAYER_GROUPS: читаемость, синтаксис, канцелярит,
        стиль, фоника. Синтаксические слои считаются по дереву зависимостей и доступны
        только для объекта Doc с разбором зависимостей; Doc без границ предложений
        делится на предложения razdel. По умолчанию включаются слои HIGHLIGHT_DEFAULT_LAYERS
        (длинные предложения, сложные слова, пассив, цепочки родительных, расщепленные
        сказуемые, штампы), доступные источнику; layers="all" включает все доступные
        Результат отображается в Jupyter как HTML со стилями и легендой, метод to_html
        возвращает ту же разметку для документации и веб-приложений; фрагменты разных слоев
        могут пересекаться

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
        source (str|Doc): Источник данных (строка или объект Doc)
        layers (list[str]|str): Слои подсветки; если не заданы, включаются слои
            HIGHLIGHT_DEFAULT_LAYERS, доступные источнику; "all" - все доступные
        long_sent_word_factor (int): Минимальное количество слов в длинном предложении
        complex_syl_factor (int): Минимальное количество слогов в сложном слове
        stopwords (list[str]): Список стоп-слов; если не задан, стоп-слова определяются
            по части речи с помощью pymorphy3
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
        SourceTypeError: Если передаваемое значение не является строкой или объектом Doc,
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

    def __init__(
        self,
        source: str | Doc,
        layers: Sequence[str] | str | None = None,
        long_sent_word_factor: int = LONG_SENT_WORD_FACTOR,
        complex_syl_factor: int = COMPLEX_SYL_FACTOR,
        stopwords: Collection[str] | None = None,
        cliches: Collection[str] | None = None,
        alliteration_threshold: float = ALLITERATION_THRESHOLD,
    ):
        check_integer(long_sent_word_factor, "number of words in a long sentence")
        check_integer(complex_syl_factor, "number of syllables in a complex word")
        if long_sent_word_factor < 1:
            raise ParameterError("Количество слов в длинном предложении должно быть больше 0")
        if complex_syl_factor < 1:
            raise ParameterError("Количество слогов в сложном слове должно быть больше 0")
        check_number(alliteration_threshold, "threshold of the alliteration")
        if not 0 < alliteration_threshold <= 1:
            raise ParameterError("Порог аллитерации должен быть в интервале (0, 1]")
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
        super().__init__(source, layers)

    def iter_words(self, text: str) -> Iterator[tuple[int, int, str]]:
        """Слова строки с позициями по iter_text_words, без знаков препинания"""
        return iter_text_words(text)

    def iter_sents(self, text: str) -> Iterator[tuple[int, int, str]]:
        """Предложения строки с позициями по iter_text_sents"""
        return iter_text_sents(text)

    def doc_words(self, doc: Doc) -> list[Word]:
        """Слова объекта Doc с позициями по get_doc_words"""
        return get_doc_words(doc)

    def find(
        self, layer: str, words: Sequence[Word], sents: Sequence[Sent], doc: Doc | None
    ) -> list[Highlight]:
        """
        Поиск фрагментов слоя

        Аргументы:
            layer (str): Слой подсветки
            words (list[Word]): Слова текста с позициями
            sents (list[Sent]): Предложения текста с позициями
            doc (Doc): Объект Doc источника; None для строки

        Вывод:
            list[Highlight]: Фрагменты слоя
        """
        if layer in SYNTAX_FINDERS:
            return SYNTAX_FINDERS[layer](doc) if doc is not None else []
        finders: dict[str, Callable[[], list[Highlight]]] = {
            "long_sents": lambda: find_long_sents(sents, self._long_sent_word_factor),
            "complex_words": lambda: find_complex_words(words, self._complex_syl_factor),
            "rare_words": lambda: find_rare_words(words),
            "stopwords": lambda: find_stopwords(words, self._stopwords),
            "verbal_nouns": lambda: find_verbal_nouns(words),
            "compound_prepositions": lambda: find_compound_prepositions(words),
            "cliches": lambda: find_cliches(words, self._cliches),
            "parentheticals": lambda: find_parentheticals(words),
            "connectors": lambda: find_connector_highlights(words, sents),
            "alliteration": lambda: find_alliteration(words, self._alliteration_threshold, sents),
        }
        return finders[layer]()


def highlight(
    source: str | Doc,
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
        Слои из HIGHLIGHT_LAYERS_DESC: длинные предложения, сложные и редкие слова,
        пассив, обороты, цепочки родительных, расщепленные сказуемые, отглагольные
        существительные, производные предлоги, штампы, стоп-слова, вводные слова,
        коннекторы, аллитерация; синтаксические слои доступны только для объекта Doc
        с разбором зависимостей, подробнее в классе HighlightedText

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        layers (list[str]|str): Слои подсветки; если не заданы, включаются слои
            HIGHLIGHT_DEFAULT_LAYERS, доступные источнику; "all" - все доступные
        long_sent_word_factor (int): Минимальное количество слов в длинном предложении
        complex_syl_factor (int): Минимальное количество слогов в сложном слове
        stopwords (list[str]): Список стоп-слов; если не задан, стоп-слова определяются
            по части речи с помощью pymorphy3
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


def get_doc_words(doc: Doc) -> list[Word]:
    """
    Извлечение слов с позициями из объекта Doc

    Описание:
        Слова iter_doc_units, дефисные слова - одним словом; при разметке частей
        речи слово получает часть речи UD (unit_pos)

    Аргументы:
        doc (Doc): Объект Doc

    Вывод:
        list[Word]: Слова с позициями
    """
    tagged = doc.has_annotation("POS")
    words = []
    for unit in iter_doc_units(doc, join_hyphens=True):
        text = unit_text(unit)
        word = text.lstrip(BYTE_ORDER_MARK)
        start = unit[0].idx + len(text) - len(word)
        end = unit[-1].idx + len(unit[-1])
        words.append(Word(start, end, word, unit_pos(unit) if tagged else None))
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
    """
    return [
        Highlight(
            sent.start,
            sent.end,
            "long_sents",
            f"длинное предложение, {plural(sent.n_words, 'слово', 'слова', 'слов')}",
        )
        for sent in sents
        if sent.n_words >= long_sent_word_factor
    ]


def find_complex_words(words: Iterable[Word], complex_syl_factor: int) -> list[Highlight]:
    """
    Поиск сложных слов

    Аргументы:
        words (list[Word]): Слова с позициями
        complex_syl_factor (int): Минимальное количество слогов в сложном слове

    Вывод:
        list[Highlight]: Фрагменты слоя complex_words
    """
    highlights = []
    for word in words:
        n_syllables = count_syllables(word.text)
        if n_syllables >= complex_syl_factor:
            note = f"сложное слово, {plural(n_syllables, 'слог', 'слога', 'слогов')}"
            highlights.append(Highlight(word.start, word.end, "complex_words", note))
    return highlights


def find_stopwords(
    words: Iterable[Word], stopwords: Collection[str] | None = None
) -> list[Highlight]:
    """
    Поиск стоп-слов

    Описание:
        Стоп-слова определяются по части речи (функция is_stopword) или по переданному
        списку без учета регистра, как при вычислении водности в StyleStats

    Аргументы:
        words (list[Word]): Слова с позициями
        stopwords (list[str]): Список стоп-слов; если не задан, используется разметка pymorphy3

    Вывод:
        list[Highlight]: Фрагменты слоя stopwords
    """
    if stopwords is not None:
        stopwords_set = {word.lower() for word in stopwords}
        matches = [word for word in words if word.text.lower() in stopwords_set]
    else:
        matches = [word for word in words if is_stopword(word.text.lower())]
    return [Highlight(word.start, word.end, "stopwords", "стоп-слово") for word in matches]


def find_rare_words(words: Iterable[Word]) -> list[Highlight]:
    """
    Поиск редких слов

    Описание:
        Слова, лемма которых (первый разбор pymorphy3) отсутствует во вшитом списке
        10 000 самых частых лемм (get_rank), как в доле p_beyond_top10000 класса
        LexicalStats; учитываются только слова из русских букв длиной от двух букв,
        числа, латиница, сокращения (т.е.) и стоп-слова (во-первых) не подсвечиваются

    Аргументы:
        words (list[Word]): Слова с позициями

    Вывод:
        list[Highlight]: Фрагменты слоя rare_words
    """
    return [
        Highlight(word.start, word.end, "rare_words", "редкое слово: вне топ-10000")
        for word in words
        if RUSSIAN_WORD.fullmatch(word.text)
        and not is_stopword(word.text.lower())
        and get_rank(parse_word(word.text).normal_form) is None
    ]


def find_verbal_nouns(words: Iterable[Word]) -> list[Highlight]:
    """
    Поиск отглагольных существительных

    Описание:
        Слова ruts.style_stats.find_verbal_nouns, как в доле verbal_nouns класса StyleStats

    Аргументы:
        words (list[Word]): Слова с позициями

    Вывод:
        list[Highlight]: Фрагменты слоя verbal_nouns
    """
    words = list(words)
    spans = style_stats.find_verbal_nouns([word.text for word in words])
    note = "отглагольное существительное"
    return [
        Highlight(words[start].start, words[start].end, "verbal_nouns", note) for start, _ in spans
    ]


def find_phrase_highlights(
    words: Sequence[Word], phrases: Iterable[str] | Mapping[str, str], layer: str, label: str
) -> list[Highlight]:
    """
    Поиск словосочетаний из списка

    Описание:
        Словосочетания ищутся по словоформам (find_phrases), фрагмент покрывает
        слова от первого до последнего вместе со знаками между ними; в подсказке -
        словарная форма словосочетания

    Аргументы:
        words (list[Word]): Слова с позициями
        phrases (list[str]|dict[str, str]): Словосочетания через пробел или варианты
            словосочетаний с их словарной формой (expand_phrases)
        layer (str): Слой подсветки
        label (str): Подпись фрагмента в подсказке

    Вывод:
        list[Highlight]: Фрагменты слоя
    """
    pairs = (
        phrases.items()
        if isinstance(phrases, Mapping)
        else ((phrase, phrase) for phrase in phrases)
    )
    forms: dict[str, str] = {}
    for variant, phrase in pairs:
        forms.setdefault(" ".join(normalize_yo(variant).split()), phrase)
    texts = [word.text for word in words]
    highlights = []
    for start, end in find_phrases(texts, forms):
        phrase = forms[" ".join(normalize_yo(word) for word in texts[start:end])]
        note = f"{label}: «{phrase}»"
        highlights.append(Highlight(words[start].start, words[end - 1].end, layer, note))
    return highlights


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


def find_parentheticals(words: Sequence[Word]) -> list[Highlight]:
    """
    Поиск вводных слов

    Описание:
        Вводные обороты и слова ruts.style_stats.find_parentheticals, как
        в calc_parentheticals; у оборота в подсказке - его форма из PARENTHETICALS

    Аргументы:
        words (list[Word]): Слова с позициями

    Вывод:
        list[Highlight]: Фрагменты слоя parentheticals
    """
    highlights = find_phrase_highlights(words, PARENTHETICALS, "parentheticals", "вводный оборот")
    phrases = {highlight.start for highlight in highlights}
    for start, _ in style_stats.find_parentheticals([word.text for word in words]):
        if words[start].start not in phrases:
            word = words[start]
            highlights.append(Highlight(word.start, word.end, "parentheticals", "вводное слово"))
    return sorted(highlights, key=lambda h: h.start)


def find_connector_highlights(
    words: Sequence[Word], sents: Sequence[Sent] | None
) -> list[Highlight]:
    """
    Поиск коннекторов

    Описание:
        Коннекторы ищутся внутри каждого предложения (find_connectors), без границ
        предложений - по всему тексту; однословные коннекторы проверяются по части
        речи слова из разметки Doc, а без нее - по pymorphy3 (connector_pos), так
        «раз» и «значит» как существительное и глагол не считаются; в подсказке
        класс и тип коннектора

    Аргументы:
        words (list[Word]): Слова с позициями
        sents (list[Sent]): Предложения с позициями; None, если границы неизвестны

    Вывод:
        list[Highlight]: Фрагменты слоя connectors
    """
    groups = group_words_by_sents(words, sents) if sents else [list(words)]
    highlights = []
    for group in groups:
        texts = [word.text for word in group]
        pos = [word.pos or connector_pos(word.text) for word in group]
        for connector in find_connectors(texts, sent_index=0, pos=pos):
            note = (
                f"коннектор «{connector.text}»: {CONNECTOR_CLASSES[connector.cls]}, "
                f"{CONNECTOR_TYPES[connector.kind]}"
            )
            highlights.append(
                Highlight(
                    group[connector.start].start, group[connector.end - 1].end, "connectors", note
                )
            )
    return highlights


def get_stem(word: str) -> str:
    """
    Получение основы словоформы

    Описание:
        Основа - общая начальная часть словоформы и ее леммы по pymorphy3:
        крупных → крупн, руках → рук, шуршат → шурша, камыши → камыш
        Для супплетивных форм (шла → идти, люди → человек) общая часть короче
        двух букв, и основой считается вся словоформа

    Аргументы:
        word (str): Словоформа в нижнем регистре

    Вывод:
        str: Основа словоформы
    """
    lemma = parse_word(word).normal_form
    length = 0
    for letter, lemma_letter in zip(word, lemma, strict=False):
        if letter != lemma_letter:
            break
        length += 1
    return word[:length] if length >= 2 else word


def calc_alliteration_runs(
    text: Sequence[str], threshold: float = ALLITERATION_THRESHOLD
) -> list[tuple[int, int, str]]:
    """
    Поиск повторов согласной в соседних словах

    Описание:
        Повтор - цепочка из двух и более соседних слов, в основе каждого из которых
        есть одна и та же согласная буква; слова короче трех букв, стоп-слова и слова
        без гласных цепочку не прерывают и не продолжают (по полю плыл - повтор п)
        Согласная ищется в основе слова (функция get_stem), а не в окончании:
        окончания согласуются с соседними словами и повторяются по грамматике,
        а не по звучанию - этих крупных, своим целям и нуждам, в других губерниях
        Буква й не учитывается и в основе, так как в именительном падеже она входит
        в лемму прилагательного (красивый молодой)
        Вероятность цепочки при независимом распределении букв - произведение по словам
        вероятностей встретить согласную хотя бы раз среди букв основы, 1 - (1 - f)^n,
        где f - частота согласной в русских текстах, n - число букв в основе;
        цепочка считается аллитерацией, если вероятность ниже порога
        На каждой позиции проверяется около двадцати согласных, поэтому порог
        по умолчанию строгий: на прозе при 0.001 подсвечено около 5% слов,
        при 0.01 - около 20%, в основном случайные совпадения частых букв
        Так три соседних 5-буквенных основы с ш дают 0.00005, две - 0.0013,
        а цепочка из четырех 8-буквенных основ с т - 0.04: повтор редкой согласной
        заметен в двух-трех словах, повтор частой в длинных словах ожидаем
        и аллитерацией не считается
        Индекс аллитерации PhonStats измеряет сгруппированность повторов во всем тексте,
        здесь ищутся их места

    Ссылки:
        https://ru.wikipedia.org/wiki/Частотность

    Аргументы:
        text (list[str]): Список слов
        threshold (float): Порог вероятности

    Вывод:
        list[tuple[int, int, str]]: Индексы первого и за последним словом цепочки
            и согласная в порядке появления в тексте
    """
    words = [word.lower() for word in text]
    letters = [[letter for letter in word if letter in LETTERS] for word in words]
    transparent = [
        len(word_letters) < ALLITERATION_MIN_WORD_LEN
        or not any(letter in VOWELS for letter in word_letters)
        or is_stopword(word)
        for word, word_letters in zip(words, letters, strict=True)
    ]
    stems = [[letter for letter in get_stem(word) if letter in LETTERS] for word in words]
    runs = []
    for consonant in sorted(CONSONANTS - ALLITERATION_IGNORED_LETTERS):
        frequency = RU_LETTER_FREQUENCIES[consonant]
        start = None
        stop = 0
        probability = 1.0
        for i, stem in enumerate(stems):
            if transparent[i]:
                continue
            if consonant in stem:
                if start is None:
                    start, probability = i, 1.0
                stop = i + 1
                probability *= 1 - (1 - frequency) ** len(stem)
            elif start is not None:
                if stop - start >= 2 and probability < threshold:
                    runs.append((start, stop, consonant))
                start = None
        if start is not None and stop - start >= 2 and probability < threshold:
            runs.append((start, stop, consonant))
    return sorted(runs)


def find_alliteration(
    words: Sequence[Word],
    threshold: float = ALLITERATION_THRESHOLD,
    sents: Sequence[Sent] | None = None,
) -> list[Highlight]:
    """
    Поиск аллитераций

    Описание:
        Повторы ищутся внутри предложений; если границы предложений не заданы,
        текст считается одним предложением

    Аргументы:
        words (list[Word]): Слова с позициями
        threshold (float): Порог вероятности повтора согласной, см. calc_alliteration_runs
        sents (list[Sent]): Предложения с позициями

    Вывод:
        list[Highlight]: Фрагменты слоя alliteration
    """
    groups = [list(words)] if sents is None else group_words_by_sents(words, sents)
    highlights = []
    for group in groups:
        for start, stop, consonant in calc_alliteration_runs(
            [word.text for word in group], threshold
        ):
            note = f"аллитерация на «{consonant}»"
            highlights.append(
                Highlight(group[start].start, group[stop - 1].end, "alliteration", note)
            )
    return highlights


def _word_tokens(doc: Doc) -> Callable[[Iterable[Token]], list[Token]]:
    """
    Функция, дополняющая токены слов всеми частями их дефисных слов

    Аргументы:
        doc (Doc): Объект Doc

    Вывод:
        Callable[[Iterable[Token]], list[Token]]: Токены вместе с частями их слов
    """
    units = {token.i: unit for unit in iter_doc_units(doc, join_hyphens=True) for token in unit}
    return lambda tokens: [part for token in tokens for part in units.get(token.i, [token])]


def _clause_span(token: Token, units: Mapping[int, list[Token]]) -> tuple[int, int]:
    """
    Позиции фрагмента оборота: слова поддерева токена, представленные в нем
    своей частью (get_words), со всеми частями

    Аргументы:
        token (Token): Вершина оборота
        units (Mapping[int, list[Token]]): Токены слов по номеру представляющей части

    Вывод:
        tuple[int, int]: Позиция первого символа и позиция за последним символом
    """
    return tokens_span([part for child in token.subtree for part in units.get(child.i, ())])


def _units_by_word(doc: Doc) -> dict[int, list[Token]]:
    """
    Токены каждого слова Doc по номеру части, которой слово представлено (get_words)

    Аргументы:
        doc (Doc): Объект Doc

    Вывод:
        dict[int, list[Token]]: Токены слов
    """
    return {
        get_words(unit, join_hyphens=True)[0].i: unit
        for unit in iter_doc_units(doc, join_hyphens=True)
    }


def find_passive(doc: Doc) -> list[Highlight]:
    """
    Поиск пассивных глагольных форм

    Описание:
        Форма подсвечивается вместе со вспомогательным глаголом (был продан);
        знаки препинания пропускаются, даже если модель пометила их глаголом
        (тире между подлежащим и сказуемым)

    Аргументы:
        doc (Doc): Объект Doc с разбором зависимостей

    Вывод:
        list[Highlight]: Фрагменты слоя passive
    """
    highlights = []
    word_tokens = _word_tokens(doc)
    for token in get_words(doc, join_hyphens=True):
        if is_passive(token):
            auxiliaries = [
                child
                for child in get_children(token, join_hyphens=True)
                if child.dep_ == "aux:pass"
            ]
            start, end = tokens_span(word_tokens([token, *auxiliaries]))
            note = "пассив без агенса" if is_agentless(token) else "пассив"
            highlights.append(Highlight(start, end, "passive", note))
    return highlights


def find_participle_clauses(doc: Doc) -> list[Highlight]:
    """
    Поиск причастных оборотов

    Аргументы:
        doc (Doc): Объект Doc с разбором зависимостей

    Вывод:
        list[Highlight]: Фрагменты слоя participle_clauses
    """
    highlights = []
    units = _units_by_word(doc)
    for token in get_words(doc, join_hyphens=True):
        if is_participle_clause(token):
            start, end = _clause_span(token, units)
            n_words = subtree_len(token, join_hyphens=True)
            note = f"причастный оборот, {plural(n_words, 'слово', 'слова', 'слов')}"
            highlights.append(Highlight(start, end, "participle_clauses", note))
    return highlights


def find_converb_clauses(doc: Doc) -> list[Highlight]:
    """
    Поиск деепричастных оборотов

    Аргументы:
        doc (Doc): Объект Doc с разбором зависимостей

    Вывод:
        list[Highlight]: Фрагменты слоя converb_clauses
    """
    highlights = []
    units = _units_by_word(doc)
    for token in get_words(doc, join_hyphens=True):
        if is_converb_clause(token):
            start, end = _clause_span(token, units)
            n_words = subtree_len(token, join_hyphens=True)
            note = f"деепричастный оборот, {plural(n_words, 'слово', 'слова', 'слов')}"
            highlights.append(Highlight(start, end, "converb_clauses", note))
    return highlights


def find_split_predicate_highlights(doc: Doc) -> list[Highlight]:
    """
    Поиск расщепленных сказуемых

    Описание:
        Пары легкий глагол - именная часть из find_split_predicates; фрагмент покрывает
        слова от первого до последнего из пары (осуществляет плановую проверку)

    Аргументы:
        doc (Doc): Объект Doc с разбором зависимостей

    Вывод:
        list[Highlight]: Фрагменты слоя split_predicates
    """
    highlights = []
    for verb, noun in find_split_predicates(doc):
        start, end = tokens_span([verb, noun])
        note = f"расщепленное сказуемое: {get_lemma(verb)} {get_lemma(noun)}"
        highlights.append(Highlight(start, end, "split_predicates", note))
    return highlights


def _genitive_chain(token: Token) -> tuple[list[Token], int]:
    tokens = [token]
    depth = 1
    for child in get_children(token, join_hyphens=True):
        if is_genitive_modifier(child):
            child_tokens, child_depth = _genitive_chain(child)
            tokens += child_tokens
            depth = max(depth, child_depth + 1)
    return tokens, depth


def find_genitive_chains(doc: Doc) -> list[Highlight]:
    """
    Поиск цепочек родительных падежей

    Описание:
        Цепочка - два и более вложенных беспредложных определения в родительном падеже,
        как в calc_genitive_chains; фрагмент покрывает управляющее слово и все определения
        цепочки: повышение эффективности использования ресурсов

    Аргументы:
        doc (Doc): Объект Doc с разбором зависимостей

    Вывод:
        list[Highlight]: Фрагменты слоя genitive_chains
    """
    highlights = []
    word_tokens = _word_tokens(doc)
    for token in get_words(doc, join_hyphens=True):
        if not is_genitive_modifier(token) or is_genitive_modifier(token.head):
            continue
        chain, depth = _genitive_chain(token)
        if depth < 2:
            continue
        start, end = tokens_span(word_tokens([token.head, *chain]))
        note = f"цепочка из {plural(depth, 'родительного', 'родительных', 'родительных')}"
        highlights.append(Highlight(start, end, "genitive_chains", note))
    return highlights


SYNTAX_FINDERS: dict[str, Callable[[Doc], list[Highlight]]] = {
    "passive": find_passive,
    "participle_clauses": find_participle_clauses,
    "converb_clauses": find_converb_clauses,
    "genitive_chains": find_genitive_chains,
    "split_predicates": find_split_predicate_highlights,
}
