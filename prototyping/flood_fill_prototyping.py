import cv2
import queue
import numpy as np
import math
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

def flood_fill_edge_finder(image, x_loc, y_loc, target_color, replacement_color):
    width = len(image[0])
    height = len(image)
    current_x = x_loc
    current_y = y_loc

    total_edge_list = []
    left_edge_list = []
    right_edge_list = []

    while current_y > 0:
        if not check_pixels_in_one_direction(image, target_color, current_x, current_y, 5, True):
            break
        current_y -= 5
        while current_x > 0 and check_pixels_in_one_direction(image, target_color, current_x, current_y, 5, True, True):
            current_x -= 1
        image[current_y][current_x] = replacement_color
        left_edge_list.append((current_x, current_y))
        current_x = x_loc
        while current_x < width - 1 and check_pixels_in_one_direction(image, target_color, current_x, current_y, 5, False, True):
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
        if not check_pixels_in_one_direction(image, target_color, current_x, current_y, 5, False):
            break
        current_y += 5
        while current_x > 0 and check_pixels_in_one_direction(image, target_color, current_x, current_y, 5, True, True):
            current_x -= 1
        image[current_y][current_x] = replacement_color
        left_edge_list.append((current_x, current_y))
        current_x = x_loc
        while current_x < width - 1 and check_pixels_in_one_direction(image, target_color, current_x, current_y, 5, False, True):
            current_x += 1
        image[current_y][current_x] = replacement_color
        right_edge_list.append((current_x, current_y))
        current_x = x_loc
    left_edge_list = left_edge_list[::-1]
    total_edge_list += right_edge_list + left_edge_list

    return total_edge_list, image


x_global = 0
y_global = 0
def register_click(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global x_global, y_global
        x_global = int(x)
        y_global = int(y)

image_name = "../cs225.png"

image = cv2.imread(image_name)
cv2.namedWindow('image')
cv2.setMouseCallback('image', register_click)
cv2.imshow('image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
print(x_global, y_global)
target_color = np.array(image[y_global][x_global].tolist())
replace_color = np.array([0, 255, 0])

flood_fill_image = flood_fill(image, x_global, y_global, target_color, replace_color)
cv2.namedWindow('image')
cv2.setMouseCallback('image', register_click)
cv2.imshow('image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

total_edge_list, dotted_image = flood_fill_edge_finder(flood_fill_image, x_global, y_global, replace_color, np.array([0, 0, 0]))
cv2.imshow('image', dotted_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

def minimum_bounding_rectangle(points):
    """
    Find the smallest bounding rectangle for a set of points.
    Returns a set of points representing the corners of the bounding box.

    :param points: an nx2 matrix of coordinates
    :rval: an nx2 matrix of coordinates
    """
    pi2 = np.pi/2.

    # get the convex hull for the points
    hull_points = points[ConvexHull(points).vertices]

    # calculate edge angles
    edges = np.zeros((len(hull_points)-1, 2))
    edges = hull_points[1:] - hull_points[:-1]

    angles = np.zeros((len(edges)))
    angles = np.arctan2(edges[:, 1], edges[:, 0])

    angles = np.abs(np.mod(angles, pi2))
    angles = np.unique(angles)

    # find rotation matrices
    # XXX both work
    rotations = np.vstack([
        np.cos(angles),
        np.cos(angles-pi2),
        np.cos(angles+pi2),
        np.cos(angles)]).T
#     rotations = np.vstack([
#         np.cos(angles),
#         -np.sin(angles),
#         np.sin(angles),
#         np.cos(angles)]).T
    rotations = rotations.reshape((-1, 2, 2))

    # apply rotations to the hull
    rot_points = np.dot(rotations, hull_points.T)

    # find the bounding points
    min_x = np.nanmin(rot_points[:, 0], axis=1)
    max_x = np.nanmax(rot_points[:, 0], axis=1)
    min_y = np.nanmin(rot_points[:, 1], axis=1)
    max_y = np.nanmax(rot_points[:, 1], axis=1)

    # find the box with the best area
    areas = (max_x - min_x) * (max_y - min_y)
    best_idx = np.argmin(areas)

    # return the best box
    x1 = max_x[best_idx]
    x2 = min_x[best_idx]
    y1 = max_y[best_idx]
    y2 = min_y[best_idx]
    r = rotations[best_idx]

    rval = np.zeros((4, 2))
    rval[0] = np.dot([x1, y2], r)
    rval[1] = np.dot([x2, y2], r)
    rval[2] = np.dot([x2, y1], r)
    rval[3] = np.dot([x1, y1], r)

    return rval

total_edge_list = np.array(total_edge_list)
total_edge_list = total_edge_list.reshape(len(total_edge_list), 2)

best_points = minimum_bounding_rectangle(total_edge_list)

def plot_vertices(image, corners, color):
    for corner in corners:
        corner = (int(corner[0]), int(corner[1]))
        for i in range(-5, 5):
            image[corner[1] + i][corner[0]] = color
        for i in range(-5, 5):
            image[corner[1]][corner[0] + i] = color
    return image

image = cv2.imread(image_name)
image = plot_vertices(image, best_points, replace_color)
cv2.imshow('image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
