"""
Written by james on 2/23/2019
Feature: Fills out whitespace between green pixels
"""
from floodFillPrototype import x_min, x_max, y_min, y_max, FILENAME
import cv2
import numpy as np
import math
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

# def add_padding(image, dist):
#     count = 0
#     new_image = image.copy()
#     new_x_max = x_max + dist if x_max + dist < width else width - 1
#     new_x_min = x_min - dist if x_min - dist > 0 else 0
#     new_y_max = y_max + dist if y_max + dist < height else height - 1
#     new_y_min = y_min - dist if y_min - dist > 0 else 0
#     for x in range(new_x_min, new_x_max):
#         for y in range(new_y_min, new_y_max):
#             if not np.array_equal(new_image[y][x], RGB_GREEN) and is_good(image, x, y, dist):
#                 new_image[y][x] = RGB_GREEN
#                 count += 1
#     print(count)
#     return new_image
#
#
# def is_good(image, x, y, dist):
#     right_x = x + dist if x + dist < width else width - 1
#     left_x = x - dist if x - dist > 0 else 0
#     top_y = y + dist if y + dist < height else height - 1
#     bot_y = y - dist if y - dist > 0 else 0
#
#     # bottom edge check
#     for nx in range(left_x, right_x):
#         if np.array_equal(image[bot_y][nx], RGB_GREEN):
#             return True
#
#     # top edge check
#     for nx in range(left_x, right_x):
#         if np.array_equal(image[top_y][nx], RGB_GREEN):
#             return True
#
#     # left edge check
#     for ny in range(top_y + 1, bot_y - 1):
#         if np.array_equal(image[ny][left_x], RGB_GREEN):
#             return True
#
#     # right edge check
#     for ny in range(top_y + 1, bot_y - 1):
#         if np.array_equal(image[ny][right_x], RGB_GREEN):
#             return True
#
#     return False
#
# def is_within_distance(x1, y1, x2, y2, dist):
#     return dist >= math.sqrt((x2-x1)**2 + (y2-y1)**2)



full = change_color(image)
full[np.where((full != [0, 255, 0]).all(axis = 2))] = [255, 255, 255]



# kernel = np.ones((20, 20), np.float32) / 25
# img = cv2.filter2D(full, -1, kernel)
#
# pad_dist = 10
# img2 = add_padding(img, pad_dist)
img2 = cv2.blur(full, (5, 5))
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