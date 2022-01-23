from sympy import lambdify, Piecewise, symbols as _symbols, sympify
t = _symbols('t')
del _symbols


def _process(last, funcs, durations):
    position = 0
    for f, d in zip(funcs, durations):
        try:
            pf = f.subs(t, t-position)
        except AttributeError: # not a sympy thing, so a constant.
            pf = sympify(f)
        position += d
        last = f.subs(t, d)
        yield (pf, t < position)
    yield (sympify(last), True)


# Doesn't really need to be used externally, but it looks nice.
def Segments(*args):
    return _Segments(args[::2], args[1::2])


class _Segments:
    def __new__(cls, funcs, durations): # TODO: interning
        instance = super().__new__(cls)
        instance._funcs = tuple(funcs)
        instance._durations = tuple(durations)
        return instance


    def __or__(self, other):
        if isinstance(other, tuple):
            other = Segments(*other)
        if not isinstance(other, _Segments):
            return NotImplemented # could be a Joiner...
        return _Segments(
            self._funcs + other._funcs, self._durations + other._durations
        )


    def formula(self, dtype):
        symbolic = Piecewise(*_process(dtype(0), self._funcs, self._durations))
        return lambdify(t, symbolic, 'math'), sum(self._durations)
