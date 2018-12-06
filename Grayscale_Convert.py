'''
Written by james on 11/4/2018

Feature: Converts image to grayscale
'''

import cv2

filename = 'some_houses'
img = cv2.imread(filename + '.PNG', 0)
cv2.imwrite(filename + '_gray.PNG', img)