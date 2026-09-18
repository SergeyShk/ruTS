import re
from collections.abc import Callable, Generator
from itertools import islice
from pathlib import Path
from typing import Any

from ..constants import DEFAULT_DATA_DIR
from ..exceptions import DataFileError, DatasetNotFoundError, ParameterError
from ..utils import download_file, extract_archive, to_path
from .dataset import Dataset

# Фильтр - предикат над записью набора данных
Filters = list[Callable[[dict[str, Any]], bool]]

NAME = "texts_by_grade"
META = {
    "url": "https://github.com/infoculture/plainrussian",
    "description": "Тексты с метками класса проекта Plain Russian Language",
    "author": "Бегтин И.В.",
    "license": "CC0 1.0",
}
DOWNLOAD_URL = (
    "https://github.com/SergeyShk/ruTS/raw/master/ruts/datasets/data/texts_by_grade.tar.xz"
)
GRADES = (1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 17)
DEFAULT_DATASET_DIR = DEFAULT_DATA_DIR.joinpath("texts")


class TextsByGrade(Dataset):
    """
    Класс для работы с набором данных текстов с метками класса проекта Plain Russian Language

    Описание:
        68 текстов из репозитория проекта: 55 из списка TEXT_LIST, на которых Иван Бегтин
        подбирал коэффициенты формул удобочитаемости для русского языка, и 13 из папок
        репозитория, не вошедших в список. Сказки и детская литература (1 класс), школьная
        программа по литературе (3-11 классы), статья Википедии (12 класс), газетная статья
        (15 класс), нормативные и деловые документы (17 класс)
        Метка - класс школы или год обучения: 12-14 соответствуют 1-3 курсам вуза,
        15-17 - 4-6 курсам
        Тексты распространяются под лицензией CC0 1.0 и используются для проверки
        формул удобочитаемости

    Ссылки:
        https://github.com/infoculture/plainrussian
        https://github.com/infoculture/plainrussian/tree/master/api/textmetric/textsbygrade

    Примеры использования:
    Информация о наборе данных:
        >>> from pprint import pprint
        >>> from ruts.datasets import TextsByGrade
        >>> tbg = TextsByGrade()
        >>> pprint(tbg.info)
        {'author': 'Бегтин И.В.',
         'description': 'Тексты с метками класса проекта Plain Russian Language',
         'license': 'CC0 1.0',
         'url': 'https://github.com/infoculture/plainrussian',
         'Наименование': 'texts_by_grade'}

    Итерация по набору данных:
        >>> for record in tbg.get_records(grade=1, subject='Ряба'):
        ...     pprint(record)
        {'file': PosixPath('.../ruts_data/texts/texts_by_grade/grade_1/9'),
         'grade': 1,
         'source': 'http://skazki.org.ru/tales/yaichko/',
         'subject': 'Курочка Ряба',
         'text': 'Жил себе дед да баба, у них была курочка Ряба...'}

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
                    ">>> tbg = TextsByGrade()\n"
                    ">>> tbg.download()"
                )
                raise DatasetNotFoundError(msg)
        return True

    def download(self, force: bool = False) -> None:
        """
        Загрузка набора данных из сети и извлечение файлов

        Аргументы:
            force (bool): Загрузить набор данных, даже если он уже загружен
        """
        filepath = download_file(
            url=DOWNLOAD_URL,
            filename=self._filename,
            dirpath=self.data_dir,
            force=force,
        )
        if filepath:
            extract_archive(filepath)
        self.check_data()

    def get_texts(
        self,
        grade: int | None = None,
        subject: str | None = None,
        min_len: int | None = None,
        max_len: int | None = None,
        limit: int | None = None,
    ) -> Generator[str, None, None]:
        """
        Получение текстов (без заголовков) из набора данных

        Аргументы:
            grade (int): Уровень сложности текстов
            subject (str): Наименование текстов
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)
            limit (int): Количество текстов

        Вывод:
            generator[str]: Генератор текстов
        """
        filters = self.__get_filters(grade, subject, min_len, max_len)
        for record in islice(self.__filtered_iter(filters), limit):
            yield record["text"]

    def get_records(
        self,
        grade: int | None = None,
        subject: str | None = None,
        min_len: int | None = None,
        max_len: int | None = None,
        limit: int | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        """
        Получение записей (с заголовками) из набора данных

        Аргументы:
            grade (int): Уровень сложности текстов
            subject (str): Наименование текстов
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)
            limit (int): Количество текстов

        Вывод:
            generator[dict[str, object]]: Генератор записей
        """
        filters = self.__get_filters(grade, subject, min_len, max_len)
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
            filepaths = (path for path in dirpath.iterdir() if re.fullmatch(r"[0-9]+", path.name))
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
        for record in self:
            if all(filter_(record) for filter_ in filters):
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
                header_block, text = f.read().strip().split("\n\n", 1)
                headers = tuple(header.split(": ", 1)[1] for header in header_block.split("\n"))
            return {
                "grade": int(headers[0]),
                "subject": headers[1],
                "source": headers[2],
                "text": text,
                "file": filepath,
            }
        except Exception as e:
            raise DataFileError("Не удалось извлечь записи из файла") from e

    @staticmethod
    def __get_filters(
        grade: int | None,
        subject: str | None,
        min_len: int | None,
        max_len: int | None,
    ) -> Filters:
        """
        Получение списка фильтров

        Аргументы:
            grade (int): Уровень сложности текстов
            subject (str): Наименование текстов
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)

        Вывод:
            filters (Filters): Список фильтров-предикатов

        Исключения:
            ParameterError: Если некорректно выбран уровень текста
            ParameterError: Если минимальная длина текста не больше 0
            ParameterError: Если максимальная длина текста не больше 0
            ParameterError: Если минимальная длина текста больше максимальной
        """
        filters: Filters = []
        if grade:
            if grade not in GRADES:
                raise ParameterError(f"Некорректно выбран уровень текста {GRADES} - {grade}")
            filters.append(lambda record: record.get("grade", "") == grade)
        if subject:
            pattern = re.compile(f".*{subject}.*", re.IGNORECASE)
            filters.append(lambda record: len(re.findall(pattern, record.get("subject", ""))) > 0)
        if min_len:
            if min_len < 1:
                raise ParameterError("Минимальная длина текста должна быть больше 0")
            filters.append(lambda record: len(record.get("text", "")) >= min_len)
        if max_len:
            if max_len < 1:
                raise ParameterError("Максимальная длина текста должна быть больше 0")
            filters.append(lambda record: len(record.get("text", "")) <= max_len)
        if min_len and max_len and min_len > max_len:
            raise ParameterError("Минимальная длина текста больше максимальной")
        return filters
