import importlib

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
