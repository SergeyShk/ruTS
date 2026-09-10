import re
from collections.abc import Callable, Generator
from itertools import islice
from pathlib import Path
from typing import Any

from ..constants import DEFAULT_DATA_DIR
from ..utils import download_file, extract_archive, to_path
from .dataset import Dataset

# Фильтр - предикат над записью набора данных
Filters = list[Callable[[dict[str, Any]], bool]]

NAME = "sov_chrest_lit"
META = {
    "url": "https://dataverse.harvard.edu/file.xhtml?fileId=3670902&version=DRAFT",
    "description": "Корпус советских хрестоматий по литературе",
    "author": "Шкарин С.С.",
}
DOWNLOAD_URL = (
    "https://github.com/SergeyShk/ruTS/raw/master/ruts/datasets/data/sov_chrest_lit.tar.xz"
)
TEXT_TYPES = [
    "Рассказ",
    "Стихотворение",
    "Сказка",
    "Пословица",
    "Загадка",
    "Песня",
    "Басня",
]
DEFAULT_DATASET_DIR = DEFAULT_DATA_DIR.joinpath("texts")


class SovChLit(Dataset):
    """
    Класс для работы с набором данных советских хрестоматий по литературе

    Описание:
        Для формирования набора данных используются оцифрованные издания проекта "Школьные учебники СССР":
            1. Родная речь. Книга для чтения в I классе начальной школы. Е.Е. Соловьева, Л.А. Карпинская, Н.Н. Щепетова

    Ссылки:
        https://dataverse.harvard.edu/file.xhtml?fileId=3670902&version=DRAFT
        https://sheba.spb.ru/shkola/lit.htm

    Примеры использования:
    Информация о наборе данных:
        >>> from ruts.datasets import SovChLit
        >>> svc = SovChLit()
        >>> svc.info
        {'description': 'Корпус советских хрестоматий по литературе',
        'url': 'https://dataverse.harvard.edu/file.xhtml?fileId=3670902&version=DRAFT',
        'Наименование': 'sov_chrest_lit'}

    Итерация по набору данных:
        >>> for i in svc.get_records(max_len=100, category='Весна', limit=1):
        >>>     print(i)
        {'author': 'Е. Трутнева',
        'book': 'Родная речь. Книга для чтения в I классе начальной школы',
        'category': 'Весна',
        'file': PosixPath('../ruTS/ruts_data/texts/sov_chrest_lit/grade_1/155'),
        'grade': 1,
        'subject': 'Дождик',
        'text': 'Дождик, дождик, поливай, будет хлеба каравай!\n'
                'Дождик, дождик, припусти, дай гороху подрасти!',
        'type': 'Стихотворение',
        'year': 1963}

    Аргументы:
        data_dir (str): Путь к директории с набором данных

    Атрибуты:
        labels (tuple[str]): Кортеж уровней сложности текстов

    Методы:
        check_data: Проверка наличия всех необходимых директорий и файлов в наборе данных
        download: Загрузка набора данных из сети
        get_texts: Получение текстов (без заголовков) из набора данных
        get_records: Получение записей (с заголовками) из набора данных
    """

    def __init__(self, data_dir: str | Path = DEFAULT_DATASET_DIR) -> None:
        super().__init__(NAME, meta=META)
        self.data_dir = to_path(data_dir).resolve()
        self.labels = ("grade_1",)
        self._filename = NAME + ".tar.xz"
        self._filepath = self.data_dir.joinpath(self._filename)

    @property
    def filepath(self) -> str | None:
        """
        Путь к архиву набора данных.
        """
        if self._filepath.is_file():
            return str(self._filepath)
        return None

    def check_data(self) -> bool:
        """
        Проверка наличия всех необходимых директорий и файлов в наборе данных

        Вывод:
            bool: Результат проверки

        Исключения:
            OSError: Если набор данных не обнаружен
        """
        dirpaths = (self.data_dir.joinpath(NAME, label) for label in self.labels)
        for dirpath in dirpaths:
            if not dirpath.is_dir():
                msg = (
                    f"Набор данных {NAME} не обнаружен\n"
                    "Загрузите его, выполнив команды:\n"
                    ">>> svc = SovChLit()\n"
                    ">>> svc.download()"
                )
                raise OSError(msg)
        return True

    def download(self, force: bool = False) -> None:
        """
        Загрузка набора данных из сети и извлечение файлов

        Аргументы:
            force (bool): Загрузить набор данных, даже если он уже загружен
        """
        filepath = download_file(
            url=DOWNLOAD_URL,
            filename="sov_chrest_lit.tar.xz",
            dirpath=self.data_dir,
            force=force,
        )
        if filepath:
            extract_archive(filepath)
        self.check_data()

    def get_texts(
        self,
        grade: int | None = None,
        book: str | None = None,
        year: int | None = None,
        category: str | None = None,
        text_type: str | None = None,
        subject: str | None = None,
        author: str | None = None,
        min_len: int | None = None,
        max_len: int | None = None,
        limit: int | None = None,
    ) -> Generator[str, None, None]:
        """
        Получение текстов (без заголовков) из набора данных

        Аргументы:
            grade (int): Уровень сложности текстов
            book (str): Наименование книги
            year (int): Год издания книги
            category (str): Категория текстов
            text_type (str): Тип текстов
            subject (str): Наименование текстов
            author (str): Автор текстов
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)
            limit (int): Количество текстов

        Вывод:
            generator[str]: Генератор текстов
        """
        filters = self.__get_filters(
            grade, book, year, category, text_type, subject, author, min_len, max_len
        )
        for record in islice(self.__filtered_iter(filters), limit):
            yield record["text"]

    def get_records(
        self,
        grade: int | None = None,
        book: str | None = None,
        year: int | None = None,
        category: str | None = None,
        text_type: str | None = None,
        subject: str | None = None,
        author: str | None = None,
        min_len: int | None = None,
        max_len: int | None = None,
        limit: int | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        """
        Получение записей (с заголовками) из набора данных

        Аргументы:
            grade (int): Уровень сложности текстов
            book (str): Наименование книги
            year (int): Год издания книги
            category (str): Категория текстов
            text_type (str): Тип текстов
            subject (str): Наименование текстов
            author (str): Автор текстов
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)
            limit (int): Количество текстов

        Вывод:
            generator[dict[str, object]]: Генератор записей
        """
        filters = self.__get_filters(
            grade, book, year, category, text_type, subject, author, min_len, max_len
        )
        yield from islice(self.__filtered_iter(filters), limit)

    def __iter__(self) -> Generator[dict[str, Any], None, None]:
        """
        Итерация по набору данных

        Вывод:
            generator[dict[str, object]]: Генератор записей
        """
        self.check_data()
        dirpaths = (self.data_dir.joinpath(NAME, label) for label in self.labels)
        for dirpath in dirpaths:
            for filepath in sorted(dirpath.iterdir()):
                if re.match(r"[0-9]+", filepath.name):
                    yield self.__load_record(filepath)

    def __filtered_iter(self, filters: Filters) -> Generator[dict[str, Any], None, None]:
        """
        Итерация по набору данных с учетом фильтров

        Аргументы:
            filters (Filters): Список фильтров-предикатов

        Вывод:
            generator[dict[str, object]]: Генератор записей
        """
        if filters:
            for record in self:
                if all(filter_(record) for filter_ in filters):
                    yield record
        else:
            for record in self:
                yield record

    @staticmethod
    def __load_record(filepath: str | Path) -> dict[str, Any]:
        """
        Загрузка записи из файла набора данных

        Аргументы:
            filepath (str|Path): Путь к файлу набора данных

        Вывод:
            dict[str, object]: Справочник полей загруженной записи

        Исключения:
            ValueError: Если не удалось извлечь записи из файла
        """
        try:
            with to_path(filepath).open(encoding="utf-8") as f:
                header_block, text = f.read().strip().split("\n\n")
                headers = tuple(header.split(":")[1][1:] for header in header_block.split("\n"))
            return {
                "grade": int(headers[0]),
                "book": headers[1],
                "year": int(headers[2]),
                "category": headers[3],
                "type": headers[4],
                "subject": headers[5],
                "author": headers[6],
                "text": text,
                "file": filepath,
            }
        except Exception as e:
            raise ValueError("Не удалось извлечь записи из файла") from e

    @staticmethod
    def __get_filters(
        grade: int | None,
        book: str | None,
        year: int | None,
        category: str | None,
        text_type: str | None,
        subject: str | None,
        author: str | None,
        min_len: int | None,
        max_len: int | None,
    ) -> Filters:
        """
        Получение списка фильтров

        Аргументы:
            grade (int): Уровень сложности текстов
            book (str): Наименование книги
            year (int): Год издания книги
            category (str): Категория текстов
            text_type (str): Тип текстов
            subject (str): Наименование текста
            author (str): Автор текста
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)

        Вывод:
            filters (Filters): Список фильтров-предикатов

        Исключения:
            ValueError: Если некорректно выбран уровень текста
            ValueError: Если некорректно выбран тип текста
            ValueError: Если минимальная длина текста не больше 0
            ValueError: Если максимальная длина текста не больше 0
            ValueError: Если минимальная длина текста больше максимальной
        """
        filters: Filters = []
        if grade:
            if grade not in range(1, 12):
                raise ValueError(f"Некорректно выбран уровень текста (1-11) - {grade}")
            filters.append(lambda record: record.get("grade", "") == grade)
        if book:
            pattern = re.compile(f".*{book}.*", re.IGNORECASE)
            filters.append(lambda record: len(re.findall(pattern, record.get("book", ""))) > 0)
        if year:
            filters.append(lambda record: record.get("year", "") == year)
        if category:
            filters.append(lambda record: record.get("category", "") == category)
        if text_type:
            if text_type not in TEXT_TYPES:
                raise ValueError(f"Некорректно выбран тип текста - {text_type}")
            filters.append(lambda record: record.get("type", "") == text_type)
        if subject:
            pattern = re.compile(f".*{subject}.*", re.IGNORECASE)
            filters.append(lambda record: len(re.findall(pattern, record.get("subject", ""))) > 0)
        if author:
            pattern = re.compile(f".*{author}.*", re.IGNORECASE)
            filters.append(lambda record: len(re.findall(pattern, record.get("author", ""))) > 0)
        if min_len:
            if min_len < 1:
                raise ValueError("Минимальная длина текста должна быть больше 0")
            filters.append(lambda record: len(record.get("text", "")) >= min_len)
        if max_len:
            if max_len < 1:
                raise ValueError("Максимальная длина текста должна быть больше 0")
            filters.append(lambda record: len(record.get("text", "")) <= max_len)
        if min_len and max_len and min_len > max_len:
            raise ValueError("Минимальная длина текста больше максимальной")
        return filters
