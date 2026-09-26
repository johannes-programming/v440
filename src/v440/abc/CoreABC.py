"""Provide the CoreABC abstract base for v440 classes."""

__all__: list[str] = ["CoreABC"]

from abc import abstractmethod
from typing import Any, Self

import setdoc
from copyable import Copyable
from datarepr import oxford

from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.errors.VersionError import VersionError


class CoreABC(Copyable):
    __slots__ = ()

    @abstractmethod
    @setdoc.basic
    def __bool__(self: Self, /) -> bool: ...

    @abstractmethod
    @setdoc.basic
    def __eq__(self: Self, other: object, /) -> bool: ...

    @setdoc.basic
    def __format__(self: Self, format_spec: object, /) -> str:
        body: str
        head: str
        parsed: tuple[Any, ...]
        spec: str
        tail: str
        msg: str
        try:
            spec = str(format_spec)
            body = spec.strip()
            if spec and not body:
                raise ValueError
            head = spec[: len(spec) - len(spec.lstrip())]
            tail = spec[len(spec.rstrip()) :]
            parsed = self._format_parse(body)
        except Exception:
            msg = Cfg.cfg.data["consts"]["errors"]["format"]
            msg %= (format_spec, type(self).__name__)
            raise VersionError(msg)  # from None
        return head + str(self._format_parsed(parsed)) + tail

    @abstractmethod
    @setdoc.basic
    def __ge__(self: Self, other: Self, /) -> bool: ...

    @abstractmethod
    @setdoc.basic
    def __gt__(self: Self, other: Self, /) -> bool: ...

    @setdoc.basic
    def __init__(
        self: Self, other: Self | None = None, /, **kwargs: Any
    ) -> None:
        self._init_other(other)
        self._init_kwargs(**kwargs)

    @abstractmethod
    @setdoc.basic
    def __le__(self: Self, other: Self, /) -> bool: ...

    @abstractmethod
    @setdoc.basic
    def __lt__(self: Self, other: Self, /) -> bool: ...

    @abstractmethod
    @setdoc.basic
    def __repr__(self: Self, /) -> str: ...

    @setdoc.basic
    def __str__(self: Self, /) -> str:
        return format(self, "")

    @abstractmethod
    def _deformat(self: Self, body: str) -> Any: ...

    @staticmethod
    @abstractmethod
    def _deformat_origin() -> Any: ...

    @classmethod
    @abstractmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]: ...

    @abstractmethod
    def _format_parsed(self: Self, parsed: tuple[Any, ...], /) -> object: ...

    def _init_kwargs(self: Self, /, **kwargs: Any) -> None:
        x: str
        y: Any
        for x, y in kwargs.items():
            setattr(self, x.lstrip("_"), y)

    @abstractmethod
    def _init_other(self: Self, other: Self | None, /) -> None: ...

    @abstractmethod
    def _string_fset(self: Self, value: str, /) -> None: ...

    @setdoc.basic
    def copy(self: Self, /) -> Self:
        return type(self)(self)

    @classmethod
    def deformat(cls: type[Self], /, *strings: object) -> str:
        ans: str
        bodies: set[str]
        body: str
        head: str
        heads: set[str]
        tail: str
        tails: set[str]
        x: str
        y: Any
        y = cls._deformat_origin()
        try:
            bodies = set()
            heads = set()
            tails = set()
            for x in map(str, strings):
                body = x.strip()
                if body:
                    head = x[: len(x) - len(x.lstrip())]
                    tail = x[len(x.rstrip()) :]
                else:
                    head = x
                    tail = ""
                bodies.add(body)
                heads.add(head)
                tails.add(tail)
            if strings:
                (head,) = heads
                (tail,) = tails
            else:
                head = ""
                tail = ""
            for body in bodies:
                y &= cls(string=body)._deformat(body)
            ans = y.best(forbids_empty=bool(head or tail))
            return head + ans + tail
        except VersionError:
            raise
        except Exception:
            msg = Cfg.cfg.data["consts"]["errors"]["deformat"]
            msg %= oxford(*strings)
            raise VersionError(msg)

    @property
    @abstractmethod
    def packaging(self: Self, /) -> Any: ...

    @property
    def string(self: Self, /) -> str:
        "This property represents self as str."
        return format(self, "")

    @string.setter
    @setter
    def string(self: Self, value: object, /) -> None:
        self._string_fset(str(value).strip().lower())
