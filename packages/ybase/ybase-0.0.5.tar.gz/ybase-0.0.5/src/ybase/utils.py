from typing import Any


async def as_tree(obj: Any) -> dict | list:
    """
    Convert an object to a tree structure.
    """
    if hasattr(obj, "as_tree"):
        return await obj.as_tree()

    match obj:
        case dict() | list() | tuple() | set() | int() | float() | str() | bool():
            return obj
        case _:
            return str(obj)

