from contextlib import contextmanager
from typing import *

__all__ = ["Exceptor"]


class Exceptor:

    captured: Optional[type]

    def __init__(self: Self) -> None:
        self.captured = None

    @contextmanager
    def capture(self: Self, *args: type) -> Generator:
        excTypes: tuple
        if args == ():
            excTypes = (BaseException,)
        else:
            excTypes = args
        try:
            yield self
        except excTypes as e:
            self.captured = e
        else:
            self.captured = None
