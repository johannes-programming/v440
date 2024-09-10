from __future__ import annotations

import typing

import scaevola

from . import utils


class Pre:
    _PHASEDICT = dict(
        alpha="a",
        a="a",
        beta="b",
        b="b",
        preview="rc",
        pre="rc",
        c="rc",
        rc="rc",
    )

    def __bool__(self):
        return bool(self.phase)

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return self.data == other.data

    def __hash__(self) -> int:
        return hash((self.phase, self.subphase))

    @typing.overload
    def __init__(self, data=None) -> None: ...
    @typing.overload
    def __init__(self, phase, subphase=0): ...

    def __init__(self, *args, **kwargs):
        self._init(*args, **kwargs)(*args, **kwargs)

    def __repr__(self) -> str:
        return "%s(%r)" % (type(self).__name__, str(self))

    def __str__(self) -> str:
        if self:
            return self.phase + str(self.subphase)
        else:
            return ""

    def _init(self, *args, **kwargs):
        if "data" in kwargs.keys():
            return self._init_data
        if kwargs:
            return self._init_items
        if len(args) > 1:
            return self._init_items
        return self._init_data

    def _init_data(self, data=None):
        self.data = data

    def _init_items(self, phase, subphase=0):
        self.phase = phase
        self.subphase = subphase

    def copy(self):
        return type(self)(self)

    @property
    def data(self):
        if not self.phase:
            return None
        return self.phase, self.subphase

    @data.setter
    @utils.setterdeco
    def data(self, value, /):
        value = utils.tolist(value, ".")
        if len(value) == 0:
            del self.data
            return
        if len(value) > 1:
            self.phase, self.subphase = value
            return
        value = value[0]
        if type(value) is int:
            raise TypeError
        for long, short in type(self)._PHASEDICT.items():
            p, value = utils.lsplit(value, long, "")
            if p == "":
                continue
            self.phase = short
            self.subphase = value
            return
        raise ValueError

    @data.deleter
    def data(self):
        del self.phase

    @property
    def phase(self):
        return self._phase

    @phase.setter
    @utils.setterdeco
    def phase(self, value):
        if not value:
            del self.phase
            return
        value = utils.literal(value)
        value = type(self)._PHASEDICT[value]
        self._phase = value

    @phase.deleter
    def phase(self):
        self._phase = None
        self._subphase = 0

    @property
    def subphase(self):
        return self._subphase

    @subphase.setter
    @utils.setterdeco
    def subphase(self, value):
        value = utils.numeral(value)
        if value == 0:
            del self.subphase
            return
        if self.phase:
            self._subphase = value
            return
        raise utils.VersionError("no subphase allowed without a phase")

    @subphase.deleter
    def subphase(self):
        self._subphase = 0
