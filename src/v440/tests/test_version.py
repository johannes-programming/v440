import operator
import unittest

import packaging.version

from v440.core.Version import Version
from v440.core.VersionError import VersionError

VERSION_STRINGS = [
    # Basic Versioning
    "1.0.0",
    "0.9.1",
    "2.1.0",
    "10.5.3",
    "0.0.1",
    "0.0.0",
    "0.1",
    "1.2",
    "2.4",
    # Pre-releases (alpha, beta, release candidate)
    "1.0.0a1",
    "2.0b3",
    "0.9.1rc4",
    "1.1.0-alpha",
    "3.0.0b2",
    "4.1.0-rc.1",
    "1.1a0",
    "1.1.0-alpha.2",
    "5.0rc1",
    # Post-releases
    "1.0.0.post1",
    "2.1.0.post4",
    "3.2.1.post7",
    "1.2.post.3",
    "1.2.0-post4",
    "0.9.0post5",
    # Development releases
    "1.0.0.dev1",
    "2.0.0.dev2",
    "0.9.1.dev10",
    "2.1.dev0",
    "1.0dev5",
    "1.1.0-dev3",
    "0.5.0.dev4",
    # Local Versions
    "1.0.0+local",
    "2.0.1+20130313144700",
    "1.0.0+exp.sha.5114f85",
    "1.0.0+abc.5.1",
    "1.0.1+2019.10.22",
    "0.9.0+ubuntu1",
    "2.1.0+build.12345",
    "3.2.1+dfsg1",
    # Epoch Versions
    "1!0.1.0",
    "2!1.0.0",
    "1!2.3.4",
    "0!0.0.1",
    "3!1.2.0",
    # Mixed Versions (combining post, dev, pre-releases, etc.)
    "1.0.0a1.post2",
    "2.1.0b2.dev3",
    "1.2.3rc1+build123",
    "1!1.0.0a1.dev1",
    "1.2.3.post4+exp.sha.5114f85",
    "3.2.1rc2.post1.dev3",
    "0!0.9.0.post5.dev7+local.5",
    "2!3.4.5a2+ubuntu1",
    # Edge Cases / Special Forms
    "1.0",
    "v2.0",  # Some might write v prefix in tags, though it's non-standard
    "1.2.3-456",
    "2.0.0-beta",
    "1.0.0.dev1234567",
    "1.0.0.post123456789",
    "1.2.3+abc.123",
    "1.0+deadbeef",
    "0.1+build.1",
    # Invalid or Potentially Problematic Cases (for error handling)
    "1..0",  # double dot
    "1.0.0+@build",  # invalid character
    "1.2.3-beta",  # non-PEP 440 pre-release format
    "01.0.0",  # leading zero
    "1.0.0beta1",  # invalid beta format
    "v1.2.3"  # use of v, technically non-standard
    # Increasing complexity with more combinations
    "1.0.0a1.post2.dev3",
    "1!2.0.0b3.post1+exp.sha.1234abcd",
    "1!1.0.0.dev4567.post9+20190101",
    "0.9.0.post99.dev1000+ubuntu12.04.5",
    "3!2.1.0-alpha.5+build.34567abcd",
    "1.2.3a1.post11.dev7+sha256.abc123def456",
    "0!0.0.0a1.post9999.dev8888+local-build.0",
    "42!1.0.0rc999.post999.dev9999+exp.build.local1",
    # Combining epochs with local versions
    "2!1.0.0+local.version.1234",
    "1!2.0.1.post3.dev1+local.hash.deadbeef",
    "3!4.5.6a2.post8.dev9+build.sha.abcdef123456",
    # Advanced pre-release + post-release + development combinations
    "0.1a1.post2.dev0+local.build.1234abc",
    "2!5.6.7b5.post10.dev1000+exp.sha12345678",
    "1.0.0b99.post8888.dev7777+local.version.abcdef",
    "0.5.0rc1.post1111.dev987+local.build.exp123",
    "0!1.1a1.post1.dev100+local.build.hash99999",
    # Very large versions with long numeric parts
    "1.0.0.post999999.dev9999999+build.1234567890",
    "0!99999999.99999.99999+local.version.9876543210",
    "100!0.0.0a0.post0.dev0+exp.sha.0",
    "2!999.999.999a999.post9999.dev9999+local.build.9",
    # Complex strings with multiple epochs, large numbers, and combinations
    "10!9999.8888.7777a6666.post5555.dev4444+build.hash123abc",
    "1!1.1a1000000000.post1000000000.dev1000000000+local.0",
    # Mixed use of pre-release and post-release with complex local versions
    "1.0.0a1.post2+ubuntu16.04",
    "2.0.0-rc.1.post2+build.sha.e91e63f0",
    "1.0.0-alpha+linux-x86_64",
    "0.1.0-beta+20190506.commit.gdeadbeef",
    # Invalid cases (testing error handling for extreme cases)
    "0.0.0a1.post0.dev0+local.build.invalid_character#",
    "1.0.0-alpha_1",  # invalid separator
    "1.0.0a1..post2",  # double dot
    "1!2.0.0+",  # trailing plus sign
    "v1.0.0.post0.dev0",  # 'v' prefix with multiple post/dev releases
    "1.0.0.a1",  # invalid pre-release format
    "2!1..0",  # double dot with epoch
    "1.0.0++local.version.doubleplus",  # double plus in local version
    "1.2.3alpha1.post2",  # invalid pre-release format
    "00!1.0.0",  # invalid epoch with leading zero
    "1.0.0a01.post00.dev01+build00",  # invalid leading zeros
    "1.0.0+build@sha.123",  # invalid character in local version
    "v1.0.0-0",  # invalid pre-release number
    "1.0.0alpha_beta",  # invalid underscore in pre-release
    "1.0.0...dev",  # triple dots
    # Extreme cases with very long versions
    "0.1.0a12345678901234567890.post12345678901234567890.dev12345678901234567890+build12345678901234567890",
    "1.2.3+local.version.with.extremely.long.identifier.123456789012345678901234567890",
    "0!0.0.0a9999999999999.post9999999999999.dev9999999999999+build.sha.9999999999999",
    # Cases with inconsistent pre-release and post-release ordering
    "1.0.0.post1a1",  # post before alpha (invalid)
    "1.0.0.dev1rc1",  # dev before rc (invalid)
    "2!1.0.0rc1.post1a1",  # rc and post combined in wrong order (invalid)
    "3!1.0.0a1.dev1rc1+build123",  # rc after dev (invalid)
]


class TestExample(unittest.TestCase):

    def test_example_1(self):
        v = Version("v1.0.0")
        self.assertEqual(str(v), "1")  # Initial version
        self.assertEqual(v.format("3"), "1.0.0")  # Initial version formatted

    def test_example_2(self):
        v = Version("2.5.3")
        self.assertEqual(str(v), "2.5.3")  # Modified version
        v.release[1] = 64
        v.release.micro = 4
        self.assertEqual(str(v), "2.64.4")  # Further modified version

    def test_example_3(self):
        v1 = Version("1.6.3")
        v2 = Version("1.6.4")
        self.assertEqual(str(v1), "1.6.3")  # v1
        self.assertEqual(str(v2), "1.6.4")  # v2
        self.assertFalse(v1 == v2)  # v1 == v2 gives False
        self.assertTrue(v1 != v2)  # v1 != v2 gives True
        self.assertFalse(v1 >= v2)  # v1 >= v2 gives False
        self.assertTrue(v1 <= v2)  # v1 <= v2 gives True
        self.assertFalse(v1 > v2)  # v1 > v2 gives False
        self.assertTrue(v1 < v2)  # v1 < v2 gives True

    def test_example_3a(self):
        v1 = Version("1.6.3")
        v2 = "1.6.4"
        self.assertEqual(str(v1), "1.6.3")  # v1
        self.assertEqual(str(v2), "1.6.4")  # v2
        self.assertFalse(v1 == v2)  # v1 == v2 gives False
        self.assertTrue(v1 != v2)  # v1 != v2 gives True
        self.assertFalse(v1 >= v2)  # v1 >= v2 gives False
        self.assertTrue(v1 <= v2)  # v1 <= v2 gives True
        self.assertFalse(v1 > v2)  # v1 > v2 gives False
        self.assertTrue(v1 < v2)  # v1 < v2 gives True

    def test_example_3b(self):
        v1 = "1.6.3"
        v2 = Version("1.6.4")
        self.assertEqual(str(v1), "1.6.3")  # v1
        self.assertEqual(str(v2), "1.6.4")  # v2
        self.assertFalse(v1 == v2)  # v1 == v2 gives False
        self.assertTrue(v1 != v2)  # v1 != v2 gives True
        self.assertFalse(v1 >= v2)  # v1 >= v2 gives False
        self.assertTrue(v1 <= v2)  # v1 <= v2 gives True
        self.assertFalse(v1 > v2)  # v1 > v2 gives False
        self.assertTrue(v1 < v2)  # v1 < v2 gives True

    def test_example_4(self):
        v = Version("2.5.3.9")
        self.assertEqual(str(v), "2.5.3.9")  # before sorting
        v.release.sort()
        self.assertEqual(str(v), "2.3.5.9")  # after sorting

    def test_example_5(self):
        v = Version("2.0.0-alpha.1")
        self.assertEqual(str(v), "2a1")  # Pre-release version
        v.pre = "beta.2"
        self.assertEqual(str(v), "2b2")  # Modified pre-release version
        v.pre[1] = 4
        self.assertEqual(str(v), "2b4")  # Further modified pre-release version
        v.pre.phase = "PrEvIeW"
        self.assertEqual(str(v), "2rc4")  # Even further modified pre-release version

    def test_example_6(self):
        v = Version("1.2.3")
        v.post = "post1"
        v.local = "local.7.dev"
        self.assertEqual(str(v), "1.2.3.post1+local.7.dev")  # Post-release version
        self.assertEqual(v.format("-1"), "1.2.post1+local.7.dev")  # Formatted version
        v.post = "post.2"
        self.assertEqual(str(v), "1.2.3.post2+local.7.dev")  # Modified version
        v.post = None
        self.assertEqual(str(v), "1.2.3+local.7.dev")  # Modified without post
        v.post = "post", 3
        v.local.sort()
        self.assertEqual(str(v), "1.2.3.post3+dev.local.7")  # After sorting local
        v.local.append(8)
        self.assertEqual(str(v), "1.2.3.post3+dev.local.7.8")  # Modified with new local
        v.local = "3.test.19"
        self.assertEqual(str(v), "1.2.3.post3+3.test.19")  # Modified local again

    def test_example_7(self):
        v = Version("5.0.0")
        self.assertEqual(str(v), "5")  # Original version
        v.data = None
        self.assertEqual(str(v), "0")  # After reset
        v.base = "4!5.0.1"
        self.assertEqual(str(v), "4!5.0.1")  # Before error
        with self.assertRaises(Exception) as context:
            v.base = "9!x"
        self.assertTrue(
            "not a valid numeral segment" in str(context.exception)
        )  # Error
        self.assertEqual(str(v), "4!5.0.1")  # After error

    def test_example_8(self):
        v = Version("1.2.3.4.5.6.7.8.9.10")
        v.release.bump(index=7, amount=5)
        self.assertEqual(str(v), "1.2.3.4.5.6.7.13")  # Bumping


class TestSlicing(unittest.TestCase):
    def test_slicing_1(self):
        v = Version("1.2.3.4.5.6.7.8.9.10")
        v.release[-8:15:5] = "777"
        self.assertEqual(str(v), "1.2.7.4.5.6.7.7.9.10.0.0.7")

    def test_slicing_2(self):
        v = Version("1.2.3.4.5.6.7.8.9.10")
        try:
            v.release[-8:15:5] = 777
        except Exception as e:
            error = e
        else:
            error = None
        self.assertNotEqual(error, None)

    def test_slicing_3(self):
        v = Version("1.2.3.4.5.6.7.8.9.10")
        v.release[3:4] = 777
        self.assertEqual(str(v), "1.2.3.777.5.6.7.8.9.10")

    def test_slicing_4(self):
        v = Version("1.2.3.4.5.6.7.8.9.10")
        v.release[3:4] = "777"
        self.assertEqual(str(v), "1.2.3.7.7.7.5.6.7.8.9.10")

    def test_slicing_5(self):
        v = Version("1")
        v.release[3:4] = "777"
        self.assertEqual(str(v), "1.0.0.7.7.7")

    def test_slicing_6(self):
        v = Version("1")
        v.release[3:4] = 777
        self.assertEqual(str(v), "1.0.0.777")

    def test_slicing_7(self):
        v = Version("1.2.3.4.5.6.7.8.9.10")
        del v.release[-8:15:5]
        self.assertEqual(str(v), "1.2.4.5.6.7.9.10")


class TestPackaging(unittest.TestCase):
    def test_strings(self):

        pure = list()

        for s in VERSION_STRINGS:
            try:
                a = packaging.version.Version(s)
            except:
                continue
            else:
                pure.append(s)

        for s in pure:
            a = packaging.version.Version(s)
            b = str(a)
            f = len(a.release)
            g = Version(s).format(f)
            self.assertEqual(b, g)

        for s in pure:
            a = packaging.version.Version(s)
            b = Version(s).packaging()
            self.assertEqual(a, b, f"{s} should match packaging.version.Version")

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


class TestVersionRelease(unittest.TestCase):

    def setUp(self):
        # Create a version class instance
        self.version = Version()

    def test_release_basic_assignment(self):
        # Test simple assignment of a list of non-negative integers
        self.version.release = [1, 2, 3]
        self.assertEqual(self.version.release, [1, 2, 3])

    def test_release_trailing_zeros(self):
        # Test that trailing zeros are removed
        self.version.release = [1, 2, 3, 0, 0]
        self.assertEqual(self.version.release, [1, 2, 3])

    def test_release_zero(self):
        # Test that a single zero is allowed
        self.version.release = [0]
        self.assertEqual(self.version.release, [])

    def test_release_empty_list(self):
        # Test empty list assignment
        self.version.release = []
        self.assertEqual(self.version.release, [])

    def test_release_conversion_string(self):
        # Test assignment of string that can be converted to numbers
        self.version.release = ["1", "2", "3"]
        self.assertEqual(self.version.release, [1, 2, 3])

    def test_release_conversion_mixed(self):
        # Test assignment of mixed string and integer values
        self.version.release = ["1", 2, "3"]
        self.assertEqual(self.version.release, [1, 2, 3])

    def test_release_invalid_value(self):
        # Test that invalid values raise an appropriate error
        with self.assertRaises(VersionError):
            self.version.release = ["a", 2, "3"]

    def test_major_minor_micro_aliases(self):
        # Test major, minor, and micro aliases for the first three indices
        self.version.release = [1, 2, 3]
        self.assertEqual(self.version.release.major, 1)
        self.assertEqual(self.version.release.minor, 2)
        self.assertEqual(self.version.release.micro, 3)
        self.assertEqual(self.version.release.patch, 3)  # 'patch' is an alias for micro

    def test_release_modify_aliases(self):
        # Test modifying the release via major, minor, and micro properties
        self.version.release = [1, 2, 3]
        self.version.release.major = 10
        self.version.release.minor = 20
        self.version.release.micro = 30
        self.assertEqual(self.version.release, [10, 20, 30])
        self.assertEqual(self.version.release.patch, 30)

    def test_release_with_tailing_zeros_simulation(self):
        # Test that the release can simulate arbitrary high number of tailing zeros
        self.version.release = [1, 2]
        simulated_release = self.version.release[:5]
        self.assertEqual(simulated_release, [1, 2, 0, 0, 0])

    def test_release_assignment_with_bool_conversion(self):
        # Test that boolean values get converted properly to integers
        self.version.release = [True, False, 3]
        self.assertEqual(self.version.release, [1, 0, 3])

    def test_release_empty_major(self):
        # Test that an empty release still has valid major, minor, micro values
        self.version.release = []
        self.assertEqual(self.version.release.major, 0)
        self.assertEqual(self.version.release.minor, 0)
        self.assertEqual(self.version.release.micro, 0)
        self.assertEqual(self.version.release.patch, 0)

    def test_release_modify_with_alias_increase_length(self):
        # Test that modifying an alias can extend the length of release
        self.version.release = [1]
        self.version.release.minor = 5  # This should make release [1, 5]
        self.assertEqual(self.version.release, [1, 5])
        self.version.release.micro = 3  # This should make release [1, 5, 3]
        self.assertEqual(self.version.release, [1, 5, 3])

    def test_release_modify_major_only(self):
        # Test that setting just the major property works
        self.version.release.major = 10
        self.assertEqual(self.version.release, [10])

    def test_release_modify_minor_only(self):
        # Test that setting just the minor property extends release
        self.version.release = []
        self.version.release.minor = 1
        self.assertEqual(self.version.release, [0, 1])

    def test_release_modify_micro_only(self):
        # Test that setting just the micro (patch) property extends release
        self.version.release = []
        self.version.release.micro = 1
        self.assertEqual(self.version.release, [0, 0, 1])

    def test_release_large_numbers(self):
        # Test that release can handle large integers
        self.version.release = [1000000000, 2000000000, 3000000000]
        self.assertEqual(self.version.release, [1000000000, 2000000000, 3000000000])


class TestAdditionalVersionRelease(unittest.TestCase):

    def setUp(self):
        # Initialize a fresh Version instance for every test
        self.version = Version()

    def test_release_append(self):
        # Test the append method of the release list-like object
        self.version.release = [1, 2, 3]
        self.version.release.append(4)
        self.assertEqual(self.version.release, [1, 2, 3, 4])

    def test_release_extend(self):
        # Test extending the release list
        self.version.release = [1, 2]
        self.version.release.extend([3, 4, 5])
        self.assertEqual(self.version.release, [1, 2, 3, 4, 5])

    def test_release_insert(self):
        # Test inserting an element at a specific index
        self.version.release = [1, 2, 4]
        self.version.release.insert(2, 3)
        self.assertEqual(self.version.release, [1, 2, 3, 4])

    def test_release_pop(self):
        # Test popping an element
        self.version.release = [1, 2, 3]
        popped_value = self.version.release.pop()
        self.assertEqual(popped_value, 3)
        self.assertEqual(self.version.release, [1, 2])

    def test_release_pop_with_index(self):
        # Test popping an element at a specific index
        self.version.release = [1, 2, 3]
        popped_value = self.version.release.pop(1)
        self.assertEqual(popped_value, 2)
        self.assertEqual(self.version.release, [1, 3])

    def test_release_remove(self):
        # Test removing a specific value
        self.version.release = [1, 2, 3]
        self.version.release.remove(2)
        self.assertEqual(self.version.release, [1, 3])

    def test_release_clear(self):
        # Test clearing the release
        self.version.release = [1, 2, 3]
        self.version.release.clear()
        self.assertEqual(self.version.release, [])

    def test_release_count(self):
        # Test counting occurrences of a value
        self.version.release = [1, 2, 2, 3]
        count = self.version.release.count(2)
        self.assertEqual(count, 2)

    def test_release_index(self):
        # Test getting the index of a value
        self.version.release = [1, 2, 3]
        index = self.version.release.index(2)
        self.assertEqual(index, 1)

    def test_release_reverse(self):
        # Test reversing the release
        self.version.release = [1, 2, 3]
        self.version.release.reverse()
        self.assertEqual(self.version.release, [3, 2, 1])

    def test_release_sort(self):
        # Test sorting the release
        self.version.release = [3, 1, 2]
        self.version.release.sort()
        self.assertEqual(self.version.release, [1, 2, 3])

    def test_release_equality_with_list(self):
        # Test equality of release with a normal list
        self.version.release = [1, 2, 3]
        self.assertTrue(self.version.release == [1, 2, 3])

    def test_release_inequality_with_list(self):
        # Test inequality of release with a normal list
        self.version.release = [1, 2, 3]
        self.assertFalse(self.version.release == [1, 2, 4])

    def test_release_len(self):
        # Test the length of the release list
        self.version.release = [1, 2, 3]
        self.assertEqual(len(self.version.release), 3)

    def test_release_slice_assignment(self):
        # Test assigning a slice to release
        self.version.release = [1, 2, 3, 4, 5]
        self.version.release[1:4] = [20, 30, 40]
        self.assertEqual(self.version.release, [1, 20, 30, 40, 5])

    def test_release_invalid_assignment(self):
        # Test assigning an invalid type to release (should raise an error)
        with self.assertRaises(VersionError):
            self.version.release = ["1", "invalid", "3"]

    def test_release_iterable(self):
        # Test if release supports iteration
        self.version.release = [1, 2, 3]
        result = [x for x in self.version.release]
        self.assertEqual(result, [1, 2, 3])

    def test_release_repr(self):
        # Test the repr of the release property
        self.version.release = [1, 2, 3]
        self.assertEqual(str(self.version.release), "1.2.3")

    def test_release_data_property(self):
        # Test the 'data' property
        self.version.release = [1, 2, 3]
        self.assertEqual(self.version.release.data, [1, 2, 3])

    def test_release_data_setter(self):
        # Test setting the 'data' property directly
        self.version.release.data = [10, 20, 30]
        self.assertEqual(self.version.release, [10, 20, 30])

    def test_release_data_property_empty(self):
        # Test 'data' property when release is empty
        self.version.release = []
        self.assertEqual(self.version.release.data, [])

    def test_release_max_integer(self):
        # Test handling of very large integer values in release
        large_value = 10**18
        self.version.release = [large_value]
        self.assertEqual(self.version.release, [large_value])

    def test_release_non_integer_elements(self):
        # Ensure assigning non-integer, non-convertible values to release raises an error
        with self.assertRaises(VersionError):
            self.version.release = ["invalid", 2, 3]

    def test_release_contains(self):
        # Test 'in' keyword with release
        self.version.release = [1, 2, 3]
        self.assertIn(2, self.version.release)
        self.assertNotIn(4, self.version.release)

    def test_release_mul(self):
        # Test multiplying the release (list behavior)
        self.version.release = [1, 2]
        self.assertEqual(self.version.release * 3, [1, 2, 1, 2, 1, 2])

    def test_release_addition(self):
        # Test adding another list to release
        self.version.release = [1, 2, 3]
        self.assertEqual(self.version.release + [4, 5], [1, 2, 3, 4, 5])

    def test_release_invalid_float_value(self):
        # Ensure assigning non-integer float raises an error
        with self.assertRaises(VersionError):
            self.version.release = [1, 2.5, 3]

    def test_release_integer_float(self):
        # Ensure assigning float with integer value is allowed and converted to int
        self.version.release = [True, False, 3]
        self.assertEqual(self.version.release, [1, 0, 3])

    def test_release_invalid_boolean_assignment(self):
        # Ensure assigning invalid boolean-like values (not `True/False`) raises an error
        with self.assertRaises(VersionError):
            self.version.release = ["true", "false"]

    def test_release_boolean_assignment(self):
        # Ensure valid boolean values are converted to integers
        self.version.release = [True, False, 1]
        self.assertEqual(self.version.release, [1, 0, 1])


class TestVersionLocal(unittest.TestCase):

    def setUp(self):
        # Initialize a fresh Version instance for every test
        self.version = Version()

    def test_local_basic_assignment(self):
        # Test simple assignment of a list of strings or non-negative integers
        self.version.local = [1, "local", "dev"]
        self.assertEqual(self.version.local, [1, "local", "dev"])

    def test_local_empty_list(self):
        # Test assigning an empty list
        self.version.local = []
        self.assertEqual(self.version.local, [])

    def test_local_conversion_string(self):
        # Test assignment of a string that can be converted into numbers or remains as string
        self.version.local = ["1", "2", "local", "test"]
        self.assertEqual(self.version.local, [1, 2, "local", "test"])

    def test_local_conversion_mixed(self):
        # Test assignment of mixed string, integer, and other values
        self.version.local = ["1", 2, "local", 4, True]
        self.assertEqual(self.version.local, [1, 2, "local", 4, 1])  # True -> 1

    def test_local_invalid_value(self):
        # Test that invalid values raise an appropriate error
        with self.assertRaises(VersionError):
            self.version.local = ["a", {}, "3"]

    def test_local_append(self):
        # Test appending to the local list
        self.version.local = [1, "dev"]
        self.version.local.append("build")
        self.assertEqual(self.version.local, [1, "dev", "build"])

    def test_local_extend(self):
        # Test extending the local list
        self.version.local = [1, "dev"]
        self.version.local.extend(["test", 123])
        self.assertEqual(self.version.local, [1, "dev", "test", 123])

    def test_local_insert(self):
        # Test inserting into the local list
        self.version.local = [1, "dev"]
        self.version.local.insert(1, "alpha")
        self.assertEqual(self.version.local, [1, "alpha", "dev"])

    def test_local_pop(self):
        # Test popping an element from local
        self.version.local = [1, "dev", "build"]
        popped_value = self.version.local.pop()
        self.assertEqual(popped_value, "build")
        self.assertEqual(self.version.local, [1, "dev"])

    def test_local_pop_with_index(self):
        # Test popping an element at a specific index
        self.version.local = [1, "dev", "build"]
        popped_value = self.version.local.pop(1)
        self.assertEqual(popped_value, "dev")
        self.assertEqual(self.version.local, [1, "build"])

    def test_local_remove(self):
        # Test removing a specific value
        self.version.local = [1, "dev", "build"]
        self.version.local.remove("dev")
        self.assertEqual(self.version.local, [1, "build"])

    def test_local_clear(self):
        # Test clearing the local list
        self.version.local = [1, "dev", "build"]
        self.version.local.clear()
        self.assertEqual(self.version.local, [])

    def test_local_count(self):
        # Test counting occurrences of a value in the local list
        self.version.local = [1, "dev", "dev", "build"]
        count = self.version.local.count("dev")
        self.assertEqual(count, 2)

    def test_local_index(self):
        # Test getting the index of a value in the local list
        self.version.local = [1, "dev", "build"]
        index = self.version.local.index("dev")
        self.assertEqual(index, 1)

    def test_local_reverse(self):
        # Test reversing the local list
        self.version.local = [1, "dev", "build"]
        self.version.local.reverse()
        self.assertEqual(self.version.local, ["build", "dev", 1])

    def test_local_sort(self):
        # Test sorting the local list
        self.version.local = [3, 1, "dev", 2, "2", "4a", "a4"]
        self.version.local.sort()
        self.assertEqual(self.version.local, ["4a", "a4", "dev", 1, 2, 2, 3])

    def test_local_len(self):
        # Test the length of the local list
        self.version.local = [1, "dev", "build"]
        self.assertEqual(len(self.version.local), 3)

    def test_local_slice_assignment(self):
        # Test assigning a slice to the local list
        self.version.local = [1, "dev", "build"]
        self.version.local[1:3] = ["alpha", "beta"]
        self.assertEqual(self.version.local, [1, "alpha", "beta"])

    def test_local_contains(self):
        # Test 'in' keyword with local list
        self.version.local = [1, "dev", "build"]
        self.assertIn("dev", self.version.local)
        self.assertNotIn("alpha", self.version.local)

    def test_local_mul(self):
        # Test multiplying the local list
        self.version.local = [1, "dev"]
        self.assertEqual(self.version.local * 3, [1, "dev", 1, "dev", 1, "dev"])

    def test_local_addition(self):
        # Test adding another list to local
        self.version.local = [1, "dev"]
        self.assertEqual(self.version.local + ["build"], [1, "dev", "build"])

    def test_local_equality_with_list(self):
        # Test equality of local with a normal list
        self.version.local = [1, "dev"]
        self.assertTrue(self.version.local == [1, "dev"])

    def test_local_inequality_with_list(self):
        # Test inequality of local with a normal list
        self.version.local = [1, "dev"]
        self.assertFalse(self.version.local == [1, "build"])

    def test_local_boolean_assignment(self):
        # Ensure boolean values are handled correctly and converted to integers
        self.version.local = [True, False, "dev"]
        self.assertEqual(self.version.local, [1, 0, "dev"])

    def test_local_repr(self):
        # Test repr of local list
        self.version.local = [1, "dev", "build"]
        self.assertEqual(str(self.version.local), "1.dev.build")

    def test_local_data_property(self):
        # Test that 'data' property correctly reflects local's internal list
        self.version.local = [1, "dev", "build"]
        self.assertEqual(self.version.local.data, [1, "dev", "build"])

    def test_local_data_setter(self):
        # Test that 'data' property can be set directly
        self.version.local.data = ["custom", "data"]
        self.assertEqual(self.version.local, ["custom", "data"])

    def test_local_large_integers(self):
        # Test handling of very large integers in local
        large_value = 10**18
        self.version.local = [large_value]
        self.assertEqual(self.version.local, [large_value])

    def test_local_non_string_elements(self):
        # Ensure non-string and non-convertible values raise an error
        with self.assertRaises(VersionError):
            self.version.local = [1, [], "test"]

    def test_local_iterable(self):
        # Test if local supports iteration
        self.version.local = "1.dev.build"
        result = [x for x in self.version.local]
        self.assertEqual(result, [1, "dev", "build"])


class TestField(unittest.TestCase):

    def setUp(self):
        # Initialize a fresh Version instance for every test
        self.version = Version()

    def test_field(self):
        for x in VERSION_STRINGS:
            try:
                v = Version(x)
            except VersionError:
                continue
            self.assertEqual(v.isdevrelease(), v.packaging().is_devrelease)
            self.assertEqual(v.isprerelease(), v.packaging().is_prerelease)
            self.assertEqual(v.ispostrelease(), v.packaging().is_postrelease)
            self.assertEqual(str(v.base), v.packaging().base_version)
            self.assertEqual(str(v.public), v.packaging().public)
            self.version.local = v.packaging().local
            self.assertEqual(str(v.local), str(self.version.local))


class TestVersionSpecifiers(unittest.TestCase):

    def test_basic_version_with_post_specifier(self):
        # Test basic version with post specifier using a hyphen
        version = Version("1.2.3-4")
        self.assertEqual(str(version), "1.2.3.post4")

    def test_version_with_multiple_post_specifiers(self):
        # Test multiple post specifiers, last one should take precedence
        version = Version("1.2.3-4-5")
        self.assertEqual(str(version), "1.2.3.post5")

    def test_version_with_mixed_post_and_dev_specifiers(self):
        # Test multiple mixed specifiers (dev, post), last one should take precedence
        version = Version("1.2.3-dev1-post2-dev3")
        self.assertEqual(str(version), "1.2.3.post2.dev3")

    def test_version_with_pre_release_and_post_specifiers(self):
        # Test pre-release specifier followed by a post-release
        version = Version("1.2.3a1-4")
        self.assertEqual(str(version), "1.2.3a1.post4")

    def test_version_with_multiple_pre_and_post_specifiers(self):
        # Test multiple pre-release and post-release specifiers, last one should take precedence
        version = Version("1.2.3a1-4-5")
        self.assertEqual(str(version), "1.2.3a1.post5")

    def test_version_with_post_and_local_specifiers(self):
        # Test post-release with local version specifier
        version = Version("1.2.3-4+local")
        self.assertEqual(str(version), "1.2.3.post4+local")

    def test_version_with_post_specifier_and_epoch(self):
        # Test version with an epoch and post specifier
        version = Version("1!1.2.3-4")
        self.assertEqual(str(version), "1!1.2.3.post4")

    def test_version_with_wrong_order_specifiers(self):
        # Test version with wrong order of specifiers (e.g., post before pre)
        version = Version("1.2.3-4a1")
        self.assertEqual(str(version), "1.2.3a1.post4")

    def test_version_with_multiple_misordered_specifiers(self):
        # Test version with a more complex wrong ordering of specifiers
        version = Version("1.2.3-4a1-dev5-6")
        self.assertEqual(str(version), "1.2.3a1.post6.dev5")

    def test_version_with_dev_specifier_after_post(self):
        # Test version where a dev specifier follows a post-release (last one takes precedence)
        version = Version("1.2.3-4-dev5")
        self.assertEqual(str(version), "1.2.3.post4.dev5")

    def test_version_with_epoch_and_wrong_order_specifiers(self):
        # Test version with epoch and mixed, wrong order of specifiers
        version = Version("1!1.2.3-4-dev2")
        self.assertEqual(str(version), "1!1.2.3.post4.dev2")

    def test_version_with_multiple_epoch_and_specifiers(self):
        # Test multiple version specifiers (only last specifier should count)
        version = Version("2!1.2.3-4-5")
        self.assertEqual(str(version), "2!1.2.3.post5")

    def test_version_with_invalid_specifiers(self):
        # Test version with invalid specifiers that should raise an error
        with self.assertRaises(VersionError):
            Version("1.2.3--4")

        with self.assertRaises(VersionError):
            Version("1.2.3a1--4")

    def test_version_with_repeated_dev_specifier(self):
        # Test version where the dev specifier is repeated multiple times
        version = Version("1.2.3-dev1-dev2")
        self.assertEqual(str(version), "1.2.3.dev2")

    def test_version_with_complex_specifiers_and_local(self):
        # Test a complex version with mixed specifiers and a local version
        version = Version("1.2.3a1-4-dev5+local")
        self.assertEqual(str(version), "1.2.3a1.post4.dev5+local")

    def test_version_with_multiple_releases_and_epoch(self):
        # Test version with multiple release-like elements and an epoch
        version = Version("1!1.2.3a1-4-dev5-6+local")
        self.assertEqual(str(version), "1!1.2.3a1.post6.dev5+local")


if __name__ == "__main__":
    unittest.main()
