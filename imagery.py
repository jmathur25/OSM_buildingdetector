"""Interface for downloading aerial imagery from Mapbox.
"""

import requests
from PIL import Image
from io import BytesIO
from geolocation import *
import os.path
import numpy as np
from mapbox import Maps
import matplotlib
matplotlib.use('PS')
import matplotlib.pyplot as plt

class ImageryDownloader(object):

    def __init__(self, access_token):
        """Initializes the object with a Mapbox access token"""
        self.maps = Maps(access_token=access_token)
    
    def download_tile(self, x, y, zoom):
        """Downloads a map tile as an image.
           Note that x and y refer to Slippy Map coordinates.
        """
        response = self.maps.tile("mapbox.satellite", x, y, zoom)
        image = Image.open(BytesIO(response.content))

        return image
    
    def get_tiles_around(self, x, y, zoom):
        im = self.download_tile(x, y, zoom)
        print(im.size, np.array(im).shape)
        return im
        # """Downloads all the tiles around the x, y tile"""
        # image = Image.new("RGB", (256 * 3, 256 * 3))
        # for i in range(-1, 2, 1):
        #     for j in range(-1, 2, 1):
        #         try:
        #             tile_part = Image.fromarray(self.download_tile(x + i, y + j, zoom))
        #             image.paste(tile_part, (256 * (i + 1), 256 * (j + 1)))
        #         except:
        #             pass
        # return image
