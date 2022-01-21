from collections.abc import Iterable
from contextlib import contextmanager
from functools import partial
from time import time


class Clock:
    def __init__(self, source):
        # source -> function taking no arguments and returning a number
        # representing time elapsed (should be monotonically increasing).
        self._source = source
        self._last = 0 if source is None else source()
        # start of current 'lap'.
        self._start = self._last
        # data type, so everyone can sync up
        self._dtype = type(self._last)
        # accumulated time for previous 'laps'.
        self._elapsed = type(self._last)(0)
        # scaling factor for current lap time.
        self._rate = type(self._last)(1)
        # A lap ends whenever the 'now' is set or 'rate' changes.
        self._paused = 0 


    def _read(self):
        if self._paused:
            return
        # always use the current value to set the marker
        if self._source is None:
            self._last += self.rate
        else:
            self._last = max(self._last, self._source())


    def _lap(self):
        self._elapsed = self.now
        self._start = self._last


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


    @contextmanager
    def sync(self):
        self._read()
        self._paused += 1
        try:
            yield self
        finally:
            self._paused -= 1


def Call(func=time):
    return Clock(func)


def Auto():
    return Clock(None)


def Manual(): # For convenience
    result = Clock(None)
    result.rate = 0
    return result
