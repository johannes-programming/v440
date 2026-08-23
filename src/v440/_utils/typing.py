__all__: list[str] = [
    "SupportsDunderGE",
    "SupportsDunderGT",
    "SupportsDunderLE",
    "SupportsDunderLT",
]

from typing import Any, Protocol


class SupportsDunderGE[Other, Return](Protocol):
    def __ge__(self: Any, other: Other, /) -> Return: ...
class SupportsDunderGT[Other, Return](Protocol):
    def __gt__(self: Any, other: Other, /) -> Return: ...
class SupportsDunderLE[Other, Return](Protocol):
    def __le__(self: Any, other: Other, /) -> Return: ...
class SupportsDunderLT[Other, Return](Protocol):
    def __lt__(self: Any, other: Other, /) -> Return: ...
