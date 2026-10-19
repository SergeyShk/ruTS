from typing import TYPE_CHECKING

from anyts.utils import make_lazy

if TYPE_CHECKING:
    from .corpus import collocation_network, dispersion_plot, keyness_plot
    from .fingerprinting import fingerprinting
    from .highlight import Highlight, HighlightedText, highlight
    from .sentences import sentence_lengths, sentence_lengths_plot
    from .stylometry import dendrogram_plot, mds_plot, mendenhall_plot, pca_plot
    from .vocabulary import frequency_spectrum_plot, heaps_plot
    from .word_tree import wordtree
    from .zipf import zipf, zipf_theory

# Модуль каждого имени, импорт при первом обращении: подсветка не грузит matplotlib
_MODULES = {
    "Highlight": "highlight",
    "HighlightedText": "highlight",
    "collocation_network": "corpus",
    "dendrogram_plot": "stylometry",
    "dispersion_plot": "corpus",
    "fingerprinting": "fingerprinting",
    "frequency_spectrum_plot": "vocabulary",
    "heaps_plot": "vocabulary",
    "highlight": "highlight",
    "keyness_plot": "corpus",
    "mds_plot": "stylometry",
    "mendenhall_plot": "stylometry",
    "pca_plot": "stylometry",
    "sentence_lengths": "sentences",
    "sentence_lengths_plot": "sentences",
    "wordtree": "word_tree",
    "zipf": "zipf",
    "zipf_theory": "zipf",
}


__all__ = [
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
]

make_lazy(__name__, _MODULES)
