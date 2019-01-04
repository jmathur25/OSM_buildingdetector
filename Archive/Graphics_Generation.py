'''
Written by james on 11/3/2018
Feature: Grabs the outline of a shape a user identifies.
Note: need graphics
'''

from graphics import *
from random import randint
import cv2 as cv

def draw_rect(win, x, y, h, w):
    rect = Rectangle(Point(x, y), Point(x + h, y + w))
    rect.setFill("black")
    rect.draw(win)

def close(win, x, y):
    new = []
    but = Rectangle(Point(x,y), Point(x + 50,y + 20))
    but.setFill("red")
    new.append(but)
    word = Text(Point(x + 25,y + 10),"Done")
    new.append(word)
    return new

win = GraphWin('Image', 800, 800)

for i in range(10):
    draw_rect(win, randint(0,740), randint(30,800), randint(30,200), randint(30,200))

################Button Creation ###########################################
button = close(win, 750, 0)
for obj in button:
    obj.draw(win)


################Continuously grabs mouse click data########################
mouse = win.getMouse()
while mouse.x < 750 or mouse.y > 20:
    mouse = win.getMouse()



print(mouse.x, mouse.y)


# Closes window
win.close()