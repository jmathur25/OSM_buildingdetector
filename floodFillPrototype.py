import cv2
import queue
import numpy as np
import math

THRESHOLD = 25

FILENAME = 'slanted_1'

# img = cv2.imread(FILENAME + '.png')
# cv2.imwrite(FILENAME + 'compressed.png', img,  [cv2.IMWRITE_PNG_COMPRESSION, 0])
image = cv2.imread(FILENAME + '.png')
height = image.shape[0]
width = image.shape[1]
# used for smoothing out image.
kernel = np.ones((5, 5), np.float32) / 25

def RGB_distance_threshold(first_rgb, second_rgb):
    return math.sqrt(np.sum((np.absolute(first_rgb - second_rgb))**2))

x_max = 0
y_max = 0
x_min = width - 1
y_min = height - 1

def flood_fill(image, x_loc, y_loc, target_color, replacement_color):
    image[y_loc, x_loc] = replacement_color
    pixel_queue = queue.Queue()
    pixel_queue.put((x_loc, y_loc))
    width = len(image[0])
    height = len(image)
    while not pixel_queue.empty():
        global x_max, y_max, x_min, y_min
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
    return image


x_global = 0
y_global = 0
def register_click(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global x_global, y_global
        x_global = int(x)
        y_global = int(y)
        print(x_global, y_global)

        # image indexing returns something weird so this fixed it
        target_color = np.array(image[y_global][x_global].tolist())
        # green color
        replace_color = np.array([0, 255, 0])

        image2 = flood_fill(image, x_global, y_global, target_color, replace_color)
        # smoothed = cv2.filter2D(image2, -1, kernel)


        cv2.imshow('image2', image2)
        cv2.imwrite(FILENAME + 'detected.PNG', image2)



cv2.namedWindow('image')
cv2.setMouseCallback('image', register_click)
cv2.imshow('image', image)

#print(x_global, y_global)

cv2.waitKey(0)
cv2.destroyAllWindows()

