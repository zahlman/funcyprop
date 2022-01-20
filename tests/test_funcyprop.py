# standard library
from itertools import count # a stable integer clock
# installed packages
import pytest
from sympy import Piecewise
# this package
from funcyprop import __version__, add_properties, make_clock, Source, t


def test_version():
    assert __version__ == '0.1.0'


def test_source_loop():
    s = Source(make_clock(count()), int, int)
    assert s.loop is None
    s.loop = 3.0
    assert isinstance(s.loop, int) and s.loop == 3


def test_source_values():
    s = Source(make_clock(count()), int, int)
    s.add(t**2, 10)
    s.add((10-t)**2, 10)
    assert s.formula == Piecewise((t**2, t<10), ((20-t)**2, t<20), (0.0, True))
    samples = [s.value for _ in range(25)]
    assert samples == [
        0, 1, 4, 9, 16,
        25, 36, 49, 64, 81,
        100, 81, 64, 49, 36,
        25, 16, 9, 4, 1,
        0, 0, 0, 0, 0
    ]


def test_source_loop_values():
    s = Source(make_clock(count()), int, int)
    s.add(t, 3)
    s.loop = 0
    samples = [s.value for _ in range(10)]
    assert samples == [0, 1, 2, 0, 1, 2, 0, 1, 2, 0]


def test_decorate():
    @add_properties(int, count(), x=int, y=int)
    class Test:
        def __init__(self):
            self._x.add(t**2, 10)
            self._x.add((10-t)**2, 10)
            self._y.add(10*t, 10)
            self._y.add(10*(10-t), 10)
    example = Test()
    samples = [example.x for x in range(25)]
    assert samples == [
        0, 1, 4, 9, 16,
        25, 36, 49, 64, 81,
        100, 81, 64, 49, 36,
        25, 16, 9, 4, 1,
        0, 0, 0, 0, 0
    ]
    example._y.reset(-1) # read 0 next time
    samples = [example.y for y in range(25)]
    assert samples == [
        0, 10, 20, 30, 40,
        50, 60, 70, 80, 90,
        100, 90, 80, 70, 60,
        50, 40, 30, 20, 10,
        0, 0, 0, 0, 0
    ]


@pytest.mark.parametrize('dtype', (int, float))
def test_math(dtype): # demonstrate strict interval bounds
    @add_properties(dtype, 'time', x=int, y=int)
    class Test:
        def __init__(self):
            self.time = 0
            self._x.add(t, 5)
            self._y.add(t, 5)
    Test.z = Test.x * Test.y - 1
    example = Test()
    samples = []
    for _ in range(10):
        samples.append(example.z)
        example.time += 1
    # The result is the same with ints because even though t=5 isn't in the
    # .add()ed interval, the "hold" at the end is calculated with t=5.
    assert samples == [-1, 0, 3, 8, 15, 24, 24, 24, 24, 24]
