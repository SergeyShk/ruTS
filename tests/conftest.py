import pytest
from spacy.language import Language

from tests.pipelines import load_model_nlp, load_nlp


@pytest.fixture(scope="module")
def nlp() -> Language:
    return load_nlp()


@pytest.fixture(scope="module")
def model_nlp() -> Language:
    return load_model_nlp()
