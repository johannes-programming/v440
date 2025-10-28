import enum
import functools
import operator
import tomllib
import unittest
from importlib import resources
from typing import *

import iterprod
import packaging.version

from v440 import core
from v440.core.Version import Version
from v440.core.VersionError import VersionError


class Util(enum.Enum):
    util = None

    @functools.cached_property
    def data(self: Self) -> dict:
        text: str = resources.read_text("v440.tests", "testdata.toml")
        data: dict = tomllib.loads(text)
        return data


class TestDeformatting(unittest.TestCase):
    def test_0(self: Self) -> None:
        x: str
        y: dict
        for x, y in Util.util.data["deformatting"].items():
            with self.subTest(clsname=x):
                self.go_examples(x, y)

    def go_examples(self: Self, clsname: str, tables: dict) -> None:
        cls: type = getattr(getattr(core, clsname), clsname)
        split: dict = {False: dict(), True: dict()}
        x: str
        y: dict
        for x, y in tables.items():
            split[y["valid"]][tuple(x.split())] = y
        for x, y in split[False].items():
            with self.subTest(valid=False, example=x):
                self.go_invalid_example(cls, x, **y)
        for x, y in split[True].items():
            with self.subTest(valid=True, example=x):
                self.go_valid_example(cls, x, **y)

    def go_invalid_example(
        self: Self, cls: type, example: tuple[str], /, **kwargs: Any
    ) -> None:
        with self.assertRaises(TypeError):
            cls.deformat(*example)

    def go_valid_example(
        self: Self,
        cls: type,
        example: tuple[str],
        /,
        *,
        solution: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if solution is not None:
            self.assertEqual(solution, cls.deformat(*example))


class TestStringExamples(unittest.TestCase):
    def test_versions(self: Self) -> None:
        x: str
        y: dict
        for x, y in Util.util.data["examples"]["Version"].items():
            with self.subTest(example=x):
                self.go_version(x, **y)

    def go_version(self: Self, example: str, /, *, valid: bool, **kwargs: Any) -> None:
        if not valid:
            with self.assertRaises(packaging.version.InvalidVersion):
                packaging.version.Version(example)
            return
        s: str
        x: Version = Version(example)
        y: packaging.version.Version = packaging.version.Version(example)
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

    def test_0(self: Self) -> None:
        x: str
        y: dict
        for x, y in Util.util.data["examples"].items():
            with self.subTest(clsname=x):
                self.go_examples(x, y)

    def go_examples(self: Self, clsname: str, tables: dict) -> None:
        cls: type = getattr(getattr(core, clsname), clsname)
        split: dict = {False: dict(), True: dict()}
        x: str
        y: dict
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
            cls(example)

    def go_valid_example(
        self: Self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.go_valid_example_string(*args, **kwargs)
        self.go_valid_example_normed(*args, **kwargs)
        self.go_valid_example_formatted(*args, **kwargs)
        self.go_valid_example_deformatted(*args, **kwargs)
        self.go_valid_example_remake(*args, **kwargs)

    def go_valid_example_string(
        self: Self, cls: type, example: str, /, **kwargs
    ) -> None:
        obj: Any = cls(example)
        self.assertEqual(str(obj), obj.string)
        self.assertEqual(str(obj), format(obj))
        self.assertEqual(str(obj), format(obj, ""))

    def go_valid_example_normed(
        self: Self,
        cls: type,
        example: str,
        /,
        *,
        normed: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        obj: Any = cls(example)
        if normed is not None:
            self.assertEqual(obj.string, normed)

    def go_valid_example_formatted(
        self: Self,
        cls: type,
        example: str,
        /,
        *,
        formatted: Iterable = (),
        **kwargs: Any,
    ) -> None:
        obj: Any = cls(example)
        for x, y in dict(formatted).items():
            with self.subTest(spec=x, target=y):
                self.assertEqual(y, format(obj, x))

    def go_valid_example_deformatted(
        self: Self,
        cls: type,
        example: str,
        /,
        *,
        deformatted: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        spec: str = cls.deformat(example)
        if deformatted is not None:
            self.assertEqual(spec, deformatted)

    def go_valid_example_remake(
        self: Self,
        cls: type,
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        obj: Any = cls(example)
        spec: str = cls.deformat(example)
        remake: str = format(obj, spec)
        self.assertEqual(
            example,
            remake,
            msg="example=%r, remake=%r, spec=%r" % (example, remake, spec),
        )


class TestVersionReleaseAttrs(unittest.TestCase):

    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["release-data"].items():
            with self.subTest(key=k):
                self.go_data(**v)

    def go_data(
        self: Self,
        query: list,
        attrname: Optional[str] = None,
        args: list | tuple = (),
        kwargs: dict | tuple = (),
        target: Optional[list] = None,
        solution: Any = None,
        queryname: str = "data",
    ) -> None:
        # Test the append method of the release list-like object
        version: Version = Version()
        setattr(version.public.base.release, queryname, query)
        if attrname is not None:
            attr: Any = getattr(version.public.base.release, attrname)
            ans: Any = attr(*args, **dict(kwargs))
            self.assertEqual(ans, solution)
        if target is not None:
            ans: list = list(version.public.base.release)
            self.assertEqual(ans, target)


class TestDataSetter(unittest.TestCase):

    def test_0(self: Self) -> None:
        x: str
        y: dict
        for x, y in Util.util.data["data-setter"].items():
            with self.subTest(clsname=x):
                self.go_clsname(x, y)

    def go_clsname(
        self: Self,
        clsname: str,
        legacy_table: dict,
        /,
    ) -> None:
        cls: type = getattr(getattr(core, clsname), clsname)
        x: str
        y: dict
        for x, y in legacy_table.items():
            with self.subTest(legacy_name=x):
                self.go_task(cls, **y)

    def go_task(
        self: Self,
        *args: Any,
        valid: bool,
        **kwargs: Any,
    ) -> None:
        if valid:
            self.go_valid(*args, **kwargs)
        else:
            self.go_invalid(*args, **kwargs)

    def go_invalid(
        self: Self,
        cls: type,
        /,
        *,
        query: list,
        queryname: str = "data",
        **kwargs: Any,
    ) -> None:
        obj: Any = cls()
        with self.assertRaises(VersionError):
            setattr(obj, queryname, query)

    def go_valid(
        self: Self,
        cls: type,
        /,
        *,
        query: list,
        queryname: str = "data",
        check: Optional[list] = None,
        attrname: Optional[str] = None,
        args: list | tuple = (),
        kwargs: dict | tuple = (),
        solution: Optional[list] = None,
        **_kwargs: Any,
    ) -> None:
        ans: Any
        attr: Any
        obj: Any
        obj = cls()
        setattr(obj, queryname, query)
        if attrname is not None:
            attr = getattr(obj, attrname)
            ans = attr(*args, **dict(kwargs))
            self.assertEqual(ans, check)
        if solution is not None:
            ans = list(obj)
            self.assertEqual(ans, solution)


class TestVersionEpochGo(unittest.TestCase):

    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["epoch"].items():
            with self.subTest(key=k):
                self.go(**v)

    def go(
        self: Self,
        full: Any,
        part: Any,
        query: Any = None,
        key: str = "",
    ) -> None:
        msg: str = "epoch %r" % key
        v: Version = Version("1.2.3")
        v.public.base.epoch = query
        self.assertEqual(str(v), full, msg=msg)
        self.assertIsInstance(v.public.base.epoch, int, msg=msg)
        self.assertEqual(v.public.base.epoch, part, msg=msg)


class TestSlicingGo(unittest.TestCase):
    def test_0(self: Self) -> None:
        sli: dict = Util.util.data["slicingmethod"]
        k: str
        v: dict
        for k, v in sli.items():
            with self.subTest(key=k):
                self.go(**v)

    def go(
        self: Self,
        query: Any,
        change: Any,
        solution: str,
        start: Any = None,
        stop: Any = None,
        step: Any = None,
    ) -> None:
        v: Version = Version(query)
        v.public.base.release[start:stop:step] = change
        self.assertEqual(str(v), solution)


class TestDataProperty(unittest.TestCase):
    def test_0(self: Self) -> None:
        for k, v in Util.util.data["data-property"].items():
            with self.subTest(key=k):
                self.go(**v, key=k)

    def go(
        self: Self,
        query: Any = None,
        solution: Any = None,
        key: str = "",
    ) -> None:
        msg: str = "data-property %r" % key
        version: Version = Version()
        version.string = query
        self.assertEqual(solution, str(version), msg=msg)


class TestPackagingA(unittest.TestCase):
    def test_0(self: Self) -> None:
        x: str
        y: list
        for x, y in Util.util.data["examples"]["Version"].items():
            with self.subTest(example=x):
                self.go(x, **y)

    def go(self: Self, text: str, /, *, valid: bool, **kwargs: Any) -> None:
        if not valid:
            return
        self.go_format(text)

    def go_format(self: Self, text: str) -> None:
        a: packaging.version.Version = packaging.version.Version(text)
        b: str = str(a)
        f: str = "#." * len(a.release)
        f = f[:-1]
        g: str = format(Version(text), f)
        self.assertEqual(b, g)


class TestPackagingC(unittest.TestCase):
    def test_0(self: Self) -> None:
        pure: list = list()
        for x, y in Util.util.data["examples"]["Version"].items():
            if y["valid"]:
                pure.append(x)
        ops: list = [
            operator.eq,
            operator.ne,
            operator.gt,
            operator.ge,
            operator.le,
            operator.lt,
        ]
        args: tuple
        for args in iterprod.iterprod(pure, pure, ops):
            with self.subTest(args=args):
                self.go(*args)

    def go(self: Self, x: str, y: str, func: Callable, /) -> None:
        a: packaging.version.Version = packaging.version.Version(x)
        b: packaging.version.Version = Version(string=x).packaging
        c: packaging.version.Version = packaging.version.Version(y)
        d: packaging.version.Version = Version(string=y).packaging
        native: bool = func(a, c)
        convert: bool = func(b, d)
        msg: str = f"{func} should match for {x!r} and {y!r}"
        self.assertEqual(native, convert, msg=msg)


class TestSlots(unittest.TestCase):
    def test_0(self: Self) -> None:
        x: Any
        y: Any
        for x, y in Util.util.data["core-non-attributes"].items():
            with self.subTest(test_label=x):
                self.go(**y)

    def go(
        self: Self,
        clsname: str,
        attrname: str,
        attrvalue: Any,
        string: Any = None,
    ) -> None:
        cls: type = getattr(getattr(core, clsname), clsname)
        obj: Any = cls(string=string)
        with self.assertRaises(AttributeError):
            setattr(obj, attrname, attrvalue)


class TestReleaseAlias(unittest.TestCase):
    def test_0(self: Self) -> None:
        x: Any
        y: Any
        for x, y in Util.util.data["release-key"].items():
            with self.subTest(test_label=x):
                self.go(**y)

    def go(self: Self, steps: list) -> None:
        version: Version = Version()
        step: dict
        for step in steps:
            self.modify(version=version, **step)

    def modify(
        self: Self,
        version: Version,
        name: str,
        value: Any,
        solution: Optional[list] = None,
    ) -> None:
        setattr(version.public.base.release, name, value)
        if solution is None:
            return
        answer: list = list(version.public.base.release)
        self.assertEqual(answer, solution)


if __name__ == "__main__":
    unittest.main()
