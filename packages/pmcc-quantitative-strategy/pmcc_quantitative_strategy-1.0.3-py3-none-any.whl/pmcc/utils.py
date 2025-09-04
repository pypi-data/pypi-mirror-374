from __future__ import annotations

from typing import TypeGuard


def is_number(x: object) -> TypeGuard[float | int]:
    """Return True for int/float but not bool (bool is a subclass of int).

    This mirrors the local helper patterns used across modules, centralized here
    for consistency.
    """
    return isinstance(x, (int, float)) and not isinstance(x, bool)  # noqa: UP038
