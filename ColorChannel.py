import pyqtgraph as pg
from ImageItems import DrawingImage, HoverImage
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np
import ImageProc as ip
import os

class Channel:
    
    colors = {'r':0, 'g':1, 'b':2}
    nchannels = 0
    
    def __init__(self, tab, c, name=None):
        self.c = c
        if name is None:
            self.name = "Channel{}".format(Channel.nchannels)
        else:
            self.name = name
            
        self.background_img_item = pg.ImageItem(opacity=1, border=pg.mkPen(c, width=5))
        self.background_img = None
        self.layerlines = []
        
        layout = QHBoxLayout(tab)
        tab.setLayout(layout)
        self.view = pg.GraphicsView(parent=tab)
        self.viewbox = pg.ViewBox(lockAspect=True)
        self.viewbox.invertY()
        self.view.setCentralItem(self.viewbox)
        layout.addWidget(self.view)
        
        self.viewbox.addItem(self.background_img_item)
        
        Channel.nchannels += 1
        
    def setBackgroundImage(self, img, align=True, setbg=True):
        if align:
            self.background_img_item.setImage(img.T)
        else:
            self.background_img_item.setImage(img)
        if setbg:
            self.background_img = img
        
    def hasBackground(self):
        return self.background_img is not None
            
    def updateLayers(self, layer, value):
        self.layerlines[layer].setValue(value)
        
    def hidebg(self):
        pass
        
    def showbg(self):
        pass
    
    def reset(self):
        self.viewbox.removeItem(self.background_img_item)
        for l in self.layerlines:
            self.viewbox.removeItem(l)
        self.background_img_item = pg.ImageItem(opacity=1, border=pg.mkPen(self.c, width=5))
        self.background_img = None
        self.layerlines = []
        self.viewbox.addItem(self.background_img_item)
        
    def setLayers(self, layers):
        for layer in layers:
            line = pg.InfiniteLine(movable=False, angle=0)
            line.setValue(layer)
            self.viewbox.addItem(line)
            self.layerlines.append(line)
            
    def hasLayers(self):
        return len(self.layerlines) != 0
    

class LayerChannel(Channel):
    
    def setLayers(self, layers):
        for layer in layers:
            line = pg.InfiniteLine(movable=True, angle=0)
            line.setValue(layer)
            self.viewbox.addItem(line)
            self.layerlines.append(line)
            
    def addLayers(self):
        layers = ip.addLayers(self.background_img)
        self.setLayers(layers)
        return layers
        
        
class DetectionChannel(Channel):
    
    def __init__(self, tab, c, name=None):
        super().__init__(tab, c, name)
        
        self.label_img_item = DrawingImage(c, compositionMode=pg.QtGui.QPainter.CompositionMode_Plus, opacity=1)
        self.hover_img_item = HoverImage(opacity=1, compositionMode=pg.QtGui.QPainter.CompositionMode_Plus)
        self.histogram_item = pg.HistogramLUTItem()
        self.histogram_item.setImageItem(self.background_img_item)
        self.histogram_item.setMinimumHeight(500)
        self.histogram_item.setHistogramRange(0, 300)
        self.histogram_state = None
        
        self.viewbox.addItem(self.label_img_item)
        self.viewbox.addItem(self.hover_img_item)
        
        self.view.addItem(self.histogram_item)
        
    def reset(self):
        super().reset()
        self.viewbox.removeItem(self.hover_img_item)
        self.viewbox.removeItem(self.label_img_item)
        self.view.removeItem(self.histogram_item)
        self.label_img_item = DrawingImage(self.c, compositionMode=pg.QtGui.QPainter.CompositionMode_Plus, opacity=1)
        self.hover_img_item = HoverImage(opacity=1, compositionMode=pg.QtGui.QPainter.CompositionMode_Plus)
        self.histogram_item = pg.HistogramLUTItem()
        self.histogram_item.setImageItem(self.background_img_item)
        self.histogram_item.setMinimumHeight(500)
        self.histogram_item.setHistogramRange(0, 300)
        self.histogram_state = None
        self.viewbox.addItem(self.label_img_item)
        self.viewbox.addItem(self.hover_img_item)
        self.view.addItem(self.histogram_item)
        
    def showbg(self):
        self.setBackgroundImage(self.background_img, setbg=False)
        if self.histogram_state is not None:
            self.histogram_item.restoreState(self.histogram_state)

    def hidebg(self):
        self.histogram_state = self.histogram_item.saveState()
        self.setBackgroundImage(np.zeros_like(self.background_img), setbg=False)
        
    @property
    def label_img(self):
        if self.label_img_item.image is None:
            return None
        return self.label_img_item.image[:,:,super().colors[self.c]]
        
    def setBackgroundImage(self, img, setbg=True):
        super().setBackgroundImage(img, setbg=setbg)
        self.hover_img_item.setImage(np.zeros_like(img.T, dtype=np.uint8))
        self.histogram_item.setLevels(0, 255)
        
    def getLabels(self):
        im = np.any(self.label_img_item.image, axis=2)*255
        return im.T
        
    def runDetection(self, ts, var, mins, maxs, th):
        labels = ip.findCells(self.background_img, ts, var, mins, maxs, th)
        im = np.zeros((labels.shape[1], labels.shape[0], 3))
        im[:,:,super().colors[self.c]] = labels.T
        self.label_img_item.setImage(im)
        
    def hasLabels(self):
        return self.label_img is not None
    
    def countCells(self, layerVals):
        counts = ip.countCells(self.label_img > 0, layerVals)
        return counts
    
    def set_brushsize(self, value):
        self.label_img_item.setKernel(value)
        self.hover_img_item.setKernel(value)
        
    
class ResultsChannel(Channel):
    
    def __init__(self, tab, c, channels, name=None):
        super().__init__(tab, c, name)
        self.channels = channels
        self.cell_counts = None
        
    def hasCellCounts(self):
        return self.cell_counts is not None
    
    def getLabels(self):
        im = (self.background_img_item.image > 0) * 255
        return im.T
    
    def updateColocal(self):
        colocal = np.stack([c.label_img for c in self.channels]+[np.zeros_like(self.channels[0].label_img)], axis=2) * 255
        self.background_img_item.setImage(colocal)
        
    def countCells(self):
        self.updateColocal()
        if len(self.layerlines) == 0:
            layerVals = None
        else:
            layerVals = [layer.value() for layer in self.layerlines]
        counts = [ip.countCells(self.background_img_item.image > 0, layerVals)]
        for chan in self.channels:
            counts.append(chan.countCells(layerVals))
        self.cell_counts = np.stack(counts, axis=1)
        
        string = "Layer / {}".format(self.name)
        string += "".join(['/ '+c.name for c in self.channels])
        string += '\n'
        if layerVals is None:
            string += "{:<d}         {:0>3d}       {:0>3d}      {:0>3d}".format(1, self.cell_counts[0,0], self.cell_counts[0,1], self.cell_counts[0,2])
        else:
            for i in range(self.cell_counts.shape[0]):
                string += "{:<d}         {:0>3d}       {:0>3d}      {:0>3d}\n".format(i+1, self.cell_counts[i,0], self.cell_counts[i,1], self.cell_counts[i,2])
                
        return string
    
    def exportData(self, export_text, fname_text):
        ##TODO: Make more reconfigurable
        
        
        dir_name = export_text
        path, base_filename = os.path.split(fname_text)
        base_filename, _ = os.path.splitext(base_filename)
        full_fn = os.path.join(dir_name, base_filename)
        np.savetxt(full_fn+".csv", self.cell_counts, fmt='%d', delimiter=',', 
                   header=self.name+"".join([', '+c.name for c in self.channels]), comments="")
        ip.saveImages(full_fn, self.getLabels(), self.channels[0].getLabels(), self.channels[1].getLabels())
        
        return full_fn