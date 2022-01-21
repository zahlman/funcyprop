from collections.abc import Iterable
from functools import partial
from time import time


class Clock:
    def __init__(self, source):
        # source -> function taking no arguments and returning a number
        # representing time elapsed (should be monotonically increasing).
        self._source = source
        self._last = source()
        # start of current 'lap'.
        self._start = self._last
        # data type, so everyone can sync up
        self._dtype = type(self._last)
        # accumulated time for previous 'laps'.
        self._elapsed = type(self._last)(0)
        # scaling factor for current lap time.
        self._rate = type(self._last)(1)
        # A lap ends whenever the 'now' is set or 'rate' changes.


    def _read(self):
        # always use the current value to set the marker
        self._last = max(self._last, self._source())


    def _lap(self):
        self._elapsed = self.now
        self._start = self._last


    def tick(self):
        self._last += 1 # for attribute/item-based clocks.


    @property
    def dtype(self): # read-only.
        return self._dtype


    @property
    def rate(self):
        return self._rate


    @rate.setter
    def rate(self, value):
        self._lap()
        self._rate = type(self._last)(value)


    @property
    def now(self):
        self._read()
        result = self._elapsed + (self._last - self._start) * self._rate
        return result


    @now.setter
    def now(self, value):
        self._lap()
        self._elapsed = value


def make_clock(*args, dtype=float):
    if len(args) == 2:
        context, attrname = args
        assert isinstance(attrname, str)
        return Clock(partial(getattr, context, attrname))
    if len(args) == 0:
        return Clock(time)
    value, = args
    if callable(value):
        return Clock(value)
    raise TypeError('unrecognized clock source')
