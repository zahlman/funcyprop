import time

from sympy import Piecewise, symbols as _symbols, sympify
t = _symbols('t')
del _symbols


__version__ = '0.1.0'


class PiecewiseBuilderT:
    def __init__(self, clocktype=float):
        self._clocktype = clocktype
        self._funcs = []
        self._thresholds = []
        # represents a piecewise function in `t` where the value is
        # self._funcs[i](t) until time self._thresholds[i].
        self._loop = None
        # by default, the value is self._funcs[-1](self._thresholds[-1])
        # from then on. If a loop point is set, instead the function values
        # loop indefinitely from that point until the end.
        self._built = None


    def _recalculate(self):
        if not self._thresholds:
            raise ValueError("can't compute formula for empty builder")
        end = self._thresholds[-1]
        loop = self._loop
        funcs = self._funcs.copy()
        if loop is None:
            conditions = [
                t < threshold for threshold in self._thresholds
            ] + [True]
            funcs.append(sympify(self._funcs[-1].subs(t, end)))
        else:
            modded_t = Piecewise(
                (t, t < loop),
                (loop + (t - loop) % (end - loop), True)
            )
            conditions = [
                modded_t < threshold for threshold in self._thresholds
            ]
        self._built = Piecewise(*zip(funcs, conditions))


    @property
    def loop(self):
        return self._loop


    @loop.setter
    def loop(self, value):
        self._built = None # invalidate so threshold checks can be updated
        if value is not None:
            value = self._clocktype(value)
        self._loop = value


    @property
    def built(self):
        if self._built is None:
            self._recalculate()
        return self._built


    def add(self, func, duration):
        self._built = None # invalidate cache
        end = self._thresholds[-1] if self._thresholds else 0
        # rebase time to the start of the segment.
        self._funcs.append(func.subs(t, t-end))
        self._thresholds.append(duration + end)


class Source:
    def __init__(self, clock=None, clocktype=float, resulttype=float):
        if isinstance(clock, tuple):
            context, attrname = clock
            if not isinstance(attrname, str):
                raise TypeError('invalid clock')
            self._clock = lambda: getattr(context, attrname)
        elif callable(clock):
            self._clock = clock
        elif clock is None:
            self._clock = time.time
        else:
            raise TypeError('invalid clock')
        self._clocktype = clocktype
        self._resulttype = resulttype
        self.now = 0
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


    @property
    def now(self):
        return self._clocktype(self._clock()) - self._start


    @now.setter
    def now(self, value):
        self._start = self._clocktype(self._clock()) - value


    @property
    def value(self):
        return self._resulttype(self.formula.subs(t, self.now))


    def add(self, func, duration):
        self._builder.add(func, duration)
