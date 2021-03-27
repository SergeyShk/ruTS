from spacy.language import Language
from spacy.tokens import Doc

from .basic_stats import BasicStats
from .diversity_stats import DiversityStats
from .morph_stats import MorphStats
from .readability_stats import ReadabilityStats


@Language.factory("basic")
class BasicStatsComponent(object):
    """
    Класс для компонента основных статистик текста

    Примеры использования:
    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe('basic', last=True)

    Доступ к извлеченным статистикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.basic.get_stats()
        >>> doc._.basic.c_letters
        {4: 3}

    Аргументы:
        name (str): Наименование компонента в пайплайне
    """

    def __init__(self, nlp: Language, name: str = "basic"):
        self.name = name
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Добавление извлеченных статистик в компонент

        Аргументы:
            doc (Doc): Объект Doc

        Вывод:
            doc (Doc): Модифицированный объект Doc
        """
        bs = BasicStats(doc)
        doc._.set(self.name, bs)
        return doc


@Language.factory("morph")
class MorphStatsComponent(object):
    """
    Класс для компонента морфологических статистик текста

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe('morph', last=True)

    Доступ к извлеченным статистикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.morph.get_stats()
        >>> doc._.morph.case
        ('nomn', 'gent', 'datv')

    Аргументы:
        name (str): Наименование компонента в пайплайне
    """

    def __init__(self, nlp: Language, name: str = "morph"):
        self.name = name
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Добавление извлеченных статистик в компонент

        Аргументы:
            doc (Doc): Объект Doc

        Вывод:
            doc (Doc): Модифицированный объект Doc
        """
        ms = MorphStats(doc)
        doc._.set(self.name, ms)
        return doc


@Language.factory("readability")
class ReadabilityStatsComponent(object):
    """
    Класс для компонента основных метрик удобочитаемости текста

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe('readability', last=True)

    Доступ к извлеченным метрикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.readability.get_stats()
        >>> doc._.readability.flesch_reading_easy
        82.735

    Аргументы:
        name (str): Наименование компонента в пайплайне
    """

    def __init__(self, nlp: Language, name: str = "readability"):
        self.name = name
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Добавление извлеченных метрик в компонент

        Аргументы:
            doc (Doc): Объект Doc

        Вывод:
            doc (Doc): Модифицированный объект Doc
        """
        rs = ReadabilityStats(doc)
        doc._.set(self.name, rs)
        return doc


@Language.factory("diversity")
class DiversityStatsComponent(object):
    """
    Класс для компонента основных метрик лексического разнообразия текста

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe('diversity', last=True)

    Доступ к извлеченным метрикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.diversity.get_stats()
        >>> doc._.diversity.rttr
        1.7320508075688774

    Аргументы:
        name (str): Наименование компонента в пайплайне
    """

    def __init__(self, nlp: Language, name: str = "diversity"):
        self.name = name
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Добавление извлеченных метрик в компонент

        Аргументы:
            doc (Doc): Объект Doc

        Вывод:
            doc (Doc): Модифицированный объект Doc
        """
        ds = DiversityStats(doc)
        doc._.set(self.name, ds)
        return doc
