from typing import Any, Dict, Generator

from abc import ABCMeta, abstractmethod


class Dataset(object, metaclass=ABCMeta):
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
    def get_records(self, *args: Any) -> Generator[Dict[str, Any], None, None]:
        raise NotImplementedError

    @abstractmethod
    def download(self, force: bool = False):
        raise NotImplementedError
