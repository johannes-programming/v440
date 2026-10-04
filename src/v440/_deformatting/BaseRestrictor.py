"""Provide the Base class for v440 public version base."""

from __future__ import annotations

__all__: list[str] = ["BaseRestrictor"]

from dataclasses import dataclass
from typing import Self

from v440._deformatting.Mag import Mag
from v440._deformatting.ReleaseRestrictor import ReleaseRestrictor


@dataclass(frozen=True, kw_only=True)
class BaseRestrictor:
    """Track formatting constraints for a public-version base."""

    basev: str
    epoch: Mag
    release: ReleaseRestrictor

    def best(self: Self, /) -> str:
        """Return the shortest format fragment satisfying these constraints."""
        result: str
        result = self.basev
        result += "#" * self.epoch
        result += "!" * (self.epoch > 0)
        result += self.release.best()
        return result

    def union(self: Self, other: Self, /) -> Self:
        """Combine these constraints with another compatible observation."""
        epoch: Mag
        if self.basev != other.basev:
            raise ValueError
        epoch = self.epoch.union(other.epoch)
        return type(self)(
            basev=self.basev,
            epoch=epoch,
            release=self.release.union(other.release),
        )
