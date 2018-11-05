import numpy as np
from scipy.signal import correlate2d
import scipy.ndimage as ndi
import skimage.measure as skm
from skimage import morphology
from skimage.io import imsave
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

def countCells(bin_img, layers=None):
    layerNums = []
    y = 0
    x = 0 
    height = bin_img.shape[0]
    if layers is None:
        layers = [height]
        
    labels = skm.label(bin_img)
    stats = skm.regionprops(labels)
    layer1 = 0
    layer2_3 = 0
    layer4 = 0
    layer5 = 0
    layer6 = 0
    
    for prop in stats:
        x, y = prop.centroid
        print(prop)
        if y <= layers[0]:
            layer1+=1
        elif layers[0] < y <= layers[1]:
            layer2_3+=1
        elif layers[1] < y <= layers[2]:
            layer4+=1
        elif layers[2] < y <= layers[3]:
            layer5+=1
        elif layers[3] < y:
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
    
    layer1End = int(.2*blue.shape[0])
    layer2_3End = int(.4*blue.shape[0])
    layer4End = int(.6*blue.shape[0])
    layer5End = int(.8*blue.shape[0])
    
    return layer1End, layer2_3End, layer4End, layer5End

def saveImages(filename, yellow, red, green):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        imsave(filename + "_yellow.png", yellow)
        imsave(filename + "_red.png", red)
        imsave(filename + "_green.png", green)