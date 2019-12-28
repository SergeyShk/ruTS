import os
from setuptools import setup, find_packages

version_file = os.path.join(os.path.dirname(__file__), 'ruts', 'VERSION')
with open(version_file, 'r') as f:
    VERSION = f.read().strip()

readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
with open(readme_file, 'r') as f:
    README = f.read()

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
    description='Russian Texts Statistics',
    long_description=README,
    long_description_content_type='text/markdown',
    license='MIT License',
    keywords=[
        'NLP', 
        'natural language processing',
        'CL',
        'computational linguistics',
        'text analytics'
    ],
    maintainer='Шкарин Сергей',
    maintainer_email='kouki.sergey@gmail.com',
    author='Шкарин Сергей, Смирнова Екатерина',
    author_email='kouki.sergey@gmail.com, ekanerina@yandex.ru',
    url='https://github.com/SergeyShk/ruTS',
    download_url='https://github.com/SergeyShk/ruTS/archive/0.1.0.tar.gz',
    packages=find_packages(exclude=('tests.*', 'tests')),
    python_requires='>=3.6',
    package_data={'ruts': ['VERSION']},
    install_requires=INSTALL_REQUIRES,
    extras_requires=EXTRAS_REQUIRES
)