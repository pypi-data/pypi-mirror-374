import tkinter as tk
from tkinter import colorchooser
import turtle as t
import random as r
def ri (a, b):
    r.randint(a, b)
def key (a, b):
    t.onekeypress(a, str(b))
def click(a):
    t.onscreenclick(a)
def getcolor(tit):
    colorchooser.askcolor(title = tit)
def rc (a):
    r.choice(a)

