import cv2
import numpy as np
import geolocation
import backend
import math
import PIL.ImageOps
from .FloodFill_To_Edges_Actual import run_all

# all rectangles are parallel to the xy axis
class Rectangle:
    current_id = 0

    # do rectangles try to merge with neighboring rectangles?
    merge_mode = False

    # list of all rectangles in existence
    all_rectangles = []

    # recently changed rectangles that need to be recognized by the backend
    # access added_rectangles and removed_rectangles through get_changed_rectangles()
    added_rectangles = []
    removed_rectangles = []

    tolerable_distance_to_combine_rectangles = 0.00005  # buildings need to be this (lat/long degrees) away to merge

    def __init__(self, init_points, to_id=True):
        self.points = init_points  # a point is a list, in (lat, long) form

        if to_id:
            Rectangle.current_id += 1
            self.id = Rectangle.current_id
            Rectangle.add_rectangle(self)

        # try to merge with all other rectangles, but if close enough
        # print('making new rectangle, merge status:', Rectangle.merge_mode)
        # print('all rects:', Rectangle.all_rectangles)
        # print('current rects:', Rectangle.added_rectangles)
        if Rectangle.merge_mode:
            for i in range(0, len(Rectangle.all_rectangles) - 1):
                if Rectangle.all_rectangles[i].merge_with(self):
                    # the merge is done and the Rectangles class is accordingly adjusted
                    break

    def merge_with(self, other_rectangle):
        for point in other_rectangle.points:
            # if the rectangles overlap
            if self.has_point_inside_approx(point):
                # get cords for the merged rectangle
                top = min(self.get_up_bound(), other_rectangle.get_up_bound())
                bot = max(self.get_down_bound(), other_rectangle.get_down_bound())
                right = max(self.get_right_bound(), other_rectangle.get_right_bound())
                left = min(self.get_left_bound(), other_rectangle.get_left_bound())

                # updating the static added_rectangles and removed_rectangles lists
                Rectangle.remove_rectangle_internally(other_rectangle)
                Rectangle.remove_rectangle_internally(self)

                # make a new merged rectangle
                Rectangle([[right, top], [left, top], [left, bot], [right, bot]])
                return True
        return False

    # Checks if a point is inside/on the borders
    def has_point_inside(self, point_to_check):
        has_up_bound, has_down_bound, has_left_bound, has_right_bound = False, False, False, False
        # check all lines in this rectangle -> does the point lay in between 4 lines?
        for i in range(0, len(self.points)):
            point1 = self.points[i]
            point2 = self.points[(i + 1) % len(self.points)]
            # if vertical line
            if point1[0] == point2[0]:
                if point1[1] < point_to_check[1] < point2[1] or point1[1] > point_to_check[1] > point2[1]:
                    # point_to_check is within the y-range of the line
                    if point_to_check[0] >= point1[0]:
                        has_left_bound = True
                    if point_to_check[0] <= point1[0]:
                        has_right_bound = True
            # if horizontal line
            if point1[1] == point2[1]:
                if point1[0] < point_to_check[0] < point2[0] or point1[0] > point_to_check[0] > point2[0]:
                    # point_to_check is within the x-domain of the line
                    if point_to_check[1] >= point1[1]:
                        has_down_bound = True
                    if point_to_check[1] <= point1[1]:
                        has_up_bound = True
        return has_up_bound and has_down_bound and has_left_bound and has_right_bound

    # check if point is close enough to be inside by shifting the point up, down, left, right
    def has_point_inside_approx(self, point_to_check, tolerable_distance=tolerable_distance_to_combine_rectangles):
        if tolerable_distance == 0:
            return self.has_point_inside(point_to_check)
        slide_right = self.has_point_inside((point_to_check[0] + tolerable_distance, point_to_check[1]))
        slide_left = self.has_point_inside((point_to_check[0] - tolerable_distance, point_to_check[1]))
        slide_up = self.has_point_inside((point_to_check[0], point_to_check[1] - tolerable_distance))
        slide_down = self.has_point_inside((point_to_check[0], point_to_check[1] + tolerable_distance))
        stay_put = self.has_point_inside(point_to_check)
        return slide_right or slide_left or slide_up or slide_down or stay_put

    # returns leftmost x cord
    def get_left_bound(self):
        left_bound = self.points[0][0]
        for point in self.points:
            if point[0] < left_bound:
                left_bound = point[0]
        return left_bound

    # returns rightmost x cord
    def get_right_bound(self):
        right_bound = self.points[0][0]
        for point in self.points:
            if point[0] > right_bound:
                right_bound = point[0]
        return right_bound

    # returns smallest y cord
    def get_up_bound(self):
        up_bound = self.points[0][1]
        for point in self.points:
            if point[1] < up_bound:
                up_bound = point[1]
        return up_bound

    # returns largest y cord
    def get_down_bound(self):
        down_bound = self.points[0][1]
        for point in self.points:
            if point[1] > down_bound:
                down_bound = point[1]
        return down_bound

    # once you get the added and removed rectangles, those lists are cleared is cleared
    # returns a tuple of lists -> (added_rectangles_list, removed_rectangles_list)
    @staticmethod
    def get_changed_rectangles():
        return Rectangle.get_added_rectangles(), Rectangle.get_removed_rectangles()

    @staticmethod
    def get_added_rectangles():
        temp = Rectangle.added_rectangles.copy()
        Rectangle.added_rectangles.clear()
        return temp

    @staticmethod
    def get_removed_rectangles():
        temp = Rectangle.removed_rectangles.copy()
        Rectangle.removed_rectangles.clear()
        return temp

    # updating the static added_rectangles and removed_rectangles lists
    @staticmethod
    def remove_rectangle_internally(rect):
        # if rectangle was added recently and not seen by the backend yet
        if rect in Rectangle.added_rectangles:
            Rectangle.added_rectangles.remove(rect)
        else:  # rectangle is established on the backend and needs to be removed
            Rectangle.removed_rectangles.append(rect)

        Rectangle.all_rectangles.remove(rect)

    # updating the static added_rectangles and removed_rectangles lists
    @staticmethod
    def add_rectangle(rect):
        Rectangle.all_rectangles.append(rect)
        Rectangle.added_rectangles.append(rect)

    @staticmethod
    def get_all_rectangles():
        return Rectangle.all_rectangles

    def get_id(self):
        return self.id

    def get_points(self):
        return self.points

    # convert a list of rectangles into a list of rectangle ids
    @staticmethod
    def arr_rect_to_id(rect_arr):
        id_arr = []
        for rect in rect_arr:
            id_arr.append(rect.get_id())
        return id_arr

    @staticmethod
    def delete_rect(remove_rect_id):
        for rect in Rectangle.all_rectangles:
            if rect.get_id() == remove_rect_id:
                Rectangle.all_rectangles.remove(rect)
                if rect in Rectangle.added_rectangles:
                    Rectangle.added_rectangles.remove(rect)
                if rect in Rectangle.removed_rectangles:
                    Rectangle.removed_rectangles.remove(rect)
                return True
        return False

    # reset all internal storage of rectangle objects
    @staticmethod
    def delete_all_rects():
        Rectangle.all_rectangles.clear()
        Rectangle.added_rectangles.clear()
        Rectangle.removed_rectangles.clear()


# detect a rectangle, then log it to the Rectangle class, which keeps track of merging and logging rectangles
def detect_rectangle(pil_image, xtile, ytile, lat, long, zoom, complex, threshold=None):
    """ Tries to detect the rectangle at a given point on an image. """

    if not complex:
        pil_image = PIL.ImageOps.grayscale(pil_image)

        im = np.array(pil_image)

        # Get the x,y coordinates of the click
        x, y = geolocation.deg_to_tilexy_matrix(lat, long, zoom)

        quad_one = get_next_intensity_change(im, x, y, 1, 0)
        quad_four = get_next_intensity_change(im, x, y, 0, -1)
        quad_two = get_next_intensity_change(im, x, y, 0, 1)
        quad_three = get_next_intensity_change(im, x, y, -1, 0)

        corner1 = quad_one[0], quad_two[1]
        corner2 = quad_one[0], quad_four[1]
        corner3 = quad_three[0], quad_four[1]
        corner4 = quad_three[0], quad_two[1]

        # Calculate the geocoordinates of the rectangle
        topright = geolocation.tilexy_to_deg_matrix(xtile, ytile, zoom, corner1[0], corner1[1])
        bottomright = geolocation.tilexy_to_deg_matrix(xtile, ytile, zoom, corner2[0], corner2[1])
        bottomleft = geolocation.tilexy_to_deg_matrix(xtile, ytile, zoom, corner3[0], corner3[1])
        topleft = geolocation.tilexy_to_deg_matrix(xtile, ytile, zoom, corner4[0], corner4[1])

        topleft = list(topleft)
        topright = list(topright)
        bottomright = list(bottomright)
        bottomleft = list(bottomleft)

        Rectangle([topleft, topright, bottomright, bottomleft])

        retangles_to_add = Rectangle.get_added_rectangles()

        # return the rectangle's id added from the click/merge, the rectangle's points, and the ids of all rectangles to remove (from merging)
        return (retangles_to_add[0].get_id(), retangles_to_add[0].get_points(),
                Rectangle.arr_rect_to_id(Rectangle.get_removed_rectangles()))

    else:
        """ Tries to detect the rectangle at a given point on an image. """
        if threshold == None:
            threshold = 25

        # Get the x,y coordinates of the click
        x, y = geolocation.deg_to_tilexy_matrix(lat, long, zoom)

        pil_image = np.array(pil_image)
        building_points = run_all(pil_image, x, y, threshold)
        vertex_list = []
        # corners are already structured
        for corner in building_points:
            next_vertex = geolocation.tilexy_to_deg_matrix(xtile, ytile, zoom, corner[0], corner[1])
            vertex_list.append(list(next_vertex))

        Rectangle(vertex_list)

        retangles_to_add = Rectangle.get_added_rectangles()

        # return the rectangle's id added from the click/merge, the rectangle's points, and the ids of all rectangles to remove (from merging)
        return (retangles_to_add[0].get_id(), retangles_to_add[0].get_points(),
                Rectangle.arr_rect_to_id(Rectangle.get_removed_rectangles()))


# Get the next major intensity change in a given direction.
def get_next_intensity_change(image, x, y, xstep, ystep):

    def threshold_slider(cur_intensity):
        fit = math.ceil(0.25*cur_intensity - 10)
        if fit < 0:
            fit = 10
        return fit

    lookahead = 5
    width = image.shape[1]
    height = image.shape[0]


    while (x >= 0 and x < width and y >= 0 and y < height):
        
        if (x + xstep < 0 or x + xstep >= width or y + ystep < 0 or y + ystep >= height):
            break
        
        x += xstep
        y += ystep

        # keeps the x coordinates and y coordinates bounded by 0 and width / height respectively
        downx = max(min(int(x + xstep * lookahead), width - 1), 0)
        downy = max(min(int(y + ystep * lookahead), height - 1), 0)
        
        cur_intensity = int(image[int(y), int(x)])
        next_intensity = int(image[downy, downx])
        threshold = threshold_slider(cur_intensity)
        
        if (abs(cur_intensity - next_intensity) > threshold):
            for i in range(lookahead, -1, -1):
                downx = max(min(int(x + xstep * i), width - 1), 0)
                downy = max(min(int(y + ystep * i), height - 1), 0)
                
                next_intensity = int(image[downy, downx])
                if (abs(cur_intensity - next_intensity) > threshold):
                    return (downx, downy)
            return (downx, downy)
    
    return (x, y)

# delete the rectangle manually (such as from undo-ing a click from the frontend)
def delete_rect(rect_id):
    Rectangle.delete_rect(rect_id)


# set if rectangles merge or not
def set_merge_mode(merge_mode_state):
    Rectangle.merge_mode = merge_mode_state


# toggle between True and False for merge_mode
def toggle_merge_mode():
    Rectangle.merge_mode = not Rectangle.merge_mode
    return Rectangle.merge_mode


def get_merge_mode():
    return Rectangle.merge_mode


def get_all_rects():
	return Rectangle.get_all_rectangles()


def get_all_rects_id():
	return Rectangle.arr_rect_to_id(Rectangle.get_all_rectangles())


def delete_all_rects():
	Rectangle.delete_all_rects()


def get_all_rects_dictionary():
    rect_dict = {}
    for rect in Rectangle.all_rectangles:
        rect_dict[rect.get_id()] = rect.get_points()
    return rect_dict
    