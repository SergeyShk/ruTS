"""Конвейеры spaCy для тестов Doc"""

from collections.abc import Sequence

import pytest
import spacy
from spacy.language import Language

from ruts import load_pipeline


def load_nlp(exclude: Sequence[str] = ()) -> Language:
    """Рекомендуемый конвейер load_pipeline: токены и предложения anySeg, морфология ruMorph"""
    pytest.importorskip("ru_core_news_sm")
    return load_pipeline(exclude=exclude)


def load_model_nlp(exclude: Sequence[str] = ()) -> Language:
    """Обычный ru_core_news_sm без лемматизатора: ему нужен pymorphy3"""
    pytest.importorskip("ru_core_news_sm")
    return spacy.load("ru_core_news_sm", exclude=["lemmatizer", *exclude])
