from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import cv2
import numpy as np
import ImageProc as ip
import os
from enum import IntEnum

class Tabs(IntEnum):
    red = 0
    green = 1
    blue = 2
    yellow = 3

class Mixin:
    def browse_button_callback(self):
        filename, _ = QFileDialog.getOpenFileName(self,"Select Image File","./images","Tiff Files(*.tif);;All Files (*)")
        if not os.path.isfile(filename):
            print("User pressed cancel or selected invalid file")
            return
        self.fname_entry.setText(filename)
        # Open Image
        im = cv2.imread(filename)
        if im is None:
            print("Invalid image")
            return
        self.blueImg, self.greenImg, self.redImg = cv2.split(im)
        if self.blueImg.sum() == 0:
            print("Selected image has no blue channel")
            self.blueImg = None
        else:
            self.blueBackgroundImage.setImage(self.blueImg.astype(np.uint8).T)
        self.redBackgroundImage.setImage(self.redImg.astype(np.uint8).T)
        self.redHoverImage.setImage(np.zeros_like(self.redImg.T, dtype=np.uint8))
        self.greenBackgroundImage.setImage(self.greenImg.astype(np.uint8).T)
        self.greenHoverImage.setImage(np.zeros_like(self.greenImg.T, dtype=np.uint8))
        self.yellowBackgroundImage.setImage(im.astype(np.uint8).transpose(1,0,2))
        if self.current_tab in [Tabs.red, Tabs.green]:
            self.run_button.setEnabled(True)
        
    def run_button_callback(self):
        if self.current_tab == Tabs.red:
            if self.redImg is None:
                return
            redCells = ip.findCells(self.redImg, self.threshold)
            redCells = np.insert(np.zeros((redCells.shape[1],redCells.shape[0],2),
                                          dtype=np.uint8), 0, redCells.T, axis=2)
            self.redCellImage.setImage(redCells)
        elif self.current_tab == Tabs.green:
            if self.greenImg is None:
                return
            greenCells = ip.findCells(self.greenImg, self.threshold)
            greenCells = np.insert(np.zeros((greenCells.shape[1],greenCells.shape[0],2),
                                            dtype=np.uint8), 1, greenCells.T, axis=2)
            self.greenCellImage.setImage(greenCells)
            
    def layer_button_callback(self):
        if self.current_tab == Tabs.blue and self.blueImg is not None:
            layers = ip.addLayers(self.blueImg)
            self.layerlines = []
            for layer in layers:
                inf = pg.InfiniteLine(movable=True, angle=0)
                inf.setValue(layer)
                self.blueVb.addItem(inf)
                self.layerlines.append(inf)
                
    def update_colocal_image(self):
        colocal = (self.greenCellImage.image[:,:,1] > 0) * (self.redCellImage.image[:,:,0] > 0)
        colocal = np.stack([colocal*255, colocal*255, np.zeros_like(colocal,dtype=np.uint8)], axis=2)
        self.yellowCellImage.setImage(colocal)
                
    def tab_changed_callback(self, index):
        self.current_tab = index
        if self.current_tab == Tabs.red and self.redImg is not None:
            self.run_button.setEnabled(True)
        elif self.current_tab == Tabs.green and self.greenImg is not None:
            self.run_button.setEnabled(True)
        else:
            self.run_button.setEnabled(False)
        if self.current_tab == Tabs.blue and self.blueImg is not None:
            self.layer_button.setEnabled(True)
        else:
            self.layer_button.setEnabled(False)
        if (self.current_tab == Tabs.yellow and 
            self.greenCellImage.image is not None and 
            self.redCellImage.image is not None):
            self.update_colocal_image()
        
    def count_button_callback(self):
        if(self.redCellImage.image is None or
           self.greenCellImage.image is None):
            print("Label cells before counting cells")
            return
        if self.yellowCellImage.image is None:
            self.update_colocal_image()
        layerVals = []
        if self.layerlines is None:
            layerVals = None
            print("No layer lines, assuming all cells are in layer 1")
        else:
            for layerline in self.layerlines:
                layerVals.append(layerline.value())
        countY = ip.countCells(self.yellowCellImage.image.sum(axis=2) > 0, layerVals)
        countR = ip.countCells(self.redCellImage.image.sum(axis=2) > 0, layerVals)
        countG = ip.countCells(self.greenCellImage.image.sum(axis=2) > 0, layerVals)
    
        for x in countY:
            print(x)
            
        for x in countR:
            print(x)
            
        for x in countG:
            print(x)
            
    def threshold_slider_callback(self, value):
        self.threshold = value / 100
        self.threshold_label.setText("Detection Threshold: {}".format(self.threshold))
        
    def tempsize_slider_callback(self, value):
        self.tempsize = value
        self.tempsize_label.setText("Template Size: {}".format(self.tempsize))
    
    def opacity_slider_callback(self, value):
        self.opacity = value/100
        self.opacity_label.setText("Cell Image Opacity: {}".format(self.opacity))
        self.redCellImage.setOpacity(self.opacity)
        self.greenCellImage.setOpacity(self.opacity)
        self.yellowCellImage.setOpacity(self.opacity)
    
    def showhide_button_callback(self):
        return
    
    def brushsize_slider_callback(self, value):
        self.brushsize = value
        self.brushsize_label.setText("Brush Size: {}".format(self.brushsize))