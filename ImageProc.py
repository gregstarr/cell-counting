import numpy as np
from scipy.signal import correlate2d
import scipy.ndimage as ndi
import skimage.measure as skm
from skimage import morphology
#from skimage.io import imsave
from skimage.external.tifffile import imsave, TiffFile
import cv2
import warnings

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
    xc = correlate2d(img_w_noise, temp-temp.mean(), 'same')
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
    cells3[:20,:] = 0
    cells3[:,:20] = 0
    cells3[-20:,:] = 0
    cells3[:,-20:] = 0

    return cells3

def countCells(bin_img, l=None):
    layerNums = [] #cell count per layer array
    layerCount = 0 #cell count for current layer
    #print(len(l))
    layerValues = l.copy() #where the layers are
    y = 0
    x = 0 
    height = bin_img.shape[1]
    #print(len(layerValues))
    if layerValues is None:
        layerValues = [height]
    else:
        layerValues.append(height)
    labels = skm.label(bin_img)
    stats = skm.regionprops(labels)
    prevLayerVal = 0
    for layer in layerValues:
        #print(str(prevLayerVal)+"<"+str(layer))
        for prop in stats:
            x, y = prop.centroid
            if prevLayerVal<=y<layer:
                layerCount+=1
        #print(layerCount)
        layerNums.append(layerCount)
        layerCount = 0
        prevLayerVal = layer
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

def addLayers(blue, numLayers):
    adder = 1/(numLayers+1)
    multiplier = 0 
    layers = []
    for x in range(0, numLayers): 
        multiplier+=adder
        layer = int(multiplier*blue.shape[0])
        layers.append(layer)
        
    return layers

def saveImages(filename, channelLabels, channelNames, layerValues, thresholdValues, minValues, maxValues, tsValues, varValues ):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
    for x in range(0, len(channelLabels)):
        imsave(filename + "_"+channelNames[x]+".tif", channelLabels[x].astype(np.uint8), metadata={"layers": layerValues, "thresholdValues": thresholdValues, "minValues": minValues, "maxValues": maxValues, "tsValues": tsValues, "varValues": varValues})
