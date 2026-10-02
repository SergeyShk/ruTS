import importlib
from types import ModuleType

import pytest

import ruts

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
    assert set(ruts.__all__) >= PACKAGE_NAMES
    assert all(hasattr(ruts, name) for name in ruts.__all__)


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
    "ruts.cohesion_stats": "anyts.cohesion",
    "ruts.syntax_stats": "anyts.syntax",
    "ruts.corpus": "anyts.corpus",
    "ruts.corpus.collocations": "anyts.corpus.collocations",
    "ruts.corpus.dispersion": "anyts.corpus.dispersion",
    "ruts.corpus.keyness": "anyts.corpus.keyness",
    "ruts.corpus.stylometry": "anyts.corpus.stylometry",
    "ruts.corpus.compare": "anyts.corpus.compare",
    "ruts.corpus.kwic": "anyts.corpus.kwic",
}
# Имена ядра, которые библиотека определяет сама: подклассы с русскими крючками,
# обертки с русскими умолчаниями, русские описания метрик и русский шаблон чисел
RUSSIAN = {
    "CharNgramsExtractor",
    "DIVERSITY_STATS_DESC",
    "DiversityStats",
    "NUMBER_PATTERN",
    "SentsExtractor",
    "WordsExtractor",
    "keyness",
    "kwic",
}
# Классы второго среза ядра, у которых в ruTS пока свои реализации
OWN_UNTIL_SECOND_SLICE = {"BasicStats", "ReadabilityStats"}


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
            or name in OWN_UNTIL_SECOND_SLICE
        ):
            continue
        own = getattr(library_module, name)
        if name in RUSSIAN:
            assert own is not value, name
            assert not isinstance(value, type) or issubclass(own, value), name
        else:
            assert own is value, name
