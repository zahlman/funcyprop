from functools import partial, partialmethod
import operator

from sympy.core.basic import Basic as SympyFunction
from sympy import lambdify, Piecewise, piecewise_fold, symbols, sympify
t = symbols('t')
del symbols


# FIXME use this in other places
def valid_clock(number):
    return sympify(number).is_comparable


def _segment(f, d, position, last):
    try:
        pf = f.subs(t, t-position)
    except AttributeError: # not a sympy thing, so a constant.
        pf = sympify(f)
    end = d + position
    return pf, ((t <= end) if last else (t < end))


def _process(funcs, durations):
    position = 0
    for f, d in zip(funcs[:-1], durations[:-1]):
        yield _segment(f, d, position, False)
        position += d
    yield _segment(funcs[-1], durations[-1], position, True)


def coerce(thing, duration=None):
    if isinstance(thing, Function):
        return thing
    if isinstance(thing, tuple):
        return Segments(*thing)
    if duration is None:
        raise TypeError(f"can't coerce {thing} to Function without a duration")
    func = sympify(thing)
    if not isinstance(func, SympyFunction):
        raise TypeError(f"can't coerce {thing} to Function")
    return Function(func, duration)


def Segments(*args):
    # TODO: think more about handling for clock types and result types.
    if not args:
        return Function(sympify(0), 0)
    funcs, durations = args[::2], args[1::2]
    if len(funcs) != len(durations):
        raise ValueError("funcs and durations don't match up")
    if not all(d >= 0 for d in durations):
        raise ValueError("durations can't be negative")
    return Function(
        Piecewise(*_process(funcs, durations)), sum(durations)
    )


class Function:
    """Wraps a Sympy function `f(t)`, to be evaluated on [0, `duration`].
    The value of `f(duration)` is used for all t > duration.
    Will explicitly fail for t < 0."""
    def __init__(self, func, duration):
        func = sympify(func).simplify() # in case it's a constant
        unbindable = func.free_symbols - {t}
        if unbindable:
            raise ValueError(f'func binds extra symbols: {unbindable}')
        if not valid_clock(duration):
            raise TypeError('duration must be comparable to float')
        if duration < 0:
            raise TypeError('duration cannot be negative')
        self._func = func
        self._duration = duration


    # helper for binary operations.
    def _binop(self, op, other):
        f, d = self._func, self._duration
        try:
            other = coerce(other, d)
        except TypeError:
            return NotImplemented
        return Function(op(f, other._func), min(d, other._duration))


    def __eq__(self, other):
        return all((
            self._func.equals(other._func),
            self._duration == other._duration
        ))


    def __str__(self):
        return f'Function({self._func}, {self._duration})'
    __repr__ = __str__


    def __or__(self, other):
        if isinstance(other, tuple):
            other = Segments(*other)
        if not isinstance(other, Function):
            return NotImplemented # could be a Joiner...
        d = self.duration
        end = d + other.duration
        return Function(
            piecewise_fold(Piecewise(
                (self._func, t < d), (other._func.subs(t, t-d), t <= end)
            )),
            self.duration + other.duration
        )


    def __ror__(self, other):
        if isinstance(other, tuple):
            return Segments(*other) | self
        return NotImplemented


    def __matmul__(self, amount): # change rate inversely
        d = self.duration
        t_sub = ((t - d) if amount < 0 else t) * amount
        return Function(self._func.subs(t, t_sub), abs(d / amount))


    def __rmatmul__(self, func): # compose the function
        return Function(func(self._func), self.duration)


    @property
    def duration(self):
        return self._duration


    def reverse(self):
        return self @ -1


    def at(self, position):
        return self._func.subs(t, position)


    @property
    def formula(self):
        d = self.duration
        # Enforce domain
        func = piecewise_fold(Piecewise(
            (self._func.subs(t, d), t >= d),
            (self._func, (t >= 0))
        )).simplify()
        return lambdify(t, self._func, 'math')


for name in ('add', 'sub', 'mul', 'truediv', 'floordiv'):
    op = getattr(operator, name)
    setattr(Function, f'__{name}__', partialmethod(Function._binop, op))
    op = partial((lambda op, lhs, rhs: op(rhs, lhs)), op)
    setattr(Function, f'__r{name}__', partialmethod(Function._binop, op))
