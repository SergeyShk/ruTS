import re
import shutil
from collections.abc import Callable, Generator
from itertools import islice
from pathlib import Path
from typing import Any

from ..constants import DEFAULT_DATA_DIR
from ..utils import download_file, extract_archive, normalize_yo, sha256, to_path
from .dataset import Dataset

# Фильтр - предикат над записью набора данных
Filters = list[Callable[[dict[str, Any]], bool]]

NAME = "russian_literature"
META = {
    "url": "https://github.com/d0rj/RusLit",
    "description": "Собрание русской классической литературы RusLit",
    "author": "d0rj",
    "license": "Общественное достояние (PDDL)",
}
COMMIT = "4509680428729da225a73a22008133660f92bb7e"
DOWNLOAD_URL = f"https://github.com/d0rj/RusLit/archive/{COMMIT}.zip"
ARCHIVE = NAME + ".zip"
ARCHIVE_SHA256 = "76cf8a91353c62b49dad7c282c5a6d42dcc5f8b0ab27f910ebdc8009579c8993"
GENRES = ("prose", "poems", "publicism")
AUTHORS = {
    "Blok": "Александр Блок",
    "Bryusov": "Валерий Брюсов",
    "Chekhov": "Антон Чехов",
    "Dostoevsky": "Фёдор Достоевский",
    "Gogol": "Николай Гоголь",
    "Gorky": "Максим Горький",
    "Herzen": "Александр Герцен",
    "Lermontov": "Михаил Лермонтов",
    "Nekrasov": "Николай Некрасов",
    "Pushkin": "Александр Пушкин",
    "Tolstoy": "Лев Толстой",
    "Turgenev": "Иван Тургенев",
}
ENCODINGS = ("utf-8", "cp1251")
DEFAULT_DATASET_DIR = DEFAULT_DATA_DIR.joinpath("texts")


class RussianLiterature(Dataset):
    """
    Класс для работы с собранием русской классической литературы RusLit

    Описание:
        373 произведения 12 авторов XIX - начала XX века в трех жанрах: проза
        (Чехов, Толстой, Достоевский, Горький, Брюсов, Гоголь, Герцен, Пушкин,
        Тургенев, Блок, Лермонтов - 269 текстов, от рассказов до романов), поэзия
        (Пушкин, Лермонтов, Некрасов, Блок - 78 текстов) и публицистика (Толстой -
        26 текстов); 39 млн символов. Год написания взят из файлов info.csv
        собрания, у 28 произведений его нет. Заголовок с именем автора
        и названием в начале файла срезается (strip_header) - у 288 текстов;
        у 8 фамилия автора остается в первых строках в других формах заголовка
        или посвящениях, что важно для атрибуции авторства
        Тексты в общественном достоянии (на Kaggle - лицензия PDDL), собраны
        с сайтов LitLib, Wikisource и Ilibrary; набор загружается из репозитория
        (закрепленный коммит) и сверяется с контрольной суммой SHA-256. Подходит
        для атрибуции авторства и сравнения жанров

    Ссылки:
        https://github.com/d0rj/RusLit
        https://www.kaggle.com/datasets/d0rj3228/russian-literature

    Примеры использования:
    Информация о наборе данных:
        >>> from ruts.datasets import RussianLiterature
        >>> rl = RussianLiterature()
        >>> rl.info
        {'Наименование': 'russian_literature',
        'author': 'd0rj',
        'description': 'Собрание русской классической литературы RusLit',
        'license': 'Общественное достояние (PDDL)',
        'url': 'https://github.com/d0rj/RusLit'}

    Итерация по набору данных:
        >>> for i in rl.get_records(genre='poems', author='Пушкин', limit=1):
        >>>     print(i)
        {'genre': 'poems',
        'author': 'Александр Пушкин',
        'title': '19 октября',
        'year_from': 1825,
        'year_to': 1825,
        'text': 'Роняет лес багряный свой убор...',
        'file': PosixPath('../ruTS/ruts_data/texts/russian_literature/poems/Pushkin/19 октября.txt')}

    Аргументы:
        data_dir (str): Путь к директории с набором данных

    Атрибуты:
        genres (tuple[str]): Кортеж жанров
        authors (dict[str, str]): Русские имена авторов по названиям папок

    Методы:
        check_data: Проверка наличия всех необходимых директорий в наборе данных
        download: Загрузка набора данных из сети
        get_texts: Получение текстов (без заголовков) из набора данных
        get_records: Получение записей (с заголовками) из набора данных
    """

    def __init__(self, data_dir: str | Path = DEFAULT_DATASET_DIR) -> None:
        super().__init__(NAME, meta=META)
        self.data_dir = to_path(data_dir).resolve()
        self.genres = GENRES
        self.authors = AUTHORS
        self._filepath = self.data_dir.joinpath(ARCHIVE)
        self._dirpath = self.data_dir.joinpath(NAME)

    @property
    def filepath(self) -> str | None:
        """
        Путь к архиву набора данных
        """
        if self._filepath.is_file():
            return str(self._filepath)
        return None

    def check_data(self) -> bool:
        """
        Проверка наличия всех необходимых директорий в наборе данных

        Вывод:
            bool: Результат проверки

        Исключения:
            OSError: Если набор данных не обнаружен
        """
        for genre in self.genres:
            if not self._dirpath.joinpath(genre).is_dir():
                msg = (
                    f"Набор данных {NAME} не обнаружен\n"
                    "Загрузите его, выполнив команды:\n"
                    ">>> rl = RussianLiterature()\n"
                    ">>> rl.download()"
                )
                raise OSError(msg)
        return True

    def download(self, force: bool = False) -> None:
        """
        Загрузка набора данных из сети и извлечение файлов

        Описание:
            Архив репозитория по закрепленному коммиту сверяется с контрольной
            суммой SHA-256; поврежденный или подмененный файл (например, после
            оборванной загрузки) удаляется и загружается заново в том же вызове.
            Если архив уже есть, а какой-то
            из папок жанров нет, архив извлекается заново; прежняя директория
            набора перед извлечением удаляется

        Аргументы:
            force (bool): Загрузить набор данных, даже если он уже загружен

        Исключения:
            RuntimeError: Если архив не прошел проверку
        """
        filepath = download_file(
            url=DOWNLOAD_URL, filename=ARCHIVE, dirpath=self.data_dir, force=force
        )
        missing = any(not self._dirpath.joinpath(genre).is_dir() for genre in self.genres)
        if filepath or missing:
            if sha256(self._filepath) != ARCHIVE_SHA256:
                self._filepath.unlink(missing_ok=True)
                download_file(
                    url=DOWNLOAD_URL, filename=ARCHIVE, dirpath=self.data_dir, force=True
                )
                if sha256(self._filepath) != ARCHIVE_SHA256:
                    self._filepath.unlink(missing_ok=True)
                    raise RuntimeError(
                        f"Файл {self._filepath} не прошел проверку контрольной суммы и удален, "
                        "повторите загрузку"
                    )
            shutil.rmtree(self._dirpath, ignore_errors=True)
            extract_archive(self._filepath, self.data_dir)
        self.check_data()

    def get_texts(
        self,
        genre: str | None = None,
        author: str | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        min_len: int | None = None,
        max_len: int | None = None,
        limit: int | None = None,
    ) -> Generator[str, None, None]:
        """
        Получение текстов (без заголовков) из набора данных

        Аргументы:
            genre (str): Жанр из GENRES - prose, poems или publicism
            author (str): Автор (подстрока русского имени без учета регистра)
            year_from (int): Наименьший год написания
            year_to (int): Наибольший год написания
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)
            limit (int): Количество текстов

        Вывод:
            generator[str]: Генератор текстов
        """
        filters = self.__get_filters(genre, author, year_from, year_to, min_len, max_len)
        for record in islice(self.__filtered_iter(filters), limit):
            yield record["text"]

    def get_records(
        self,
        genre: str | None = None,
        author: str | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        min_len: int | None = None,
        max_len: int | None = None,
        limit: int | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        """
        Получение записей (с заголовками) из набора данных

        Аргументы:
            genre (str): Жанр из GENRES - prose, poems или publicism
            author (str): Автор (подстрока русского имени без учета регистра)
            year_from (int): Наименьший год написания
            year_to (int): Наибольший год написания
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)
            limit (int): Количество текстов

        Вывод:
            generator[dict[str, object]]: Генератор записей
        """
        filters = self.__get_filters(genre, author, year_from, year_to, min_len, max_len)
        yield from islice(self.__filtered_iter(filters), limit)

    def __iter__(self) -> Generator[dict[str, Any], None, None]:
        """
        Итерация по набору данных

        Описание:
            Жанры в порядке GENRES, внутри - папки авторов и файлы по алфавиту;
            тексты читаются по одному, год ищется в info.csv по названию файла
            без учета регистра и буквы ё («Алёша горшок» и «Алёша Горшок»)

        Вывод:
            generator[dict[str, object]]: Генератор записей
        """
        self.check_data()
        for genre in self.genres:
            for author_dir in sorted(
                path for path in self._dirpath.joinpath(genre).iterdir() if path.is_dir()
            ):
                years = {
                    _title_key(title): value
                    for title, value in load_years(author_dir.joinpath("info.csv")).items()
                }
                author = self.authors.get(author_dir.name, author_dir.name)
                for filepath in sorted(author_dir.glob("*.txt")):
                    year_from, year_to = years.get(_title_key(filepath.stem), (None, None))
                    yield {
                        "genre": genre,
                        "author": author,
                        "title": filepath.stem,
                        "year_from": year_from,
                        "year_to": year_to,
                        "text": strip_header(read_text(filepath), author, filepath.stem),
                        "file": filepath,
                    }

    def __filtered_iter(self, filters: Filters) -> Generator[dict[str, Any], None, None]:
        """
        Итерация по набору данных с учетом фильтров

        Аргументы:
            filters (Filters): Список фильтров-предикатов

        Вывод:
            generator[dict[str, object]]: Генератор записей
        """
        for record in self:
            if all(filter_(record) for filter_ in filters):
                yield record

    @staticmethod
    def __get_filters(
        genre: str | None,
        author: str | None,
        year_from: int | None,
        year_to: int | None,
        min_len: int | None,
        max_len: int | None,
    ) -> Filters:
        """
        Получение списка фильтров

        Описание:
            Произведения без года не проходят фильтры по годам

        Аргументы:
            genre (str): Жанр из GENRES
            author (str): Автор (подстрока русского имени без учета регистра)
            year_from (int): Наименьший год написания
            year_to (int): Наибольший год написания
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)

        Вывод:
            filters (Filters): Список фильтров-предикатов

        Исключения:
            ValueError: Если некорректно выбран жанр
            ValueError: Если наименьший год больше наибольшего
            ValueError: Если минимальная длина текста не больше 0
            ValueError: Если максимальная длина текста не больше 0
            ValueError: Если минимальная длина текста больше максимальной
        """
        filters: Filters = []
        if genre:
            if genre not in GENRES:
                raise ValueError(f"Некорректно выбран жанр {GENRES} - {genre}")
            filters.append(lambda record: record["genre"] == genre)
        if author:
            pattern = re.compile(re.escape(author), re.IGNORECASE)
            filters.append(lambda record: pattern.search(record["author"]) is not None)
        if year_from is not None:
            filters.append(
                lambda record: record["year_from"] is not None and record["year_from"] >= year_from
            )
        if year_to is not None:
            filters.append(
                lambda record: record["year_to"] is not None and record["year_to"] <= year_to
            )
        if year_from is not None and year_to is not None and year_from > year_to:
            raise ValueError("Наименьший год больше наибольшего")
        if min_len:
            if min_len < 1:
                raise ValueError("Минимальная длина текста должна быть больше 0")
            filters.append(lambda record: len(record["text"]) >= min_len)
        if max_len:
            if max_len < 1:
                raise ValueError("Максимальная длина текста должна быть больше 0")
            filters.append(lambda record: len(record["text"]) <= max_len)
        if min_len and max_len and min_len > max_len:
            raise ValueError("Минимальная длина текста больше максимальной")
        return filters


def load_years(filepath: str | Path) -> dict[str, tuple[int | None, int | None]]:
    """
    Чтение годов написания произведений из файла info.csv

    Описание:
        Строки вида «название,год», год - 1825 или 1824-1825; название может
        содержать запятые и кавычки, поэтому разделяется по последней запятой,
        кавычки отбрасываются. Отсутствующий файл дает пустой справочник

    Аргументы:
        filepath (str|Path): Путь к файлу info.csv

    Вывод:
        dict[str, tuple[int|None, int|None]]: Первый и последний год по названию
    """
    path = to_path(filepath)
    if not path.is_file():
        return {}
    years = {}
    for line in read_text(path).splitlines()[1:]:
        if "," not in line:
            continue
        title, _, value = line.rpartition(",")
        years[title.strip().strip('"')] = parse_years(value)
    return years


def parse_years(value: str) -> tuple[int | None, int | None]:
    """
    Разбор года написания из info.csv

    Аргументы:
        value (str): Год или диапазон годов через дефис

    Вывод:
        tuple[int|None, int|None]: Первый и последний год, None без года
    """
    match = re.fullmatch(r"\s*(\d{4})(?:\s*-\s*(\d{4}))?\s*", value)
    if not match:
        return None, None
    first = int(match.group(1))
    return first, int(match.group(2)) if match.group(2) else first


def strip_header(text: str, author: str, title: str) -> str:
    """
    Удаление заголовка с автором и названием из начала текста

    Описание:
        Файлы собрания часто начинаются с имени автора и названия: «Александр
        Пушкин» и «19 ОКТЯБРЯ» на отдельных строках, «Валерий Брюсов. Бемоль»
        одной строкой, автор с отчеством («Валерий Яковлевич Брюсов»), инициалами
        («В.Я. Брюсов», «Л.Н.Толстой», «М. Горький») или фамилией впереди («Горький
        Максим»). Для атрибуции авторства это утечка, поэтому
        заголовок срезается, когда первая строка - имя автора записи в одной
        из этих форм (само по себе или с названием записи после точки), а следующая
        непустая строка при совпадении с названием тоже отбрасывается; повторенный
        заголовок срезается еще раз; сравнение без учета регистра и буквы ё.
        Заголовки в других формах остаются в тексте

    Аргументы:
        text (str): Текст файла
        author (str): Автор записи в виде «Имя Фамилия»
        title (str): Название записи

    Вывод:
        str: Текст без заголовка
    """
    lines = text.split("\n")
    name, surname = normalize_yo(author).split()[0], normalize_yo(author).split()[-1]
    given = rf"(?:{re.escape(name)}(?:\s+[^\W\d_]+)?|{re.escape(name[0])}\.\s*(?:[^\W\d_]\.)?)"
    header = re.compile(
        rf"^\s*(?:{given}\s*{re.escape(surname)}|{re.escape(surname)}\s+{given})"
        rf"\.?(?:\s+(?P<title>.+?))?\s*$"
    )
    while lines:
        match = header.match(normalize_yo(lines[0]))
        if not match:
            break
        remainder = _title_key(match.group("title") or "")
        if remainder and remainder != _title_key(title):
            break
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
        if lines and _title_key(lines[0]) == _title_key(title):
            lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
    return "\n".join(lines).strip()


def _title_key(value: str) -> str:
    return normalize_yo(value.strip().strip('"«»').strip().rstrip(".?!…"))


def read_text(filepath: str | Path) -> str:
    """
    Чтение текстового файла набора данных

    Описание:
        Файлы в UTF-8, единичные - в cp1251; кодировки из ENCODINGS перебираются
        по порядку

    Аргументы:
        filepath (str|Path): Путь к файлу

    Вывод:
        str: Текст файла

    Исключения:
        ValueError: Если файл не удалось прочитать ни в одной из кодировок
    """
    data = to_path(filepath).read_bytes()
    for encoding in ENCODINGS:
        try:
            return data.decode(encoding).lstrip("﻿").strip()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Не удалось прочитать файл {filepath}")
