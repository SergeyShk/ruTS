import os
import shutil
import tarfile
import urllib
import zipfile
from .constants import RU_VOWELS, DEFAULT_DATA_DIR
from pathlib import Path
from typing import Union

def count_syllables(word: str) -> int:
    """
    Вычисление количества слогов в слове

    Аргументы:
        word (str): Строка слова

    Вывод:
        int: Количество слогов
    """
    return sum((1 for char in word if char in RU_VOWELS))

def to_path(path: str) -> Path:
    """
    Перевод строкового представления пути в объект Path

    Аргументы:
        path (str): Cтроковое представление пути

    Вывод:
        Path: Объект Path

    Исключения:
        TypeError: Если передаваемое значение не является строкой или объектом Path
    """
    if isinstance(path, str):
        return Path(path)
    elif isinstance(path, Path):
        return path
    else:
        raise TypeError("Некорректно указан путь")

def download_file(
    url: str,
    filename: str = None,
    dirpath: Union[str, Path] = DEFAULT_DATA_DIR,
    force: bool = False
) -> str:
    """
    Загрузка файла из сети

    Аргументы:
        url (str): Адрес загружаемого файла
        filename (str): Название файла после загрузки
        dirpath (str|Path): Путь к директории для загруженного файла
        force (bool): Загрузить набор данных, даже если он уже загружен

    Вывод:
        str: Путь к загруженному файлу

    Исключения:
        RuntimeError: Если не удалось загрузить файл
    """
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    if not filename:
        filename = os.path.basename(urllib.parse.urlparse(urllib.parse.unquote_plus(url)).path)
    filepath = to_path(dirpath).resolve() / filename
    if filepath.is_file() and force is False:
        print(f"Файл {filepath} уже загружен")
        return None
    else:
        try:
            print(f"Загрузка файла {url}...")
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        except:
            raise RuntimeError("Не удалось загрузить файл")
        else:
            print(f"Файл успешно загружен: {filepath}")
    return str(filepath)

def extract_archive(
    archive_file: Union[str, Path],
    extract_dir: Union[str, Path] = None
) -> str:
    """
    Извлечение файлов из архива в формате ZIP или TAR

    Аргументы:
        archive_file (str|Path): Путь к файлу архива
        extract_dir (str|Path): Путь к директории для извлеченных файлов

    Вывод:
        str: Путь к директории с извлеченными файлами
    """
    archive_file = to_path(archive_file).resolve()
    if not extract_dir:
        extract_dir = str(archive_file.parent)
    archive_file = str(archive_file)
    os.makedirs(extract_dir, exist_ok=True)
    is_zip = zipfile.is_zipfile(archive_file)
    is_tar = tarfile.is_tarfile(archive_file)
    if not is_zip and not is_tar:
        print(f"Файл {archive_file} не является архивом в формате ZIP или TAR")
        return extract_dir
    else:
        print(f"Извлечение файлов из архива {archive_file}...")
        shutil.unpack_archive(archive_file, extract_dir=extract_dir, format=None)
        if is_zip:
            with zipfile.ZipFile(archive_file, mode='r') as f:
                members = f.namelist()
        else:
            with tarfile.open(archive_file, mode='r') as f:
                members = f.getnames()
        src_basename = os.path.commonpath(members)
        dest_basename = os.path.basename(archive_file)
        if src_basename:
            while True:
                tmp, _ = os.path.splitext(dest_basename)
                if tmp == dest_basename:
                    break
                else:
                    dest_basename = tmp
            if src_basename != dest_basename:
                return shutil.move(
                    os.path.join(extract_dir, src_basename),
                    os.path.join(extract_dir, dest_basename),
                )
            else:
                return os.path.join(extract_dir, src_basename)
        else:
            return extract_dir

if __name__ == "__main__":
    text = "самооборона"
    print(count_syllables(text))
    print(extract_archive('test.tar.xz'))