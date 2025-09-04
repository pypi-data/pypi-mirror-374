from deep_apply.types import TAllowedObjectTypes


def add_key_to_depth_key(key: str, depth_key: str | None) -> str:
    """
    Add key to depth key.

    :param key: The current key.
    :param depth_key: The current depth key.
    """

    if depth_key:
        new_depth_key = f"{depth_key}:{key}"
    else:
        new_depth_key = key

    return new_depth_key


def can_handle_object_type(
    allowed_types: list[TAllowedObjectTypes] | None,
    type_to_check: TAllowedObjectTypes,
) -> bool:
    """
    Check if object type is allowed to be handled.

    :param allowed_types: A list of types allowed.
    :param type_to_check: Tye type to check.
    """

    if (allowed_types is None) or (type_to_check in allowed_types):
        return True

    return False
