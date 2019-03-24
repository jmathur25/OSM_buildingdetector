import cv2
import queue
import numpy as np
import math
from matplotlib import pyplot as plt

def run_all3(click_x, click_y, thresh):
    THRESHOLD = 25

    # should read "preImage.PNG" if the first click or else ERROR!! Later fix
    FILENAME = 'classifiers/backendImages/floodFill.PNG'
    image = cv2.imread(FILENAME)

    # used for smoothing out image.
    kernel = np.ones((5, 5), np.float32) / 25

    def RGB_distance_threshold(first_rgb, second_rgb):
        return math.sqrt(np.sum((np.absolute(first_rgb - second_rgb))**2))

    def flood_fill(image, x_loc, y_loc, target_color, replacement_color):
        image[y_loc, x_loc] = replacement_color
        pixel_queue = queue.Queue()
        pixel_queue.put((x_loc, y_loc))

        width = len(image[0])
        height = len(image)
        # keeps them reverse to start with, so that they can be assigned during flood_fill
        x_max = 0
        y_max = 0
        x_min = width - 1
        y_min = height - 1

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
        return image, x_min, x_max, y_min, y_max

    target_color = np.array(image[click_y][click_x].tolist())
    replace_color = np.array([0, 255, 0])
    # updates current image object
    image, x_min, x_max, y_min, y_max = flood_fill(image, click_x, click_y, target_color, replace_color)
    print('width:', len(image[0]), 'height:', len(image))
    print(x_min, x_max, y_min, y_max)

    # crops the images for good viewing
    save_xmax = x_max + 20
    save_xmin = x_min - 20
    save_ymax = y_max + 20
    save_ymin = y_min - 20
    if save_xmax > len(image[0]) - 1:
        save_xmax = len(image[0]) - 1
    if save_xmin < 0:
        save_xmin = 0
    if save_ymax > len(image) - 1:
        save_ymax = len(image) - 1
    if save_ymin < 0:
        save_ymin = 0

    # to show the current state in the context of the original image
    cv2.imwrite('classifiers/backendImages/floodFill.PNG', image)
    # for displaying on the frontend
    image_crop = image[save_ymin:save_ymax, save_xmin:save_xmax]
    cv2.imwrite('classifiers/backendImages/floodFill_Display.PNG', image_crop)

    # Green Fill part from James
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
    
    cv2.imwrite("test.png", img2)

    return coord

