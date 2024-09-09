from __future__ import annotations

import types
import typing

import scaevola

from . import utils


@utils.compclass(list)
class Local(scaevola.Scaevola):
    def __add__(self, other, /):
        return self._new(self._data + self._todata(other))

    @classmethod
    def __class_getitem__(cls, key, /):
        return types.GenericAlias(cls, key)

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self._data == other._data

    def __getitem__(self, key, /):
        if type(key) is not slice:
            return self._data[key]
        return self._new(self._data[key])

    def __hash__(self):
        raise TypeError("unhashable type: %r" % type(self).__name__)

    def __iadd__(self, other, /):
        self._data += self._todata(other)

    def __imul__(self, other, /):
        self._data *= other

    def __init__(self, data=[]):
        self.data = data

    def __le__(self, other):
        other = type(self)(other)
        return self._cmpkey() <= other._cmpkey()

    def __lt__(self, other):
        other = type(self)(other)
        return self._cmpkey() < other._cmpkey()

    def __mul__(self, other, /):
        return self._new(self._data * other)

    def __repr__(self) -> str:
        return "%s(%r)" % (type(self).__name__, str(self))

    def __reversed__(self, /):
        ans = self[:]
        ans._data.reverse()
        return ans

    def __rmul__(self, other, /):
        return self.__mul__(other)

    def __setitem__(self, key, value, /):
        if type(key) is not slice:
            self._data[key] = utils.segment(value)
        else:
            self._data[key] = self._todata(value._data)

    def __str__(self) -> str:
        return ".".join(str(x) for x in self)

    def _cmpkey(self):
        return [self._sortkey(x) for x in self]

    @classmethod
    def _new(cls, data, /):
        ans = object.__new__(cls)
        ans._data = data
        return ans

    @staticmethod
    def _sortkey(value):
        return type(value) is int, value

    @staticmethod
    def _todata(data, /):
        return utils.todata(data, "+")

    def append(self, elem, /):
        self._data.append(utils.segment(elem))

    def copy(self):
        return self._new(self.data)

    @property
    def data(self, /):
        return list(self._data)

    @data.setter
    @utils.setterdeco
    def data(self, data, /):
        self._data = self._todata(data)

    @data.deleter
    def data(self):
        self._data = []

    def extend(self, data, /):
        self.__iadd__(data)

    def insert(self, index, elem, /):
        self._data.insert(index, utils.segment(elem))

    def sort(self, *, key=None, reverse=False):
        if key is None:
            key = self._sortkey
        self._data.sort(key=key, reverse=reverse)
