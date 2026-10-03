"""Provide the Base class for v440 public version base."""

from __future__ import annotations

__all__: list[str] = ["Base"]

import operator
from typing import Any, Final, Self

from v440._deformatting.BaseRestrictor import BaseRestrictor
from v440._deformatting.Mag import Mag
from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.abc.NestedABC import NestedABC
from v440.core.Release import Release as Release_


class Base(NestedABC):

    """Represent Base."""
    Release: Final[type[Release_]] = Release_
    _epoch: int
    _release: Release_

    __slots__ = ("_epoch", "_release")

    def _cmp(self: Self, /) -> tuple[int, Release_]:
        """Handle cmp."""
        return self.epoch, self.release

    def _deformat(self: Self, string: str, /) -> BaseRestrictor:
        """Handle deformat."""
        epoch: str
        matches: dict[str, str]
        matches = Cfg.fullmatches("base", string)
        epoch = matches["epoch"]
        return BaseRestrictor(
            basev=matches["basev"],
            epoch=Mag(len(epoch) if epoch.startswith("0") else -len(epoch)),
            release=self.release._deformat(matches["release"]),
        )

    @classmethod
    def _format_parse(
        cls: type[Self],
        spec: str,
        /,
    ) -> tuple[str, int, str]:
        """Handle format parse."""
        matches: dict[str, str]
        matches = Cfg.fullmatches("base_f", spec)
        return (
            matches["basev_f"],
            len(matches["epoch_f"]),
            matches["release_f"],
        )

    def _format_parsed(
        self: Self,
        /,
        basev_f: str,
        epoch_mag: int,
        release_f: str,
    ) -> str:
        """Handle format parsed."""
        ans: str
        ans = basev_f
        if epoch_mag or self.epoch:
            ans += format(self.epoch, "0%sd" % epoch_mag)
            ans += "!"
        ans += format(self.release, release_f)
        return ans

    @classmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]:
        """Handle init factories."""
        return dict(_epoch=int, _release=Release_)

    def _string_fset(self: Self, value: str, /) -> None:
        """Handle string fset."""
        matches: dict[str, str]
        matches = Cfg.fullmatches("base", value)
        if matches["epoch"]:
            self.epoch = int(matches["epoch"])
        else:
            self.epoch = 0
        self.release.string = matches["release"]

    def _todict(self: Self, /) -> dict[str, Any]:
        """Handle todict."""
        return dict(epoch=self.epoch, release=self.release)

    @property
    def epoch(self: Self, /) -> int:
        "Represent the epoch."
        return self._epoch

    @epoch.setter
    @setter
    def epoch(self: Self, value: Any, /) -> None:
        """Perform epoch."""
        v: int
        v = operator.index(value)
        if v < 0:
            raise ValueError
        self._epoch = v

    packaging = NestedABC.string

    @property
    def release(self: Self, /) -> Release_:
        "Represent the release."
        return self._release

    @release.setter
    @setter
    def release(self: Self, value: object, /) -> None:
        """Perform release."""
        self.release.string = value
