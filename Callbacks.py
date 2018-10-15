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
            redCells = ip.findCells(self.redImg, self.tempsize, self.variance, self.minSize, self.maxSize, self.threshold)
            redCells = np.insert(np.zeros((redCells.shape[1],redCells.shape[0],2),
                                          dtype=np.uint8), 0, redCells.T, axis=2)
            self.redCellImage.setImage(redCells)
        elif self.current_tab == Tabs.green:
            if self.greenImg is None:
                return
            greenCells = ip.findCells(self.greenImg, self.tempsize, self.variance, self.minSize, self.maxSize, self.threshold)
            greenCells = np.insert(np.zeros((greenCells.shape[1],greenCells.shape[0],2),
                                            dtype=np.uint8), 1, greenCells.T, axis=2)
            self.greenCellImage.setImage(greenCells)
            
    def layer_button_callback(self):
        if self.current_tab == Tabs.blue and self.blueImg is not None:
            layers = ip.addLayers(self.blueImg)
            self.layerlinesB = []
            self.layerlinesR = []
            self.layerlinesG = []
            self.layerlinesY = []
            for layer in layers:
                infB = pg.InfiniteLine(movable=True, angle=0)
                infR = pg.InfiniteLine(movable=False, angle=0)
                infG = pg.InfiniteLine(movable=False, angle=0)
                infY = pg.InfiniteLine(movable=False, angle=0)
                infB.setValue(layer)
                infR.setValue(layer)
                infG.setValue(layer)
                infY.setValue(layer)                
                self.blueVb.addItem(infB)
                self.redVb.addItem(infR)
                self.greenVb.addItem(infG)
                self.yellowVb.addItem(infY)
                self.layerlinesB.append(infB)
                self.layerlinesR.append(infR)
                self.layerlinesG.append(infG)
                self.layerlinesY.append(infY)
            self.layerlinesB[0].sigPositionChangeFinished.connect(self.change_lines(0))
            self.layerlinesB[1].sigPositionChangeFinished.connect(self.change_lines(1))
            self.layerlinesB[2].sigPositionChangeFinished.connect(self.change_lines(2))
            self.layerlinesB[3].sigPositionChangeFinished.connect(self.change_lines(3))

    def change_lines(self, lineNum):
        
        def layer_function():
            self.layerlinesR[lineNum].setValue(self.layerlinesB[lineNum].value())
            self.layerlinesG[lineNum].setValue(self.layerlinesB[lineNum].value())
            self.layerlinesY[lineNum].setValue(self.layerlinesB[lineNum].value())

        return layer_function
       
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
            for layerline in self.layerlinesB:
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

    def min_slider_callback(self, value):
        self.minSize = value
        self.min_label.setText("Minimum Cell Size: {}".format(self.minSize))
        
    def max_slider_callback(self, value):
        self.maxSize = value
        self.max_label.setText("Maximum Cell Size: {}".format(self.maxSize))
    
    def tempsize_slider_callback(self, value):
        self.tempsize = value
        self.tempsize_label.setText("Template Size: {}".format(self.tempsize))
        
    def variance_entry_callback(self):
        self.variance = float(self.variance_entry.text())
    
    def opacity_slider_callback(self, value):
        self.opacity = value/100
        self.opacity_label.setText("Cell Image Opacity: {}".format(self.opacity))
        self.redCellImage.setOpacity(self.opacity)
        self.greenCellImage.setOpacity(self.opacity)
        self.yellowCellImage.setOpacity(self.opacity)
    
    def showhide_button_callback(self):
        if self.showCells:
            if self.current_tab == Tabs.red:
                self.redCellImage.setOpacity(0)
            elif self.current_tab == Tabs.green:
                self.greenCellImage.setOpacity(0)
            elif self.current_tab == Tabs.yellow:
                self.yellowCellImage.setOpacity(0)
            self.showCells = False 

        else:
            if self.current_tab == Tabs.red:
                self.redCellImage.setOpacity(self.opacity)
            elif self.current_tab == Tabs.green:
                self.greenCellImage.setOpacity(self.opacity)
            elif self.current_tab == Tabs.yellow:
                self.yellowCellImage.setOpacity(self.opacity)
            self.showCells = True 
   
    def brushsize_slider_callback(self, value):
        self.brushsize = value
        self.brushsize_label.setText("Brush Size: {}".format(self.brushsize))
        self.redCellImage.setKernel(self.brushsize)
        self.redHoverImage.setKernel(self.brushsize)
        self.greenCellImage.setKernel(self.brushsize)
        self.greenHoverImage.setKernel(self.brushsize)
