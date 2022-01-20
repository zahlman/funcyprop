from collections.abc import Iterable
from functools import partial
from time import time


class Clock:
    def __init__(self, source, dtype):
        self._source = source
        self._dtype = dtype
        self._start = self._dtype(0)
        self._last = self._dtype(0)


    # default implementation expects `source` to be a callable.
    def _read(self, setting):
        # always use the current value to set the marker
        self._last = self._dtype(max(self._last, self._source()))


    @property
    def now(self):
        self._read(False)
        return self._last - self._start


    @now.setter
    def now(self, value):
        self._read(True)
        self._start = self._last - value


class IterClock(Clock):
    def __init__(self, source, dtype):
        super().__init__(source, dtype)
        self._source = iter(self._source)
        self._last = self._dtype(0)


    def _read(self, setting):
        # when setting the offset, use the cached value (so as to sync neatly).
        if not setting:
            self._last = self._dtype(max(self._last, next(self._source)))


def make_clock(*args, dtype=float):
    if len(args) == 2:
        context, attrname = args
        assert isinstance(attrname, str)
        return Clock(partial(getattr, context, attrname), dtype)
    value, = args
    if len(args) == 0:
        return Clock(time, dtype)
    if callable(value):
        return Clock(value, dtype)
    if isinstance(value, Iterable):
        return IterClock(value, dtype)
    raise TypeError('unrecognized clock source')

