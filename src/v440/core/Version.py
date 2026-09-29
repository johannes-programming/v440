"""Provide the central Version class for mutable PEP 440 versions."""

from __future__ import annotations

__all__: list[str] = ["Version"]

from collections import abc
from dataclasses import dataclass
from typing import Any, Final, Self

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

    def _deformat(self: Self, spec: str, /) -> VersionAccumulation:
        body: str
        leading: str
        local: str
        public: str
        trailing: str
        body = spec.strip()
        leading, trailing = spec.split(body)
        public, local = split_version(body)
        return VersionAccumulation(
            leading=White(leading),
            public=self.public._deformat(public),
            local=self.local._deformat(local),
            trailing=White(trailing),
        )

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        return tuple(split_version(spec))

    def _format_parsed(self: Self, parsed: tuple[Any, ...], /) -> str:
        public_f: str
        local_f: str
        public_f, local_f = parsed
        return join_version(
            format(self.public, public_f),
            format(self.local, local_f),
        )

    @classmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]:
        return dict(_public=Public_, _local=Local_)

    def _string_fset(self: Self, value: str, /) -> None:
        self.public.string, self.local.string = split_version(value.strip())

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


class White(str):
    def best(self: Self, /) -> str:
        return self

    def intersection(self: Self, other: Self, /) -> Self:
        if self == other:
            return self
        else:
            raise ArithmeticError


@dataclass(frozen=True, kw_only=True)
class VersionAccumulation:
    leading: White
    local: LocalAccumulation
    public: PublicAccumulation
    trailing: White

    def best(self: Self, /) -> str:
        joined: str
        local: str
        public: str
        public = self.public.best()
        local = self.local.best()
        joined = join_version(public, local)
        if joined:
            return self.leading + joined + self.trailing
        if self.leading or self.trailing:
            return self.leading + "#" + self.trailing
        return ""

    def intersection(self: Self, other: Self, /) -> Self:
        return type(self)(
            leading=self.leading.intersection(other.leading),
            public=self.public.intersection(other.public),
            local=self.local.intersection(other.local),
            trailing=self.trailing.intersection(other.trailing),
        )


def join_version(public: str, local: str = "") -> str:
    if local:
        return public + "+" + local
    else:
        return public


def split_version(string: str, /) -> abc.Iterable[str]:
    if string.endswith("+"):
        raise ValueError
    if "+" in string:
        return string.split("+")
    else:
        return string, ""
