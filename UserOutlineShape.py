'''
Written by james on 11/3/2018
Feature: Grabs the outline of a shape a user identifies.

NOTE: image must be in grayscale
'''

import cv2
import time


filename = 'some_houses_gray.png'
image = cv2.imread(filename)
height = image.shape[0]
width = image.shape[1]

def getOutline(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # colorsB = image[y, x, 0]
        # colorsG = image[y, x, 1]
        # colorsR = image[y, x, 2]
        # colors = image[y, x]
        # print("Red: ", colorsR)
        # print("Green: ", colorsG)
        # print("Blue: ", colorsB)
        # print("Coordinates of pixel: X: ", x, "Y: ", y)

        x_position = x
        y_position = y
        threshold = 50
        timeout = time.time() + 5  # 5 seconds to timeout
        '''
        Left method
        '''
        while x_position != 1:
            x_position -= 1
            if time.time() > timeout:
                break

            # Setting the value of the compare image
            if x_position < 10:
                LEFTx_compare = 0
            else:
                LEFTx_compare = x_position - 10

            # Getting intensities
            current_intensity = int(image[y, x_position, 0])  # the current intensity of pixel
            compare_intensity = int(image[y, LEFTx_compare, 0])  # intensity of pixel you want to compare


            if abs(current_intensity - compare_intensity) > threshold:
                # cv2.line(image, (LEFTx_compare, 0), (LEFTx_compare, height), (255, 0, 0), 5)
                break

        '''
        UP method
        '''
        while y_position != 1:
            y_position -= 1
            if time.time() > timeout:
                break

            # Setting the value of the compare image
            if y_position < 10:
                UPy_compare = 0
            else:
                UPy_compare = y_position - 10

            # Getting intensities
            current_intensity = int(image[y_position, x, 0])  # the current intensity of pixel
            compare_intensity = int(image[UPy_compare, x, 0])  # intensity of pixel you want to compare


            if abs(current_intensity - compare_intensity) > threshold:
                # cv2.line(image, (0, UPy_compare), (width, UPy_compare), (255, 0, 0), 5)
                break

        '''
        DOWN method
        '''
        while y_position != height:
            y_position += 1
            if time.time() > timeout:
                break

            # Setting the value of the compare image
            if y_position > height - 10:
                DOWNy_compare = height
            else:
                DOWNy_compare = y_position + 10

            # Getting intensities
            current_intensity = int(image[y_position, x, 0])  # the current intensity of pixel
            compare_intensity = int(image[DOWNy_compare, x, 0])  # intensity of pixel you want to compare


            if abs(current_intensity - compare_intensity) > threshold:
                # cv2.line(image, (0, DOWNy_compare), (width, DOWNy_compare), (255, 0, 0), 5)
                break

        '''
        Right method
        '''
        while x_position != width:
            x_position += 1
            if time.time() > timeout:
                break

            # Setting the value of the compare image
            if x_position > width - 10:
                RIGHTx_compare = width
            else:
                RIGHTx_compare = x_position + 10

            # Getting intensities
            current_intensity = int(image[y, x_position, 0])  # the current intensity of pixel
            compare_intensity = int(image[y, RIGHTx_compare, 0])  # intensity of pixel you want to compare


            if abs(current_intensity - compare_intensity) > threshold:
                # cv2.line(image, (RIGHTx_compare, 0), (RIGHTx_compare, height), (255, 0, 0), 5)
                break

        # DRAWING LINES
        cv2.line(image, (RIGHTx_compare, UPy_compare), (RIGHTx_compare, DOWNy_compare), (255, 0, 0), 5)
        cv2.line(image, (LEFTx_compare, UPy_compare), (LEFTx_compare, DOWNy_compare), (255, 0, 0), 5)
        cv2.line(image, (LEFTx_compare, UPy_compare), (RIGHTx_compare, UPy_compare), (255, 0, 0), 5)
        cv2.line(image, (LEFTx_compare, DOWNy_compare), (RIGHTx_compare, DOWNy_compare), (255, 0, 0), 5)




# bind the function to window
cv2.namedWindow('mouseRGB')
cv2.setMouseCallback('mouseRGB', getOutline)

# Do until esc pressed
while (1):
    cv2.imshow('mouseRGB', image)
    if cv2.waitKey(20) & 0xFF == 27:
        break
# if esc pressed, finish.
cv2.destroyAllWindows()