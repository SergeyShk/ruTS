import hashlib
import logging
import os
import shutil
import tarfile
import unicodedata
import urllib.parse
import urllib.request
import zipfile
from collections.abc import Iterable, Iterator, Sequence
from functools import lru_cache
from pathlib import Path, PurePosixPath

import pymorphy3
from razdel import tokenize
from spacy.tokens import Doc, Span, Token

from .constants import (
    DEFAULT_DATA_DIR,
    PUNCTUATIONS,
    RU_VOWELS,
    UD_TO_OPENCORPORA_POS,
    VERBAL_NOUN_LEMMAS,
    VERBAL_NOUN_SUFFIXES,
)
from .exceptions import DataFileError, DownloadError, SourceTypeError

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_morph_analyzer() -> pymorphy3.MorphAnalyzer:
    """
    Получение морфологического анализатора pymorphy3

    Вывод:
        MorphAnalyzer: Морфологический анализатор
    """
    return pymorphy3.MorphAnalyzer()


@lru_cache(maxsize=131072)
def parse_word(word: str) -> pymorphy3.analyzer.Parse:
    """
    Морфологический разбор словоформы с кэшированием

    Описание:
        Возвращает первый (наиболее вероятный) разбор pymorphy3
        Результаты кэшируются по словоформе: в тексте на 75 тысяч токенов
        всего около 14 тысяч уникальных форм, повторный разбор не нужен

    Аргументы:
        word (str): Словоформа

    Вывод:
        Parse: Разбор словоформы
    """
    return get_morph_analyzer().parse(word)[0]


@lru_cache(maxsize=131072)
def lemmatize(word: str, pos: str = "") -> str:
    """
    Лемматизация словоформы pymorphy3 с учетом части речи Universal Dependencies

    Описание:
        Среди разборов словоформы выбирается первый, часть речи которого соответствует
        заданной части речи UD по таблице UD_TO_OPENCORPORA_POS, как делает
        лемматизатор spaCy для русского языка: «стали» с NOUN - сталь, с VERB - стать
        Без части речи или без подходящего разбора берется первый разбор

    Аргументы:
        word (str): Словоформа
        pos (str): Часть речи UD

    Вывод:
        str: Лемма
    """
    parses = get_morph_analyzer().parse(word)
    allowed = UD_TO_OPENCORPORA_POS.get(pos, frozenset())
    parse = next((parse for parse in parses if parse.tag.POS in allowed), parses[0])
    return str(parse.normal_form)


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


def normalize_yo(word: str) -> str:
    """
    Замена буквы ё на е в нижнем регистре

    Аргументы:
        word (str): Слово

    Вывод:
        str: Слово без буквы ё
    """
    return word.lower().replace("ё", "е")


def find_phrases(words: Sequence[str], phrases: Iterable[str]) -> list[tuple[int, int]]:
    """
    Поиск словосочетаний в последовательности слов

    Описание:
        Слова и словосочетания сравниваются в нижнем регистре без буквы ё; в каждой
        позиции выбирается самое длинное словосочетание, найденные не пересекаются
        Словосочетания индексируются по первому слову, так что в каждой позиции
        сравниваются только начинающиеся с этого слова

    Аргументы:
        words (list[str]): Слова текста
        phrases (list[str]): Словосочетания через пробел

    Вывод:
        list[tuple[int, int]]: Границы найденных словосочетаний как срезы words;
            пустые словосочетания пропускаются
    """
    patterns = sorted(
        {pattern for phrase in phrases if (pattern := tuple(normalize_yo(phrase).split()))},
        key=len,
        reverse=True,
    )
    by_first: dict[str, list[tuple[str, ...]]] = {}
    for pattern in patterns:
        by_first.setdefault(pattern[0], []).append(pattern)
    normalized = [normalize_yo(word) for word in words]
    spans = []
    position = 0
    while position < len(normalized):
        for pattern in by_first.get(normalized[position], ()):
            end = position + len(pattern)
            if tuple(normalized[position:end]) == pattern:
                spans.append((position, end))
                position = end
                break
        else:
            position += 1
    return spans


def iter_text_words(text: str) -> Iterator[tuple[int, int, str]]:
    """
    Извлечение слов с позициями из строки

    Описание:
        Токенизация razdel, знаки препинания отбрасываются как в WordsExtractor

    Аргументы:
        text (str): Строка текста

    Вывод:
        generator[tuple[int, int, str]]: Позиция первого символа, позиция за последним
            символом и текст каждого слова
    """
    for token in tokenize(text):
        if not is_punctuation(token.text):
            yield token.start, token.stop, token.text


def iter_doc_units(source: Doc | Span) -> Iterator[list[Token]]:
    """
    Извлечение слов из объекта Doc или Span в виде списков токенов

    Описание:
        Знаки препинания и символы отбрасываются той же проверкой is_punctuation,
        что и для строки (№, %, $ и другие символы категории S - не слова, хотя
        spaCy не считает их пунктуацией), пробельные токены пропускаются. Слова
        с дефисом (во-первых, по-видимому, кое-как), которые токенизатор spaCy
        режет на части и дефис, склеиваются обратно, если между частями нет
        пробелов, - razdel в основном оставляет такие слова целыми; обычное
        слово - список из одного токена

    Аргументы:
        source (Doc|Span): Объект Doc или Span

    Вывод:
        generator[list[Token]]: Токены каждого слова
    """
    tokens = list(source)
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.is_space or is_punctuation(token.text):
            index += 1
            continue
        last = index
        while (
            last + 2 < len(tokens)
            and tokens[last + 1].text == "-"
            and not tokens[last].whitespace_
            and not tokens[last + 1].whitespace_
            and not tokens[last + 2].is_space
            and not is_punctuation(tokens[last + 2].text)
        ):
            last += 2
        yield tokens[index : last + 1]
        index = last + 1


def iter_doc_words(source: Doc | Span) -> Iterator[tuple[int, int, str]]:
    """
    Извлечение слов с позициями из объекта Doc или Span

    Описание:
        Слова собираются из токенов iter_doc_units, текст дефисного слова - из текстов
        его частей, между которыми нет пробелов

    Аргументы:
        source (Doc|Span): Объект Doc или Span

    Вывод:
        generator[tuple[int, int, str]]: Позиция первого символа, позиция за последним
            символом и текст каждого слова
    """
    for unit in iter_doc_units(source):
        yield unit[0].idx, unit[-1].idx + len(unit[-1]), "".join(token.text for token in unit)


def is_punctuation(token: str) -> bool:
    """
    Проверка, состоит ли токен только из знаков препинания и символов

    Описание:
        Знаками считаются символы из PUNCTUATIONS и символы Юникода категорий
        P (пунктуация) и S (символы), поэтому фильтруются и многосимвольные
        токены вроде «?!», «!..», «--», «…», «№», «„»

    Аргументы:
        token (str): Токен

    Вывод:
        bool: Результат проверки
    """
    return all(char in PUNCTUATIONS or unicodedata.category(char)[0] in "PS" for char in token)


_DELETE_VOWELS = str.maketrans("", "", "".join(RU_VOWELS))


@lru_cache(maxsize=1 << 16)
def count_letters(word: str) -> int:
    """
    Вычисление количества букв в строке

    Описание:
        Буквы любого алфавита (str.isalpha), без цифр, дефисов и знаков; результаты
        кэшируются по словоформе, поэтому повторный подсчет бесплатен. Для целых
        текстов функция не предназначена - они осели бы в кэше

    Аргументы:
        word (str): Словоформа

    Вывод:
        int: Количество букв
    """
    return sum(map(str.isalpha, word))


@lru_cache(maxsize=1 << 16)
def count_syllables(word: str) -> int:
    """
    Вычисление количества слогов в слове

    Описание:
        Число гласных букв; результаты кэшируются по словоформе

    Аргументы:
        word (str): Строка слова

    Вывод:
        int: Количество слогов
    """
    return len(word) - len(word.translate(_DELETE_VOWELS))


def check_sequence(value: object, what: str = "слов") -> None:
    """
    Проверка, что аргумент - последовательность, а не строка

    Описание:
        Строка формально удовлетворяет Sequence[str], но перебирается посимвольно;
        функции, ожидающие список слов или текстов, отвергают ее явно

    Аргументы:
        value (object): Проверяемое значение
        what (str): Что ожидается, для сообщения об ошибке

    Исключения:
        SourceTypeError: Если передана строка
    """
    if isinstance(value, str):
        raise SourceTypeError(f"Ожидается список {what}, а не строка")


def to_path(path: str | Path) -> Path:
    """
    Перевод строкового представления пути в объект Path

    Аргументы:
        path (str): Cтроковое представление пути

    Вывод:
        Path: Объект Path

    Исключения:
        SourceTypeError: Если передаваемое значение не является строкой или объектом Path
    """
    if isinstance(path, str):
        return Path(path)
    if isinstance(path, Path):
        return path
    raise SourceTypeError("Некорректно указан путь")


DOWNLOAD_TIMEOUT = 60


def download_file(
    url: str,
    filename: str | None = None,
    dirpath: str | Path = DEFAULT_DATA_DIR,
    force: bool = False,
) -> str:
    """
    Загрузка файла из сети

    Аргументы:
        url (str): Адрес загружаемого файла
        filename (str): Название файла после загрузки
        dirpath (str|Path): Путь к директории для загруженного файла
        force (bool): Загрузить набор данных, даже если он уже загружен

    Вывод:
        str: Путь к загруженному файлу

    Описание:
        Файл пишется во временное имя рядом с целевым и переименовывается после
        полной загрузки, поэтому оборванная загрузка не оставляет частичного файла,
        который следующий вызов принял бы за загруженный. Соединение ждет ответа
        не дольше DOWNLOAD_TIMEOUT секунд

    Исключения:
        DownloadError: Если не удалось создать директорию или загрузить файл
    """
    dirpath = to_path(dirpath)
    try:
        dirpath.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise DownloadError(f"Не удалось создать директорию {dirpath}") from e
    if not filename:
        filename = Path(urllib.parse.urlparse(urllib.parse.unquote_plus(url)).path).name
    filepath = dirpath.resolve() / filename
    if filepath.is_file() and force is False:
        logger.info("Файл %s уже загружен", filepath)
        return ""
    partial = filepath.with_name(filepath.name + ".part")
    try:
        logger.info("Загрузка файла %s", url)
        req = urllib.request.Request(url)
        with (
            urllib.request.urlopen(req, timeout=DOWNLOAD_TIMEOUT) as response,
            partial.open("wb") as out_file,
        ):
            shutil.copyfileobj(response, out_file)
        partial.replace(filepath)
    except Exception as e:
        partial.unlink(missing_ok=True)
        raise DownloadError("Не удалось загрузить файл") from e
    logger.info("Файл загружен: %s", filepath)
    return str(filepath)


def _is_outside(member: str) -> bool:
    """Проверка, что путь члена архива ведет за пределы директории извлечения"""
    parts = PurePosixPath(member.replace("\\", "/")).parts
    return bool(parts) and (parts[0] in ("/", "..") or ".." in parts)


def extract_archive(archive_file: str | Path, extract_dir: str | Path | None = None) -> str:
    """
    Извлечение файлов из архива в формате ZIP или TAR

    Описание:
        Архив ZIP извлекается через ZipFile.extractall: shutil.unpack_archive в части
        версий Python пропускает файлы, в имени которых есть две точки подряд
        («Ма-аленькая!....txt»), а не только компоненты пути «..». Если корень
        архива отличается от имени архива без расширений, он переименовывается,
        а прежняя директория с этим именем удаляется, иначе повторное извлечение
        положило бы копию внутрь нее

    Аргументы:
        archive_file (str|Path): Путь к файлу архива
        extract_dir (str|Path): Путь к директории для извлеченных файлов

    Вывод:
        str: Путь к директории с извлеченными файлами

    Исключения:
        DataFileError: Если архив поврежден, содержит пути за пределами директории
            извлечения или директорию не удалось создать
    """
    archive_path = to_path(archive_file).resolve()
    extract_path = to_path(extract_dir) if extract_dir else archive_path.parent
    try:
        extract_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise DataFileError(f"Не удалось создать директорию {extract_path}") from e
    is_zip = zipfile.is_zipfile(archive_path)
    is_tar = tarfile.is_tarfile(archive_path)
    if not is_zip and not is_tar:
        logger.warning("Файл %s не является архивом в формате ZIP или TAR", archive_path)
        return str(extract_path)
    logger.info("Извлечение файлов из архива %s", archive_path)
    try:
        if is_zip:
            with zipfile.ZipFile(archive_path, mode="r") as zip_file:
                members = zip_file.namelist()
                if any(_is_outside(member) for member in members):
                    raise DataFileError(
                        f"Архив {archive_path} содержит пути за пределами директории"
                    )
                zip_file.extractall(extract_path)
        else:
            shutil.unpack_archive(archive_path, extract_dir=extract_path, filter="data")
            with tarfile.open(archive_path, mode="r") as tar_file:
                members = tar_file.getnames()
    except (OSError, zipfile.BadZipFile, tarfile.TarError, shutil.ReadError) as e:
        raise DataFileError(f"Не удалось извлечь архив {archive_path}") from e
    src_basename = os.path.commonpath(members)
    if src_basename and not (extract_path / src_basename).is_dir():
        src_basename = str(Path(src_basename).parent)
    if not src_basename or src_basename == ".":
        return str(extract_path)
    # Отбрасываем все расширения: stalin_works.tar.xz -> stalin_works
    dest_basename = archive_path.name
    while (stem := Path(dest_basename).stem) != dest_basename:
        dest_basename = stem
    if src_basename != dest_basename:
        destination = extract_path / dest_basename
        if destination.is_dir():
            shutil.rmtree(destination)
        return str(shutil.move(extract_path / src_basename, destination))
    return str(extract_path / src_basename)


def sha256(path: Path) -> str:
    """
    Вычисление контрольной суммы SHA-256 файла

    Аргументы:
        path (Path): Путь к файлу

    Вывод:
        str: Контрольная сумма в шестнадцатеричном виде, пустая строка для отсутствующего файла
    """
    if not path.is_file():
        return ""
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def safe_divide(num: float | int, den: float | int, default: float | int = 0) -> float:
    """
    Безопасное деление двух чисел

    Аргументы:
        num (float|int): Число в числителе
        den (float|int): Число в знаменателе
        default (float|int): Значение по умолчанию при возникновении ошибки

    Вывод:
        float: Результат безопасного деления
    """
    if not den:
        return default
    return num / den
