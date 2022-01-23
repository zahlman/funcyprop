from functools import partial, partialmethod
import operator
from .source import Source, t
from .clock import Clock


class Funcyprop(property):
    def _overload(self, op, other):
        if isinstance(other, Funcyprop):
            return Funcyprop(lambda obj: op(self.fget(obj), other.fget(obj)))
        return Funcyprop(lambda obj: op(self.fget(obj), other))


for name in ('add', 'mul', 'sub'):
    method = partialmethod(Funcyprop._overload, getattr(operator, name))
    setattr(Funcyprop, f'__{name}__', method)


def apply(func, subprop):
    fget = subprop.fget # avoid looking it up each time
    return Funcyprop(lambda obj: func(fget(obj)))


def gather(clock, cls, *names):
    funcs = [getattr(cls, name).fget for name in names]
    def access(obj):
        with clock.sync():
            return tuple(func(obj) for func in funcs)
    return Funcyprop(access)


def make_funcyprop(name):
    return Funcyprop(lambda obj: getattr(obj, name).value)


def my_new(cls, old_new, to_add, clock, *args, **kwargs):
    obj_new = object.__new__
    obj = obj_new(cls) if old_new is obj_new else old_new(cls, *args, **kwargs)
    if not isinstance(clock, Clock): # delayed construction
        maker, name = clock
        clock = maker() # created separate clock per instance
        if not isinstance(clock, Clock):
            raise TypeError('invalid clock')
        setattr(obj, name, clock)
    for name, resulttype in to_add:
        setattr(obj, '_' + name, Source(clock, resulttype))
    return obj


def decorate(to_add, clock, cls):
    # clock is either a Clock instance or a function that returns one
    cls.__new__ = partialmethod(my_new, cls.__new__, to_add, clock)
    for name, resulttype in to_add:
        setattr(cls, name, make_funcyprop('_' + name))
    return cls


def add_properties(clock, /, **names):
    to_add = [
        (name, resulttype)
        for name, resulttype in names.items()
    ]
    return partial(decorate, to_add, clock)
