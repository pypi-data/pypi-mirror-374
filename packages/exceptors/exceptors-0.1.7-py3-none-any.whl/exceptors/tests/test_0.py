import unittest
from typing import *

from exceptors.core import Exceptor


class TestExceptor(unittest.TestCase):
    def test_captures_matching_exception(self: Self) -> None:
        exceptor: Exceptor = Exceptor()
        with exceptor.capture(ValueError):
            raise ValueError("bad value")
        self.assertIsNotNone(exceptor.captured)
        self.assertIsInstance(exceptor.captured, ValueError)
        self.assertEqual(str(exceptor.captured), "bad value")

    def test_no_exception_leaves_captured_none(self: Self) -> None:
        exceptor: Exceptor = Exceptor()
        with exceptor.capture(ValueError):
            pass
        self.assertIsNone(exceptor.captured)

    def test_captures_one_of_multiple_types(self: Self) -> None:
        exceptor: Exceptor = Exceptor()
        with exceptor.capture(ValueError, KeyError):
            raise KeyError("missing")
        self.assertIsNotNone(exceptor.captured)
        self.assertIsInstance(exceptor.captured, KeyError)
        self.assertEqual(
            str(exceptor.captured), "'missing'"
        )  # KeyError stringifies with quotes

    def test_non_matching_exception_propagates_and_does_not_set_captured(
        self: Self,
    ) -> None:
        exceptor: Exceptor = Exceptor()
        with self.assertRaises(ZeroDivisionError):
            with exceptor.capture(ValueError, KeyError):
                1 / 0  # ZeroDivisionError not in capture set
        # Since the exception propagated out, Exceptor should not have recorded anything
        self.assertIsNone(exceptor.captured)

    def test_reuse_and_reset_semantics(self: Self) -> None:
        exceptor: Exceptor = Exceptor()

        # First, capture an exception
        with exceptor.capture(RuntimeError):
            raise RuntimeError("first")
        self.assertIsInstance(exceptor.captured, RuntimeError)

        # Next, a clean block should reset captured to None
        with exceptor.capture(RuntimeError):
            pass
        self.assertIsNone(exceptor.captured)

        # Finally, capture another (different) exception type by passing multiple
        with exceptor.capture(RuntimeError, TypeError):
            raise TypeError("second")
        self.assertIsInstance(exceptor.captured, TypeError)

    def test_empty_type_tuple_never_catches(self: Self) -> None:
        exceptor: Exceptor = Exceptor()
        # Passing no types should behave like catching nothing: exception propagates
        with self.assertRaises(ValueError):
            with exceptor.capture():
                raise ValueError("won't be caught")
        self.assertIsNone(exceptor.captured)


if __name__ == "__main__":
    unittest.main()
