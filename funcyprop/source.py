from sympy import Piecewise, symbols as _symbols, sympify
t = _symbols('t')
del _symbols


class PiecewiseBuilderT:
    def __init__(self, clocktype=float):
        self._clocktype = clocktype
        self._funcs = [sympify(clocktype())]
        self._conditions = [True]
        self._loop = None
        self._end = clocktype()
        self._built = None


    def _recalculate(self):
        self._built = Piecewise(*zip(self._funcs, self._conditions))


    @property
    def loop(self):
        return self._loop


    @loop.setter
    def loop(self, value):
        if value is not None: # normalize it
            value = self._clocktype(value)
        self._loop = value


    @property
    def loopsize(self):
        l = self.loop
        return None if l is None else self._end - l


    @property
    def built(self):
        if self._built is None:
            self._recalculate()
        return self._built


    def add(self, func, duration):
        self._built = None # invalidate cache
        # rebase time to the start of the segment.
        self._funcs.insert(-1, func.subs(t, t-self._end))
        self._end += duration
        self._funcs[-1] = sympify(func.subs(t, duration))
        self._conditions.insert(-1, t < self._end)


class Source:
    def __init__(self, clock, clocktype=float, resulttype=float):
        self._clock = clock
        self._resulttype = resulttype
        self._builder = PiecewiseBuilderT(clocktype)


    @property
    def formula(self):
        return self._builder.built


    @property
    def loop(self):
        return self._builder.loop


    @loop.setter
    def loop(self, value):
        self._builder.loop = value


    def reset(self, now=0):
        self._clock.now = now


    @property
    def value(self):
        now, l = self._clock.now, self.loop
        if l is not None:
            now = l + (now - l) % self._builder.loopsize
        return self._resulttype(self.formula.subs(t, now))


    def add(self, func, duration):
        self._builder.add(func, duration)
