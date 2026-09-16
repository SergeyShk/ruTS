import re
import xml.etree.ElementTree as ET
from collections import Counter
from collections.abc import Callable, Generator
from itertools import islice
from pathlib import Path
from typing import Any

from ..constants import DEFAULT_DATA_DIR
from ..utils import download_file, sha256, to_path
from .dataset import Dataset

# Фильтр - предикат над записью набора данных
Filters = list[Callable[[dict[str, Any]], bool]]

NAME = "poetry_corpus"
META = {
    "url": "https://github.com/IlyaGusev/PoetryCorpus",
    "description": "Корпус русской поэзии PoetryCorpus",
    "author": "Гусев И.О.",
    "license": "Apache-2.0",
}
COMMIT = "7a5f70e6a46b4717f7c903671f9a6a917aee6162"
DOWNLOAD_URL = f"https://github.com/IlyaGusev/PoetryCorpus/raw/{COMMIT}/datasets/corpus/all.xml"
FILENAME = "poetry_corpus.xml"
FILE_SHA256 = "3f6e43fb066916f3ee32dd7b63488c4831b62a29f72caa41e806a8ef59749c89"
DEFAULT_DATASET_DIR = DEFAULT_DATA_DIR.joinpath("texts")


class PoetryCorpus(Dataset):
    """
    Класс для работы с корпусом русской поэзии PoetryCorpus

    Описание:
        16 694 стихотворения 195 авторов XVIII-XX веков (13 млн символов), собранные
        Ильей Гусевым для библиотеки rupo: автор, название или первая строка, годы
        написания (есть у 12 857 стихотворений) и темы (20 тем, размечены
        3 904 стихотворения: о любви, военные, о дружбе, детские, о животных,
        о природе, патриотические, посвящения и другие)
        Корпус распространяется под лицензией Apache-2.0 и подходит для стилометрии,
        стиховедения и сравнения авторов; файл загружается из репозитория корпуса
        (закрепленный коммит) и сверяется с контрольной суммой SHA-256

    Ссылки:
        https://github.com/IlyaGusev/PoetryCorpus
        https://github.com/IlyaGusev/rupo

    Примеры использования:
    Информация о наборе данных:
        >>> from ruts.datasets import PoetryCorpus
        >>> pc = PoetryCorpus()
        >>> pc.info
        {'Наименование': 'poetry_corpus',
        'author': 'Гусев И.О.',
        'description': 'Корпус русской поэзии PoetryCorpus',
        'license': 'Apache-2.0',
        'url': 'https://github.com/IlyaGusev/PoetryCorpus'}

    Итерация по набору данных:
        >>> for i in pc.get_records(author='Лермонтов', theme='О любви', limit=1):
        >>>     print(i)
        {'author': 'Михаил Лермонтов',
        'title': 'Нищий',
        'themes': ('О любви',),
        'year_from': 1830,
        'year_to': 1830,
        'text': 'У врат обители святой...'}

    Аргументы:
        data_dir (str): Путь к директории с набором данных

    Атрибуты:
        authors (Counter): Число стихотворений по авторам
        themes (Counter): Число стихотворений по темам

    Методы:
        check_data: Проверка наличия файла набора данных
        download: Загрузка набора данных из сети
        get_texts: Получение текстов (без заголовков) из набора данных
        get_records: Получение записей (с заголовками) из набора данных
    """

    def __init__(self, data_dir: str | Path = DEFAULT_DATASET_DIR) -> None:
        super().__init__(NAME, meta=META)
        self.data_dir = to_path(data_dir).resolve()
        self._filepath = self.data_dir.joinpath(FILENAME)

    @property
    def filepath(self) -> str | None:
        """
        Путь к файлу набора данных
        """
        if self._filepath.is_file():
            return str(self._filepath)
        return None

    @property
    def authors(self) -> Counter[str]:
        """
        Число стихотворений по авторам
        """
        return Counter(record["author"] for record in self)

    @property
    def themes(self) -> Counter[str]:
        """
        Число стихотворений по темам
        """
        return Counter(theme for record in self for theme in record["themes"])

    def check_data(self) -> bool:
        """
        Проверка наличия файла набора данных

        Вывод:
            bool: Результат проверки

        Исключения:
            OSError: Если набор данных не обнаружен
        """
        if not self._filepath.is_file():
            msg = (
                f"Набор данных {NAME} не обнаружен\n"
                "Загрузите его, выполнив команды:\n"
                ">>> pc = PoetryCorpus()\n"
                ">>> pc.download()"
            )
            raise OSError(msg)
        return True

    def download(self, force: bool = False) -> None:
        """
        Загрузка набора данных из сети

        Описание:
            Файл корпуса загружается из репозитория по закрепленному коммиту
            и сверяется с контрольной суммой SHA-256; поврежденный или подмененный
            файл удаляется, чтобы повторная загрузка не пропускалась

        Аргументы:
            force (bool): Загрузить набор данных, даже если он уже загружен

        Исключения:
            RuntimeError: Если файл не прошел проверку
        """
        download_file(url=DOWNLOAD_URL, filename=FILENAME, dirpath=self.data_dir, force=force)
        if self._filepath.is_file() and sha256(self._filepath) != FILE_SHA256:
            self._filepath.unlink()
            raise RuntimeError(
                f"Файл {self._filepath} не прошел проверку контрольной суммы и удален, "
                "повторите загрузку"
            )
        self.check_data()

    def get_texts(
        self,
        author: str | None = None,
        theme: str | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        min_len: int | None = None,
        max_len: int | None = None,
        limit: int | None = None,
    ) -> Generator[str, None, None]:
        """
        Получение текстов (без заголовков) из набора данных

        Аргументы:
            author (str): Автор (подстрока без учета регистра)
            theme (str): Тема (подстрока без учета регистра)
            year_from (int): Наименьший год написания
            year_to (int): Наибольший год написания
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)
            limit (int): Количество текстов

        Вывод:
            generator[str]: Генератор текстов
        """
        filters = self.__get_filters(author, theme, year_from, year_to, min_len, max_len)
        for record in islice(self.__filtered_iter(filters), limit):
            yield record["text"]

    def get_records(
        self,
        author: str | None = None,
        theme: str | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        min_len: int | None = None,
        max_len: int | None = None,
        limit: int | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        """
        Получение записей (с заголовками) из набора данных

        Аргументы:
            author (str): Автор (подстрока без учета регистра)
            theme (str): Тема (подстрока без учета регистра)
            year_from (int): Наименьший год написания
            year_to (int): Наибольший год написания
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)
            limit (int): Количество текстов

        Вывод:
            generator[dict[str, object]]: Генератор записей
        """
        filters = self.__get_filters(author, theme, year_from, year_to, min_len, max_len)
        yield from islice(self.__filtered_iter(filters), limit)

    def __iter__(self) -> Generator[dict[str, Any], None, None]:
        """
        Итерация по набору данных

        Описание:
            Файл читается потоково (iterparse), разобранные стихотворения
            освобождаются, поэтому память не зависит от размера корпуса

        Вывод:
            generator[dict[str, object]]: Генератор записей

        Исключения:
            ValueError: Если не удалось извлечь записи из файла
        """
        self.check_data()
        yield from load_records(self._filepath)

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
        author: str | None,
        theme: str | None,
        year_from: int | None,
        year_to: int | None,
        min_len: int | None,
        max_len: int | None,
    ) -> Filters:
        """
        Получение списка фильтров

        Описание:
            Стихотворения без года не проходят фильтры по годам

        Аргументы:
            author (str): Автор (подстрока без учета регистра)
            theme (str): Тема (подстрока без учета регистра)
            year_from (int): Наименьший год написания
            year_to (int): Наибольший год написания
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)

        Вывод:
            filters (Filters): Список фильтров-предикатов

        Исключения:
            ValueError: Если наименьший год больше наибольшего
            ValueError: Если минимальная длина текста не больше 0
            ValueError: Если максимальная длина текста не больше 0
            ValueError: Если минимальная длина текста больше максимальной
        """
        filters: Filters = []
        if author:
            pattern = re.compile(re.escape(author), re.IGNORECASE)
            filters.append(lambda record: pattern.search(record["author"]) is not None)
        if theme:
            pattern_theme = re.compile(re.escape(theme), re.IGNORECASE)
            filters.append(
                lambda record: any(pattern_theme.search(item) for item in record["themes"])
            )
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


def load_records(filepath: str | Path) -> Generator[dict[str, Any], None, None]:
    """
    Потоковое чтение стихотворений из файла корпуса

    Описание:
        Файл - XML с элементами item внутри корневого items: author, name, themes
        (вложенные item), date_from, date_to, text; вложенные item тем отличаются
        от стихотворений по глубине

    Аргументы:
        filepath (str|Path): Путь к файлу корпуса

    Вывод:
        generator[dict[str, object]]: Генератор записей

    Исключения:
        ValueError: Если не удалось извлечь записи из файла
    """
    depth = 0
    try:
        for event, element in ET.iterparse(to_path(filepath), events=("start", "end")):
            if event == "start":
                depth += 1
                continue
            depth -= 1
            if element.tag == "item" and depth == 1:
                yield {
                    "author": (element.findtext("author") or "").strip(),
                    "title": (element.findtext("name") or "").strip(),
                    "themes": tuple(
                        (theme.text or "").strip() for theme in element.findall("themes/item")
                    ),
                    "year_from": _year(element.findtext("date_from")),
                    "year_to": _year(element.findtext("date_to")),
                    "text": (element.findtext("text") or "").strip(),
                }
                element.clear()
    except ET.ParseError as e:
        raise ValueError("Не удалось извлечь записи из файла") from e


def _year(value: str | None) -> int | None:
    value = (value or "").strip()
    return int(value) if value.isdigit() else None
