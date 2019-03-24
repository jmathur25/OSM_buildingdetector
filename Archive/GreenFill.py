import cv2
import numpy as np
import operator
from functools import reduce
import math


RGB_GREEN = np.array([0, 255, 0])
distance = 10

def run_all2(image, x_min, y_min, x_max, y_max):
    height = image.shape[0]
    width = image.shape[1]
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
    full[np.where((full != [0,255,0]).all(axis = 2))] = [255,255,255]

    # kernel = np.ones((20, 20), np.float32) / 25
    # img = cv2.filter2D(full, -1, kernel)
    img = cv2.blur(full, (4, 4))
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    corners = cv2.goodFeaturesToTrack(gray,12,0.1,10)

    temp = []
    for corner in corners:
        temp.append((corner[0][0], corner[0][1]))

    center = tuple(map(operator.truediv, reduce(lambda x, y: map(operator.add, x, y), temp), [len(temp)] * 2))
    tcoord = (sorted(temp, key=lambda coord: (-135 - math.degrees(math.atan2(*tuple(map(operator.sub, coord, center))[::-1]))) % 360))

    coord = []
    for c in tcoord:
        coord.append((int(c[0]), int(c[1])))

    return coord
