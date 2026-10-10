from __future__ import annotations

__all__: list[str] = ["lower_ascii"]
TABLE: dict[int, int] = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "abcdefghijklmnopqrstuvwxyz",
)


def lower_ascii(value: str, /) -> str:
    return value.translate(TABLE)
