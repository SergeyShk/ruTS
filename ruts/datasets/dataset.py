from collections.abc import Callable, Mapping
from pathlib import Path

import anyts.datasets
from anyts.datasets import Filter

from ..constants import CORE_MESSAGES
from ..utils import normalize_yo, with_core_messages

check_limit = with_core_messages(anyts.datasets.check_limit)
download_file = with_core_messages(anyts.datasets.download_file)
extract_archive = with_core_messages(anyts.datasets.extract_archive)
fetch_archive = with_core_messages(anyts.datasets.fetch_archive)
length_filters = with_core_messages(anyts.datasets.length_filters)
to_path = with_core_messages(anyts.datasets.to_path)


class Dataset(anyts.datasets.Dataset):
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
    repr_name = "Набор данных"
    name_key = "Наименование"


def substring_filter(field: str, value: str) -> Filter:
    """
    Фильтр записей по подстроке поля без учета регистра и буквы ё

    Аргументы:
        field (str): Наименование поля записи
        value (str): Искомая подстрока

    Вывод:
        Filter: Фильтр-предикат

    Исключения:
        ParameterError: Если подстрока не строка
    """
    return anyts.datasets.substring_filter(field, value, normalize_yo, messages=CORE_MESSAGES)


def is_numbered(path: Path) -> bool:
    """
    Проверка, что файл - запись набора данных, названная номером

    Аргументы:
        path (Path): Путь к файлу

    Вывод:
        bool: Результат проверки
    """
    return path.name.isdigit()


def is_complete(
    dirpath: Path, counts: Mapping[str, int], is_record: Callable[[Path], bool] = is_numbered
) -> bool:
    """
    Проверка, что в каждой директории набора данных есть все файлы записей

    Аргументы:
        dirpath (Path): Директория набора данных
        counts (Mapping[str, int]): Число файлов записей по пути директории внутри набора
        is_record (Callable[[Path], bool]): Предикат файла записи, по умолчанию is_numbered

    Вывод:
        bool: Результат проверки
    """
    for name, count in counts.items():
        path = dirpath.joinpath(name)
        if not path.is_dir() or sum(map(is_record, path.iterdir())) < count:
            return False
    return True
