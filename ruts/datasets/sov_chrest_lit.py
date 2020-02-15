
import io
import os
import re
from ..constants import DEFAULT_DATA_DIR
from ..utils import to_path, download_file, extract_archive
from .dataset import Dataset
from itertools import islice
from pathlib import Path
from typing import Any, Dict, Generator, Union

NAME = "sov_chrest_lit"
META = {
    'url': 'https://dataverse.harvard.edu/file.xhtml?fileId=3670902&version=DRAFT',
    'description': 'Корпус советских хрестоматий по литературе'
}
DOWNLOAD_URL = "https://dataverse.harvard.edu/api/access/datafile/:persistentId?persistentId=doi:10.7910/DVN/HK5RYS/EPJUN0"
TEXT_TYPES = ['Рассказ', 'Стихотворение', 'Сказка', 'Пословица', 'Загадка', 'Песня', 'Басня']

class SovChLit(Dataset):
    def __init__(self, data_dir=DEFAULT_DATA_DIR.joinpath("texts")):
        super().__init__(NAME, meta=META)
        self.data_dir = to_path(data_dir).resolve()
        self.labels = ("grade_1",)
        self.subset = None

    def download(self, force: bool = False):
        """
        Загрузка набора данных из сети и извлечение файлов

        Аргументы:
            force (bool): Загрузить набор данных, даже если он уже загружен
        """
        filepath = download_file(
            url=DOWNLOAD_URL,
            filename='sov_chrest_lit.tar.xz',
            dirpath=self.data_dir,
            force=force
        )
        if filepath:
            extract_archive(filepath)
        self.__check_data()

    def get_texts(
        self,
        grade: int = None,
        book: str = None,
        year: str = None,
        category: str = None,
        text_type: str = None,
        subject: str = None,
        author: str = None,
        min_len: int = None,
        max_len: int = None,
        limit: int = None
    ):
        filters = self.__get_filters(grade, book, year, category, text_type, subject, author, min_len, max_len)
        for record in islice(self.__filtered_iter(filters), limit):
            yield record['text']

    def get_records(
        self,
        grade: int = None,
        book: str = None,
        year: str = None,
        category: str = None,
        text_type: str = None,
        subject: str = None,
        author: str = None,
        min_len: int = None,
        max_len: int = None,
        limit: int = None
    ):
        filters = self.__get_filters(grade, book, year, category, text_type, subject, author, min_len, max_len)
        for record in islice(self.__filtered_iter(filters), limit):
            yield record

    def __iter__(self) -> Generator[Dict[str, Any], None, None]:
        """
        Итерация по набору данных

        Вывод:
            generator[dict[str, object]]: Генератор записей
        """
        self.__check_data()
        dirpaths = (
            self.data_dir.joinpath(NAME, label)
            for label in self.labels
        )
        for dirpath in dirpaths:
            for filepath in os.listdir(dirpath):
                if re.match(r'[0-9]+', filepath):
                    yield self.__load_record(dirpath.joinpath(filepath))

    def __filtered_iter(self, filters) -> Generator[Dict[str, Any], None, None]:
        """
        Итерация по набору данных с учетом фильтров

        Аргументы:
            filters (list[str]): Список фильтров

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
    def __load_record(filepath: Union[str, Path]) -> Dict[str, Any]:
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
            with io.open(filepath, mode='r', encoding='utf-8') as f:
                headers, text = f.read().strip().split('\n\n')
                headers = tuple(header.split(':')[1][1:] for header in headers.split('\n'))
            return {
                'grade': int(headers[0]),
                'book': headers[1],
                'year': int(headers[2]),
                'category': headers[3],
                'type': headers[4],
                'subject': headers[5],
                'author': headers[6],
                'text': text,
                'file': filepath
            }
        except:
            raise ValueError("Не удалось извлечь записи из файла")

    def __check_data(self) -> bool:
        """
        Проверка наличия всех необходимых директорий и файлов в наборе данных

        Вывод:
            bool: Результат проверки

        Исключения:
            OSError: Если набор данных не обнаружен
        """
        dirpaths = (
            self.data_dir.joinpath(NAME, label)
            for label in self.labels
        )
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

    @staticmethod
    def __get_filters(
        grade: int,
        book: str,
        year: str,
        category: str,
        text_type: str,
        subject: str,
        author: str,
        min_len: int,
        max_len: int
    ):
        filters = []
        if grade:
            if grade not in range(1, 12):
                raise ValueError(f"Некорректно выбран уровень текста (1-11) - {grade}")
            filters.append(
                lambda record: record.get('grade', '') == grade
            )
        if book:
            pattern = re.compile(f".*{book}.*")
            filters.append(
                lambda record: len(re.findall(pattern, record.get('book', ''))) > 0
            )
        if text_type:
            if text_type not in TEXT_TYPES:
                raise ValueError(f"Некорректно выбран тип текста - {text_type}")
            filters.append(
                lambda record: record.get('type', '') == text_type
            )
        if min_len:
            if min_len < 1:
                raise ValueError(f"Минимальный размер текста должен быть больше 0")
            filters.append(
                lambda record: len(record.get('text', '')) >= min_len
            )
        if max_len:
            if max_len < 1:
                raise ValueError(f"Максимальный размер текста должен быть больше 0")
            filters.append(
                lambda record: len(record.get('text', '')) <= max_len
            )
        if min_len and max_len and min_len > max_len:
            raise ValueError("Минимальная длина текста больше максимальной")
        return filters


if __name__ == "__main__":
    sc = SovChLit()
    print(sc.info)
    for i in sc.get_records(min_len=1000, limit=2):
        print(i)