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
from v440.core.Public import Public as Public_


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


@dataclass(frozen=True, kw_only=True)
class VersionAccumulation:
    locals: frozenset[str]
    publics: frozenset[str]

    def __and__(self: Self, other: Self, /) -> Self:
        return type(self)(
            locals=self.locals | other.locals,
            publics=self.publics | other.publics,
        )

    def best(self: Self, /, *, forbids_empty: bool = False) -> str:
        ans: str
        public: str
        local: str
        public = Public_.deformat(*self.publics)
        local = Local_.deformat(*self.locals)
        ans = join_version(public, local)
        if forbids_empty and not ans:
            return "#"
        return ans


class Version(NestedABC):

    Public: Final[type[Public_]] = Public_
    Local: Final[type[Local_]] = Local_
    _public: Public_
    _local: Local_

    __slots__ = ("_public", "_local")

    def _cmp(self: Self, /) -> tuple[Public_, Local_]:
        return self.public, self.local

    def _deformat(self: Self, body: str, /) -> VersionAccumulation:
        local: str
        public: str
        public, local = split_version(body)
        return VersionAccumulation(
            locals=frozenset({local}),
            publics=frozenset({public}),
        )

    @staticmethod
    def _deformat_origin() -> VersionAccumulation:
        return VersionAccumulation(
            locals=frozenset(),
            publics=frozenset(),
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
        self.public.string, self.local.string = split_version(value)

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
