"""Interface for downloading aerial imagery from Mapbox.
"""

import requests
from PIL import Image
from io import BytesIO
from geolocation import *

class ImageryDownloader(object):

    def __init__(self, access_token):
        """Initializes the object with a Mapbox access token"""
        self.access_token = access_token
    
    def download_tile(self, x, y, zoom):
        """Downloads a map tile as an image.
           Note that x and y refer to Slippy Map coordinates.
        """
        url = "https://a.tiles.mapbox.com/v4/digitalglobe.316c9a2e/" \
               "" + str(zoom) + "/" + str(x) + "/" + str(y) + "" \
               ".png?access_token=" + self.access_token
        req = requests.get(url)
        image = Image.open(BytesIO(req.content))
        return image
