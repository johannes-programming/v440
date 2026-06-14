from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Final, Self

import packaging.version

from v440.abc.NestedABC import NestedABC
from v440.core.Local import Local as Local_
from v440.core.Public import Public as Public_

__all__ = ["Version"]


class Version(NestedABC):

    Public: Final[type[Public_]] = Public_
    Local: Final[type[Local_]] = Local_
    _public: Public_
    _local: Local_

    __slots__ = ("_public", "_local")

    def _cmp(self: Self) -> tuple[Public_, Local_]:
        return self.public, self.local

    @classmethod
    def _deformat(cls: type[Self], info: dict[Any, Any], /) -> str:
        publics: set[str]
        locals_: set[str]
        x: str
        y: str
        publics = set()
        locals_ = set()
        for x, y in map(cls._split, info.keys()):
            publics.add(x)
            locals_.add(y)
        x = Public_.deformat(*publics)
        y = Local_.deformat(*locals_)
        return cls._join(x, y)

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        return tuple(cls._split(spec))

    def _format_parsed(self: Self, parsed: tuple[Any, ...], /) -> str:
        public_f: str
        local_f: str
        public_f, local_f = parsed
        return self._join(
            format(self.public, public_f),
            format(self.local, local_f),
        )

    @classmethod
    def _init_factories(cls: type[Self]) -> dict[str, Any]:
        return dict(_public=Public_, _local=Local_)

    @classmethod
    def _join(cls: type[Self], public: str, local: str = "") -> str:
        if local:
            return public + "+" + local
        else:
            return public

    def _string_fset(self: Self, value: str) -> None:
        self.public.string, self.local.string = self._split(value)

    @classmethod
    def _split(cls: type[Self], string: str, /) -> Iterable[str]:
        if string.endswith("+"):
            raise ValueError
        if "+" in string:
            return string.split("+")
        else:
            return string, ""

    def _todict(self: Self) -> dict[str, Any]:
        return dict(public=self.public, local=self.local)

    @property
    def local(self: Self) -> Local_:
        "This property represents the local identifier."
        return self._local

    @local.setter
    def local(self: Self, value: object, /) -> None:
        self.local.string = value

    @property
    def packaging(self: Self) -> packaging.version.Version:
        "This method returns an eqivalent packaging.version.Version object."
        return packaging.version.Version(str(self))

    @packaging.setter
    def packaging(self: Self, value: object) -> None:
        self.string = value

    @property
    def public(self: Self) -> Public_:
        "This property represents the public identifier."
        return self._public

    @public.setter
    def public(self: Self, value: object, /) -> None:
        self.public.string = value
