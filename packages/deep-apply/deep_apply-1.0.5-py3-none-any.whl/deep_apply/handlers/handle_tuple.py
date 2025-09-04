from typing import Callable


def handle_tuple(apply: Callable, **kwargs) -> tuple:
    """
    Handle tuple.
    """

    data = kwargs["data"]
    depth_level: int = kwargs["depth_level"]

    data = list(data)

    for index, value in enumerate(data):
        kwargs["data"] = value
        kwargs["depth_level"] = depth_level + 1
        data[index] = apply(
            **kwargs,
        )

    data = tuple(data)

    return data
