from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import cv2
import numpy as np
import ImageProc as ip
import os
from enum import IntEnum
from ColorChannel import DetectionChannel

class Tabs(IntEnum):
    red = 0
    green = 1
    blue = 2
    yellow = 3

class Mixin:
    def browse_button_callback(self):
        filename, _ = QFileDialog.getOpenFileName(self,"Select Image File","./images","Tiff Files(*.tif);;All Files (*)")
        if not os.path.isfile(filename):
            self.status_box.append("User pressed cancel or selected invalid file")
            return
        self.fname_entry.setText(filename)
        # Open Image
        im = cv2.imread(filename)   
        if im is None:
            self.status_box.append("Invalid image")
            return
        blueImg, greenImg, redImg = cv2.split(im)
        if blueImg.sum() == 0:
            self.status_box.append("Selected image has no blue channel")
        else:
            self.blueChannel.setBackgroundImage(blueImg)
        self.redChannel.setBackgroundImage(redImg)
        self.greenChannel.setBackgroundImage(greenImg)
        if self.current_tab in [Tabs.red, Tabs.green]:
            self.run_button.setEnabled(True)
        
    def browse_export_button_callback(self):
        dirname = QFileDialog.getExistingDirectory(self,"Select export location","./",QFileDialog.ShowDirsOnly)
        self.export_entry.setText(dirname)
        
    def export_button_callback(self):
        if not self.resultChannel.hasCellCounts():
            self.status_box.append("Count cells before exporting")
            return
        full_fn = self.resultChannel.exportData(self.export_entry.text(), self.fname_entry.text())
        self.status_box.append("saving " + full_fn)
    
    def run_button_callback(self):
        if not self.channels[self.current_tab].hasBackground():
            self.status_box.append("Choose image before running")
            return
        self.channels[self.current_tab].runDetection(self.tempsize, self.variance, self.minSize, self.maxSize, self.threshold)
        
            
    def layer_button_callback(self):
        if self.current_tab == Tabs.blue and self.blueChannel.hasBackground():
            layers = self.blueChannel.addLayers()
            self.redChannel.setLayers(layers)
            self.greenChannel.setLayers(layers)
            self.resultChannel.setLayers(layers)
            
            for i,layerline in enumerate(self.blueChannel.layerlines):
                layerline.sigPositionChangeFinished.connect(self.change_lines(i))

    def change_lines(self, lineNum):
        bluelayerline = self.blueChannel.layerlines[lineNum]
        def layer_function():
            self.redChannel.updateLayers(lineNum, bluelayerline.value())
            self.greenChannel.updateLayers(lineNum, bluelayerline.value())
            self.resultChannel.updateLayers(lineNum, bluelayerline.value())

        return layer_function
                
    def tab_changed_callback(self, index):
        self.current_tab = index
        channel = self.channels[self.current_tab]
        if isinstance(channel, DetectionChannel):
            channel.set_brushsize(self.brushsize)
            if self.showhidebg_button.isChecked():
                channel.showbg()
            else:
                channel.hidebg()
            if self.showhidecells_button.isChecked():
                channel.label_img_item.setVisible(True)
            else:
                channel.label_img_item.setVisible(False)
                
        # Run Button
        if self.current_tab == Tabs.red and self.redChannel.hasBackground():
            self.run_button.setEnabled(True)
        elif self.current_tab == Tabs.green and self.greenChannel.hasBackground():
            self.run_button.setEnabled(True)
        else:
            self.run_button.setEnabled(False)
        # Layer Button
        if self.current_tab == Tabs.blue and self.blueChannel.hasBackground():
            self.layer_button.setEnabled(True)
        else:
            self.layer_button.setEnabled(False)
        # Update Yellow channel
        if (self.current_tab == Tabs.yellow and 
            self.greenChannel.hasLabels() and 
            self.redChannel.hasLabels()):
            self.resultChannel.updateColocal()
        
        
    def count_button_callback(self):
        if not self.redChannel.hasLabels() or not self.greenChannel.hasLabels():
            self.status_box.append("Label cells before counting cells")
            return
        
        if not self.blueChannel.hasLayers():
            self.status_box.append('All cells assumed to be in layer 1 (press "Add Layers")')
        
        result_text = self.resultChannel.countCells()
        self.status_box.append(result_text)
        
            
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
        self.variance_label.setText("Template Variance: {}".format(self.variance))
    
    def showhidecells_button_callback(self, state):
        channel = self.channels[self.current_tab]
        if isinstance(channel, DetectionChannel):
            if state:
                channel.label_img_item.setVisible(True)
            else:
                channel.label_img_item.setVisible(False)
            
    def showhidebg_button_callback(self, state):
        if state:
            self.channels[self.current_tab].showbg()
        else:
            self.channels[self.current_tab].hidebg()
   
    def brushsize_slider_callback(self, value):
        self.brushsize = value
        self.brushsize_label.setText("Brush Size: {}".format(self.brushsize))
        self.channels[self.current_tab].set_brushsize(value)
