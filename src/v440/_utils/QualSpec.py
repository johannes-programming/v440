import string as string_
from typing import *
from v440._utils.Cfg import Cfg


class QualSpec(NamedTuple):
    head: str
    mag: int

    def __and__(self: Self, other: Self) -> Self:
        if self.head == "":
            return other
        if other.head == "":
            return self
        h: str
        if self.head == other.head:
            h = self.head
        elif self.head[:-1] == other.head and self.head[-1] in ".-_":
            h = self.head
        elif other.head[:-1] == self.head and other.head[-1] in ".-_":
            h = other.head
        else:
            raise ValueError
        m: int = min(self.mag, other.mag)
        n: int = max(self.mag, other.mag)
        if 0 < m + n < n:
            raise ValueError
        if 0 <= m < n:
            raise ValueError
        return type(self)(h, n)

    @classmethod
    def by_example(cls: type, value: str, /) -> Self:
        x: str = value.rstrip(string_.digits)
        y: str = value[len(x) :]
        if y.startswith("0"):
            return cls(x, len(y))
        else:
            return cls(x, -len(y))

    @classmethod
    def by_examples(cls: type, *values: str) -> Self:
        ans: Self = cls("", 0)
        s: str
        for s in values:
            ans &= cls.by_string(s)
        return ans

    @classmethod
    def by_spec(cls: type, value: str, /) -> Self:
        x: str = value.rstrip("#")
        ans: Self = cls(x, len(value) - len(x))
        return ans

    def options(
            self: Self, 
            *, 
            hollow: str, 
            short: str, 
    ) -> set:
        s:str
        ans: set = set()
        if self.head == "":
            ans.add("")
            for s in Cfg.cfg.data["consts"]["short"]:
                ans.add(s % short)
            return ans
        if self.head == hollow and (self.mag < 0 or self.mag == 1):
            ans.add("")
        if self.mag < 0:
            ans.add(self.head)
            ans.add(self.head + "#")
        else:
            ans.add(self.head + self.mag * "#")
        return ans
