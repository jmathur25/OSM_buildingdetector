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
            #yNext = y + distance if y + distance < height else height - 1
            xNext = x + distance if x + distance < width else width - 1
            xPrev = x - distance if x - distance > 0 else 0
            #compareDownRgb = image[yNext][x]
            compareRightRgb = image[y][xNext]
            compareLeftRgb = image[y][xPrev]

            if np.array_equal(compareLeftRgb, RGB_GREEN) and np.array_equal(compareRightRgb, RGB_GREEN) \
                    and not np.array_equal(rgb, RGB_GREEN):
                image[y][x] = RGB_GREEN
                # for xTemp in range(xPrev, xNext):
                #     rgbTemp = image[y][xTemp]
                #     if not np.array_equal(rgbTemp, RGB_GREEN) and x_min < xTemp < x_max:
                #         image[y][xTemp] = RGB_GREEN

    for y in range(y_min, y_max):
        for x in range(x_min, x_max):

            rgb = image[y][x]
            # yNext = y + distance if y + distance < height else height - 1
            yNext = y + distance if y + distance < height else height - 1
            yPrev = y - distance if y - distance > 0 else 0
            #compareDownRgb = image[yNext][x]
            compareRightRgb = image[yNext][x]
            compareLeftRgb = image[yPrev][x]

            if np.array_equal(compareLeftRgb, RGB_GREEN) and np.array_equal(compareRightRgb, RGB_GREEN) \
                and not np.array_equal(rgb, RGB_GREEN):
                image[y][x] = RGB_GREEN
                # for yTemp in range(yPrev, yNext):
                #     rgbTemp = image[yTemp][x]
                #     if not np.array_equal(rgbTemp, RGB_GREEN) and y_min < yTemp < y_max:
                #         image[yTemp][x] = RGB_GREEN

    return image


full = change_color(image)
#
# # full[np.where((full == [0,255,0]).all(axis = 2))] = [0,0,0]
full[np.where((full != [0,255,0]).all(axis = 2))] = [255,255,255]
# # cv2.imwrite(FILENAME + 'fullGreen.PNG', full)

# plt.subplot(121),plt.imshow(image)
# plt.title('Original Image'), plt.xticks([]), plt.yticks([])
# plt.subplot(122),plt.imshow(full)
# plt.title('Full Image'), plt.xticks([]), plt.yticks([])
# plt.show()
kernel = np.ones((20, 20), np.float32) / 25
img = cv2.filter2D(full, -1, kernel)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

corners = cv2.goodFeaturesToTrack(gray,12,0.1,10)
corners = np.int0(corners)
print(corners)
for i in corners:
    x,y = i.ravel()
    cv2.circle(img,(x,y),3,255,-1)

plt.imshow(img),plt.show()
# cv2.imwrite(FILENAME + "edited.png", img)
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