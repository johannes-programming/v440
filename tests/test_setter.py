"""Test transactional property setters."""

__all__: list[str] = ["TestSetter"]

import unittest
from typing import Any, Self

from v440.abc.CoreABC import CoreABC
from v440.abc.QualABC import QualABC
from v440.core.Base import Base
from v440.core.Dev import Dev
from v440.core.Local import Local
from v440.core.Post import Post
from v440.core.Pre import Pre
from v440.core.Public import Public
from v440.core.Qual import Qual
from v440.core.Release import Release
from v440.core.Version import Version
from v440.errors.VersionError import VersionError


class TestSetter(unittest.TestCase):
    def test_core_abc_does_not_override_setattr(self: Self, /) -> None:
        self.assertNotIn("__setattr__", CoreABC.__dict__)

    def test_failed_setter_restores_instance(self: Self, /) -> None:
        version: Version
        version = Version(string="1.2.3")
        with self.assertRaises(VersionError):
            version.public.base.epoch = -1
        self.assertEqual(str(version), "1.2.3")

    def test_type_error_passes_through_and_restores_instance(
        self: Self,
        /,
    ) -> None:
        value: Any
        version: Version
        value = 1.5
        version = Version(string="1.2.3")
        with self.assertRaises(TypeError):
            version.public.base.epoch = value
        self.assertEqual(str(version), "1.2.3")
