# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 23:08:58 2018

@author: Greg
"""

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import pyqtgraph as pg
import cv2
import numpy as np
import CellCounting as cc

# Base PyQtGraph configuration
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class DrawingImage(pg.ImageItem):
    
    colors = {'r':0, 'g':1, 'b':2, 'y':[0,1]}
    
    def __init__(self, c, image=None, **kargs):
        pg.ImageItem.__init__(self, image, **kargs)
        self.kern = np.zeros((3,3,3),dtype=np.uint8)
        self.kern[:,:,DrawingImage.colors[c]] = 255
        self.x = None
        self.y = None
    
    def mouseClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setDrawKernel(self.kern, center=(1,1))
            self.drawAt(event.pos(), event)
        if event.button() == Qt.RightButton:
            self.setDrawKernel(self.kern*0, center=(1,1))
            self.drawAt(event.pos(), event)

    def mouseDragEvent(self, event):
        if event.isStart():
            if event.button() == Qt.LeftButton:
                self.setDrawKernel(self.kern, center=(1,1))
            if event.button() == Qt.RightButton:
                self.setDrawKernel(self.kern*0, center=(1,1))
        if event.button() in [Qt.LeftButton, Qt.RightButton]:
            
            pos = event.pos()
            x, y = int(np.round(pos.x())), int(np.round(pos.y()))
            self.drawAt(event.pos(), event)
            if self.x is None or self.y is None:
                self.x = x
                self.y = y
                return
            sx,sy = np.sign(x-self.x), np.sign(y-self.y)
            
            if sx == 0:
                self.x = x
                self.y = y
                if event.isFinish():
                    self.x = None
                    self.y = None
                return
            
            if sy == 0:
                self.x = x
                self.y = y
                if event.isFinish():
                    self.x = None
                    self.y = None
                return
            
            
            X,Y = np.meshgrid(np.arange(1,abs(x-self.x))*sx,np.arange(1,abs(y-self.y))*sy)
            slope = (y-self.y)/(x-self.x)
            if sx == 1 and sy == 1:
                gte = slope >= (2*Y-1)/(2*X+1)
                lte = slope <= (2*Y+1)/(2*X-1)
            elif sx == 1 and sy == -1:
                lte = slope <= (2*Y+1)/(2*X+1)
                gte = slope >= (2*Y-1)/(2*X-1)
            elif sx == -1 and sy == -1:
                lte = slope <= (2*Y-1)/(2*X+1)
                gte = slope >= (2*Y+1)/(2*X-1)
            elif sx == -1 and sy == 1:
                lte = slope <= (2*Y-1)/(2*X-1)
                gte = slope >= (2*Y+1)/(2*X+1)
                
            result = lte*gte
            pixels = np.where(result.T)
            
            xs = sx*pixels[0] + self.x
            ys = sy*pixels[1] + self.y
            for x1,y1 in zip(xs,ys):
                p = QPoint(x1,y1)
                self.drawAt(p)
            
            self.x = x
            self.y = y
            
            if event.isFinish():
                self.x = None
                self.y = None

    def hoverEvent(self, event):
        if not event.isExit():
            # the mouse is hovering over the image; make sure no other items
            # will receive left click/drag events from here. 
            event.acceptDrags(Qt.LeftButton)
            event.acceptClicks(Qt.LeftButton)
            event.acceptDrags(Qt.RightButton)
            event.acceptClicks(Qt.RightButton)
            
class HoverImage(pg.ImageItem):
    
    def __init__(self, image=None, **kargs):
        pg.ImageItem.__init__(self, image, **kargs)
        self.kern = np.ones((3,3),dtype=np.uint8) * 255
        self.setDrawKernel(self.kern, center=(1,1))

    def hoverEvent(self, event):
        if not event.isExit():
            self.image[:,:] = 0
            self.updateImage()
            self.drawAt(event.pos(), event)
        else:
            self.image[:,:] = 0
            self.updateImage()


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.current_tab = 0
        self.threshold = .12
        self.opacity = .75
        self.brushsize = 3
        self.tempsize = 10
                
        #%% Layouts        
        toplevel_layout = QVBoxLayout()
        hlayout_top = QHBoxLayout()
        hlayout_bottom = QSplitter()
        bottom_right_layout = QVBoxLayout()
        bottom_right = QWidget()
        bottom_right.setLayout(bottom_right_layout)
        toplevel_layout.addLayout(hlayout_top)
        toplevel_layout.addWidget(hlayout_bottom)
        tabs = QTabWidget()
        tabs.currentChanged.connect(self.tab_changed_callback)
        hlayout_bottom.addWidget(tabs)
        hlayout_bottom.addWidget(bottom_right)
        widget = QWidget()
        widget.setLayout(toplevel_layout)
        self.setCentralWidget(widget)
        
        #%% File Selection
        fname_label = QLabel('Image Path:')
        self.fname_entry = QLineEdit()
        browse_button = QPushButton('Browse')
        browse_button.pressed.connect(self.browse_button_callback)
        hlayout_top.addWidget(fname_label)
        hlayout_top.addWidget(self.fname_entry)
        hlayout_top.addWidget(browse_button)
        
        #%% TABS
        # red tab
        redTab = QWidget()
        redTabLayout = QHBoxLayout(redTab)
        redTab.setLayout(redTabLayout)
        tabs.addTab(redTab, "Red")
        self.redBackgroundImage = pg.ImageItem(opacity=1, border=pg.mkPen('r',width=5))
        self.redCellImage = DrawingImage('r', compositionMode=pg.QtGui.QPainter.CompositionMode_Plus, opacity=self.opacity)
        self.redHoverImage = HoverImage(opacity=self.opacity, compositionMode=pg.QtGui.QPainter.CompositionMode_Plus)
        self.redView = pg.GraphicsView(parent=redTab)
        self.redVb = pg.ViewBox(lockAspect=True)
        self.redVb.addItem(self.redBackgroundImage)
        self.redVb.addItem(self.redCellImage)
        self.redVb.addItem(self.redHoverImage)
        self.redView.setCentralItem(self.redVb)
        redTabLayout.addWidget(self.redView)
        # green tab
        greenTab = QWidget()
        greenTabLayout = QHBoxLayout(greenTab)
        greenTab.setLayout(greenTabLayout)
        tabs.addTab(greenTab, "Green")
        self.greenBackgroundImage = pg.ImageItem(opacity=1, border=pg.mkPen('g',width=5))
        self.greenCellImage = DrawingImage('g', compositionMode=pg.QtGui.QPainter.CompositionMode_Plus, opacity=self.opacity)
        self.greenHoverImage = HoverImage(opacity=self.opacity, compositionMode=pg.QtGui.QPainter.CompositionMode_Plus)
        self.greenView = pg.GraphicsView(parent=greenTab)
        self.greenVb = pg.ViewBox(lockAspect=True)
        self.greenVb.addItem(self.greenBackgroundImage)
        self.greenVb.addItem(self.greenCellImage)
        self.greenVb.addItem(self.greenHoverImage)
        self.greenView.setCentralItem(self.greenVb)
        greenTabLayout.addWidget(self.greenView)  
        # blue tab
        blueTab = QWidget()
        blueTabLayout = QHBoxLayout(blueTab)
        blueTab.setLayout(blueTabLayout)
        tabs.addTab(blueTab, "Blue")
        self.blueBackgroundImage = pg.ImageItem(opacity=1, border=pg.mkPen('b',width=5))
        self.blueView = pg.GraphicsView(parent=blueTab)
        self.blueVb = pg.ViewBox(lockAspect=True)
        self.blueVb.addItem(self.blueBackgroundImage)
        self.blueView.setCentralItem(self.blueVb)
        blueTabLayout.addWidget(self.blueView)  
        # yellow tab
        yellowTab = QWidget()
        yellowTabLayout = QHBoxLayout(yellowTab)
        yellowTab.setLayout(yellowTabLayout)
        tabs.addTab(yellowTab, "Yellow")
        self.yellowBackgroundImage = pg.ImageItem(opacity=1, border=pg.mkPen('y',width=5))
        self.yellowCellImage = DrawingImage('y', compositionMode=pg.QtGui.QPainter.CompositionMode_Plus, opacity=self.opacity)
        self.yellowHoverImage = HoverImage(opacity=self.opacity, compositionMode=pg.QtGui.QPainter.CompositionMode_Plus)
        self.yellowView = pg.GraphicsView(parent=yellowTab)
        self.yellowVb = pg.ViewBox(lockAspect=True)
        self.yellowVb.addItem(self.yellowBackgroundImage)
        self.yellowVb.addItem(self.yellowCellImage)
        self.yellowVb.addItem(self.yellowHoverImage)
        self.yellowView.setCentralItem(self.yellowVb)
        yellowTabLayout.addWidget(self.yellowView) 
        
        #%% CONTROL PANEL
        # view/edit control box
        viewControlBox = QGroupBox("View / Edit Options")
        bottom_right_layout.addWidget(viewControlBox)
        viewLayout = QVBoxLayout()
        viewControlBox.setLayout(viewLayout)
        #show/hide
        showhide_button = QPushButton("Show / Hide Cells")
        showhide_button.pressed.connect(self.showhide_button_callback)
        viewLayout.addWidget(showhide_button)
        #opacity slider
        self.opacity_label = QLabel("Cell Image Opacity: {}".format(self.opacity))
        viewLayout.addWidget(self.opacity_label)
        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setMinimum(0)
        opacity_slider.setMaximum(100)
        opacity_slider.setTickInterval(1)
        opacity_slider.setSliderPosition(int(self.opacity*100))
        opacity_slider.valueChanged.connect(self.opacity_slider_callback)
        viewLayout.addWidget(opacity_slider)
        #brush size slider
        self.brushsize_label = QLabel("Brush Size: {}".format(self.brushsize))
        viewLayout.addWidget(self.brushsize_label)
        brushsize_slider = QSlider(Qt.Horizontal)
        brushsize_slider.setMinimum(1)
        brushsize_slider.setMaximum(10)
        brushsize_slider.setTickInterval(1)
        brushsize_slider.setSliderPosition(3)
        brushsize_slider.valueChanged.connect(self.brushsize_slider_callback)
        viewLayout.addWidget(brushsize_slider)
        #single click label/unlabel
        
        
        # algorithm control box
        detectionControlBox = QGroupBox("Detection Options")
        bottom_right_layout.addWidget(detectionControlBox)
        detectionLayout = QVBoxLayout()
        detectionControlBox.setLayout(detectionLayout)
        #threshold slider
        self.threshold_label = QLabel("Detection Threshold: {}".format(self.threshold))
        detectionLayout.addWidget(self.threshold_label)
        threshold_slider = QSlider(Qt.Horizontal)
        threshold_slider.setMinimum(0)
        threshold_slider.setMaximum(100)
        threshold_slider.setTickInterval(1)
        threshold_slider.setSliderPosition(12)
        threshold_slider.valueChanged.connect(self.threshold_slider_callback)
        detectionLayout.addWidget(threshold_slider)
        #template size
        self.tempsize_label = QLabel("Template Size: {}".format(self.tempsize))
        detectionLayout.addWidget(self.tempsize_label)
        tempsize_slider = QSlider(Qt.Horizontal)
        tempsize_slider.setMinimum(1)
        tempsize_slider.setMaximum(20)
        tempsize_slider.setTickInterval(1)
        tempsize_slider.setSliderPosition(10)
        tempsize_slider.valueChanged.connect(self.tempsize_slider_callback)
        detectionLayout.addWidget(tempsize_slider)
        #template variance
        variance_label = QLabel("Template Variance:")
        detectionLayout.addWidget(variance_label)
        variance_entry = QLineEdit()
        detectionLayout.addWidget(variance_entry)
        #remove horizontal noise checkbox
        
        # run / count buttons
        runControlBox = QGroupBox("Run / Count")
        bottom_right_layout.addWidget(runControlBox)
        runControlLayout = QVBoxLayout()
        runControlBox.setLayout(runControlLayout)
        #run button
        run_button = QPushButton("Run")
        run_button.pressed.connect(self.run_button_callback)
        runControlLayout.addWidget(run_button)
        #count button
        count_button = QPushButton("Count Cells")
        count_button.pressed.connect(self.count_button_callback)
        runControlLayout.addWidget(count_button)
        
        #blue channel layers
        layersControlBox = QGroupBox("Add Layers")
        bottom_right_layout.addWidget(layersControlBox)
        layersControlLayout = QVBoxLayout()
        layersControlBox.setLayout(layersControlLayout)
        #add layers button 
        layer_button = QPushButton("Add Layers")
        layer_button.pressed.connect(self.layer_button_callback)
        layersControlLayout.addWidget(layer_button)
        
        self.setWindowTitle("Cell Counter 2000")
        self.setGeometry(100,100,1280,960)
        self.show()
        a,b = hlayout_bottom.sizes()
        hlayout_bottom.setSizes([.8*(a+b), .2*(a+b)])
        
        
    def browse_button_callback(self):
        filename, _ = QFileDialog.getOpenFileName(self,"Select Image File","./images","Tiff Files(*.tif);;All Files (*)")
        if filename is None:
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
        if self.current_tab == 0:
            if self.redImg is None:
                return
            redCells = cc.findCells(self.redImg, self.threshold)
            redCells = np.insert(np.zeros((redCells.shape[1],redCells.shape[0],2),dtype=np.uint8), 0, redCells.T, axis=2)
            self.redCellImage.setImage(redCells)
        elif self.current_tab == 1:
            if self.greenImg is None:
                return
            greenCells = cc.findCells(self.greenImg, self.threshold)
            greenCells = np.insert(np.zeros((greenCells.shape[1],greenCells.shape[0],2),dtype=np.uint8), 1, greenCells.T, axis=2)
            self.greenCellImage.setImage(greenCells)
            
    def layer_button_callback(self):
        if self.current_tab == 2:
            layers = cc.addLayers(self.blueImg)
            width = self.blueImg.shape[1]
            height = self.blueImg.shape[0]
            layer1 = layers['layer1']
            layer2_3 = layers['layer2/3']
            layer4 = layers['layer4']
            layer5 = layers['layer5']
            layer6 = layers['layer6']
            
            imLayer1 = cv2.rectangle(self.blueImg, (0,0), (width,layer1[-1]), (255, 255, 00), 3)
            imLayer2_3 = cv2.rectangle(self.blueImg, (0,layer1[-1]), (width, layer2_3[-1]), (255, 255, 00), 3)
            imLayer4 = cv2.rectangle(self.blueImg, (0,layer2_3[-1]), (width,layer4[-1]), (255, 255, 00), 3)
            imLayer5 = cv2.rectangle(self.blueImg, (0,layer4[-1]), (width,layer5[-1]), (255, 255, 00), 3)
            imLayer6 = cv2.rectangle(self.blueImg, (0,layer5[-1]), (width,height), (255, 255, 00), 3)

            self.blueBackgroundImage.setImage(imLayer1)
            self.blueBackgroundImage.setImage(imLayer2_3)
            self.blueBackgroundImage.setImage(imLayer4)
            self.blueBackgroundImage.setImage(imLayer5)
            self.blueBackgroundImage.setImage(imLayer6)
            
    def tab_changed_callback(self, index):
        self.current_tab = index
        if self.current_tab == 3:
            colocal = (self.greenCellImage.image[:,:,1] > 0) * (self.redCellImage.image[:,:,0] > 0)
            colocal = np.stack([colocal*255, colocal*255, np.zeros_like(colocal,dtype=np.uint8)], axis=2)
            self.yellowCellImage.setImage(colocal)
        
    def count_button_callback(self):
        count = cc.countCells(self.yellowCellImage.image.sum(axis=2) > 0)
        print(count)
    
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
    


if __name__ == '__main__':

    app = QApplication([])
    window = MainWindow()
    app.exec_()