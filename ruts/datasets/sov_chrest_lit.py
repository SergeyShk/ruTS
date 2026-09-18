from collections.abc import Generator
from itertools import islice
from pathlib import Path
from typing import Any

from ..constants import DEFAULT_DATA_DIR
from ..exceptions import DataFileError, DatasetNotFoundError, ParameterError
from ..utils import download_file, extract_archive, to_path
from .dataset import Dataset, Filters, check_limit, length_filters, substring_filter

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
    "Совет",
    "Шутка",
]
GRADES = (1,)
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
        >>> from pprint import pprint
        >>> from ruts.datasets import SovChLit
        >>> svc = SovChLit()
        >>> pprint(svc.info)
        {'author': 'Шкарин С.С.',
         'description': 'Корпус советских хрестоматий по литературе',
         'url': 'https://dataverse.harvard.edu/file.xhtml?fileId=3670902&version=DRAFT',
         'Наименование': 'sov_chrest_lit'}

    Итерация по набору данных:
        >>> for record in svc.get_records(max_len=100, category='Весна', limit=1):
        ...     pprint(record)
        {'author': 'С. Маршак',
         'book': 'Родная речь. Книга для чтения в I классе начальной школы',
         'category': 'Весна',
         'file': ...Path('.../ruts_data/texts/sov_chrest_lit/grade_1/114'),
         'grade': 1,
         'subject': 'Март',
         'text': 'Рыхлый снег темнеет в марте, тают льдинки на окне.\\n'
                 'Зайчик бегает по парте и по карте на стене.',
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
        self.labels = tuple(f"grade_{grade}" for grade in GRADES)
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
            DatasetNotFoundError: Если набор данных не обнаружен
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
                raise DatasetNotFoundError(msg)
        return True

    def download(self, force: bool = False) -> None:
        """
        Загрузка набора данных из сети и извлечение файлов

        Описание:
            Если архив уже есть, а какой-то из директорий уровней нет, архив
            извлекается заново

        Аргументы:
            force (bool): Загрузить набор данных, даже если он уже загружен
        """
        filepath = download_file(
            url=DOWNLOAD_URL,
            filename=self._filename,
            dirpath=self.data_dir,
            force=force,
        )
        missing = any(not self.data_dir.joinpath(NAME, label).is_dir() for label in self.labels)
        if filepath or missing:
            extract_archive(self._filepath)
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
            book (str): Наименование книги (подстрока без учета регистра)
            year (int): Год издания книги
            category (str): Категория текстов (подстрока без учета регистра)
            text_type (str): Тип текстов
            subject (str): Наименование текстов (подстрока без учета регистра)
            author (str): Автор текстов (подстрока без учета регистра)
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)
            limit (int): Количество текстов

        Вывод:
            generator[str]: Генератор текстов
        """
        filters = self.__get_filters(
            grade, book, year, category, text_type, subject, author, min_len, max_len
        )
        check_limit(limit)
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
            book (str): Наименование книги (подстрока без учета регистра)
            year (int): Год издания книги
            category (str): Категория текстов (подстрока без учета регистра)
            text_type (str): Тип текстов
            subject (str): Наименование текстов (подстрока без учета регистра)
            author (str): Автор текстов (подстрока без учета регистра)
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)
            limit (int): Количество текстов

        Вывод:
            generator[dict[str, object]]: Генератор записей
        """
        filters = self.__get_filters(
            grade, book, year, category, text_type, subject, author, min_len, max_len
        )
        check_limit(limit)
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
            filepaths = (path for path in dirpath.iterdir() if path.name.isdigit())
            for filepath in sorted(filepaths, key=lambda path: int(path.name)):
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
            DataFileError: Если не удалось извлечь записи из файла
        """
        try:
            with to_path(filepath).open(encoding="utf-8") as f:
                header_block, text = f.read().strip().split("\n\n", maxsplit=1)
                headers = tuple(
                    header.split(":", 1)[1].strip() for header in header_block.split("\n")
                )
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
            raise DataFileError("Не удалось извлечь записи из файла") from e

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
            book (str): Наименование книги (подстрока без учета регистра)
            year (int): Год издания книги
            category (str): Категория текстов (подстрока без учета регистра)
            text_type (str): Тип текстов
            subject (str): Наименование текста (подстрока без учета регистра)
            author (str): Автор текста (подстрока без учета регистра)
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)

        Вывод:
            filters (Filters): Список фильтров-предикатов

        Исключения:
            ParameterError: Если некорректно выбран уровень текста
            ParameterError: Если некорректно выбран тип текста
            ParameterError: Если минимальная длина текста не больше 0
            ParameterError: Если максимальная длина текста не больше 0
            ParameterError: Если минимальная длина текста больше максимальной
        """
        filters: Filters = []
        if grade is not None:
            if grade not in GRADES:
                raise ParameterError(f"Некорректно выбран уровень текста {GRADES} - {grade}")
            filters.append(lambda record: record["grade"] == grade)
        if book is not None:
            filters.append(substring_filter("book", book))
        if year is not None:
            filters.append(lambda record: record["year"] == year)
        if category is not None:
            filters.append(substring_filter("category", category))
        if text_type is not None:
            if text_type not in TEXT_TYPES:
                raise ParameterError(f"Некорректно выбран тип текста - {text_type}")
            filters.append(lambda record: record["type"] == text_type)
        if subject is not None:
            filters.append(substring_filter("subject", subject))
        if author is not None:
            filters.append(substring_filter("author", author))
        filters.extend(length_filters(min_len, max_len))
        return filters
