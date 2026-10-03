"""
У каждой русской страницы документации есть английская с теми же заголовками, якорями и ссылками

Английские страницы подключают секции страниц anyTS (--8<-- "page:section"), загруженных
в docs/core скриптом scripts/core_docs.py; русская страница несет перевод каждой под меткой
<!-- core: page:section digest -->, где digest - первые семь знаков SHA-1 секции, с которой
сделан перевод, так что изменившаяся секция роняет тест, пока перевод не обновлен
"""

import hashlib
import re
from pathlib import Path

import pytest

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
