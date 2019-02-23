import cv2
import queue
import numpy as np
import math

THRESHOLD = 25

def RGB_distance_threshold(first_rgb, second_rgb):
    return math.sqrt(np.sum((np.absolute(first_rgb - second_rgb))**2))

def flood_fill(image, x_loc, y_loc, target_color, replacement_color):
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

        if current_x < width - 1:
            right_rgb = image[current_y][current_x + 1]
            if RGB_distance_threshold(right_rgb, target_color) < THRESHOLD and not np.array_equal(image[current_y][current_x + 1], replacement_color):
                image[current_y][current_x + 1] = replacement_color
                pixel_queue.put((current_x + 1, current_y))

        if current_y < height - 1:
            up_rgb = image[current_y + 1][current_x]
            if RGB_distance_threshold(up_rgb, target_color) < THRESHOLD and not np.array_equal(image[current_y + 1][current_x], replacement_color):
                image[current_y + 1][current_x] = replacement_color
                pixel_queue.put((current_x, current_y + 1))

        if current_y > 0:
            down_rgb = image[current_y - 1][current_x]
            if RGB_distance_threshold(down_rgb, target_color) < THRESHOLD and not np.array_equal(image[current_y - 1][current_x], replacement_color):
                image[current_y - 1][current_x] = replacement_color
                pixel_queue.put((current_x, current_y - 1))
    return image


x_global = 0
y_global = 0
def register_click(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global x_global, y_global
        x_global = int(x)
        y_global = int(y)

image = cv2.imread('slanted_1.PNG')
cv2.namedWindow('image')
cv2.setMouseCallback('image', register_click)
cv2.imshow('image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(x_global, y_global)

# image indexing returns something weird so this fixed it
target_color = np.array(image[y_global][x_global].tolist())
# green color
replace_color = np.array([0, 255, 0])

image = flood_fill(image, x_global, y_global, target_color, replace_color)
cv2.imshow('image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

