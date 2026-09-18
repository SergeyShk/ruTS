import pytest
from _pytest.doctest import DoctestItem

from ruts.datasets.dataset import Dataset


@pytest.fixture(autouse=True)
def _skip_doctests_without_data(request):
    """
    Примеры в докстрингах, которым нужен набор данных, выполняются только при загруженном наборе
    """
    item = request.node
    if not isinstance(item, DoctestItem):
        return
    for value in item.dtest.globs.values():
        if (
            isinstance(value, type)
            and issubclass(value, Dataset)
            and value is not Dataset
            and value().filepath is None
        ):
            pytest.skip(f"набор данных {value.__name__} не загружен")
