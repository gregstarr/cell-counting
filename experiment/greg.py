# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 14:41:32 2018

@author: gqs0108
"""

import numpy as np
from matplotlib import pyplot as plt
import cv2
import scipy.ndimage as ndi
import scipy.signal as ssi
import skimage.measure as skm
from skimage.feature import peak_local_max
from skimage.morphology import watershed

im = cv2.imread('180904_ImageJ_Test_Scn1aE2_Cells.tif')
blue, green, red = cv2.split(im)

green = green.astype(float)
proto1 = green[356:380,450:470]
proto2 = green[770:785,464:479]
proto3 = green[646:661,378:391]
proto4 = green[425:438,279:297]
proto5 = green[356:371,637:647]
proto6 = green[530:545,274:289]
proto7 = green[576:592,335:350]
proto8 = green[682:695,479:491]
protos = [proto1,proto2,proto3,proto4,proto5,proto6,proto7,proto8]
xcs = []

for proto in protos:
    xcs.append(ssi.correlate2d(green, proto,'same'))
xc = np.mean(xcs)

gwn = green.copy()
for i in range(gwn.shape[0]):
    zm = green[i,:] == 0
    gwn[i,zm] = np.random.randn(np.sum(zm))*np.std(green[i,~zm]) + np.mean(green[i,~zm])
    ones = np.where(zm == 0)[0]
    fo = ones.min()
    lo = ones.max()
    gwn[i,0:fo+4] = ndi.filters.gaussian_filter1d(gwn[i,0:fo+4], 4)
    gwn[i,lo-4:] = ndi.filters.gaussian_filter1d(gwn[i,lo-4:], 4)


xc = ssi.correlate2d(gwn, proto-proto.mean(), 'valid')

bxc = xc > xc.max()/8
labels,n = ndi.label(bxc)
props = skm.regionprops(labels)
bxc2 = bxc.copy()
for prop in props:
    if prop.area > 250 or prop.eccentricity < .4:
        bxc2[prop.coords[:,0],prop.coords[:,1]] = 0

distance = ndi.distance_transform_edt(bxc2)
local_maxi = peak_local_max(distance, indices=False, num_peaks=len(props), min_distance=10, labels=bxc2)
markers = ndi.label(local_maxi)[0]
labels2 = watershed(-distance, markers, mask=bxc2)
props2 = skm.regionprops(labels2)

plt.figure()
plt.imshow(green)
plt.figure()
plt.imshow(gwn)
plt.figure()
plt.imshow(xc)
plt.figure()
plt.imshow(green)
plt.imshow(ndi.interpolation.shift(bxc2, [3,3]), alpha=.1)
plt.figure()
plt.imshow(bxc)
for p in props:
    mr,mc,mar,mac = p.bbox
    plt.plot([mc,mc],[mr,mar])
    plt.plot([mc,mac],[mr,mr])
    plt.plot([mc,mac],[mar,mar])
    plt.plot([mac,mac],[mr,mar])
plt.figure()
plt.imshow(bxc2)
