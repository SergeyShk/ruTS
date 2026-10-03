from anyts.visualizers.stylometry import (
    dendrogram_plot as core_dendrogram_plot,
    mds_plot as core_mds_plot,
    mendenhall_plot as core_mendenhall_plot,
    pca_plot as core_pca_plot,
)

from ._labels import with_russian_labels

dendrogram_plot = with_russian_labels(core_dendrogram_plot)
pca_plot = with_russian_labels(core_pca_plot)
mds_plot = with_russian_labels(core_mds_plot)
mendenhall_plot = with_russian_labels(core_mendenhall_plot)
