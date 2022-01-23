from math import pi, sin, cos
from time import sleep, time
from timeit import timeit
import tkinter as tk
from .. import add_properties, apply, gather, Call, Linear, Segments, ShiftRight, t


# setup and main loop
class Circle:
    # a drawable object bound to a canvas.
    def __init__(self, canvas, radius):
        self._oval = canvas.create_oval(0, 0, 0, 0, state='hidden', fill='red')
        self._canvas = canvas
        self._radius = radius
        self._visible = False


    @property
    def visible(self):
        return self._visible


    @visible.setter
    def visible(self, value):
        value = bool(value)
        self._visible = value
        self._canvas.itemconfigure(
            self._oval, state=('normal' if value else 'hidden')
        )


    def draw(self, x, y):
        r = self._radius
        self._canvas.coords(self._oval, x-r, y-r, x+r, y+r)


class Window(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.geometry('500x500')
        self.resizable(width=False, height=False)
        canvas = tk.Canvas(self)
        canvas.pack(fill="both", expand=True)
        self._ball = Circle(canvas, 10)
        self._fps = 0
        self._target = time()
        self._controller = controller


    def start(self):
        self._ball.visible = True
        self.after(100, self.frame)


    def frame(self):
        now = time()
        self._fps += 1
        if now > self._target + 1:
            print('FPS:', self._fps, end='\r')
            self._fps = 0
            self._target += 1
        self._ball.draw(*self._controller.xy)
        self.after_idle(self.frame)


# controller
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


# main program
controller = Controller()
cost = timeit(lambda: controller.xy, number=100000)
print(f'Quick timeit test: {cost*10}us per coords property access')
with my_clock.sync():
    cost = timeit(lambda: controller.xy, number=100000)
    print(f'while synced: {cost*10}us per coords property access')
root = Window(controller)
root.start()
tk.mainloop()
