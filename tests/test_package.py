import importlib
import re
import subprocess
import sys
from types import MappingProxyType, ModuleType

import pytest

import ruts
from ruts.corpus import sentence_rhythm, split_windows
from ruts.diversity_stats import calc_ttr, calc_windowed, check_params
from ruts.readability_stats import calc_reading_time
from ruts.visualizers.highlight import HighlightedText

# Публичные имена 0.15.0.dev7: переезд на ядро не должен терять ни одного
PACKAGE_NAMES = {
    "BasicStats",
    "BasicStatsComponent",
    "CharNgramsExtractor",
    "CohesionStats",
    "CohesionStatsComponent",
    "DataFileError",
    "DatasetNotFoundError",
    "DiversityStats",
    "DiversityStatsComponent",
    "DownloadError",
    "LexicalStats",
    "LexicalStatsComponent",
    "MorphStats",
    "MorphStatsComponent",
    "ParameterError",
    "PhonStats",
    "PhonStatsComponent",
    "ReadabilityStats",
    "ReadabilityStatsComponent",
    "RutsError",
    "SentsExtractor",
    "SourceError",
    "SourceTypeError",
    "StyleStats",
    "StyleStatsComponent",
    "SyntaxStats",
    "SyntaxStatsComponent",
    "UnknownStatError",
    "VerseStats",
    "VerseStatsComponent",
    "WordsExtractor",
    "__version__",
}
SUBPACKAGE_NAMES = {
    "corpus": {
        "Collocation",
        "Concordance",
        "Dispersion",
        "Keyword",
        "ZetaScore",
        "bootstrap_median_diff",
        "calc_cliff_delta",
        "calc_cohen_d",
        "collocations",
        "compare_corpora",
        "compare_features",
        "corpus_features",
        "delta",
        "delta_profiles",
        "dispersion",
        "format_kwic",
        "frequency_table",
        "function_words_profile",
        "holm_correction",
        "keyness",
        "kilgarriff_chi2",
        "kwic",
        "mendenhall_curve",
        "mendenhall_distance",
        "print_kwic",
        "sentence_rhythm",
        "split_windows",
        "text_features",
        "z_scores",
        "zeta",
    },
    "datasets": {
        "FreqDict",
        "PoetryCorpus",
        "RussianLiterature",
        "SovChLit",
        "StalinWorks",
        "StressDict",
        "TextsByGrade",
    },
    "visualizers": {
        "Highlight",
        "HighlightedText",
        "collocation_network",
        "dendrogram_plot",
        "dispersion_plot",
        "fingerprinting",
        "frequency_spectrum_plot",
        "heaps_plot",
        "highlight",
        "keyness_plot",
        "mds_plot",
        "mendenhall_plot",
        "pca_plot",
        "sentence_lengths",
        "sentence_lengths_plot",
        "wordtree",
        "zipf",
        "zipf_theory",
    },
}


def test_package_names():
    # Компоненты - атрибуты пакета, но не __all__: import * не грузит spaCy
    components = {name for name in PACKAGE_NAMES if name.endswith("Component")}
    assert set(ruts.__all__) >= PACKAGE_NAMES - components
    assert not set(ruts.__all__) & components
    assert all(hasattr(ruts, name) for name in PACKAGE_NAMES | set(ruts.__all__))


@pytest.mark.parametrize("name", SUBPACKAGE_NAMES)
def test_subpackage_names(name):
    module = importlib.import_module(f"ruts.{name}")
    assert set(module.__all__) >= SUBPACKAGE_NAMES[name]
    assert module.__all__ == sorted(module.__all__)
    assert all(hasattr(module, attr) for attr in module.__all__)


# Модули библиотеки и модули ядра, на которых они построены
CORE_MODULES = {
    "ruts": "anyts",
    "ruts.exceptions": "anyts.exceptions",
    "ruts.utils": "anyts.utils",
    "ruts.extractors": "anyts.extractors",
    "ruts.diversity_stats": "anyts.diversity_stats",
    "ruts.cohesion_stats": "anyts.cohesion_stats",
    "ruts.syntax_stats": "anyts.syntax_stats",
    "ruts.style_stats": "anyts.style_stats",
    "ruts.lexical_stats": "anyts.lexical_stats",
    "ruts.corpus": "anyts.corpus",
    "ruts.corpus.collocations": "anyts.corpus.collocations",
    "ruts.corpus.dispersion": "anyts.corpus.dispersion",
    "ruts.corpus.keyness": "anyts.corpus.keyness",
    "ruts.corpus.stylometry": "anyts.corpus.stylometry",
    "ruts.corpus.compare": "anyts.corpus.compare",
    "ruts.corpus.kwic": "anyts.corpus.kwic",
    "ruts.basic_stats": "anyts.basic_stats",
    "ruts.readability_stats": "anyts.readability_stats",
    "ruts.components": "anyts.components",
    "ruts.phon_stats": "anyts.phon_stats",
    "ruts.datasets.dataset": "anyts.datasets",
    "ruts.visualizers": "anyts.visualizers",
    "ruts.visualizers.highlight": "anyts.visualizers.highlight",
}
# Имена ядра, которые модуль библиотеки определяет сам: подклассы с русскими крючками,
# обертки с русскими умолчаниями, русские описания, подписи и настройки
RUSSIAN = {
    "ruts": {"CharNgramsExtractor", "DiversityStats", "SentsExtractor", "WordsExtractor"},
    "ruts.utils": {"find_phrases"},
    "ruts.extractors": {
        "CharNgramsExtractor",
        "NUMBER_PATTERN",
        "SentsExtractor",
        "WordsExtractor",
    },
    "ruts.diversity_stats": {
        "DIVERSITY_STATS_DESC",
        "DiversityStats",
        "calc_windowed",
        "check_params",
    },
    "ruts.cohesion_stats": {"COHESION_STATS_DESC", "CohesionStats", "SentsExtractor"},
    "ruts.syntax_stats": {
        "SYNTAX_STATS_DESC",
        "SyntaxStats",
        "is_clause_head",
        "is_infinitive_clause",
        "is_infinitive_clause_head",
        "is_subordinate_clause_head",
    },
    "ruts.style_stats": {
        "STYLE_STATS_DESC",
        "StyleStats",
        "WordsExtractor",
        "calc_academic_nausea",
        "calc_keyword_density",
        "calc_parentheticals",
        "calc_phrase_density",
        "calc_water",
        "calc_zipf_naturalness",
        "check_params",
        "find_nausea_words",
        "find_parentheticals",
    },
    "ruts.lexical_stats": {"LEXICAL_STATS_DESC", "LexicalStats", "calc_surprisal"},
    "ruts.corpus": {
        "collocations",
        "dispersion",
        "keyness",
        "kwic",
        "sentence_rhythm",
        "split_windows",
    },
    "ruts.corpus.collocations": {"collocations"},
    "ruts.corpus.dispersion": {"dispersion"},
    "ruts.corpus.keyness": {"keyness"},
    "ruts.corpus.compare": {
        "CLOSING_MARKS",
        "OPENING_MARKS",
        "SYMMETRIC_MARKS",
        "sentence_rhythm",
        "split_windows",
    },
    "ruts.corpus.kwic": {"kwic"},
    "ruts.basic_stats": {
        "BASIC_STATS_DESC",
        "BasicStats",
        "COMPLEX_SYL_FACTOR",
        "DASH_PATTERN",
        "LONG_WORD_LETTER_FACTOR",
        "PUNCTUATION_MARKS",
        "SentsExtractor",
        "WordsExtractor",
        "count_punctuations",
    },
    "ruts.readability_stats": {
        "BasicStats",
        "GRADE_AGE_LEVELS",
        "POSTGRADUATE_LEVEL",
        "READABILITY_GRADE_STATS",
        "READABILITY_PRESETS",
        "READABILITY_STATS_DESC",
        "READING_EASE_GRADES",
        "READING_SPEED_NORMS",
        "READING_SPEED_WPM",
        "ReadabilityStats",
        "SMOG_COMPLEX_SYL_FACTOR",
        "calc_automated_readability_index",
        "calc_coleman_liau_index",
        "calc_consensus_grade",
        "calc_flesch_kincaid_grade",
        "calc_flesch_reading_easy",
        "calc_reading_time",
        "calc_smog_index",
        "flesch_reading_easy_to_grade",
        "grade_to_age",
    },
    "ruts.components": {
        "BasicStats",
        "BasicStatsComponent",
        "CohesionStats",
        "CohesionStatsComponent",
        "DiversityStatsComponent",
        "LexicalStats",
        "LexicalStatsComponent",
        "PhonStats",
        "PhonStatsComponent",
        "ReadabilityStats",
        "ReadabilityStatsComponent",
        "StyleStats",
        "StyleStatsComponent",
        "SyntaxStats",
        "SyntaxStatsComponent",
        "is_number",
    },
    "ruts.phon_stats": {
        "PHON_STATS_DESC",
        "PhonStats",
        "WordsExtractor",
        "check_params",
        "cv_pattern",
    },
    "ruts.datasets.dataset": {"Dataset", "substring_filter"},
    "ruts.visualizers": {
        "HighlightedText",
        "dendrogram_plot",
        "dispersion_plot",
        "fingerprinting",
        "frequency_spectrum_plot",
        "heaps_plot",
        "keyness_plot",
        "mds_plot",
        "mendenhall_plot",
        "pca_plot",
        "sentence_lengths",
        "sentence_lengths_plot",
        "wordtree",
        "zipf",
        "zipf_theory",
    },
    "ruts.visualizers.highlight": {
        "HighlightedText",
        "calc_alliteration_runs",
        "find_alliteration",
        "find_complex_words",
        "find_connector_highlights",
        "find_long_sents",
        "find_phrase_highlights",
        "find_split_predicate_highlights",
        "get_doc_words",
    },
}

# Имена ядра, которые библиотека еще не перевела на объект ядра: MorphStats до каркаса ядра
PENDING = {"ruts.components": {"MorphStats", "MorphStatsComponent"}}


@pytest.mark.parametrize(("library", "core"), CORE_MODULES.items())
def test_core_names(library, core):
    """Имя ядра в библиотеке - объект ядра, а не его копия"""
    library_module, core_module = importlib.import_module(library), importlib.import_module(core)
    # dir, а не vars: ленивый пакет ядра импортирует имена при первом обращении
    for name in dir(core_module):
        value = getattr(core_module, name)
        if (
            name.startswith("_")
            or isinstance(value, ModuleType)
            or not hasattr(library_module, name)
            or name in PENDING.get(library, ())
        ):
            continue
        own = getattr(library_module, name)
        if name in RUSSIAN.get(library, ()):
            assert own is not value, name
            assert not isinstance(value, type) or issubclass(own, value), name
        else:
            assert own is value, name


TEXT_STATS = (
    "BasicStats",
    "ReadabilityStats",
    "DiversityStats",
    "MorphStats",
    "StyleStats",
    "PhonStats",
    "CohesionStats",
    "LexicalStats",
    "VerseStats",
)


@pytest.mark.parametrize("name", TEXT_STATS)
@pytest.mark.parametrize("text", ["", "   ", "?!"])
def test_no_words_message(name, text):
    """Текст без слов дает одно сообщение во всех классах, а не английское сообщение ядра"""
    with pytest.raises(ruts.SourceError, match=r"^В источнике данных отсутствуют слова$"):
        getattr(ruts, name)(text)


@pytest.mark.parametrize("name", TEXT_STATS)
def test_source_type_message(name):
    with pytest.raises(ruts.SourceTypeError, match=r"^Источник данных не может быть типа int$"):
        getattr(ruts, name)(5)


@pytest.mark.parametrize("name", [*TEXT_STATS, "SyntaxStats"])
def test_source_span_message(name):
    """Span вместо Doc - подсказка as_doc, а не тип источника"""
    import spacy

    span = spacy.blank("ru")("Кот спит на окне.")[0:2]
    with pytest.raises(ruts.SourceTypeError, match=r"^Источник данных не может быть Span"):
        getattr(ruts, name)(span)


@pytest.mark.parametrize("name", ["BasicStats", "ReadabilityStats"])
def test_extractor_type_messages(name):
    stats = getattr(ruts, name)
    with pytest.raises(ruts.SourceTypeError, match=r"^Экстрактор предложений должен быть"):
        stats("Кот спит.", sents_extractor=5)
    with pytest.raises(ruts.SourceTypeError, match=r"^Экстрактор слов должен быть"):
        stats("Кот спит.", words_extractor=5)


@pytest.mark.parametrize(
    "name",
    [
        "BasicStats",
        "ReadabilityStats",
        "DiversityStats",
        "MorphStats",
        "StyleStats",
        "PhonStats",
        "CohesionStats",
        "LexicalStats",
    ],
)
def test_no_words_after_the_words_extractor(name):
    """Экстрактор, отбросивший все слова текста, дает то же сообщение, что текст без слов"""
    extractor = ruts.WordsExtractor(stopwords=["в", "году"], filter_nums=True)
    with pytest.raises(ruts.SourceError, match=r"^В источнике данных отсутствуют слова$"):
        getattr(ruts, name)("В 2024 году.", words_extractor=extractor)


def test_core_messages():
    """Русский словарь сообщений ядра полон: новый ключ ядра не выйдет по-английски"""
    from anyts.constants import MESSAGES

    from ruts.constants import _RU_CORE_MESSAGES, CORE_MESSAGES

    assert set(_RU_CORE_MESSAGES) == set(MESSAGES)
    assert CORE_MESSAGES == _RU_CORE_MESSAGES
    with pytest.raises(TypeError):
        CORE_MESSAGES["no_words"] = "Нет слов"  # type: ignore[index]
    for cls in (
        ruts.BasicStats,
        ruts.ReadabilityStats,
        ruts.DiversityStats,
        ruts.StyleStats,
        ruts.LexicalStats,
        ruts.PhonStats,
        ruts.SyntaxStats,
        ruts.CohesionStats,
        ruts.SentsExtractor,
        ruts.WordsExtractor,
        ruts.CharNgramsExtractor,
        HighlightedText,
    ):
        assert cls.messages is CORE_MESSAGES


def test_new_core_message_falls_back_to_english():
    """Ключ, добавленный патчем ядра, выходит по-английски, а проверка сообщений ядра проходит"""
    from anyts.constants import MESSAGES
    from anyts.utils import check_messages

    from ruts.constants import _RU_CORE_MESSAGES

    patched = MappingProxyType({**MESSAGES, "new_key": "New message"})
    merged = MappingProxyType({**patched, **_RU_CORE_MESSAGES})
    check_messages(merged, patched)
    assert merged["new_key"] == "New message"


@pytest.mark.parametrize(
    ("call", "match"),
    [
        (lambda: ruts.DiversityStats("Кот спит", window_len=0), r"^Размер окна должен быть"),
        (lambda: ruts.DiversityStats("Кот спит").windowed("ttr", 0), r"^Размер окна должен быть"),
        (
            lambda: ruts.ReadabilityStats("Кот спит.").describe("x"),
            r"^'?Неизвестная статистика: x",
        ),
        (lambda: ruts.BasicStats("Кот спит.", complex_syl_factor=0), r"^Наименьшее число слогов"),
        (lambda: calc_windowed(["кот"] * 5, calc_ttr, window_len=0), r"^Размер окна должен быть"),
        (lambda: check_params(window_len=0), r"^Размер окна должен быть"),
        (lambda: calc_reading_time(10, 0), r"^Скорость чтения должна быть"),
        (lambda: ruts.WordsExtractor(ngram_range=(2, 1)), r"^Нижняя граница N-грамм больше"),
        (lambda: ruts.SentsExtractor(min_len=-1), r"^Границы длины предложения не могут"),
        (lambda: ruts.CharNgramsExtractor(n=0), r"^Длина N-граммы должна быть больше 0"),
        (lambda: split_windows("Кот спит", 0), r"^Размер окна должен быть"),
        (lambda: split_windows("Кот спит", 2, 3), r"^Наименьшее число слов в окне не может"),
        (lambda: sentence_rhythm([3, -1]), r"^Длины предложений не могут быть отрицательными"),
    ],
)
def test_core_messages_in_russian(call, match):
    with pytest.raises(ValueError, match=match):
        call()


@pytest.mark.parametrize("name", [*TEXT_STATS, "SyntaxStats"])
def test_stats_interface(name):
    """Каждый класс статистик - подкласс Stats ядра с русскими сообщениями"""
    from anyts.stats import Stats

    from ruts.constants import CORE_MESSAGES

    stats_class = getattr(ruts, name)
    assert issubclass(stats_class, Stats)
    assert stats_class.messages is CORE_MESSAGES
    assert stats_class.stats_desc


@pytest.mark.parametrize("name", [*TEXT_STATS, "SyntaxStats"])
def test_stats_in_docstring(name):
    """Каждая метрика get_stats описана в разделе «Атрибуты» докстринга своего класса"""
    stats_class = getattr(ruts, name)
    attributes = re.search(r"Атрибуты:\n(.*?)\n\n", stats_class.__doc__, re.DOTALL)
    assert attributes is not None
    assert [key for key in stats_class.stats_desc if f" {key} (" not in attributes[1]] == []


def _run(code: str) -> str:
    """Вывод кода в отдельном процессе, где ничего не импортировано заранее"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


@pytest.mark.parametrize(
    ("statement", "absent"),
    [
        ("import ruts", ("spacy", "thinc", "scipy", "pandas", "matplotlib")),
        ("from ruts.visualizers import highlight", ("spacy", "pandas", "matplotlib")),
        ("from ruts.corpus import kwic", ("spacy", "pandas", "matplotlib")),
    ],
)
def test_imports_are_light(statement, absent):
    loaded = _run(f"import sys\n{statement}\nprint(' '.join(sorted(sys.modules)))").split()
    assert not set(absent) & set(loaded)


def test_only_components_import_spacy():
    """spaCy грузят документы пользователя и компоненты, а не импорт модулей ruTS"""
    code = (
        "import importlib, pkgutil, sys, ruts\n"
        "names = [m.name for m in pkgutil.walk_packages(ruts.__path__, 'ruts.')]\n"
        "for name in names:\n"
        "    if name != 'ruts.components':\n"
        "        importlib.import_module(name)\n"
        "print(len(names), 'spacy' in sys.modules, 'thinc' in sys.modules)"
    )
    n_modules, spacy, thinc = _run(code).split()
    assert int(n_modules) > 40
    assert (spacy, thinc) == ("False", "False")


def test_components_on_first_use():
    code = (
        "import sys, ruts\n"
        "before = 'spacy' in sys.modules\n"
        "component = ruts.StyleStatsComponent\n"
        "print(before, 'spacy' in sys.modules, component.__module__)"
    )
    assert _run(code) == "False True ruts.components"


def test_factories_without_import():
    """Фабрики находятся по точкам входа spacy_factories, без import ruts"""
    code = (
        "import spacy\n"
        "nlp = spacy.blank('ru')\n"
        "nlp.add_pipe('ruts_style')\n"
        "print(nlp('мама мыла раму')._.ruts_style.water)"
    )
    assert _run(code) == "0.0"


@pytest.mark.parametrize(
    "stub", ["sys.modules['spacy'] = None", "sys.modules['spacy'] = types.ModuleType('spacy')"]
)
def test_import_with_a_stub_of_spacy(stub):
    """Пометка «spaCy недоступен» и заглушка spaCy (Pyodide) не мешают импорту"""
    code = (
        f"import sys, types\n{stub}\n"
        "import ruts\n"
        "print(ruts.StyleStats('Мама мыла раму.').water, 'ruts.components' in sys.modules)"
    )
    assert _run(code) == "0.0 False"


def test_star_import_and_help_without_spacy():
    code = (
        "import pydoc, sys\n"
        "from ruts import *\n"
        "import ruts\n"
        "pydoc.render_doc(ruts)\n"
        "print('BasicStats' in dir(), 'spacy' in sys.modules, 'ruts.components' in sys.modules)"
    )
    assert _run(code) == "True False False"


def test_lazy_packages_export_their_names():
    for package in (ruts, ruts.corpus, ruts.visualizers):
        assert set(package.__all__) <= set(dir(package))
        assert all(getattr(package, name) is not None for name in package.__all__)
    assert callable(ruts.visualizers.highlight) and callable(ruts.corpus.kwic)


def test_factories_with_spacy_loaded_before():
    """Точки входа, прочитанные до установки ruTS, не мешают: при загруженном spaCy
    import ruts регистрирует фабрики сам"""
    code = (
        "import catalogue\n"
        "catalogue.AVAILABLE_ENTRY_POINTS = {}\n"
        "import spacy, ruts\n"
        "nlp = spacy.blank('ru')\n"
        "nlp.add_pipe('ruts_basic')\n"
        "print(nlp('мама мыла раму')._.ruts_basic.n_words)"
    )
    assert _run(code) == "3"


def test_doc_of_spacy_loaded_after():
    """Doc распознается и тогда, когда spaCy загружен после import ruts"""
    code = (
        "import sys, ruts\n"
        "before = 'spacy' in sys.modules\n"
        "import spacy\n"
        "doc = spacy.blank('ru')('Мама мыла раму. Кот спал.')\n"
        "print(before, ruts.BasicStats(doc).n_sents, len(ruts.DiversityStats(doc).words),"
        " len(ruts.StyleStats(doc).words))"
    )
    assert _run(code) == "False 2 5 5"
