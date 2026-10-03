import anyts.datasets
from anyts.datasets import Filter

from ..utils import normalize_yo


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
    return anyts.datasets.substring_filter(field, value, normalize_yo)
