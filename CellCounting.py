# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 18:48:03 2018

@author: Greg
"""

import numpy as np
from scipy.signal import correlate2d
import scipy.ndimage as ndi
import skimage.measure as skm
import cv2

def findCells(img, threshold=.125):
    
    # Add noise to blank pixels
    img_w_noise = addHorizontalNoise(img)
    
    # create gaussian image cell template
    var = 4
    X,Y = np.meshgrid(np.arange(-9.5,10.5),np.arange(-9.5,10.5))
    temp = np.exp(-.5*((X**2+Y**2)/var))
    
    # correlate with green image
    xc = correlate2d(img_w_noise, temp-temp.mean(), 'valid')
    xc = ndi.interpolation.shift(xc, [temp.shape[1]/2,temp.shape[0]/2])
    
    # threshold
    cells = xc > xc.max() * threshold
    
    return cells

def countCells(bin_img):
    labels,n = ndi.label(bin_img)
    return n

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