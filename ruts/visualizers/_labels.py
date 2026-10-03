import functools
import inspect
from collections.abc import Callable, Mapping, Sequence
from typing import Any, TypeVar, cast

from ..constants import VISUALIZER_LABELS

F = TypeVar("F", bound=Callable[..., Any])


def russian_labels(name: str, labels: Any) -> Any:
    """
    Русские подписи графика с заданными поверх

    Аргументы:
        name (str): Название графика - ключ VISUALIZER_LABELS
        labels (dict[str, str]): Заданные подписи; пара подписей легенды keyness_plot

    Вывод:
        dict[str, str]: Подписи для функции ядра; неверные возвращаются как есть - их отвергает ядро
    """
    if name == "keyness_plot" and isinstance(labels, Sequence) and not isinstance(labels, str):
        if len(labels) != 2:
            return labels
        labels = {"target": labels[0], "reference": labels[1]}
    if labels is None:
        return dict(VISUALIZER_LABELS[name])
    if isinstance(labels, Mapping):
        return {**VISUALIZER_LABELS[name], **labels}
    return labels


def with_russian_labels(func: F) -> F:
    """
    Функция графика ядра с русскими подписями по умолчанию

    Аргументы:
        func (Callable): Функция графика ядра с параметром labels

    Вывод:
        Callable: Функция с той же сигнатурой
    """
    signature = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        bound = signature.bind(*args, **kwargs)
        bound.arguments["labels"] = russian_labels(func.__name__, bound.arguments.get("labels"))
        return func(*bound.args, **bound.kwargs)

    return cast(F, wrapper)
