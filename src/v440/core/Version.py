from __future__ import annotations

from typing import *

import packaging.version
import setdoc

from v440._utils.guarding import guard
from v440._utils.SlotStringer import SlotStringer
from v440.core.Local import Local
from v440.core.Public import Public

__all__ = ["Version"]


class Version(SlotStringer):
    __slots__ = ("_public", "_local")

    string: str
    local: Local
    public: Public

    @setdoc.basic
    def __init__(self: Self, string: Any = "0") -> None:
        self._public = Public()
        self._local = Local()
        self.string = string

    def _cmp(self: Self) -> tuple:
        return self.public, self.local

    def _format(self: Self, spec: str, /) -> str:
        f: str
        g: str
        if "+" in spec:
            f, g = spec.split("+")
        else:
            f = spec
            g = ""
        f = format(self.public, f)
        g = format(self.local, g)
        if g:
            f = f + "+" + g
        return f

    def _string_fset(self: Self, value: str) -> None:
        if value.endswith("+"):
            raise ValueError
        if "+" not in value:
            self.public.string = value
            self.local.string = ""
            return
        self.public.string, self.local.string = value.split("+")

    def _todict(self: Self) -> dict:
        return dict(public=self.public, local=self.local)

    @property
    def local(self: Self) -> Local:
        "This property represents the local identifier."
        return self._local

    @property
    def packaging(self: Self) -> packaging.version.Version:
        "This method returns an eqivalent packaging.version.Version object."
        return packaging.version.Version(str(self))

    @packaging.setter
    @guard
    def packaging(self: Self, value: Any) -> None:
        self.string = value

    @property
    def public(self: Self) -> Public:
        "This property represents the public identifier."
        return self._public
