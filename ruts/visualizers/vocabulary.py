from anyts.visualizers.vocabulary import (
    frequency_spectrum_plot as core_frequency_spectrum_plot,
    heaps_plot as core_heaps_plot,
)

from ._labels import with_russian_labels

heaps_plot = with_russian_labels(core_heaps_plot)
frequency_spectrum_plot = with_russian_labels(core_frequency_spectrum_plot)
