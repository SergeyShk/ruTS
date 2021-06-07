import io
import os

from setuptools import find_packages, setup

version_file = os.path.join(os.path.dirname(__file__), "ruts", "VERSION")
with io.open(version_file, mode="r", encoding="utf-8") as f:
    VERSION = f.read().strip()

readme_file = os.path.join(os.path.dirname(__file__), "README.md")
with io.open(readme_file, mode="r", encoding="utf-8") as f:
    README = f.read()

INSTALL_REQUIRES = [
    "scipy>=1.6.0",
    "nltk",
    "pymorphy2",
    "razdel",
    "spacy>=3.0.0",
    "matplotlib>=3.3.0",
    "numpy>=1.20.0",
    "pandas",
    "graphviz",
]

setup(
    name="ruts",
    version=VERSION,
    description="Russian Texts Statistics",
    long_description=README,
    long_description_content_type="text/markdown",
    license="MIT License",
    keywords=[
        "NLP",
        "natural language processing",
        "CL",
        "computational linguistics",
        "text analytics",
        "russian",
    ],
    maintainer="Шкарин Сергей",
    maintainer_email="kouki.sergey@gmail.com",
    author="Шкарин Сергей, Смирнова Екатерина",
    author_email="kouki.sergey@gmail.com, ekanerina@yandex.ru",
    url="https://github.com/SergeyShk/ruTS",
    download_url="https://github.com/SergeyShk/ruTS/archive/0.7.0.tar.gz",
    packages=find_packages(exclude=("tests.*", "tests", "docs")),
    python_requires=">=3.7",
    classifiers=(
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Linguistic",
        "Natural Language :: Russian",
    ),
    package_data={"ruts": ["VERSION"]},
    install_requires=INSTALL_REQUIRES,
    test_suite="tests",
    project_urls={
        "Source Code": "https://github.com/SergeyShk/ruTS",
        "Issue Tracker": "https://github.com/SergeyShk/ruTS/issues",
        "spaCy uniVerse": "https://spacy.io/universe/project/ruts",
    },
)
