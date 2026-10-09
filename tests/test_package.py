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
    "ruts.basic_stats": "anyts.basic_stats",
    "ruts.readability_stats": "anyts.readability_stats",
    "ruts.components": "anyts.components",
    "ruts.phon_stats": "anyts.phonetics",
    "ruts.datasets.dataset": "anyts.datasets",
    "ruts.visualizers": "anyts.visualizers",
    "ruts.visualizers.highlight": "anyts.visualizers.highlight",
}
# Имена ядра, которые библиотека определяет сама: подклассы с русскими крючками,
# обертки с русскими умолчаниями, русские описания, подписи и настройки
RUSSIAN = {
    "BASIC_STATS_DESC",
    "BasicStats",
    "COMPLEX_SYL_FACTOR",
    "CharNgramsExtractor",
    "DASH_PATTERN",
    "DIVERSITY_STATS_DESC",
    "Dataset",
    "DiversityStats",
    "GRADE_AGE_LEVELS",
    "HighlightedText",
    "LONG_WORD_LETTER_FACTOR",
    "NUMBER_PATTERN",
    "POSTGRADUATE_LEVEL",
    "PUNCTUATION_MARKS",
    "READABILITY_GRADE_STATS",
    "READABILITY_PRESETS",
    "READABILITY_STATS_DESC",
    "READING_SPEED_NORMS",
    "READING_SPEED_WPM",
    "ReadabilityStats",
    "SMOG_COMPLEX_SYL_FACTOR",
    "SentsExtractor",
    "WordsExtractor",
    "calc_automated_readability_index",
    "calc_coleman_liau_index",
    "calc_flesch_kincaid_grade",
    "calc_flesch_reading_easy",
    "calc_reading_time",
    "calc_smog_index",
    "collocations",
    "count_punctuations",
    "dendrogram_plot",
    "dispersion",
    "dispersion_plot",
    "fingerprinting",
    "frequency_spectrum_plot",
    "get_doc_words",
    "grade_to_age",
    "heaps_plot",
    "keyness",
    "keyness_plot",
    "kwic",
    "mds_plot",
    "mendenhall_plot",
    "pca_plot",
    "sentence_lengths",
    "sentence_lengths_plot",
    "substring_filter",
    "wordtree",
    "zipf",
    "zipf_theory",
}


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
        ):
            continue
        own = getattr(library_module, name)
        if name in RUSSIAN:
            assert own is not value, name
            assert not isinstance(value, type) or issubclass(own, value), name
        else:
            assert own is value, name
