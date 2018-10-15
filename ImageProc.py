import numpy as np
from scipy.signal import correlate2d
import scipy.ndimage as ndi
import skimage.measure as skm
from skimage import morphology
import cv2

def findCells(img, size, variance, minSize, maxSize, threshold=.125):
    
    # Add noise to blank pixels
    img_w_noise = addHorizontalNoise(img)
    
    # create gaussian image cell template
    var = variance
    low = -(size-0.5)   
    high = size+0.5
    X,Y = np.meshgrid(np.arange(low, high), np.arange(low, high))
    temp = np.exp(-.5*((X**2+Y**2)/var))
    
    # correlate with green image
    xc = correlate2d(img_w_noise, temp-temp.mean(), 'valid')
    xc = ndi.interpolation.shift(xc, [temp.shape[1]/2,temp.shape[0]/2])
    
    # threshold
    cells = xc > xc.max() * threshold
    
    cells2 = morphology.remove_small_objects(cells, min_size=minSize, connectivity=2)
    cells2=cells2.astype(np.uint8)
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(cells2, connectivity=8)
    sizes = stats[1:, -1]; nb_components = nb_components - 1 
    cells3 = np.zeros((output.shape))
    for i in range(0, nb_components):
        if sizes[i] <= maxSize:
            cells3[output == i + 1] = 255
    cells3=cells3.astype(np.uint8)


    return cells3

def countCells(bin_img, layers=None):
    #labels,n = ndi.label(bin_img)
    layerNums = []
    y = 0
    x = 0 
    width = bin_img.shape[1]
    height = bin_img.shape[0]
    if layers is None:
        layers = [height]
   # for layer in layers:
   #     layer_img = bin_img[y:y+layer, x:width]
   #     labels, n= ndi.label(layer_img)
  #      layerNums.append(n)
  #      y = y+layer
  #  layer_img = bin_img[y:height, x:width]
  #  labels, n= ndi.label(layer_img)
  #  layerNums.append(n)
    labels = skm.label(bin_img)
    stats = skm.regionprops(labels)
    layer1 = 0
    layer2_3 = 0
    layer4 = 0
    layer5 = 0
    layer6 = 0
    
    for prop in stats:
        y, x = prop.centroid
        if 0<y<=layers[0]:
            layer1+=1
        elif layers[0]<y<=layers[1]:
            layer2_3+=1
        elif layers[1]<y<=layers[2]:
            layer4+=1
        elif layers[2]<y<=layers[3]:
            layer5+=1
        elif layers[3]<y<=height:
            layer6+=1
    
    layerNums.append(layer1)
    layerNums.append(layer2_3)
    layerNums.append(layer4)
    layerNums.append(layer5)
    layerNums.append(layer6)

    return layerNums

def addHorizontalNoise(image):
    
    image = image.astype(float)
    image_with_noise = image.copy()
    for i in range(image.shape[0]):
        zm = image[i,:] == 0
        if np.all(zm):
            continue
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
                layer2_3End = midDensity[x+1]
            else:
                break
    
    for x in range(lenHigh-1):
        if highDensity[x] > layer2_3End:
            if highDensity[x+1] - highDensity[x] < 70:
                layer4End = highDensity[x+1]
                layer5End = highDensity[x+2]
            else:
                break
    
    return layer1End, layer2_3End, layer4End, layer5End
