import cv2
import queue
import numpy as np
import math
from .floodFillActual import flood_fill
from scipy.spatial import ConvexHull
from scipy.ndimage.interpolation import rotate

THRESHOLD = 25

def RGB_distance_threshold(first_rgb, second_rgb):
    return math.sqrt(np.sum((np.absolute(first_rgb - second_rgb))**2)) < THRESHOLD

def check_pixels_in_one_direction(image, target_color, cur_x, cur_y, iterations, isNegative, checkY=True):
    for i in range(iterations):
        if isNegative:
            i = -i
        if checkY:
            if RGB_distance_threshold(image[cur_y + i][cur_x], target_color):
                return True
        else:
            if RGB_distance_threshold(image[cur_y][cur_x + i], target_color):
                return True
    return False

def flood_fill_edge_finder(image, x_loc, y_loc, target_color, replacement_color):
    width = len(image[0])
    height = len(image)
    current_x = x_loc
    current_y = y_loc

    total_edge_list = []
    left_edge_list = []
    right_edge_list = []

    while current_y > 0:
        if not check_pixels_in_one_direction(image, target_color, current_x, current_y, 3, True):
            break
        current_y -= 1
        while current_x > 0 and check_pixels_in_one_direction(image, target_color, current_x, current_y, 3, True, True):
            current_x -= 1
        image[current_y][current_x] = replacement_color
        left_edge_list.append((current_x, current_y))
        current_x = x_loc
        while current_x < width - 1 and check_pixels_in_one_direction(image, target_color, current_x, current_y, 3, False, True):
            current_x += 1
        image[current_y][current_x] = replacement_color
        right_edge_list.append((current_x, current_y))
        current_x = x_loc

    # -----------------------------------------
    # intermediate
    # -----------------------------------------
    current_y = y_loc
    current_x = x_loc
    
    right_edge_list = right_edge_list[::-1]
    total_edge_list = left_edge_list + right_edge_list
    left_edge_list = []
    right_edge_list = []

    # -----------------------------------------
    # start of second while
    # -----------------------------------------

    while current_y < height - 1:
        if not check_pixels_in_one_direction(image, target_color, current_x, current_y, 3, False):
            break
        current_y += 1
        while current_x > 0 and check_pixels_in_one_direction(image, target_color, current_x, current_y, 3, True, True):
            current_x -= 1
        image[current_y][current_x] = replacement_color
        left_edge_list.append((current_x, current_y))
        current_x = x_loc
        while current_x < width - 1 and check_pixels_in_one_direction(image, target_color, current_x, current_y, 3, False, True):
            current_x += 1
        image[current_y][current_x] = replacement_color
        right_edge_list.append((current_x, current_y))
        current_x = x_loc
    left_edge_list = left_edge_list[::-1]
    total_edge_list += right_edge_list + left_edge_list

    return total_edge_list, image

def line_from_points(point1, point2):
    # format: Ay + Bx + C = 0
    slope = (point2[1] - point1[1]) / (point2[0] - point1[0])
    A = point2[0] - point1[0]
    B = -(point2[1] - point1[1])
    C = -(point2[0] - point1[0])(-point1[1] - (point1[1] - slope*point1[0]) + point1[0])

    return A, B, C

print(line_from_points((1,2), (0,3)))

def perpendicularDistance(point, line):
    slope = line[0]
    point_on_line = line[1]



def DouglasPecker(points, error):
    dmax = 0
    index = 0
    end = len(points) - 1
    for i in range(1, end + 1):
        d = perpendicularDistance(points[i], line_from_points(points[0], points[end]))
        if d > dmax:
            index = i
            dmax = d

def run_all(image, click_x, click_y, threshold_passed=None):
    global THRESHOLD
    if threshold_passed != None:
        THRESHOLD = threshold_passed
        print('new threshold: ', THRESHOLD)

    target_color = np.array(image[click_y][click_x].tolist())
    replace_color = np.array([0, 255, 0])

    cv2.imwrite('preImage.PNG', image)
    image, _, _, _, _ = flood_fill(image, click_x, click_y, target_color, replace_color)
    cv2.imwrite('floodFill.PNG', image)
    total_edge_list, image = flood_fill_edge_finder(image, click_x, click_y, replace_color, np.array([0, 0, 0]))
    total_edge_list = np.array(total_edge_list)
    total_edge_list = total_edge_list.reshape(len(total_edge_list), 2)

    best_points = minimum_bounding_rectangle(total_edge_list)

    return best_points


