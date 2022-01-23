from .segments import _Segments, Segments


class Source:
    def __init__(self, clock, resulttype=float):
        self._clock = clock
        self._resulttype = resulttype
        self._loop = None
        self._end = self._value()
        self.segments = Segments()
        self._transition = None


    @property
    def loop(self):
        return self._loop


    def _value(self, raw=0):
        return self._clock.dtype(raw)


    @loop.setter
    def loop(self, value):
        if value is not None: # normalize it to the clock's type
            value = self._value(value)
        self._loop = value


    @property
    def segments(self):
        return self._segments


    @segments.setter
    def segments(self, value):
        if not isinstance(value, _Segments):
            value = Segments(*value)
        self._segments = value
        self._formula, self._end = self._segments.formula(self._resulttype)
        self._clock.now = 0


    @property
    def value(self):
        # We must be sure to only access 'now' once, because of auto clocks
        now, l = self._clock.now, self.loop
        if l is not None:
            now = l + (now - l) % (self._end - l)
        return self._resulttype(self._formula(now))
