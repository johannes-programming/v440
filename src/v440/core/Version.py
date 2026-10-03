"""Provide the central Version class for mutable PEP 440 versions."""

from __future__ import annotations

__all__: list[str] = ["Version"]

from typing import Any, Final, NamedTuple, Self

import packaging.version

from v440._deformatting.VersionRestrictor import VersionRestrictor
from v440._utils.setter import setter
from v440.abc.NestedABC import NestedABC
from v440.core.Local import Local as Local_
from v440.core.Public import Public as Public_


class Version(NestedABC):
    """Represent Version."""

    Public: Final[type[Public_]] = Public_
    Local: Final[type[Local_]] = Local_
    _public: Public_
    _local: Local_

    __slots__ = ("_public", "_local")

    def _cmp(self: Self, /) -> tuple[Public_, Local_]:
        """Handle cmp."""
        return self.public, self.local

    def _deformat(self: Self, string: str, /) -> VersionRestrictor:
        """Handle deformat."""
        split: VersionSplit
        split = VersionSplit.by_string(string)
        return VersionRestrictor(
            leading=split.leading,
            public=self.public._deformat(split.public),
            local=self.local._deformat(split.local),
            trailing=split.trailing,
        )

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        """Handle format parse."""
        return (VersionSplit.by_string(spec),)

    def _format_parsed(self: Self, split: VersionSplit, /) -> str:
        """Handle format parsed."""
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
        """Handle init factories."""
        return dict(_public=Public_, _local=Local_)

    def _string_fset(self: Self, value: str, /) -> None:
        """Handle string fset."""
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
        """Handle todict."""
        return dict(public=self.public, local=self.local)

    @property
    def local(self: Self, /) -> Local_:
        "Represent the local identifier."
        return self._local

    @local.setter
    @setter
    def local(self: Self, value: object, /) -> None:
        """Perform local."""
        self.local.string = value

    @property
    def packaging(self: Self, /) -> packaging.version.Version:
        "Return an equivalent packaging.version.Version object."
        return packaging.version.Version(str(self))

    @packaging.setter
    @setter
    def packaging(self: Self, value: object, /) -> None:
        """Perform packaging."""
        self.string = value

    @property
    def public(self: Self, /) -> Public_:
        "Represent the public identifier."
        return self._public

    @public.setter
    @setter
    def public(self: Self, value: object, /) -> None:
        """Perform public."""
        self.public.string = value


class VersionSplit(NamedTuple):
    """Represent VersionSplit."""

    leading: str
    public: str
    local: str
    trailing: str

    @classmethod
    def by_string(cls: type[Self], /, string: str) -> Self:
        """Build an instance by string."""
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
