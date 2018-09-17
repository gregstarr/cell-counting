from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import cv2

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


## Create image item
I = cv2.imread("180904_ImageJ_Test_Scn1aE2_Cells.tif")
b,g,r = cv2.split(I)
img = pg.ImageItem(g.astype(np.uint8).T, opacity=1, border=pg.mkPen('g'))
img2 = DrawingImage(np.zeros((g.shape[1], g.shape[0], 3),dtype=np.uint8), opacity=.2)

app = QtGui.QApplication([])
view = pg.GraphicsView(background=pg.mkColor('w'))
l = pg.GraphicsLayout(border=(100,100,100))
view.setCentralItem(l)
view.show()
view.setWindowTitle('pyqtgraph example: GraphicsLayout')
view.resize(800,600)

## Title at top
text = "Green Image"
l.addLabel(text, col=0)
l.nextRow()
vb = l.addViewBox(lockAspect=True)
vb.addItem(img)
vb.addItem(img2)
vb.autoRange()

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()