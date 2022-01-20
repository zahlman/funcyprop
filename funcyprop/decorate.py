from functools import partial
from .source import Source, t
from .clock import make_clock


def propgetter(name, self):
    return getattr(self, name).value


def my_new(old_new, to_add, clockdata, clocktype, *args, **kwargs):
    result = old_new(*args, **kwargs)
    # use the same clock for each property, but we can't create it
    # until we're setting up the instance.
    if len(clockdata) == 1 and isinstance(clockdata[0], str):
        clockdata = (result, clockdata)
    clock = make_clock(*clockdata, dtype=clocktype)
    for name, resulttype in to_add:
        setattr(result, '_' + name, Source(clock, clocktype, resulttype))
    return result


def decorate(to_add, clock, clocktype, cls):
    cls.__new__ = partial(my_new, cls.__new__, to_add, clock, clocktype)
    for name, resulttype in to_add:
        setattr(cls, name, property(fget=partial(propgetter, '_' + name)))
    return cls


def add_properties(clocktype, /, *clockdata, **names):
    to_add = [
        (name, resulttype)
        for name, resulttype in names.items()
    ]
    return partial(decorate, to_add, clockdata, clocktype)
