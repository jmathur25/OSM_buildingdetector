import cv2
import queue
import numpy as np
import math

image = cv2.imread('test_building.PNG')
cv2.imshow('image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
# print(image)

THRESHOLD = 30

def RGB_distance_threshold(first_rgb, second_rgb):
    return math.sqrt(np.sum((np.absolute(first_rgb - second_rgb))**2))

def flood_fill(image, x_loc, y_loc, target_color, replacement_color):
    pixel_queue = queue.Queue()
    pixel_queue.put((x_loc, y_loc))
    while not pixel_queue.empty():
        current_x, current_y = pixel_queue.get()
        left_rgb = image[current_x - 1][current_y]
        if RGB_distance_threshold(left_rgb, target_color) < THRESHOLD and not np.array_equal(image[current_x - 1][current_y], replacement_color):
            image[current_x - 1][current_y] = replacement_color
            pixel_queue.put((current_x - 1, current_y))

        right_rgb = image[current_x + 1][current_y]
        if RGB_distance_threshold(right_rgb, target_color) < THRESHOLD and not np.array_equal(image[current_x + 1][current_y], replacement_color):
            image[current_x + 1][current_y] = replacement_color
            pixel_queue.put((current_x + 1, current_y))

        up_rgb = image[current_x][current_y + 1]
        if RGB_distance_threshold(up_rgb, target_color) < THRESHOLD and not np.array_equal(image[current_x][current_y + 1], replacement_color):
            image[current_x][current_y + 1] = replacement_color
            pixel_queue.put((current_x, current_y + 1))

        down_rgb = image[current_x][current_y - 1]
        if RGB_distance_threshold(down_rgb, target_color) < THRESHOLD and not np.array_equal(image[current_x][current_y - 1], replacement_color):
            image[current_x][current_y - 1] = replacement_color
            pixel_queue.put((current_x, current_y - 1))
    return image


# x = np.array([1,2,6])
# y = np.array([2,1,4])
# print(RGB_distance_threshold(x, y))

print(image[100][80])
target_color = np.array([197, 219, 219])
replace_color = np.array([0, 255, 0])
image = flood_fill(image, 100, 80, target_color, replace_color)

cv2.imshow('image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
