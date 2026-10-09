from anyts.visualizers.corpus import (
    collocation_network as collocation_network,
    dispersion_plot as core_dispersion_plot,
    keyness_plot as core_keyness_plot,
)

from ..utils import with_stripped_marks
from ._labels import with_russian_labels

dispersion_plot = with_russian_labels(
    with_stripped_marks(core_dispersion_plot, "words", "targets")
)
keyness_plot = with_russian_labels(core_keyness_plot)
