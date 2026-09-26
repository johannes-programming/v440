__all__: list[str] = [
    "TestDeformatting",
    "TestFormat",
    "TestOrder",
    "TestReleaseAlias",
    "TestSlicingGo",
    "TestSlots",
    "TestStringExamples",
    "TestTotalAttrSetter",
    "TestTotalMethod",
    "TestTypeNames",
    "TestFunction",
    "TestVersionEpochGo",
]

import contextlib
import enum
import functools
import importlib
import io
import operator
import shlex
import tomllib
import types
import unittest
from collections import abc
from pathlib import Path
from typing import Any, Self, cast

from packaging.version import InvalidVersion
from packaging.version import Version as Version_

from v440 import core
from v440.core.Version import Version
from v440.errors.VersionError import VersionError


class Util(enum.Enum):
    util = None

    @functools.cached_property
    def data(self: Self, /) -> dict[str, Any]:
        file: Path
        stream: io.BufferedReader
        file = Path(__file__).parent / "testdata.toml"
        with file.open("rb") as stream:
            return tomllib.load(stream)

    @functools.cached_property
    def examples(self: Self, /) -> dict[str, Any]:
        return cast(dict[str, Any], Util.util.data.get("examples", {}))

    @classmethod
    def import_(cls: type[Self], qualname: str, /) -> Any:
        module: types.ModuleType
        name: str
        names: list[str]
        names = qualname.split(".")
        name = names.pop(-1)
        module = importlib.import_module(".".join(names))
        return getattr(module, name)


class TestDeformatting(unittest.TestCase):

    def go_blob(
        self: Self,
        cls: type[Any],
        /,
        *,
        valid: bool,
        **kwargs: Any,
    ) -> None:
        with self.subTest(valid=valid):
            if valid:
                self.go_blob_valid(cls, **kwargs)
            else:
                self.go_blob_invalid(cls, **kwargs)

    def go_blob_invalid(
        self: Self,
        cls: type[Any],
        /,
        *,
        strings: list[str],
        **kwargs: Any,
    ) -> None:
        with self.assertRaises(VersionError):
            cls.deformat(*strings)

    def go_blob_valid(
        self: Self,
        cls: type[Any],
        /,
        *,
        solution: str,
        strings: list[str],
        **kwargs: Any,
    ) -> None:
        answer: str
        answer = cls.deformat(*strings)
        self.assertEqual(answer, solution)

    def go_cls(
        self: Self,
        cls: type[Any],
        /,
        **typedict: dict[str, Any],
    ) -> None:
        example: tuple[str]
        log: dict[tuple[str], str]
        log = dict()
        for testname, testdict in typedict.items():
            example = tuple(testdict["strings"])
            with self.subTest(testname=testname, example=example):
                self.assertNotIn(
                    example,
                    log,
                    "conflict with %r" % log.get(example),
                )
                log[example] = testname
                self.go_blob(cls, **testdict)

    def test_0(self: Self, /) -> None:
        cls: type[Any]
        typename: str
        typedict: dict[Any, Any]
        for typename, typedict in Util.util.data["deformatting"].items():
            cls = Util.import_("v440.core.{0}.{0}".format(typename))
            with self.subTest(typename=typename):
                self.go_cls(cls, **typedict)


class TestStringExamples(unittest.TestCase):

    def go_version(
        self: Self, example: str, /, *, valid: bool, **kwargs: Any
    ) -> None:
        s: str
        x: Version
        y: Version_
        if not valid:
            with self.assertRaises(InvalidVersion):
                Version_(example)
            return
        x = Version(string=example)
        y = Version_(example)
        self.assertEqual(y, x.packaging)
        s = y.base_version
        while s.endswith(".0"):
            s = s[:-2]
        self.assertTrue(s, x.public.base.packaging)
        self.assertEqual(
            y.dev,
            x.public.qual.dev.packaging,
        )
        self.assertEqual(
            y.local,
            x.local.packaging,
        )
        self.assertEqual(
            y.is_devrelease,
            x.public.qual.isdevrelease(),
        )
        self.assertEqual(
            y.is_postrelease,
            x.public.qual.ispostrelease(),
        )
        self.assertEqual(
            y.is_prerelease,
            x.public.qual.isprerelease(),
        )
        self.assertEqual(
            y.major,
            x.public.base.release.major,
        )
        self.assertEqual(
            y.micro,
            x.public.base.release.micro,
        )
        self.assertEqual(
            y.minor,
            x.public.base.release.minor,
        )
        self.assertEqual(
            y.post,
            x.public.qual.post.packaging,
        )
        self.assertEqual(
            y.pre,
            x.public.qual.pre.packaging,
        )
        s = y.public
        self.assertTrue(s.startswith(x.public.base.packaging))
        s = s[len(x.public.base.packaging) :]
        self.assertTrue(s.endswith(x.public.qual.packaging))
        if x.public.qual.packaging:
            s = s[: -len(x.public.qual.packaging)]
        self.assertEqual(s, ".0" * (len(s) // 2))
        self.assertEqual(
            y.release[: len(x.public.base.release)],
            x.public.base.release.packaging,
        )

    def test_versions(self: Self, /) -> None:
        x: str
        y: dict[Any, Any]
        for x, y in Util.util.examples["Version"].items():
            with self.subTest(example=x):
                self.go_version(x, **y)


class TestTypeNames(unittest.TestCase):
    def go_name(self: Self, name: str, /) -> None:
        cls: type[Any]
        cls = Util.import_(f"v440.core.{name}.{name}")
        self.assertEqual(cls.__name__, name)

    def test_0(self: Self) -> None:
        for name in Util.util.data["synonymous-to-empty"]:
            self.go_name(name)


class TestStringExamples0(unittest.TestCase):

    def go_examples(
        self: Self, /, clsname: str, tables: dict[Any, Any]
    ) -> None:
        cls: type
        split: dict[Any, Any]
        x: str
        y: dict[Any, Any]
        cls = Util.import_("v440.core.{0}.{0}".format(clsname))
        split = {False: dict(), True: dict()}
        for x, y in tables.items():
            split[y["valid"]][x] = y
        for x, y in split[False].items():
            with self.subTest(valid=False, example=x):
                self.go_invalid_example(cls, x, **y)
        for x, y in split[True].items():
            with self.subTest(valid=True, example=x):
                self.go_valid_example(cls, x, **y)

    def go_invalid_example(
        self: Self, cls: type, example: str, /, **kwargs: Any
    ) -> None:
        with self.assertRaises(VersionError):
            cls(string=example)

    def go_valid_example(
        self: Self,
        /,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.go_valid_example_deformatted(*args, **kwargs)
        self.go_valid_example_formatted(*args, **kwargs)
        self.go_valid_example_remake(*args, **kwargs)
        self.go_valid_example_repr(*args, **kwargs)
        self.go_valid_example_str(*args, **kwargs)
        self.go_valid_example_synonym(*args, **kwargs)

    def go_valid_example_deformatted(
        self: Self,
        cls: Any,
        example: str,
        /,
        *,
        deformatted: str | None = None,
        **kwargs: Any,
    ) -> None:
        spec: str
        spec = cls.deformat(example)
        if deformatted is not None:
            self.assertEqual(spec, deformatted)

    def go_valid_example_formatted(
        self: Self,
        cls: type,
        example: str,
        /,
        *,
        formatted: abc.Iterable[Any] = (),
        **kwargs: Any,
    ) -> None:
        obj: Any
        obj = cls(string=example)
        for x, y in dict(formatted).items():
            with self.subTest(spec=x, target=y):
                self.assertEqual(y, format(obj, x))

    def go_valid_example_remake(
        self: Self,
        cls: Any,
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        obj: Any
        remake: str
        spec: str
        obj = cls(string=example)
        spec = cls.deformat(example)
        remake = format(obj, spec)
        self.assertEqual(
            example,
            remake,
            msg="example=%r, remake=%r, spec=%r" % (example, remake, spec),
        )

    def go_valid_example_repr(
        self: Self,
        cls: type,
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        bool_: bool | None
        obj: Any
        repr_: str | None
        obj = cls(string=example)
        bool_ = cast(bool | None, kwargs.get("bool"))
        if bool_ is not None:
            self.assertEqual(bool(obj), bool_)
        repr_ = cast(str | None, kwargs.get("repr"))
        if repr_ is not None:
            self.assertEqual(repr(obj), repr_)

    def go_valid_example_str(
        self: Self,
        cls: type,
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        obj: Any
        answer: str
        solution: str | None
        obj = cls(string=example)
        answer = str(obj)
        self.assertEqual(answer, obj.string)
        self.assertEqual(answer, format(obj))
        self.assertEqual(answer, format(obj, ""))
        solution = cast(str | None, kwargs.get("str"))
        if solution is not None:
            self.assertEqual(str(obj), solution)

    def go_valid_example_synonym(
        self: Self,
        cls: type[Any],
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        obj: Any
        syn: str
        syn = Util.util.data["synonymous-to-empty"][cls.__name__][""][
            "synonym"
        ]
        obj = cls(string=example)
        x = format(obj, "")
        y = format(obj, syn)
        with self.subTest(msg="synonym", empty=x, synonym=y):
            self.assertEqual(x, y)

    def test_0(self: Self, /) -> None:
        x: str
        y: dict[Any, Any]
        for x, y in Util.util.examples.items():
            with self.subTest(clsname=x):
                self.go_examples(x, y)


class TestTotalAttrSetter(unittest.TestCase):

    def go_clsname(
        self: Self,
        clsname: str,
        legacy_table: dict[Any, Any],
        /,
    ) -> None:
        cls: type
        x: str
        y: dict[Any, Any]
        cls = getattr(getattr(core, clsname), clsname)
        for x, y in legacy_table.items():
            with self.subTest(legacy_name=x):
                self.go_task(cls, **y)

    def go_task(
        self: Self,
        /,
        *args: Any,
        exceptiontype: str,
        **kwargs: Any,
    ) -> None:
        if exceptiontype:
            self.go_task_invalid(*args, **kwargs, exceptiontype=exceptiontype)
        else:
            self.go_task_valid(*args, **kwargs)

    def go_task_invalid(
        self: Self,
        cls: type,
        /,
        *,
        exceptiontype: str,
        query: list[Any],
        queryname: str,
        **kwargs: Any,
    ) -> None:
        exc: type[Exception]
        obj: Any
        exc = Util.import_(exceptiontype)
        obj = cls()
        with self.assertRaises(exc):
            setattr(obj, queryname, query)

    def go_task_valid(
        self: Self,
        cls: type,
        /,
        *,
        query: list[Any],
        queryname: str,
        **_kwargs: Any,
    ) -> None:
        obj: Any
        obj = cls()
        setattr(obj, queryname, query)

    def test_0(self: Self, /) -> None:
        x: str
        y: dict[Any, Any]
        for x, y in Util.util.data["attr-setter"].items():
            with self.subTest(clsname=x):
                self.go_clsname(x, y)


class TestTotalMethod(unittest.TestCase):

    def go_clsname(
        self: Self,
        clsname: str,
        legacy_table: dict[Any, Any],
        /,
    ) -> None:
        cls: type
        x: str
        y: dict[Any, Any]
        cls = getattr(getattr(core, clsname), clsname)
        for x, y in legacy_table.items():
            with self.subTest(legacy_name=x):
                self.go_task(cls, **y)

    def go_task(
        self: Self,
        cls: type,
        /,
        *,
        args: abc.Sequence[Any] = (),
        attrname: str,
        check: list[Any] | None = None,
        kwargs: dict[Any, Any] | tuple[()] = (),
        query: list[Any],
        queryname: str,
        **_kwargs: Any,
    ) -> None:
        ans: Any
        attr: Any
        obj: Any
        obj = cls()
        setattr(obj, queryname, query)
        attr = getattr(obj, attrname)
        ans = attr(*args, **dict(kwargs))
        self.assertEqual(ans, check)

    def test_1(self: Self, /) -> None:
        x: str
        y: dict[Any, Any]
        for x, y in Util.util.data["total-method"].items():
            with self.subTest(clsname=x):
                self.go_clsname(x, y)


class TestFunction(unittest.TestCase):

    def go_clsname(
        self: Self,
        clsname: str,
        legacy_table: dict[Any, Any],
        /,
    ) -> None:
        cls: type
        x: str
        y: dict[Any, Any]
        cls = getattr(getattr(core, clsname), clsname)
        for x, y in legacy_table.items():
            with self.subTest(legacy_name=x):
                self.go_task(cls, **y)

    def go_task(
        self: Self,
        cls: type,
        /,
        *,
        args: abc.Sequence[Any] = (),
        kwargs: dict[Any, Any] | tuple[()] = (),
        query: list[Any],
        queryname: str,
        solution: Any,
        solutionname: str,
        **_kwargs: Any,
    ) -> None:
        ans: Any
        obj: Any
        obj = cls()
        setattr(obj, queryname, query)
        ans = Util.import_(solutionname)(obj, *args, **dict(kwargs))
        self.assertEqual(ans, solution)

    def test_2(self: Self, /) -> None:
        x: str
        y: dict[Any, Any]
        for x, y in Util.util.data["function"].items():
            with self.subTest(clsname=x):
                self.go_clsname(x, y)


class TestVersionEpochGo(unittest.TestCase):

    def test_0(self: Self, /) -> None:
        x: str
        y: dict[str, Any]
        for x, y in Util.util.data["epoch"][""].items():
            with self.subTest(key=x):
                self.go(**y)

    def go(
        self: Self,
        /,
        full: Any,
        part: Any,
        query: Any = None,
        key: str = "",
    ) -> None:
        msg: str
        v: Version
        msg = "epoch %r" % key
        v = Version(string="1.2.3")
        v.public.base.epoch = query
        self.assertEqual(str(v), full, msg=msg)
        self.assertIsInstance(v.public.base.epoch, int, msg=msg)
        self.assertEqual(v.public.base.epoch, part, msg=msg)


class TestSlicingGo(unittest.TestCase):

    def go_cls(self: Self, cls: type[Any], /, **kwargs: Any) -> None:
        x: str
        y: dict[str, Any]
        for x, y in kwargs.items():
            with self.subTest(key=x):
                self.go_cls_key(cls, **y)

    def go_cls_key(
        self: Self,
        cls: type[Any],
        /,
        *,
        change: Any,
        exceptiontype: str,
        query: Any,
        solution: str,
        start: Any = None,
        stop: Any = None,
        step: Any = None,
    ) -> None:
        ctx: Any
        exc: Any
        v: Any
        v = cls(string=query)
        if exceptiontype:
            exc = Util.import_(exceptiontype)
            ctx = self.assertRaises(exc)
        else:
            ctx = contextlib.nullcontext()
        with ctx:
            v[start:stop:step] = change
        self.assertEqual(str(v), solution)

    def test_2(self: Self, /) -> None:
        cls: type[Any]
        x: str
        y: dict[Any, Any]
        for x, y in Util.util.data["slicing"].items():
            cls = Util.import_(f"v440.core.{x}.{x}")
            with self.subTest(typename=x):
                self.go_cls(cls, **y)


class TestFormat(unittest.TestCase):

    def go(self: Self, text: str, /, *, valid: bool, **kwargs: Any) -> None:
        a: Version_
        b: str
        f: str
        g: str
        if not valid:
            return
        a = Version_(text)
        b = str(a)
        f = "#." * len(a.release)
        f = f[:-1]
        g = format(Version(string=text), f)
        self.assertEqual(b, g)

    def test_0(self: Self, /) -> None:
        x: str
        y: dict[str, Any]
        for x, y in Util.util.examples["Version"].items():
            with self.subTest(example=x):
                self.go(x, **y)


class TestOrder(unittest.TestCase):

    def go(
        self: Self,
        *,
        func: abc.Callable[[Any, Any], Any],
        x: str,
        y: str,
    ) -> None:
        a: Version_
        b: Version
        c: Version_
        d: Version_
        e: Version
        f: Version_
        backwards: bool
        current: bool
        legacy: bool
        a = Version_(x)
        b = Version(string=x)
        c = b.packaging
        d = Version_(y)
        e = Version(string=y)
        f = e.packaging
        legacy = func(a, d)
        current = func(b, e)
        backwards = func(c, f)
        self.assertEqual(
            current,
            legacy,
            f"operator.{func.__name__}({x!r}, {y!r}) should match for current and legacy.",
        )
        self.assertEqual(
            current,
            backwards,
            f"operator.{func.__name__}({x!r}, {y!r}) should match for current and backwards.",
        )

    def go_op(
        self: Self,
        /,
        func: abc.Callable[[Any, Any], Any],
        pure: list[str],
    ) -> None:
        i: int
        for i in range(len(pure) ** 2):
            x = pure[i // len(pure)]
            y = pure[i % len(pure)]
            with self.subTest(x=x, y=y):
                self.go(x=x, y=y, func=func)

    def test_0(self: Self, /) -> None:
        pure: list[str]
        x: str
        y: dict[str, Any]
        pure = []
        for x, y in Util.util.examples["Version"].items():
            if y["valid"]:
                pure.append(x)
        for o in ("eq", "ge", "gt", "le", "lt", "ne"):
            func = getattr(operator, o)
            with self.subTest(func=o):
                self.go_op(func=func, pure=pure)


class TestSlots(unittest.TestCase):
    def go_blob(
        self: Self,
        cls: type[Any],
        /,
        attrname: str,
        attrvalue: Any,
        string: Any = None,
    ) -> None:
        obj: Any
        obj = cls(string=string)
        with self.assertRaises(AttributeError):
            setattr(obj, attrname, attrvalue)

    def go_cls(
        self: Self, cls: type[Any], /, **typetests: dict[str, Any]
    ) -> None:
        testdict: dict[str, Any]
        testname: str
        for testname, testdict in typetests.items():
            with self.subTest(testname=testname):
                self.go_blob(cls, **testdict)

    def test_0(self: Self, /) -> None:
        cls: type[Any]
        typename: str
        typetests: dict[str, dict[str, Any]]
        for typename, typetests in Util.util.data[
            "core-non-attributes"
        ].items():
            cls = Util.import_("v440.core.{0}.{0}".format(typename))
            with self.subTest(typename=typename):
                self.go_cls(cls, **typetests)


class TestReleaseAlias(unittest.TestCase):
    def test_0(self: Self, /) -> None:
        x: Any
        y: Any
        for x, y in Util.util.data["release-key"][""].items():
            with self.subTest(test_label=x):
                self.go(**y)

    def go(self: Self, /, steps: list[Any]) -> None:
        version: Version
        step: dict[str, Any]
        version = Version()
        for step in steps:
            self.modify(version=version, **step)

    def modify(
        self: Self,
        /,
        version: Version,
        name: str,
        value: Any,
        solution: list[Any] | None = None,
    ) -> None:
        answer: list[Any]
        setattr(version.public.base.release, name, value)
        if solution is None:
            return
        answer = list(version.public.base.release)
        self.assertEqual(answer, solution)


if __name__ == "__main__":
    unittest.main()
