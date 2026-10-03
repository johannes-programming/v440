"""Verify mutable Version operations across the public API."""

from __future__ import annotations

__all__: list[str] = [
    "TestDataHoldStandards",
    "TestDevNoGo",
    "TestVersionBumpRelease",
    "TestVersionLocal",
    "TestVersionLocal0",
    "TestVersionManipulation",
    "TestVersionPre",
    "TestVersionPreviousExample",
    "TestVersionQualPatch",
    "TestVersionRelative",
    "TestVersionRelease",
    "TestVersionReleaseAdditional",
    "TestVersionSlicingNoGo",
]

import unittest
from typing import Any, Self

from v440.core.Local import Local
from v440.core.Qual import Qual
from v440.core.Release import Release
from v440.core.Version import Version
from v440.errors.VersionError import VersionError


class TestVersionBumpRelease(unittest.TestCase):
    """Verify version bump release behavior."""

    def test_release_bump(self: Self, /) -> None:
        # Create an instance of the v440.Version class
        """Verify release bump behavior."""
        release: Release
        release = Release(string="1.2.3")

        # Bump the version using the bump method
        release.bump(1, 2)
        self.assertEqual(str(release), "1.4")  # Bumped version

        # Bump the version again
        release.bump(2, 1)
        self.assertEqual(str(release), "1.4.1")  # Further bumped version

        # Bump the version again
        release.bump()
        self.assertEqual(str(release), "1.4.2")  # Further bumped version


class TestVersionManipulation(unittest.TestCase):
    """Verify version manipulation behavior."""

    def test_version_modification(self: Self, /) -> None:
        # Create an instance of the v440.Version class
        """Verify version modification behavior."""
        version: Version
        version = Version(string="1.2.3")

        # Modify individual parts of the version
        version.public.base.release.major = 2
        version.public.base.release.minor = 5
        version.public.qual.string = "beta.1"
        version.local.string = "local.7.dev"

        # Verify the expected output
        self.assertEqual(str(version), "2.5.3b1+local.7.dev")


class TestVersionLocal0(unittest.TestCase):
    """Verify version local 0 behavior."""

    def test_version_operations(self: Self, /) -> None:
        """Verify version operations behavior."""
        backup: Local
        version: Any
        version = Version(string="1.2.3")
        backup = version.local
        version.local.string = "local.1.2.3"
        self.assertEqual(str(version), "1.2.3+local.1.2.3")
        self.assertEqual(str(version.local), "local.1.2.3")
        version.local.append("extra")
        self.assertEqual(str(version), "1.2.3+local.1.2.3.extra")
        self.assertEqual(str(version.local), "local.1.2.3.extra")
        version.local.remove(1)
        self.assertEqual(str(version), "1.2.3+local.2.3.extra")
        self.assertEqual(str(version.local), "local.2.3.extra")
        self.assertEqual(version.local[0], "local")
        self.assertEqual(version.local[-1], "extra")
        version.local.sort()
        self.assertEqual(str(version), "1.2.3+extra.local.2.3")
        self.assertEqual(str(version.local), "extra.local.2.3")
        version.local.clear()
        self.assertEqual(str(version), "1.2.3")
        self.assertEqual(str(version.local), "")
        version.local.string = "reset.1.2"
        self.assertEqual(str(version), "1.2.3+reset.1.2")
        self.assertEqual(str(version.local), "reset.1.2")
        self.assertTrue(version.local is backup)


class TestVersionPre(unittest.TestCase):
    """Verify version pre behavior."""

    def test_pre(self: Self, /) -> None:
        """Verify pre behavior."""
        backup: Qual
        version: Version
        version = Version(string="1.2.3")
        backup = version.public.qual

        # Initial version, no pre-release version
        self.assertEqual(str(version), "1.2.3")
        self.assertEqual(str(version.public.qual), "")

        # Set pre-release version to "a1"
        version.public.qual.string = "a1"
        self.assertEqual(str(version), "1.2.3a1")
        self.assertEqual(str(version.public.qual), "a1")

        # Modify pre-release phase to "preview"
        version.public.qual.pre.lit = "preview"
        self.assertEqual(str(version), "1.2.3rc1")
        self.assertEqual(str(version.public.qual), "rc1")

        # Modify subphase to "42"
        version.public.qual.pre.num = 42
        self.assertEqual(str(version), "1.2.3rc42")
        self.assertEqual(str(version.public.qual), "rc42")

        # Change phase to a formatted string "BeTa"
        version.public.qual.pre.lit = "BeTa"
        self.assertEqual(str(version), "1.2.3b42")
        self.assertEqual(str(version.public.qual), "b42")
        self.assertEqual(version.public.qual, backup)

        # Set pre-release to None
        version.public.qual.string = ""
        self.assertEqual(str(version), "1.2.3")
        self.assertEqual(str(version.public.qual), "")


class TestVersionPreviousExample(unittest.TestCase):
    """Verify version previous example behavior."""

    def test_example_2(self: Self, /) -> None:
        """Verify example 2 behavior."""
        version: Version
        version = Version(string="2.5.3")
        self.assertEqual(str(version), "2.5.3")  # Modified version
        version.public.base.release[1] = 64
        version.public.base.release.micro = 4
        self.assertEqual(str(version), "2.64.4")  # Further modified version

    def test_example_3(self: Self, /) -> None:
        """Verify example 3 behavior."""
        v1: Version
        v2: Version
        v1 = Version(string="1.6.3")
        v2 = Version(string="1.6.4")
        self.assertEqual(str(v1), "1.6.3")  # v1
        self.assertEqual(str(v2), "1.6.4")  # v2
        # eq
        self.assertFalse(v1 == v2)
        self.assertFalse(v2 == v1)
        self.assertFalse(v1 == str(v1))
        self.assertFalse(v2 == str(v2))
        self.assertTrue(v1 == v1)
        self.assertTrue(v2 == v2)
        self.assertFalse(str(v1) == v1)
        self.assertFalse(str(v2) == v2)
        # ne
        self.assertTrue(v1 != v2)
        self.assertTrue(v2 != v1)
        self.assertTrue(v1 != str(v1))
        self.assertTrue(v2 != str(v2))
        self.assertFalse(v1 != v1)
        self.assertFalse(v2 != v2)
        self.assertTrue(str(v1) != v1)
        self.assertTrue(str(v2) != v2)
        # ge
        self.assertFalse(v1 >= v2)
        self.assertTrue(v2 >= v1)
        with self.assertRaises(Exception):
            v1 >= str(v2)
        with self.assertRaises(Exception):
            str(v1) >= v2
        with self.assertRaises(Exception):
            v2 >= str(v1)
        with self.assertRaises(Exception):
            str(v2) >= v1
        # le
        self.assertFalse(v2 <= v1)
        self.assertTrue(v1 <= v2)
        with self.assertRaises(Exception):
            v1 <= str(v2)
        with self.assertRaises(Exception):
            str(v1) <= v2
        with self.assertRaises(Exception):
            v2 <= str(v1)
        with self.assertRaises(Exception):
            str(v2) <= v1
        # gt
        self.assertFalse(v1 > v2)
        self.assertTrue(v2 > v1)
        with self.assertRaises(Exception):
            v1 > str(v2)
        with self.assertRaises(Exception):
            str(v1) > v2
        with self.assertRaises(Exception):
            v2 > str(v1)
        with self.assertRaises(Exception):
            str(v2) > v1
        # lt
        self.assertFalse(v2 < v1)
        self.assertTrue(v1 < v2)
        with self.assertRaises(Exception):
            v1 < str(v2)
        with self.assertRaises(Exception):
            str(v1) < v2
        with self.assertRaises(Exception):
            v2 < str(v1)
        with self.assertRaises(Exception):
            str(v2) < v1

    def test_example_5(self: Self, /) -> None:
        """Verify example 5 behavior."""
        version: Version
        version = Version(string="2.0.0-alpha.1")
        self.assertEqual(str(version), "2a1")  # Pre-release version
        version.public.qual.pre.string = "beta.2"
        self.assertEqual(str(version), "2b2")  # Modified pre-release version
        with self.assertRaises(Exception):
            version.public.qual.pre[1] = 4  # type: ignore[index]
        self.assertEqual(str(version), "2b2")  # Further modified pre-release version
        version.public.qual.pre.lit = "PrEvIeW"
        self.assertEqual(
            str(version), "2rc2"
        )  # Even further modified pre-release version

    def test_example_6(self: Self, /) -> None:
        """Verify example 6 behavior."""
        version: Version
        version = Version(string="1.2.3")
        version.public.qual.post.string = -1
        version.local.string = "local.7.dev"
        self.assertEqual(
            str(version), "1.2.3.post1+local.7.dev"
        )  # Post-release version
        self.assertEqual(
            format(version, "#.#"), "1.2.3.post1+local.7.dev"
        )  # Formatted version
        version.public.qual.post.string = -2
        self.assertEqual(str(version), "1.2.3.post2+local.7.dev")  # Modified version
        version.public.qual.post.string = ""
        self.assertEqual(str(version), "1.2.3+local.7.dev")  # Modified without post
        version.public.qual.post.string = -3
        version.local.sort()
        self.assertEqual(
            str(version), "1.2.3.post3+dev.local.7"
        )  # After sorting local
        version.local.append(8)
        self.assertEqual(
            str(version), "1.2.3.post3+dev.local.7.8"
        )  # Modified with new local
        version.local.string = "3.test.19"
        self.assertEqual(
            str(version), "1.2.3.post3+3.test.19"
        )  # Modified local again

    def test_example_7(self: Self, /) -> None:
        """Verify example 7 behavior."""
        version: Version
        version = Version(string="5.0.0")
        self.assertEqual(str(version), "5")  # Original version
        version.string = "00000000.0000.00.0"
        self.assertEqual(str(version), "0")  # After reset
        version.public.base.string = "4!5.0.1"
        self.assertEqual(str(version), "4!5.0.1")  # Before error
        with self.assertRaises(VersionError):
            version.public.base.string = "9!x"
        self.assertEqual(str(version), "4!5.0.1")  # After error


class TestVersionQualPatch(unittest.TestCase):
    """Verify version qual patch behavior."""

    def test_example_0(self: Self, /) -> None:
        """Verify example 0 behavior."""
        left_qual: Qual
        right_qual: Qual
        left_qual = Qual(string="a1")
        right_qual = Qual(string="b2")
        with self.assertRaises(Exception):
            left_qual += right_qual  # type: ignore[operator]


class TestVersionRelative(unittest.TestCase):
    """Verify version relative behavior."""

    def test_cmp(self: Self, /) -> None:
        """Verify cmp behavior."""
        self.assertFalse(Version(string="1+1") == Version(string="1+a"))
        self.assertFalse(Version(string="1+1") <= Version(string="1+a"))
        self.assertFalse(Version(string="1+1") < Version(string="1+a"))
        self.assertTrue(Version(string="1+1") >= Version(string="1+a"))
        self.assertTrue(Version(string="1+1") > Version(string="1+a"))
        self.assertTrue(Version(string="1+1") != Version(string="1+a"))


class TestVersionRelease(unittest.TestCase):
    """Verify version release behavior."""

    def test_repr(self: Self, /) -> None:
        """Verify repr behavior."""
        release: Release
        release = Release([1, 2, 3])
        self.assertEqual(repr(release), "Release([1, 2, 3])")
        self.assertEqual(str(release), "1.2.3")

    def test_major_minor_micro_aliases(self: Self, /) -> None:
        # Test major, minor, and micro aliases for the first three indices
        """Verify major minor micro aliases behavior."""
        version: Any
        version = Version()
        version.public.base.release.data = [1, 2, 3]
        self.assertEqual(version.public.base.release.major, 1)
        self.assertEqual(version.public.base.release.minor, 2)
        self.assertEqual(version.public.base.release.micro, 3)
        self.assertEqual(
            version.public.base.release.patch, 3
        )  # 'patch' is an alias for micro

    def test_release_modify_aliases(self: Self, /) -> None:
        # Test modifying the release via major, minor, and micro properties
        """Verify release modify aliases behavior."""
        version: Any
        version = Version()
        version.public.base.release.data = [1, 2, 3]
        version.public.base.release.major = 10
        version.public.base.release.minor = 20
        version.public.base.release.micro = 30
        self.assertEqual(list(version.public.base.release), [10, 20, 30])
        self.assertEqual(version.public.base.release.patch, 30)

    def test_release_with_tailing_zeros_simulation(self: Self, /) -> None:
        # Test that the release can simulate arbitrary high number of tailing zeros
        """Verify release with tailing zeros simulation behavior."""
        simulated_release: Release
        version: Version
        version = Version()
        version.public.base.release.data = [1, 2]
        simulated_release = version.public.base.release[:5]
        self.assertEqual(
            simulated_release, Version.Public.Base.Release([1, 2])
        )

    def test_release_empty_major(self: Self, /) -> None:
        # Test that an empty release still has valid major, minor, micro values
        """Verify release empty major behavior."""
        version: Any
        version = Version()
        version.public.base.release.data = []
        self.assertEqual(version.public.base.release.major, 0)
        self.assertEqual(version.public.base.release.minor, 0)
        self.assertEqual(version.public.base.release.micro, 0)
        self.assertEqual(version.public.base.release.patch, 0)


class TestVersionReleaseAdditional(unittest.TestCase):
    """Verify version release additional behavior."""

    def test_release_inequality_with_list(self: Self, /) -> None:
        # Test inequality of release with a normal list
        """Verify release inequality with list behavior."""
        version: Any
        version = Version()
        version.public.base.release.data = [1, 2, 3]
        self.assertFalse(version.public.base.release == [1, 2, 4])

    def test_release_len(self: Self, /) -> None:
        # Test the length of the release list
        """Verify release len behavior."""
        version: Any
        version = Version()
        version.public.base.release.data = [1, 2, 3]
        self.assertEqual(len(version.public.base.release), 3)

    def test_release_slice_assignment(self: Self, /) -> None:
        # Test assigning a slice to release
        """Verify release slice assignment behavior."""
        version: Any
        version = Version()
        version.public.base.release.data = [1, 2, 3, 4, 5]
        version.public.base.release[1:4] = [20, 30, 40]
        self.assertEqual(
            list(version.public.base.release),
            [1, 20, 30, 40, 5],
        )

    def test_release_iterable(self: Self, /) -> None:
        # Test if release supports iteration
        """Verify release iterable behavior."""
        version: Any
        result: list[Any]
        version = Version()
        version.public.base.release.data = [1, 2, 3]
        result = list(version.public.base.release)
        self.assertEqual(result, [1, 2, 3])

    def test_release_repr(self: Self, /) -> None:
        # Test the repr of the release property
        """Verify release repr behavior."""
        version: Any
        version = Version()
        version.public.base.release.data = [1, 2, 3]
        self.assertEqual(str(version.public.base.release), "1.2.3")

    def test_release_data_property(self: Self, /) -> None:
        # Test the 'data' property
        """Verify release data property behavior."""
        version: Any
        version = Version()
        version.public.base.release.data = [1, 2, 3]
        self.assertEqual(version.public.base.release.data, (1, 2, 3))

    def test_release_data_setter(self: Self, /) -> None:
        # Test setting the 'data' property directly
        """Verify release data setter behavior."""
        version: Any
        version = Version()
        version.public.base.release.data = [10, 20, 30]
        self.assertEqual(list(version.public.base.release), [10, 20, 30])

    def test_release_contains(self: Self, /) -> None:
        # Test 'in' keyword with release
        """Verify release contains behavior."""
        version: Any
        version = Version()
        version.public.base.release.data = [1, 2, 3]
        self.assertIn(2, version.public.base.release)
        self.assertNotIn(4, version.public.base.release)

    def test_release_mul(self: Self, /) -> None:
        # Test multiplying the release (list behavior)
        """Verify release mul behavior."""
        answer: list[int]
        solution: list[int]
        version: Any
        version = Version()
        version.public.base.release.data = [1, 2]
        answer = list(version.public.base.release * 3)
        solution = [1, 2, 1, 2, 1, 2]
        self.assertEqual(answer, solution)

    def test_release_addition(self: Self, /) -> None:
        # Test adding another list to release
        """Verify release addition behavior."""
        answer: list[Any]
        solution: list[Any]
        version: Any
        version = Version()
        version.public.base.release.data = [1, 2, 3]
        answer = list(version.public.base.release) + [4, 5]
        solution = [1, 2, 3, 4, 5]
        self.assertEqual(answer, solution)


class TestVersionLocal(unittest.TestCase):
    """Verify version local behavior."""

    def test_local_len(self: Self, /) -> None:
        # Test the length of the local list
        """Verify local len behavior."""
        version: Any
        version = Version()
        version.local.data = [1, "dev", "build"]
        self.assertEqual(len(version.local), 3)

    def test_local_slice_assignment(self: Self, /) -> None:
        # Test assigning a slice to the local list
        """Verify local slice assignment behavior."""
        version: Any
        version = Version()
        version.local.data = [1, "dev", "build"]
        version.local[1:3] = ["alpha", "beta"]
        self.assertEqual(list(version.local), [1, "alpha", "beta"])

    def test_local_contains(self: Self, /) -> None:
        # Test 'in' keyword with local list
        """Verify local contains behavior."""
        version: Any
        version = Version()
        version.local.data = [1, "dev", "build"]
        self.assertIn("dev", version.local)
        self.assertNotIn("alpha", version.local)

    def test_local_mul(self: Self, /) -> None:
        # Test multiplying the local list
        """Verify local mul behavior."""
        answer: list[Any]
        solution: list[Any]
        version: Any
        version = Version()
        version.local.data = [1, "dev"]
        answer = list(version.local * 3)
        solution = [1, "dev", 1, "dev", 1, "dev"]
        self.assertEqual(answer, solution)

    def test_local_addition(self: Self, /) -> None:
        # Test adding another list to local
        """Verify local addition behavior."""
        answer: list[Any]
        solution: list[Any]
        version: Any
        version = Version()
        version.local.data = [1, "dev"]
        answer = list(version.local + ["build"])
        solution = [1, "dev", "build"]
        self.assertEqual(answer, solution)

    def test_local_inequality_with_list(self: Self, /) -> None:
        # Test inequality of local with a normal list
        """Verify local inequality with list behavior."""
        version: Any
        version = Version()
        version.local.data = [1, "dev"]
        self.assertFalse(version.local == [1, "build"])

    def test_local_repr(self: Self, /) -> None:
        # Test repr of local list
        """Verify local repr behavior."""
        version: Any
        version = Version()
        version.local.data = [1, "dev", "build"]
        self.assertEqual(str(version.local), "1.dev.build")

    def test_local_data_property(self: Self, /) -> None:
        # Test that 'data' property correctly reflects local's internal list
        """Verify local data property behavior."""
        version: Any
        version = Version()
        version.local.data = [1, "dev", "build"]
        self.assertEqual(version.local.data, (1, "dev", "build"))


class TestVersionSlicingNoGo(unittest.TestCase):
    """Verify version slicing no go behavior."""

    def test_slicing_2(self: Self, /) -> None:
        """Verify slicing 2 behavior."""
        version: Version
        version = Version(string="1.2.3.4.5.6.7.8.9.10")
        with self.assertRaises(Exception):
            version.public.base.release[-8:15:5] = 777  # type: ignore[call-overload]

    def test_slicing_7(self: Self, /) -> None:
        """Verify slicing 7 behavior."""
        version: Version
        version = Version(string="1.2.3.4.5.6.7.8.9.10")
        del version.public.base.release[-8:15:5]
        self.assertEqual(str(version), "1.2.4.5.6.7.9.10")


class TestDevNoGo(unittest.TestCase):
    """Verify dev no go behavior."""

    def test_initial_none_dev(self: Self, /) -> None:
        """Verify initial none dev behavior."""
        version: Version
        version = Version(string="1.2.3")
        self.assertEqual(str(version), "1.2.3")
        self.assertFalse(version.public.qual.dev)

    def test_dev_as_none(self: Self, /) -> None:
        """Verify dev as none behavior."""
        version: Version
        version = Version(string="1.2.3")
        version.public.qual.dev.string = ""
        self.assertEqual(str(version), "1.2.3")
        self.assertFalse(version.public.qual.dev)


class TestDataHoldStandards(unittest.TestCase):
    """Verify data hold standards behavior."""

    def test_list_like_comparison(self: Self, /) -> None:
        """Verify list like comparison behavior."""
        local: Local
        release: Release
        local = Local()
        release = Release()
        local.data = (1, 2, 3)
        release.data = (1, 2, 3)
        self.assertEqual(local, release)
        local.data = (1, 2, 4)
        release.data = (1, 2, 3)
        self.assertGreater(local, release)
        local.data = (1, 2, 3)
        release.data = (1, 2, 4)
        self.assertLess(local, release)


if __name__ == "__main__":
    unittest.main()
