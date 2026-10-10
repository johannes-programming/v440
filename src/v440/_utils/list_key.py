from __future__ import annotations

__all__: list[str] = ["list_key"]


def list_key(item: int | str, /) -> tuple[bool, int | str]:
    """Return key for sorting int before str in Local."""
    return isinstance(item, int), item
