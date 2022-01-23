from itertools import count
# installed packages
import pytest
from sympy import Piecewise
# this package
from funcyprop import __version__, add_properties, Auto, Manual, Segments, Source, t


def test_version():
    assert __version__ == '0.1.0'


def test_source_loop():
    s = Source(Auto(), int)
    assert s.loop is None
    s.loop = 3.0
    assert isinstance(s.loop, int) and s.loop == 3


def test_source_values():
    s = Source(Auto(), int)
    s.segments = (t**2, 10, (10-t)**2, 10)
    samples = [s.value for _ in range(25)] 
    # When reading from a counter, the first result will be 1 more than
    # the last reset value. TODO is this the best behaviour?
    assert samples == [
        1, 4, 9, 16, 25,
        36, 49, 64, 81, 100,
        81, 64, 49, 36, 25,
        16, 9, 4, 1, 0,
        0, 0, 0, 0, 0
    ]


def test_source_loop_values():
    s = Source(Auto(), int)
    s.segments = (t, 3)
    s.loop = 0
    samples = [s.value for _ in range(10)]
    assert samples == [1, 2, 0, 1, 2, 0, 1, 2, 0, 1]


def test_decorate():
    @add_properties((Manual, 'c'), x=int, y=int)
    class Test:
        def __init__(self):
            self._x.segments = (t**2, 5, (5-t)**2, 5)
            self._y.segments = (5*t, 5, 5*(5-t), 5)
    example = Test()
    samples = []
    for _ in range(12):
        samples.append((example.x, example.y))
        example.c.now += 1
    assert samples == [
        (0, 0), (1, 5), (4, 10), (9, 15), (16, 20), (25, 25),
        (16, 20), (9, 15), (4, 10), (1, 5), (0, 0), (0, 0)
    ]


@pytest.mark.parametrize('dtype', (int, float))
def test_math(dtype): # demonstrate strict interval bounds
    clock = Auto()
    @add_properties(clock, x=int, y=int)
    class Test:
        def __init__(self):
            self._x.segments = (t, 5)
            self._y.segments = (t, 5)
    Test.z = Test.x * Test.y - 1
    example = Test()
    samples = []
    for _ in range(10):
        with clock.sync():
            samples.append(example.z)
    # The result is the same with ints because even though t=5 isn't in the
    # .add()ed interval, the "hold" at the end is calculated with t=5.
    assert samples == [0, 3, 8, 15, 24, 24, 24, 24, 24, 24]


@pytest.mark.xfail
def test_segment_math():
    s = Segments(t, 1)
    s2 = Segments(t**2, 1)
    assert s * s == s2
    assert s - 1 == Segments(t-1, 1)
    assert s + 1 == Segments(t+1, 1)
    assert (s+1) * (s-1) == s2 - 1
    s3 = (s * 5) @ .2
    assert s3 | (s3 @ -1) == Segments(5*t, 5, 5*(5-t), 5)
    s4 = (s2 * 25) @ .2
    assert s4 == Segments(t**2, 5)
