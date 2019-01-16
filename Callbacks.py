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
import json


class Tabs(IntEnum):
    red = 0
    green = 1
    blue = 2
    layers = 3
    results = 4
    #layers = 4

class Mixin:
    def getParameters(self):
        with open('config.json') as json_data_file:
            data = json.load(json_data_file)  
        if data['dapi']=="Yes":
            self.seperateDapiFile = True
        if data['artificalLayerChannel']!= "None":
            self.artificalLayerChannel = data['artificalLayerChannel'] #Red, Green, or Blue 
        if data['blue channel']!= "None":
            self.blueChannelStatus = data['blue channel'] #either count or layers 
        self.numLayers = int(data['numLayers'])-1
        
    def browse_button_callback(self):
        self.getParameters()
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
        for c in self.channels:
            c.reset()
        blueImg, greenImg, redImg = cv2.split(im)
        if blueImg.sum() == 0:
            self.status_box.append("Selected image has no blue channel")
        else:
            self.blueChannel.setBackgroundImage(blueImg)
        self.redChannel.setBackgroundImage(redImg)
        self.greenChannel.setBackgroundImage(greenImg)
        if self.artificalLayerChannel!=None:
            if self.artificalLayerChannel=="Red":
                self.layersChannel.setBackgroundImage(redImg)
            elif self.artificalLayerChannel=="Green":
                self.layersChannel.setBackgroundImage(greenImg)
            elif self.artificalLayerChannel=="Blue":
                self.layersChannel.setBackgroundImage(blueImg)
        if self.blueChannelStatus=="Count":
             if self.current_tab in [Tabs.red, Tabs.green, Tabs.blue]:
                 self.run_button.setEnabled(True)           
        elif self.blueChannelStatus=="Layers" or self.blueChannelStatus==None:
            if self.current_tab in [Tabs.red, Tabs.green]:
                self.run_button.setEnabled(True)
    
    def browse_button_dapi_callback(self):
        self.getParameters()
        dapi_filename, _ = QFileDialog.getOpenFileName(self,"Select Dapi File","./images","Tiff Files(*.tif);;All Files (*)")
        if not os.path.isfile(dapi_filename):
            self.status_box.append("User pressed cancel or selected invalid file")
            return
        self.fname_entry_dapi.setText(dapi_filename)
                #Open Dapi Image
        dapiIm = cv2.imread(dapi_filename)
        dapi, gdapi, rdapi = cv2.split(dapiIm)
        print(dapi.shape)
        if dapi.sum()==0:
            self.status_box.append("Invalid image")
            return 
        else:
            self.layersChannel.setBackgroundImage(dapi)

    
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
        self.getParameters()
        if self.blueChannelStatus=="Layers":
            if self.current_tab == Tabs.blue and self.blueChannel.hasBackground() and not self.blueChannel.hasLayers():
                layers = self.blueChannel.addLayers(self.numLayers)
                self.redChannel.setLayers(layers)
                self.greenChannel.setLayers(layers)
                self.resultChannel.setLayers(layers)
        elif self.blueChannelStatus=="Count":
            if self.current_tab == Tabs.layers and self.layersChannel.hasBackground() and not self.layersChannel.hasLayers():
                layers = self.layersChannel.addLayers(self.numLayers)
                self.redChannel.setLayers(layers)
                self.greenChannel.setLayers(layers)
                self.blueChannel.setLayers(layers)
                self.resultChannel.setLayers(layers)
        elif self.blueChannelStatus==None:
            if self.current_tab == Tabs.layers and self.layersChannel.hasBackground() and not self.layersChannel.hasLayers():
                layers = self.layersChannel.addLayers(self.numLayers)
                self.redChannel.setLayers(layers)
                self.greenChannel.setLayers(layers)
                self.resultChannel.setLayers(layers)
        if self.blueChannelStatus=="Layers":             
            for i,layerline in enumerate(self.blueChannel.layerlines):
                layerline.sigPositionChangeFinished.connect(self.change_lines(i))
        else:
            for i,layerline in enumerate(self.layersChannel.layerlines):
                layerline.sigPositionChangeFinished.connect(self.change_lines(i))
                
    def change_lines(self, lineNum):
        self.getParameters()
        if self.blueChannelStatus=="Layers":
            bluelayerline = self.blueChannel.layerlines[lineNum]
        else:
            bluelayerline = self.layersChannel.layerlines[lineNum]
            
        def layer_function():
            if self.blueChannelStatus=="Layers" or self.blueChannelStatus==None:
                self.redChannel.updateLayers(lineNum, bluelayerline.value())
                self.greenChannel.updateLayers(lineNum, bluelayerline.value())
                self.resultChannel.updateLayers(lineNum, bluelayerline.value())
            elif self.blueChannelStatus=="Count":
                self.redChannel.updateLayers(lineNum, bluelayerline.value())
                self.greenChannel.updateLayers(lineNum, bluelayerline.value())
                self.blueChannel.updateLayers(lineNum, bluelayerline.value())
                self.resultChannel.updateLayers(lineNum, bluelayerline.value())
        return layer_function
                
    def tab_changed_callback(self, index):
        self.getParameters()
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
        elif self.blueChannelStatus=="Count" and self.current_tab == Tabs.blue and self.blueChannel.hasBackground():
            self.run_button.setEnabled(True)
        else:
            self.run_button.setEnabled(False)
        # Layer Button
        if self.blueChannelStatus=="Layers" and self.current_tab == Tabs.blue and self.blueChannel.hasBackground():
            self.layer_button.setEnabled(True)
        elif self.artificalLayerChannel != None and self.current_tab == Tabs.layers and self.layersChannel.hasBackground():
            self.layer_button.setEnabled(True)
        else:
            self.layer_button.setEnabled(False)
        # Update result channel
        if self.blueChannelStatus=="Layers" or self.artificalLayerChannel != None:
            if (self.current_tab == Tabs.results and 
                self.greenChannel.hasLabels() and 
                self.redChannel.hasLabels()):
                self.resultChannel.updateColocal()
        elif self.blueChannelStatus=="Count":
            if (self.current_tab == Tabs.results and 
                self.greenChannel.hasLabels() and 
                self.redChannel.hasLabels() and self.blueChannel.hasLabels()):
                self.resultChannel.updateColocal()

    def count_button_callback(self):
        self.getParameters()
        if self.blueChannelStatus=="Layers":           
            if not self.redChannel.hasLabels() or not self.greenChannel.hasLabels():
                self.status_box.append("Label cells before counting cells")
                return
            if not self.blueChannel.hasLayers():
                self.status_box.append('All cells assumed to be in layer 1 (press "Add Layers")')
        elif self.blueChannelStatus=="Count":
            if not self.redChannel.hasLabels() or not self.greenChannel.hasLabels() or not self.blueChannel.hasLabels():
                self.status_box.append("Label cells before counting cells")
                return
            if not self.layersChannel.hasLayers():
                self.status_box.append('All cells assumed to be in layer 1 (press "Add Layers")')
        elif self.artificalLayerChannel != None:
            if not self.redChannel.hasLabels() or not self.greenChannel.hasLabels():
                self.status_box.append("Label cells before counting cells")
                return
            if not self.layersChannel.hasLayers():
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