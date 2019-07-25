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
    """Configuration for training on data in MS COCO format.
    Derives from the base Config class and overrides values specific
    to the COCO dataset.
    """
    NAME = "OSM_buildingdetector"
    GPU_COUNT = 1 # 1 GPU = CPU
    IMAGES_PER_GPU = 1

    IMAGE_MAX_DIM = 320
    IMAGE_MIN_DIM = 320

MODEL_DIR = ''
ROOT_DIR = ''

class Mask_RCNN_Detect():

    def __init__(self):
        self.inference_config = InferenceConfig()
        self.model = modellib.MaskRCNN(
            mode="inference", config=self.inference_config, model_dir=MODEL_DIR)

        model_path = os.path.join(ROOT_DIR, "weights/pretrained_weights.h5")
        print("Loading weights from ", model_path)
        self.model.load_weights(model_path, by_name=True)
        self.model.detect([imageio.core.util.Array(np.array(Image.open('osm_images/tmp.PNG'))[:, :, :3])])
        print("initial detect works")

    def detect_building(self, image, lat=None, long=None, zoom=None):
        print(type(image), image.shape)
        Image.fromarray(image).save('click_original.png')

        # just a regular image
        if lat is None or long is None or zoom is None:
            return _detect_single(image)

        # to return
        masks = None

        # image needs to be split into pieces
        if image.shape[0] > 500 or image.shape[1] > 500:
            masks = _detect_with_split(image)
        else:
            image = Image.fromarray(image)
            image.save('click_original.png')
            original_size = (image.size[0], image.size[1])
            image = image.resize((320, 320), Image.ANTIALIAS)
            detection = self.model.detect(
                [imageio.core.util.Array(np.array(image)[:, :, :3])])
            masks = detection[0]['masks']
            masks = masks.any(axis=2) # flattens masks, doesn't solve overlap problem
            masks = Image.fromarray(masks).resize(original_size, Image.ANTIALIAS)
            plt.imsave('result.png', masks)
            masks = np.array(masks)

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
            return _detect_with_split(image)

        image = Image.fromarray(image)
        original_size = (image.size[0], image.size[1])
        image = image.resize((320, 320), Image.ANTIALIAS)
        detection = self.model.detect(
            [imageio.core.util.Array(np.array(image)[:, :, :3])])
        masks = detection[0]['masks']
        masks = masks.any(axis=2) # flattens masks, doesn't solve overlap problem
        masks = Image.fromarray(masks).resize(original_size, Image.ANTIALIAS)
        if save is not None:
            plt.imsave(save, masks)
        masks = np.array(masks)
        return masks

    def _detect_with_split(self, image):
        minimum = 280
        height, width, image.shape[0], image.shape[1]
        # makes sure image needs to be split in the first
        assert height >= 2 * minimum or width >= 2 * minimum
        vert_num_splits = height // minimum
        horiz_num_splits = width // minimum

        # 250 x 560
        final_mask = np.zeros((image.shape[0], image.shape[1]))
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

                image = image[svi:evi, shi:ehi, :]
                image = Image.fromarray(image)
                original_size = (image.size[0], image.size[1])
                image = image.resize((320, 320), Image.ANTIALIAS)
                detection = self.model.detect([imageio.core.util.Array(np.array(image)[:, :, :3])])
                masks = detection[0]['masks']
                masks = masks.any(axis=2)  # flattens masks, doesn't solve overlap problem
                masks = Image.fromarray(masks).resize(original_size, Image.ANTIALIAS)
                # pastes result into the final mask
                final_mask[svi:evi, shi:ehi] = masks

        return final_mask



        # image_tl = image[:len(image)//2, :len(image)//2, :]  # top left
        # image_tr = image[len(image)//2:, :len(image)//2, :]  # top right
        # image_br = image[len(image)//2:, len(image)//2:, :]  # bottom right
        # image_bl = image[:len(image)//2, len(image)//2:, :]  # bottom left

        # mask_tl = None
        # mask_tr = None
        # mask_br = None
        # mask_bl = None
        # for i, image in enumerate([image_tl, image_tr, image_br, image_bl]):
        #     image = Image.fromarray(image)
        #     original_size = (image.size[0], image.size[1])
        #     image = image.resize((320, 320), Image.ANTIALIAS)
        #     detection = self.model.detect(
        #         [imageio.core.util.Array(np.array(image)[:, :, :3])])
        #     masks = detection[0]['masks']
        #     masks = masks.any(axis=2)  # doesn't solve overlap problem
        #     masks = Image.fromarray(masks).resize(
        #         original_size, Image.ANTIALIAS)
        #     if i == 0:
        #         mask_tl = masks
        #     elif i == 1:
        #         mask_tr = masks
        #     elif i == 2:
        #         mask_br = masks
        #     else:
        #         mask_bl = masks

        # mask_up = np.hstack((mask_tl, mask_tr))
        # mask_down = np.hstack((mask_bl, mask_br))
        # masks = np.vstack((mask_up, mask_down))

        # return masks
