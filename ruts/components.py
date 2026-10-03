"""
Компоненты spaCy для классов статистик

Описание:
    Каждый компонент кладет в doc._.<name> объект класса статистик, где name - имя
    компонента в пайплайне: add_pipe("ruts_basic", name="basic") дает doc._.basic
    spaCy такие объекты не сериализует, поэтому Doc.to_bytes(), DocBin(store_user_data=True)
    и nlp.pipe(n_process > 1) с этими компонентами не работают - исключайте
    user_data при сохранении или храните get_stats() отдельно
    Фабрики - точки входа spacy_factories, поэтому сохраненный пайплайн загружается
    spacy.load() без импорта ruts
    Документ без слов проходит пайплайн нетронутым, расширение остается None;
    имя, занятое расширением другого пакета, - ParameterError
    Добавление компонента расширяет токенизатор пайплайна правилами add_dash_rules
"""

import re

from anyts.components import StatsComponent
from anyts.constants import (
    DIVERSITY_LOG_BASE,
    HDD_SAMPLE_SIZE,
    MATTR_WINDOW_LEN,
    MTLD_MIN_LEN,
    MTLD_TTR_THRESHOLD,
)
from anyts.utils import check_words, iter_doc_units
from spacy.language import Language
from spacy.tokens import Doc

from .basic_stats import BasicStats
from .cohesion_stats import CohesionStats, unit_text
from .constants import (
    NAUSEA_TOP_N,
    PHON_WINDOW_LEN,
)
from .datasets.freq2011 import FreqDict
from .datasets.stress_dict import StressDict
from .diversity_stats import DiversityStats, check_params as check_diversity_params
from .lexical_stats import LexicalStats, is_number
from .morph_stats import MorphStats
from .phon_stats import PhonStats, check_params as check_phon_params
from .readability_stats import ReadabilityStats, check_preset
from .style_stats import StyleStats, check_params as check_style_params
from .syntax_stats import SyntaxStats
from .utils import add_dash_rules
from .verse_stats import VerseStats

_LETTER = re.compile(r"[^\W\d_]")


class _Component(StatsComponent):
    """Компонент ruTS: расширяет токенизатор пайплайна правилами add_dash_rules"""

    def prepare(self, nlp: Language) -> None:
        add_dash_rules(nlp)


@Language.factory("ruts_basic")
class BasicStatsComponent(_Component):
    """
    Класс для компонента основных статистик текста

    Примеры использования:
    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe("ruts_basic", name="basic", last=True)
        <ruts.components.BasicStatsComponent object at 0x...>

    Доступ к извлеченным статистикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.basic.c_letters
        {4: 3}

    Аргументы:
        name (str): Наименование компонента в пайплайне
    """

    def __init__(self, nlp: Language, name: str = "ruts_basic"):
        super().__init__(nlp, name)

    def compute(self, doc: Doc) -> BasicStats:
        return BasicStats(doc)


@Language.factory("ruts_morph")
class MorphStatsComponent(_Component):
    """
    Класс для компонента морфологических статистик текста

    Описание:
        Части речи и признаки берутся из разметки модели (token.pos_, token.morph)
        в терминах Universal Dependencies, в пайплайне без теггера - из pymorphy3

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe("ruts_morph", name="morph", last=True)
        <ruts.components.MorphStatsComponent object at 0x...>

    Доступ к извлеченным статистикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.morph.case
        ('Nom', None, 'Acc')

    Аргументы:
        name (str): Наименование компонента в пайплайне
    """

    def __init__(self, nlp: Language, name: str = "ruts_morph"):
        super().__init__(nlp, name)

    def compute(self, doc: Doc) -> MorphStats:
        return MorphStats(doc)


@Language.factory("ruts_readability")
class ReadabilityStatsComponent(_Component):
    """
    Класс для компонента основных метрик удобочитаемости текста

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe("ruts_readability", name="readability", last=True)
        <ruts.components.ReadabilityStatsComponent object at 0x...>

    Выбор пресета коэффициентов:
        >>> nlp.add_pipe('ruts_readability', name='readability_fiction', config={'preset': 'fiction'}, last=True)
        <ruts.components.ReadabilityStatsComponent object at 0x...>

    Доступ к извлеченным метрикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.readability.flesch_reading_easy
        82.735

    Основные статистики другого компонента вместо повторного подсчета:
        >>> _ = nlp.add_pipe("ruts_basic", name="basic", before="readability")
        >>> nlp.add_pipe('ruts_readability', name='readability_reuse', config={'basic': 'basic'}, last=True)
        <ruts.components.ReadabilityStatsComponent object at 0x...>

    Аргументы:
        name (str): Наименование компонента в пайплайне
        preset (str): Пресет коэффициентов (plainrussian, fiction, academic)
        basic (str): Расширение компонента основных статистик, которые берутся
            вместо повторного подсчета

    Исключения:
        ParameterError: Если пресет неизвестен
        SourceError: Если в указанном расширении нет основных статистик
    """

    def __init__(
        self,
        nlp: Language,
        name: str = "ruts_readability",
        preset: str = "plainrussian",
        basic: str | None = None,
    ):
        check_preset(preset)
        self.preset = preset
        self.basic = basic
        super().__init__(nlp, name)

    def compute(self, doc: Doc) -> ReadabilityStats:
        source: Doc | BasicStats = doc
        if self.basic is not None:
            source = self.from_extension(doc, self.basic, BasicStats, "ruts_basic")
        return ReadabilityStats(source, preset=self.preset)


@Language.factory("ruts_diversity")
class DiversityStatsComponent(_Component):
    """
    Класс для компонента основных метрик лексического разнообразия текста

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe("ruts_diversity", name="diversity", last=True)
        <ruts.components.DiversityStatsComponent object at 0x...>

    Настройка окон, порогов и основания логарифма:
        >>> nlp.add_pipe('ruts_diversity', name='diversity_ln', config={'window_len': 100, 'log_base': 2.718281828459045}, last=True)
        <ruts.components.DiversityStatsComponent object at 0x...>

    Доступ к извлеченным метрикам:
        >>> doc = nlp("мама мыла раму")
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
        name: str = "ruts_diversity",
        window_len: int = MATTR_WINDOW_LEN,
        mtld_threshold: float = MTLD_TTR_THRESHOLD,
        mtld_min_len: int = MTLD_MIN_LEN,
        hdd_sample_size: int = HDD_SAMPLE_SIZE,
        log_base: float = DIVERSITY_LOG_BASE,
    ):
        check_diversity_params(window_len, mtld_threshold, mtld_min_len, hdd_sample_size, log_base)
        self.window_len = window_len
        self.mtld_threshold = mtld_threshold
        self.mtld_min_len = mtld_min_len
        self.hdd_sample_size = hdd_sample_size
        self.log_base = log_base
        super().__init__(nlp, name)

    def compute(self, doc: Doc) -> DiversityStats:
        return DiversityStats(
            doc,
            window_len=self.window_len,
            mtld_threshold=self.mtld_threshold,
            mtld_min_len=self.mtld_min_len,
            hdd_sample_size=self.hdd_sample_size,
            log_base=self.log_base,
        )


@Language.factory("ruts_style")
class StyleStatsComponent(_Component):
    """
    Класс для компонента SEO-метрик стиля текста

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe("ruts_style", name="style", last=True)
        <ruts.components.StyleStatsComponent object at 0x...>

    Настройка списка стоп-слов и количества самых частых слов:
        >>> nlp.add_pipe('ruts_style', name='style_short', config={'stopwords': ['и', 'в', 'не'], 'top_n': 5}, last=True)
        <ruts.components.StyleStatsComponent object at 0x...>

    Доступ к извлеченным метрикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.style.water
        0.0

    Аргументы:
        name (str): Наименование компонента в пайплайне
        stopwords (list[str]): Список стоп-слов для водности; если не задан, используется разметка pymorphy3
        top_n (int): Количество самых частых слов для академической тошноты и естественности по Ципфу

    Исключения:
        SourceTypeError: Если стоп-слова не набор строк
        ParameterError: Если количество самых частых слов не целое число или меньше 1
    """

    def __init__(
        self,
        nlp: Language,
        name: str = "ruts_style",
        stopwords: list[str] | None = None,
        top_n: int = NAUSEA_TOP_N,
    ):
        check_style_params(top_n)
        if stopwords is not None:
            check_words(stopwords, "stopwords", ordered=False)
        self.stopwords = stopwords
        self.top_n = top_n
        super().__init__(nlp, name)

    def compute(self, doc: Doc) -> StyleStats:
        return StyleStats(doc, stopwords=self.stopwords, top_n=self.top_n)


@Language.factory("ruts_phon")
class PhonStatsComponent(_Component):
    """
    Класс для компонента фоностатистик текста

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe("ruts_phon", name="phon", last=True)
        <ruts.components.PhonStatsComponent object at 0x...>

    Настройка окна для аллитерации и ассонанса:
        >>> nlp.add_pipe('ruts_phon', name='phon_windowed', config={'window_len': 5}, last=True)
        <ruts.components.PhonStatsComponent object at 0x...>

    Доступ к извлеченным статистикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.phon.p_open_syllables
        1.0

    Аргументы:
        name (str): Наименование компонента в пайплайне
        window_len (int): Размер окна в словах для аллитерации и ассонанса
    """

    def __init__(self, nlp: Language, name: str = "ruts_phon", window_len: int = PHON_WINDOW_LEN):
        check_phon_params(window_len)
        self.window_len = window_len
        super().__init__(nlp, name)

    def compute(self, doc: Doc) -> PhonStats:
        return PhonStats(doc, window_len=self.window_len)


@Language.factory("ruts_syntax", requires=["token.dep", "token.head"])
class SyntaxStatsComponent(_Component):
    """
    Класс для компонента синтаксических статистик текста

    Описание:
        Компонент работает по дереву зависимостей, поэтому в пайплайне должен
        быть парсер (модели ru_core_news_sm, ru_core_news_md, ru_core_news_lg)

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe("ruts_syntax", name="syntax", last=True)
        <ruts.components.SyntaxStatsComponent object at 0x...>

    Доступ к извлеченным статистикам:
        >>> doc = nlp("мама мыла раму")
        >>> doc._.syntax.tree_depth
        1.0

    Аргументы:
        name (str): Наименование компонента в пайплайне
    """

    def __init__(self, nlp: Language, name: str = "ruts_syntax"):
        super().__init__(nlp, name)

    def compute(self, doc: Doc) -> SyntaxStats:
        return SyntaxStats(doc)


@Language.factory("ruts_cohesion")
class CohesionStatsComponent(_Component):
    """
    Класс для компонента статистик связности текста

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe("ruts_cohesion", name="cohesion", last=True)
        <ruts.components.CohesionStatsComponent object at 0x...>

    Доступ к извлеченным статистикам:
        >>> doc = nlp("Кот сидел на окне. Он смотрел на птиц.")
        >>> doc._.cohesion.argument_overlap_adjacent
        0.0

    Аргументы:
        name (str): Наименование компонента в пайплайне
    """

    def __init__(self, nlp: Language, name: str = "ruts_cohesion"):
        super().__init__(nlp, name)

    def compute(self, doc: Doc) -> CohesionStats:
        return CohesionStats(doc)


@Language.factory("ruts_lexical")
class LexicalStatsComponent(_Component):
    """
    Класс для компонента статистик лексической сложности текста

    Описание:
        Документ, в котором все слова - числа, проходит нетронутым

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe("ruts_lexical", name="lexical", last=True)
        <ruts.components.LexicalStatsComponent object at 0x...>

    Словарь из другой директории:
        >>> nlp.add_pipe('ruts_lexical', name='lexical_dicts', config={'data_dir': '/path/to/dicts'}, last=True)
        <ruts.components.LexicalStatsComponent object at 0x...>

    Доступ к извлеченным статистикам:
        >>> doc = nlp("Кот сидел на окне и смотрел на птиц")
        >>> doc._.lexical.p_top1000
        0.75

    Аргументы:
        name (str): Наименование компонента в пайплайне
        data_dir (str): Путь к директории с частотным словарем; если не задан,
            используется директория по умолчанию
    """

    def __init__(self, nlp: Language, name: str = "ruts_lexical", data_dir: str | None = None):
        self.freq_dict = FreqDict(data_dir) if data_dir else FreqDict()
        super().__init__(nlp, name)

    def accepts(self, doc: Doc) -> bool:
        """Статистики получает документ со словом, которое не число"""
        return any(
            not is_number(unit_text(unit)) for unit in iter_doc_units(doc, join_hyphens=True)
        )

    def compute(self, doc: Doc) -> LexicalStats:
        return LexicalStats(doc, freq_dict=self.freq_dict)


@Language.factory("ruts_verse")
class VerseStatsComponent(_Component):
    """
    Класс для компонента стиховедческих статистик текста

    Описание:
        Компонент работает по тексту Doc с переносами строк, поэтому текст
        стихотворения нужно передавать в nlp как есть, не склеивая строки;
        текст с буквами, но без русских слов дает пустые статистики, как VerseStats,
        документ без букв проходит нетронутым

    Добавление компонента в пайплайн:
        >>> import ruts
        >>> import spacy
        >>> nlp = spacy.load('ru_core_news_sm')
        >>> nlp.add_pipe("ruts_verse", name="verse", last=True)
        <ruts.components.VerseStatsComponent object at 0x...>

    Доступ к извлеченным статистикам:
        >>> doc = nlp("Буря мглою небо кроет,\\nВихри снежные крутя;\\nТо, как зверь, она завоет,\\nТо заплачет, как дитя")
        >>> doc._.verse.meter, doc._.verse.n_feet
        ('хорей', 4)

    Словарь ударений из другой директории - компонент с этим словарем требует
    его загрузки при первом вызове:
        >>> nlp.add_pipe('ruts_verse', name='verse_dicts', config={'data_dir': '/path/to/dicts'}, last=True)
        <ruts.components.VerseStatsComponent object at 0x...>

    Аргументы:
        name (str): Наименование компонента в пайплайне
        data_dir (str): Путь к директории со словарем ударений; если не задан,
            используется директория по умолчанию
    """

    def __init__(self, nlp: Language, name: str = "ruts_verse", data_dir: str | None = None):
        self.stress_dict = StressDict(data_dir) if data_dir else StressDict()
        super().__init__(nlp, name)

    def accepts(self, doc: Doc) -> bool:
        """Статистики получает документ с буквой"""
        return _LETTER.search(doc.text) is not None

    def compute(self, doc: Doc) -> VerseStats:
        return VerseStats(doc, stress_dict=self.stress_dict)
