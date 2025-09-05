from contextlib import contextmanager
from typing import *

__all__ = ["Exceptor"]


class Exceptor:

    __slots__ = ("captured",)

    captured: Optional[BaseException]

    def __init__(self: Self) -> None:
        self.captured = None

    @contextmanager
    def capture(self: Self, *args: type) -> Generator:
        try:
            yield self
        except args as e:
            self.captured = e
        else:
            self.captured = None
