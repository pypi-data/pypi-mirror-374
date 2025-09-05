import unittest
from typing import *

from exceptors.core import Exceptor


class TestExceptor(unittest.TestCase):
    def test_captures_matching_exception(self: Self) -> None:
        ex = Exceptor()
        with ex.capture(ValueError):
            raise ValueError("bad value")
        self.assertIsNotNone(ex.captured)
        self.assertIsInstance(ex.captured, ValueError)
        self.assertEqual(str(ex.captured), "bad value")

    def test_no_exception_leaves_captured_none(self: Self) -> None:
        ex = Exceptor()
        with ex.capture(ValueError):
            pass
        self.assertIsNone(ex.captured)

    def test_captures_one_of_multiple_types(self: Self) -> None:
        ex = Exceptor()
        with ex.capture(ValueError, KeyError):
            raise KeyError("missing")
        self.assertIsNotNone(ex.captured)
        self.assertIsInstance(ex.captured, KeyError)
        self.assertEqual(
            str(ex.captured), "'missing'"
        )  # KeyError stringifies with quotes

    def test_non_matching_exception_propagates_and_does_not_set_captured(
        self: Self,
    ) -> None:
        ex = Exceptor()
        with self.assertRaises(ZeroDivisionError):
            with ex.capture(ValueError, KeyError):
                1 / 0  # ZeroDivisionError not in capture set
        # Since the exception propagated out, Exceptor should not have recorded anything
        self.assertIsNone(ex.captured)

    def test_reuse_and_reset_semantics(self: Self) -> None:
        ex = Exceptor()

        # First, capture an exception
        with ex.capture(RuntimeError):
            raise RuntimeError("first")
        self.assertIsInstance(ex.captured, RuntimeError)

        # Next, a clean block should reset captured to None
        with ex.capture(RuntimeError):
            pass
        self.assertIsNone(ex.captured)

        # Finally, capture another (different) exception type by passing multiple
        with ex.capture(RuntimeError, TypeError):
            raise TypeError("second")
        self.assertIsInstance(ex.captured, TypeError)

    def test_empty_type_tuple_never_catches(self: Self) -> None:
        ex = Exceptor()
        # Passing no types should behave like catching nothing: exception propagates
        with self.assertRaises(ValueError):
            with ex.capture():
                raise ValueError("won't be caught")
        self.assertIsNone(ex.captured)


if __name__ == "__main__":
    unittest.main()
