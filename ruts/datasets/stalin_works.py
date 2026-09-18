from collections.abc import Generator
from itertools import islice
from pathlib import Path
from typing import Any

from ..constants import DEFAULT_DATA_DIR
from ..exceptions import DataFileError, DatasetNotFoundError, ParameterError
from ..utils import to_path
from .dataset import Dataset, Filters, check_limit, fetch_archive, length_filters, substring_filter

NAME = "stalin_works"
META = {
    "url": "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/JMPSDM",
    "description": "Полное собрание сочинений И.В. Сталина",
    "author": "Шкарин С.С.",
}
DOWNLOAD_URL = (
    "https://github.com/SergeyShk/ruTS/raw/master/ruts/datasets/data/stalin_works.tar.xz"
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
        >>> from pprint import pprint
        >>> from ruts.datasets import StalinWorks
        >>> sw = StalinWorks()
        >>> pprint(sw.info)
        {'author': 'Шкарин С.С.',
         'description': 'Полное собрание сочинений И.В. Сталина',
         'url': 'https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/JMPSDM',
         'Наименование': 'stalin_works'}

    Итерация по набору данных:
        >>> for record in sw.get_records(year=1937, text_type='Письмо', limit=1):
        ...     pprint(record)
        {'file': ...Path('.../ruts_data/texts/stalin_works/volume_14/59'),
         'is_translation': False,
         'source': 'Книга "Иосиф Сталин в объятиях семьи"',
         'subject': 'Письмо матери 10 марта 1937 года',
         'text': 'Маме – моей привет!...',
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

    def __init__(self, data_dir: str | Path = DEFAULT_DATASET_DIR) -> None:
        super().__init__(NAME, meta=META)
        self.data_dir = to_path(data_dir).resolve()
        self.labels = tuple(f"volume_{i}" for i in range(1, 17))
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
                    ">>> sw = StalinWorks()\n"
                    ">>> sw.download()"
                )
                raise DatasetNotFoundError(msg)
        return True

    def download(self, force: bool = False) -> None:
        """
        Загрузка набора данных из сети и извлечение файлов

        Описание:
            Если архив уже есть, а какой-то из директорий томов нет, архив
            извлекается заново; архив, который не удалось извлечь, удаляется
            и загружается заново в том же вызове

        Аргументы:
            force (bool): Загрузить набор данных, даже если он уже загружен

        Исключения:
            DownloadError: Если не удалось загрузить архив
            DataFileError: Если загруженный архив не удалось извлечь
        """
        missing = any(not self.data_dir.joinpath(NAME, label).is_dir() for label in self.labels)
        fetch_archive(DOWNLOAD_URL, self._filepath, missing, force)
        self.check_data()

    def get_texts(
        self,
        volume: int | None = None,
        year: int | None = None,
        text_type: str | None = None,
        is_translation: bool | None = None,
        source: str | None = None,
        subject: str | None = None,
        topic: str | None = None,
        min_len: int | None = None,
        max_len: int | None = None,
        limit: int | None = None,
    ) -> Generator[str, None, None]:
        """
        Получение текстов (без заголовков) из набора данных

        Аргументы:
            volume (int): Номер тома
            year (int): Год издания книги
            text_type (str): Тип текстов
            is_translation (bool): Признак перевода
            source (str): Первоначальный источник текстов (подстрока без учета регистра)
            subject (str): Наименование текстов (подстрока без учета регистра)
            topic (str): Наименование подраздела текстов (подстрока без учета регистра)
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
        check_limit(limit)
        for record in islice(self.__filtered_iter(filters), limit):
            yield record["text"]

    def get_records(
        self,
        volume: int | None = None,
        year: int | None = None,
        text_type: str | None = None,
        is_translation: bool | None = None,
        source: str | None = None,
        subject: str | None = None,
        topic: str | None = None,
        min_len: int | None = None,
        max_len: int | None = None,
        limit: int | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        """
        Получение записей (с заголовками) из набора данных

        Аргументы:
            volume (int): Номер тома
            year (int): Год издания книги
            text_type (str): Тип текстов
            is_translation (bool): Признак перевода
            source (str): Первоначальный источник текстов (подстрока без учета регистра)
            subject (str): Наименование текстов (подстрока без учета регистра)
            topic (str): Наименование подраздела текстов (подстрока без учета регистра)
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
        except Exception as e:
            raise DataFileError("Не удалось извлечь записи из файла") from e

    @staticmethod
    def __get_filters(
        volume: int | None,
        year: int | None,
        text_type: str | None,
        is_translation: bool | None,
        source: str | None,
        subject: str | None,
        topic: str | None,
        min_len: int | None,
        max_len: int | None,
    ) -> Filters:
        """
        Получение списка фильтров

        Аргументы:
            volume (int): Номер тома
            year (int): Год издания книги
            text_type (str): Тип текстов
            is_translation (bool): Признак перевода
            source (str): Первоначальный источник текстов (подстрока без учета регистра)
            subject (str): Наименование текстов (подстрока без учета регистра)
            topic (str): Наименование подраздела текстов (подстрока без учета регистра)
            min_len (int): Минимальная длина текста (в символах)
            max_len (int): Максимальная длина текста (в символах)

        Вывод:
            filters (Filters): Список фильтров-предикатов

        Исключения:
            ParameterError: Если некорректно выбран номер тома
            ParameterError: Если некорректно выбран тип текста
            ParameterError: Если минимальная длина текста не больше 0
            ParameterError: Если максимальная длина текста не больше 0
            ParameterError: Если минимальная длина текста больше максимальной
        """
        filters: Filters = []
        if volume is not None:
            if volume not in range(1, 17):
                raise ParameterError(f"Некорректно выбран номер тома (1-16) - {volume}")
            filters.append(lambda record: record["volume"] == volume)
        if year is not None:
            filters.append(lambda record: record["year"] == year)
        if text_type is not None:
            if text_type not in TEXT_TYPES:
                raise ParameterError(f"Некорректно выбран тип текста - {text_type}")
            filters.append(lambda record: record["type"] == text_type)
        if is_translation is not None:
            filters.append(lambda record: record["is_translation"] == is_translation)
        if source is not None:
            filters.append(substring_filter("source", source))
        if subject is not None:
            filters.append(substring_filter("subject", subject))
        if topic is not None:
            filters.append(substring_filter("topic", topic))
        filters.extend(length_filters(min_len, max_len))
        return filters
