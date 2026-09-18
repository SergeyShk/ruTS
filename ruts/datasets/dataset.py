import re
from abc import ABCMeta, abstractmethod
from collections.abc import Callable, Generator
from typing import Any

from ..exceptions import ParameterError

Filter = Callable[[dict[str, Any]], bool]
Filters = list[Filter]


class Dataset(metaclass=ABCMeta):
    """
    Абстрактный класс для работы с набором данных

    Аргументы:
        name (str): Наименование набора данных
        meta (dict): Справочная информация о наборе данных

    Методы:
        check_data: Проверка наличия всех необходимых директорий и файлов в наборе данных
        get_texts: Получение текстов (без заголовков) из набора данных
        get_records: Получение записей (с заголовками) из набора данных
        download: Загрузка набора данных из сети
    """

    __test__ = False

    @abstractmethod
    def __init__(self, name, meta=None):
        self.name = name
        self.meta = meta or {}

    def __repr__(self):
        return f"Набор данных('{self.name}')"

    @property
    def info(self):
        info = {"Наименование": self.name}
        info.update(self.meta)
        return info

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError

    @abstractmethod
    def check_data(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_texts(self, *args: Any) -> Generator[str, None, None]:
        raise NotImplementedError

    @abstractmethod
    def get_records(self, *args: Any) -> Generator[dict[str, Any], None, None]:
        raise NotImplementedError

    @abstractmethod
    def download(self, force: bool = False) -> None:
        raise NotImplementedError


def check_limit(limit: int | None) -> None:
    """
    Проверка количества записей

    Аргументы:
        limit (int): Количество записей

    Исключения:
        ParameterError: Если количество записей отрицательное
    """
    if limit is not None and limit < 0:
        raise ParameterError(f"Количество записей не должно быть отрицательным - {limit}")


def substring_filter(field: str, value: str) -> Filter:
    """
    Фильтр записей по подстроке поля без учета регистра

    Аргументы:
        field (str): Наименование поля записи
        value (str): Искомая подстрока

    Вывод:
        Filter: Фильтр-предикат
    """
    pattern = re.compile(re.escape(value), re.IGNORECASE)
    return lambda record: pattern.search(record[field]) is not None


def length_filters(min_len: int | None, max_len: int | None) -> Filters:
    """
    Фильтры записей по длине текста

    Аргументы:
        min_len (int): Минимальная длина текста (в символах)
        max_len (int): Максимальная длина текста (в символах)

    Вывод:
        Filters: Список фильтров-предикатов

    Исключения:
        ParameterError: Если минимальная длина текста не больше 0
        ParameterError: Если максимальная длина текста не больше 0
        ParameterError: Если минимальная длина текста больше максимальной
    """
    filters: Filters = []
    if min_len is not None:
        if min_len < 1:
            raise ParameterError("Минимальная длина текста должна быть больше 0")
        filters.append(lambda record: len(record["text"]) >= min_len)
    if max_len is not None:
        if max_len < 1:
            raise ParameterError("Максимальная длина текста должна быть больше 0")
        filters.append(lambda record: len(record["text"]) <= max_len)
    if min_len is not None and max_len is not None and min_len > max_len:
        raise ParameterError("Минимальная длина текста больше максимальной")
    return filters
