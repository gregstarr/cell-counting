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
    
    colors = {'r':0, 'g':1, 'b':2}
    
    def __init__(self, c, image=None, **kargs):
        pg.ImageItem.__init__(self, image, **kargs)
        self.kern = np.zeros((3,3,3),dtype=np.uint8)
        self.kern[:,:,DrawingImage.colors[c]] = 255
    
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
            self.drawAt(event.pos(), event)

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
        
        toplevel_layout = QVBoxLayout()
        hlayout_top = QHBoxLayout()
        hlayout_bottom = QHBoxLayout()
        toplevel_layout.addLayout(hlayout_top)
        toplevel_layout.addLayout(hlayout_bottom)
        
        fname_label = QLabel('Image Path:')
        self.fname_entry = QLineEdit()
        browse_button = QPushButton('Browse')
        browse_button.pressed.connect(self.browse_button_callback)
        run_button = QPushButton('Run')
        run_button.pressed.connect(self.run_button_callback)
        hlayout_top.addWidget(fname_label)
        hlayout_top.addWidget(self.fname_entry)
        hlayout_top.addWidget(browse_button)
        hlayout_top.addWidget(run_button)
        
        tabs = QTabWidget()
        redTab = QWidget()
        redTabLayout = QHBoxLayout(redTab)
        redTab.setLayout(redTabLayout)
        tabs.addTab(redTab, "Red")
        
        self.redBackgroundImage = pg.ImageItem(opacity=1, border=pg.mkPen('r',width=5))
        self.redCellImage = DrawingImage('r', opacity=.2)
        self.redHoverImage = HoverImage(opacity=.2)
        self.redView = pg.GraphicsView(parent=redTab)
        ## Title at top
        redGraphLayout = pg.GraphicsLayout()
        redTitle = "Red Image"
        redGraphLayout.addLabel(redTitle, col=0)
        redGraphLayout.nextRow()
        self.redVb = redGraphLayout.addViewBox(lockAspect=True)
        self.redVb.addItem(self.redBackgroundImage)
        self.redVb.addItem(self.redCellImage)
        self.redVb.addItem(self.redHoverImage)
        self.redView.setCentralItem(redGraphLayout)
        redTabLayout.addWidget(self.redView)
        
        greenTab = QWidget()
        greenTabLayout = QHBoxLayout(greenTab)
        greenTab.setLayout(greenTabLayout)
        tabs.addTab(greenTab, "Green")
        
        self.greenBackgroundImage = pg.ImageItem(opacity=1, border=pg.mkPen('g',width=5))
        self.greenCellImage = DrawingImage('g', opacity=.2)
        self.greenHoverImage = HoverImage(opacity=.2)
        self.greenView = pg.GraphicsView(parent=greenTab)
        ## Title at top
        greenGraphLayout = pg.GraphicsLayout()
        greenTitle = "Green Image"
        greenGraphLayout.addLabel(greenTitle, col=0)
        greenGraphLayout.nextRow()
        self.greenVb = greenGraphLayout.addViewBox(lockAspect=True)
        self.greenVb.addItem(self.greenBackgroundImage)
        self.greenVb.addItem(self.greenCellImage)
        self.greenVb.addItem(self.greenHoverImage)
        self.greenView.setCentralItem(greenGraphLayout)
        greenTabLayout.addWidget(self.greenView)        
        
        button = QPushButton('poopies')
        
        hlayout_bottom.addWidget(tabs)
        hlayout_bottom.addWidget(button)
        
        widget = QWidget()
        widget.setLayout(toplevel_layout)
        self.setCentralWidget(widget)
        
        self.setWindowTitle("Cell Counter 2000")
        self.show()
        
        
    def browse_button_callback(self):
        filename, _ = QFileDialog.getOpenFileName(self,"Select Image File","./images","Tiff Files(*.tif);;All Files (*)")
        self.fname_entry.setText(filename)
        
    def run_button_callback(self):
        fname = self.fname_entry.text()
        greenImg, redImg, greenCells, redCells = cc.findCells(fname)
        greenCells = np.insert(np.zeros((greenCells.shape[1],greenCells.shape[0],2),dtype=np.uint8), 1, greenCells.T, axis=2)
        redCells = np.insert(np.zeros((redCells.shape[1],redCells.shape[0],2),dtype=np.uint8), 0, redCells.T, axis=2)
        self.redBackgroundImage.setImage(redImg.astype(np.uint8).T)
        self.redCellImage.setImage(redCells)
        self.redHoverImage.setImage(np.zeros_like(redImg.T, dtype=np.uint8))
        self.greenBackgroundImage.setImage(greenImg.astype(np.uint8).T)
        self.greenCellImage.setImage(greenCells)
        self.greenHoverImage.setImage(np.zeros_like(greenImg.T, dtype=np.uint8))


if __name__ == '__main__':

    app = QApplication([])
    window = MainWindow()
    app.exec_()