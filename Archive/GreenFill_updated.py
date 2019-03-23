"""
Written by james on 2/23/2019
Feature: Fills out whitespace between green pixels
"""
from floodFillPrototype import x_min, x_max, y_min, y_max, FILENAME
import cv2
import numpy as np
from matplotlib import pyplot as plt

image = cv2.imread(FILENAME + 'detected' + '.PNG')

height = image.shape[0]
width = image.shape[1]

RGB_GREEN = np.array([0, 255, 0])
distance = 10
def change_color(image):
    for x in range(x_min, x_max):
        for y in range(y_min, y_max):
            rgb = image[y][x]
            xNext = x + distance if x + distance < width else width - 1
            xPrev = x - distance if x - distance > 0 else 0
            compareRightRgb = image[y][xNext]
            compareLeftRgb = image[y][xPrev]

            if np.array_equal(compareLeftRgb, RGB_GREEN) and np.array_equal(compareRightRgb, RGB_GREEN) \
                    and not np.array_equal(rgb, RGB_GREEN):
                image[y][x] = RGB_GREEN

    for ny in range(y_min, y_max):
        for nx in range(x_min, x_max):

            rgb = image[ny][nx]
            yNext = ny + distance if ny + distance < height else height - 1
            yPrev = ny - distance if ny - distance > 0 else 0
            compareRightRgb = image[yNext][nx]
            compareLeftRgb = image[yPrev][nx]

            if np.array_equal(compareLeftRgb, RGB_GREEN) and np.array_equal(compareRightRgb, RGB_GREEN) \
                and not np.array_equal(rgb, RGB_GREEN):
                image[ny][nx] = RGB_GREEN

    return image

full = change_color(image)
full[np.where((full != [0, 255, 0]).all(axis = 2))] = [255, 255, 255]

img2 = cv2.blur(full, (4, 4))
gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)

corners = cv2.goodFeaturesToTrack(gray,12,0.1,10)
corners = np.int0(corners)
coord = []
for corner in corners:
    coord.append((corner[0][0], corner[0][1]))

print(coord)
for i in corners:
    x,y = i.ravel()
    cv2.circle(img2,(x,y),3,255,-1)

plt.imshow(img2), plt.show()