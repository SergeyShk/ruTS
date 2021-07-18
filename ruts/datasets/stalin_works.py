from typing import Any, Dict, Generator, List, Optional, Union

import io
import os
import re
from itertools import islice
from pathlib import Path

from ..constants import DEFAULT_DATA_DIR
from ..utils import download_file, extract_archive, to_path
from .dataset import Dataset

NAME = "stalin_works"
META = {
    "url": "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/JMPSDM",
    "description": "Полное собрание сочинений И.В. Сталина",
    "author": "Шкарин С.С.",
}
DOWNLOAD_URL = (
    "https://github.com/SergeyShk/ruTS/raw/poetry/ruts/datasets/data/stalin_works.tar.xz"
)
TEXT_TYPES = [
    "Протокол",
    "Прошение",
    "Стихотворение",
    "Телеграмма",
    "Доклад",
    "Приказ",
    "Статья",
    "Выступление",
    "Беседа",
    "Записка",
    "Отчет",
    "Письмо",
    "Брошюра",
    "Прокламация",
    "Постановление",
    "Резолюция",
    "Комментарий",
]
DEFAULT_DATASET_DIR = DEFAULT_DATA_DIR.joinpath("texts")


class StalinWorks(Dataset):
    """
    Класс для работы с набором данных полного собрания сочинений И.В. Сталина

    Описание:
        Для формирования набора данных используются 16 основных томов оцифрованного полного собрания сочинений И.В. Сталина:
            Том 1. Произведения 1901-1907
            Том 2. Произведения 1907-1913
            Том 3. Произведения 1917 (март-октябрь)
            Том 4. Произведения 1917-1920
            Том 5. Произведения 1921-1923
            Том 6. Произведения 1924
            Том 7. Произведения 1925
            Том 8. Произведения 1926
            Том 9. Произведения 1926-1927
            Том 10. Произведения 1927
            Том 11. Произведения 1928-1929
            Том 12. Произведения 1929-1930
            Том 13. Произведения 1930-1934
            Том 14. Произведения 1934-1940
            Том 15. Произведения 1941-1945
            Том 16. Произведения 1946-1952

    Ссылки:
        https://dataverse.harvard.edu/file.xhtml?fileId=4623793&version=DRAFT
        https://ruslit.traumlibrary.net/page/stalin.html

    Примеры использования:
    Информация о наборе данных:
        >>> from ruts.datasets import StalinWorks
        >>> sw = StalinWorks()
        >>> sw.info
        {'description': 'Полное собрание сочинений И.В. Сталина',
        'url': 'https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/JMPSDM',
        'Наименование': 'stalin_works'}

    Итерация по набору данных:
        >>> for i in sw.get_records(year=1937, text_type='Письмо', limit=1):
        >>>     print(i)
        {'file': PosixPath('../ruTS/ruts_data/texts/stalin_works/volume_14/59'),
        'is_translation': False,
        'source': 'Книга "Иосиф Сталин в объятиях семьи"',
        'subject': 'Письмо матери 10 марта 1937 года',
        'text': 'Маме – моей привет!\n'
                'Как живет, как чувствует себя мама – моя? Передают, что ты здорова и '
                'бодра. Правда это? Если это правда, то я бесконечно рад этому. Наш '
                'род, видимо, крепкий род.\n'
                'Я здоров.\n'
                'Мои дети тоже чувствуют себя хорошо.\n'
                'Желаю здоровья, живи долгие годы, мама – моя.\n'
                'Твой Coco.\n'
                '10.\xa0III.37\xa0г.',
        'topic': '',
        'type': 'Письмо',
        'volume': 14,
        'year': 1937}

    Аргументы:
        data_dir (str): Путь к директории с набором данных

    Атрибуты:
        labels (tuple[str]): Кортеж номеров томов

    Методы:
        check_data: Проверка наличия всех необходимых директорий и файлов в наборе данных
        download: Загрузка набора данных из сети
        get_texts: Получение текстов (без заголовков) из набора данных
        get_records: Получение записей (с заголовками) из набора данных
    """

    def __init__(self, data_dir: str = DEFAULT_DATASET_DIR):
        super().__init__(NAME, meta=META)
        self.data_dir = to_path(data_dir).resolve()
        self.labels = tuple(f"volume_{i}" for i in range(1, 17))
        self._filename = NAME + ".tar.xz"
        self._filepath = self.data_dir.joinpath(self._filename)

    @property
    def filepath(self) -> Optional[str]:
        """
        Путь к архиву набора данных.
        """
        if self._filepath.is_file():
            return str(self._filepath)
        else:
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
                    ">>> sw = StalinWorks()\n"
                    ">>> sw.download()"
                )
                raise OSError(msg)
        return True

    def download(self, force: bool = False):
        """
        Загрузка набора данных из сети и извлечение файлов

        Аргументы:
            force (bool): Загрузить набор данных, даже если он уже загружен
        """
        filepath = download_file(
            url=DOWNLOAD_URL,
            filename="stalin_works.tar.xz",
            dirpath=self.data_dir,
            force=force,
        )
        if filepath:
            extract_archive(filepath)
        self.check_data()

    def get_texts(
        self,
        volume: int = None,
        year: int = None,
        text_type: str = None,
        is_translation: bool = None,
        source: str = None,
        subject: str = None,
        topic: str = None,
        min_len: int = None,
        max_len: int = None,
        limit: int = None,
    ) -> Generator[str, None, None]:
        """
        Получение текстов (без заголовков) из набора данных

        Аргументы:
            volume (int): Номер тома
            year (int): Год издания книги
            text_type (str): Тип текстов
            is_translation (bool): Признак перевода
            source (str): Первоначальный источник текстов
            subject (str): Наименование текстов
            topic (str): Наименование подраздела текстов
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)
            limit (int): Количество текстов

        Вывод:
            generator[str]: Генератор текстов
        """
        filters = self.__get_filters(
            volume,
            year,
            text_type,
            is_translation,
            source,
            subject,
            topic,
            min_len,
            max_len,
        )
        for record in islice(self.__filtered_iter(filters), limit):
            yield record["text"]

    def get_records(
        self,
        volume: int = None,
        year: int = None,
        text_type: str = None,
        is_translation: bool = None,
        source: str = None,
        subject: str = None,
        topic: str = None,
        min_len: int = None,
        max_len: int = None,
        limit: int = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Получение записей (с заголовками) из набора данных

        Аргументы:
            volume (int): Номер тома
            year (int): Год издания книги
            text_type (str): Тип текстов
            is_translation (bool): Признак перевода
            source (str): Первоначальный источник текстов
            subject (str): Наименование текстов
            topic (str): Наименование подраздела текстов
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)
            limit (int): Количество текстов

        Вывод:
            generator[dict[str, object]]: Генератор записей
        """
        filters = self.__get_filters(
            volume,
            year,
            text_type,
            is_translation,
            source,
            subject,
            topic,
            min_len,
            max_len,
        )
        for record in islice(self.__filtered_iter(filters), limit):
            yield record

    def __iter__(self) -> Generator[Dict[str, Any], None, None]:
        """
        Итерация по набору данных

        Вывод:
            generator[dict[str, object]]: Генератор записей
        """
        self.check_data()
        dirpaths = (self.data_dir.joinpath(NAME, label) for label in self.labels)
        for dirpath in dirpaths:
            for filepath in os.listdir(dirpath):
                if re.match(r"[0-9]+", filepath):
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
            with io.open(filepath, mode="r", encoding="utf-8") as f:
                headers, text = f.read().strip().split("\n\n")
                headers = tuple(header.split(":")[1][1:] for header in headers.split("\n"))
            return {
                "volume": int(headers[0]),
                "year": int(headers[1]),
                "type": headers[2],
                "is_translation": bool(int(headers[3])),
                "source": headers[4],
                "subject": headers[5],
                "topic": headers[6],
                "text": text,
                "file": filepath,
            }
        except Exception:
            raise ValueError("Не удалось извлечь записи из файла")

    @staticmethod
    def __get_filters(
        volume: int,
        year: int,
        text_type: str,
        is_translation: bool,
        source: str,
        subject: str,
        topic: str,
        min_len: int,
        max_len: int,
    ) -> List[str]:
        """
        Получение списка фильтров

        Аргументы:
            volume (int): Номер тома
            year (int): Год издания книги
            text_type (str): Тип текстов
            is_translation (bool): Признак перевода
            source (str): Первоначальный источник текстов
            subject (str): Наименование текстов
            topic (str): Наименование подраздела текстов
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)

        Вывод:
            filters (list[str]): Список фильтров

        Исключения:
            ValueError: Если некорректно выбран номер тома
            ValueError: Если некорректно выбран тип текста
            ValueError: Если минимальная длина текста не больше 0
            ValueError: Если максимальная длина текста не больше 0
            ValueError: Если минимальная длина текста больше максимальной
        """
        filters = []
        if volume:
            if volume not in range(1, 17):
                raise ValueError(f"Некорректно выбран номер тома (1-16) - {volume}")
            filters.append(lambda record: record.get("volume", "") == volume)
        if year:
            filters.append(lambda record: record.get("year", "") == year)
        if text_type:
            if text_type not in TEXT_TYPES:
                raise ValueError(f"Некорректно выбран тип текста - {text_type}")
            filters.append(lambda record: record.get("type", "") == text_type)
        if is_translation is not None:
            filters.append(lambda record: record.get("is_translation", "") == is_translation)
        if source:
            pattern = re.compile(f".*{source}.*", re.IGNORECASE)
            filters.append(lambda record: len(re.findall(pattern, record.get("source", ""))) > 0)
        if subject:
            pattern = re.compile(f".*{subject}.*", re.IGNORECASE)
            filters.append(lambda record: len(re.findall(pattern, record.get("subject", ""))) > 0)
        if topic:
            pattern = re.compile(f".*{topic}.*", re.IGNORECASE)
            filters.append(lambda record: len(re.findall(pattern, record.get("topic", ""))) > 0)
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
