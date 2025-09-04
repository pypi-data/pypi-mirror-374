import importlib
from typing import Any

try:
    pydantic = importlib.import_module("pydantic")
except ModuleNotFoundError:
    pydantic = None


def is_dict(data: Any) -> bool:
    """
    Check if data type is dict.
    """

    return isinstance(data, dict)


def is_list(data: Any) -> bool:
    """
    Check if data type is list.
    """

    return isinstance(data, list)


def is_set(data: Any) -> bool:
    """
    Check if data type is set.
    """

    return isinstance(data, set)


def is_tuple(data: Any) -> bool:
    """
    Check if data type is tuple.
    """

    return isinstance(data, tuple)


def is_pydantic_model(data: Any) -> bool:
    """
    Check if data is a pydantic model.
    """

    if not pydantic:
        return False

    return isinstance(data, pydantic.BaseModel)
