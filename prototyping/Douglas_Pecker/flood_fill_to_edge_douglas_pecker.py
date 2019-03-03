import cv2
import queue
import numpy as np
import math

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

def green_fill(image, x_max, y_max, x_min, y_min):
    width = len(image[0])
    height = len(image)
    RGB_GREEN = np.array([0, 255, 0])
    distance = 10
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

    total_edge_list = []
    while not pixel_queue.empty():
        current_x, current_y = pixel_queue.get()
        if current_x > 0:
            left_rgb = image[current_y][current_x - 1]
            if RGB_distance_threshold(left_rgb, target_color) and not np.array_equal(image[current_y][current_x - 1], replacement_color):
                image[current_y][current_x - 1] = replacement_color
                pixel_queue.put((current_x - 1, current_y))
                if (x_min > current_x - 1):
                    x_min = current_x - 1
            else:
                total_edge_list.append((current_x, current_y))

        if current_x < width - 1:
            right_rgb = image[current_y][current_x + 1]
            if RGB_distance_threshold(right_rgb, target_color) and not np.array_equal(image[current_y][current_x + 1], replacement_color):
                image[current_y][current_x + 1] = replacement_color
                pixel_queue.put((current_x + 1, current_y))
                if (x_max < current_x + 1):
                    x_max = current_x + 1
            else:
                total_edge_list.append((current_x, current_y))

        if current_y < height - 1:
            up_rgb = image[current_y + 1][current_x]
            if RGB_distance_threshold(up_rgb, target_color) and not np.array_equal(image[current_y + 1][current_x], replacement_color):
                image[current_y + 1][current_x] = replacement_color
                pixel_queue.put((current_x, current_y + 1))
                if (y_max < current_y + 1):
                    y_max = current_y + 1
            else:
                total_edge_list.append((current_x, current_y))

        if current_y > 0:
            down_rgb = image[current_y - 1][current_x]
            if RGB_distance_threshold(down_rgb, target_color) and not np.array_equal(image[current_y - 1][current_x], replacement_color):
                image[current_y - 1][current_x] = replacement_color
                pixel_queue.put((current_x, current_y - 1))
                if (y_min > current_y - 1):
                    y_min = current_y - 1
            else:
                total_edge_list.append((current_x, current_y))

    return image, x_max, y_max, x_min, y_min, total_edge_list

def flood_fill_edge_finder(image, x_max, y_max, x_min, y_min, target_color, replacement_color):
    width = len(image[0])
    height = len(image)
    current_x = x_max
    current_y = y_max

    total_edge_list = []
    right_edge_list = []
    left_edge_list = []

    while current_y > y_min:
        # if not check_pixels_in_one_direction(image, target_color, current_x, current_y, 3, True):
        #     break
        current_y -= 1
        while not np.array_equal(image[current_y][current_x], target_color):
            current_x -= 1
        image[current_y][current_x] = replacement_color
        right_edge_list.append((current_x, current_y))
        while current_x > x_min and check_pixels_in_one_direction(image, target_color, current_x, current_y, 3, True, True):
            current_x -= 1
        image[current_y][current_x] = replacement_color
        left_edge_list.append((current_x, current_y))
        current_x = x_max
    
    total_edge_list = right_edge_list + left_edge_list[::-1]

    return total_edge_list, image

def line_from_points(point1, point2):
    # format: Ay + Bx + C = 0
    if point2[0] == point1[0]:
        return (None, point1)
    slope = (point2[1] - point1[1]) / (point2[0] - point1[0])
    A = point2[0] - point1[0]
    B = -(point2[1] - point1[1])
    C = -(point2[0] - point1[0])*(point1[1]-slope*point1[0])

    if (A < 0):
        A = -A
        B = -B
        C = -C

    return A, B, C

def perpendicular_distance(point, line):
    # if perpendicular, then just take x distance
    if len(line) == 2:
        return abs(point[0]-line[1][0])
    # uses point-line theorem where a line in format Ay + Bx + C = 0 and point (x1, y1) has distance abs(A*y1 + B*x1 + C) / sqrt(A**2 + B**2)
    A = line[0]
    B = line[1]
    C = line[2]
    d = abs(A*point[1] + B*point[0] + C) / math.sqrt(A**2 + B**2)
    return d

# see https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm
def DouglasPecker(points, epsilon):
    dmax = 0
    index = 0
    end = len(points) - 1
    line = line_from_points(points[0], points[end])
    for i in range(1, end):
        d = perpendicular_distance(points[i], line)
        if d > dmax:
            index = i
            dmax = d
    result = []
    # If max distance is greater than epsilon, recursively simplify
    if ( dmax > epsilon ):
        recResults1 = DouglasPecker(points[:index+1], epsilon)
        recResults2 = DouglasPecker(points[index:], epsilon)
        # Build the result list, and makes sure [1,2,3]+[3,4,5] =[1,2,3,4,5]
        if (recResults1[-1] == recResults2[0]):
            recResults1.pop()
        result = recResults1 + recResults2
    else:
        result = [points[0], points[end]]
    return result

# tests, expect something along the lines of [(0, 0), (3, 3), (6, 3), (0, 0)]; the last point will be (1,0)
# points = [(0, 0), (1, 1), (2, 2), (3, 3), (4,3), (5,3), (6,3), (5,2), (4,1), (3, 0), (2, 0), (1, 0)]
# print(DouglasPecker(points, 1))
# print(perpendicular_distance((3, 3), line_from_points((0, 0), (6, 3))))

def plot_vertices(image, corners, color):
    for corner in corners:
        corner = (int(corner[0]), int(corner[1]))
        for i in range(-5, 5):
            image[corner[1] + i][corner[0]] = color
        for i in range(-5, 5):
            image[corner[1]][corner[0] + i] = color
    return image

def run_all(image, click_x, click_y, threshold_passed=None):
    global THRESHOLD
    if threshold_passed != None:
        THRESHOLD = threshold_passed
        print('new threshold: ', THRESHOLD)

    target_color = np.array(image[click_y][click_x].tolist())
    replace_color = np.array([0, 255, 0])

    cv2.imwrite('preImage.PNG', image)
    flood_image, x_max, y_max, x_min, y_min, total_edge_list = flood_fill(image, click_x, click_y, target_color, replace_color)
    cv2.imwrite('floodFill.PNG', flood_image)
    # green_fill_image = green_fill(image, x_max, y_max, x_min, y_min)
    # cv2.imwrite('greenFill.PNG', green_fill_image)
    # total_edge_list, edge_image = flood_fill_edge_finder(green_fill_image, x_max, y_max, x_min, y_min, replace_color, np.array([0, 0, 0]))

    image_name = "../test_building.PNG"
    image = cv2.imread(image_name)
    edge_image = plot_vertices(image, total_edge_list, replace_color)
    cv2.imshow('image', edge_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # total_edge_list = np.array(total_edge_list)
    # total_edge_list = total_edge_list.reshape(len(total_edge_list), 2)
    print("edge length: ", len(total_edge_list))
    best_points = DouglasPecker(total_edge_list, 10)
    print("new edge length: ", len(best_points))
    return best_points

x_global = 0
y_global = 0
def register_click(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global x_global, y_global
        x_global = int(x)
        y_global = int(y)

image_name = "../test_building.PNG"

image = cv2.imread(image_name)
cv2.namedWindow('image')
cv2.setMouseCallback('image', register_click)
cv2.imshow('image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(x_global, y_global)
target_color = np.array(image[y_global][x_global].tolist())
replace_color = np.array([0, 255, 0])

best_points = run_all(image, x_global, y_global)
# print(" ")
# print(best_points)
image = cv2.imread(image_name)
image = plot_vertices(image, best_points, replace_color)
cv2.imshow('image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
