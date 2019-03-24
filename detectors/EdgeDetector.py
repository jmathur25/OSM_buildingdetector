import numpy as np
import imageio
import scipy.ndimage
import matplotlib.pyplot as plt

# This is how faint a line needs to be before we don't draw it. 
# Lower for less lines
DARKEN_THRESHOLD = 30

# This is the sigma for the gaussian filter.
# Raise for less detail
RESOLUTION = 3
FILE = './diff_hue'

def dodge(front,back):
    result=front*255/(255-back)
    result[result>255]=255
    result[back==255]=255
    return result.astype('uint8')

def grayscale(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])

def roundUp(arr):
  result = arr
  result[result < DARKEN_THRESHOLD] = 255
  result[result >= DARKEN_THRESHOLD] = 0
  return result.astype('uint8')
  
def darken(greyscale):
  return map(roundUp, greyscale)

img = FILE + ".PNG"
s = imageio.imread(img)
g = grayscale(s)
i = 255-g
b = scipy.ndimage.filters.gaussian_filter(i,sigma = RESOLUTION)
#b = scipy.ndimage.filters.sobel(i)
sx = scipy.ndimage.sobel(i, axis=0, mode='constant')
sxy = scipy.ndimage.sobel(i, axis=-1, mode='constant')
sy = scipy.ndimage.sobel(i, axis=1, mode='constant')
b = np.hypot(sxy, np.hypot(sx, sy))
plt.imsave(FILE + 'Process.png', b, cmap='gray', vmin=0, vmax=255)