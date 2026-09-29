"""Provide the central Version class for mutable PEP 440 versions."""

from __future__ import annotations

__all__: list[str] = ["Version"]

from dataclasses import dataclass
from typing import Any, Final, NamedTuple, Self

import packaging.version

from v440._utils.setter import setter
from v440.abc.NestedABC import NestedABC
from v440.core.Local import Local as Local_
from v440.core.Local import LocalAccumulation
from v440.core.Public import Public as Public_
from v440.core.Public import PublicAccumulation


class Version(NestedABC):

    Public: Final[type[Public_]] = Public_
    Local: Final[type[Local_]] = Local_
    _public: Public_
    _local: Local_

    __slots__ = ("_public", "_local")

    def _cmp(self: Self, /) -> tuple[Public_, Local_]:
        return self.public, self.local

    def _deformat(self: Self, string: str, /) -> VersionAccumulation:
        split: VersionSplit
        split = VersionSplit.by_string(string)
        return VersionAccumulation(
            leading=split.leading,
            public=self.public._deformat(split.public),
            local=self.local._deformat(split.local),
            trailing=split.trailing,
        )

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        return (VersionSplit.by_string(spec),)

    def _format_parsed(self: Self, split: VersionSplit, /) -> str:
        local: str
        local = format(self.local, split.local)
        if local:
            local = "+" + local
        return (
            split.leading
            + format(self.public, split.public)
            + local
            + split.trailing
        )

    @classmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]:
        return dict(_public=Public_, _local=Local_)

    def _string_fset(self: Self, value: str, /) -> None:
        stripped: str
        stripped = value.strip()
        if stripped.endswith("+"):
            raise ValueError
        if "+" in stripped:
            self.public.string, self.local.string = stripped.split("+")
        else:
            self.public.string = stripped
            self.local.string = ""

    def _todict(self: Self, /) -> dict[str, Any]:
        return dict(public=self.public, local=self.local)

    @property
    def local(self: Self, /) -> Local_:
        "This property represents the local identifier."
        return self._local

    @local.setter
    @setter
    def local(self: Self, value: object, /) -> None:
        self.local.string = value

    @property
    def packaging(self: Self, /) -> packaging.version.Version:
        "This method returns an eqivalent packaging.version.Version object."
        return packaging.version.Version(str(self))

    @packaging.setter
    @setter
    def packaging(self: Self, value: object, /) -> None:
        self.string = value

    @property
    def public(self: Self, /) -> Public_:
        "This property represents the public identifier."
        return self._public

    @public.setter
    @setter
    def public(self: Self, value: object, /) -> None:
        self.public.string = value


@dataclass(frozen=True, kw_only=True)
class VersionAccumulation:
    leading: str
    public: PublicAccumulation
    local: LocalAccumulation
    trailing: str

    def best(self: Self, /) -> str:
        ans: str
        ans = self.local.best()
        if ans:
            ans = "+" + ans
        ans = self.public.best() + ans
        if ans or self.leading == self.trailing == "":
            return self.leading + ans + self.trailing
        else:
            return self.leading + "!" + self.trailing

    def intersection(self: Self, other: Self, /) -> Self:
        if self.leading != other.leading or self.trailing != other.trailing:
            raise ArithmeticError
        return type(self)(
            leading=self.leading,
            public=self.public.intersection(other.public),
            local=self.local.intersection(other.local),
            trailing=self.trailing,
        )


class VersionSplit(NamedTuple):
    leading: str
    public: str
    local: str
    trailing: str

    @classmethod
    def by_string(cls: type[Self], /, string: str) -> Self:
        leading: str
        local: str
        public: str
        stripped: str
        trailing: str
        if string == "":
            return cls("", "", "", "")
        stripped = string.strip()
        leading, trailing = string.split(stripped)
        if "+" in stripped:
            public, local = stripped.split("+")
        else:
            public = stripped
            local = ""
        return cls(
            leading=leading,
            public=public,
            local=local,
            trailing=trailing,
        )
