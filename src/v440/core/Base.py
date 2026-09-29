"""Provide the Base class for v440 public version base."""

from __future__ import annotations

__all__: list[str] = ["Base"]

import operator
from dataclasses import dataclass
from typing import Any, Final, Self

from v440._deformatting.Mag import Mag
from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.abc.NestedABC import NestedABC
from v440.core.Release import Release as Release_
from v440.core.Release import ReleaseAccumulation


class Base(NestedABC):

    Release: Final[type[Release_]] = Release_
    _epoch: int
    _release: Release_

    __slots__ = ("_epoch", "_release")

    def _cmp(self: Self, /) -> tuple[int, Release_]:
        return self.epoch, self.release

    def _deformat(self: Self, body: str, /) -> BaseAccumulation:
        epoch: str
        matches: dict[str, str]
        matches = Cfg.fullmatches("base", body)
        epoch = matches["epoch"]
        return BaseAccumulation(
            basev=matches["basev"],
            epoch=Mag(len(epoch) if epoch.startswith("0") else -len(epoch)),
            release=self.release._deformat(matches["release"]),
        )

    @classmethod
    def _format_parse(
        cls: type[Self],
        spec: str,
        /,
    ) -> tuple[Any, ...]:
        matches: dict[str, str]
        matches = Cfg.fullmatches("base_f", spec)
        return (
            matches["basev_f"],
            len(matches["epoch_f"]),
            matches["release_f"],
        )

    def _format_parsed(
        self: Self,
        parsed: tuple[Any, ...],
        /,
    ) -> str:
        basev_f: str
        epoch_mag: int
        release_f: str
        ans: str
        basev_f, epoch_mag, release_f = parsed
        ans = basev_f
        if epoch_mag or self.epoch:
            ans += format(self.epoch, "0%sd" % epoch_mag)
            ans += "!"
        ans += format(self.release, release_f)
        return ans

    @classmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]:
        return dict(_epoch=int, _release=Release_)

    def _string_fset(self: Self, value: str, /) -> None:
        matches: dict[str, str]
        matches = Cfg.fullmatches("base", value)
        if matches["epoch"]:
            self.epoch = int(matches["epoch"])
        else:
            self.epoch = 0
        self.release.string = matches["release"]

    def _todict(self: Self, /) -> dict[str, Any]:
        return dict(epoch=self.epoch, release=self.release)

    @property
    def epoch(self: Self, /) -> int:
        "This property represents the epoch."
        return self._epoch

    @epoch.setter
    @setter
    def epoch(self: Self, value: Any, /) -> None:
        v: int
        v = operator.index(value)
        if v < 0:
            raise ValueError
        self._epoch = v

    packaging = NestedABC.string

    @property
    def release(self: Self, /) -> Release_:
        "This property represents the release."
        return self._release

    @release.setter
    @setter
    def release(self: Self, value: object, /) -> None:
        self.release.string = value


@dataclass(frozen=True, kw_only=True)
class BaseAccumulation:
    basev: str | None
    epoch: Mag
    release: ReleaseAccumulation

    def best(self: Self, /) -> str:
        ans: str
        ans = self.basev or ""
        ans += "#" * self.epoch
        ans += "!" * (self.epoch > 0)
        ans += self.release.best()
        return ans

    def intersection(self: Self, other: Self, /) -> Self:
        basev: str | None
        epoch: Mag
        if self.basev is None:
            basev = other.basev
        elif other.basev is None:
            basev = self.basev
        elif self.basev == other.basev:
            basev = self.basev
        else:
            raise ValueError
        epoch = self.epoch.intersection(other.epoch)
        return type(self)(
            basev=basev,
            epoch=epoch,
            release=self.release.intersection(other.release),
        )
