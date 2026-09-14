from spacy.language import Language
from spacy.tokens import Doc

from .basic_stats import BasicStats
from .cohesion_stats import CohesionStats
from .constants import (
    DIVERSITY_LOG_BASE,
    HDD_SAMPLE_SIZE,
    MATTR_WINDOW_LEN,
    MTLD_MIN_LEN,
    MTLD_TTR_THRESHOLD,
    NAUSEA_TOP_N,
    PHON_WINDOW_LEN,
)
from .diversity_stats import DiversityStats
from .morph_stats import MorphStats
from .phon_stats import PhonStats
from .readability_stats import ReadabilityStats
from .style_stats import StyleStats
from .syntax_stats import SyntaxStats


@Language.factory("basic")
class BasicStatsComponent:
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
class MorphStatsComponent:
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
class ReadabilityStatsComponent:
    """
    Класс для компонента основных метрик удобочитаемости текста

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe('readability', last=True)

    Выбор пресета коэффициентов:
        >>> nlp.add_pipe('readability', config={'preset': 'fiction'}, last=True)

    Доступ к извлеченным метрикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.readability.get_stats()
        >>> doc._.readability.flesch_reading_easy
        82.735

    Аргументы:
        name (str): Наименование компонента в пайплайне
        preset (str): Пресет коэффициентов (plainrussian, fiction, academic)
    """

    def __init__(self, nlp: Language, name: str = "readability", preset: str = "plainrussian"):
        self.name = name
        self.preset = preset
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Добавление извлеченных метрик в компонент

        Аргументы:
            doc (Doc): Объект Doc

        Вывод:
            doc (Doc): Модифицированный объект Doc
        """
        rs = ReadabilityStats(doc, preset=self.preset)
        doc._.set(self.name, rs)
        return doc


@Language.factory("diversity")
class DiversityStatsComponent:
    """
    Класс для компонента основных метрик лексического разнообразия текста

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe('diversity', last=True)

    Настройка окон, порогов и основания логарифма:
        >>> nlp.add_pipe('diversity', config={'window_len': 100, 'log_base': 2.718281828459045}, last=True)

    Доступ к извлеченным метрикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.diversity.get_stats()
        >>> doc._.diversity.rttr
        1.7320508075688774

    Аргументы:
        name (str): Наименование компонента в пайплайне
        window_len (int): Размер окна для MATTR и сегмента для MSTTR
        mtld_threshold (float): Порог TTR для MTLD, MA-MTLD и MTLD-W
        mtld_min_len (int): Минимальная длина фактора для MTLD, MA-MTLD и MTLD-W
        hdd_sample_size (int): Размер выборки для HD-D
        log_base (float): Основание логарифма для метрик Summer, Maas и Dugast
    """

    def __init__(
        self,
        nlp: Language,
        name: str = "diversity",
        window_len: int = MATTR_WINDOW_LEN,
        mtld_threshold: float = MTLD_TTR_THRESHOLD,
        mtld_min_len: int = MTLD_MIN_LEN,
        hdd_sample_size: int = HDD_SAMPLE_SIZE,
        log_base: float = DIVERSITY_LOG_BASE,
    ):
        self.name = name
        self.window_len = window_len
        self.mtld_threshold = mtld_threshold
        self.mtld_min_len = mtld_min_len
        self.hdd_sample_size = hdd_sample_size
        self.log_base = log_base
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Добавление извлеченных метрик в компонент

        Аргументы:
            doc (Doc): Объект Doc

        Вывод:
            doc (Doc): Модифицированный объект Doc
        """
        ds = DiversityStats(
            doc,
            window_len=self.window_len,
            mtld_threshold=self.mtld_threshold,
            mtld_min_len=self.mtld_min_len,
            hdd_sample_size=self.hdd_sample_size,
            log_base=self.log_base,
        )
        doc._.set(self.name, ds)
        return doc


@Language.factory("style")
class StyleStatsComponent:
    """
    Класс для компонента SEO-метрик стиля текста

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe('style', last=True)

    Настройка списка стоп-слов и количества самых частых слов:
        >>> nlp.add_pipe('style', config={'stopwords': ['и', 'в', 'не'], 'top_n': 5}, last=True)

    Доступ к извлеченным метрикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.style.get_stats()
        >>> doc._.style.water
        0.0

    Аргументы:
        name (str): Наименование компонента в пайплайне
        stopwords (list[str]): Список стоп-слов для водности; если не задан, используется разметка pymorphy3
        top_n (int): Количество самых частых слов для академической тошноты и естественности по Ципфу
    """

    def __init__(
        self,
        nlp: Language,
        name: str = "style",
        stopwords: list[str] | None = None,
        top_n: int = NAUSEA_TOP_N,
    ):
        self.name = name
        self.stopwords = stopwords
        self.top_n = top_n
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Добавление извлеченных метрик в компонент

        Аргументы:
            doc (Doc): Объект Doc

        Вывод:
            doc (Doc): Модифицированный объект Doc
        """
        ss = StyleStats(doc, stopwords=self.stopwords, top_n=self.top_n)
        doc._.set(self.name, ss)
        return doc


@Language.factory("phon")
class PhonStatsComponent:
    """
    Класс для компонента фоностатистик текста

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe('phon', last=True)

    Настройка окна для аллитерации и ассонанса:
        >>> nlp.add_pipe('phon', config={'window_len': 5}, last=True)

    Доступ к извлеченным статистикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.phon.get_stats()
        >>> doc._.phon.p_open_syllables
        1.0

    Аргументы:
        name (str): Наименование компонента в пайплайне
        window_len (int): Размер окна в словах для аллитерации и ассонанса
    """

    def __init__(self, nlp: Language, name: str = "phon", window_len: int = PHON_WINDOW_LEN):
        self.name = name
        self.window_len = window_len
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Добавление извлеченных статистик в компонент

        Аргументы:
            doc (Doc): Объект Doc

        Вывод:
            doc (Doc): Модифицированный объект Doc
        """
        ps = PhonStats(doc, window_len=self.window_len)
        doc._.set(self.name, ps)
        return doc


@Language.factory("syntax", requires=["token.dep", "token.head"])
class SyntaxStatsComponent:
    """
    Класс для компонента синтаксических статистик текста

    Описание:
        Компонент работает по дереву зависимостей, поэтому в пайплайне должен
        быть парсер (модели ru_core_news_sm, ru_core_news_md, ru_core_news_lg)

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe('syntax', last=True)

    Доступ к извлеченным статистикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.syntax.get_stats()
        >>> doc._.syntax.tree_depth
        1.0

    Аргументы:
        name (str): Наименование компонента в пайплайне
    """

    def __init__(self, nlp: Language, name: str = "syntax"):
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
        ss = SyntaxStats(doc)
        doc._.set(self.name, ss)
        return doc


@Language.factory("cohesion")
class CohesionStatsComponent:
    """
    Класс для компонента статистик связности текста

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe('cohesion', last=True)

    Доступ к извлеченным статистикам:
        >>> doc = nlp("Кот сидел на окне. Он смотрел на птиц.")
        >>> doc._.cohesion.get_stats()
        >>> doc._.cohesion.argument_overlap_adjacent
        0.0

    Аргументы:
        name (str): Наименование компонента в пайплайне
    """

    def __init__(self, nlp: Language, name: str = "cohesion"):
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
        cs = CohesionStats(doc)
        doc._.set(self.name, cs)
        return doc
