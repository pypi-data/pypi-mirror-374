from contextlib import contextmanager
from typing import *

__all__ = ["Exceptor"]


class Exceptor:

    __slots__ = ("_captured",)

    captured: Optional[BaseException]

    def __init__(self: Self) -> None:
        self._captured = None

    @contextmanager
    def capture(self: Self, *args: type) -> Generator:
        "This contextmanager captures exceptions."
        try:
            yield self
        except args as e:
            self._captured = e
        else:
            self._captured = None

    @property
    def captured(self: Self) -> property:
        "This property stores the captured exception."
        return self._captured
