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
    """Model a mutable PEP 440 version."""

    Public: Final[type[Public_]] = Public_
    Local: Final[type[Local_]] = Local_
    _public: Public_
    _local: Local_

    __slots__ = ("_public", "_local")

    def _cmp(self: Self, /) -> tuple[Public_, Local_]:
        """Return the comparison key for this value."""
        return self.public, self.local

    def _deformat(self: Self, string: str, /) -> VersionRestrictor:
        """Infer formatting constraints that reproduce the supplied rendering."""
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
        """Parse a format specification into normalized rendering fields."""
        return (VersionSplit.by_string(spec),)

    def _format_parsed(self: Self, split: VersionSplit, /) -> str:
        """Render this value from normalized format fields."""
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
        """Return factories for the nested fields owned by this class."""
        return dict(_public=Public_, _local=Local_)

    def _string_fset(self: Self, value: str, /) -> None:
        """Parse a string into this instance's normalized fields."""
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
        """Return this instance's nested fields by public name."""
        return dict(public=self.public, local=self.local)

    @property
    def local(self: Self, /) -> Local_:
        """Return the local-version identifier."""
        return self._local

    @local.setter
    @setter
    def local(self: Self, value: object, /) -> None:
        """Update the local-version identifier from the supplied value."""
        self.local.string = value

    @property
    def packaging(self: Self, /) -> packaging.version.Version:
        """Return an equivalent packaging.version.Version object."""
        return packaging.version.Version(str(self))

    @packaging.setter
    @setter
    def packaging(self: Self, value: object, /) -> None:
        """Update this value from its packaging-compatible representation."""
        self.string = value

    @property
    def public(self: Self, /) -> Public_:
        """Return the public-version identifier."""
        return self._public

    @public.setter
    @setter
    def public(self: Self, value: object, /) -> None:
        """Update the public-version identifier from the supplied value."""
        self.public.string = value


class VersionSplit(NamedTuple):
    """Store the leading, public, local, and trailing parts of a version string."""

    leading: str
    public: str
    local: str
    trailing: str

    @classmethod
    def by_string(cls: type[Self], /, string: str) -> Self:
        """Split a version string into whitespace, public, and local components."""
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
