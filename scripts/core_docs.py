"""
Загрузка документации anyTS в docs/core

Английские страницы подключают именованные секции страниц anyTS, а тест документации
сверяет с ними русские переводы. Страницы берутся с тега версии anyTS из uv.lock, так что
сайт описывает то самое ядро, от которого зависит библиотека; версия записывается
в docs/core/VERSION, и страницы загружаются заново, только когда она меняется.
docs/core нет в git и на сайте.

Использование:
    uv run python scripts/core_docs.py [ANYTS_DIR]

С ANYTS_DIR страницы копируются из локального клона anyTS как есть, чтобы увидеть
в документации невыпущенные изменения ядра.
"""

import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "core"
REPOSITORY = "https://github.com/SergeyShk/anyTS"


def locked_version() -> str:
    """Версия anyTS в uv.lock"""
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    return next(package["version"] for package in lock["package"] if package["name"] == "anyts")


def copy_pages(source: Path, version: str) -> None:
    """Замена docs/core страницами клона anyTS"""
    shutil.rmtree(TARGET, ignore_errors=True)
    shutil.copytree(source / "docs", TARGET)
    (TARGET / "VERSION").write_text(version + "\n", encoding="utf-8")


def main() -> None:
    if len(sys.argv) > 1:
        copy_pages(Path(sys.argv[1]), "local")
        print(f"docs/core: anyTS из {sys.argv[1]}")
        return
    version = locked_version()
    marker = TARGET / "VERSION"
    if marker.is_file() and marker.read_text(encoding="utf-8").strip() == version:
        return
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as clone:
        clone_command = ["git", "-c", "advice.detachedHead=false", "clone", "--quiet"]
        subprocess.run(
            [*clone_command, "--depth", "1", "--branch", version, REPOSITORY, clone],
            check=True,
        )
        copy_pages(Path(clone), version)
    print(f"docs/core: anyTS {version}")


if __name__ == "__main__":
    main()
