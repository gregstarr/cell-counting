# -*- coding: utf-8 -*-

import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import cv2


imfn = "180904_ImageJ_Test_Scn1aE2_Cells.tif"
im = cv2.imread(imfn)
blue, greenImg, redImg = cv2.split(im)
pg.setConfigOptions(imageAxisOrder='row-major')
pg.image(greenImg)

