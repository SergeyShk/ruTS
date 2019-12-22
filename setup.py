import os
from setuptools import setup, find_packages

version_file = os.path.join(os.path.dirname(__file__), 'ruts', 'VERSION')
with open(version_file, 'r') as f:
    VERSION = f.read().strip()

INSTALL_REQUIRES = [
    'nltk',
    'pymorphy2',
    'spacy>=2.0.12'
]

EXTRAS_REQUIRES = {
    'viz': ['matplotlib']
}

setup(
    name='ruts',
    version=VERSION,
    descripion='Russian Texts Statistics',
    author='Шкарин Сергей, Смирнова Екатерина',
    author_email='kouki.sergey@gmail.com, ekanerina@yandex.ru',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=INSTALL_REQUIRES,
    extras_requires=EXTRAS_REQUIRES
)