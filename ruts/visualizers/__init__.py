from .corpus import collocation_network, dispersion_plot, keyness_plot
from .fingerprinting import fingerprinting
from .highlight import Highlight, HighlightedText, highlight
from .sentences import sentence_lengths, sentence_lengths_plot
from .stylometry import dendrogram_plot, mds_plot, mendenhall_plot, pca_plot
from .vocabulary import frequency_spectrum_plot, heaps_plot
from .word_tree import wordtree
from .zipf import zipf, zipf_theory

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
