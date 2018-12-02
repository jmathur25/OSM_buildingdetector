"""Interface for downloading aerial imagery from Mapbox.
"""

import requests
from PIL import Image
from io import BytesIO
from geolocation import *
import os.path

class ImageryDownloader(object):

    def __init__(self, access_token):
        """Initializes the object with a Mapbox access token"""
        self.access_token = access_token
    
    def download_tile(self, x, y, zoom):
        """Downloads a map tile as an image.
           Note that x and y refer to Slippy Map coordinates.
        """
        
        # Try to fetch the image from the cache first
        img_fname = "imgcache/" + str(zoom) + "/" + str(x) + "/" + str(y) + ".png"
        if os.path.isfile(img_fname):
            return Image.open(img_fname)
        
        # Download the image
        url = "https://a.tiles.mapbox.com/v4/digitalglobe.316c9a2e/" \
               "" + str(zoom) + "/" + str(x) + "/" + str(y) + "" \
               ".png?access_token=" + self.access_token
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