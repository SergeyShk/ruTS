from anyts.visualizers.zipf import zipf as core_zipf, zipf_theory as core_zipf_theory

from ._labels import with_russian_labels

zipf = with_russian_labels(core_zipf)
zipf_theory = with_russian_labels(core_zipf_theory)
