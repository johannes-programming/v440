import unittest
from typing import *

from v440.core.Local import Local
from v440.core.Qual import Qual
from v440.core.Version import Version
from v440.core.VersionError import VersionError


class TestVersionManipulation(unittest.TestCase):

    def test_version_modification(self: Self) -> None:
        # Create an instance of the v440.Version class
        v: Version = Version("1.2.3")

        # Modify individual parts of the version
        v.public.base.release.major = 2
        v.public.base.release.minor = 5
        v.public.qual = "beta.1"
        v.local = "local.7.dev"

        # Verify the expected output
        self.assertEqual(str(v), "2.5.3b1+local.7.dev")


class TestVersionLocal(unittest.TestCase):

    def test_version_operations(self: Self) -> None:
        v: Version = Version("1.2.3")
        backup: Local = v.local
        v.local = "local.1.2.3"
        self.assertEqual(str(v), "1.2.3+local.1.2.3")
        self.assertEqual(str(v.local), "local.1.2.3")
        v.local.append("extra")
        self.assertEqual(str(v), "1.2.3+local.1.2.3.extra")
        self.assertEqual(str(v.local), "local.1.2.3.extra")
        v.local.remove(1)
        self.assertEqual(str(v), "1.2.3+local.2.3.extra")
        self.assertEqual(str(v.local), "local.2.3.extra")
        self.assertEqual(v.local[0], "local")
        self.assertEqual(v.local[-1], "extra")
        v.local.sort()
        self.assertEqual(str(v), "1.2.3+extra.local.2.3")
        self.assertEqual(str(v.local), "extra.local.2.3")
        v.local.clear()
        self.assertEqual(str(v), "1.2.3")
        self.assertEqual(str(v.local), "")
        v.local = "reset.1.2"
        self.assertEqual(str(v), "1.2.3+reset.1.2")
        self.assertEqual(str(v.local), "reset.1.2")
        self.assertTrue(v.local is backup)


class TestPre(unittest.TestCase):

    def test_pre(self: Self) -> None:
        v: Version = Version("1.2.3")
        backup: Qual = v.public.qual

        # Initial version, no pre-release version
        self.assertEqual(str(v), "1.2.3")
        self.assertEqual(v.public.qual, [None, None, None, None])

        # Set pre-release version to "a1"
        v.public.qual = "a1"
        self.assertEqual(str(v), "1.2.3a1")
        self.assertEqual(str(v.public.qual), "a1")

        # Modify pre-release phase to "preview"
        v.public.qual.prephase = "preview"
        self.assertEqual(str(v), "1.2.3rc1")
        self.assertEqual(str(v.public.qual), "rc1")

        # Modify subphase to "42"
        v.public.qual.presubphase = "42"
        self.assertEqual(str(v), "1.2.3rc42")
        self.assertEqual(str(v.public.qual), "rc42")

        # Change phase to a formatted string "BeTa"
        v.public.qual.prephase = """
        BeTa
        """
        self.assertEqual(str(v), "1.2.3b42")
        self.assertEqual(str(v.public.qual), "b42")

        self.assertEqual(v.public.qual, backup)

        # Set pre-release to None
        v.public.qual = None
        self.assertEqual(str(v), "1.2.3")
        self.assertEqual(v.public.qual, [None, None, None, None])


class TestExample(unittest.TestCase):

    def test_example_1(self: Self) -> None:
        v: Version = Version("v1.0.0")
        self.assertEqual(str(v), "1")  # Initial version
        self.assertEqual(v.format("3"), "1.0.0")  # Initial version formatted

    def test_example_2(self: Self) -> None:
        v: Version = Version("2.5.3")
        self.assertEqual(str(v), "2.5.3")  # Modified version
        v.public.base.release[1] = 64
        v.public.base.release.micro = 4
        self.assertEqual(str(v), "2.64.4")  # Further modified version

    def test_example_3a(self: Self) -> None:
        v1: Version = Version("1.6.3")
        v2: str = "1.6.4"
        self.assertEqual(str(v1), "1.6.3")  # v1
        self.assertEqual(str(v2), "1.6.4")  # v2
        self.assertFalse(v1 == v2)  # v1 == v2 gives False
        self.assertTrue(v1 != v2)  # v1 != v2 gives True
        self.assertFalse(v1 >= v2)  # v1 >= v2 gives False
        self.assertTrue(v1 <= v2)  # v1 <= v2 gives True
        self.assertFalse(v1 > v2)  # v1 > v2 gives False
        self.assertTrue(v1 < v2)  # v1 < v2 gives True

    def test_example_3b(self: Self) -> None:
        v1: str = "1.6.3"
        v2: Version = Version("1.6.4")
        self.assertEqual(str(v1), "1.6.3")  # v1
        self.assertEqual(str(v2), "1.6.4")  # v2
        self.assertFalse(v1 == v2)  # v1 == v2 gives False
        self.assertTrue(v1 != v2)  # v1 != v2 gives True
        self.assertFalse(v1 >= v2)  # v1 >= v2 gives False
        self.assertTrue(v1 <= v2)  # v1 <= v2 gives True
        self.assertFalse(v1 > v2)  # v1 > v2 gives False
        self.assertTrue(v1 < v2)  # v1 < v2 gives True

    def test_example_3c(self: Self) -> None:
        v1: Version = Version("1.6.3")
        v2: Version = Version("1.6.4")
        self.assertEqual(str(v1), "1.6.3")  # v1
        self.assertEqual(str(v2), "1.6.4")  # v2
        self.assertFalse(v1 == v2)  # v1 == v2 gives False
        self.assertTrue(v1 != v2)  # v1 != v2 gives True
        self.assertFalse(v1 >= v2)  # v1 >= v2 gives False
        self.assertTrue(v1 <= v2)  # v1 <= v2 gives True
        self.assertFalse(v1 > v2)  # v1 > v2 gives False
        self.assertTrue(v1 < v2)  # v1 < v2 gives True

    def test_example_4(self: Self) -> None:
        v: Version = Version("2.5.3.9")
        self.assertEqual(str(v), "2.5.3.9")  # before sorting
        v.public.base.release.sort()
        self.assertEqual(str(v), "2.3.5.9")  # after sorting

    def test_example_5(self: Self) -> None:
        v: Version = Version("2.0.0-alpha.1")
        self.assertEqual(str(v), "2a1")  # Pre-release version
        v.public.qual.pre = "beta.2"
        self.assertEqual(str(v), "2b2")  # Modified pre-release version
        with self.assertRaises(Exception):
            v.public.qual.pre[1] = 4
        self.assertEqual(str(v), "2b2")  # Further modified pre-release version
        v.public.qual.prephase = "PrEvIeW"
        self.assertEqual(str(v), "2rc2")  # Even further modified pre-release version

    def test_example_6(self: Self) -> None:
        v: Version = Version("1.2.3")
        v.public.qual.post = "post1"
        v.local = "local.7.dev"
        self.assertEqual(str(v), "1.2.3.post1+local.7.dev")  # Post-release version
        self.assertEqual(v.format("-1"), "1.2.post1+local.7.dev")  # Formatted version
        v.public.qual.post = "post.2"
        self.assertEqual(str(v), "1.2.3.post2+local.7.dev")  # Modified version
        v.public.qual.post = None
        self.assertEqual(str(v), "1.2.3+local.7.dev")  # Modified without post
        v.public.qual.post = "post", 3
        v.local.sort()
        self.assertEqual(str(v), "1.2.3.post3+dev.local.7")  # After sorting local
        v.local.append(8)
        self.assertEqual(str(v), "1.2.3.post3+dev.local.7.8")  # Modified with new local
        v.local = "3.test.19"
        self.assertEqual(str(v), "1.2.3.post3+3.test.19")  # Modified local again

    def test_example_7(self: Self) -> None:
        v: Version = Version("5.0.0")
        self.assertEqual(str(v), "5")  # Original version
        v.data = None
        self.assertEqual(str(v), "0")  # After reset
        v.public.base = "4!5.0.1"
        self.assertEqual(str(v), "4!5.0.1")  # Before error
        with self.assertRaises(VersionError):
            v.public.base = "9!x"
        self.assertEqual(str(v), "4!5.0.1")  # After error


class TestPatch(unittest.TestCase):
    def test_example_0(self: Self) -> None:
        x: Qual = Qual("a1")
        y: Qual = Qual("b2")
        with self.assertRaises(Exception):
            x += y


class TestVersionRelease(unittest.TestCase):

    def test_major_minor_micro_aliases(self: Self) -> None:
        # Test major, minor, and micro aliases for the first three indices
        version: Version = Version()
        version.public.base.release = [1, 2, 3]
        self.assertEqual(version.public.base.release.major, 1)
        self.assertEqual(version.public.base.release.minor, 2)
        self.assertEqual(version.public.base.release.micro, 3)
        self.assertEqual(
            version.public.base.release.patch, 3
        )  # 'patch' is an alias for micro

    def test_release_modify_aliases(self: Self) -> None:
        # Test modifying the release via major, minor, and micro properties
        version: Version = Version()
        version.public.base.release = [1, 2, 3]
        version.public.base.release.major = 10
        version.public.base.release.minor = 20
        version.public.base.release.micro = 30
        self.assertEqual(version.public.base.release, [10, 20, 30])
        self.assertEqual(version.public.base.release.patch, 30)

    def test_release_with_tailing_zeros_simulation(self: Self) -> None:
        # Test that the release can simulate arbitrary high number of tailing zeros
        version: Version = Version()
        version.public.base.release = [1, 2]
        simulated_release = version.public.base.release[:5]
        self.assertEqual(simulated_release, [1, 2, 0, 0, 0])

    def test_release_empty_major(self: Self) -> None:
        # Test that an empty release still has valid major, minor, micro values
        version: Version = Version()
        version.public.base.release = []
        self.assertEqual(version.public.base.release.major, 0)
        self.assertEqual(version.public.base.release.minor, 0)
        self.assertEqual(version.public.base.release.micro, 0)
        self.assertEqual(version.public.base.release.patch, 0)

    def test_release_modify_with_alias_increase_length(self: Self) -> None:
        # Test that modifying an alias can extend the length of release
        version: Version = Version()
        version.public.base.release = [1]
        version.public.base.release.minor = 5  # This should make release [1, 5]
        self.assertEqual(version.public.base.release, [1, 5])
        version.public.base.release.micro = 3  # This should make release [1, 5, 3]
        self.assertEqual(version.public.base.release, [1, 5, 3])

    def test_release_modify_major_only(self: Self) -> None:
        # Test that setting just the major property works
        version: Version = Version()
        version.public.base.release.major = 10
        self.assertEqual(version.public.base.release, [10])

    def test_release_modify_minor_only(self: Self) -> None:
        # Test that setting just the minor property extends release
        version: Version = Version()
        version.public.base.release = []
        version.public.base.release.minor = 1
        self.assertEqual(version.public.base.release, [0, 1])

    def test_release_modify_micro_only(self: Self) -> None:
        # Test that setting just the micro (patch) property extends release
        version: Version = Version()
        version.public.base.release = []
        version.public.base.release.micro = 1
        self.assertEqual(version.public.base.release, [0, 0, 1])


class TestAdditionalVersionRelease(unittest.TestCase):

    def test_release_inequality_with_list(self: Self) -> None:
        # Test inequality of release with a normal list
        version: Version = Version()
        version.public.base.release = [1, 2, 3]
        self.assertFalse(version.public.base.release == [1, 2, 4])

    def test_release_len(self: Self) -> None:
        # Test the length of the release list
        version: Version = Version()
        version.public.base.release = [1, 2, 3]
        self.assertEqual(len(version.public.base.release), 3)

    def test_release_slice_assignment(self: Self) -> None:
        # Test assigning a slice to release
        version: Version = Version()
        version.public.base.release = [1, 2, 3, 4, 5]
        version.public.base.release[1:4] = [20, 30, 40]
        self.assertEqual(version.public.base.release, [1, 20, 30, 40, 5])

    def test_release_iterable(self: Self) -> None:
        # Test if release supports iteration
        version: Version = Version()
        version.public.base.release = [1, 2, 3]
        result = list(version.public.base.release)
        self.assertEqual(result, [1, 2, 3])

    def test_release_repr(self: Self) -> None:
        # Test the repr of the release property
        version: Version = Version()
        version.public.base.release = [1, 2, 3]
        self.assertEqual(str(version.public.base.release), "1.2.3")

    def test_release_data_property(self: Self) -> None:
        # Test the 'data' property
        version: Version = Version()
        version.public.base.release = [1, 2, 3]
        self.assertEqual(version.public.base.release.data, [1, 2, 3])

    def test_release_data_setter(self: Self) -> None:
        # Test setting the 'data' property directly
        version: Version = Version()
        version.public.base.release.data = [10, 20, 30]
        self.assertEqual(version.public.base.release, [10, 20, 30])

    def test_release_contains(self: Self) -> None:
        # Test 'in' keyword with release
        version: Version = Version()
        version.public.base.release = [1, 2, 3]
        self.assertIn(2, version.public.base.release)
        self.assertNotIn(4, version.public.base.release)

    def test_release_mul(self: Self) -> None:
        # Test multiplying the release (list behavior)
        version: Version = Version()
        version.public.base.release = [1, 2]
        self.assertEqual(version.public.base.release * 3, [1, 2, 1, 2, 1, 2])

    def test_release_addition(self: Self) -> None:
        # Test adding another list to release
        version: Version = Version()
        version.public.base.release = [1, 2, 3]
        self.assertEqual(version.public.base.release + [4, 5], [1, 2, 3, 4, 5])


class TestVersionLocal(unittest.TestCase):

    def test_local_len(self: Self) -> None:
        # Test the length of the local list
        version: Version = Version()
        version.local = [1, "dev", "build"]
        self.assertEqual(len(version.local), 3)

    def test_local_slice_assignment(self: Self) -> None:
        # Test assigning a slice to the local list
        version: Version = Version()
        version.local = [1, "dev", "build"]
        version.local[1:3] = ["alpha", "beta"]
        self.assertEqual(version.local, [1, "alpha", "beta"])

    def test_local_contains(self: Self) -> None:
        # Test 'in' keyword with local list
        version: Version = Version()
        version.local = [1, "dev", "build"]
        self.assertIn("dev", version.local)
        self.assertNotIn("alpha", version.local)

    def test_local_mul(self: Self) -> None:
        # Test multiplying the local list
        version: Version = Version()
        version.local = [1, "dev"]
        self.assertEqual(version.local * 3, [1, "dev", 1, "dev", 1, "dev"])

    def test_local_addition(self: Self) -> None:
        # Test adding another list to local
        version: Version = Version()
        version.local = [1, "dev"]
        self.assertEqual(version.local + ["build"], [1, "dev", "build"])

    def test_local_inequality_with_list(self: Self) -> None:
        # Test inequality of local with a normal list
        version: Version = Version()
        version.local = [1, "dev"]
        self.assertFalse(version.local == [1, "build"])

    def test_local_repr(self: Self) -> None:
        # Test repr of local list
        version: Version = Version()
        version.local = [1, "dev", "build"]
        self.assertEqual(str(version.local), "1.dev.build")

    def test_local_data_property(self: Self) -> None:
        # Test that 'data' property correctly reflects local's internal list
        version: Version = Version()
        version.local = [1, "dev", "build"]
        self.assertEqual(version.local.data, [1, "dev", "build"])

    def test_local_data_setter(self: Self) -> None:
        # Test that 'data' property can be set directly
        version: Version = Version()
        version.local.data = ["custom", "data"]
        self.assertEqual(version.local, ["custom", "data"])

    def test_local_iterable(self: Self) -> None:
        # Test if local supports iteration
        version: Version = Version()
        version.local = "1.dev.build"
        result: list = list(version.local)
        self.assertEqual(result, [1, "dev", "build"])


class TestSlicingNoGo(unittest.TestCase):

    def test_slicing_2(self: Self) -> None:
        v: Version = Version("1.2.3.4.5.6.7.8.9.10")
        with self.assertRaises(Exception):
            v.public.base.release[-8:15:5] = 777

    def test_slicing_7(self: Self) -> None:
        v: Version = Version("1.2.3.4.5.6.7.8.9.10")
        del v.public.base.release[-8:15:5]
        self.assertEqual(str(v), "1.2.4.5.6.7.9.10")


class TestDevNoGo(unittest.TestCase):

    def test_initial_none_dev(self: Self) -> None:
        v: Version = Version("1.2.3")
        self.assertEqual(str(v), "1.2.3")
        self.assertIsNone(v.public.qual.dev)

    def test_dev_as_none(self: Self) -> None:
        v: Version = Version("1.2.3")
        v.public.qual.dev = None
        self.assertEqual(str(v), "1.2.3")
        self.assertIsNone(v.public.qual.dev)


class TestVersionSpecifiersNoGo(unittest.TestCase):

    def test_version_with_invalid_specifiers(self: Self) -> None:
        # Test version with invalid specifiers that should raise an error
        with self.assertRaises(VersionError):
            Version("1.2.3--4")

        with self.assertRaises(VersionError):
            Version("1.2.3a1--4")


if __name__ == "__main__":
    unittest.main()
