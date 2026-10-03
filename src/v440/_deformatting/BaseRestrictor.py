"""Provide the Base class for v440 public version base."""

from __future__ import annotations

__all__: list[str] = ["BaseRestrictor"]

from dataclasses import dataclass
from typing import Self

from v440._deformatting.Mag import Mag
from v440._deformatting.ReleaseRestrictor import ReleaseRestrictor


@dataclass(frozen=True, kw_only=True)
class BaseRestrictor:
    """Represent BaseRestrictor."""
    basev: str
    epoch: Mag
    release: ReleaseRestrictor

    def best(self: Self, /) -> str:
        """Return the best of this state."""
        ans: str
        ans = self.basev
        ans += "#" * self.epoch
        ans += "!" * (self.epoch > 0)
        ans += self.release.best()
        return ans

    def union(self: Self, other: Self, /) -> Self:
        """Unite this state with another."""
        epoch: Mag
        if self.basev != other.basev:
            raise ValueError
        epoch = self.epoch.union(other.epoch)
        return type(self)(
            basev=self.basev,
            epoch=epoch,
            release=self.release.union(other.release),
        )
