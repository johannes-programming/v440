"""Exercise v440 against recorded version examples."""

from __future__ import annotations

__all__: list[str] = [
    "TestOrder",
    "TestReleaseAlias",
    "TestSlicingGo",
    "TestTypeDeformatting",
    "TestTypeExamples",
    "TestTypeFunction",
    "TestTypeNames",
    "TestTypeSlots",
    "TestTypeTotalAttrSetter",
    "TestTypeTotalMethod",
    "TestVersionEpochGo",
]

import contextlib
import enum
import functools
import importlib
import io
import operator
import tomllib
import types
import unittest
from abc import ABC, abstractmethod
from collections import abc
from pathlib import Path
from typing import Any, ClassVar, Self, cast

from packaging.version import InvalidVersion
from packaging.version import Version as Version_

from v440 import MiniLangError, Version, VersionError


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


class BaseTestType(ABC):
    KEY0: ClassVar[str]

    @abstractmethod
    def go_type(
        self: Self, typename: str, cls: type[Any], /, **kwargs: Any
    ) -> None: ...
    @abstractmethod
    def subTest(
        self: Self, /, *, typename: str
    ) -> contextlib.AbstractContextManager[Any]: ...
    def test_key0(self: Self, /) -> None:
        """Test under KEY0."""
        cls: type[Any]
        typename: str
        typedict: dict[Any, Any]
        for typename, typedict in Util.util.data[type(self).KEY0].items():
            cls = Util.import_("v440.core.{0}.{0}".format(typename))
            with self.subTest(typename=typename):
                self.go_type(typename, cls, **typedict)


class TestOrder(unittest.TestCase):
    """Check ordering compatibility between v440 and packaging.version."""

    def go(
        self: Self,
        *,
        func: abc.Callable[[Any, Any], Any],
        x: str,
        y: str,
    ) -> None:
        """Compare ordering results across packaging and v440 representations."""
        left_reference: Version_
        left_current: Version
        left_packaging: Version_
        right_reference: Version_
        right_current: Version
        right_packaging: Version_
        backwards: bool
        current: bool
        legacy: bool
        left_reference = Version_(x)
        left_current = Version(string=x)
        left_packaging = left_current.packaging
        right_reference = Version_(y)
        right_current = Version(string=y)
        right_packaging = right_current.packaging
        legacy = func(left_reference, right_reference)
        current = func(left_current, right_current)
        backwards = func(left_packaging, right_packaging)
        self.assertEqual(
            current,
            legacy,
            f"operator.{func.__name__}({x!r}, {y!r}) should match for current and legacy.",
        )
        self.assertEqual(
            current,
            backwards,
            f"operator.{func.__name__}({x!r}, {y!r}) should match for current and backwards.",
        )

    def go_op(
        self: Self,
        /,
        func: abc.Callable[[Any, Any], Any],
        pure: list[str],
    ) -> None:
        """Run one comparison operator across every ordered pair of valid versions."""
        i: int
        for i in range(len(pure) ** 2):
            left = pure[i // len(pure)]
            right = pure[i % len(pure)]
            with self.subTest(x=left, y=right):
                self.go(x=left, y=right, func=func)

    def test_0(self: Self, /) -> None:
        """Run every comparison operator across all valid version examples."""
        pure: list[str]
        example: str
        case: dict[str, Any]
        pure = []
        for example, case in Util.util.data["examples"]["Version"].items():
            if case["valid"]:
                pure.append(example)
        for operator_name in ("eq", "ge", "gt", "le", "lt", "ne"):
            func = getattr(operator, operator_name)
            with self.subTest(func=operator_name):
                self.go_op(func=func, pure=pure)


class TestReleaseAlias(unittest.TestCase):
    """Check major, minor, and micro release aliases through configured updates."""

    def test_0(self: Self, /) -> None:
        """Run all configured release-alias cases."""
        test_label: Any
        steps: Any
        for test_label, steps in Util.util.data["release-key"][""].items():
            with self.subTest(test_label=test_label):
                self.go(**steps)

    def go(self: Self, /, steps: list[Any]) -> None:
        """Apply the configured release-alias modification steps."""
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
        """Apply one release alias update and optionally verify the resulting sequence."""
        answer: list[Any]
        setattr(version.public.base.release, name, value)
        if solution is None:
            return
        answer = list(version.public.base.release)
        self.assertEqual(answer, solution)


class TestSlicingGo(unittest.TestCase, BaseTestType):
    """Check configured slice assignments for list-like version components."""

    KEY0 = "slicing"

    def go_type(
        self: Self, typename: str, cls: type[Any], /, **kwargs: Any
    ) -> None:
        """Run configured slicing cases for one sequence class."""
        case_name: str
        case: dict[str, Any]
        for case_name, case in kwargs.items():
            with self.subTest(key=case_name):
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
        """Apply one configured slice assignment and verify its result or declared exception."""
        ctx: Any
        exc: Any
        obj: Any
        obj = cls(string=query)
        if exceptiontype:
            exc = Util.import_(exceptiontype)
            ctx = self.assertRaises(exc)
        else:
            ctx = contextlib.nullcontext()
        with ctx:
            obj[start:stop:step] = change
        self.assertEqual(str(obj), solution)


class TestTypeDeformatting(unittest.TestCase, BaseTestType):
    """Verify deformatting behavior."""

    KEY0: ClassVar[str] = "deformatting"

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
            self.assertEqual(
                format(cls(string=rendering), solution), rendering
            )

    def go_type(
        self: Self,
        typename: str,
        cls: type[Any],
        /,
        **typedict: dict[str, Any],
    ) -> None:
        """Run deformatting cases for one target class and reject duplicate example sets."""
        example: tuple[str]
        log: dict[tuple[str], str]
        self.assertGreaterEqual(len(typedict), 30)
        log = dict()
        for testname, testdict in typedict.items():
            example = tuple(testdict["strings"])
            with self.subTest(testname=testname, example=example):
                self.assertNotIn(
                    example,
                    log,
                    "conflict with %r" % log.get(example),
                )
                log[example] = testname
                self.go_blob(cls, **testdict)


class TestTypeExamples(unittest.TestCase, BaseTestType):
    """Check validity, formatting, reconstruction, and representations for recorded core examples."""

    KEY0 = "examples"

    def go_type(
        self: Self,
        typename: str,
        cls: type[Any],
        /,
        **tables: Any,
    ) -> None:
        """Partition examples by validity and run the corresponding checks."""
        for example, case in tables.items():
            with self.subTest(example=example):
                self.go_example(typename, cls, example, **case)

    def go_example(
        self: Self,
        typename: str,
        cls: type[Any],
        example: str,
        /,
        *,
        valid: bool,
        **case: Any,
    ) -> None:
        if valid:
            self.go_example_valid(typename, cls, example, **case)
        else:
            self.go_example_invalid(typename, cls, example, **case)

    def go_example_invalid(
        self: Self,
        typename: str,
        cls: type[Any],
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        """Verify that one invalid string is rejected with VersionError."""
        with self.assertRaises(VersionError):
            cls(string=example)
        if typename != "Version":
            return
        with self.assertRaises(InvalidVersion):
            Version_(example)

    def go_example_valid(
        self: Self,
        /,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run every rendering and reconstruction check for one valid example."""
        self.go_example_valid_deformatted(*args, **kwargs)
        self.go_example_valid_formatted(*args, **kwargs)
        self.go_example_valid_remake(*args, **kwargs)
        self.go_example_valid_repr(*args, **kwargs)
        self.go_example_valid_str(*args, **kwargs)
        self.go_example_valid_synonym(*args, **kwargs)
        self.go_example_valid_unformattable(*args, **kwargs)
        self.go_example_valid_version(*args, **kwargs)

    def go_example_valid_deformatted(
        self: Self,
        typename: str,
        cls: type[Any],
        example: str,
        /,
        *,
        deformatted: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Verify the inferred deformatting specification for one valid example."""
        spec: str
        spec = cls.deformat(example)
        if deformatted is not None:
            self.assertEqual(spec, deformatted)

    def go_example_valid_formatted(
        self: Self,
        typename: str,
        cls: type[Any],
        example: str,
        /,
        *,
        formatted: dict[str, str] | tuple[()] = (),
        **kwargs: Any,
    ) -> None:
        """Verify declared format specifications for one valid example."""
        obj: Any
        spec: str
        target: str
        obj = cls(string=example)
        for spec, target in dict(formatted).items():
            with self.subTest(spec=spec, target=target):
                self.assertEqual(target, format(obj, spec))

    def go_example_valid_remake(
        self: Self,
        typename: str,
        cls: type[Any],
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        """Verify that deformatting and formatting reproduce the original example."""
        obj: Any
        remake: str
        spec: str
        obj = cls(string=example)
        spec = cls.deformat(example)
        remake = format(obj, spec)
        self.assertEqual(
            example,
            remake,
            msg="example=%r, remake=%r, spec=%r" % (example, remake, spec),
        )

    def go_example_valid_repr(
        self: Self,
        typename: str,
        cls: type[Any],
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        """Verify truthiness and repr expectations for one valid example."""
        bool_: bool
        obj: Any
        repr_: str | None
        obj = cls(string=example)
        bool_ = kwargs.get("bool", True)
        self.assertEqual(bool(obj), bool_)
        repr_ = cast(str | None, kwargs.get("repr"))
        if repr_ is not None:
            self.assertEqual(repr(obj), repr_)

    def go_example_valid_str(
        self: Self,
        typename: str,
        cls: type[Any],
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        """Verify canonical string rendering for one valid example."""
        obj: Any
        answer: str
        solution: str | None
        obj = cls(string=example)
        answer = str(obj)
        self.assertEqual(answer, obj.string)
        self.assertEqual(answer, format(obj))
        self.assertEqual(answer, format(obj, ""))
        solution = cast(str | None, kwargs.get("str"))
        if solution is not None:
            self.assertEqual(str(obj), solution)

    def go_example_valid_synonym(
        self: Self,
        typename: str,
        cls: type[Any],
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        """Verify that a documented format synonym matches the empty specification."""
        obj: Any
        syn: str
        syn = Util.util.data["synonymous-to-empty"][cls.__name__][""][
            "synonym"
        ]
        obj = cls(string=example)
        empty_rendering = format(obj, "")
        synonym_rendering = format(obj, syn)
        with self.subTest(
            msg="synonym", empty=empty_rendering, synonym=synonym_rendering
        ):
            self.assertEqual(empty_rendering, synonym_rendering)

    def go_example_valid_unformattable(
        self: Self,
        typename: str,
        cls: type[Any],
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        obj = cls(string=example)
        for spec in Util.util.data["unformattable"][cls.__name__]:
            with (
                self.subTest(unformattable=spec),
                self.assertRaises(MiniLangError),
            ):
                format(obj, spec)

    def go_example_valid_version(
        self: Self,
        typename: str,
        cls: type[Any],
        text: str,
        /,
        **kwargs: Any,
    ) -> None:
        if typename != "Version":
            return
        self.go_example_valid_version_format(text, **kwargs)
        self.go_example_valid_version_mirror(text, **kwargs)

    def go_example_valid_version_format(
        self: Self,
        text: str,
        /,
        **kwargs: Any,
    ) -> None:
        """Compare one valid version format with packaging.version output."""
        reference: Version_
        expected: str
        spec: str
        actual: str
        reference = Version_(text)
        expected = str(reference)
        spec = "#." * len(reference.release)
        spec = spec[:-1]
        actual = format(Version(string=text), spec)
        self.assertEqual(expected, actual)

    def go_example_valid_version_mirror(
        self: Self,
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        """Compare one version example with packaging.version behavior."""
        base_version: str
        current: Version
        reference: Version_
        current = Version(string=example)
        reference = Version_(example)
        self.assertEqual(reference, current.packaging)
        base_version = reference.base_version
        while base_version.endswith(".0"):
            base_version = base_version[:-2]
        self.assertTrue(base_version, current.public.base.packaging)
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
        base_version = reference.public
        self.assertTrue(base_version.startswith(current.public.base.packaging))
        base_version = base_version[len(current.public.base.packaging) :]
        self.assertTrue(base_version.endswith(current.public.qual.packaging))
        if current.public.qual.packaging:
            base_version = base_version[: -len(current.public.qual.packaging)]
        self.assertEqual(base_version, ".0" * (len(base_version) // 2))
        self.assertEqual(
            reference.release[: len(current.public.base.release)],
            current.public.base.release.packaging,
        )


class TestTypeFunction(unittest.TestCase, BaseTestType):
    """Check data-driven function calls against their expected results."""

    KEY0 = "function"

    def go_type(
        self: Self,
        typename: str,
        cls: type[Any],
        /,
        **legacy_table: dict[Any, Any],
    ) -> None:
        """Run configured function cases for one core class."""
        legacy_name: str
        case: dict[Any, Any]
        for legacy_name, case in legacy_table.items():
            with self.subTest(legacy_name=legacy_name):
                self.go_task(cls, **case)

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
        """Invoke one configured function case and verify its result."""
        ans: Any
        obj: Any
        obj = cls()
        setattr(obj, queryname, query)
        ans = Util.import_(solutionname)(obj, *args, **dict(kwargs))
        self.assertEqual(ans, solution)


class TestTypeNames(unittest.TestCase, BaseTestType):
    """Check that documented core type names resolve to their classes."""

    KEY0 = "synonymous-to-empty"

    def go_type(
        self: Self, typename: str, cls: type[Any], /, **kwargs: Any
    ) -> None:
        """Verify that one core class can be imported by its public type name."""
        self.assertEqual(cls.__name__, typename)


class TestTypeSlots(unittest.TestCase, BaseTestType):
    """Check that slotted core classes reject undeclared attributes."""

    KEY0 = "core-non-attributes"

    def go_blob(
        self: Self,
        cls: type[Any],
        /,
        attrname: str,
        attrvalue: Any,
        string: Any = None,
    ) -> None:
        """Verify that one undeclared attribute cannot be assigned."""
        obj: Any
        obj = cls(string=string)
        with self.assertRaises(AttributeError):
            setattr(obj, attrname, attrvalue)

    def go_type(
        self: Self,
        typename: str,
        cls: type[Any],
        /,
        **typetests: dict[str, Any],
    ) -> None:
        """Run slot-protection cases for one class."""
        testdict: dict[str, Any]
        testname: str
        for testname, testdict in typetests.items():
            with self.subTest(testname=testname):
                self.go_blob(cls, **testdict)


class TestTypeTotalAttrSetter(unittest.TestCase, BaseTestType):
    """Check data-driven attribute assignments and their declared exceptions."""

    KEY0 = "attr-setter"

    def go_type(
        self: Self,
        typename: str,
        cls: type[Any],
        /,
        **legacy_table: Any,
    ) -> None:
        """Run attribute-setter cases for one core class."""
        legacy_name: str
        case: dict[Any, Any]
        cls = Util.import_(f"v440.core.{typename}.{typename}")
        for legacy_name, case in legacy_table.items():
            with self.subTest(legacy_name=legacy_name):
                self.go_task(cls, **case)

    def go_task(
        self: Self,
        /,
        *args: Any,
        exceptiontype: str,
        **kwargs: Any,
    ) -> None:
        """Dispatch one attribute-setter case to its valid or invalid check."""
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
        """Verify that one invalid attribute assignment raises its declared exception."""
        exc: type[Exception]
        obj: Any
        exc = Util.import_(exceptiontype)
        obj = cls()
        with self.assertRaises(exc):
            setattr(obj, queryname, query)

    def go_task_valid(
        self: Self,
        cls: type,
        /,
        *,
        query: list[Any],
        queryname: str,
        **_kwargs: Any,
    ) -> None:
        """Apply one valid attribute assignment."""
        obj: Any
        obj = cls()
        setattr(obj, queryname, query)


class TestTypeTotalMethod(unittest.TestCase, BaseTestType):
    """Check data-driven method calls against their expected results."""

    KEY0 = "total-method"

    def go_type(
        self: Self,
        typename: str,
        cls: type[Any],
        /,
        **legacy_table: dict[Any, Any],
    ) -> None:
        """Run method cases for one core class."""
        legacy_name: str
        case: dict[Any, Any]
        for legacy_name, case in legacy_table.items():
            with self.subTest(legacy_name=legacy_name):
                self.go_task(cls, **case)

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
        """Invoke one configured method case and verify its result."""
        ans: Any
        attr: Any
        obj: Any
        obj = cls()
        setattr(obj, queryname, query)
        attr = getattr(obj, attrname)
        ans = attr(*args, **dict(kwargs))
        self.assertEqual(ans, check)


class TestVersionEpochGo(unittest.TestCase):
    """Check epoch assignments from the shared test data."""

    def test_0(self: Self, /) -> None:
        """Run all configured epoch-assignment cases."""
        case_name: str
        case: dict[str, Any]
        for case_name, case in Util.util.data["epoch"][""].items():
            with self.subTest(key=case_name):
                self.go(**case)

    def go(
        self: Self,
        /,
        full: Any,
        part: Any,
        query: Any = None,
        key: str = "",
    ) -> None:
        """Apply one epoch assignment and verify the resulting full and component values."""
        msg: str
        version: Version
        msg = "epoch %r" % key
        version = Version(string="1.2.3")
        version.public.base.epoch = query
        self.assertEqual(str(version), full, msg=msg)
        self.assertIsInstance(version.public.base.epoch, int, msg=msg)
        self.assertEqual(version.public.base.epoch, part, msg=msg)


if __name__ == "__main__":
    unittest.main()
