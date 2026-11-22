from anyts.visualizers.verse import rhythm_plot as core_rhythm_plot

from ._labels import with_russian_labels

rhythm_plot = with_russian_labels(core_rhythm_plot)
