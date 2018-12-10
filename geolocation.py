"""Contains functions dealing with geolocation. This is mostly used for finding
coordinates from Slippy Map tiles and vice versa.  Slippy Map tiles are used in
aerial imagery APIs.

For more information (and for the source of some of these functions) see
https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
"""
import math


def deg_to_tile(lat_deg, lon_deg, zoom):
    """Converts coordinates into the nearest x,y Slippy Map tile"""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad)))
                 / math.pi) / 2.0 * n)
    return (xtile, ytile)


def tile_to_deg(xtile, ytile, zoom):
    """Returns the coordinates of the northwest corner of a Slippy Map
    x,y tile"""
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

def deg_to_tilexy(lat_deg, lon_deg, zoom):
    """Converts geocoordinates to an x,y position on a tile."""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    x = ((lon_deg + 180.0) / 360.0 * n)
    y = ((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad)))
        / math.pi) / 2.0 * n)
    return (int((x % 1) * 256), int((y % 1) * 256))

def deg_to_tilexy_matrix(lat_deg, lon_deg, zoom, center_tile_xoffset = 1, center_tile_yoffset = 1):
    """Converts geocoordinates to an x,y position on a tile matrix.
    For a 3x3 tile matrix, the image used is the center tile, so pass
    1 for center_tile_xoffset and 1 for center_tile_yoffset"""
    x, y = deg_to_tilexy(lat_deg, lon_deg, zoom)
    return (256 * center_tile_xoffset + x, 256 * center_tile_yoffset + y)

def tilexy_to_deg(xtile, ytile, zoom, x, y):
    """Converts a specific location on a tile (x,y) to geocoordinates."""
    decimal_x = xtile + x / 256
    decimal_y = ytile + y / 256
    n = 2.0 ** zoom
    lon_deg = decimal_x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * decimal_y / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

def tilexy_to_deg_matrix(xtile, ytile, zoom, x, y, center_tile_xoffset = 1, center_tile_yoffset = 1):
    """Converts an x,y position on a tile matrix to geocoordinates.
    For a 3x3 tile matrix, the image used is the center tile, so pass
    1 for center_tile_xoffset and 1 for center_tile_yoffset"""
    return tilexy_to_deg(xtile + center_tile_xoffset, ytile + center_tile_yoffset, zoom, x, y)
