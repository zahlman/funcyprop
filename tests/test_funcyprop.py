# standard library
from itertools import count # a stable integer clock
# installed packages
import pytest
from sympy import Piecewise
# this package
from funcyprop import __version__, PiecewiseBuilderT, Source, t


def intclock():
    counter = iter(count())
    return lambda: next(counter)


def test_version():
    assert __version__ == '0.1.0'


def test_builder_loop():
    b = PiecewiseBuilderT()
    assert b.loop is None
    b.loop = 3
    assert isinstance(b.loop, float) and b.loop == 3.0


def test_builder_add():
    b = PiecewiseBuilderT()
    b.add(t**2, 10)
    b.add((10-t)**2, 10)
    assert b.built == Piecewise((t**2, t<10), ((20-t)**2, t<20), (0.0, True))


def test_source_loop():
    s = Source(intclock(), int, int)
    assert s.loop is None
    s.loop = 3.0
    assert isinstance(s.loop, int) and s.loop == 3


def test_source_values():
    s = Source(intclock(), int, int)
    s.add(t**2, 10)
    s.add((10-t)**2, 10)
    assert s.formula == Piecewise((t**2, t<10), ((20-t)**2, t<20), (0.0, True))
    samples = [s.value for _ in range(25)]
    # Setting the 'now' - also at initialization - necessarily consumes
    # a value from the iterator. This is unavoidable; the iterator doesn't
    # know why it's being consumed, and the Source doesn't know the "time"
    # value comes from an iterator. TODO: Document this gotcha.
    # Better yet: directly support specifying the clock as an iterator.
    # Maybe give clocks a parameter for that info?
    assert samples == [
        1, 4, 9, 16, 25,
        36, 49, 64, 81, 100,
        81, 64, 49, 36, 25,
        16, 9, 4, 1, 0,
        0, 0, 0, 0, 0
    ]


@pytest.mark.xfail
def test_source_loop_values():
    s = Source(intclock(), int, int)
    s.add(t, 3)
    s.loop = 0
    samples = [s.value for _ in range(10)]
    assert samples == [0, 1, 2, 0, 1, 2, 0, 1, 2, 0]
