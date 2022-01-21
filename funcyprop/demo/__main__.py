from math import pi
from time import sleep, time 
import tkinter as tk
from sympy import sin, cos
from .. import add_properties, apply_many, Call, t


@add_properties(Call(), x=int, y=int)
class Thing:
    def __new__(cls, canvas):
        return super().__new__(cls)


    def __init__(self, canvas):
        self._oval = canvas.create_oval(0, 0, 0, 0, state='hidden', fill='red')
        self._canvas = canvas
        self._started = False


    def draw(self):
        if not self._started:
            self._started = True
            self._x.add(250 + sin(t) * 200, 2*pi)
            self._y.add(250 + cos(t) * 200, 2*pi)
            self._x.loop = 0
            self._y.loop = 0
            self._canvas.itemconfigure(self._oval, state='normal')
        coords = self.coords
        self._canvas.coords(self._oval, *coords)
Thing.coords = apply_many(tuple, Thing.x-10, Thing.y-10, Thing.x+10, Thing.y+10)

import timeit


root = tk.Tk()
root.geometry('500x500')
root.resizable(width=False, height=False)
canvas = tk.Canvas(root)
canvas.pack(fill="both", expand=True)
thing = Thing(canvas)
cost = timeit.timeit(lambda:thing.coords, number=1000)
print(f'Quick timeit test: {cost}ms per coords property access')


fps = 0
target = time()


def frame():
    global fps, target
    now = time()
    fps += 1
    if now > target + 1:
        print('FPS:', fps, end='\r')
        fps, target = 0, target + 1
    thing.draw()
    root.after_idle(frame)


root.after(100, frame)
tk.mainloop()
