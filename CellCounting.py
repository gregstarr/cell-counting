# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 18:48:03 2018

@author: Greg
"""

import numpy as np
from scipy.signal import correlate2d
import scipy.ndimage as ndi
import cv2

def findCells(imageFile):
    
    # Open Image
    im = cv2.imread(imageFile)
    blue, greenImg, redImg = cv2.split(im)
    
    # Add noise to blank pixels
    gwn = addHorizontalNoise(greenImg)
    rwn = addHorizontalNoise(redImg)
    
    # create gaussian image cell template
    var = 4
    X,Y = np.meshgrid(np.arange(-9.5,10.5),np.arange(-9.5,10.5))
    temp = np.exp(-.5*((X**2+Y**2)/var))
    
    # correlate with green image
    gxc = correlate2d(gwn, temp-temp.mean(), 'valid')
    gxc = ndi.interpolation.shift(gxc, [temp.shape[1]/2,temp.shape[0]/2])
    rxc = correlate2d(rwn, temp-temp.mean(), 'valid')
    rxc = ndi.interpolation.shift(rxc, [temp.shape[1]/2,temp.shape[0]/2])
    
    # threshold
    greenCells = gxc > gxc.max()/8
    redCells = rxc > rxc.max()/8
    
    return greenImg, redImg, greenCells, redCells

def addHorizontalNoise(image):
    
    image = image.astype(float)
    image_with_noise = image.copy()
    for i in range(image.shape[0]):
        zm = image[i,:] == 0
        image_with_noise[i,zm] = np.random.randn(np.sum(zm)) * np.std(image[i,~zm]) + np.mean(image[i,~zm])
        ones = np.where(zm == 0)[0]
        fo = ones.min()
        lo = ones.max()
        image_with_noise[i,0:fo+4] = ndi.filters.gaussian_filter1d(image_with_noise[i,0:fo+4], 4)
        image_with_noise[i,lo-4:] = ndi.filters.gaussian_filter1d(image_with_noise[i,lo-4:], 4)
        
    return image_with_noise