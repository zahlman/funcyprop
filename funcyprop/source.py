from sympy import lambdify, Piecewise, symbols as _symbols, sympify
t = _symbols('t')
del _symbols


class Source:
    def __init__(self, clock, clocktype=float, resulttype=float):
        self._clock = clock
        self._clocktype = clocktype
        self._resulttype = resulttype
        self._funcs = [sympify(clocktype())]
        self._conditions = [True]
        self._loop = None
        self._end = clocktype()
        self._formula = None


    @property
    def loop(self):
        return self._loop


    @loop.setter
    def loop(self, value):
        if value is not None: # normalize it
            value = self._clocktype(value)
        self._loop = value


    def add(self, func, duration):
        self._formula = None # invalidate cache
        # rebase time to the start of the segment.
        self._funcs.insert(-1, func.subs(t, t-self._end))
        self._end += duration
        self._funcs[-1] = sympify(func.subs(t, duration))
        self._conditions.insert(-1, t < self._end)


    def reset(self, now=0):
        # allow recalculation after adding but before value grab, to
        # potentially avoid hiccups
        self.formula
        self._clock.now = now


    @property
    def formula(self):
        # also expose this as read-only, for easier testing.
        if self._formula is None:
            symbolic = Piecewise(*zip(self._funcs, self._conditions))
            self._formula = lambdify(t, symbolic, 'math')
        return self._formula


    @property
    def value(self):
        now, l = self._clock.now, self.loop
        if l is not None:
            now = l + (now - l) % (self._end - l)
        return self._resulttype(self.formula(now))
