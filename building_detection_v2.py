import cv2
import numpy
import geolocation

# Next unique rectangle ID
current_rect_id = 0

def detect_rectangle(pil_image_grayscale, xtile, ytile, lat, long, zoom):
    """ Tries to detect the rectangle at a given point on an image. """
    im = numpy.array(pil_image_grayscale)
    
    # Get the x,y coordinates of the click
    x, y = geolocation.deg_to_tilexy_matrix(lat, long, zoom)
    
    # Get the boundaries of the rectangle
    left_loc_x, left_loc_y = get_next_intensity_change(im, x, y, -1, 0)
    right_loc_x, right_loc_y = get_next_intensity_change(im, x, y, 1, 0)
    up_loc_x, up_loc_y = get_next_intensity_change(im, x, y, 0, -1)
    down_loc_x, down_loc_y = get_next_intensity_change(im, x, y, 0, 1)
    
    # Calculate the geocoordinates of the rectangle
    topleft = geolocation.tilexy_to_deg_matrix(xtile, ytile, zoom, left_loc_x, up_loc_y)
    topright = geolocation.tilexy_to_deg_matrix(xtile, ytile, zoom, right_loc_x, up_loc_y)
    bottomright = geolocation.tilexy_to_deg_matrix(xtile, ytile, zoom, right_loc_x, down_loc_y)
    bottomleft = geolocation.tilexy_to_deg_matrix(xtile, ytile, zoom, left_loc_x, down_loc_y)
    
    topleft = list(topleft)
    topright = list(topright)
    bottomright = list(bottomright)
    bottomleft = list(bottomleft)
    
    rect_points = [topleft, topright, bottomright, bottomleft]
    rectangles_ids_to_remove = []
    
    # Get this rectangle's ID
    global current_rect_id
    my_id = current_rect_id
    current_rect_id += 1
    
    return (current_rect_id, rect_points, rectangles_ids_to_remove)

""" Get the next major intensity change in a given direction. """
def get_next_intensity_change(image, x, y, xstep, ystep):
    threshold = 30
    lookahead = 5
    width = image.shape[1]
    height = image.shape[0]
    
    seen = []
    seen_sum = 0
    
    xstart = x
    ystart = y
    
    while (x >= 0 and x < width and y >= 0 and y < height):
        
        if (x + xstep < 0 or x + xstep >= width or y + ystep < 0 or y + ystep >= height):
            break
        
        x += xstep
        y += ystep
        
        downx = max(min(x + xstep * lookahead, width - 1), 0)
        downy = max(min(y + ystep * lookahead, height - 1), 0)
        
        cur_intensity = int(image[y, x])
        next_intensity = int(image[downy, downx])
        
        seen.append(cur_intensity)
        seen_sum += cur_intensity
        
        # Find the variance
        if (len(seen) > 3):
            average = seen_sum / len(seen)
            variance = 0
            
            for i in seen:
                variance += (i - average) ** 2
            
            variance /= (len(seen) - 1)
            
            if (abs(cur_intensity - average) ** 2 > variance * 10 or abs(cur_intensity - next_intensity) > threshold):
                return (x, y)
    
    return (x, y)