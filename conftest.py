import pytest
from _pytest.doctest import DoctestItem

from ruts.datasets.dataset import Dataset


@pytest.fixture(autouse=True)
def _skip_doctests_without_data(request):
    """
    Примеры в докстрингах наборов данных выполняются, только если набор загружен
    """
    item = request.node
    if not isinstance(item, DoctestItem) or not item.name.startswith("ruts.datasets."):
        return
    for value in item.dtest.globs.values():
        if (
            isinstance(value, type)
            and issubclass(value, Dataset)
            and value is not Dataset
            and value().filepath is None
        ):
            pytest.skip(f"набор данных {value.__name__} не загружен")
