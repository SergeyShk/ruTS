import bisect
from collections.abc import Generator
from functools import cache
from itertools import islice
from pathlib import Path
from typing import Any

import numpy as np

from ..constants import DEFAULT_DATA_DIR, RU_VOWELS
from ..exceptions import DatasetNotFoundError, DownloadError
from ..utils import download_file, extract_archive, normalize_yo, sha256, to_path
from .dataset import Dataset, check_limit

NAME = "stress_dict"
META = {
    "url": "https://github.com/Koziev/NLP_Datasets",
    "description": "Словарь ударений all_accents (Википедия, Викисловарь, грамматический словарь)",
    "author": "Козиев И.",
    "license": "CC0-1.0",
}
COMMIT = "95dcb28d77bae169faa3570697c67d0292c32a0d"
DOWNLOAD_URL = f"https://github.com/Koziev/NLP_Datasets/raw/{COMMIT}/Stress/all_accents.zip"
ARCHIVE = "all_accents.zip"
ARCHIVE_SHA256 = "83776e8c1dc1e1983a6b48987b7876ef6cc6f5d899bd303e21fa74f63e46cf9d"
FILENAME = "all_accents.tsv"
STRESS_MARK = "^"
CHUNK_SIZE = 1 << 24
DEFAULT_DATASET_DIR = DEFAULT_DATA_DIR.joinpath("dicts")
VOWELS = frozenset(letter.lower() for letter in RU_VOWELS)


class StressIndex:
    """
    Индекс файла словаря для двоичного поиска словоформ

    Описание:
        Файл хранится в памяти как есть, позиции начала строк и табуляций
        находятся векторно, ключ строки - байты до табуляции; строки в файле
        отсортированы по кодам символов, а порядок байтов UTF-8 совпадает с порядком
        кодов, поэтому двоичный поиск идет по байтам без декодирования

    Аргументы:
        data (bytes): Содержимое файла словаря
    """

    def __init__(self, data: bytes) -> None:
        ends = _positions(data, ord("\n"))
        if not len(ends) or ends[-1] != len(data) - 1:
            ends = np.append(ends, len(data))
        starts = np.empty_like(ends)
        starts[0] = 0
        starts[1:] = ends[:-1] + 1
        # Первая табуляция каждой строки, у строки без табуляции - ее конец
        tabs = _positions(data, ord("\t"))
        tabs = np.append(tabs, len(data))[np.searchsorted(tabs, starts)]
        self.data = data
        self.starts = starts
        self.tabs = np.minimum(tabs, ends)
        self.ends = ends

    def __len__(self) -> int:
        return len(self.starts)

    def _key(self, position: int) -> bytes:
        return self.data[self.starts[position] : self.tabs[position]]

    def find(self, word: str) -> str | None:
        """
        Поиск словоформы

        Аргументы:
            word (str): Словоформа в нижнем регистре без ё

        Вывод:
            str|None: Запись словаря с меткой ударения, None если словоформы нет
        """
        key = word.encode("utf-8")
        position = bisect.bisect_left(range(len(self)), key, key=self._key)
        if position < len(self) and self._key(position) == key:
            return self.data[self.tabs[position] + 1 : self.ends[position]].decode("utf-8")
        return None


class StressDict(Dataset):
    """
    Класс для работы со словарем ударений Ильи Козиева (all_accents)

    Описание:
        1 680 535 словоформ с позицией основного ударения: данные Википедии
        и Викисловаря, дополненные формами по таблицам словоизменения грамматического
        словаря автора в предположении, что ударение при склонении и спряжении
        не сдвигается. Поэтому у форм с подвижным ударением (реки́ - ре́ки, воды́ - во́ды)
        записан один из вариантов, омографы (за́мок - замо́к) даны одной строкой,
        а буква ё везде заменена на е. Словарь распространяется под лицензией CC0
        и загружается из репозитория автора (закрепленный коммит) с проверкой
        контрольной суммы SHA-256
        Файл словаря (77 МБ) читается один раз на процесс и индексируется целиком
        в памяти без разбора строк: поиск словоформы идет двоичным поиском
        по отсортированному файлу, поэтому загрузка занимает доли секунды,
        а словарь - около 100 МБ памяти
        Для расстановки ударений в тексте и стихе служит модуль verse_stats:
        он поправляет известные ошибки словаря, восстанавливает ударение по букве ё
        и подгоняет его под метр

    Ссылки:
        https://github.com/Koziev/NLP_Datasets#ударения

    Примеры использования:
    Загрузка и информация о словаре:
        >>> from ruts.datasets import StressDict
        >>> sd = StressDict()
        >>> sd.download()  # doctest: +SKIP
        >>> sd.info['license']
        'CC0-1.0'

    Поиск словоформы - номер ударного слога, считая с нуля:
        >>> sd.lookup('корова'), sd.lookup('ёжик'), sd.lookup('котоведение')
        (1, 0, None)
        >>> 'корова' in sd
        True

    Итерация по словарю:
        >>> for record in sd.get_records(limit=2):
        ...     print(record)
        {'word': '-де', 'stress': 0}
        {'word': '-ка', 'stress': 0}

    Аргументы:
        data_dir (str): Путь к директории со словарем

    Методы:
        check_data: Проверка наличия файла словаря
        download: Загрузка словаря из сети
        lookup: Получение номера ударного слога словоформы
        get_texts: Получение словоформ словаря
        get_records: Получение записей словаря
    """

    def __init__(self, data_dir: str | Path = DEFAULT_DATASET_DIR) -> None:
        super().__init__(NAME, meta=META)
        self.data_dir = to_path(data_dir).resolve()
        self._filepath = self.data_dir.joinpath(FILENAME)
        self._checked = False

    @property
    def filepath(self) -> str | None:
        """
        Путь к файлу словаря
        """
        if self._filepath.is_file():
            return str(self._filepath)
        return None

    def check_data(self) -> bool:
        """
        Проверка наличия файла словаря

        Вывод:
            bool: Результат проверки

        Исключения:
            DatasetNotFoundError: Если словарь не обнаружен
        """
        if not self._filepath.is_file():
            msg = (
                f"Словарь {NAME} не обнаружен\n"
                "Загрузите его, выполнив команды:\n"
                ">>> sd = StressDict()\n"
                ">>> sd.download()"
            )
            raise DatasetNotFoundError(msg)
        return True

    def download(self, force: bool = False) -> None:
        """
        Загрузка словаря из сети и извлечение файла

        Описание:
            Загруженный архив сверяется с контрольной суммой SHA-256; поврежденный
            или подмененный файл удаляется, чтобы повторная загрузка не пропускалась
            Если архив уже есть, а файл словаря нет, архив извлекается заново

        Аргументы:
            force (bool): Загрузить словарь, даже если он уже загружен

        Исключения:
            DownloadError: Если не удалось загрузить файл или он не прошел проверку
        """
        archive = self.data_dir.joinpath(ARCHIVE)
        filepath = download_file(
            url=DOWNLOAD_URL,
            filename=ARCHIVE,
            dirpath=self.data_dir,
            force=force,
        )
        if filepath or not self._filepath.is_file():
            if sha256(archive) != ARCHIVE_SHA256:
                archive.unlink(missing_ok=True)
                raise DownloadError(
                    f"Файл {archive} не прошел проверку контрольной суммы и удален, "
                    "повторите загрузку"
                )
            extract_archive(archive, self.data_dir)
        self.check_data()
        load_index.cache_clear()

    def __iter__(self) -> Generator[dict[str, Any], None, None]:
        """
        Итерация по словарю

        Вывод:
            generator[dict[str, object]]: Генератор записей словаря - словоформа
                и номер ударного слога (None у 507 форм без ударения)
        """
        self.check_data()
        with self._filepath.open(encoding="utf-8") as file:
            for line in file:
                word, _, accented = line.rstrip("\n").partition("\t")
                yield {"word": word, "stress": stress_from_accented(accented)}

    def get_records(self, limit: int | None = None) -> Generator[dict[str, Any], None, None]:
        """
        Получение записей словаря

        Аргументы:
            limit (int): Количество записей

        Вывод:
            generator[dict[str, object]]: Генератор записей словаря

        Исключения:
            ParameterError: Если количество записей отрицательное
        """
        check_limit(limit)
        yield from islice(self, limit)

    def get_texts(self, limit: int | None = None) -> Generator[str, None, None]:
        """
        Получение словоформ словаря

        Аргументы:
            limit (int): Количество словоформ

        Вывод:
            generator[str]: Генератор словоформ
        """
        for record in self.get_records(limit):
            yield record["word"]

    def lookup(self, word: str) -> int | None:
        """
        Получение номера ударного слога словоформы

        Описание:
            Словоформа приводится к нижнему регистру, ё заменяется на е, как в словаре;
            слоги считаются по гласным с нуля

        Аргументы:
            word (str): Словоформа

        Вывод:
            int|None: Номер ударного слога, None если словоформы в словаре нет
                или ударение у нее не указано
        """
        accented = self._index.find(normalize_yo(word))
        if accented is None:
            return None
        return stress_from_accented(accented)

    @property
    def _index(self) -> StressIndex:
        """Индекс файла словаря с однократной проверкой наличия файла"""
        if not self._checked:
            self.check_data()
            self._checked = True
        return load_index(self._filepath)

    def __len__(self) -> int:
        return len(self._index)

    def __contains__(self, word: object) -> bool:
        return isinstance(word, str) and self._index.find(normalize_yo(word)) is not None


def stress_from_accented(accented: str) -> int | None:
    """
    Номер ударного слога по записи словаря с меткой ударения

    Аргументы:
        accented (str): Словоформа с меткой ^ перед ударной гласной (кор^ова)

    Вывод:
        int|None: Номер ударного слога с нуля, None если метки нет
    """
    position = accented.find(STRESS_MARK)
    if position < 0:
        return None
    return sum(letter in VOWELS for letter in accented[:position])


def _positions(data: bytes, byte: int) -> np.ndarray:
    """
    Позиции байта в данных

    Описание:
        Маска сравнения строится кусками по CHUNK_SIZE байт, чтобы не удваивать
        память под файл словаря целиком
    """
    positions = []
    for offset in range(0, len(data), CHUNK_SIZE):
        chunk = np.frombuffer(
            data, dtype=np.uint8, count=min(CHUNK_SIZE, len(data) - offset), offset=offset
        )
        positions.append(np.flatnonzero(chunk == byte).astype(np.int32) + offset)
    return np.concatenate(positions) if positions else np.zeros(0, dtype=np.int32)


@cache
def load_index(filepath: Path) -> StressIndex:
    """
    Чтение файла словаря в индекс

    Описание:
        Результат кэшируется по пути к файлу, поэтому все экземпляры StressDict
        с одной директорией используют один индекс; кэш сбрасывается при повторной
        загрузке

    Аргументы:
        filepath (Path): Путь к файлу словаря

    Вывод:
        StressIndex: Индекс словаря
    """
    return StressIndex(filepath.read_bytes())
