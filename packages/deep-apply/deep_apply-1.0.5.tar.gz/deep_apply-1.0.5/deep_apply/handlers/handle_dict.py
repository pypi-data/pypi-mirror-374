from typing import Callable

from deep_apply import helpers


def handle_dict(apply: Callable, **kwargs) -> dict:
    """
    Handle dict.
    """

    data = kwargs["data"]
    depth_key: str | None = kwargs.get("depth_key")
    depth_level: int = kwargs.get("depth_level")

    for key, value in data.items():
        kwargs["key"] = key
        kwargs["data"] = value
        kwargs["depth_key"] = helpers.add_key_to_depth_key(key=key, depth_key=depth_key)
        kwargs["depth_level"] = depth_level + 1
        data[key] = apply(
            **kwargs,
        )

    return data
