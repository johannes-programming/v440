"""Provide the Clue helper class for version de/formatting in v440."""

__all__: list[str] = ["Clue"]

from dataclasses import dataclass
from typing import Self

from v440._utils.Cfg import Cfg


@dataclass(frozen=True, kw_only=True)
class Clue:
    head: str = ""
    mag: int = 0

    def __and__(self: Self, other: Self, /) -> Self:
        m: int
        if self.head == "":
            return other
        if other.head == "":
            return self
        if self.head != other.head:
            raise ValueError
        if self.mag < 0 and other.mag < 0:
            m = max(self.mag, other.mag)
        elif self.mag < 0 or other.mag < 0:
            if 0 < self.mag + other.mag:
                raise ValueError
            m = max(self.mag, other.mag)
        else:
            if self.mag != other.mag:
                raise ValueError
            m = self.mag
        return type(self)(head=self.head, mag=m)

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

    def possible(self: Self, /, *, hollow: str, short: str) -> set[str]:
        n: str
        nums: set[str]
        ans: set[str]
        ans = set()
        if self.head == "":
            ans.add("")
            ans.add(short + "#")
            return ans
        if self.mag < 0:
            nums = {"", "#"}
        else:
            nums = {"#" * self.mag}
        ans = set()
        for n in nums:
            ans.add(self.head + n)
        if (hollow + "#") in ans:
            ans.add("")
        return ans

    def seal(self: Self, /) -> Self:
        mag: int
        mag = self.mag if self.mag >= -1 else -1
        return type(self)(head=self.head, mag=mag)

    def solo(self: Self, /, hollow: str) -> str:
        mag: int
        if self.head == "":
            return ""
        mag = self.mag if self.mag >= -1 else -1
        if self.head == hollow and mag in (-1, 1):
            return ""
        return self.head + max(0, mag) * "#"
