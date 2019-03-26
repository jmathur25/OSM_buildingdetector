import numpy as np
import queue
import math
import time

class FloodFill:
    RGB_GREEN = np.array([0, 255, 0])
    RGB_BLACK = np.array([0, 0, 0])
    CROP_PIXEL_MARGIN = 20
    TIME_MAX = 3

    def __init__(self, image, x_click, y_click, threshold):
        self.image = image
        self.x_click = x_click
        self.y_click = y_click
        # self.THRESHOLD = threshold
        self.THRESHOLD = 25

        self.width = len(image[0])
        self.height = len(image)
        self.target_color = np.array(image[self.y_click, self.x_click].tolist())
        self.replacement_color = np.array(FloodFill.RGB_GREEN.tolist())

        # created during flood_fill
        # x_max is not supposed to be 0, but by starting it at 0 it can be adjusted during the run of floodFill
        # see how these vars are updated for that to make sense
        self.x_max, self.y_max, self.x_min, self.y_min = 0, 0, self.width - 1, self.height - 1

    def flood_fill(self):
        message = None
        # if you click on a green pixel, just return
        if np.array_equal(self.image[self.y_click, self.x_click], self.replacement_color):
            message = 'green'
            print('clicked a green pixel!')
            return self.image, message

        self.image[self.y_click, self.x_click] = self.replacement_color
        pixel_queue = queue.Queue()
        pixel_queue.put((self.x_click, self.y_click))
        start_time = time.time()
        while not pixel_queue.empty():
            # makes sure flood fill doesn't run too long
            if (time.time() - start_time > FloodFill.TIME_MAX):
                message = 'timeout'
                print('flood fill took too long')
                break

            current_x, current_y = pixel_queue.get()
            if current_x > 0:
                left_rgb = self.image[current_y][current_x - 1]
                if FloodFill.RGB_distance(left_rgb, self.target_color) < self.THRESHOLD and not np.array_equal(self.image[current_y][current_x - 1], self.replacement_color):
                    self.image[current_y][current_x - 1] = self.replacement_color
                    pixel_queue.put((current_x - 1, current_y))
                    if (self.x_min > current_x - 1):
                        self.x_min = current_x - 1

            if current_x < self.width - 1:
                right_rgb = self.image[current_y][current_x + 1]
                if FloodFill.RGB_distance(right_rgb, self.target_color) < self.THRESHOLD and not np.array_equal(self.image[current_y][current_x + 1], self.replacement_color):
                    self.image[current_y][current_x + 1] = self.replacement_color
                    pixel_queue.put((current_x + 1, current_y))
                    if (self.x_max < current_x + 1):
                        self.x_max = current_x + 1

            if current_y < self.height - 1:
                up_rgb = self.image[current_y + 1][current_x]
                if FloodFill.RGB_distance(up_rgb, self.target_color) < self.THRESHOLD and not np.array_equal(self.image[current_y + 1][current_x], self.replacement_color):
                    self.image[current_y + 1][current_x] = self.replacement_color
                    pixel_queue.put((current_x, current_y + 1))
                    if (self.y_max < current_y + 1):
                        self.y_max = current_y + 1

            if current_y > 0:
                down_rgb = self.image[current_y - 1][current_x]
                if FloodFill.RGB_distance(down_rgb, self.target_color) < self.THRESHOLD and not np.array_equal(self.image[current_y - 1][current_x], self.replacement_color):
                    self.image[current_y - 1][current_x] = self.replacement_color
                    pixel_queue.put((current_x, current_y - 1))
                    if (self.y_min > current_y - 1):
                        self.y_min = current_y - 1

        # return self.image, message
        return image, message

    def green_fill(self):
        distance = 10
        for x in range(self.x_min, self.x_max):
            for y in range(self.y_min, self.y_max):
                rgb = self.image[y][x]
                xNext = x + distance if x + distance < self.width else self.width - 1
                xPrev = x - distance if x - distance > 0 else 0
                compareRightRgb = self.image[y][xNext]
                compareLeftRgb = self.image[y][xPrev]

                if np.array_equal(compareLeftRgb, FloodFill.RGB_GREEN) and np.array_equal(compareRightRgb, FloodFill.RGB_GREEN) \
                        and not np.array_equal(rgb, FloodFill.RGB_GREEN):
                    self.image[y][x] = FloodFill.RGB_GREEN

        for ny in range(self.y_min, self.y_max):
            for nx in range(self.x_min, self.x_max):

                rgb = self.image[ny][nx]
                yNext = ny + distance if ny + distance < self.height else self.height - 1
                yPrev = ny - distance if ny - distance > 0 else 0
                compareRightRgb = self.image[yNext][nx]
                compareLeftRgb = self.image[yPrev][nx]

                if np.array_equal(compareLeftRgb, FloodFill.RGB_GREEN) and np.array_equal(compareRightRgb, FloodFill.RGB_GREEN) \
                    and not np.array_equal(rgb, FloodFill.RGB_GREEN):
                    self.image[ny][nx] = FloodFill.RGB_GREEN

        return self.image

    def crop_image(self):
        save_xmax = self.x_max + FloodFill.CROP_PIXEL_MARGIN
        save_xmin = self.x_min - FloodFill.CROP_PIXEL_MARGIN
        save_ymax = self.y_max + FloodFill.CROP_PIXEL_MARGIN
        save_ymin = self.y_min - FloodFill.CROP_PIXEL_MARGIN
        if save_xmax > self.width - 1:
            save_xmax = self.width - 1
        if save_xmin < 0:
            save_xmin = 0
        if save_ymax > self.height- 1:
            save_ymax = self.height - 1
        if save_ymin < 0:
            save_ymin = 0

        return self.image[save_ymin:save_ymax, save_xmin:save_xmax]

    def __check_pixels_in_one_direction(self, target_color, cur_x, cur_y, iterations, isNegative, checkY=True):
        for i in range(iterations):
            if isNegative:
                i = -i
            if checkY:
                if FloodFill.RGB_distance(self.image[cur_y + i][cur_x], target_color) < self.THRESHOLD:
                    return True
            else:
                if FloodFill.RGB_distance(self.image[cur_y][cur_x + i], target_color) < self.THRESHOLD:
                    return True
        return False

    def find_edges(self):
        # now that floodfill has been run, we need to look at all pixels that have been converted
        target_color = FloodFill.RGB_GREEN
        replace_color = FloodFill.RGB_BLACK

        current_x = self.x_click
        current_y = self.y_click
        total_edge_list = []
        left_edge_list = []
        right_edge_list = []

        while current_y > 0:
            if not self.__check_pixels_in_one_direction(target_color, current_x, current_y, 3, True):
                break
            current_y -= 1
            while current_x > 0 and self.__check_pixels_in_one_direction(target_color, current_x, current_y, 3, True, True):
                current_x -= 1
            # moves left
            self.image[current_y][current_x] = replace_color
            left_edge_list.append((current_x, current_y))
            current_x = self.x_click
            # moves right
            while current_x < self.width - 1 and self.__check_pixels_in_one_direction(target_color, current_x, current_y, 3, False, True):
                current_x += 1
            self.image[current_y][current_x] = replace_color
            right_edge_list.append((current_x, current_y))
            current_x = self.x_click

        # -----------------------------------------
        # intermediate
        # -----------------------------------------
        current_y = self.y_click
        current_x = self.x_click
        
        right_edge_list = right_edge_list[::-1]
        total_edge_list = left_edge_list + right_edge_list
        left_edge_list = []
        right_edge_list = []

        # -----------------------------------------
        # start of second while
        # -----------------------------------------

        while current_y < self.height - 1:
            if not self.__check_pixels_in_one_direction(target_color, current_x, current_y, 3, False):
                break
            current_y += 1
            # moves left
            while current_x > 0 and self.__check_pixels_in_one_direction(target_color, current_x, current_y, 3, True, True):
                current_x -= 1
            self.image[current_y][current_x] = replace_color
            left_edge_list.append((current_x, current_y))
            current_x = self.x_click
            # moves right
            while current_x < self.width - 1 and self.__check_pixels_in_one_direction(target_color, current_x, current_y, 3, False, True):
                current_x += 1
            self.image[current_y][current_x] = replace_color
            right_edge_list.append((current_x, current_y))
            current_x = self.x_click

        left_edge_list = left_edge_list[::-1]
        total_edge_list += right_edge_list + left_edge_list

        return self.image, total_edge_list

    @staticmethod
    def RGB_distance(first_rgb, second_rgb):
        return math.sqrt(np.sum((np.absolute(first_rgb - second_rgb))**2))

import cv2
image = cv2.imread('./test_images/pre_image.PNG')
flood = FloodFill(image, 472, 340, 25)
result, message = flood.flood_fill()
print('done running flood fill')
cv2.imshow('result', result)
cv2.waitKey(0)
cv2.destroyAllWindows()
