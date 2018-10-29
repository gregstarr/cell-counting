import Layout
import Callbacks
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg

# Base PyQtGraph configuration
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
    
class CellCounterApp(QMainWindow, Layout.Mixin, Callbacks.Mixin):

    def __init__(self, *args, **kwargs):
        super(CellCounterApp, self).__init__(*args, **kwargs)
        
        self.current_tab = 0
        self.threshold = .2
        self.opacity = .75
        self.brushsize = 5
        self.tempsize = 10
        self.variance = 4
        self.minSize = 10
        self.maxSize = 200
        self.channels = []
        
        self.setupLayout()
        