import unittest

from v440.core.Version import Version


class TestVersionManipulation(unittest.TestCase):

    def test_version_modification(self):
        # Create an instance of the v440.Version class
        v = Version("1.2.3")

        # Modify individual parts of the version
        v.release.major = 2
        v.release.minor = 5
        v.pre = "beta.1"
        v.local = "local.7.dev"

        # Verify the expected output
        self.assertEqual(str(v), "2.5.3b1+local.7.dev")


class TestData(unittest.TestCase):
    def test_data(self):

        v = Version("42!1.2.3.dev1337+5.nov")
        self.assertEqual("42!1.2.3.dev1337+5.nov", str(v))
        self.assertEqual(v.data, str(v))
        self.assertEqual(type(v.data), str)

        v.data = 4.2
        self.assertEqual("4.2", str(v))
        self.assertEqual(v.data, str(v))
        self.assertEqual(type(v.data), str)

        v.data = 9001
        self.assertEqual("9001", str(v))
        self.assertEqual(v.data, str(v))
        self.assertEqual(type(v.data), str)

        v.data = None
        self.assertEqual("0", str(v))
        self.assertEqual(v.data, str(v))
        self.assertEqual(type(v.data), str)

        v.data = "1701!4.5.6.rc255+reset"
        self.assertEqual("1701!4.5.6rc255+reset", str(v))
        self.assertEqual(v.data, str(v))
        self.assertEqual(type(v.data), str)


class TestVersionDev(unittest.TestCase):

    def test_initial_none_dev(self):
        v = Version("1.2.3")
        self.assertEqual(str(v), "1.2.3")
        self.assertIsNone(v.dev)

    def test_dev_as_int(self):
        v = Version("1.2.3")
        v.dev = 1
        self.assertEqual(str(v), "1.2.3.dev1")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 1)

    def test_dev_as_string_int(self):
        v = Version("1.2.3")
        v.dev = "42"
        self.assertEqual(str(v), "1.2.3.dev42")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 42)

    def test_dev_as_string_with_dev_prefix(self):
        v = Version("1.2.3")
        v.dev = "dev1000"
        self.assertEqual(str(v), "1.2.3.dev1000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 1000)

    def test_dev_as_string_with_dev_dot_prefix(self):
        v = Version("1.2.3")
        v.dev = "dev.2000"
        self.assertEqual(str(v), "1.2.3.dev2000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 2000)

    def test_dev_as_string_with_dot_dev_prefix(self):
        v = Version("1.2.3")
        v.dev = ".dev.3000"
        self.assertEqual(str(v), "1.2.3.dev3000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 3000)

    def test_dev_as_string_with_dot_dev_number_prefix(self):
        v = Version("1.2.3")
        v.dev = ".dev4000"
        self.assertEqual(str(v), "1.2.3.dev4000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 4000)

    def test_dev_as_tuple(self):
        v = Version("1.2.3")
        v.dev = ("dev", "5000")
        self.assertEqual(str(v), "1.2.3.dev5000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 5000)

    def test_dev_as_list(self):
        v = Version("1.2.3")
        v.dev = ["dev", "6000"]
        self.assertEqual(str(v), "1.2.3.dev6000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 6000)

    def test_dev_as_uppercase_string(self):
        v = Version("1.2.3")
        v.dev = "DEV7000"
        self.assertEqual(str(v), "1.2.3.dev7000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 7000)

    def test_dev_as_mixed_case_string(self):
        v = Version("1.2.3")
        v.dev = "dEv8000"
        self.assertEqual(str(v), "1.2.3.dev8000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 8000)

    def test_dev_as_list_mixed_case(self):
        v = Version("1.2.3")
        v.dev = ["dEV", "9000"]
        self.assertEqual(str(v), "1.2.3.dev9000")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 9000)

    def test_dev_as_false(self):
        v = Version("1.2.3")
        v.dev = False
        self.assertEqual(str(v), "1.2.3.dev0")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 0)

    def test_dev_as_true(self):
        v = Version("1.2.3")
        v.dev = True
        self.assertEqual(str(v), "1.2.3.dev1")
        self.assertIsInstance(v.dev, int)
        self.assertEqual(v.dev, 1)

    def test_dev_as_none(self):
        v = Version("1.2.3")
        v.dev = None
        self.assertEqual(str(v), "1.2.3")
        self.assertIsNone(v.dev)


class TestVersionEpoch(unittest.TestCase):
    def test_epoch_as_int(self):
        v = Version("1.2.3")
        v.epoch = 1
        self.assertEqual(str(v), "1!1.2.3")
        self.assertIsInstance(v.epoch, int)
        self.assertEqual(v.epoch, 1)

    def test_epoch_as_string_number(self):
        v = Version("1.2.3")
        v.epoch = "42"
        self.assertEqual(str(v), "42!1.2.3")
        self.assertIsInstance(v.epoch, int)
        self.assertEqual(v.epoch, 42)

    def test_epoch_as_string_with_non_digit(self):
        v = Version("1.2.3")
        v.epoch = "9001!"
        self.assertEqual(str(v), "9001!1.2.3")
        self.assertIsInstance(v.epoch, int)
        self.assertEqual(v.epoch, 9001)

    def test_epoch_as_false(self):
        v = Version("1.2.3")
        v.epoch = False
        self.assertEqual(str(v), "1.2.3")
        self.assertIsInstance(v.epoch, int)
        self.assertEqual(v.epoch, 0)

    def test_epoch_as_true(self):
        v = Version("1.2.3")
        v.epoch = True
        self.assertEqual(str(v), "1!1.2.3")
        self.assertIsInstance(v.epoch, int)
        self.assertEqual(v.epoch, 1)

    def test_epoch_as_none(self):
        v = Version("1.2.3")
        v.epoch = None
        self.assertEqual(str(v), "1.2.3")
        self.assertIsInstance(v.epoch, int)
        self.assertEqual(v.epoch, 0)


class TestVersionLocal(unittest.TestCase):

    def test_version_operations(self):
        v = Version("1.2.3")
        backup = v.local
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


class TestVersion(unittest.TestCase):

    def test_version_pre(self):
        v = Version("1.2.3")
        backup = v.pre

        # Initial version, no pre-release version
        self.assertEqual(str(v), "1.2.3")
        self.assertEqual(v.pre, [None, None])

        # Set pre-release version to "a1"
        v.pre = "a1"
        self.assertEqual(str(v), "1.2.3a1")
        self.assertEqual(str(v.pre), "a1")

        # Modify pre-release phase to "preview"
        v.pre.phase = "preview"
        self.assertEqual(str(v), "1.2.3rc1")
        self.assertEqual(str(v.pre), "rc1")

        # Modify subphase to "42"
        v.pre.subphase = "42"
        self.assertEqual(str(v), "1.2.3rc42")
        self.assertEqual(str(v.pre), "rc42")

        # Change phase to a formatted string "BeTa"
        v.pre.phase = """
        BeTa
        """
        self.assertEqual(str(v), "1.2.3b42")
        self.assertEqual(str(v.pre), "b42")

        self.assertEqual(v.pre, backup)

        # Set pre-release to None
        v.pre = None
        self.assertEqual(str(v), "1.2.3")
        self.assertEqual(v.pre, [None, None])


if __name__ == "__main__":
    unittest.main()
