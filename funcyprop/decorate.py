from functools import partial, partialmethod
import operator
from .source import Source, t
from .clock import make_clock


class Funcyprop(property):
    def _overload(self, op, other):
        if isinstance(other, Funcyprop):
            return Funcyprop(lambda obj: op(self.fget(obj), other.fget(obj)))
        return Funcyprop(lambda obj: op(self.fget(obj), other))


for name in ('add', 'mul', 'sub'):
    method = partialmethod(Funcyprop._overload, getattr(operator, name))
    setattr(Funcyprop, f'__{name}__', method)


def apply(func, subprop):
    return Funcyprop(lambda obj: func(subprop.fget(obj)))


def apply_many(func, *subprops):
    return Funcyprop(lambda obj: func(s.fget(obj) for s in subprops))


def make_funcyprop(name):
    return Funcyprop(lambda obj: getattr(obj, name).value)


def my_new(cls, old_new, to_add, clockdata, clocktype, *args, **kwargs):
    obj_new = object.__new__
    obj = obj_new(cls) if old_new is obj_new else old_new(cls, *args, **kwargs)
    # use the same clock for each property, but we can't create it
    # until we're setting up the instance.
    if len(clockdata) == 1 and isinstance(clockdata[0], str):
        clockdata = (obj,) + clockdata
    clock = make_clock(*clockdata, dtype=clocktype)
    for name, resulttype in to_add:
        setattr(obj, '_' + name, Source(clock, clocktype, resulttype))
    return obj


def decorate(to_add, clock, clocktype, cls):
    cls.__new__ = partialmethod(my_new, cls.__new__, to_add, clock, clocktype)
    for name, resulttype in to_add:
        setattr(cls, name, make_funcyprop('_' + name))
    return cls


def add_properties(clocktype, /, *clockdata, **names):
    to_add = [
        (name, resulttype)
        for name, resulttype in names.items()
    ]
    return partial(decorate, to_add, clockdata, clocktype)
