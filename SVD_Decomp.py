'''
Written by james on 11/10/2018

Feature: Image Decomposition
'''

import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

path = 'some_houses_gray.png'
img = Image.open(path)
s = float(os.path.getsize(path))/1000
print("Size(dimension): ",img.size)
plt.title("Original Image (%0.2f Kb):" %s)
plt.imshow(img)

imggray = img.convert('LA')
imgmat = np.array( list(imggray.getdata(band = 0)), float)
imgmat.shape = (imggray.size[1], imggray.size[0])
imgmat = np.matrix(imgmat)
plt.figure()
plt.imshow(imgmat, cmap = 'gray')
plt.title("Image after converting it into the Grayscale pattern")
plt.show()

print("After compression: ")
U, S, Vt = np.linalg.svd(imgmat) #single value decomposition
# for i in range(1, 20):
#     cmpimg = np.matrix(U[:, :i]) * np.diag(S[:i]) * np.matrix(Vt[:i,:])
#     plt.imshow(cmpimg, cmap = 'gray')
#     title = " Image after =  %s" %i
#     plt.title(title)
#     plt.show()
#     result = Image.fromarray((cmpimg ).astype(np.uint8))
cmpimg = np.matrix(U[:, :4]) * np.diag(S[:4]) * np.matrix(Vt[:4,:])
result = Image.fromarray((cmpimg ).astype(np.uint8))
result.save('compressed_big.jpg')