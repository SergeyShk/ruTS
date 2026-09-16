import csv
import hashlib
from collections.abc import Generator
from functools import cache
from itertools import islice
from pathlib import Path
from typing import Any, NamedTuple

from ..constants import DEFAULT_DATA_DIR
from ..utils import download_file, extract_archive, normalize_yo, to_path
from .dataset import Dataset

NAME = "freq2011"
META = {
    "url": "http://dict.ruslang.ru/freq.php",
    "description": "Частотный словарь современного русского языка (на материалах НКРЯ)",
    "author": "Ляшевская О. Н., Шаров С. А.",
    "license": "Лицензия не указана, при использовании просьба ссылаться на первоисточник",
    "citation": (
        "Ляшевская О. Н., Шаров С. А. Частотный словарь современного русского языка "
        "(на материалах Национального корпуса русского языка). М.: Азбуковник, 2009."
    ),
}
DOWNLOAD_URL = "http://dict.ruslang.ru/Freq2011.zip"
ARCHIVE = "Freq2011.zip"
ARCHIVE_SHA256 = "1ae2950966c34c52355e4d5cb91f1cc715f1d50774af71cdf4319223130c7c6e"
FILENAME = "freqrnc2011.csv"
FILENAME_SHA256 = "a3742a5656a54e4ae164e8030769c4242e2ad8f5d73660d8614153e2f3c44f94"
CORPUS_SIZE = 92_000_000
DEFAULT_DATASET_DIR = DEFAULT_DATA_DIR.joinpath("dicts")


class Entry(NamedTuple):
    """
    Статья частотного словаря

    Атрибуты:
        lemma (str): Лемма
        pos (tuple[str, ...]): Части речи леммы в разметке MyStem (s, v, a, adv, s.PROP)
        ipm (float): Частота на миллион словоупотреблений, сумма по частям речи
        range (int): Число сегментов корпуса из 100, в которых встретилась лемма
        dispersion (int): Коэффициент Жуйана D
        docs (int): Число текстов, в которых встретилась лемма
    """

    lemma: str
    pos: tuple[str, ...]
    ipm: float
    range: int
    dispersion: int
    docs: int


class FreqDict(Dataset):
    """
    Класс для работы с частотным словарем Ляшевской и Шарова (Freq2011)

    Описание:
        52 138 лемм современного подкорпуса НКРЯ (1950-2007, 92 млн словоупотреблений)
        с частотой ipm, диапазоном R (число сегментов корпуса из 100), коэффициентом
        Жуйана D, числом текстов и частью речи в разметке MyStem; имена собственные
        помечены s.PROP. Словарь загружается с сайта dict.ruslang.ru (только HTTP),
        лицензия не указана, авторы просят ссылаться на первоисточник
        Для поиска леммы с несколькими частями речи (а - союз, частица, междометие)
        склеиваются: ipm суммируется, R, D и число текстов берутся максимальные;
        лемма приводится к нижнему регистру, ё заменяется на е, как в словаре
        Разобранный словарь кэшируется по пути к файлу и читается один раз на процесс;
        загруженный архив сверяется с контрольной суммой SHA-256 - файл на сайте
        не менялся с 2013 года

    Ссылки:
        http://dict.ruslang.ru/freq.php
        http://dict.ruslang.ru/freq.pdf

    Примеры использования:
    Загрузка и информация о словаре:
        >>> from ruts.datasets import FreqDict
        >>> fd = FreqDict()
        >>> fd.download()
        >>> fd.info['citation']
        'Ляшевская О. Н., Шаров С. А. Частотный словарь современного русского языка (на материалах Национального корпуса русского языка). М.: Азбуковник, 2009.'

    Поиск леммы:
        >>> fd.lookup('кот')
        Entry(lemma='кот', pos=('s',), ipm=40.3, range=98, dispersion=90, docs=947)
        >>> fd.ipm('котёнок'), fd.ipm('котоведение')
        (14.5, 0.0)

    Итерация по словарю:
        >>> for record in fd.get_records(pos='s', min_ipm=2700, limit=2):
        >>>     print(record)
        {'lemma': 'год', 'pos': 's', 'ipm': 3727.5, 'range': 100, 'dispersion': 94, 'docs': 29477}
        {'lemma': 'человек', 'pos': 's', 'ipm': 2723.0, 'range': 100, 'dispersion': 97, 'docs': 20423}

    Аргументы:
        data_dir (str): Путь к директории со словарем

    Атрибуты:
        entries (dict[str, Entry]): Справочник статей по нормализованной лемме
        min_ipm (float): Минимальная частота в словаре

    Методы:
        check_data: Проверка наличия файла словаря
        download: Загрузка словаря из сети
        lookup: Получение статьи по лемме
        ipm: Получение частоты леммы
        get_texts: Получение лемм словаря
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
            OSError: Если словарь не обнаружен
        """
        if not self._filepath.is_file():
            msg = (
                f"Словарь {NAME} не обнаружен\n"
                "Загрузите его, выполнив команды:\n"
                ">>> fd = FreqDict()\n"
                ">>> fd.download()"
            )
            raise OSError(msg)
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
            RuntimeError: Если не удалось загрузить файл или он не прошел проверку
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
                raise RuntimeError(
                    f"Файл {archive} не прошел проверку контрольной суммы и удален, "
                    "повторите загрузку"
                )
            extract_archive(archive, self.data_dir)
        self.check_data()
        load_entries.cache_clear()
        load_min_ipm.cache_clear()

    def __iter__(self) -> Generator[dict[str, Any], None, None]:
        """
        Итерация по словарю

        Вывод:
            generator[dict[str, object]]: Генератор записей словаря
        """
        self.check_data()
        with self._filepath.open(encoding="utf-8", newline="") as file:
            reader = csv.reader(file, delimiter="\t")
            next(reader)
            for lemma, pos, ipm, range_, dispersion, docs in reader:
                yield {
                    "lemma": lemma,
                    "pos": pos,
                    "ipm": float(ipm),
                    "range": int(range_),
                    "dispersion": int(dispersion),
                    "docs": int(docs),
                }

    def get_records(
        self,
        pos: str | None = None,
        min_ipm: float | None = None,
        limit: int | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        """
        Получение записей словаря

        Аргументы:
            pos (str): Часть речи в разметке MyStem (s, v, a, adv, s.PROP)
            min_ipm (float): Минимальная частота
            limit (int): Количество записей

        Вывод:
            generator[dict[str, object]]: Генератор записей словаря
        """
        records = (
            record
            for record in self
            if (pos is None or record["pos"] == pos)
            and (min_ipm is None or record["ipm"] >= min_ipm)
        )
        yield from islice(records, limit)

    def get_texts(
        self,
        pos: str | None = None,
        min_ipm: float | None = None,
        limit: int | None = None,
    ) -> Generator[str, None, None]:
        """
        Получение лемм словаря

        Аргументы:
            pos (str): Часть речи в разметке MyStem (s, v, a, adv, s.PROP)
            min_ipm (float): Минимальная частота
            limit (int): Количество лемм

        Вывод:
            generator[str]: Генератор лемм
        """
        for record in self.get_records(pos, min_ipm, limit):
            yield record["lemma"]

    @property
    def entries(self) -> dict[str, Entry]:
        """
        Справочник статей словаря по нормализованной лемме

        Вывод:
            dict[str, Entry]: Статьи, части речи одной леммы склеены
        """
        self._ensure_data()
        return load_entries(self._filepath)

    @property
    def min_ipm(self) -> float:
        """
        Минимальная частота в словаре
        """
        self._ensure_data()
        return load_min_ipm(self._filepath)

    def _ensure_data(self) -> None:
        """
        Однократная проверка наличия файла словаря перед чтением

        Описание:
            Результат первой успешной проверки запоминается, чтобы lookup и ipm
            не обращались к файловой системе на каждое слово
        """
        if not self._checked:
            self.check_data()
            self._checked = True

    def lookup(self, lemma: str) -> Entry | None:
        """
        Получение статьи словаря по лемме

        Аргументы:
            lemma (str): Лемма в любом регистре, с ё или без

        Вывод:
            Entry|None: Статья словаря, None если леммы в словаре нет
        """
        return self.entries.get(normalize_yo(lemma))

    def ipm(self, lemma: str) -> float:
        """
        Получение частоты леммы

        Аргументы:
            lemma (str): Лемма

        Вывод:
            float: Частота на миллион словоупотреблений, 0 если леммы в словаре нет
        """
        entry = self.lookup(lemma)
        return entry.ipm if entry else 0.0

    def __len__(self) -> int:
        return len(self.entries)

    def __contains__(self, lemma: object) -> bool:
        return isinstance(lemma, str) and normalize_yo(lemma) in self.entries


def sha256(path: Path) -> str:
    """
    Вычисление контрольной суммы SHA-256 файла

    Аргументы:
        path (Path): Путь к файлу

    Вывод:
        str: Контрольная сумма в шестнадцатеричном виде, пустая строка для отсутствующего файла
    """
    if not path.is_file():
        return ""
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


@cache
def load_entries(filepath: Path) -> dict[str, Entry]:
    """
    Разбор файла словаря в справочник статей по нормализованной лемме

    Описание:
        Результат кэшируется по пути к файлу, поэтому все экземпляры FreqDict
        с одной директорией используют один разобранный словарь; кэш сбрасывается
        при повторной загрузке

    Аргументы:
        filepath (Path): Путь к файлу словаря

    Вывод:
        dict[str, Entry]: Статьи, части речи одной леммы склеены
    """
    entries: dict[str, Entry] = {}
    with filepath.open(encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader)
        for lemma, pos, ipm, range_, dispersion, docs in reader:
            key = normalize_yo(lemma)
            entry = entries.get(key)
            if entry is None:
                entries[key] = Entry(
                    key, (pos,), float(ipm), int(range_), int(dispersion), int(docs)
                )
            else:
                entries[key] = Entry(
                    key,
                    (*entry.pos, pos),
                    round(entry.ipm + float(ipm), 2),
                    max(entry.range, int(range_)),
                    max(entry.dispersion, int(dispersion)),
                    max(entry.docs, int(docs)),
                )
    return entries


@cache
def load_min_ipm(filepath: Path) -> float:
    """
    Минимальная частота в файле словаря

    Описание:
        Считается один раз по разобранному словарю и кэшируется по пути к файлу,
        как load_entries; используется как частота слов вне словаря при расчете
        сюрпризала

    Аргументы:
        filepath (Path): Путь к файлу словаря

    Вывод:
        float: Минимальная частота
    """
    return min(entry.ipm for entry in load_entries(filepath).values())
