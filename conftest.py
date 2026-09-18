from doctest import UnexpectedException

import pytest
from _pytest.doctest import DoctestItem, MultipleDoctestFailures

from ruts.exceptions import DatasetNotFoundError


def _needs_dataset(error: BaseException) -> bool:
    failures = error.failures if isinstance(error, MultipleDoctestFailures) else [error]
    return any(
        isinstance(failure, UnexpectedException)
        and isinstance(failure.exc_info[1], DatasetNotFoundError)
        for failure in failures
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Пример в докстринге, упавший из-за незагруженного набора данных, считается пропущенным
    """
    outcome = yield
    report = outcome.get_result()
    if (
        isinstance(item, DoctestItem)
        and call.when == "call"
        and call.excinfo is not None
        and _needs_dataset(call.excinfo.value)
    ):
        report.outcome = "skipped"
        report.longrepr = (str(item.path), item.reportinfo()[1], "набор данных не загружен")
