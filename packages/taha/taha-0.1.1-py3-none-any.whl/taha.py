import tkinter as tk
import requests
from tkinter import colorchooser
import turtle as t
import random as ra
from datetime import datetime
import time
now = datetime.now()
hour = now.hour
minute = now.minute
second = now.second
microsecond = now.microsecond
def ri (a, b):
    return ra.randint(a, b)
def key (a, b):
    t.listen()
    t.onkeypress(a, str(b))
def click(a):
    t.onscreenclick(a)
def getcolor(tit):
    return colorchooser.askcolor(title = tit)
def rc (a):
    return ra.choice(a)

def leftclick (a):
    t.onscreenclick(a, btn = 1)
def middleclick (a):
    t.onscreenclick(a, btn = 2)
def rightclick (a):
    t.onscreenclick(a, btn = 3)
def move (x, y):
    t.goto(x, y)
def randcolor():
    t.colormode(255)
    r = ra.randint(1, 255)
    g = ra.randint(1, 255)
    b = ra.randint(1, 255)
    t.color ((r, g, b))
def rgbcolor(r, g, b):
    t.colormode(255)
    t.color ((r, g, b))
def getping(url):
    start = time.time()
    requests.get(url)
    end = time.time()
    return round((end - start)* 1000)
