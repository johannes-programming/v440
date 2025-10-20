from __future__ import annotations

import operator
from typing import *

import setdoc

from v440._utils import forms
from v440._utils.Cfg import Cfg
from v440._utils.guarding import guard
from v440._utils.SlotStringer import SlotStringer
from v440.core.Release import Release

__all__ = ["Base"]


class Base(SlotStringer):

    __slots__ = ("_epoch", "_release")

    string: str
    packaging: str
    epoch: int
    release: Release

    @setdoc.basic
    def __init__(self: Self, string: Any = "0") -> None:
        self._epoch = 0
        self._release = Release()
        self.string = string

    def _cmp(self: Self) -> tuple:
        return self.epoch, self.release

    @classmethod
    def _deformat(cls: type, info: dict[str, Self], /) -> str:
        table: dict = dict()
        table["basev"] = set()
        table["epoch"] = set()
        table["release"] = set()
        matches: dict
        s: str
        t: str
        for s in info.keys():
            matches = Cfg.fullmatches("base", s)
            for t in ("basev", "epoch", "release"):
                table[t].add(forms.none_empty(matches, t))
        s = cls._deformat_basev(table["basev"])
        s += cls._deformat_epoch(table["epoch"])
        s += Release.deformat(*table["release"])
        return s

    @classmethod
    def _deformat_basev(cls: type, table: set) -> str:
        if len(table) <= 1:
            return next(iter(table), "")
        raise ValueError

    @classmethod
    def _deformat_epoch(cls: type, table: set[str]) -> str:
        data: set = set(len(x) for x in table if x.startswith("0") or x == "")
        if data == set() or data == {0}:
            return ""
        if data == {1}:
            return "!"
        if len(data) == 1:
            return "#" * data.pop() + "!"
        raise ValueError

    @classmethod
    def _format_parse(cls: type, spec: str, /) -> dict:
        p: str
        y: str
        if spec[:1] in tuple("Vv"):
            p = spec[0]
            y = spec[1:]
        else:
            p = ""
            y = spec
        x: str = ""
        if "!" in y:
            x, y = y.split("!")
            if x == "":
                x = "#"
            elif x.strip("#"):
                raise ValueError
        ans: dict = dict(prefix=p, epoch_n=len(x), release_f=y)
        return ans

    def _format_parsed(self: Self, *, prefix: str, epoch_n: int, release_f: str) -> str:
        ans: str = prefix
        if epoch_n or self.epoch:
            ans += format(self.epoch, "0%sd" % epoch_n)
            ans += "!"
        ans += format(self.release, release_f)
        return ans

    def _string_fset(self: Self, value: str) -> None:
        matches: dict = Cfg.fullmatches("base", value)
        if matches["epoch"] is None:
            self.epoch = 0
        else:
            self.epoch = int(matches["epoch"])
        self.release.string = matches["release"]

    def _todict(self: Self) -> dict:
        return dict(epoch=self.epoch, release=self.release)

    @property
    def epoch(self: Self) -> int:
        "This property represents the epoch."
        return self._epoch

    @epoch.setter
    @guard
    def epoch(self: Self, value: Any) -> None:
        v: int = operator.index(value)
        if v < 0:
            raise ValueError
        self._epoch = v

    @property
    def release(self: Self) -> Release:
        "This property represents the release."
        return self._release
