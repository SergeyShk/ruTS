import html
from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass
from itertools import pairwise
from typing import NamedTuple

from razdel import sentenize, tokenize
from spacy.tokens import Doc, Token

from ..constants import (
    ALLITERATION_IGNORED_LETTERS,
    ALLITERATION_MIN_WORD_LEN,
    ALLITERATION_THRESHOLD,
    COMPLEX_SYL_FACTOR,
    HIGHLIGHT_LAYERS_DESC,
    HIGHLIGHT_SYNTAX_LAYERS,
    LONG_SENT_WORD_FACTOR,
    RU_LETTER_FREQUENCIES,
)
from ..phon_stats import CONSONANTS, LETTERS, VOWELS
from ..style_stats import is_stopword
from ..syntax_stats import (
    get_words,
    is_agentless,
    is_converb_clause,
    is_genitive_modifier,
    is_participle_clause,
    is_passive,
    is_word,
)
from ..utils import count_syllables, is_punctuation, parse_word

CSS = """\
.ruts-highlight { line-height: 1.7; }
.ruts-highlight-legend { display: flex; flex-wrap: wrap; gap: 0.4em 1.2em; margin-bottom: 0.8em; font-size: 0.9em; }
.ruts-highlight-legend .ruts-hl { padding: 0 0.3em; }
.ruts-highlight-count { opacity: 0.6; margin-left: 0.3em; }
.ruts-highlight-text { white-space: pre-wrap; }
.ruts-highlight .ruts-hl.ruts-hl-long_sents, .ruts-highlight .ruts-hl.ruts-hl-complex_words, .ruts-highlight .ruts-hl.ruts-hl-stopwords, .ruts-highlight .ruts-hl.ruts-hl-passive { color: #1f2328; border-radius: 2px; }
.ruts-hl-long_sents { background: #fef9c3; }
.ruts-hl-complex_words { background: #fed7aa; }
.ruts-hl-stopwords { background: #bae6fd; }
.ruts-hl-passive { background: #fecaca; }
.ruts-hl-participle_clauses { border-bottom: 2px solid #7c3aed; }
.ruts-hl-converb_clauses { border-bottom: 2px solid #0d9488; }
.ruts-hl-genitive_chains { border-bottom: 2px solid #b45309; }
.ruts-hl-alliteration { text-decoration-line: underline; text-decoration-style: dotted; text-decoration-color: #db2777; text-decoration-thickness: 2px; text-underline-offset: 3px; }
"""


class Word(NamedTuple):
    start: int
    end: int
    text: str


class Sent(NamedTuple):
    start: int
    end: int
    n_words: int


@dataclass(frozen=True)
class Highlight:
    """
    Подсвеченный фрагмент текста

    Аргументы:
        start (int): Позиция первого символа фрагмента
        end (int): Позиция за последним символом фрагмента
        layer (str): Слой подсветки
        note (str): Пояснение к фрагменту для всплывающей подсказки
    """

    start: int
    end: int
    layer: str
    note: str = ""


class HighlightedText:
    """
    Класс для подсветки текста по слоям в стиле Главреда и Тургенева

    Описание:
        Каждый слой отмечает фрагменты, по которым считаются статистики библиотеки:
            long_sents - предложения с числом слов не меньше long_sent_word_factor (BasicStats, ReadabilityStats)
            complex_words - слова с числом слогов не меньше complex_syl_factor (BasicStats, ReadabilityStats)
            stopwords - стоп-слова по части речи или переданному списку, «вода» текста (StyleStats)
            passive - пассивные глагольные формы вместе со вспомогательным глаголом (SyntaxStats)
            participle_clauses - причастные обороты (SyntaxStats)
            converb_clauses - деепричастные обороты (SyntaxStats)
            genitive_chains - цепочки родительных падежей с управляющим словом (SyntaxStats)
            alliteration - повторы согласной в соседних словах, маловероятные при частотах букв русского языка (PhonStats)
        Слои passive, participle_clauses, converb_clauses и genitive_chains считаются по дереву
        зависимостей и доступны только для объекта Doc с разбором зависимостей; слой long_sents
        для Doc требует границ предложений. По умолчанию включаются все слои, доступные источнику
        Результат отображается в Jupyter как HTML со стилями и легендой, метод to_html
        возвращает ту же разметку для документации и веб-приложений; фрагменты разных слоев
        могут пересекаться, при отрисовке текст режется на отрезки с набором классов CSS

    Пример использования:
        >>> from ruts.visualizers import highlight
        >>> text = "Чуть слышно, бесшумно шуршат камыши. Повышение эффективности использования ресурсов обсуждалось."
        >>> ht = highlight(text)
        >>> ht.counts
        {'long_sents': 0, 'complex_words': 4, 'stopwords': 0, 'alliteration': 1}
        >>> ht.highlights[0]
        Highlight(start=5, end=35, layer='alliteration', note='аллитерация на «ш»')
        >>> ht.to_html(legend=False, css=False)
        '<div class="ruts-highlight"><div class="ruts-highlight-text">Чуть <span class="ruts-hl ruts-hl-alliteration" title="аллитерация на «ш»">слышно, бесшумно шуршат камыши</span>. ...'

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        layers (list[str]): Слои подсветки; если не заданы, включаются все доступные источнику
        long_sent_word_factor (int): Минимальное количество слов в длинном предложении
        complex_syl_factor (int): Минимальное количество слогов в сложном слове
        stopwords (list[str]): Список стоп-слов; если не задан, стоп-слова определяются
            по части речи с помощью pymorphy3
        alliteration_threshold (float): Порог вероятности повтора согласной при независимом
            распределении букв, ниже которого повтор считается аллитерацией

    Атрибуты:
        text (str): Текст источника данных
        layers (tuple[str]): Включенные слои подсветки в порядке отрисовки
        highlights (tuple[Highlight]): Подсвеченные фрагменты в порядке появления в тексте
        counts (dict[str, int]): Количество фрагментов каждого слоя

    Методы:
        to_html: Получение HTML-разметки подсвеченного текста

    Исключения:
        TypeError: Если передаваемое значение не является строкой или объектом Doc
        ValueError: Если в источнике данных отсутствуют слова
        ValueError: Если задан неизвестный или недоступный источнику слой
        ValueError: Если пороги слоев заданы некорректно
    """

    def __init__(
        self,
        source: str | Doc,
        layers: Sequence[str] | None = None,
        long_sent_word_factor: int = LONG_SENT_WORD_FACTOR,
        complex_syl_factor: int = COMPLEX_SYL_FACTOR,
        stopwords: Sequence[str] | None = None,
        alliteration_threshold: float = ALLITERATION_THRESHOLD,
    ):
        if isinstance(source, Doc):
            self.text = source.text
            words = [
                Word(token.idx, token.idx + len(token), token.text) for token in get_words(source)
            ]
            sents = get_doc_sents(source) if source.has_annotation("SENT_START") else None
            doc = source if source.has_annotation("DEP") else None
        elif isinstance(source, str):
            self.text = source
            words = get_text_words(source)
            sents = get_text_sents(source, words)
            doc = None
        else:
            raise TypeError("Некорректный источник данных")
        if not words:
            raise ValueError("В источнике данных отсутствуют слова")
        if long_sent_word_factor < 1:
            raise ValueError("Количество слов в длинном предложении должно быть больше 0")
        if complex_syl_factor < 1:
            raise ValueError("Количество слогов в сложном слове должно быть больше 0")
        if not 0 < alliteration_threshold <= 1:
            raise ValueError("Порог аллитерации должен быть в интервале (0, 1]")
        available = [
            layer
            for layer in HIGHLIGHT_LAYERS_DESC
            if not (layer == "long_sents" and sents is None)
            and not (layer in HIGHLIGHT_SYNTAX_LAYERS and doc is None)
        ]
        self.layers = select_layers(layers, available)

        finders: dict[str, Callable[[], list[Highlight]]] = {
            "long_sents": lambda: find_long_sents(sents or [], long_sent_word_factor),
            "complex_words": lambda: find_complex_words(words, complex_syl_factor),
            "stopwords": lambda: find_stopwords(words, stopwords),
            "alliteration": lambda: find_alliteration(words, alliteration_threshold, sents),
            "passive": lambda: find_passive(doc) if doc else [],
            "participle_clauses": lambda: find_participle_clauses(doc) if doc else [],
            "converb_clauses": lambda: find_converb_clauses(doc) if doc else [],
            "genitive_chains": lambda: find_genitive_chains(doc) if doc else [],
        }
        highlights = [h for layer in self.layers for h in finders[layer]()]
        self.highlights = tuple(sorted(highlights, key=lambda h: (h.start, -h.end)))

    @property
    def counts(self) -> dict[str, int]:
        return {
            layer: sum(1 for h in self.highlights if h.layer == layer) for layer in self.layers
        }

    def to_html(self, legend: bool = True, css: bool = True) -> str:
        """
        Получение HTML-разметки подсвеченного текста

        Описание:
            Разметка - блок div с классом ruts-highlight, внутри легенда со счетчиками
            и текст, в котором подсвеченные отрезки обернуты в span с классами
            ruts-hl и ruts-hl-<слой>; пояснения фрагментов выводятся в атрибут title
            Переносы строк сохраняются как символьные ссылки, поэтому разметку можно
            вставлять в Markdown без пустых строк внутри блока

        Аргументы:
            legend (bool): Добавлять легенду со счетчиками фрагментов
            css (bool): Добавлять стили слоев

        Вывод:
            str: HTML-разметка
        """
        parts = ['<div class="ruts-highlight">']
        if css:
            parts.append(f"<style>{CSS}</style>")
        if legend:
            items = "".join(
                f'<span><span class="ruts-hl ruts-hl-{layer}">{HIGHLIGHT_LAYERS_DESC[layer]}</span>'
                f'<span class="ruts-highlight-count">{count}</span></span>'
                for layer, count in self.counts.items()
            )
            parts.append(f'<div class="ruts-highlight-legend">{items}</div>')
        parts.append(f'<div class="ruts-highlight-text">{self._render_text()}</div></div>')
        return "".join(parts)

    def _repr_html_(self) -> str:
        return self.to_html()

    def _render_text(self) -> str:
        chunks = []
        for start, end, active in split_segments(len(self.text), self.highlights):
            chunk = html.escape(self.text[start:end]).replace("\n", "&#10;")
            if active:
                active.sort(key=lambda h: self.layers.index(h.layer))
                classes = " ".join(f"ruts-hl-{h.layer}" for h in active)
                notes = "; ".join(dict.fromkeys(h.note for h in active if h.note))
                title = f' title="{html.escape(notes)}"' if notes else ""
                chunk = f'<span class="ruts-hl {classes}"{title}>{chunk}</span>'
            chunks.append(chunk)
        return "".join(chunks)


def highlight(
    source: str | Doc,
    layers: Sequence[str] | None = None,
    long_sent_word_factor: int = LONG_SENT_WORD_FACTOR,
    complex_syl_factor: int = COMPLEX_SYL_FACTOR,
    stopwords: Sequence[str] | None = None,
    alliteration_threshold: float = ALLITERATION_THRESHOLD,
) -> HighlightedText:
    """
    Подсветка текста по слоям в стиле Главреда и Тургенева

    Описание:
        Слои: long_sents, complex_words, stopwords, passive, participle_clauses,
        converb_clauses, genitive_chains, alliteration; синтаксические слои доступны
        только для объекта Doc с разбором зависимостей, подробнее в классе HighlightedText

    Аргументы:
        source (str|Doc): Источник данных (строка или объект Doc)
        layers (list[str]): Слои подсветки; если не заданы, включаются все доступные источнику
        long_sent_word_factor (int): Минимальное количество слов в длинном предложении
        complex_syl_factor (int): Минимальное количество слогов в сложном слове
        stopwords (list[str]): Список стоп-слов; если не задан, стоп-слова определяются
            по части речи с помощью pymorphy3
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
        alliteration_threshold=alliteration_threshold,
    )


def select_layers(layers: Sequence[str] | None, available: Sequence[str]) -> tuple[str, ...]:
    """
    Выбор слоев подсветки

    Аргументы:
        layers (list[str]): Запрошенные слои; если не заданы, берутся все доступные
        available (list[str]): Слои, доступные источнику данных

    Вывод:
        tuple[str]: Слои в порядке отрисовки

    Исключения:
        ValueError: Если задан неизвестный или недоступный источнику слой
    """
    if layers is None:
        return tuple(available)
    if isinstance(layers, str):
        layers = [layers]
    for layer in layers:
        if layer not in HIGHLIGHT_LAYERS_DESC:
            raise ValueError(f"Неизвестный слой подсветки: {layer}")
        if layer not in available:
            requirement = (
                "границ предложений в объекте Doc"
                if layer == "long_sents"
                else "объекта Doc с разбором зависимостей"
            )
            raise ValueError(f"Слой {layer} требует {requirement}")
    return tuple(layer for layer in HIGHLIGHT_LAYERS_DESC if layer in layers)


def get_text_words(text: str) -> list[Word]:
    """
    Извлечение слов с позициями из строки

    Описание:
        Токенизация razdel, знаки препинания отбрасываются как в WordsExtractor

    Аргументы:
        text (str): Строка текста

    Вывод:
        list[Word]: Список слов с позициями
    """
    return [
        Word(token.start, token.stop, token.text)
        for token in tokenize(text)
        if not is_punctuation(token.text)
    ]


def get_text_sents(text: str, words: Sequence[Word]) -> list[Sent]:
    """
    Извлечение предложений с позициями и числом слов из строки

    Описание:
        Разбиение на предложения razdel, как в SentsExtractor; слова относятся
        к предложению по позиции первого символа

    Аргументы:
        text (str): Строка текста
        words (list[Word]): Слова текста с позициями

    Вывод:
        list[Sent]: Список предложений с позициями и числом слов
    """
    sents = []
    index = 0
    for sent in sentenize(text):
        n_words = 0
        while index < len(words) and words[index].start < sent.stop:
            n_words += words[index].start >= sent.start
            index += 1
        sents.append(Sent(sent.start, sent.stop, n_words))
    return sents


def get_doc_sents(doc: Doc) -> list[Sent]:
    """
    Извлечение предложений с позициями и числом слов из объекта Doc

    Описание:
        Пробельные токены в начале и конце предложения не входят в его позиции:
        sentencizer ставит границу на перенос строки после точки

    Аргументы:
        doc (Doc): Объект Doc с границами предложений

    Вывод:
        list[Sent]: Список предложений с позициями и числом слов
    """
    sents = []
    for sent in doc.sents:
        tokens = [token for token in sent if not token.is_space]
        if tokens:
            start = min(token.idx for token in tokens)
            end = max(token.idx + len(token) for token in tokens)
            sents.append(Sent(start, end, len(get_words(sent))))
    return sents


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
    words: Iterable[Word], stopwords: Sequence[str] | None = None
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


def group_words_by_sents(words: Sequence[Word], sents: Sequence[Sent]) -> list[list[Word]]:
    """
    Группировка слов по предложениям

    Описание:
        Слова и предложения упорядочены по позиции, поэтому достаточно одного прохода;
        слово относится к предложению по позиции первого символа, слова вне
        предложений пропускаются

    Аргументы:
        words (list[Word]): Слова с позициями
        sents (list[Sent]): Предложения с позициями

    Вывод:
        list[list[Word]]: Слова каждого предложения
    """
    groups: list[list[Word]] = [[] for _ in sents]
    index = 0
    for word in words:
        while index < len(sents) and sents[index].end <= word.start:
            index += 1
        if index < len(sents) and sents[index].start <= word.start:
            groups[index].append(word)
    return groups


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
        есть одна и та же согласная буква; слова короче трех букв (предлоги, союзы,
        частицы, местоимения он, их) и слова без гласных (аббревиатуры) цепочку
        не прерывают и не продолжают: по полю плыл - повтор п в двух словах
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
        len(word) < ALLITERATION_MIN_WORD_LEN or not any(letter in VOWELS for letter in word)
        for word in letters
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


def tokens_span(tokens: Iterable[Token]) -> tuple[int, int]:
    """
    Вычисление позиций фрагмента текста, покрывающего слова

    Описание:
        Знаки препинания и пробельные токены не учитываются, поэтому запятые
        на границах оборота во фрагмент не входят

    Аргументы:
        tokens (Doc|Span|list[Token]): Последовательность токенов

    Вывод:
        tuple[int, int]: Позиция первого символа и позиция за последним символом
    """
    words = get_words(tokens)
    return min(token.idx for token in words), max(token.idx + len(token) for token in words)


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
    for token in doc:
        if is_word(token) and is_passive(token):
            auxiliaries = [child for child in token.children if child.dep_ == "aux:pass"]
            start, end = tokens_span([token, *auxiliaries])
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
    for token in doc:
        if is_participle_clause(token):
            start, end = tokens_span(token.subtree)
            n_words = len(get_words(token.subtree))
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
    for token in doc:
        if is_converb_clause(token):
            start, end = tokens_span(token.subtree)
            n_words = len(get_words(token.subtree))
            note = f"деепричастный оборот, {plural(n_words, 'слово', 'слова', 'слов')}"
            highlights.append(Highlight(start, end, "converb_clauses", note))
    return highlights


def _genitive_chain(token: Token) -> tuple[list[Token], int]:
    tokens = [token]
    depth = 1
    for child in token.children:
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
    for token in doc:
        if not is_genitive_modifier(token) or is_genitive_modifier(token.head):
            continue
        chain, depth = _genitive_chain(token)
        if depth < 2:
            continue
        start, end = tokens_span([token.head, *chain])
        note = f"цепочка из {plural(depth, 'родительного', 'родительных', 'родительных')}"
        highlights.append(Highlight(start, end, "genitive_chains", note))
    return highlights


def split_segments(
    length: int, highlights: Sequence[Highlight]
) -> Iterator[tuple[int, int, list[Highlight]]]:
    """
    Разбиение текста на отрезки с одинаковым набором фрагментов

    Описание:
        Границы отрезков - начала и концы всех фрагментов; пересекающиеся
        и вложенные фрагменты разных слоев дают отрезки с несколькими слоями

    Аргументы:
        length (int): Длина текста
        highlights (list[Highlight]): Фрагменты, отсортированные по позиции начала

    Вывод:
        iterator[tuple[int, int, list[Highlight]]]: Позиции отрезка и покрывающие его фрагменты
    """
    bounds = sorted({0, length, *(h.start for h in highlights), *(h.end for h in highlights)})
    pending = sorted(highlights, key=lambda h: h.start)
    active: list[Highlight] = []
    index = 0
    for start, end in pairwise(bounds):
        while index < len(pending) and pending[index].start <= start:
            active.append(pending[index])
            index += 1
        active = [h for h in active if h.end > start]
        yield start, end, list(active)
