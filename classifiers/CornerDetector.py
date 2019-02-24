import numpy as np
import cv2
from matplotlib import pyplot as plt


image = cv2.imread('champaigneditedcompressed.png')
kernel = np.ones((20, 20), np.float32) / 25
img = cv2.filter2D(image, -1, kernel)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

corners = cv2.goodFeaturesToTrack(gray,10,0.01,10)
corners = np.int0(corners)
print(corners)
for i in corners:
    x,y = i.ravel()
    cv2.circle(img,(x,y),3,255,-1)

plt.imshow(img),plt.show()
