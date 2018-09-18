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
    
    def __init__(self, image=None, **kargs):
        pg.ImageItem.__init__(self, image, **kargs)
        self.kern = np.zeros((3,3,3),dtype=np.uint8)
        self.kern[:,:,1] = 255
    
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
        
        
        self.backgroundImage = pg.ImageItem(opacity=1, border=pg.mkPen('g',width=5))
        self.cellImage = DrawingImage(opacity=.2)
        self.hoverImage = HoverImage(opacity=.2)
        
        self.view = pg.GraphicsView(parent=self)
        l = pg.GraphicsLayout()
        self.view.setCentralItem(l)
        
        ## Title at top
        text = "Green Image"
        l.addLabel(text, col=0)
        l.nextRow()
        self.vb = l.addViewBox(lockAspect=True)
        self.vb.addItem(self.backgroundImage)
        self.vb.addItem(self.cellImage)
        self.vb.addItem(self.hoverImage)
        
        button = QPushButton('poopies')
        
        hlayout_bottom.addWidget(self.view)
        hlayout_bottom.addWidget(button)
        
        widget = QWidget()
        widget.setLayout(toplevel_layout)
        self.setCentralWidget(widget)
        
        self.setWindowTitle("Cell Counter 2000")
        self.show()
        
        
    def browse_button_callback(self):
        filename, _ = QFileDialog.getOpenFileName(self,"Select Image File", "","All Files (*);;Tiff Files(*.tiff)")
        self.fname_entry.setText(filename)
        
    def run_button_callback(self):
        fname = self.fname_entry.text()
        greenImg, redImg, greenCells, redCells = cc.findCells(fname)
        greenCells = np.insert(np.zeros((greenCells.shape[1],greenCells.shape[0],2),dtype=np.uint8), 1, greenCells.T, axis=2)
        self.backgroundImage.setImage(greenImg.astype(np.uint8).T)
        self.cellImage.setImage(greenCells)
        self.hoverImage.setImage(np.zeros_like(greenImg.T, dtype=np.uint8))


if __name__ == '__main__':

    app = QApplication([])
    window = MainWindow()
    app.exec_()