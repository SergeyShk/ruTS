from anyts.corpus.collocations import (
    Collocation as Collocation,
    calc_dice as calc_dice,
    calc_log_likelihood as calc_log_likelihood,
    calc_logdice as calc_logdice,
    calc_mi as calc_mi,
    calc_mi3 as calc_mi3,
    calc_min_sensitivity as calc_min_sensitivity,
    calc_npmi as calc_npmi,
    calc_t_score as calc_t_score,
    collocations as core_collocations,
)

from ..utils import with_stripped_marks

collocations = with_stripped_marks(core_collocations, "node")
