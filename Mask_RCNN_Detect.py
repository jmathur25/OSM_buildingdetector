import imagery
from mrcnn import model as modellib, utils
from mrcnn.config import Config
import os
from PIL import Image
import imageio
import numpy as np
import warnings
import geolocation

import matplotlib
matplotlib.use('PS')
import matplotlib.pyplot as plt
import matplotlib.path as pltPath

# scaling the image
from skimage.transform import resize as resize
warnings.filterwarnings('ignore')

# gets a minimum bounding rectangle
from detectors.algorithms import Polygonify
import cv2

class InferenceConfig(Config):
    # Give the configuration a recognizable name
    NAME = "OSM_buildingdetector"

    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

    # Number of classes (including background)
    NUM_CLASSES = 1 + 1  # 1 Backgroun + 1 Building

    IMAGE_MAX_DIM = 320
    IMAGE_MIN_DIM = 320


MODEL_DIR = ''
ROOT_DIR = ''


class Mask_RCNN_Detect():
    def __init__(self, weights):
        self.inference_config = InferenceConfig()
        self.model = modellib.MaskRCNN(
            mode="inference", config=self.inference_config, model_dir=MODEL_DIR)

        # model_path = os.path.join(ROOT_DIR, "weights/pretrained_weights.h5")
        model_path = os.path.join(ROOT_DIR, weights)
        print("Loading weights from ", model_path)
        self.model.load_weights(model_path, by_name=True)
        self.model.detect([imageio.core.util.Array(
            np.array(Image.open('default_images/tmp.PNG'))[:, :, :3])])
        print("initial detect works")

        self.image_id = 1
        self.building_id = 1 # for id-ing buildings
        self.geo_to_point = {}
        self.id_geo_tile = {}
        self.id_geo = {}

    def clear(self):
        self.geo_point = {}
        self.id_geo_tile = {}
        self.id_geo = {}

    # to_id should only be true while using the Flask app
    # id-ing will help the Mask_R_CNN keep track of each building and adjustments that need to be made
    def detect_building(self, image, lat=None, long=None, zoom=None, rectanglify=True, to_fill=False):
        assert(image.shape[-1] == 3) # must be size hxwx3

        
        # to return
        masks = self._detect_single(image, rectanglify, to_fill)
        
        # just a regular image, not part of Flask setup
        if lat is None or long is None or zoom is None:
            masks = resize(masks, (image.shape[0], image.shape[1]), preserve_range=True) # masks can be reshaped, corners can't
            masks = masks != 0 # converts to bool mask
            return masks

        self.image_id += 1

        # list of lat/long points to plot
        to_return = {}

        # find xtile, ytile
        xtile, ytile = geolocation.deg_to_tile(lat, long, zoom)
        if (xtile+1, ytile+1) not in self.geo_to_point:
            self.geo_to_point[(xtile+1,ytile+1)] = {}
        relevant = self.geo_to_point[(xtile+1,ytile+1)]

        if rectanglify:
            # finds corners
            building_ids = np.unique(masks)
            building_ids = building_ids[building_ids != 0].astype(int).tolist()
            for i, ids in enumerate(building_ids):
                points = np.argwhere(masks == ids).tolist() # gets as coordinates
                if len(points) != 4:
                    print("NOT 4 POINTS INSTANCE, SKIPPING BY DEFAULT")
                    continue
                for j in range(len(points)):
                    x = points[j][1]
                    y = points[j][0]
                    x = int((image.shape[1] / masks.shape[1]) * x) # scales x to what it would be in the original image
                    y = int((image.shape[1] / masks.shape[1]) * y) # scales y to what it would be in the original image
                    geopoint = list(geolocation.tilexy_to_deg_matrix(xtile+1, ytile+1, zoom, x, y))
                    points[j] = geopoint
                tmp = points[2] # needs to be swapped to be in the right order when plotted
                points[2] = points[3]
                points[3] = tmp
                to_return[self.building_id] = points
                relevant[self.building_id] = points # all the points are stored in class memory
                self.id_geo_tile[self.building_id] = (xtile+1, ytile+1) # if the building id is given, we can backtrace the geotile
                self.id_geo[self.building_id] = points
                self.building_id += 1
        return to_return

    def _detect_single(self, image, rectanglify=True, to_fill=False):
        image = (resize(image, (320, 320), anti_aliasing=True) * 256).astype(np.uint8)
        detection = self.model.detect(
            [imageio.core.util.Array(image)])
        masks = detection[0]['masks']
        masks = self._small_merge(masks)
        plt.imsave('runtime/masks/mask_{}.png'.format(self.image_id), (masks != 0).astype(bool))
            
        if rectanglify:
            # finds all buildings (one building has the same number in masks)
            building_ids = np.unique(masks)
            building_ids = building_ids[building_ids != 0]
            out_mask = np.zeros((masks.shape[0], masks.shape[1], 3), dtype=np.uint8)
            for i, ids in enumerate(building_ids):
                building_corner_image = self._detect_mask_corners(masks == ids) # gets the corners of a building in a boolean mask
                points = np.argwhere(building_corner_image) # gets as coordinates
                plottable = []
                for x,y in zip(points[:,0], points[:,1]):
                    plottable.append((y, x))
                    if not to_fill: out_mask[x,y,:] = np.array([i+1,i+1,i+1]) # gets the corner
                tmp = np.copy(plottable[2]) # reorders points
                plottable[2] = plottable[3]
                plottable[3] = tmp
                plottable = np.array(plottable, np.int32).reshape(-1,1,2)
                if to_fill:
                    cv2.fillPoly(out_mask, [plottable], (i+1,i+1,i+1)) # draws a rectangle using points
            masks = out_mask[:,:,0]

        return masks # not resized back

    # merges buildings and prevents significant overlap / massive masks
    def _small_merge(self, masks):  # merges only the small ones inside
        net_mask = np.zeros((masks.shape[0], masks.shape[1]))
        for i, layer in enumerate(range(masks.shape[2])):
            m = masks[:, :, layer]  # gives an id
            shared = (m & (net_mask != 0))
            i += 1 # ids range from 1 to # buildings
            shared_count = np.count_nonzero(shared)
            if (shared_count > 100):
                new_id = i
                tmp = np.argwhere(shared)[0]
                collision_id = net_mask[tmp[0], tmp[1]]
                collision_id_mask = net_mask == collision_id

                new_count = np.count_nonzero(m)
                collision_count = np.count_nonzero(collision_id_mask)

                if new_count < collision_count:
                    net_mask[collision_id_mask] = 0
                    net_mask += m * new_id
            else:
                net_mask += m * i

        return net_mask # can make this into a single boolean mask by running net_mask != 0

    # need a way to efficiently do this, perhaps sort by tile
    # given a lat/lng or a building_id, it deletes a building
    def delete_mask(self, lat=None, lng=None, zoom=None, building_id=None):
        assert lat is not None or building_id is not None
        if building_id is not None:
            xtile, ytile = self.id_geo_tile[building_id]
            del self.geo_to_point[(xtile, ytile)][building_id]
            del self.id_geo_tile[building_id]
            del self.id_geo[building_id]
            return building_id

        # find xtile, ytile
        xtile, ytile = geolocation.deg_to_tile(lat, lng, zoom)
        if (xtile+1, ytile+1) in self.geo_to_point:
            relevant = self.geo_to_point[(xtile+1,ytile+1)]
            for building_id in relevant:
                points = relevant[building_id]
                polygon = pltPath.Path(points)
                if polygon.contains_point([lat,lng]):
                    del relevant[building_id]
                    del self.id_geo_tile[building_id]
                    return building_id
        return -1 # no match


    # gets the corners from a boolean mask, returns a new mask with just the corners
    def _detect_mask_corners(self, im):
        dst = cv2.cornerHarris(np.float32(im),2,3,0.04)
        idxs = np.argwhere(dst != 0)
        guides = np.median(idxs, axis=0)
        
        distr = np.sum((idxs - guides)**2,axis=1)
        # helps rule out far points that don't belong to the main image
        std = np.std(distr)
        median = np.median(distr)
        upper = (2*std + 1) * median
        lower = (1 - 2*std) * median
        
        lookup = np.any([distr < (2*std + 1) * median, distr > (1 - 2*std) * median], axis=0)
        
        pg = Polygonify(idxs[lookup])
        corners = pg.find_polygon()

        img = np.zeros(im.shape, dtype=bool)
        for x,y in zip(corners[:,0], corners[:,1]):
            x = int(round(x))
            y = int(round(y))
            if x < 0: x = 0
            elif x >= im.shape[0]: x = im.shape[0] - 1
            if y < 0: y = 0
            elif y >= im.shape[1]: y = im.shape[1] - 1
            img[x,y] = True
        return img

    def plot_corners(self, dict_corners, mask_shape):
        out_mask = np.zeros(mask_shape)
        for i, v in enumerate(dict_corners.values()):
            cv2.fillPoly(out_mask, [np.array(v)], (i+1,i+1,i+1))
        return out_mask
