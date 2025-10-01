from __future__ import annotations

from typing import *

import packaging.version
import setdoc
from overloadable import Overloadable

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
    def __bool__(self: Self) -> bool:
        return bool(self.local or self.public)

    @Overloadable
    @setdoc.basic
    def __init__(self: Self, *args: Any, **kwargs: Any) -> bool:
        if "string" in kwargs.keys():
            return True
        if len(args) <= 1 and len(kwargs) == 0:
            return True
        return False

    @__init__.overload(True)
    @setdoc.basic
    def __init__(self: Self, string: Any = "0") -> None:
        self._public = Public()
        self._local = Local()
        self.string = string

    @__init__.overload(False)
    @setdoc.basic
    def __init__(
        self: Self,
        public: Any = "0",
        local: Any = "",
    ) -> None:
        self._public = Public()
        self._local = Local()
        self.public.string = public
        self.local.string = local

    def _format(self: Self, format_spec: str) -> str:
        ans: str = format(self.public, format_spec)
        if self.local:
            ans += "+" + format(self.local)
        return ans

    def _string_fset(self: Self, value: str) -> None:
        parsed: Iterable
        if "+" in value:
            parsed = value.split("+")
        else:
            parsed = value, ""
        self.public.string, self.local.string = parsed

    def _todict(self: Self) -> dict:
        return dict(public=self.public, local=self.local)

    @property
    def local(self: Self) -> Local:
        "This property represents the local identifier."
        return self._local

    def packaging(self: Self) -> packaging.version.Version:
        "This method returns an eqivalent packaging.version.Version object."
        return packaging.version.Version(str(self))

    @property
    def public(self: Self) -> Self:
        "This property represents the public identifier."
        return self._public
