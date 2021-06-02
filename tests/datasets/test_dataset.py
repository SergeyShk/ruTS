import pytest

from ruts.datasets.dataset import Dataset


class TestErrorDataset(Dataset):
    def __init__(self, name, meta):
        super(TestErrorDataset, self).__init__(name, meta)


class TestDataset(Dataset):
    def __init__(self, name, meta):
        super(TestDataset, self).__init__(name, meta)

    def __iter__(self):
        super(TestDataset, self).__iter__()

    def check_data(self):
        super(TestDataset, self).check_data()

    def get_texts(self, *args):
        super(TestDataset, self).get_texts()

    def get_records(self, *args):
        super(TestDataset, self).get_records()

    def download(self):
        super(TestDataset, self).download()


@pytest.fixture(scope="module")
def dataset():
    dataset_ = TestDataset("test", {"a": 1, "b": 2})
    return dataset_


def test_iter_non_implement_error(dataset):
    with pytest.raises(NotImplementedError):
        dataset.__iter__()


def test_repr(dataset):
    assert dataset.__repr__() == "Набор данных('test')"


def test_info(dataset):
    assert list(dataset.info.keys()) == ["Наименование", "a", "b"]


def test_type_error():
    with pytest.raises(TypeError):
        TestErrorDataset("", {})


@pytest.mark.parametrize(
    "name", ["__iter__", "check_data", "get_texts", "get_records", "download"]
)
def test_methods(dataset, name):
    assert hasattr(dataset, name)
    with pytest.raises(NotImplementedError):
        getattr(dataset, name)()
