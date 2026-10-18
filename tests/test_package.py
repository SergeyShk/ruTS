import importlib
import subprocess
import sys
from types import ModuleType

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
    "ruts.components": {"BasicStats", "ReadabilityStats"},
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
    "ruts.visualizers.highlight": {"HighlightedText", "find_phrases", "get_doc_words"},
}


# Копии механики ядра до переезда классов на каркасы anyTS 0.3: каждый PR 0.18 убирает свои
PENDING = {
    "ruts.components": {
        "BasicStatsComponent",
        "CohesionStats",
        "CohesionStatsComponent",
        "DiversityStatsComponent",
        "LexicalStats",
        "LexicalStatsComponent",
        "PhonStats",
        "PhonStatsComponent",
        "ReadabilityStatsComponent",
        "StyleStats",
        "StyleStatsComponent",
        "SyntaxStats",
        "SyntaxStatsComponent",
        "check_diversity_params",
        "check_phon_params",
        "check_style_params",
        "is_number",
    },
    "ruts.visualizers.highlight": {
        "ALLITERATION_THRESHOLD",
        "calc_alliteration_runs",
        "find_alliteration",
        "find_complex_words",
        "find_connector_highlights",
        "find_long_sents",
        "find_phrase_highlights",
        "find_split_predicate_highlights",
    },
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
    with pytest.raises(ruts.SourceTypeError, match=r"^Некорректный источник данных$"):
        getattr(ruts, name)(5)


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


def test_new_core_message_does_not_break_import():
    """Ключ, добавленный патчем ядра, выходит по-английски, а импорт ruTS работает"""
    code = (
        "import anyts.constants as core;"
        "core.MESSAGES['new_key'] = 'New message';"
        "import ruts;"
        "print(ruts.BasicStats.messages['new_key'])"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    assert result.stdout.strip() == "New message"


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
