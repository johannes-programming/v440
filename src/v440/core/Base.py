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
    """Model the epoch and release portion of a public version."""

    Release: Final[type[Release_]] = Release_
    _epoch: int
    _release: Release_

    __slots__ = ("_epoch", "_release")

    def _cmp(self: Self, /) -> tuple[int, Release_]:
        """Return the comparison key for this value."""
        return self.epoch, self.release

    def _deformat(self: Self, string: str, /) -> BaseRestrictor:
        """Infer formatting constraints that reproduce the supplied rendering."""
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
        """Parse a format specification into normalized rendering fields."""
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
        """Render this value from normalized format fields."""
        result: str
        result = basev_f
        if epoch_mag or self.epoch:
            result += format(self.epoch, "0%sd" % epoch_mag)
            result += "!"
        result += format(self.release, release_f)
        return result

    @classmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]:
        """Return factories for the nested fields owned by this class."""
        return dict(_epoch=int, _release=Release_)

    def _string_fset(self: Self, value: str, /) -> None:
        """Parse a string into this instance's normalized fields."""
        matches: dict[str, str]
        matches = Cfg.fullmatches("base", value)
        if matches["epoch"]:
            self.epoch = int(matches["epoch"])
        else:
            self.epoch = 0
        self.release.string = matches["release"]

    def _todict(self: Self, /) -> dict[str, Any]:
        """Return this instance's nested fields by public name."""
        return dict(epoch=self.epoch, release=self.release)

    @property
    def epoch(self: Self, /) -> int:
        """Return the version epoch."""
        return self._epoch

    @epoch.setter
    @setter
    def epoch(self: Self, value: Any, /) -> None:
        """Validate and assign the version epoch."""
        epoch_value: int
        epoch_value = operator.index(value)
        if epoch_value < 0:
            raise ValueError
        self._epoch = epoch_value

    packaging = NestedABC.string

    @property
    def release(self: Self, /) -> Release_:
        """Return the release-number component object."""
        return self._release

    @release.setter
    @setter
    def release(self: Self, value: object, /) -> None:
        """Update the release-number components from the supplied value."""
        self.release.string = value
