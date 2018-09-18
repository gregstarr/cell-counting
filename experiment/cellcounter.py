import numpy as np
from matplotlib import pyplot as plt
import cv2
import scipy.ndimage as ndi
from scipy.signal import correlate2d

#cells
im = cv2.imread("180904_ImageJ_Test_Scn1aE2_Cells.tif")
blue, green, red = cv2.split(im)
                                  
green = green.astype(float)
gwn = green.copy()
for i in range(gwn.shape[0]):
    zm = green[i,:] == 0
    gwn[i,zm] = np.random.randn(np.sum(zm))*np.std(green[i,~zm]) + np.mean(green[i,~zm])
    ones = np.where(zm == 0)[0]
    fo = ones.min()
    lo = ones.max()
    gwn[i,0:fo+4] = ndi.filters.gaussian_filter1d(gwn[i,0:fo+4], 4)
    gwn[i,lo-4:] = ndi.filters.gaussian_filter1d(gwn[i,lo-4:], 4)

var = 4
X,Y = np.meshgrid(np.arange(-9.5,10.5),np.arange(-9.5,10.5))
temp = np.exp(-.5*((X**2+Y**2)/var))

xc = correlate2d(gwn, temp-temp.mean(), 'same')

thresh = xc > xc.max()/8

plt.imshow(gwn, cmap='copper_r')
plt.imshow(thresh, alpha=.1)