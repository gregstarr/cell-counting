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
    red = 3
    green = 4
    blue = 5
    yellow = 6
    allen = 1
    full = 0
    merge = 2

class Mixin:
    def browse_button_callback(self):
        filename, _ = QFileDialog.getOpenFileName(self,"Select Image File","./images","Tiff Files(*.tif);;All Files (*)")
        if not os.path.isfile(filename):
            self.status_box.append("User pressed cancel or selected invalid file")
            return
        self.fname_entry.setText(filename)
        # Open Image
        self.im = cv2.imread(filename)
        self.imBackgroundImage.setImage(self.im)
        self.imBackgroundImage.rotate(-90)
        self.imPic.setImage(self.im)
        self.imPic.rotate(-90)        
        if self.im is None:
            self.status_box.append("Invalid image")
            return
        self.blueImg, self.greenImg, self.redImg = cv2.split(self.im)
        if self.blueImg.sum() == 0:
            self.status_box.append("Selected image has no blue channel")
            self.blueImg = None
        else:
            self.blueBackgroundImage.setImage(self.blueImg.astype(np.uint8).T)
        self.redBackgroundImage.setImage(self.redImg.astype(np.uint8).T)
        self.redHoverImage.setImage(np.zeros_like(self.redImg.T, dtype=np.uint8))
        self.greenBackgroundImage.setImage(self.greenImg.astype(np.uint8).T)
        self.greenHoverImage.setImage(np.zeros_like(self.greenImg.T, dtype=np.uint8))
        if self.current_tab in [Tabs.red, Tabs.green]:
            self.run_button.setEnabled(True)

    def browse_button_allen_callback(self):
        filename, _ = QFileDialog.getOpenFileName(self,"Select Image File","./images","JPG Files(*.jpg);;All Files (*)")
        if not os.path.isfile(filename):
            self.status_box.append("User pressed cancel or selected invalid file")
            return
        self.allen_entry.setText(filename)     
        # Open Image
        self.atlasImg = cv2.imread(filename)
        if self.atlasImg is None:
            self.status_box.append("Invalid image")
            return
        self.atlasBackgroundImage.setImage(self.atlasImg)
        self.atlasBackgroundImage.rotate(-90)
        self.atlas.setImage(self.atlasImg)
        self.atlas.rotate(-90)
        
    def browse_export_button_callback(self):
        dirname = QFileDialog.getExistingDirectory(self,"Select export location","./",QFileDialog.ShowDirsOnly)
        self.export_entry.setText(dirname)
        
    def export_button_callback(self):
        if self.cell_counts is None:
            self.status_box.append("Count cells before exporting")
            return
        dir_name = self.export_entry.text()
        path, base_filename = os.path.split(self.fname_entry.text())
        base_filename, _ = os.path.splitext(base_filename)
        full_fn = os.path.join(dir_name, base_filename)
        self.status_box.append("saving " + full_fn)
        np.savetxt(full_fn+".csv", self.cell_counts, fmt='%d', delimiter=',', 
                   header="Yellow, Red, Green", comments="")
        ip.saveImages(full_fn, np.any(self.yellowCellImage.image, axis=2)*255,
                      np.any(self.redCellImage.image, axis=2)*255,
                      np.any(self.greenCellImage.image, axis=2)*255)
    
    def crop_button_callback(self):
       # g = pg.GridItem()
       # self.mergeVb.addItem(g)
        #r4 = pg.ROI([0,0], [100,100], removable=True)
        #r4.addScaleHandle([1,0], [0.5, 0.5])
        #r4.addScaleHandle([0,1], [0.5, 0.5])
        #arr = np.random.rand(100,100)
        #img4 = pg.ImageItem(arr)
        #self.mergeVb.addItem(r4)
        #img4.setParentItem(r4)
        if self.current_tab == Tabs.merge:
            width = self.atlasImg.shape[1]
            height = self.atlasImg.shape[0]
            self.atlasRegion = pg.ROI([0,0],[height, width], removable=True)
            self.atlasRegion.addScaleHandle([0,0], [.5, .5])
            self.atlasRegion.addScaleHandle([1, 1], [.5, .5])
            self.mergeVb.addItem(self.atlasRegion)
            self.atlas.setParentItem(self.atlasRegion)
            self.region =  pg.PolyLineROI([[width/2,0], [width/2,-height],[width,-height], [width,0]], closed = True)
            self.atlasVb.addItem(self.region)
    
    def crop(self):
        self.atlasBackgroundImage.setImage(self.region.getArrayRegion(self.atlasImg, self.atlasBackgroundImage))
    
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
        colocal = np.stack([(self.redCellImage.image[:,:,0] > 0)*255, 
                            (self.greenCellImage.image[:,:,1] > 0)*255, 
                            np.zeros_like(self.redCellImage.image[:,:,0])], axis=2)
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
            self.status_box.append("Label cells before counting cells")
            return
        if self.yellowCellImage.image is None:
            self.update_colocal_image()
        layerVals = []
        if self.layerlinesB is None:
            layerVals = None
            self.status_box.append("No layer lines, assuming all cells are in layer 1")
        else:
            for layerline in self.layerlinesB:
                layerVals.append(layerline.value())
        
        countY = ip.countCells(self.redCellImage.image.sum(axis=2)*self.greenCellImage.image.sum(axis=2) > 0, layerVals)
        countR = ip.countCells(self.redCellImage.image.sum(axis=2) > 0, layerVals)
        countG = ip.countCells(self.greenCellImage.image.sum(axis=2) > 0, layerVals)
        self.cell_counts = np.stack([countY, countR, countG], axis=1)
        self.status_box.append("Layer / Yellow / Red / Green")
        for i,y,r,g in zip(range(len(countY)), countY, countR, countG):
            self.status_box.append("{:<d}         {:0>3d}       {:0>3d}      {:0>3d}".format(i+1,y,r,g))
            
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
