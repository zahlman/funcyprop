from functools import partial
from .segments import coerce, t


class Joiner:
    """Context-sensitive segment that can smoothly join other sequences."""
    def __init__(self, func):
        self._func = func


    def __ror__(self, lhs):
        return BoundJoiner(self._func, coerce(lhs))


class BoundJoiner:
    def __init__(self, func, lhs):
        self._func, self._lhs = func, lhs


    def __or__(self, rhs):
        return self._func(self._lhs, coerce(rhs))


def JoinerMaker(func):
    def wrapper(data):
        return Joiner(partial(func, data))
    return wrapper


@Joiner
def ShiftRight(lhs, rhs):
    """Add a constant offset to the rhs so it's continuous with the lhs."""
    return lhs | (rhs + lhs.at(lhs.duration) - rhs.at(0))


@Joiner
def ShiftLeft(lhs, rhs):
    """Add a constant offset to the lhs so it's continuous with the rhs."""
    return (lhs + rhs.at(0) - lhs.at(lhs.duration)) | rhs


@JoinerMaker
def Linear(duration, lhs, rhs):
    """Add a linear segment between the two."""
    l, r = lhs.at(lhs.duration), rhs.at(0)
    s = l + (r - l) * (t / duration)
    return lhs | (s, duration) | rhs
