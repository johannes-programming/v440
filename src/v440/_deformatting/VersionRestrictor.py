"""Provide the central Version class for mutable PEP 440 versions."""

from __future__ import annotations

__all__: list[str] = ["VersionRestrictor"]

from dataclasses import dataclass
from typing import Self

from v440._deformatting.LocalRestrictor import LocalRestrictor
from v440._deformatting.PublicRestrictor import PublicRestrictor


@dataclass(frozen=True, kw_only=True)
class VersionRestrictor:
    """Track formatting constraints for an entire version string."""

    leading: str
    public: PublicRestrictor
    local: LocalRestrictor
    trailing: str

    def best(self: Self, /) -> str:
        """Return the shortest format fragment satisfying these constraints."""
        result: str
        result = self.local.best()
        if result:
            result = "+" + result
        result = self.public.best() + result
        if result or self.leading == self.trailing == "":
            return self.leading + result + self.trailing
        else:
            return self.leading + "!" + self.trailing

    def union(self: Self, other: Self, /) -> Self:
        """Combine these constraints with another compatible observation."""
        if self.leading != other.leading or self.trailing != other.trailing:
            raise ArithmeticError
        return type(self)(
            leading=self.leading,
            public=self.public.union(other.public),
            local=self.local.union(other.local),
            trailing=self.trailing,
        )
