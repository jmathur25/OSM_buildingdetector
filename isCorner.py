"""
Written by james on 11/18/2018

Feature: Enter feature name here
"""
import numpy as np
import math
def isCorner(x, y):
    """
    Determines whether point is an edge
    :param x: x coordinate
    :param y: y coordinate
    :return: Boolean on whether point is an edge
    """
    values = []
    for i in range(1, 8, 2):
        radius = 3

        times = np.linspace(0, 6.28, (i + 1) * 4 + 1)

        add_points = set()
        for t in times:
            x_add = round(i * math.sin(t))
            y_add = round(i * math.cos(t))
            add_points.add((x_add, y_add)) # all points with radius 3 around given point

        current_intensity = int(image[y, x, 0])
        intensity = [] # add intensity of center point
        for nx, ny in add_points:
            try:
                intensity.append(int(image[y + ny, x + nx, 0]))  # gets intensities of all points around center
            except:
                intensity.append(0)  # for edges/outside cases
        same = sum(abs(i - current_intensity) < 10 for i in intensity) # same intensities
        frac = same / len(intensity)

        # if around half of points have the same intensity, return false
        if (0.1 < frac < 0.4):
            values.append(True)
        else:
            values.append(False)
    if sum(j is True for j in values) >= 3:
        return True
    else:
        return False