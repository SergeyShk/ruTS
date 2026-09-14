import os
import shutil
import tarfile
import unicodedata
import urllib.parse
import urllib.request
import zipfile
from functools import lru_cache
from pathlib import Path

import pymorphy3

from .constants import DEFAULT_DATA_DIR, PUNCTUATIONS, RU_VOWELS, UD_TO_OPENCORPORA_POS


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


def count_syllables(word: str) -> int:
    """
    Вычисление количества слогов в слове

    Аргументы:
        word (str): Строка слова

    Вывод:
        int: Количество слогов
    """
    return sum(1 for char in word if char in RU_VOWELS)


def to_path(path: str | Path) -> Path:
    """
    Перевод строкового представления пути в объект Path

    Аргументы:
        path (str): Cтроковое представление пути

    Вывод:
        Path: Объект Path

    Исключения:
        TypeError: Если передаваемое значение не является строкой или объектом Path
    """
    if isinstance(path, str):
        return Path(path)
    if isinstance(path, Path):
        return path
    raise TypeError("Некорректно указан путь")


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

    Исключения:
        RuntimeError: Если не удалось загрузить файл
    """
    dirpath = to_path(dirpath)
    dirpath.mkdir(parents=True, exist_ok=True)
    if not filename:
        filename = Path(urllib.parse.urlparse(urllib.parse.unquote_plus(url)).path).name
    filepath = dirpath.resolve() / filename
    if filepath.is_file() and force is False:
        print(f"Файл {filepath} уже загружен")
        return ""
    try:
        print(f"Загрузка файла {url}...")
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response, filepath.open("wb") as out_file:
            shutil.copyfileobj(response, out_file)
    except Exception as e:
        raise RuntimeError("Не удалось загрузить файл") from e
    else:
        print(f"Файл успешно загружен: {filepath}")
    return str(filepath)


def extract_archive(archive_file: str | Path, extract_dir: str | Path | None = None) -> str:
    """
    Извлечение файлов из архива в формате ZIP или TAR

    Аргументы:
        archive_file (str|Path): Путь к файлу архива
        extract_dir (str|Path): Путь к директории для извлеченных файлов

    Вывод:
        str: Путь к директории с извлеченными файлами
    """
    archive_path = to_path(archive_file).resolve()
    extract_path = to_path(extract_dir) if extract_dir else archive_path.parent
    extract_path.mkdir(parents=True, exist_ok=True)
    is_zip = zipfile.is_zipfile(archive_path)
    is_tar = tarfile.is_tarfile(archive_path)
    if not is_zip and not is_tar:
        print(f"Файл {archive_path} не является архивом в формате ZIP или TAR")
        return str(extract_path)
    print(f"Извлечение файлов из архива {archive_path}...")
    if is_zip:
        shutil.unpack_archive(archive_path, extract_dir=extract_path)
        with zipfile.ZipFile(archive_path, mode="r") as zip_file:
            members = zip_file.namelist()
    else:
        shutil.unpack_archive(archive_path, extract_dir=extract_path, filter="data")
        with tarfile.open(archive_path, mode="r") as tar_file:
            members = tar_file.getnames()
    src_basename = os.path.commonpath(members)
    if not src_basename:
        return str(extract_path)
    # Отбрасываем все расширения: stalin_works.tar.xz -> stalin_works
    dest_basename = archive_path.name
    while (stem := Path(dest_basename).stem) != dest_basename:
        dest_basename = stem
    if src_basename != dest_basename:
        return str(shutil.move(extract_path / src_basename, extract_path / dest_basename))
    return str(extract_path / src_basename)


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
