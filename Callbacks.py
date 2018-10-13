from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import cv2
import numpy as np
import CellCounting as cc
import os

class Mixin:
    def browse_button_callback(self):
        filename, _ = QFileDialog.getOpenFileName(self,"Select Image File","./images","Tiff Files(*.tif);;All Files (*)")
        if not os.path.isfile(filename):
            return
        self.fname_entry.setText(filename)
        # Open Image
        im = cv2.imread(filename)
        self.blueImg, self.greenImg, self.redImg = cv2.split(im)
        self.redBackgroundImage.setImage(self.redImg.astype(np.uint8).T)
        self.redHoverImage.setImage(np.zeros_like(self.redImg.T, dtype=np.uint8))
        self.greenBackgroundImage.setImage(self.greenImg.astype(np.uint8).T)
        self.greenHoverImage.setImage(np.zeros_like(self.greenImg.T, dtype=np.uint8))
        self.blueBackgroundImage.setImage(self.blueImg.astype(np.uint8).T)
        self.yellowBackgroundImage.setImage(im.astype(np.uint8).transpose(1,0,2))
        self.yellowHoverImage.setImage(np.zeros_like(im[:,:,0].T, dtype=np.uint8))
        
    def run_button_callback(self):
        if self.current_tab == 0: #red
            if self.redImg is None:
                return
            redCells = cc.findCells(self.redImg, self.threshold)
            redCells = np.insert(np.zeros((redCells.shape[1],redCells.shape[0],2),dtype=np.uint8), 0, redCells.T, axis=2)
            self.redCellImage.setImage(redCells)
        elif self.current_tab == 1: #green
            if self.greenImg is None:
                return
            greenCells = cc.findCells(self.greenImg, self.threshold)
            greenCells = np.insert(np.zeros((greenCells.shape[1],greenCells.shape[0],2),dtype=np.uint8), 1, greenCells.T, axis=2)
            self.greenCellImage.setImage(greenCells)
            
    def layer_button_callback(self):
        layers = cc.addLayers(self.blueImg)
        width = self.blueImg.shape[1]
        height = self.blueImg.shape[0]
        
        self.layerlines = []
        for layer in layers:
            inf = pg.InfiniteLine(movable=True, angle=0)
            inf.setValue(layer)
            self.blueVb.addItem(inf)
            self.layerlines.append(inf)
    
                
    def tab_changed_callback(self, index):
        self.current_tab = index
        if self.current_tab == 3 and self.greenCellImage.image is not None and self.redCellImage.image is not None:
            colocal = (self.greenCellImage.image[:,:,1] > 0) * (self.redCellImage.image[:,:,0] > 0)
            colocal = np.stack([colocal*255, colocal*255, np.zeros_like(colocal,dtype=np.uint8)], axis=2)
            self.yellowCellImage.setImage(colocal)
        
    def count_button_callback(self):
        layerVals = []
        for layerline in self.layerlines:
            layerVals.append(layerline.value())
        countY = cc.countCells(self.yellowCellImage.image.sum(axis=2) > 0, layerVals)
        countR = cc.countCells(self.redCellImage.image.sum(axis=2) > 0, layerVals)
        countG = cc.countCells(self.greenCellImage.image.sum(axis=2) > 0, layerVals)
    
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
        if self.current_tab == 0:
            self.redCellImage.setOpacity(self.opacity)
        elif self.current_tab == 1:
            self.greenCellImage.setOpacity(self.opacity)
        elif self.current_tab == 3:
            self.yellowCellImage.setOpacity(self.opacity)
    
    def showhide_button_callback(self):
        return
    
    def brushsize_slider_callback(self, value):
        self.brushsize = value
        self.brushsize_label.setText("Brush Size: {}".format(self.brushsize))