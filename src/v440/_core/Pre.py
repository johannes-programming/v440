from __future__ import annotations

import typing

import datahold

from . import utils

__all__ = ["Pre"]

PHASEDICT = dict(
    alpha="a",
    a="a",
    beta="b",
    b="b",
    preview="rc",
    pre="rc",
    c="rc",
    rc="rc",
)


class Pre(datahold.OkayList):

    def __init__(self, data=None):
        self.data = data

    __repr__ = utils.Base.__repr__

    __setattr__ = utils.Base.__setattr__

    def __str__(self) -> str:
        if self.isempty():
            return ""
        return self.phase + str(self.subphase)

    @property
    def data(self):
        return list(self._data)

    @data.setter
    @utils.setterdeco
    def data(self, value, /):
        value = utils.qparse(value, *PHASEDICT.keys())
        if value[0] is not None:
            if value[1] is None:
                raise ValueError
            value[0] = PHASEDICT[value[0]]
        self._data = value

    @data.deleter
    def data(self):
        self._data = [None, None]

    def isempty(self):
        return self._data == [None, None]

    @property
    def phase(self):
        return self._data[0]

    @phase.setter
    @utils.setterdeco
    def phase(self, value):
        data = self.data
        data[0] = value
        self.data = data

    @phase.deleter
    def phase(self):
        self.phase = None

    @property
    def subphase(self):
        return self._data[1]

    @subphase.setter
    @utils.setterdeco
    def subphase(self, value):
        data = self.data
        data[1] = value
        self.data = data

    @subphase.deleter
    def subphase(self):
        self.subphase = None
