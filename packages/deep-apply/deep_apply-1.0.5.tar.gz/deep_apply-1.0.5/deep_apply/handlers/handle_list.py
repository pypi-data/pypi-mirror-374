from typing import Callable


def handle_list(apply: Callable, **kwargs) -> list:
    """
    Handle list.
    """

    data = kwargs["data"]
    depth_level: int = kwargs.get("depth_level")

    for index, value in enumerate(data):
        kwargs["data"] = value
        kwargs["depth_level"] = depth_level + 1
        data[index] = apply(
            **kwargs,
        )

    return data
