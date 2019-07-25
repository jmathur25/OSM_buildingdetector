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

    def detect_building(self, image, lat=None, long=None, zoom=None):
        print(type(image), image.shape)
        Image.fromarray(image).save('click_original.png')

        # just a regular image
        if lat is None or long is None or zoom is None:
            return self._detect_single(image)

        # to return
        masks = None

        # image needs to be split into pieces
        if image.shape[0] > 500 or image.shape[1] > 500:
            masks = self._detect_with_split(image)
        else:
            image = Image.fromarray(image)
            image.save('click_original.png')
            original_size = (image.size[0], image.size[1])
            image = image.resize((320, 320), Image.ANTIALIAS)
            detection = self.model.detect(
                [imageio.core.util.Array(np.array(image)[:, :, :3])])
            masks = detection[0]['masks']
            masks = self._small_merge(masks)
            
            
        masks = np.array(Image.fromarray(masks).resize(original_size, Image.ANTIALIAS))
        plt.imsave('result.png', masks)

        # list of lat/long points to plot
        to_return = []

        # find xtile, ytile
        xtile, ytile = geolocation.deg_to_tile(lat, long, zoom)

        # will turn all True x,y points to lat/long
        for x in range(masks.shape[1]):  # horizontal (x)
            for y in range(masks.shape[0]):  # vertical (y)
                if masks[y, x]:
                    geo_point = geolocation.tilexy_to_deg_matrix(
                        xtile+1, ytile+1, zoom, x, y)
                    to_return.append(list(geo_point))

        return to_return

    def _detect_single(self, image, save=None):
        # image needs to be split into pieces
        if image.shape[0] >= 560 or image.shape[1] >= 560:
            return self._detect_with_split(image)

        image = Image.fromarray(image)
        original_size = (image.size[0], image.size[1])
        image = image.resize((320, 320), Image.ANTIALIAS)
        detection = self.model.detect(
            [imageio.core.util.Array(np.array(image)[:, :, :3])])
        masks = detection[0]['masks']
        masks = self._small_merge(masks) # could just do masks.any(axis=2) but this should be better
        masks = Image.fromarray(masks).resize(original_size, Image.ANTIALIAS)
        if save is not None:
            plt.imsave(save, masks)
        masks = np.array(masks)
        return masks

    def _detect_with_split(self, image):
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
                im = Image.fromarray(im)
                original_size = (im.size[0], im.size[1])
                im = im.resize((320, 320), Image.ANTIALIAS)
                detection = self.model.detect(
                    [imageio.core.util.Array(np.array(im)[:, :, :3])])
                masks = detection[0]['masks']
                masks = self._small_merge(masks)
                masks = Image.fromarray(masks).resize(
                    original_size, Image.ANTIALIAS)
                # pastes result into the final mask
                final_mask[svi:evi, shi:ehi] = masks

        return final_mask

    # merges buildings and prevents significant overlap / massive masks
    def _small_merge(self, masks):  # merges only the small ones inside
        net_mask = np.zeros((masks.shape[0], masks.shape[1]))
        for i, layer in enumerate(range(masks.shape[2])):
            m = masks[:, :, layer]  # gives an id
            shared = (m & (net_mask != 0))
            i += 1
            shared_count = np.count_nonzero(shared)
            if (shared_count > 100):
                new_id = i
                tmp = np.argwhere(shared)[0]
                collision_id = net_mask[tmp[0], tmp[1]]
                collision_id_mask = net_mask == collision_id

                new_count = np.count_nonzero(m)
                collision_count = np.count_nonzero(collision_id_mask)

                # you could use this to get larger buildings within a tolerance
                # if new_count > collision_count and new_count < 10000:
                #     net_mask[collision_id_mask] = 0
                #     net_mask += m * i
                if new_count < collision_count:
                    net_mask[collision_id_mask] = 0
                    net_mask += m * i
            else:
                net_mask += m * i
        return net_mask != 0  # True if was given an id (so is a mask)
