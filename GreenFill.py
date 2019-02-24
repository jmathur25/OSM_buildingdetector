"""
Written by james on 2/23/2019

Feature: Fills out whitespace between green pixels
"""

import cv2
import numpy as np
from matplotlib import pyplot as plt

FILENAME = 'diff_huedetected'
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

            if ((np.array_equal(rgb, RGB_GREEN) and np.array_equal(compareDownRgb, RGB_GREEN))
                    and (np.array_equal(compareLeftRgb, RGB_GREEN) and np.array_equal(compareRightRgb, RGB_GREEN))):
                for yTemp in range(y, yNext):
                    rgbTemp = image[yTemp][x]
                    if not np.array_equal(rgbTemp, RGB_GREEN):
                        image[yTemp][x] = RGB_GREEN

    return image


full = change_color(image)

# full[np.where((full == [0,255,0]).all(axis = 2))] = [0,0,0]
full[np.where((full != [0,255,0]).all(axis = 2))] = [255,255,255]
# cv2.imwrite(FILENAME + 'fullGreen.PNG', full)


kernel = np.ones((7, 7), np.float32) / 25
img = cv2.filter2D(full, -1, kernel)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

corners = cv2.goodFeaturesToTrack(gray,4,0.01,10)
corners = np.int0(corners)

for i in corners:
    x,y = i.ravel()
    cv2.circle(img,(x,y),3,255,-1)

plt.imshow(img),plt.show()

#################Harris Corner Detector############################################

# kernel = np.ones((5, 5), np.float32) / 25
#
# img = cv2.filter2D(full, -1, kernel)
# gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#
# gray = np.float32(gray)
# dst = cv2.cornerHarris(gray,2,7,0.04)
#
# #result is dilated for marking the corners, not important
# dst = cv2.dilate(dst,None)
#
# # Threshold for an optimal value, it may vary depending on the image.
# img[dst>0.01*dst.max()]=[0,0,255]
#
# cv2.imshow('dst',img)
# if cv2.waitKey(0) & 0xff == 27:
#     cv2.destroyAllWindows()