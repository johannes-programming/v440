import operator
import unittest

import packaging.version
from typing import *

from v440.core.Version import Version
from v440.core.VersionError import VersionError


import math
import tomllib
import unittest
from importlib import resources
from typing import *


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
    

class TestDev(unittest.TestCase):

    def test_initial_none_dev(self:Self)->None:
        v = Version("1.2.3")
        self.assertEqual(str(v), "1.2.3")
        self.assertIsNone(v.dev)

    def test_dev_as_none(self:Self)->None:
        v = Version("1.2.3")
        v.dev = None
        self.assertEqual(str(v), "1.2.3")
        self.assertIsNone(v.dev)


    def test_dev_as_tuple(self:Self)->None:
        self.dev(
            key = "test_dev_as_tuple",
            v_version = "1.2.3",
            v_dev =  ("dev", "5000"),
            v_str = "1.2.3.dev5000",
            v_ans = 5000,
        )
        
    def test_strings_a(self:Self)->None:
        devint :list= utils.get_data()["data"]["devint"]
        k:str
        v:dict
        for k, v in devint.items():
            self.dev(key=k, **v)
    
    def dev(self:Self, 
                key:str, 
                v_version:Any,
                v_dev:Any,
                v_str:Any,
                v_ans:Any, 
                dev_type:type=int,      
    ):
        v=Version(v_version)
        v.dev = v_dev
        self.assertEqual(str(v), v_str)
        self.assertIsInstance(v.dev, dev_type)
        self.assertEqual(v.dev, v_ans) 

class TestPackaging(unittest.TestCase):
    def test_strings_a(self:Self)->None:

        pure :list= utils.get_data()["data"]["valid"]

        for s in pure:
            a = packaging.version.Version(s)
            b = str(a)
            f = len(a.release)
            g = Version(s).format(f)
            self.assertEqual(b, g)

    def test_strings_b(self:Self)->None:

        pure :list= utils.get_data()["data"]["valid"]

        for s in pure:
            a = packaging.version.Version(s)
            b = Version(s).packaging()
            self.assertEqual(a, b, f"{s} should match packaging.version.Version")


    def test_strings_c(self:Self)->None:

        pure :list= utils.get_data()["data"]["valid"]
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


class TestField(unittest.TestCase):

    def test_field(self:Self)->None:
        valid = utils.get_data()["data"]["valid"] 
        incomp = utils.get_data()["data"]["incomp"]
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

    def test_exc(self:Self)->None:
        exc = utils.get_data()["data"]["exc"] 
        for x in exc:
            with self.assertRaises(VersionError):
                Version(x)



if __name__ == "__main__":
    unittest.main()
