import cv2
import numpy as np
import geolocation
import math

class SimpleDetect:
    def __init__(self, image, lat, long, zoom, threshold):
        self.image = image
        self.lat = lat
        self.long = long
        self.zoom = zoom
        self.threshold = threshold
    
    # slides the threshold depending on the current intensity
    def _threshold_slider(self, cur_intensity):
        fit = math.ceil(0.25*cur_intensity - 10)
        if fit < 0:
            fit = 10
        return fit

    # Get the next major intensity change in a given direction.
    def _get_next_intensity_change(self, grayscale_image, x, y, xstep, ystep):

        lookahead = 5
        width = grayscale_image.shape[1]
        height = grayscale_image.shape[0]

        while (x >= 0 and x < width and y >= 0 and y < height):
            if (x + xstep < 0 or x + xstep >= width or y + ystep < 0 or y + ystep >= height):
                break
            
            x += xstep
            y += ystep

            # keeps the x coordinates and y coordinates bounded by 0 and width / height respectively
            downx = max(min(int(x + xstep * lookahead), width - 1), 0)
            downy = max(min(int(y + ystep * lookahead), height - 1), 0)
            
            cur_intensity = int(grayscale_image[int(y), int(x)])
            next_intensity = int(grayscale_image[downy, downx])
            threshold = self._threshold_slider(cur_intensity)
            
            if (abs(cur_intensity - next_intensity) > threshold):
                for i in range(lookahead, -1, -1):
                    downx = max(min(int(x + xstep * i), width - 1), 0)
                    downy = max(min(int(y + ystep * i), height - 1), 0)
                    
                    next_intensity = int(grayscale_image[downy, downx])
                    if (abs(cur_intensity - next_intensity) > threshold):
                        return (downx, downy)
                return (downx, downy)
        
        return (x, y)

    def detect_building(self):
        grayscale_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        # Get the x,y coordinates of the click
        x, y = geolocation.deg_to_tilexy(self.lat, self.long, self.zoom)
        # find xtile, ytile
        xtile, ytile = geolocation.deg_to_tile(self.lat, self.long, self.zoom)

        quad_one = self._get_next_intensity_change(grayscale_image, x, y, 1, 0)
        quad_four = self._get_next_intensity_change(grayscale_image, x, y, 0, -1)
        quad_two = self._get_next_intensity_change(grayscale_image, x, y, 0, 1)
        quad_three = self._get_next_intensity_change(grayscale_image, x, y, -1, 0)

        corner1 = quad_one[0], quad_two[1]
        corner2 = quad_one[0], quad_four[1]
        corner3 = quad_three[0], quad_four[1]
        corner4 = quad_three[0], quad_two[1]

        # Calculate the geocoordinates of the rectangle
        top_right = geolocation.tilexy_to_deg(xtile, ytile, self.zoom, corner1[0], corner1[1])
        bottom_right = geolocation.tilexy_to_deg(xtile, ytile, self.zoom, corner2[0], corner2[1])
        bottom_left = geolocation.tilexy_to_deg(xtile, ytile, self.zoom, corner3[0], corner3[1])
        top_left = geolocation.tilexy_to_deg(xtile, ytile, self.zoom, corner4[0], corner4[1])

        top_left = list(top_left)
        top_right = list(top_right)
        bottom_right = list(bottom_right)
        bottom_left = list(bottom_left)

        # gets the current rect id, the current rect points, and any rectangles that may have been deleted
        return [top_left, top_right, bottom_right, bottom_left]
