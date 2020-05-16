from .basic_stats import BasicStats
from .diversity_stats import DiversityStats
from .morph_stats import MorphStats
from .readability_stats import ReadabilityStats
from spacy.tokens import Doc

class BasicStatsComponent(object):
    """
    Класс для компонента основных статистик текста

    Примеры использования:
    Добавление компонента в пайплайн:
        >>> from ruts import BasicStatsComponent
        >>> nlp = spacy.load('ru')
        >>> bsc = BasicStatsComponent()
        >>> nlp.add_pipe(bsc, 'basic', last=True)

    Доступ к извлеченным статистикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.bs.get_stats()
        >>> doc._.bs.c_letters
        {4: 3}

    Аргументы:
        name (str): Наименование компонента в пайплайне
    """

    def __init__(self, name: str = "bs"):
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

class MorphStatsComponent(object):
    """
    Класс для компонента морфологических статистик текста

    Добавление компонента в пайплайн:
        >>> from ruts import MorphStatsComponent
        >>> nlp = spacy.load('ru')
        >>> msc = MorphStatsComponent()
        >>> nlp.add_pipe(msc, 'morph', last=True)

    Доступ к извлеченным статистикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.ms.get_stats()
        >>> doc._.ms.case
        ('nomn', 'gent', 'datv')

    Аргументы:
        name (str): Наименование компонента в пайплайне
    """

    def __init__(self, name: str = "ms"):
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

class ReadabilityStatsComponent(object):
    """
    Класс для компонента основных метрик удобочитаемости текста

    Добавление компонента в пайплайн:
        >>> from ruts import ReadabilityStatsComponent
        >>> nlp = spacy.load('ru')
        >>> rsc = ReadabilityStatsComponent()
        >>> nlp.add_pipe(rsc, 'readability', last=True)

    Доступ к извлеченным метрикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.rs.get_stats()
        >>> doc._.rs.flesch_reading_easy
        82.735

    Аргументы:
        name (str): Наименование компонента в пайплайне
    """

    def __init__(self, name: str = "rs"):
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

class DiversityStatsComponent(object):
    """
    Класс для компонента основных метрик лексического разнообразия текста

    Добавление компонента в пайплайн:
        >>> from ruts import DiversityStatsComponent
        >>> nlp = spacy.load('ru')
        >>> dsc = DiversityStatsComponent()
        >>> nlp.add_pipe(dsc, 'diversity', last=True)

    Доступ к извлеченным метрикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.ds.get_stats()
        >>> doc._.ds.rttr
        1.7320508075688774

    Аргументы:
        name (str): Наименование компонента в пайплайне
    """

    def __init__(self, name: str = "ds"):
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