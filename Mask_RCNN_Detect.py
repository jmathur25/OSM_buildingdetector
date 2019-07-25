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
import imagery

class BuildingConfig(Config):
    """Configuration for training on data in MS COCO format.
    Derives from the base Config class and overrides values specific
    to the COCO dataset.
    """
    # Give the configuration a recognizable name
    NAME = "OSM_buildingdetector"

    # We use a GPU with 12GB memory, which can fit two images.
    # Adjust down if you get "ResourceExhaustedError" while running training
    IMAGES_PER_GPU = 2

    # Uncomment to train on 8 GPUs (default is 1)
    GPU_COUNT = 1

    # Number of classes (including background)
    NUM_CLASSES = 1 + 1  # 1 Backgroun + 1 Building

    STEPS_PER_EPOCH=1000
    VALIDATION_STEPS=50


    IMAGE_MAX_DIM=320
    IMAGE_MIN_DIM=320

class InferenceConfig(BuildingConfig):
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1 

MODEL_DIR = ''
ROOT_DIR = ''

class Mask_RCNN_Detect():

    def __init__(self):
        self.inference_config = InferenceConfig()
        self.model = modellib.MaskRCNN(mode="inference", config=self.inference_config, model_dir=MODEL_DIR)

        model_path = os.path.join(ROOT_DIR, "weights/pretrained_weights.h5")
        print("Loading weights from ", model_path)
        self.model.load_weights(model_path, by_name=True)
        self.model.detect([imageio.core.util.Array(np.array(Image.open('osm_images/tmp.PNG'))[:,:,:3])])
        print("initial detect works")

    def detect_building(self, image, lat, long, zoom):
        print(type(image), image.shape)
        Image.fromarray(image).save('click_original.png')

        image_tl = image[:len(image)//2, :len(image)//2,:] # top left
        image_tr = image[len(image)//2:, :len(image)//2,:] # top right
        image_br = image[len(image)//2:, len(image)//2:,:] # bottom right
        image_bl = image[:len(image)//2, len(image)//2:,:] # bottom left

        mask_tl = None
        mask_tr = None
        mask_br = None
        mask_bl = None
        for i, image in enumerate([image_tl, image_tr, image_br, image_bl]):
            image = Image.fromarray(image)
            original_size = (image.size[0], image.size[1])
            image = image.resize((320,320), Image.ANTIALIAS)
            detection = self.model.detect([imageio.core.util.Array(np.array(image)[:,:,:3])])
            masks = detection[0]['masks']
            masks = masks.any(axis=2) # doesn't solve overlap problem
            masks = Image.fromarray(masks).resize(original_size, Image.ANTIALIAS)
            if i == 0: mask_tl = masks
            elif i == 1: mask_tr = masks
            elif i == 2: mask_br = masks
            else: mask_bl = masks

        mask_up = np.hstack((mask_tl, mask_tr))
        mask_down = np.hstack((mask_bl, mask_br))

        masks = np.vstack((mask_up, mask_down))
        plt.imsave('result.png', masks)

        to_return = []
        
        # find xtile, ytile
        xtile, ytile = geolocation.deg_to_tile(lat, long, zoom)

        for i in range(masks.shape[1]):
            for j in range(masks.shape[0]):
                if masks[j,i]:
                    geo_point = geolocation.tilexy_to_deg_matrix(xtile, ytile, zoom, i, j)
                    to_return.append(list(geo_point))

        return to_return
