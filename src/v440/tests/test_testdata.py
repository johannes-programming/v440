import math
import operator
import tomllib
import unittest
from importlib import resources
from typing import *

import packaging.version

from v440.core.Version import Version
from v440.core.VersionError import VersionError


class utils:
    def get_data() -> dict:
        text: str = resources.read_text("v440.tests", "testdata.toml")
        data: dict = tomllib.loads(text)
        return data

    def istestable(x: Any) -> bool:
        if not isinstance(x, float):
            return True
        if not math.isnan(x):
            return True
        return False
    

class TestDataProperty(unittest.TestCase):
    def test_data(self: Self) -> None:
        self.v = Version()
        data:dict = utils.get_data()
        prop:dict = data["data"]["data_property"]
        for k, v in prop.items():
            self.data(**v, key=k)
        self.data(query=None, solution="0")
    
    def data(self:Self,
        query:Any,
        solution:str,
        key:str="",
    )->None:
        self.v.data = query
        self.assertEqual(solution, str(self.v))
        self.assertEqual(self.v.data, str(self.v))
        self.assertEqual(type(self.v.data), str)


class TestVersionRelease(unittest.TestCase):

    def setUp(self: Self) -> None:
        # Create a version class instance
        self.version = Version()

    def test_0(self: Self) -> None:
        data: dict = utils.get_data()
        release: dict = data["data"]["release"]
        for k, v in release.items():
            self.release(key=k, **v)

    def release(self: Self, query: Any, solution: Any, key: str = "") -> None:
        self.version.release = query
        self.assertEqual(self.version.release, solution)


class TestDev(unittest.TestCase):

    def test_initial_none_dev(self: Self) -> None:
        v = Version("1.2.3")
        self.assertEqual(str(v), "1.2.3")
        self.assertIsNone(v.dev)

    def test_dev_as_none(self: Self) -> None:
        v = Version("1.2.3")
        v.dev = None
        self.assertEqual(str(v), "1.2.3")
        self.assertIsNone(v.dev)

    def test_dev_as_tuple(self: Self) -> None:
        self.dev(
            key="test_dev_as_tuple",
            v_version="1.2.3",
            v_dev=("dev", "5000"),
            v_str="1.2.3.dev5000",
            v_ans=5000,
        )

    def test_strings_a(self: Self) -> None:
        devint: list = utils.get_data()["data"]["devint"]
        k: str
        v: dict
        for k, v in devint.items():
            self.dev(key=k, **v)

    def dev(
        self: Self,
        key: str,
        v_version: Any,
        v_dev: Any,
        v_str: Any,
        v_ans: Any,
        dev_type: type = int,
    ):
        v = Version(v_version)
        v.dev = v_dev
        self.assertEqual(str(v), v_str)
        self.assertIsInstance(v.dev, dev_type)
        self.assertEqual(v.dev, v_ans)


class TestVersionSpecifiers(unittest.TestCase):

    def test_version_with_invalid_specifiers(self: Self) -> None:
        # Test version with invalid specifiers that should raise an error
        with self.assertRaises(VersionError):
            Version("1.2.3--4")

        with self.assertRaises(VersionError):
            Version("1.2.3a1--4")

    def test_spec_toml(self: Self) -> None:
        data = utils.get_data()
        spec = data["data"]["spec"]
        for k, v in spec.items():
            self.spec(**v, key=k)

    def spec(self: Self, string_a: str, string_b: str, key: str = "") -> None:
        version = Version(string_a)
        self.assertEqual(str(version), string_b)


class TestPackaging(unittest.TestCase):
    def test_strings_a(self: Self) -> None:
        data:dict = utils.get_data()
        strings:dict = data["data"]["strings"]
        pure: list = strings["valid"]

        for s in pure:
            a = packaging.version.Version(s)
            b = str(a)
            f = len(a.release)
            g = Version(s).format(f)
            self.assertEqual(b, g)

    def test_strings_b(self: Self) -> None:
        data:dict = utils.get_data()
        strings:dict = data["data"]["strings"]
        pure: list = strings["valid"]

        for s in pure:
            a = packaging.version.Version(s)
            b = Version(s).packaging()
            self.assertEqual(a, b, f"{s} should match packaging.version.Version")

    def test_strings_c(self: Self) -> None:
        data:dict = utils.get_data()
        strings:dict = data["data"]["strings"]
        pure: list = strings["valid"]
        ops = [
            operator.eq,
            operator.ne,
            operator.gt,
            operator.ge,
            operator.le,
            operator.lt,
        ]
        for x in pure:
            a = packaging.version.Version(x)
            b = Version(x).packaging()
            for y in pure:
                c = packaging.version.Version(y)
                d = Version(y).packaging()
                for op in ops:
                    self.assertEqual(
                        op(a, c),
                        op(b, d),
                        f"{op} should match for {x!r} and {y!r}",
                    )

    def test_field(self: Self) -> None:
        data:dict = utils.get_data()
        strings:dict = data["data"]["strings"]
        valid: list = strings["valid"]
        incomp: list = strings["incomp"]
        versionable = valid + incomp
        version_obj = Version()
        for x in versionable:
            v = Version(x)
            self.assertEqual(v.isdevrelease(), v.packaging().is_devrelease)
            self.assertEqual(v.isprerelease(), v.packaging().is_prerelease)
            self.assertEqual(v.ispostrelease(), v.packaging().is_postrelease)
            self.assertEqual(str(v.base), v.packaging().base_version)
            self.assertEqual(str(v.public), v.packaging().public)
            version_obj.local = v.packaging().local
            self.assertEqual(str(v.local), str(version_obj.local))

    def test_exc(self: Self) -> None:
        data:dict = utils.get_data()
        strings:dict = data["data"]["strings"]
        exc: list = strings["exc"]
        for x in exc:
            with self.assertRaises(VersionError):
                Version(x)


if __name__ == "__main__":
    unittest.main()
