from __future__ import annotations

import functools
import inspect
import re
import unicodedata
from collections.abc import Callable, Collection, Iterable, Iterator, Sequence
from functools import lru_cache
from typing import TYPE_CHECKING, Any, TypeVar, cast

import anyts.utils
import rumorph
from anyseg import Segmenter
from anyts.utils import (
    add_tokenizer_rules,
    check_sequence,
    has_sents,
    is_punctuation,
    set_sent_starts as set_sent_starts,
)

from .constants import (
    CORE_MESSAGES,
    PRONOMINAL_TYPES,
    TOKENIZER_INFIXES,
    TOKENIZER_PREFIXES,
    TOKENIZER_SUFFIXES,
    VERBAL_NOUN_LEMMAS,
    VERBAL_NOUN_SUFFIXES,
)
from .exceptions import SourceTypeError

if TYPE_CHECKING:
    from spacy.language import Language
    from spacy.tokens import Doc

F = TypeVar("F", bound=Callable[..., Any])
BYTE_ORDER_MARK = "\ufeff"
CYRILLIC = "а-яёА-ЯЁ"
LATIN_STRESSED = "áéóýàèòÁÉÓÝÀÈÒ"
# Буквы вместо записей с отдельными знаками, ѐ и ѝ и ударных гласных латиницей
MARKED_LETTERS = {
    "и\u0306": "й",
    "И\u0306": "Й",
    "е\u0308": "ё",
    "Е\u0308": "Ё",
    **dict(zip("ѐѝЀЍ", "еиЕИ", strict=True)),
    **dict(zip(LATIN_STRESSED, "аеоуаеоАЕОУАЕО", strict=True)),
    **dict(zip("aeoyAEOY", "аеоуАЕОУ", strict=True)),
}
# Знаки, которых нет в написании русского слова; группа говорит, что с ними делать
MARKS = re.compile(
    "(?P<letter>[иИ]\u0306|[еЕ]\u0308)"
    f"|(?P<stress>(?<=[{CYRILLIC}])[\u0300\u0301]+|(?<=[иеИЕ][\u0306\u0308])[\u0300\u0301]+)"
    "|(?P<hyphen>\u00ad)"
    "|(?P<grave>[ѐѝЀЍ])"
    f"|(?P<latin>(?<=[{CYRILLIC}])[{LATIN_STRESSED}]|(?<=[{CYRILLIC}]\u00ad)[{LATIN_STRESSED}]"
    f"|[{LATIN_STRESSED}](?=\u00ad?[{CYRILLIC}])"
    f"|(?<=[{CYRILLIC}])[aeoyAEOY][\u0300\u0301]|[aeoyAEOY][\u0300\u0301](?=\u00ad?[{CYRILLIC}]))"
)
MARKED = re.compile(f"[\u0300\u0301\u0306\u0308\u00adѐѝЀЍ{LATIN_STRESSED}]")
SEGMENTER = Segmenter("ru")
# Разбор строки без видимых символов: знак препинания, а не слово
NO_WORD = "_"
# anySeg принимает только текст, который кодируется в UTF-8
SURROGATES = re.compile("[\ud800-\udfff]")


@lru_cache(maxsize=1)
def get_morph_analyzer() -> rumorph.Analyzer:
    """
    Получение морфологического анализатора ruMorph

    Вывод:
        Analyzer: Морфологический анализатор
    """
    return rumorph.Analyzer()


def strip_marks(text: str) -> str:
    """
    Текст без знаков ударения и мягких переносов

    Описание:
        Снимаются акут U+0301 и гравис U+0300 после кириллической буквы, буквы
        ѐ и ѝ становятся е и и, ударная гласная латиницей внутри русского слова
        (чтó, Домá) - кириллической, й и ё из двух символов (NFD) собираются
        в одну букву, мягкий перенос U+00AD снимается везде: в написание слова
        все это не входит, а словари слов с ними не узнают. Знаки
        над латиницей (Café) остаются

    Аргументы:
        text (str): Текст или слово

    Вывод:
        str: Текст без знаков

    Исключения:
        SourceTypeError: Если текст не строка

    Пример использования:
        >>> from ruts.utils import strip_marks
        >>> strip_marks("Моро\\u0301з и со\\u00adлнце, чтó, Café")
        'Мороз и солнце, что, Café'
    """
    _check_text(text)
    if not MARKED.search(text):
        return text
    return MARKS.sub(_replace_mark, text)


def _check_text(text: object) -> None:
    """SourceTypeError с русским сообщением, если текст не строка"""
    if not isinstance(text, str):
        raise SourceTypeError(CORE_MESSAGES["text_type"].format(type=type(text).__name__))


def with_stripped_marks(func: F, *names: str) -> F:
    """
    Функция ядра, которая снимает знаки ударения и мягкие переносы с аргументов

    Описание:
        Строка, список строк или список списков строк в аргументах names проходит
        через strip_marks: слова и слово запроса со знаками и без находятся
        одинаково. Неверные значения передаются как есть - их отвергает ядро

    Аргументы:
        func (Callable): Функция ядра
        names (tuple[str]): Имена аргументов со словами

    Вывод:
        Callable: Функция с той же сигнатурой
    """
    signature = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        bound = signature.bind(*args, **kwargs)
        for name in names:
            if name in bound.arguments:
                bound.arguments[name] = _strip_words(bound.arguments[name])
        return func(*bound.args, **bound.kwargs)

    return cast(F, wrapper)


def _strip_words(value: Any) -> Any:
    """Строка, список строк или список списков строк без знаков (with_stripped_marks)"""
    if isinstance(value, str):
        return strip_marks(value)
    try:
        check_sequence(value)
        # Одна проверка склеенных слов вместо поиска знаков в каждом
        joined = "".join(value)
    except SourceTypeError:
        return value
    except TypeError:
        items: Iterable[Any] = (_strip_words(item) for item in value)
    else:
        if not MARKED.search(joined):
            return value
        items = map(strip_marks, value)
    return type(value)(items) if isinstance(value, list | tuple) else list(items)


def take_marks(text: str, positions: bool = True) -> tuple[str, list[int], set[int]]:
    """
    Текст без знаков ударения и мягких переносов с картой позиций и ударениями

    Описание:
        Текст тот же, что у strip_marks; для каждого его символа - позиция
        в исходной строке, и номера символов, на которые падает ударение по знаку
        (буква перед акутом или грависом, ѐ, ѝ, ударная гласная латиницей)

    Аргументы:
        text (str): Текст
        positions (bool): Строить карту позиций; False - список позиций пуст

    Вывод:
        tuple[str, list[int], set[int]]: Текст без знаков, позиции его символов
            в исходной строке и номера ударных символов

    Пример использования:
        >>> from ruts.utils import take_marks
        >>> take_marks("Ма\\u0301ма")
        ('Мама', [0, 1, 3, 4], {1})
    """
    pieces = []
    origin: list[int] = []
    stressed = set()
    length = 0
    position = 0
    for match in MARKS.finditer(text):
        pieces.append(text[position : match.start()])
        length += match.start() - position
        if positions:
            origin.extend(range(position, match.start()))
        if match.lastgroup == "stress":
            stressed.add(length - 1)
        elif match.lastgroup != "hyphen":
            if match.lastgroup != "letter":
                stressed.add(length)
            pieces.append(_replace_mark(match))
            length += 1
            if positions:
                origin.append(match.start())
        position = match.end()
    pieces.append(text[position:])
    if positions:
        origin.extend(range(position, len(text)))
    return "".join(pieces), origin, stressed


def _replace_mark(match: re.Match[str]) -> str:
    """Замена знака из MARKS: пустая строка или буква"""
    if match.lastgroup in ("stress", "hyphen"):
        return ""
    found = match.group()
    return MARKED_LETTERS.get(found) or MARKED_LETTERS[found[0]]


@lru_cache(maxsize=131072)
def parse_all(word: str) -> tuple[rumorph.Analysis, ...]:
    """
    Морфологические разборы словоформы ruMorph с кэшированием

    Описание:
        Разборы по убыванию вероятности, без учета соседних слов; части речи
        и признаки - Universal Dependencies, пометы OpenCorpora без признака UD
        (вводное слово Prnt, переходность tran и intr) - в labels. Знаки ударения,
        мягкие переносы и ё ruMorph учитывает сам, точку - у известных ему сокращений
        (т., руб., г.), а незнакомое сокращение с точкой (тов., коп.) - X с точкой
        в лемме;
        слово с управляющими, служебными или пробельными символами (DEL, ZWSP),
        которого ruMorph не разбирает, разбирается без них, а строка без видимых
        символов - как знак препинания (NO_WORD), так что разбор есть всегда

    Аргументы:
        word (str): Словоформа

    Вывод:
        tuple[Analysis]: Разборы словоформы

    Пример использования:
        >>> from ruts.utils import parse_all
        >>> [(analysis.lemma, analysis.pos) for analysis in parse_all("стали")][:2]
        [('стать', 'VERB'), ('сталь', 'NOUN')]
    """
    analyzer = get_morph_analyzer()
    analyses = analyzer.analyze(word)
    if not analyses:
        visible = "".join(char for char in word if unicodedata.category(char)[0] not in "CZ")
        analyses = (visible and analyzer.analyze(visible)) or analyzer.analyze(NO_WORD)
    return tuple(analyses)


def parse_word(word: str) -> rumorph.Analysis:
    """
    Морфологический разбор словоформы

    Описание:
        Возвращает первый (наиболее вероятный) разбор parse_all, который
        кэширует разборы по словоформе: в тексте на 75 тысяч токенов всего около
        14 тысяч уникальных форм, повторный разбор не нужен

    Аргументы:
        word (str): Словоформа

    Вывод:
        Analysis: Разбор словоформы
    """
    return parse_all(word)[0]


def is_predicative(analysis: rumorph.Analysis) -> bool:
    """
    Проверка, является ли разбор предикативом (надо, можно, нет) или частицей «бы»

    Описание:
        В UD это глагол или вспомогательный глагол без формы VerbForm

    Аргументы:
        analysis (Analysis): Разбор ruMorph

    Вывод:
        bool: Результат проверки
    """
    return analysis.pos in ("VERB", "AUX") and "VerbForm" not in analysis.feats


def is_pronominal(analysis: rumorph.Analysis) -> bool:
    """
    Проверка, является ли разбор указательным, вопросительным или относительным словом

    Описание:
        Признак PronType со значением из PRONOMINAL_TYPES (там, тогда, где, почему);
        определительные (всегда, иногда, более - PronType=Tot) и отрицательные
        (никогда) наречия к ним не относятся

    Аргументы:
        analysis (Analysis): Разбор ruMorph

    Вывод:
        bool: Результат проверки
    """
    return not PRONOMINAL_TYPES.isdisjoint(analysis.feats.get("PronType", "").split(","))


@lru_cache(maxsize=131072)
def lemmatize(word: str, pos: str = "") -> str:
    """
    Лемматизация словоформы ruMorph с учетом части речи Universal Dependencies

    Описание:
        Среди разборов словоформы выбирается первый с заданной частью речи:
        «стали» с NOUN - сталь, с VERB - стать. Без части речи или без подходящего
        разбора берется первый разбор

    Аргументы:
        word (str): Словоформа
        pos (str): Часть речи UD

    Вывод:
        str: Лемма
    """
    analyses = parse_all(word)
    return next((analysis for analysis in analyses if analysis.pos == pos), analyses[0]).lemma


@lru_cache(maxsize=16384)
def analyze_sentence(sentence: str) -> tuple[tuple[str, rumorph.Analysis], ...]:
    """
    Слова предложения с разборами ruMorph в контексте

    Описание:
        Токены - как у WordsExtractor по умолчанию: сегментатор SEGMENTER по тексту
        без знаков ударения и мягких переносов (strip_marks); разборы выбирает
        контекстная модель ruMorph по всем токенам предложения, знаки препинания
        в вывод не входят. Токен без разборов модели разбирается, как в parse_all.
        Результаты кэшируются по тексту предложения

    Аргументы:
        sentence (str): Текст одного предложения

    Вывод:
        tuple[tuple[str, Analysis], ...]: Слово и разбор, выбранный по соседним словам

    Пример использования:
        >>> from ruts.utils import analyze_sentence
        >>> [(word, a.lemma, a.pos) for word, a in analyze_sentence("Мост сделан из стали.")]
        [('Мост', 'мост', 'NOUN'), ('сделан', 'сделать', 'VERB'), ('из', 'из', 'ADP'), ('стали', 'сталь', 'NOUN')]
    """
    forms = [token for _, _, token in iter_tokens(strip_marks(sentence))]
    analyses = get_morph_analyzer().analyze_sentence(forms)
    return tuple(
        (form, found[0] if found else parse_word(form))
        for form, found in zip(forms, analyses, strict=True)
        if not is_punctuation(form)
    )


def analyze_text(text: str) -> list[tuple[str, rumorph.Analysis]]:
    """
    Слова текста с разборами ruMorph в контексте своих предложений

    Описание:
        Предложения - iter_text_sents, слова и разборы - analyze_sentence; слова
        те же, что дает WordsExtractor по умолчанию

    Аргументы:
        text (str): Строка текста

    Вывод:
        list[tuple[str, Analysis]]: Слово и разбор, выбранный по соседним словам

    Исключения:
        SourceTypeError: Если текст не строка
    """
    sents = tuple(sent for _, _, sent in iter_text_sents(text))
    return [pair for pairs in analyze_sents(sents) for pair in pairs]


@lru_cache(maxsize=1)
def analyze_sents(
    sents: tuple[str, ...],
) -> tuple[tuple[tuple[str, rumorph.Analysis], ...], ...]:
    """
    Слова предложений текста с разборами ruMorph в контексте

    Описание:
        Разборы analyze_sentence по каждому предложению. Кэш по всему набору
        предложений: классы статистик одного текста разбирают его один раз, даже
        когда предложений больше, чем вмещает кэш analyze_sentence

    Аргументы:
        sents (tuple[str]): Тексты предложений по порядку

    Вывод:
        tuple[tuple[tuple[str, Analysis], ...], ...]: Слова и разборы каждого предложения
    """
    return tuple(analyze_sentence(sent) for sent in sents)


def analyze_words(words: Sequence[tuple[int, str]], text: str) -> list[rumorph.Analysis | None]:
    """
    Разборы в контексте для слов текста из другого токенизатора

    Описание:
        Для слов Doc spaCy без разметки: слово относится к первому предложению
        iter_text_sents, до конца которого начинается; слова предложения получают
        разборы analyze_sents, если совпадают с его словами у analyze_sentence,
        иначе None - тогда слово разбирается по одному

    Аргументы:
        words (list[tuple[int, str]]): Позиция первого символа и текст слов по порядку
        text (str): Текст, из которого они извлечены

    Вывод:
        list[Analysis|None]: Разбор каждого слова или None
    """
    spans = list(iter_text_sents(text))
    found: list[rumorph.Analysis | None] = [None] * len(words)
    first = 0
    for (_, stop, _), pairs in zip(
        spans, analyze_sents(tuple(sent for _, _, sent in spans)), strict=True
    ):
        last = first
        while last < len(words) and words[last][0] < stop:
            last += 1
        if [word for _, word in words[first:last]] == [word for word, _ in pairs]:
            found[first:last] = [analysis for _, analysis in pairs]
        first = last
    return found


def is_verbal_noun(lemma: str) -> bool:
    """
    Проверка, является ли лемма отглагольным существительным по суффиксу

    Описание:
        Суффиксы из VERBAL_NOUN_SUFFIXES: -ние, -нье, -тие, -тье, -ствие, -ция
        (повышение, участие, содействие, реализация) или лемма из VERBAL_NOUN_LEMMAS
        (производство, руководство, строительство); суффикс -ство в список не входит,
        так как в основном не отглагольный (правительство, общество, средство)
        Эвристика захватывает и неотглагольные слова с теми же суффиксами (здание)

    Аргументы:
        lemma (str): Лемма существительного

    Вывод:
        bool: Результат проверки
    """
    lemma = normalize_yo(lemma)
    return lemma.endswith(VERBAL_NOUN_SUFFIXES) or lemma in VERBAL_NOUN_LEMMAS


@lru_cache(maxsize=131072)
def normalize_yo(word: str) -> str:
    """
    Замена буквы ё на е в нижнем регистре

    Описание:
        Форма слова для сравнения: знаки ударения и мягкие переносы тоже
        снимаются (strip_marks)

    Аргументы:
        word (str): Слово

    Вывод:
        str: Слово без буквы ё
    """
    return strip_marks(word).lower().replace("ё", "е")


def find_phrases(words: Sequence[str], phrases: Collection[str]) -> list[tuple[int, int]]:
    """
    Поиск словосочетаний в последовательности слов

    Описание:
        Слова и словосочетания сравниваются в нижнем регистре без буквы ё (normalize_yo);
        в каждой позиции выбирается самое длинное словосочетание, найденные
        не пересекаются. Расчет - find_phrases ядра

    Аргументы:
        words (list[str]): Слова текста
        phrases (list[str]|set[str]): Словосочетания через пробел

    Вывод:
        list[tuple[int, int]]: Границы найденных словосочетаний как срезы words;
            пустые словосочетания пропускаются
    """
    return anyts.utils.find_phrases(words, phrases, normalize_yo)


def iter_tokens(text: str) -> Iterator[tuple[int, int, str]]:
    """
    Токенизация строки сегментатором anySeg

    Описание:
        Токены - по соглашениям UD для русского (SEGMENTER): тире реплик и ремарок,
        приклеенные к словам (-Нет -сказал он), - отдельные токены; слово через дефис
        обычно один токен (кто-то, во-первых, социально-экономический, дом-музей),
        но часть составных слов (Ростов-на-Дону, Жили-были) и слово с частицей
        (Вася-то, скажи-ка) делятся; число с разделителями (1 250 000, 4,5, 12:30) -
        один токен; сокращение внутри предложения - с точкой (т., руб.), а точка
        в конце предложения - отдельный токен. Метка порядка байтов (BOM) токеном
        не считается, одиночный суррогат (из JSON) - символ своего токена.
        В тексте токена сняты знаки ударения и мягкие переносы (strip_marks), позиции -
        по исходной строке

    Аргументы:
        text (str): Строка текста

    Вывод:
        generator[tuple[int, int, str]]: Позиция первого символа, позиция за последним
            символом и текст каждого токена
    """
    for span in SEGMENTER.tokenize(_segmentable(text)):
        word = strip_marks(text[span.start : span.end])
        if word:
            yield span.start, span.end, word


def iter_text_words(text: str) -> Iterator[tuple[int, int, str]]:
    """
    Извлечение слов с позициями из строки

    Описание:
        Токены iter_tokens, знаки препинания отбрасываются как в WordsExtractor

    Аргументы:
        text (str): Строка текста

    Вывод:
        generator[tuple[int, int, str]]: Позиция первого символа, позиция за последним
            символом и текст каждого слова

    Исключения:
        SourceTypeError: Если текст не строка
    """
    _check_text(text)
    return (
        (start, stop, token)
        for start, stop, token in iter_tokens(text)
        if not is_punctuation(token)
    )


def iter_text_sents(text: str) -> Iterator[tuple[int, int, str]]:
    """
    Предложения anySeg с позициями

    Описание:
        Предложения сегментатора SEGMENTER: пустая строка завершает предложение,
        как в SentsExtractor, отдельным предложением идут и строка без конечного знака
        (пункт списка, заголовок), и предложение после точки без пробела; знаки
        ударения и мягкие переносы внутри слов границ не меняют. Позиции и текст
        предложений - по исходной строке, со знаками

    Аргументы:
        text (str): Строка текста

    Вывод:
        generator[tuple[int, int, str]]: Позиция первого символа, позиция за последним
            символом и текст каждого предложения

    Исключения:
        SourceTypeError: Если текст не строка

    Пример использования:
        >>> from ruts.utils import iter_text_sents
        >>> [sent for _, _, sent in iter_text_sents("Он кру\\u0301т. Мы тоже.")]
        ['Он кру́т.', 'Мы тоже.']
        >>> [sent for _, _, sent in iter_text_sents("Итоги\\n\\nВсе на месте.")]
        ['Итоги', 'Все на месте.']
        >>> [sent for _, _, sent in iter_text_sents("Нужно:\\n- паспорт\\n- фото")]
        ['Нужно:', '- паспорт', '- фото']
    """
    _check_text(text)
    return (
        (sent.start, sent.end, text[sent.start : sent.end])
        for sent in SEGMENTER.sentenize(_segmentable(text))
    )


def _segmentable(text: str) -> str:
    """Текст для anySeg: одиночный суррогат - U+FFFD, длина и позиции те же"""
    return SURROGATES.sub("\ufffd", text) if SURROGATES.search(text) else text


def strip_doc_marks(doc: Doc) -> Doc:
    """
    Объект Doc со словами без знаков ударения и мягких переносов

    Описание:
        Новый Doc из текстов токенов после strip_marks с теми же пробелами
        и границами предложений (если они у каждого токена, has_sents), без прочей
        разметки; токен из одних знаков
        пропускается. Doc без знаков возвращается как есть

    Аргументы:
        doc (Doc): Объект Doc

    Вывод:
        Doc: Объект Doc без знаков
    """
    if not MARKED.search(doc.text):
        return doc
    sents = has_sents(doc)
    words: list[str] = []
    spaces: list[bool] = []
    starts: list[bool | int | None] = []
    start = False
    for token in doc:
        start = start or bool(sents and token.is_sent_start)
        word = strip_marks(token.text)
        if not word:
            if spaces:
                spaces[-1] = spaces[-1] or bool(token.whitespace_)
            continue
        words.append(word)
        spaces.append(bool(token.whitespace_))
        starts.append(start)
        start = False
    return type(doc)(doc.vocab, words=words, spaces=spaces, sent_starts=starts if sents else None)


def load_pipeline(
    model: str = "ru_core_news_sm", exclude: Iterable[str] = (), **kwargs: Any
) -> Language:
    """
    Загрузка рекомендуемого конвейера spaCy

    Описание:
        Модель spaCy с токенами и предложениями anySeg и морфологией ruMorph: токенизатор
        anyseg.Tokenizer.v1, компонент rumorph первым вместо morphologizer и lemmatizer
        модели, anyseg_sentencizer перед парсером (без парсера - последним); парсер
        и остальные компоненты - модели. Предложения, части речи и признаки Doc такого
        конвейера - те же, что у строки, слова - тоже, кроме слов с частицей через дефис
        (муж-то, скажи-ка): части их токенов anySeg склеиваются в одно слово

    Аргументы:
        model (str): Имя или путь модели spaCy: ru_core_news_sm, ru_core_news_md, ru_core_news_lg
        exclude (list[str]): Еще компоненты модели, которые не загружаются, например ner
        **kwargs: Остальные параметры spacy.load; в config токенизатор заменяется на anySeg

    Вывод:
        Language: Конвейер

    Исключения:
        OSError: Если модель не установлена

    Пример использования:
        >>> from ruts import load_pipeline
        >>> nlp = load_pipeline()
        >>> nlp.pipe_names
        ['rumorph', 'tok2vec', 'anyseg_sentencizer', 'parser', 'attribute_ruler', 'ner']
        >>> [(token.text, token.pos_, token.lemma_) for token in nlp("Нож из стали.")]
        [('Нож', 'NOUN', 'нож'), ('из', 'ADP', 'из'), ('стали', 'NOUN', 'сталь'), ('.', 'PUNCT', '.')]
    """
    import spacy

    config = dict(kwargs.pop("config", {}))
    config["nlp"] = {**config.get("nlp", {}), "tokenizer": {"@tokenizers": "anyseg.Tokenizer.v1"}}
    nlp = spacy.load(
        model, exclude=["morphologizer", "lemmatizer", *exclude], config=config, **kwargs
    )
    nlp.add_pipe("rumorph", first=True)
    if "parser" in nlp.pipe_names:
        nlp.add_pipe("anyseg_sentencizer", before="parser")
    else:
        nlp.add_pipe("anyseg_sentencizer")
    return nlp


def add_dash_rules(nlp: Language) -> None:
    """
    Добавление в токенизатор пайплайна spaCy правил для тире реплик

    Описание:
        С правилами TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES и TOKENIZER_INFIXES
        слова Doc совпадают со словами строки (iter_tokens); правила добавляет
        add_tokenizer_rules ядра, повторно - не добавляет. Компоненты ruTS добавляют
        их в свой пайплайн сами

    Аргументы:
        nlp (Language): Пайплайн, в токенизатор которого добавляются правила

    Примеры использования:
        >>> import spacy
        >>> from ruts.utils import add_dash_rules
        >>> nlp = spacy.blank("ru")
        >>> [token.text for token in nlp("-Нет -сказал он.")]
        ['-Нет', '-сказал', 'он', '.']
        >>> add_dash_rules(nlp)
        >>> [token.text for token in nlp("-Нет -сказал он.")]
        ['-', 'Нет', '-', 'сказал', 'он', '.']
    """
    add_tokenizer_rules(nlp, TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES)
