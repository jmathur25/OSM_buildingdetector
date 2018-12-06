"""
Written by james on 11/3/2018
Feature: Grabs the outline of a shape a user identifies.

NOTE: image must be in grayscale
"""

import cv2
import time

filename = 'rectangles.png'
image = cv2.imread(filename)
height = image.shape[0]
width = image.shape[1]


def draw_left(x, y, threshold, timeout):
    """
    Draws the line to the left
    :param x: X coordinate of click
    :param y: Y coordinate of click
    :param threshold: pixel gradient threshold
    :param timeout: timeout (sec)
    :return: X coordinate where pixel gradient is hit
    """
    x_position = x
    while x_position != 1:
        x_position -= 1
        if time.time() > timeout:
            break

        # Setting the value of the compare image
        if x_position < 10:
            left_x_compare = 0
        else:
            left_x_compare = x_position - 10

        # Getting intensities
        current_intensity = int(image[y, x_position, 0])  # the current intensity of pixel
        compare_intensity = int(image[y, left_x_compare, 0])  # intensity of pixel you want to compare

        if abs(current_intensity - compare_intensity) > threshold:
            return left_x_compare


def draw_up(x, y, threshold, timeout):
    """
    Draws the line up
    :param x: X coordinate of click
    :param y: Y coordinate of click
    :param threshold: pixel gradient threshold
    :param timeout: timeout (sec)
    :return: Y coordinate where pixel gradient is hit
    """
    y_position = y
    while y_position != 1:
        y_position -= 1
        if time.time() > timeout:
            break

        # Setting the value of the compare image
        if y_position < 10:
            up_y_compare = 0
        else:
            up_y_compare = y_position - 10

        # Getting intensities
        current_intensity = int(image[y_position, x, 0])  # the current intensity of pixel
        compare_intensity = int(image[up_y_compare, x, 0])  # intensity of pixel you want to compare

        if abs(current_intensity - compare_intensity) > threshold:
            return up_y_compare


def draw_down(x, y, threshold, timeout):
    """
    Draws the line down.
    :param x: X coordinate of click
    :param y: Y coordinate of click
    :param threshold: pixel gradient threshold
    :param timeout: timeout (sec)
    :return: Y coordinate where pixel gradient is hit
    """
    y_position = y
    while y_position != height:
        y_position += 1
        if time.time() > timeout:
            break

        # Setting the value of the compare image
        if y_position > height - 10:
            down_y_compare = height
        else:
            down_y_compare = y_position + 10

        # Getting intensities
        current_intensity = int(image[y_position, x, 0])  # the current intensity of pixel
        compare_intensity = int(image[down_y_compare, x, 0])  # intensity of pixel you want to compare

        if abs(current_intensity - compare_intensity) > threshold:
            return down_y_compare


def draw_right(x, y, threshold, timeout):
    """
    Draws the line to the right
    :param x: X coordinate of click
    :param y: Y coordinate of click
    :param threshold: pixel gradient threshold
    :param timeout: timeout (sec)
    :return: X coordinate where pixel gradient is hit
    """
    x_position = x
    while x_position != width:
        x_position += 1
        if time.time() > timeout:
            break

        # Setting the value of the compare image
        if x_position > width - 10:
            right_x_compare = width
        else:
            right_x_compare = x_position + 10

        # Getting intensities
        current_intensity = int(image[y, x_position, 0])  # the current intensity of pixel
        compare_intensity = int(image[y, right_x_compare, 0])  # intensity of pixel you want to compare

        if abs(current_intensity - compare_intensity) > threshold:
            return right_x_compare


# GETS USER CLICKS
def getMouse(event, x, y, flags, param):

    if event == cv2.EVENT_LBUTTONDOWN:
        threshold = 50
        timeout = time.time() + 5  # 5 seconds to timeout
        top = draw_up(x, y, threshold, timeout)
        bot = draw_down(x, y, threshold, timeout)
        right = draw_right(x, y, threshold, timeout)
        left = draw_left(x, y, threshold, timeout)

        # DRAWING LINES
        cv2.line(image, (right, top), (left, top), (255, 0, 0), 5)
        cv2.line(image, (left, top), (left, bot), (255, 0, 0), 5)
        cv2.line(image, (left, bot), (right, bot), (255, 0, 0), 5)
        cv2.line(image, (right, bot), (right, top), (255, 0, 0), 5)


# bind the function to window
cv2.namedWindow('DrawOutline')
cv2.setMouseCallback('DrawOutline', getMouse)

# Do until esc pressed
while 1:
    cv2.imshow('DrawOutline', image)
    if cv2.waitKey(20) & 0xFF == 27:
        break
# if esc pressed, finish.
cv2.destroyAllWindows()
