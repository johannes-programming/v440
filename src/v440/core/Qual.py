"""Provide the Qual class for qualified version parts in v440."""

from __future__ import annotations

__all__: list[str] = ["Qual"]

from dataclasses import dataclass
from typing import Any, Final, Self

from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.abc.NestedABC import NestedABC
from v440.core.Dev import Dev as Dev_
from v440.core.Dev import _candidate_specs_for as _dev_candidate_specs_for
from v440.core.Post import Post as Post_
from v440.core.Post import _candidate_specs_for as _post_candidate_specs_for
from v440.core.Pre import Pre as Pre_
from v440.core.Pre import _candidate_specs_for as _pre_candidate_specs_for


class Qual(NestedABC):

    Pre: Final[type[Pre_]] = Pre_
    Post: Final[type[Post_]] = Post_
    Dev: Final[type[Dev_]] = Dev_
    _pre: Pre_
    _post: Post_
    _dev: Dev_

    __slots__ = ("_pre", "_post", "_dev")

    def _cmp(self: Self, /) -> tuple[str, int, Post_, Dev_]:
        ans: tuple[str, int]
        if self.pre:
            ans = (self.pre.lit, self.pre.num)
        elif self.post or not self.dev:
            ans = ("z", 0)
        else:
            ans = ("", 0)
        return ans + (self.post, self.dev)

    def _deformat(self: Self, body: str, /) -> QualAccumulation:
        return QualAccumulation((body,))

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        matches: dict[str, str]
        matches = Cfg.fullmatches("qual_f", spec)
        return (
            matches["pre_f"],
            matches["post_f"],
            matches["dev_f"],
        )

    def _format_parsed(
        self: Self, pre_f: str, post_f: str, dev_f: str, /
    ) -> str:
        ans: str
        ans = format(self.pre, pre_f)
        ans += format(self.post, post_f)
        ans += format(self.dev, dev_f)
        return ans

    @classmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]:
        return dict(_pre=Pre_, _post=Post_, _dev=Dev_)

    def _string_fset(self: Self, value: str, /) -> None:
        matches: dict[str, str]
        matches = Cfg.fullmatches("qual", value)
        self.pre.string = matches["pre"]
        self.post.string = matches["post"]
        self.dev.string = matches["dev"]

    def _todict(self: Self, /) -> dict[str, Any]:
        return dict(pre=self.pre, post=self.post, dev=self.dev)

    @property
    def dev(self: Self, /) -> Dev_:
        "This property represents the stage of development."
        return self._dev

    @dev.setter
    @setter
    def dev(self: Self, value: object, /) -> None:
        self.dev.string = value

    def isdevrelease(self: Self, /) -> bool:
        "Return whether this instance denotes a dev-release."
        return bool(self.dev)

    def isprerelease(self: Self, /) -> bool:
        "Return whether this instance denotes a pre-release."
        return bool(self.pre) or bool(self.dev)

    def ispostrelease(self: Self, /) -> bool:
        "Return whether this instance denotes a post-release."
        return bool(self.post)

    packaging = NestedABC.string

    @property
    def post(self: Self, /) -> Post_:
        return self._post

    @post.setter
    @setter
    def post(self: Self, value: object, /) -> None:
        self.post.string = value

    @property
    def pre(self: Self, /) -> Pre_:
        return self._pre

    @pre.setter
    @setter
    def pre(self: Self, value: object, /) -> None:
        self.pre.string = value


@dataclass(frozen=True)
class QualAccumulation:
    strings: tuple[str, ...] = ()

    def intersection(self: Self, other: Self, /) -> Self:
        return type(self)(tuple(sorted(set(self.strings + other.strings))))

    def best(self: Self, /) -> str:
        """Return the actual shortest common qualification format specifier.

        A qualification spelling can have more than one decomposition at a
        component boundary.  For example, the dot in ``r.dev2`` may be read as
        part of the post spelling while formatting can instead obtain it from
        Dev's default ``.dev`` spelling.  Search component output vectors rather
        than committing to the regex parser's one decomposition of each input.
        """

        objects = tuple(Qual(string=body) for body in self.strings)
        if not objects:
            return ""

        pre_objects = tuple(obj.pre for obj in objects)
        post_objects = tuple(obj.post for obj in objects)
        dev_objects = tuple(obj.dev for obj in objects)

        pre_specs = _pre_candidate_specs_for(
            pre_objects, self.strings, "prefix"
        )
        post_specs = _post_candidate_specs_for(
            post_objects, self.strings, "contains"
        )
        dev_specs = _dev_candidate_specs_for(
            dev_objects, self.strings, "suffix"
        )

        pre_groups: dict[tuple[str, ...], list[str]] = {}
        for spec in pre_specs:
            outputs = tuple(format(obj.pre, spec) for obj in objects)
            pre_groups.setdefault(outputs, []).append(spec)

        post_groups: dict[tuple[str, ...], list[str]] = {}
        for spec in post_specs:
            outputs = tuple(format(obj.post, spec) for obj in objects)
            post_groups.setdefault(outputs, []).append(spec)

        dev_groups: dict[tuple[str, ...], list[str]] = {}
        for spec in dev_specs:
            outputs = tuple(format(obj.dev, spec) for obj in objects)
            dev_groups.setdefault(outputs, []).append(spec)

        best: str | None = None
        for pre_outputs, pre_group in pre_groups.items():
            for dev_outputs, dev_group in dev_groups.items():
                middle: list[str] = []
                possible = True
                for body, pre_output, dev_output in zip(
                    self.strings, pre_outputs, dev_outputs
                ):
                    if not body.startswith(pre_output):
                        possible = False
                        break
                    if not body.endswith(dev_output):
                        possible = False
                        break
                    if len(pre_output) + len(dev_output) > len(body):
                        possible = False
                        break
                    end = len(body) - len(dev_output)
                    middle.append(body[len(pre_output) : end])
                if not possible:
                    continue

                post_group = post_groups.get(tuple(middle))
                if post_group is None:
                    continue
                for pre_spec in pre_group:
                    for post_spec in post_group:
                        for dev_spec in dev_group:
                            spec = pre_spec + post_spec + dev_spec
                            if best is not None and (len(spec), spec) >= (
                                len(best),
                                best,
                            ):
                                continue
                            try:
                                recreates = all(
                                    format(obj, spec) == body
                                    for obj, body in zip(objects, self.strings)
                                )
                            except Exception:
                                recreates = False
                            if recreates:
                                best = spec

        if best is None:
            raise ValueError
        return best
