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

def addLayers(blue):
    
    avg = np.mean(blue, axis = 1)
    
    rows = len(avg)
    layer1 = []
    layer2_3 = []
    layer4 = []
    layer5 = []
    layer6 = []
    layers = []
    lowDensity = []
    midDensity = []
    highDensity = []
    
    for x in range(rows):
        if avg[x]<=30:
            lowDensity.append(x)
        elif 30 < avg[x] <= 40:
            midDensity.append(x)
        elif 40 < avg[x] <= 60:
            highDensity.append(x)     
    
    lenLow = len(lowDensity)
    lenMid = len(midDensity)
    lenHigh = len(highDensity) 
    
    for x in range(lenLow-1):
       if lowDensity[x+1] - lowDensity[x] < 15:
           layer1End = lowDensity[x+1]
       else:
           break
    
    for x in range(lenMid-1):
        if midDensity[x] > layer1End:
            if midDensity[x+1] - midDensity[x] < 15:
                layer2End = midDensity[x+1]
            else:
                break
    
    for x in range(lenHigh-1):
        if highDensity[x] > layer2End:
            if highDensity[x+1] - highDensity[x] < 70:
                layer3End = highDensity[x+1]
                layer4End = highDensity[x+2]
            else:
                break
    
    layer1 = np.arange(0, layer1End)
    layer2_3 = np.arange(layer1End+1, layer2End)
    layer4 = np.arange(layer2End+1, layer3End)
    layer5 = np.arange(layer3End+1, layer4End)
    layer6 = np.arange(layer4End+1, rows)
    return {'layer1':layer1, 'layer2/3':layer2_3, 'layer4':layer4, 'layer5':layer5, 'layer6':layer6 }
