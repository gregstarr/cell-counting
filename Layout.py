from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ImageItems import DrawingImage, HoverImage
import pyqtgraph as pg

class Mixin:
    def setupLayout(self):
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