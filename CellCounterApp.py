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

# Base PyQtGraph configuration
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class DrawingImage(pg.ImageItem):
    
    def __init__(self, image=None, **kargs):
        pg.ImageItem.__init__(self, image, **kargs)
        self.kern = np.zeros((3,3,3),dtype=np.uint8)
        self.kern[:,:,1] = 255
    
    def mouseClickEvent(self, event):
        if event.button() == pg.QtCore.Qt.LeftButton:
            self.setDrawKernel(self.kern, center=(1,1))
            self.drawAt(event.pos(), event)
        if event.button() == pg.QtCore.Qt.RightButton:
            self.setDrawKernel(self.kern*0, center=(1,1))
            self.drawAt(event.pos(), event)

    def mouseDragEvent(self, event):
        if event.isStart():
            if event.button() == pg.QtCore.Qt.LeftButton:
                self.setDrawKernel(self.kern, center=(1,1))
            if event.button() == pg.QtCore.Qt.RightButton:
                self.setDrawKernel(self.kern*0, center=(1,1))
        self.drawAt(event.pos(), event)

    def hoverEvent(self, event):
        if not event.isExit():
            # the mouse is hovering over the image; make sure no other items
            # will receive left click/drag events from here. 
            event.acceptDrags(pg.QtCore.Qt.LeftButton)
            event.acceptClicks(pg.QtCore.Qt.LeftButton)
            event.acceptDrags(pg.QtCore.Qt.RightButton)
            event.acceptClicks(pg.QtCore.Qt.RightButton)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        layout = QHBoxLayout()
        
        I = cv2.imread("180904_ImageJ_Test_Scn1aE2_Cells.tif")
        b,g,r = cv2.split(I)
        img = pg.ImageItem(g.astype(np.uint8).T, opacity=1, border=pg.mkPen('g'))
        img2 = DrawingImage(np.zeros((g.shape[1], g.shape[0], 3),dtype=np.uint8), opacity=.2)
        
        self.view = pg.GraphicsView(parent=self)
        l = pg.GraphicsLayout(border=(100,100,100))
        self.view.setCentralItem(l)
        
        ## Title at top
        text = "Green Image"
        l.addLabel(text, col=0)
        l.nextRow()
        vb = l.addViewBox(lockAspect=True)
        vb.addItem(img)
        vb.addItem(img2)
        vb.autoRange()
        
        button = QPushButton('poopies')
        
        layout.addWidget(self.view)
        layout.addWidget(button)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        self.setWindowTitle("Cell Counter 2000")
        self.show()


if __name__ == '__main__':

    app = QApplication([])
    window = MainWindow()
    app.exec_()