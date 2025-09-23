from __future__ import annotations

from typing import *

import setdoc

from v440._utils import qualparse
from v440._utils.SlotList import SlotList
from v440._utils.utils import guard

__all__ = ["Qual"]


class Qual(SlotList):

    __slots__ = ("_prephase", "_presubphase", "_post", "_dev")

    data: list
    prephase: Optional[str]
    presubphase: Optional[int]
    post: Optional[int]
    dev: Optional[int]

    @setdoc.basic
    def __init__(self: Self, data: Any = None) -> None:
        self._prephase = None
        self._presubphase = None
        self._post = None
        self._dev = None
        self.data = data

    @setdoc.basic
    def __str__(self: Self) -> str:
        ans: str = ""
        if self.prephase is not None:
            ans += self.prephase
        if self.presubphase is not None:
            ans += str(self.presubphase)
        if self.post is not None:
            ans += ".post%s" % self.post
        if self.dev is not None:
            ans += ".dev%s" % self.dev
        return ans

    def _cmp(self: Self) -> list:
        ans: list = list()
        if not self.pre.isempty():
            ans += list(self.pre)
        elif self.post is not None:
            ans += ["z", float("inf")]
        elif self.dev is None:
            ans += ["z", float("inf")]
        else:
            ans += ["", -1]
        ans.append(-1 if self.post is None else self.post)
        ans.append(float("inf") if self.dev is None else self.dev)
        return ans

    @property
    @setdoc.basic
    def data(self: Self) -> list:
        return [self.prephase, self.presubphase, self.post, self.dev]

    @data.setter
    @guard
    def data(self: Self, value: Any) -> None:
        self.pre, self.post, self.dev = qualparse.parse_leg(value)

    @property
    def dev(self: Self) -> Optional[int]:
        return self._dev

    @dev.setter
    @guard
    def dev(self: Self, value: Any) -> None:
        self._dev = qualparse.parse_dev(value)

    def isdevrelease(self: Self) -> bool:
        return self.dev is not None

    def isempty(self: Self) -> bool:
        return self.data == [None, None, None, None]

    def isprerelease(self: Self) -> bool:
        return {self.prephase, self.presubphase, self.dev} != {None}

    def ispostrelease(self: Self) -> bool:
        return self.post is not None

    @property
    def post(self: Self) -> Optional[int]:
        return self._post

    @post.setter
    @guard
    def post(self: Self, value: Any) -> None:
        self._post = qualparse.parse_post(value)

    @property
    def pre(self: Self) -> tuple:
        return (self._prephase, self._presubphase)

    @pre.setter
    @guard
    def pre(self: Self, value: Any) -> None:
        self._prephase, self._presubphase = qualparse.parse_pre(value)

    @property
    def prephase(self: Self) -> Optional[str]:
        return self._prephase

    @prephase.setter
    def prephase(self: Self, value: Any) -> None:
        self.pre = value, self.presubphase

    @property
    def presubphase(self: Self) -> Optional[int]:
        return self._presubphase

    @presubphase.setter
    def presubphase(self: Self, value: Any) -> None:
        self.pre = self.prephase, value
