"""
Written by james on 2/23/2019

Feature: Fills out whitespace between green pixels
"""

import cv2
import numpy as np
from matplotlib import pyplot as plt

FILENAME = 'slanted_1detected'
image = cv2.imread(FILENAME + '.PNG')



height = image.shape[0]
width = image.shape[1]

RGB_GREEN = np.array([0, 255, 0])
distance = 20
def change_color(image):
    for x in range(width):
        for y in range(height):

            rgb = image[y][x]
            yNext = y + distance if y + distance < height else height - 1
            xNext = x + distance if x + distance < width else width - 1
            xPrev = x - distance if x - distance > 0 else 0
            compareDownRgb = image[yNext][x]
            compareRightRgb = image[y][xNext]
            compareLeftRgb = image[y][xPrev]

            if (np.array_equal(rgb, RGB_GREEN) and np.array_equal(compareDownRgb, RGB_GREEN)
                    and np.array_equal(compareLeftRgb, RGB_GREEN) and np.array_equal(compareRightRgb, RGB_GREEN)):
                for yTemp in range(y, yNext):
                    rgbTemp = image[yTemp][x]
                    if not np.array_equal(rgbTemp, RGB_GREEN):
                        image[yTemp][x] = RGB_GREEN

    return image


full = change_color(image)
#
# full[np.where((full == [0,255,0]).all(axis = 2))] = [0,0,0]
# full[np.where((full != [0,255,0]).all(axis = 2))] = [255,255,255]
cv2.imwrite(FILENAME + 'fullGreen.PNG', full)
