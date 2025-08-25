import unittest

from v440.core.Version import Version
from typing import *


class TestVersionDevNonInt(unittest.TestCase):

    def test_initial_none_dev(self:Self)->None:
        v = Version("1.2.3")
        self.assertEqual(str(v), "1.2.3")
        self.assertIsNone(v.dev)

    def test_dev_as_none(self:Self)->None:
        v = Version("1.2.3")
        v.dev = None
        self.assertEqual(str(v), "1.2.3")
        self.assertIsNone(v.dev)
