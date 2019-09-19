import cv2
import queue
import numpy as np
import math
from .GreenFill import run_all2

# default threshold, frontend can change this
THRESHOLD = 25

def RGB_distance_threshold(first_rgb, second_rgb):
    return math.sqrt(np.sum((np.absolute(first_rgb - second_rgb))**2))

def flood_fill(image, x_loc, y_loc, target_color, replacement_color):
    width = len(image[0])
    height = len(image)
    x_max = 0
    y_max = 0
    x_min = width - 1
    y_min = height - 1

    image[y_loc, x_loc] = replacement_color
    pixel_queue = queue.Queue()
    pixel_queue.put((x_loc, y_loc))
    width = len(image[0])
    height = len(image)
    while not pixel_queue.empty():
        current_x, current_y = pixel_queue.get()

        if current_x > 0:
            left_rgb = image[current_y][current_x - 1]
            if RGB_distance_threshold(left_rgb, target_color) < THRESHOLD and not np.array_equal(image[current_y][current_x - 1], replacement_color):
                image[current_y][current_x - 1] = replacement_color
                pixel_queue.put((current_x - 1, current_y))
                if (x_min > current_x - 1):
                    x_min = current_x - 1

        if current_x < width - 1:
            right_rgb = image[current_y][current_x + 1]
            if RGB_distance_threshold(right_rgb, target_color) < THRESHOLD and not np.array_equal(image[current_y][current_x + 1], replacement_color):
                image[current_y][current_x + 1] = replacement_color
                pixel_queue.put((current_x + 1, current_y))
                if (x_max < current_x + 1):
                    x_max = current_x + 1

        if current_y < height - 1:
            up_rgb = image[current_y + 1][current_x]
            if RGB_distance_threshold(up_rgb, target_color) < THRESHOLD and not np.array_equal(image[current_y + 1][current_x], replacement_color):
                image[current_y + 1][current_x] = replacement_color
                pixel_queue.put((current_x, current_y + 1))
                if (y_max < current_y + 1):
                    y_max = current_y + 1

        if current_y > 0:
            down_rgb = image[current_y - 1][current_x]
            if RGB_distance_threshold(down_rgb, target_color) < THRESHOLD and not np.array_equal(image[current_y - 1][current_x], replacement_color):
                image[current_y - 1][current_x] = replacement_color
                pixel_queue.put((current_x, current_y - 1))
                if (y_min > current_y - 1):
                    y_min = current_y - 1

    return image, x_max, y_max, x_min, y_min


def run_all(image, click_x, click_y, threshold_passed=None):
    global THRESHOLD
    if threshold_passed != None:
        THRESHOLD = threshold_passed

    # used for smoothing out image.
    kernel = np.ones((5, 5), np.float32) / 25

    target_color = np.array(image[click_y][click_x].tolist())
    replace_color = np.array([0, 255, 0])

    image, x_max, y_max, x_min, y_min = flood_fill(image, click_x, click_y, target_color, replace_color)

    points = run_all2(image, x_min, y_min, x_max, y_max)
    return points
