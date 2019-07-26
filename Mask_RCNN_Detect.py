import imagery
from mrcnn import model as modellib, utils
from mrcnn.config import Config
import os
from PIL import Image
import imageio
import numpy as np
import warnings
import geolocation
import matplotlib.pyplot as plt
from skimage.transform import resize as scale_resize
warnings.filterwarnings('ignore')


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
            np.array(Image.open('osm_images/tmp.PNG'))[:, :, :3])])
        print("initial detect works")

        self.image_id = 1
        self.id = 1 # for id-ing buildings
        self.id_to_points = {}

    # to_id should only be true while using the Flask app
    # id-ing will help the Mask_R_CNN keep track of each building and adjustments that need to be made
    def detect_building(self, image, lat=None, long=None, zoom=None, to_id=False):
        print(type(image), image.shape)

        if to_id: plt.imsave('runtime/images/image_{}.png'.format(self.image_id), image)

        # to return
        masks = None

        # image needs to be split into pieces
        if image.shape[0] > 500 or image.shape[1] > 500:
            masks = self._detect_with_split(image, to_id)
        else:
            # _small_merge merges
            masks = self._detect_single(image, to_id)

        if to_id: plt.imsave('runtime/masks/mask_{}.png'.format(self.image_id), masks)

        # just a regular image, not part of Flask setup
        if lat is None or long is None or zoom is None:
            return masks != 0 # turns into boolean mask

        # list of lat/long points to plot
        to_return = {}

        # # find x, y
        x, y = geolocation.deg_to_tilexy(lat, long, zoom)

        # find xtile, ytile
        xtile, ytile = geolocation.deg_to_tile(lat, long, zoom)

        # will turn all True x,y points to lat/long
        for r in range(masks.shape[1]):  # horizontal (x)
            for c in range(masks.shape[0]):  # vertical (y)
                if masks[c, r] != 0:
                    geo_point = list(geolocation.tilexy_to_deg_matrix(xtile+1, ytile+1, zoom, r, c))
                    spot_id = masks[c, r]
                    if spot_id not in to_return:
                        to_return[spot_id] = [geo_point]
                        # storing all these points in memory will suck, need to "rectanglify"
                        self.id_to_points[spot_id] = [geo_point]
                    else:
                        to_return[spot_id].append(geo_point)
                        self.id_to_points[spot_id].append(geo_point)
        self.image_id += 1
        return to_return

    def _detect_single(self, image, to_id=False):
        # image needs to be split into pieces
        if image.shape[0] >= 560 or image.shape[1] >= 560:
            return self._detect_with_split(image)

        original_size = (image.shape[0], image.shape[1])
        image = (scale_resize(image, (320, 320), anti_aliasing=True) * 256).astype(np.uint8)
        detection = self.model.detect(
            [imageio.core.util.Array(image)])
        masks = detection[0]['masks']
        masks = self._small_merge(masks, to_id) # could just do masks.any(axis=2) but this should be better
        masks = scale_resize(masks, original_size, anti_aliasing=True, preserve_range=True)
        return masks

    def _detect_with_split(self, image, to_id=False):
        minimum = 280
        height, width = image.shape[0], image.shape[1]
        # makes sure image needs to be split in the first
        assert height >= 2 * minimum or width >= 2 * minimum
        vert_num_splits = height // minimum
        horiz_num_splits = width // minimum

        # 250 x 560
        final_mask = np.zeros((image.shape[0], image.shape[1])).astype(bool)
        for i in range(vert_num_splits + 1):
            for j in range(horiz_num_splits + 1):
                # svi = start_vert_index; evi = end_vert_endex
                svi = i * minimum
                if i == vert_num_splits - 1:
                    evi = height
                else:
                    evi = (i + 1) * (height // vert_num_splits)
                # shi = start_horiz_index; ehi = end_horiz_index
                shi = i * minimum
                if i == horiz_num_splits - 1:
                    ehi = width
                else:
                    ehi = (i + 1) * (width // horiz_num_splits)
                im = image[svi:evi, shi:ehi, :]
                original_size = (im.shape[0], im.shape[1])
                im = (scale_resize(im, (320, 320), anti_aliasing=True) * 256).astype(np.unint8)
                detection = self.model.detect(
                    [imageio.core.util.Array(im)])
                masks = detection[0]['masks']
                masks = self._small_merge(masks, to_id)
                masks = scale_resize(masks, original_size, anti_aliasing=True, preserve_range=True)
                # pastes result into the final mask
                final_mask[svi:evi, shi:ehi] = masks

        return final_mask

    # merges buildings and prevents significant overlap / massive masks
    def _small_merge(self, masks, to_id=False):  # merges only the small ones inside
        net_mask = np.zeros((masks.shape[0], masks.shape[1]))
        for i, layer in enumerate(range(masks.shape[2])):
            m = masks[:, :, layer]  # gives an id
            shared = (m & (net_mask != 0))
            i += 1
            shared_count = np.count_nonzero(shared)
            if (shared_count > 100):
                new_id = i
                if to_id:
                    new_id = self.id
                    self.id += 1
                tmp = np.argwhere(shared)[0]
                collision_id = net_mask[tmp[0], tmp[1]]
                collision_id_mask = net_mask == collision_id

                new_count = np.count_nonzero(m)
                collision_count = np.count_nonzero(collision_id_mask)

                if new_count < collision_count:
                    net_mask[collision_id_mask] = 0
                    net_mask += m * new_id
            else:
                if to_id:
                    i = self.id
                    self.id += 1
                net_mask += m * i
        return net_mask # can make this a boolean mask through net_mask != 0

    # need a way to efficiently do this, perhaps sort by tile
    def delete_mask(self, lat, long, zoom):
        print("click:", lat, long)
        for key in self.id_to_points:
            points = self.id_to_points[key]
            for point in points:
                print(point)
                if lat == point[0] and long == point[1]:
                    print("REMOVE: ", key)
                    return key

        return -1
