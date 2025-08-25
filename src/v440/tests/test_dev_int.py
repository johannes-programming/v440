import unittest

from v440.core.Version import Version
from typing import *


class TestVersionDevInt(unittest.TestCase):

    def test_dev_as_int(self:Self)->None:
        v = Version("1.2.3")
        v.dev = 1
        self.assertEqual(str(v), "1.2.3.dev1")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 1)

    def test_dev_as_string_int(self:Self)->None:
        v = Version("1.2.3")
        v.dev = "42"
        self.assertEqual(str(v), "1.2.3.dev42")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 42)

    def test_dev_as_string_with_dev_prefix(self:Self)->None:
        v = Version("1.2.3")
        v.dev = "dev1000"
        self.assertEqual(str(v), "1.2.3.dev1000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 1000)

    def test_dev_as_string_with_dev_dot_prefix(self:Self)->None:
        v = Version("1.2.3")
        v.dev = "dev.2000"
        self.assertEqual(str(v), "1.2.3.dev2000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 2000)

    def test_dev_as_string_with_dot_dev_prefix(self:Self)->None:
        v = Version("1.2.3")
        v.dev = ".dev.3000"
        self.assertEqual(str(v), "1.2.3.dev3000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 3000)

    def test_dev_as_string_with_dot_dev_number_prefix(self:Self)->None:
        v = Version("1.2.3")
        v.dev = ".dev4000"
        self.assertEqual(str(v), "1.2.3.dev4000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 4000)

    def test_dev_as_tuple(self:Self)->None:
        v = Version("1.2.3")
        v.dev = ("dev", "5000")
        self.assertEqual(str(v), "1.2.3.dev5000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 5000)

    def test_dev_as_list(self:Self)->None:
        v = Version("1.2.3")
        v.dev = ["dev", "6000"]
        self.assertEqual(str(v), "1.2.3.dev6000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 6000)

    def test_dev_as_uppercase_string(self:Self)->None:
        v = Version("1.2.3")
        v.dev = "DEV7000"
        self.assertEqual(str(v), "1.2.3.dev7000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 7000)

    def test_dev_as_mixed_case_string(self:Self)->None:
        v = Version("1.2.3")
        v.dev = "dEv8000"
        self.assertEqual(str(v), "1.2.3.dev8000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 8000)

    def test_dev_as_list_mixed_case(self:Self)->None:
        v = Version("1.2.3")
        v.dev = ["dEV", "9000"]
        self.assertEqual(str(v), "1.2.3.dev9000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 9000)

    def test_dev_as_false(self:Self)->None:
        v = Version("1.2.3")
        v.dev = False
        self.assertEqual(str(v), "1.2.3.dev0")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 0)

    def test_dev_as_true(self:Self)->None:
        v = Version("1.2.3")
        v.dev = True
        self.assertEqual(str(v), "1.2.3.dev1")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 1)


