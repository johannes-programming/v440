"""Validate v440 behavior against recorded version examples."""

from __future__ import annotations

__all__: list[str] = [
    "TestDeformatting",
    "TestFormat",
    "TestFunction",
    "TestOrder",
    "TestReleaseAlias",
    "TestSlicingGo",
    "TestSlots",
    "TestStringExamples",
    "TestTotalAttrSetter",
    "TestTotalMethod",
    "TestTypeNames",
    "TestVersionEpochGo",
]

import contextlib
import enum
import functools
import importlib
import io
import operator
import shlex
import tomllib
import types
import unittest
from collections import abc
from pathlib import Path
from typing import Any, Self, cast

from packaging.version import InvalidVersion
from packaging.version import Version as Version_

from v440 import core
from v440.core.Version import Version
from v440.errors.VersionError import VersionError


class Util(enum.Enum):
    """Load and expose shared test-data fixtures."""

    util = None

    @functools.cached_property
    def data(self: Self, /) -> dict[str, Any]:
        """Load and return the shared TOML test data."""
        file: Path
        stream: io.BufferedReader
        file = Path(__file__).parent / "testdata.toml"
        with file.open("rb") as stream:
            return tomllib.load(stream)

    @functools.cached_property
    def examples(self: Self, /) -> dict[str, Any]:
        """Return the recorded example cases from the shared test data."""
        return cast(dict[str, Any], Util.util.data.get("examples", {}))

    @classmethod
    def import_(cls: type[Self], qualname: str, /) -> Any:
        """Import the object named by a fully qualified test-data reference."""
        module: types.ModuleType
        name: str
        names: list[str]
        names = qualname.split(".")
        name = names.pop(-1)
        module = importlib.import_module(".".join(names))
        return getattr(module, name)


class TestDeformatting(unittest.TestCase):
    """Verify deformatting behavior."""

    def go_blob(
        self: Self,
        cls: type[Any],
        /,
        *,
        exceptiontype: str,
        **kwargs: Any,
    ) -> None:
        """Run the blob checks for one test-data case."""
        self.assertNotEqual(len(kwargs["strings"]), 1)
        if exceptiontype:
            self.go_blob_invalid(cls, **kwargs, exceptiontype=exceptiontype)
        else:
            self.go_blob_valid(cls, **kwargs)

    def go_blob_invalid(
        self: Self,
        cls: type[Any],
        /,
        *,
        exceptiontype: str,
        strings: list[str],
        **kwargs: Any,
    ) -> None:
        """Run the blob invalid checks for one test-data case."""
        with self.assertRaises(Util.import_(exceptiontype)):
            cls.deformat(*strings)

    def go_blob_valid(
        self: Self,
        cls: type[Any],
        /,
        *,
        solution: str,
        strings: list[str],
        **kwargs: Any,
    ) -> None:
        """Run the blob valid checks for one test-data case."""
        rendering: str
        self.assertEqual(cls.deformat(*strings), solution)
        for rendering in strings:
            self.assertEqual(format(cls(string=rendering), solution), rendering)

    def go_cls(
        self: Self,
        cls: type[Any],
        /,
        **typedict: dict[str, Any],
    ) -> None:
        """Run the cls checks for one test-data case."""
        example: tuple[str]
        log: dict[tuple[str], str]
        test_case: dict[str, Any]
        test_name: str
        self.assertGreaterEqual(len(typedict), 30)
        log = dict()
        for test_name, test_case in typedict.items():
            example = tuple(test_case["strings"])
            with self.subTest(test_name=test_name, example=example):
                self.assertNotIn(
                    example,
                    log,
                    "conflict with %r" % log.get(example),
                )
                log[example] = test_name
                self.go_blob(cls, **test_case)

    def test_0(self: Self, /) -> None:
        """Run the recorded cases for this test group."""
        cls: type[Any]
        typename: str
        typedict: dict[Any, Any]
        for typename, typedict in Util.util.data["deformatting"].items():
            cls = Util.import_("v440.core.{0}.{0}".format(typename))
            with self.subTest(typename=typename):
                self.go_cls(cls, **typedict)


class TestStringExamples(unittest.TestCase):
    """Verify string examples behavior."""

    def go_version(
        self: Self, example: str, /, *, valid: bool, **kwargs: Any
    ) -> None:
        """Run the version checks for one test-data case."""
        public_suffix: str
        current: Version
        reference: Version_
        if not valid:
            with self.assertRaises(InvalidVersion):
                Version_(example)
            with self.assertRaises(VersionError):
                Version(string=example)
            return
        current = Version(string=example)
        reference = Version_(example)
        self.assertEqual(reference, current.packaging)
        public_suffix = reference.base_version
        while public_suffix.endswith(".0"):
            public_suffix = public_suffix[:-2]
        self.assertTrue(public_suffix, current.public.base.packaging)
        self.assertEqual(
            reference.dev,
            current.public.qual.dev.packaging,
        )
        self.assertEqual(
            reference.local,
            current.local.packaging,
        )
        self.assertEqual(
            reference.is_devrelease,
            current.public.qual.isdevrelease(),
        )
        self.assertEqual(
            reference.is_postrelease,
            current.public.qual.ispostrelease(),
        )
        self.assertEqual(
            reference.is_prerelease,
            current.public.qual.isprerelease(),
        )
        self.assertEqual(
            reference.major,
            current.public.base.release.major,
        )
        self.assertEqual(
            reference.micro,
            current.public.base.release.micro,
        )
        self.assertEqual(
            reference.minor,
            current.public.base.release.minor,
        )
        self.assertEqual(
            reference.post,
            current.public.qual.post.packaging,
        )
        self.assertEqual(
            reference.pre,
            current.public.qual.pre.packaging,
        )
        public_suffix = reference.public
        self.assertTrue(public_suffix.startswith(current.public.base.packaging))
        public_suffix = public_suffix[len(current.public.base.packaging) :]
        self.assertTrue(public_suffix.endswith(current.public.qual.packaging))
        if current.public.qual.packaging:
            public_suffix = public_suffix[: -len(current.public.qual.packaging)]
        self.assertEqual(public_suffix, ".0" * (len(public_suffix) // 2))
        self.assertEqual(
            reference.release[: len(current.public.base.release)],
            current.public.base.release.packaging,
        )

    def test_versions(self: Self, /) -> None:
        """Verify versions behavior."""
        example: str
        case: dict[Any, Any]
        for example, case in Util.util.examples["Version"].items():
            with self.subTest(example=example):
                self.go_version(example, **case)


class TestTypeNames(unittest.TestCase):
    """Verify type names behavior."""

    def go_name(self: Self, name: str, /) -> None:
        """Run the name checks for one test-data case."""
        cls: type[Any]
        cls = Util.import_(f"v440.core.{name}.{name}")
        self.assertEqual(cls.__name__, name)

    def test_0(self: Self) -> None:
        """Run the recorded cases for this test group."""
        name: str
        for name in Util.util.data["synonymous-to-empty"]:
            self.go_name(name)


class TestStringExamples0(unittest.TestCase):
    """Verify string examples 0 behavior."""

    def go_examples(
        self: Self, /, clsname: str, tables: dict[Any, Any]
    ) -> None:
        """Run the examples checks for one test-data case."""
        cls: type
        split: dict[Any, Any]
        example: str
        case: dict[Any, Any]
        cls = Util.import_("v440.core.{0}.{0}".format(clsname))
        split = {False: dict(), True: dict()}
        for example, case in tables.items():
            split[case["valid"]][example] = case
        for example, case in split[False].items():
            with self.subTest(valid=False, example=example):
                self.go_invalid_example(cls, example, **case)
        for example, case in split[True].items():
            with self.subTest(valid=True, example=example):
                self.go_valid_example(cls, example, **case)

    def go_invalid_example(
        self: Self, cls: type, example: str, /, **kwargs: Any
    ) -> None:
        """Run the invalid example checks for one test-data case."""
        with self.assertRaises(VersionError):
            cls(string=example)

    def go_valid_example(
        self: Self,
        /,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the valid example checks for one test-data case."""
        self.go_valid_example_deformatted(*args, **kwargs)
        self.go_valid_example_formatted(*args, **kwargs)
        self.go_valid_example_remake(*args, **kwargs)
        self.go_valid_example_repr(*args, **kwargs)
        self.go_valid_example_str(*args, **kwargs)
        self.go_valid_example_synonym(*args, **kwargs)

    def go_valid_example_deformatted(
        self: Self,
        cls: Any,
        example: str,
        /,
        *,
        deformatted: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Run the valid example deformatted checks for one test-data case."""
        spec: str
        spec = cls.deformat(example)
        if deformatted is not None:
            self.assertEqual(spec, deformatted)

    def go_valid_example_formatted(
        self: Self,
        cls: type,
        example: str,
        /,
        *,
        formatted: dict[str, str] | tuple[()] = (),
        **kwargs: Any,
    ) -> None:
        """Run the valid example formatted checks for one test-data case."""
        instance: Any
        spec: str
        target: str
        instance = cls(string=example)
        for spec, target in dict(formatted).items():
            with self.subTest(spec=spec, target=target):
                self.assertEqual(target, format(instance, spec))

    def go_valid_example_remake(
        self: Self,
        cls: Any,
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        """Run the valid example remake checks for one test-data case."""
        instance: Any
        remake: str
        spec: str
        instance = cls(string=example)
        spec = cls.deformat(example)
        remake = format(instance, spec)
        self.assertEqual(
            example,
            remake,
            msg="example=%r, remake=%r, spec=%r" % (example, remake, spec),
        )

    def go_valid_example_repr(
        self: Self,
        cls: type,
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        """Run the valid example repr checks for one test-data case."""
        bool_: bool
        instance: Any
        repr_: str | None
        instance = cls(string=example)
        bool_ = kwargs.get("bool", True)
        self.assertEqual(bool(instance), bool_)
        repr_ = cast(str | None, kwargs.get("repr"))
        if repr_ is not None:
            self.assertEqual(repr(instance), repr_)

    def go_valid_example_str(
        self: Self,
        cls: type,
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        """Run the valid example str checks for one test-data case."""
        instance: Any
        answer: str
        solution: str | None
        instance = cls(string=example)
        answer = str(instance)
        self.assertEqual(answer, instance.string)
        self.assertEqual(answer, format(instance))
        self.assertEqual(answer, format(instance, ""))
        solution = cast(str | None, kwargs.get("str"))
        if solution is not None:
            self.assertEqual(str(instance), solution)

    def go_valid_example_synonym(
        self: Self,
        cls: type[Any],
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        """Run the valid example synonym checks for one test-data case."""
        empty_rendering: str
        instance: Any
        synonym_spec: str
        synonym_rendering: str
        synonym_spec = Util.util.data["synonymous-to-empty"][cls.__name__][""][
            "synonym"
        ]
        instance = cls(string=example)
        empty_rendering = format(instance, "")
        synonym_rendering = format(instance, synonym_spec)
        with self.subTest(
            msg="synonym",
            empty=empty_rendering,
            synonym=synonym_rendering,
        ):
            self.assertEqual(empty_rendering, synonym_rendering)

    def test_0(self: Self, /) -> None:
        """Run the recorded cases for this test group."""
        class_name: str
        tables: dict[Any, Any]
        for class_name, tables in Util.util.examples.items():
            with self.subTest(clsname=class_name):
                self.go_examples(class_name, tables)


class TestTotalAttrSetter(unittest.TestCase):
    """Verify total attr setter behavior."""

    def go_clsname(
        self: Self,
        clsname: str,
        legacy_table: dict[Any, Any],
        /,
    ) -> None:
        """Run the clsname checks for one test-data case."""
        cls: type
        legacy_name: str
        task: dict[Any, Any]
        cls = getattr(getattr(core, clsname), clsname)
        for legacy_name, task in legacy_table.items():
            with self.subTest(legacy_name=legacy_name):
                self.go_task(cls, **task)

    def go_task(
        self: Self,
        /,
        *args: Any,
        exceptiontype: str,
        **kwargs: Any,
    ) -> None:
        """Run the task checks for one test-data case."""
        if exceptiontype:
            self.go_task_invalid(*args, **kwargs, exceptiontype=exceptiontype)
        else:
            self.go_task_valid(*args, **kwargs)

    def go_task_invalid(
        self: Self,
        cls: type,
        /,
        *,
        exceptiontype: str,
        query: list[Any],
        queryname: str,
        **kwargs: Any,
    ) -> None:
        """Run the task invalid checks for one test-data case."""
        exception_class: type[Exception]
        instance: Any
        exception_class = Util.import_(exceptiontype)
        instance = cls()
        with self.assertRaises(exception_class):
            setattr(instance, queryname, query)

    def go_task_valid(
        self: Self,
        cls: type,
        /,
        *,
        query: list[Any],
        queryname: str,
        **_kwargs: Any,
    ) -> None:
        """Run the task valid checks for one test-data case."""
        instance: Any
        instance = cls()
        setattr(instance, queryname, query)

    def test_0(self: Self, /) -> None:
        """Run the recorded cases for this test group."""
        class_name: str
        legacy_table: dict[Any, Any]
        for class_name, legacy_table in Util.util.data["attr-setter"].items():
            with self.subTest(clsname=class_name):
                self.go_clsname(class_name, legacy_table)


class TestTotalMethod(unittest.TestCase):
    """Verify total method behavior."""

    def go_clsname(
        self: Self,
        clsname: str,
        legacy_table: dict[Any, Any],
        /,
    ) -> None:
        """Run the clsname checks for one test-data case."""
        cls: type
        legacy_name: str
        task: dict[Any, Any]
        cls = getattr(getattr(core, clsname), clsname)
        for legacy_name, task in legacy_table.items():
            with self.subTest(legacy_name=legacy_name):
                self.go_task(cls, **task)

    def go_task(
        self: Self,
        cls: type,
        /,
        *,
        args: abc.Sequence[Any] = (),
        attrname: str,
        check: list[Any] | None = None,
        kwargs: dict[Any, Any] | tuple[()] = (),
        query: list[Any],
        queryname: str,
        **_kwargs: Any,
    ) -> None:
        """Run the task checks for one test-data case."""
        result: Any
        method: Any
        instance: Any
        instance = cls()
        setattr(instance, queryname, query)
        method = getattr(instance, attrname)
        result = method(*args, **dict(kwargs))
        self.assertEqual(result, check)

    def test_1(self: Self, /) -> None:
        """Run the recorded cases for this test group."""
        class_name: str
        legacy_table: dict[Any, Any]
        for class_name, legacy_table in Util.util.data["total-method"].items():
            with self.subTest(clsname=class_name):
                self.go_clsname(class_name, legacy_table)


class TestFunction(unittest.TestCase):
    """Verify function behavior."""

    def go_clsname(
        self: Self,
        clsname: str,
        legacy_table: dict[Any, Any],
        /,
    ) -> None:
        """Run the clsname checks for one test-data case."""
        cls: type
        legacy_name: str
        task: dict[Any, Any]
        cls = getattr(getattr(core, clsname), clsname)
        for legacy_name, task in legacy_table.items():
            with self.subTest(legacy_name=legacy_name):
                self.go_task(cls, **task)

    def go_task(
        self: Self,
        cls: type,
        /,
        *,
        args: abc.Sequence[Any] = (),
        kwargs: dict[Any, Any] | tuple[()] = (),
        query: list[Any],
        queryname: str,
        solution: Any,
        solutionname: str,
        **_kwargs: Any,
    ) -> None:
        """Run the task checks for one test-data case."""
        result: Any
        instance: Any
        instance = cls()
        setattr(instance, queryname, query)
        result = Util.import_(solutionname)(instance, *args, **dict(kwargs))
        self.assertEqual(result, solution)

    def test_2(self: Self, /) -> None:
        """Run the recorded cases for this test group."""
        class_name: str
        legacy_table: dict[Any, Any]
        for class_name, legacy_table in Util.util.data["function"].items():
            with self.subTest(clsname=class_name):
                self.go_clsname(class_name, legacy_table)


class TestVersionEpochGo(unittest.TestCase):
    """Verify version epoch go behavior."""

    def test_0(self: Self, /) -> None:
        """Run the recorded cases for this test group."""
        key: str
        case: dict[str, Any]
        for key, case in Util.util.data["epoch"][""].items():
            with self.subTest(key=key):
                self.go(**case)

    def go(
        self: Self,
        /,
        full: Any,
        part: Any,
        query: Any = None,
        key: str = "",
    ) -> None:
        """Run the checks for one test-data case."""
        message: str
        version: Version
        message = "epoch %r" % key
        version = Version(string="1.2.3")
        version.public.base.epoch = query
        self.assertEqual(str(version), full, message=message)
        self.assertIsInstance(version.public.base.epoch, int, message=message)
        self.assertEqual(version.public.base.epoch, part, message=message)


class TestSlicingGo(unittest.TestCase):
    """Verify slicing go behavior."""

    def go_cls(self: Self, cls: type[Any], /, **kwargs: Any) -> None:
        """Run the cls checks for one test-data case."""
        key: str
        case: dict[str, Any]
        for key, case in kwargs.items():
            with self.subTest(key=key):
                self.go_cls_key(cls, **case)

    def go_cls_key(
        self: Self,
        cls: type[Any],
        /,
        *,
        change: Any,
        exceptiontype: str,
        query: Any,
        solution: str,
        start: Any = None,
        stop: Any = None,
        step: Any = None,
    ) -> None:
        """Run the cls key checks for one test-data case."""
        context: Any
        exception_class: Any
        value: Any
        value = cls(string=query)
        if exceptiontype:
            exception_class = Util.import_(exceptiontype)
            context = self.assertRaises(exception_class)
        else:
            context = contextlib.nullcontext()
        with context:
            value[start:stop:step] = change
        self.assertEqual(str(value), solution)

    def test_2(self: Self, /) -> None:
        """Run the recorded cases for this test group."""
        cls: type[Any]
        class_name: str
        cases: dict[Any, Any]
        for class_name, cases in Util.util.data["slicing"].items():
            cls = Util.import_(f"v440.core.{class_name}.{class_name}")
            with self.subTest(typename=class_name):
                self.go_cls(cls, **cases)


class TestFormat(unittest.TestCase):
    """Verify format behavior."""

    def go(self: Self, text: str, /, *, valid: bool, **kwargs: Any) -> None:
        """Run the checks for one test-data case."""
        reference: Version_
        expected: str
        spec: str
        rendered: str
        if not valid:
            return
        reference = Version_(text)
        expected = str(reference)
        spec = "#." * len(reference.release)
        spec = spec[:-1]
        rendered = format(Version(string=text), spec)
        self.assertEqual(expected, rendered)

    def test_0(self: Self, /) -> None:
        """Run the recorded cases for this test group."""
        example: str
        case: dict[str, Any]
        for example, case in Util.util.examples["Version"].items():
            with self.subTest(example=example):
                self.go(example, **case)


class TestOrder(unittest.TestCase):
    """Verify order behavior."""

    def go(
        self: Self,
        *,
        func: abc.Callable[[Any, Any], Any],
        left_text: str,
        right_text: str,
    ) -> None:
        """Run the checks for one test-data case."""
        left_reference: Version_
        left_current: Version
        left_roundtrip: Version_
        right_reference: Version_
        right_current: Version
        right_roundtrip: Version_
        backwards: bool
        current: bool
        legacy: bool
        left_reference = Version_(left_text)
        left_current = Version(string=left_text)
        left_roundtrip = left_current.packaging
        right_reference = Version_(right_text)
        right_current = Version(string=right_text)
        right_roundtrip = right_current.packaging
        legacy = func(left_reference, right_reference)
        current = func(left_current, right_current)
        backwards = func(left_roundtrip, right_roundtrip)
        self.assertEqual(
            current,
            legacy,
            (
                f"operator.{func.__name__}({left_text!r}, {right_text!r}) "
                "should match for current and legacy."
            ),
        )
        self.assertEqual(
            current,
            backwards,
            (
                f"operator.{func.__name__}({left_text!r}, {right_text!r}) "
                "should match for current and backwards."
            ),
        )

    def go_op(
        self: Self,
        /,
        func: abc.Callable[[Any, Any], Any],
        pure: list[str],
    ) -> None:
        """Run the op checks for one test-data case."""
        left_text: str
        pair_index: int
        right_text: str
        for pair_index in range(len(pure) ** 2):
            left_text = pure[pair_index // len(pure)]
            right_text = pure[pair_index % len(pure)]
            with self.subTest(left_text=left_text, right_text=right_text):
                self.go(left_text=left_text, right_text=right_text, func=func)

    def test_0(self: Self, /) -> None:
        """Run the recorded cases for this test group."""
        func: abc.Callable[[Any, Any], Any]
        operator_name: str
        pure: list[str]
        example: str
        case: dict[str, Any]
        pure = []
        for example, case in Util.util.examples["Version"].items():
            if case["valid"]:
                pure.append(example)
        for operator_name in ("eq", "ge", "gt", "le", "lt", "ne"):
            func = getattr(operator, operator_name)
            with self.subTest(func=operator_name):
                self.go_op(func=func, pure=pure)


class TestSlots(unittest.TestCase):
    """Verify slots behavior."""

    def go_blob(
        self: Self,
        cls: type[Any],
        /,
        attrname: str,
        attrvalue: Any,
        string: Any = None,
    ) -> None:
        """Run the blob checks for one test-data case."""
        instance: Any
        instance = cls(string=string)
        with self.assertRaises(AttributeError):
            setattr(instance, attrname, attrvalue)

    def go_cls(
        self: Self, cls: type[Any], /, **typetests: dict[str, Any]
    ) -> None:
        """Run the cls checks for one test-data case."""
        testdict: dict[str, Any]
        testname: str
        for testname, testdict in typetests.items():
            with self.subTest(testname=testname):
                self.go_blob(cls, **testdict)

    def test_0(self: Self, /) -> None:
        """Run the recorded cases for this test group."""
        cls: type[Any]
        typename: str
        typetests: dict[str, dict[str, Any]]
        for typename, typetests in Util.util.data[
            "core-non-attributes"
        ].items():
            cls = Util.import_("v440.core.{0}.{0}".format(typename))
            with self.subTest(typename=typename):
                self.go_cls(cls, **typetests)


class TestReleaseAlias(unittest.TestCase):
    """Verify release alias behavior."""

    def test_0(self: Self, /) -> None:
        """Run the recorded cases for this test group."""
        test_label: Any
        case: Any
        for test_label, case in Util.util.data["release-key"][""].items():
            with self.subTest(test_label=test_label):
                self.go(**case)

    def go(self: Self, /, steps: list[Any]) -> None:
        """Run the checks for one test-data case."""
        version: Version
        step: dict[str, Any]
        version = Version()
        for step in steps:
            self.modify(version=version, **step)

    def modify(
        self: Self,
        /,
        version: Version,
        name: str,
        value: Any,
        solution: list[Any] | None = None,
    ) -> None:
        """Apply one recorded release modification and verify its expected result."""
        answer: list[Any]
        setattr(version.public.base.release, name, value)
        if solution is None:
            return
        answer = list(version.public.base.release)
        self.assertEqual(answer, solution)


if __name__ == "__main__":
    unittest.main()
