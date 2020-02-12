import io
import os
from setuptools import setup, find_packages

version_file = os.path.join(os.path.dirname(__file__), 'ruts', 'VERSION')
with io.open(version_file, mode='r', encoding='utf-8') as f:
    VERSION = f.read().strip()

readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
with io.open(readme_file, mode='r', encoding='utf-8') as f:
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
        'text analytics',
        'russian'
    ],
    maintainer='Шкарин Сергей',
    maintainer_email='kouki.sergey@gmail.com',
    author='Шкарин Сергей, Смирнова Екатерина',
    author_email='kouki.sergey@gmail.com, ekanerina@yandex.ru',
    url='https://github.com/SergeyShk/ruTS',
    download_url='https://github.com/SergeyShk/ruTS/archive/0.1.0.tar.gz',
    packages=find_packages(exclude=('tests.*', 'tests')),
    python_requires='>=3.6',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Linguistic',
        'Natural Language :: Russian',
    ),
    package_data={'ruts': ['VERSION']},
    install_requires=INSTALL_REQUIRES,
    extras_requires=EXTRAS_REQUIRES
)
