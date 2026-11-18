from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from typing import TYPE_CHECKING, cast

from anyts.corpus.stylometry import (
    ZetaScore as ZetaScore,
    delta as delta,
    delta_profiles as delta_profiles,
    frequency_table as frequency_table,
    kilgarriff_chi2 as kilgarriff_chi2,
    mendenhall_curve as mendenhall_curve,
    mendenhall_distance as mendenhall_distance,
    rolling_delta as rolling_delta,
    z_scores as z_scores,
    zeta as zeta,
    zeta_segments as zeta_segments,
)
from anyts.document import get_tree
from anyts.utils import check_words, has_words, is_doc, is_document, is_punctuation

from ..constants import FUNCTION_UD_POS
from ..exceptions import SourceError
from ..utils import get_document, parse_word

if TYPE_CHECKING:
    from anyseg import Document
    from spacy.tokens import Doc


def function_words_profile(source: Sequence[str] | Doc | Document) -> dict[str, float]:
    """
    Вычисление профиля служебных слов - долей служебных частей речи

    Описание:
        Доли предлогов, сочинительных и подчинительных союзов, частиц, местоимений,
        детерминативов и междометий (FUNCTION_UD_POS) среди слов текста без знаков
        препинания; части речи - из разметки Doc или Document, без нее - по первому разбору
        ruMorph

    Аргументы:
        source (list[str]|Doc|Document): Слова текста, объект Doc или Document

    Вывод:
        dict[str, float]: Доли по частям речи из FUNCTION_UD_POS

    Исключения:
        SourceTypeError: Если слова не список строк
        SourceError: Если слов нет
    """
    if is_doc(source) or is_document(source):
        tree_words = [
            word for word in get_tree(get_document(source)).words if has_words(word.form)
        ]
        tagged = any(word.upos for word in tree_words)
        tags = [word.upos if tagged else _word_pos(word.form) for word in tree_words]
    else:
        words = cast("Sequence[str]", source)
        check_words(words)
        tags = [_word_pos(word) for word in words if not is_punctuation(word)]
    if not tags:
        raise SourceError("В источнике данных отсутствуют слова")
    counts = Counter(tags)
    return {pos: counts[pos] / len(tags) for pos in FUNCTION_UD_POS}


def _word_pos(word: str) -> str | None:
    return parse_word(word).pos
