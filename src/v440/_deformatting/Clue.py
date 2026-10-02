"""Provide the Clue helper class for version de/formatting in v440."""

__all__: list[str] = ["Clue"]

from dataclasses import dataclass
from typing import Self

from v440._utils.Cfg import Cfg

from .Mag import Mag


@dataclass(frozen=True, kw_only=True)
class BaseClue:
    head: str = ""
    mag: Mag = Mag()

    def union(self: Self, other: Self, /) -> Self:
        if self.head == "":
            return other
        if other.head == "":
            return self
        if self.head != other.head:
            raise ValueError
        return type(self)(
            head=self.head,
            mag=self.mag.union(other.mag),
        )


class Clue(BaseClue):

    def __init__(self: Self, /, *, head: str = "", mag: int = 0) -> None:
        super().__init__(head=head, mag=Mag(mag))

    @classmethod
    def by_example(cls: type[Self], value: str, /) -> Self:
        mag: int
        matches: dict[str, str]
        if value == "-0":
            return cls(head="-", mag=-1)
        matches = Cfg.fullmatches("clue", value)
        if matches["num"].startswith("0"):
            mag = len(matches["num"])
        else:
            mag = -len(matches["num"])
        return cls(head=matches["head"], mag=mag)

    @classmethod
    def by_spec(cls: type[Self], value: str, /) -> Self:
        matches: dict[str, str]
        matches = Cfg.fullmatches("clue_f", value)
        return cls(head=matches["head_f"], mag=len(matches["num_f"]))

    def possible(self: Self, /, *shorts: str, hollow: str) -> set[str]:
        ans: set[str]
        short: str
        if self.head:
            if self.mag < 0:
                ans = {self.head, self.head + "#"}
            else:
                ans = {self.head + "#" * self.mag}
            if (hollow + "#") in ans:
                ans.add("")
            return ans
        else:
            ans = {""}
            for short in shorts:
                ans.add(short)
                ans.add(short + "#")
            return ans
