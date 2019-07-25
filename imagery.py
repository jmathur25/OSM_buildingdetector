"""Interface for downloading aerial imagery from Mapbox.
"""

import requests
from PIL import Image
from io import BytesIO
from geolocation import *
import os.path
import numpy as np
import matplotlib.pyplot as plt

class ImageryDownloader(object):

    def __init__(self, imagery_url, access_token=""):
        """Initializes the object with a Mapbox access token"""
        self.imagery_url = imagery_url
        self.access_token = access_token
    
    def download_tile(self, x, y, zoom):
        """Downloads a map tile as an image.
           Note that x and y refer to Slippy Map coordinates.
        """
        
        # Try to fetch the image from the cache first
        img_fname = self.get_tile_filename(x, y, zoom)
        if os.path.isfile(img_fname):
            return (plt.imread(img_fname) * 256).astype(np.uint8)
        
        # Download the image
        url = self.imagery_url
        url = url.replace("{x}", str(x))
        url = url.replace("{y}", str(y))
        url = url.replace("{zoom}", str(zoom))
        url = url.replace("{access_key}", self.access_token)
        
        req = requests.get(url)
        image = Image.open(BytesIO(req.content))
        
        # Save in the cache
        if not os.path.exists(os.path.dirname(img_fname)):
            try:
                os.makedirs(os.path.dirname(img_fname))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        image.save(img_fname)
        
        return image

    def get_tile_filename(self, x, y, zoom):
        """Get the filename for a given tile"""
        img_fname = "imgcache/" + str(zoom) + "/" + str(x) + "/" + str(y) + ".png"
        return img_fname
    
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
