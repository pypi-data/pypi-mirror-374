from typing import Callable


def handle_set(apply: Callable, **kwargs) -> set:
    """
    Handle set.

    The set values will not be modified with the apply function.
    """

    data = kwargs["data"]
    depth_level: int = kwargs.get("depth_level")

    data = list(data)

    for index, value in enumerate(data):
        kwargs["data"] = value
        kwargs["depth_level"] = depth_level + 1
        data[index] = apply(
            **kwargs,
        )

    data = set(data)

    return data
