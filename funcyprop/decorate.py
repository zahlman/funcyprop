from functools import partial
from . import Source, t


def propgetter(name, self):
    return getattr(self, name).value


def my_new(old_new, to_add, *args, **kwargs):
    result = old_new(*args, **kwargs)
    for name, clock, clocktype, resulttype in to_add:
        if isinstance(clock, str):
            clock = (result, clock)
        setattr(result, '_' + name, Source(clock, clocktype, resulttype))
    return result


def decorate(to_add, cls):
    cls.__new__ = partial(my_new, cls.__new__, to_add)
    for name, clock, clocktype, resulttype in to_add:
        setattr(cls, name, property(fget=partial(propgetter, '_' + name)))
    return cls


def add_properties(clock, clocktype=float, /, **names):
    to_add = [ 
        (name, clock, clocktype, resulttype)
        for name, resulttype in names.items()
    ]
    return partial(decorate, to_add)
