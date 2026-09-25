"""Provide the Dev class for developmental releases in v440."""

from __future__ import annotations

__all__: list[str] = ["Dev"]

import operator
from collections import abc
from dataclasses import dataclass
from typing import Any, Self, SupportsIndex

from datarepr import oxford

from v440._utils.Cfg import Cfg
from v440._utils.Clue import Clue
from v440._utils.setter import setter
from v440.abc.QualABC import QualABC
from v440.errors.VersionError import VersionError


@dataclass
class DevDeformat:
    clue: Clue
    info: dict[str, Dev]

    def best(self: Self, /) -> str:
        return self.clue.solo(".dev")

    def intersection_update(self: Self, other: Self, /) -> None:
        self.clue &= other.clue
        self.info.update(other.info)


class Dev(QualABC):

    __slots__ = ()

    def _cmp(self: Self, /) -> tuple[int] | tuple[int, int]:
        if self.lit:
            return 0, self.num
        else:
            return (1,)

    @staticmethod
    def _deformat(body: str | None = None, /) -> DevDeformat:
        if body is None:
            return DevDeformat(
                info=dict(),
                clue=Clue(),
            )
        else:
            return DevDeformat(
                info={body: Dev(body)},
                clue=Clue.by_example(body),
            )

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        clue: Clue
        matches: dict[str, str]
        matches = Cfg.fullmatches("dev_f", spec)
        clue = Clue(
            matches["dev_head_f"],
            matches["dev_sep_f"],
            len(matches["dev_num_f"]),
        )
        return (clue,)

    def _format_parsed(self: Self, parsed: tuple[Any, ...], /) -> str:
        clue: Clue
        (clue,) = parsed
        if not self:
            return ""
        if "" == clue.head:
            return ".dev" + str(self.num)
        if 0 == clue.mag and 0 == self.num:
            return clue.head
        return clue.head + clue.sep + format(self.num, f"0{clue.mag}d")

    @classmethod
    def _lit_parse(cls: type[Self], value: str, /) -> str:
        if value == "dev":
            return "dev"
        else:
            raise ValueError

    @classmethod
    def deformat(cls: type[Self], /, *strings: object) -> str:
        x: DevDeformat | None
        x = cls._deformat()
        for flat in set(map(str, strings)):
            try:
                x.intersection_update(cls._deformat(flat))
            except Exception:
                msg = Cfg.cfg.data["consts"]["errors"]["deformat"]
                msg %= oxford(*strings)
                raise VersionError(msg)
        return x.best()

    @property
    def packaging(self: Self, /) -> int | None:
        if self:
            return self.num
        else:
            return None

    @packaging.setter
    @setter
    def packaging(self: Self, value: SupportsIndex | None, /) -> None:
        if value is None:
            self.num = 0
            self.lit = ""
        else:
            self.lit = "dev"
            self.num = operator.index(value)
