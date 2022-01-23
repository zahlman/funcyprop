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


def _trim(durations, size):
    position = 0
    for d in durations:
        if position + d >= size:
            yield size - position
            break
        yield d
        position += d


# Doesn't really need to be used externally, but it looks nice.
def Segments(*args):
    return _Segments(args[::2], args[1::2])


class _Segments:
    def __new__(cls, funcs, durations): # TODO: interning
        funcs, durations = tuple(funcs), tuple(durations)
        if len(funcs) != len(durations):
            raise ValueError("funcs and durations don't match up")
        if not all(d >= 0 for d in durations):
            raise ValueError("durations can't be negative")
        instance = super().__new__(cls)
        instance._funcs = funcs
        instance._durations = durations
        return instance


    def __eq__(self, other):
        return all(
            sf.equals(of) and sd == od
            for sf, sd, of, od in zip(
                self._funcs, self._durations, other._funcs, other._durations
            )
        )


    def __str__(self):
        args = [None] * (2 * len(self._funcs))
        args[::2] = self._funcs
        args[1::2] = self._durations
        return f'Segments{tuple(args)}'
    __repr__ = __str__


    def __or__(self, other):
        if isinstance(other, tuple):
            other = Segments(*other)
        if not isinstance(other, _Segments):
            return NotImplemented # could be a Joiner...
        return _Segments(
            self._funcs + other._funcs, self._durations + other._durations
        )


    def __add__(self, amount):
        return _Segments(
            (f + amount for f in self._funcs),
            self._durations
        )


    def __mul__(self, amount):
        return _Segments(
            (f * amount for f in self._funcs),
            self._durations
        )


    def __sub__(self, amount):
        return self + (-amount)


    def __truediv__(self, amount):
        return self * (1 / amount)


    def __matmul__(self, amount): # change rate inversely
        if amount < 0:
            return self.reverse() @ -amount
        return _Segments(
            (f.subs(t, t*amount) for f in self._funcs),
            (d / amount for d in self._durations)
        )


    def __rmatmul__(self, func): # compose the function
        return _Segments(
            (func(f) for f in self._funcs),
            self._durations
        )


    def __getitem__(self, s): # slice the sequences
        return _Segments(self._funcs[s], self._durations[s])


    def reverse(self):
        fs, ds = self._funcs, self._durations
        return _Segments(
            (f.subs(t, d-t) for f, d in zip(fs[::-1], ds[::-1])), reversed(ds)
        )


    def cut(self, size): # segments up until the given amount of time
        trimmed = tuple(_trim(self._durations, size))
        return _Segments(self._funcs[:len(trimmed)], trimmed)


    def formula(self, dtype):
        symbolic = Piecewise(*_process(dtype(0), self._funcs, self._durations))
        return lambdify(t, symbolic, 'math'), sum(self._durations)
