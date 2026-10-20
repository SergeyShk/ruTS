"""
У каждой русской страницы документации есть английская с теми же заголовками, якорями и ссылками

Английские страницы подключают секции страниц anyTS (--8<-- "page:section"), загруженных
в docs/core скриптом scripts/core_docs.py; русская страница несет перевод каждой под меткой
<!-- core: page:section digest -->, где digest - первые семь знаков SHA-1 секции, с которой
сделан перевод, так что изменившаяся секция роняет тест, пока перевод не обновлен
"""

import hashlib
import importlib
import inspect
import pkgutil
import re
from pathlib import Path

import anyts.constants
import pytest

import ruts
import ruts.constants

DOCS = Path(__file__).parent.parent / "docs"
CORE = DOCS / "core"
PAGES = sorted(
    path
    for path in DOCS.rglob("*.md")
    if not path.name.endswith(".en.md") and not path.is_relative_to(CORE)
)
INCLUDE = re.compile(r'^--8<-- "(?P<ref>[\w/.-]+\.md:[\w-]+)"$', re.MULTILINE)
MARK = re.compile(
    r"^<!-- core: (?P<ref>[\w/.-]+\.md:[\w-]+) (?P<digest>[0-9a-f]{7}) -->$", re.MULTILINE
)
SECTION = re.compile(
    r"^<!-- --8<-- \[start:(?P<name>[\w-]+)\] -->\n(?P<body>.*?)^<!-- --8<-- \[end:(?P=name)\] -->$",
    re.MULTILINE | re.DOTALL,
)


def anchors(text: str) -> set[str]:
    return set(re.findall(r"\{ #([\w-]+) \}", text))


def links(text: str) -> set[str]:
    return set(re.findall(r"\]\(([^)#\s]+\.md)", text))


def core_section(ref: str) -> str:
    page, name = ref.split(":")
    assert (CORE / page).is_file(), (
        f"нет {CORE / page}: выполните uv run python scripts/core_docs.py"
    )
    sections = {
        match["name"]: match["body"]
        for match in SECTION.finditer((CORE / page).read_text(encoding="utf-8"))
    }
    assert name in sections, f"нет секции {name} на странице {page} anyTS"
    return sections[name]


def digest(ref: str) -> str:
    return hashlib.sha1(core_section(ref).encode()).hexdigest()[:7]


@pytest.mark.parametrize("page", PAGES, ids=[str(page.relative_to(DOCS)) for page in PAGES])
def test_english_page(page):
    english = page.with_name(page.name[:-3] + ".en.md")
    assert english.is_file(), f"нет английской версии {english.relative_to(DOCS)}"
    russian_text = page.read_text(encoding="utf-8")
    english_text = INCLUDE.sub(
        lambda match: core_section(match["ref"]), english.read_text(encoding="utf-8")
    )
    assert anchors(english_text) == anchors(russian_text)
    assert links(english_text) == links(russian_text)
    assert russian_text.count("\n## ") == english_text.count("\n## ")


@pytest.mark.parametrize("page", PAGES, ids=[str(page.relative_to(DOCS)) for page in PAGES])
def test_core_translations(page):
    english = page.with_name(page.name[:-3] + ".en.md")
    included = INCLUDE.findall(english.read_text(encoding="utf-8"))
    marks = [
        (match["ref"], match["digest"])
        for match in MARK.finditer(page.read_text(encoding="utf-8"))
    ]
    assert [ref for ref, _ in marks] == included, "русская страница переводит другие секции"
    for ref, translated in marks:
        assert translated == digest(ref), f"{ref}: перевод с {translated}, в ядре {digest(ref)}"


# Блок сигнатуры: ``` {.python .signature} с одним вызовом в одной строке
SIGNATURE = re.compile(r"^``` \{\.python \.signature\}\n(\w+)\((.*)\)\n```$", re.MULTILINE)
MODULES = [
    importlib.import_module(info.name)
    for info in pkgutil.walk_packages(ruts.__path__, "ruts.")
    if not info.name.endswith("__main__")
]
CONSTANTS = [ruts.constants, anyts.constants, *MODULES]
# Страницы, имя которых не совпадает с модулем
PAGE_MODULES = {
    "extractors": "ruts.extractors",
    "datasets/poetrycorpus": "ruts.datasets.poetry_corpus",
    "datasets/russianliterature": "ruts.datasets.russian_literature",
    "datasets/sovchlit": "ruts.datasets.sov_chrest_lit",
    "datasets/stalinworks": "ruts.datasets.stalin_works",
    "datasets/stressdict": "ruts.datasets.stress_dict",
    "datasets/textsbygrade": "ruts.datasets.texts_by_grade",
}


def default_text(value: object) -> str:
    """Значение по умолчанию так, как его пишет блок сигнатуры: литерал, имя или константа"""
    if value is None or isinstance(value, bool | int | float | str | tuple):
        return repr(value)
    if callable(value) and hasattr(value, "__qualname__"):
        return value.__qualname__
    for module in CONSTANTS:
        for name, constant in vars(module).items():
            if name.isupper() and constant is value:
                return name
    return repr(value)


def signature_text(target: object) -> str:
    """Параметры вызываемого объекта так, как их пишет блок сигнатуры"""
    parts = []
    keyword_only = False
    for param in inspect.signature(target).parameters.values():
        if param.kind is param.KEYWORD_ONLY and not keyword_only:
            parts.append("*")
            keyword_only = True
        if param.kind is param.VAR_POSITIONAL:
            parts.append(f"*{param.name}")
            keyword_only = True
        elif param.kind is param.VAR_KEYWORD:
            parts.append(f"**{param.name}")
        elif param.default is param.empty:
            parts.append(param.name)
        else:
            parts.append(f"{param.name}={default_text(param.default)}")
    return ", ".join(parts)


def page_target(page: Path, name: str) -> object:
    """Вызываемый объект страницы: из модуля страницы или единственный с этим именем в ruTS"""
    key = page.relative_to(DOCS).with_suffix("").as_posix().removesuffix(".en")
    module_name = PAGE_MODULES.get(key) or PAGE_MODULES.get(key.split("/")[0])
    if module_name is None:
        module_name = "ruts." + key.replace("/", ".")
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        module = None
    if module is not None and name in vars(module):
        return vars(module)[name]
    targets = {id(vars(m)[name]): vars(m)[name] for m in MODULES if name in vars(m)}
    return next(iter(targets.values())) if len(targets) == 1 else None


def test_signatures_match_the_code():
    found = 0
    for page in sorted(path for path in DOCS.rglob("*.md") if not path.is_relative_to(CORE)):
        text = INCLUDE.sub(
            lambda match: core_section(match["ref"]), page.read_text(encoding="utf-8")
        )
        for name, written in SIGNATURE.findall(text):
            target = page_target(page, name)
            where = page.relative_to(DOCS)
            assert target is not None, f"{where}: {name} нет в ruTS"
            assert written == signature_text(target), (
                f"{where}: {name}({written}) расходится с кодом"
            )
            found += 1
    assert found
