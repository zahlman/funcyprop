# `Funcyprop` - powerful algebraic tools for time-varying properties

*So you're making a game...* and you want to control the positioning of some decorative element. It's not using the physics engine, but it needs to follow a fairly complex path to make an interesting animation. You'd like to have an object from which you can get the `x` and `y` positions at any given time...

... but wouldn't it be nicer if it knew about the time, so you could get the values with simple property syntax? What if you could describe the movement piece-wise, using symbolic representation of the functions to evaluate, and simple smooth joining of the pieces - all without tearing your hair out over the math? What if it were easy to loop the animation, change the speed on demand, or transition into new animations with a nice cubic spline? What if it were a one-liner to synthesize new properties from existing ones?

With `funcyprop`, your code can look like:

```python
def polar_to_rectangular(rt):
    r, theta = rt
    return r * cos(theta) + 250, r * sin(theta) + 250


my_clock = Call()
@add_properties(my_clock, r=float, theta=float)
class Controller:
    def __init__(self):
        outward = (10*t**2, pi) | ShiftRight | (-10*(pi-t)**2, pi)
        self._r.segments = (outward | Linear(2*pi) | outward @ -1) @ 0.5 
        self._theta.segments = (t, 2*pi)
        self._r.loop = 0
        self._theta.loop = 0
Controller.xy = apply(
    polar_to_rectangular, gather(my_clock, Controller, 'r', 'theta')
)
```

But what does it do?

## See for Yourself

The above code is included in a simple Tkinter-based demo, which uses it to control the path of a moving circle in a static window. To see it in action, just run `python -m funcyprop.demo`.

## How it Works

`Call` creates a wrapper for a callable function that can return a time value, defaulting to `time.time`. It ensures the value seen in the property calculation is monotonically increasing; it handles looping; and it be sped up or slowed down via a `rate` property. It also offers a context manager interface, so that you can use the same time value for multiple properties. `gather` is a utility that synthesizes a property as a tuple of other properties, using synchronized clock access.

The `add_properties` decorator hacks the class to add the specified properties (with results from the underlying functions cast to the specified type), and hacks `__new__` to add controller objects to each new instance - as corresponding `_`-named attributes. Because it uses `__new__`, you have access in `__init__` and can make the properties available immediately.

The controller holds a representation of the function that calculates the property value - a piecewise function in one variable, `t`. This is a symbol provided by `Sympy`, which you can use to create arbitrary Sympy functions. The `Formula` wrapper class represents a sequence of those "segments"; and you can concatenate them with `|`, and use "joiners" for fancier transitions. Tuples of alternating (function, duration) pairs are automatically coerced into `Formula` instances, where possible. When a `Formula` is assigned to the `segments` property, it is automatically converted into a plain function via `sympy.lambdify`. Manipulating the formulas is slow, but the resulting function performs quite well.

When the `xy` property is requested, a `with my_clock.sync():` block is entered, the `x` and `y` properties are accessed respectively, and a tuple is returned. For the individual property accesses, the corresponding function is evaluated at an appropriate `t` value, depending on the `loop` setting, the amount of elapsed time, and the history of the `rate` value over that time. (The clock's value can also be explicitly set.)

This is just a taste - properly documenting this project will take a while...