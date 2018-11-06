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
    
    layerNums = [0]*5
    labels = skm.label(bin_img)
    stats = skm.regionprops(labels)
    
    if layers is not None:
        processed_layers = preprocessLayers(layers, bin_img.shape)
        print(processed_layers)
    else:
        layerNums[0] = len(labels)
        return layerNums
    
    for prop in stats:
        x, y = prop.centroid
        for i in range(len(processed_layers)):
            if aboveLayer([x,y], processed_layers[i]):
                layerNums[i] += 1
                break
        else:
            layerNums[-1] += 1

    return layerNums

def aboveLayer(point, layer):
    ## TODO: Make this work for all cells at once
    for i in range(layer.shape[0]-1):
        if point[0] >= layer[i,0] and point[0] <layer[i+1,0]:
            break
    if point[1] <= layer[i,1] and point[1] <= layer[i+1,1]:
        return True
    if point[1] > layer[i,1] and point[1] > layer[i+1,1]:
        return False
    yt = (layer[i+1,1] - layer[i,1])*(point[0]-layer[i,0]) / (layer[i+1,0]-layer[i,0]) + layer[i,1]
    if point[1] <= yt:
        return True
    return False

def preprocessLayers(layers, imshape):
    ## TODO: Make this check for layer intersections that occur within image
    new_layers = []
    for layer in layers[::-1]:
        #Left Side
        ax = -1*layer[0,0]/(layer[0,0]-layer[1,0])
        ay = (imshape[0]-layer[0,1])/(layer[0,1]-layer[1,1])
        if abs(ax) < abs(ay):
            firstpt = np.array([0, layer[0,1] + ax*(layer[0,1]-layer[1,1])])
        else:
            firstpt = np.array([layer[0,0] + ay*(layer[0,0]-layer[1,0]), imshape[0]])
            
        #Right Side    
        ax = (imshape[1]-layer[-1,0])/(layer[-1,0]-layer[-2,0])
        ay = (imshape[0]-layer[-1,1])/(layer[-1,1]-layer[-2,1])
        if abs(ax) < abs(ay):
            lastpt = np.array([imshape[1], layer[-1,1] + ax*(layer[-1,1]-layer[-2,1])])
        else:
            lastpt = np.array([layer[-1,0] + ay*(layer[-1,0]-layer[-2,0]), imshape[0]])
            
        if len(new_layers) > 0:
            firstpt[1] = min(firstpt[1], new_layers[-1][0,1])
            firstpt[0] = min(firstpt[0], new_layers[-1][0,0])
            lastpt[1] = min(lastpt[1], new_layers[-1][-1,1])
            lastpt[0] = max(lastpt[0], new_layers[-1][-1,0])
        
        new_layers.append(np.concatenate([firstpt[None,:], layer, lastpt[None,:]], axis=0))
        
    return new_layers[::-1]
        
    
        
    
    

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