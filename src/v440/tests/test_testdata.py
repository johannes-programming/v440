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
from v440.core.Release import Release
from v440.core.Version import Version
from v440.core.VersionError import VersionError


class Util(enum.Enum):
    util = None

    @functools.cached_property
    def data(self: Self) -> dict:
        text: str = resources.read_text("v440.tests", "testdata.toml")
        data: dict = tomllib.loads(text)
        return data


class TestVersionReleaseAttrs(unittest.TestCase):

    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["release_attr"].items():
            with self.subTest(key=k):
                self.go(**v)

    def go(
        self: Self,
        query: list,
        attrname: Optional[str] = None,
        args: list | tuple = (),
        kwargs: dict | tuple = (),
        target: Optional[list] = None,
        solution: Any = None,
    ) -> None:
        # Test the append method of the release list-like object
        version: Version = Version()
        version.public.base.release = query
        if attrname is not None:
            attr: Any = getattr(version.public.base.release, attrname)
            ans: Any = attr(*args, **dict(kwargs))
            self.assertEqual(ans, solution)
        if target is not None:
            self.assertEqual(version.public.base.release, target)


class TestVersionReleaseVersionError(unittest.TestCase):

    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["release_VersionError"].items():
            with self.subTest(key=k):
                self.go(**v)

    def go(
        self: Self,
        query: list,
    ) -> None:
        version: Version = Version()
        with self.assertRaises(VersionError):
            version.public.base.release = query


class TestVersionLocalVersionError(unittest.TestCase):

    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["local_VersionError"].items():
            with self.subTest(key=k):
                self.go(**v)

    def go(
        self: Self,
        query: list,
    ) -> None:
        version: Version = Version()
        with self.assertRaises(VersionError):
            version.local = query


class TestVersionLocalGo(unittest.TestCase):
    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["local-attr"].items():
            with self.subTest(key=k):
                self.go(**v)

    def go(
        self: Self,
        query: list,
        attrname: Optional[str] = None,
        args: list | tuple = (),
        kwargs: dict | tuple = (),
        target: Optional[list] = None,
        solution: Any = None,
    ) -> None:
        version: Version = Version()
        version.local = query
        if attrname is not None:
            attr: Any = getattr(version.local, attrname)
            ans: Any = attr(*args, **dict(kwargs))
            self.assertEqual(ans, solution)
        if target is not None:
            self.assertEqual(version.local, target)


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
    def test_slicing_3(self: Self) -> None:
        sli: dict = Util.util.data["slicingmethod"]
        k: str
        v: dict
        for k, v in sli.items():
            self.go(**v, key=k)

    def go(
        self: Self,
        query: Any,
        change: Any,
        solution: str,
        start: Any = None,
        stop: Any = None,
        step: Any = None,
        key: str = "",
    ) -> None:
        v: Version = Version(query)
        v.public.base.release[start:stop:step] = change
        self.assertEqual(str(v), solution, "slicingmethod %s" % key)


class TestDataProperty(unittest.TestCase):
    def test_data(self: Self) -> None:
        for k, v in Util.util.data["data-property"].items():
            self.go(**v, key=k)

    def go(
        self: Self,
        query: Any = None,
        solution: Any = None,
        key: str = "",
    ) -> None:
        msg: str = "data-property %r" % key
        version: Version = Version()
        version.data = query
        self.assertEqual(solution, str(version), msg=msg)


class TestVersionRelease(unittest.TestCase):

    def test_0(self: Self) -> None:
        k: str
        v: Any
        for k, v in Util.util.data["release"].items():
            with self.subTest(key=k):
                self.go(**v)

    def go(self: Self, query: Any, solution: Any) -> None:
        release: Release = Release(query)
        self.assertEqual(release, solution)


class TestDevGo(unittest.TestCase):
    def test_dev_as_tuple(self: Self) -> None:
        self.go(
            key="test_dev_as_tuple",
            v_version="1.2.3",
            v_dev=("dev", "5000"),
            v_str="1.2.3.dev5000",
            v_ans=5000,
        )

    def test_strings_a(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["devint"].items():
            with self.subTest(key=k):
                self.go(**v, key=k)

    def go(
        self: Self,
        key: str,
        v_version: Any,
        v_str: Any,
        v_ans: Any,
        v_dev: Any = None,
        dev_type: type = int,
    ):
        msg: str = "dev %r" % key
        v: Version = Version(v_version)
        v.public.qual.dev = v_dev
        self.assertEqual(str(v), v_str, msg=msg)
        self.assertIsInstance(v.public.qual.dev, dev_type, msg=msg)
        self.assertEqual(v.public.qual.dev, v_ans, msg=msg)


class TestVersionSpecifiersGo(unittest.TestCase):

    def test_spec_toml(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["spec"].items():
            self.go(**v, key=k)

    def go(self: Self, string_a: str, string_b: str, key: str = "") -> None:
        msg: str = "spec %r" % key
        version: Version = Version(string_a)
        self.assertEqual(str(version), string_b, msg=msg)


class TestPackagingA(unittest.TestCase):
    def test_strings_a(self: Self) -> None:
        s: str
        x: str
        y: list
        for x, y in Util.util.data["strings"]["valid"].items():
            for s in y:
                with self.subTest(key=x):
                    self.go(text=s)

    def go(self: Self, text: str) -> None:
        a: packaging.version.Version
        b: str
        f: int
        g: str
        a = packaging.version.Version(text)
        b = str(a)
        f = len(a.release)
        g = Version(text).format(f)
        self.assertEqual(b, g)


class TestPackagingB(unittest.TestCase):
    def test_strings_b(self: Self) -> None:
        a: packaging.version.Version
        b: packaging.version.Version
        s: str
        msg: str
        x: str
        y: list
        for x, y in Util.util.data["strings"]["valid"].items():
            for s in y:
                a = packaging.version.Version(s)
                b = Version(s).packaging()
                msg = f"{s} should match packaging.version.Version"
                self.assertEqual(a, b, msg=msg)


class TestPackagingC(unittest.TestCase):
    def test_strings_c(self: Self) -> None:
        pure: list = list()
        l: list
        for l in Util.util.data["strings"]["valid"].values():
            pure += l
        ops: list = [
            operator.eq,
            operator.ne,
            operator.gt,
            operator.ge,
            operator.le,
            operator.lt,
        ]
        a: packaging.version.Version
        b: packaging.version.Version
        c: packaging.version.Version
        d: packaging.version.Version
        native: bool
        convert: bool
        msg: str
        op: Any
        for x, y, op in iterprod.iterprod(pure, pure, ops):
            a = packaging.version.Version(x)
            b = Version(x).packaging()
            c = packaging.version.Version(y)
            d = Version(y).packaging()
            native = op(a, c)
            convert = op(b, d)
            msg = f"{op} should match for {x!r} and {y!r}"
            self.assertEqual(native, convert, msg=msg)


class TestPackagingField(unittest.TestCase):
    def test_field(self: Self) -> None:
        versionable: list = list()
        l: list
        for l in Util.util.data["strings"]["valid"].values():
            versionable += l
        for l in Util.util.data["strings"]["incomp"].values():
            versionable += l
        version_obj: Version = Version()
        v: Version
        x: str
        for x in versionable:
            v = Version(x)
            self.assertEqual(v.public.qual.isdevrelease(), v.packaging().is_devrelease)
            self.assertEqual(v.public.qual.isprerelease(), v.packaging().is_prerelease)
            self.assertEqual(
                v.public.qual.ispostrelease(), v.packaging().is_postrelease
            )
            self.assertEqual(str(v.public.base), v.packaging().base_version)
            self.assertEqual(str(v.public), v.packaging().public)
            version_obj.local = v.packaging().local
            self.assertEqual(str(v.local), str(version_obj.local))


class TestPackagingExc(unittest.TestCase):
    def test_exc_pack(self: Self) -> None:
        impure: list = list()
        l: list
        for l in Util.util.data["strings"]["incomp"].values():
            impure += l
        for l in Util.util.data["strings"]["exc"].values():
            impure += l
        x: str
        for x in impure:
            with self.assertRaises(packaging.version.InvalidVersion):
                packaging.version.Version(x)


class TestExc(unittest.TestCase):
    def test_exc(self: Self) -> None:
        x: str
        y: list
        for x, y in Util.util.data["strings"]["exc"].items():
            with self.subTest(test_label=x):
                self.go(queries=y)

    def go(self: Self, queries: list) -> None:
        x: str
        for x in queries:
            with self.assertRaises(VersionError):
                Version(x)


class TestSlots(unittest.TestCase):
    def test_slots(self: Self) -> None:
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
        data: Any = None,
        isimported: Optional[bool] = False,
    ) -> None:
        cls: type
        if isimported:
            cls = getattr(core, clsname)
        else:
            cls = getattr(getattr(core, clsname), clsname)
        obj: Any = cls(data)
        with self.assertRaises(AttributeError):
            setattr(obj, attrname, attrvalue)


if __name__ == "__main__":
    unittest.main()
