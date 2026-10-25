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
from anyts.utils import check_words, is_doc, is_punctuation, iter_doc_units

from ..constants import FUNCTION_UD_POS
from ..exceptions import SourceError
from ..morph_stats import tag_to_ud_pos
from ..utils import parse_word

if TYPE_CHECKING:
    from spacy.tokens import Doc


def function_words_profile(source: Sequence[str] | Doc) -> dict[str, float]:
    """
    Вычисление профиля служебных слов - долей служебных частей речи

    Описание:
        Доли предлогов, сочинительных и подчинительных союзов, частиц, местоимений,
        детерминативов и междометий (FUNCTION_UD_POS) среди слов текста; по первому
        разбору pymorphy3 для списка слов и по разметке для Doc с частями речи,
        знаки препинания в обоих случаях не считаются словами.
        Служебные слова не зависят от темы текста, поэтому их профиль -
        классический признак авторства

    Аргументы:
        source (list[str]|Doc): Слова текста или объект Doc

    Вывод:
        dict[str, float]: Доли по частям речи из FUNCTION_UD_POS

    Исключения:
        SourceTypeError: Если слова не список строк
        SourceError: Если слов нет
    """
    if is_doc(source):
        units = list(iter_doc_units(source, join_hyphens=True))
        tagged = source.has_annotation("POS")
        tags = [
            unit[0].pos_ if tagged and len(unit) == 1 else _word_pos("".join(t.text for t in unit))
            for unit in units
        ]
    else:
        words = cast("Sequence[str]", source)
        check_words(words)
        tags = [_word_pos(word) for word in words if not is_punctuation(word)]
    if not tags:
        raise SourceError("В источнике данных отсутствуют слова")
    counts = Counter(tags)
    return {pos: counts[pos] / len(tags) for pos in FUNCTION_UD_POS}


def _word_pos(word: str) -> str | None:
    parse = parse_word(word)
    return tag_to_ud_pos(parse.tag, parse.normal_form, word)
