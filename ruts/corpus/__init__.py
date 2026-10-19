from typing import TYPE_CHECKING

from anyts.utils import make_lazy

if TYPE_CHECKING:
    from .collocations import Collocation, collocations
    from .compare import (
        bootstrap_median_diff,
        calc_cliff_delta,
        calc_cohen_d,
        check_comparison_params,
        compare_corpora,
        compare_features,
        corpus_features,
        holm_correction,
        sentence_rhythm,
        split_windows,
        text_features,
    )
    from .dispersion import Dispersion, dispersion
    from .keyness import FrequencyReference, Keyword, check_keyness_params, keyness
    from .kwic import Concordance, format_kwic, kwic, print_kwic
    from .stylometry import (
        ZetaScore,
        delta,
        delta_profiles,
        frequency_table,
        function_words_profile,
        kilgarriff_chi2,
        mendenhall_curve,
        mendenhall_distance,
        z_scores,
        zeta,
    )

# Модуль каждого имени, импорт при первом обращении: конкорданс не грузит pandas и SciPy
_MODULES = {
    "Collocation": "collocations",
    "Concordance": "kwic",
    "Dispersion": "dispersion",
    "FrequencyReference": "keyness",
    "Keyword": "keyness",
    "ZetaScore": "stylometry",
    "bootstrap_median_diff": "compare",
    "calc_cliff_delta": "compare",
    "calc_cohen_d": "compare",
    "check_comparison_params": "compare",
    "check_keyness_params": "keyness",
    "collocations": "collocations",
    "compare_corpora": "compare",
    "compare_features": "compare",
    "corpus_features": "compare",
    "delta": "stylometry",
    "delta_profiles": "stylometry",
    "dispersion": "dispersion",
    "format_kwic": "kwic",
    "frequency_table": "stylometry",
    "function_words_profile": "stylometry",
    "holm_correction": "compare",
    "keyness": "keyness",
    "kilgarriff_chi2": "stylometry",
    "kwic": "kwic",
    "mendenhall_curve": "stylometry",
    "mendenhall_distance": "stylometry",
    "print_kwic": "kwic",
    "sentence_rhythm": "compare",
    "split_windows": "compare",
    "text_features": "compare",
    "z_scores": "stylometry",
    "zeta": "stylometry",
}


__all__ = [
    "Collocation",
    "Concordance",
    "Dispersion",
    "FrequencyReference",
    "Keyword",
    "ZetaScore",
    "bootstrap_median_diff",
    "calc_cliff_delta",
    "calc_cohen_d",
    "check_comparison_params",
    "check_keyness_params",
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
]

make_lazy(__name__, _MODULES)
