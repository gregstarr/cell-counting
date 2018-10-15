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
        
        hlayout_bottom.addWidget(tabs)
        hlayout_bottom.addWidget(bottom_right)
        widget = QWidget()
        widget.setLayout(toplevel_layout)
        self.setCentralWidget(widget)
        
        #%% File Selection
        fname_label = QLabel('Image Path:')
        self.fname_entry = QLineEdit()
        browse_button = QPushButton('Browse')
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
        redView = pg.GraphicsView(parent=redTab)
        self.redVb = pg.ViewBox(lockAspect=True)
        self.redVb.addItem(self.redBackgroundImage)
        self.redVb.addItem(self.redCellImage)
        self.redVb.addItem(self.redHoverImage)
        redView.setCentralItem(self.redVb)
        redTabLayout.addWidget(redView)
        # green tab
        greenTab = QWidget()
        greenTabLayout = QHBoxLayout(greenTab)
        greenTab.setLayout(greenTabLayout)
        tabs.addTab(greenTab, "Green")
        self.greenBackgroundImage = pg.ImageItem(opacity=1, border=pg.mkPen('g',width=5))
        self.greenCellImage = DrawingImage('g', compositionMode=pg.QtGui.QPainter.CompositionMode_Plus, opacity=self.opacity)
        self.greenHoverImage = HoverImage(opacity=self.opacity, compositionMode=pg.QtGui.QPainter.CompositionMode_Plus)
        greenView = pg.GraphicsView(parent=greenTab)
        self.greenVb = pg.ViewBox(lockAspect=True)
        self.greenVb.addItem(self.greenBackgroundImage)
        self.greenVb.addItem(self.greenCellImage)
        self.greenVb.addItem(self.greenHoverImage)
        greenView.setCentralItem(self.greenVb)
        greenTabLayout.addWidget(greenView)  
        # blue tab
        blueTab = QWidget()
        blueTabLayout = QHBoxLayout(blueTab)
        blueTab.setLayout(blueTabLayout)
        tabs.addTab(blueTab, "Blue")
        self.blueBackgroundImage = pg.ImageItem(opacity=1, border=pg.mkPen('b',width=5))
        blueView = pg.GraphicsView(parent=blueTab)
        self.blueVb = pg.ViewBox(lockAspect=True)
        self.blueVb.addItem(self.blueBackgroundImage)
        blueView.setCentralItem(self.blueVb)
        blueTabLayout.addWidget(blueView)  
        # yellow tab
        yellowTab = QWidget()
        yellowTabLayout = QHBoxLayout(yellowTab)
        yellowTab.setLayout(yellowTabLayout)
        tabs.addTab(yellowTab, "Yellow")
        self.yellowBackgroundImage = pg.ImageItem(opacity=1, border=pg.mkPen('y',width=5))
        self.yellowCellImage = pg.ImageItem(compositionMode=pg.QtGui.QPainter.CompositionMode_Plus, opacity=self.opacity)
        self.yellowView = pg.GraphicsView(parent=yellowTab)
        self.yellowVb = pg.ViewBox(lockAspect=True)
        self.yellowVb.addItem(self.yellowBackgroundImage)
        self.yellowVb.addItem(self.yellowCellImage)
        self.yellowView.setCentralItem(self.yellowVb)
        yellowTabLayout.addWidget(self.yellowView) 
        
        #%% CONTROL PANEL
        # run / count buttons
        runControlBox = QGroupBox("Run / Count")
        bottom_right_layout.addWidget(runControlBox)
        runControlLayout = QVBoxLayout()
        runControlBox.setLayout(runControlLayout)
        #run button
        self.run_button = QPushButton("Run", enabled=False)
        runControlLayout.addWidget(self.run_button)
        #count button
        count_button = QPushButton("Count Cells")
        runControlLayout.addWidget(count_button)
        
        # view/edit control box
        viewControlBox = QGroupBox("View / Edit Options")
        bottom_right_layout.addWidget(viewControlBox)
        viewLayout = QVBoxLayout()
        viewControlBox.setLayout(viewLayout)
        #show/hide
        showhide_button = QPushButton("Show / Hide Cells")
        viewLayout.addWidget(showhide_button)
        #opacity slider
        self.opacity_label = QLabel("Cell Image Opacity: {}".format(self.opacity))
        viewLayout.addWidget(self.opacity_label)
        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setMinimum(0)
        opacity_slider.setMaximum(100)
        opacity_slider.setTickInterval(1)
        opacity_slider.setSliderPosition(int(self.opacity*100))
        viewLayout.addWidget(opacity_slider)
        #brush size slider
        self.brushsize_label = QLabel("Brush Size: {}".format(self.brushsize))
        viewLayout.addWidget(self.brushsize_label)
        brushsize_slider = QSlider(Qt.Horizontal)
        brushsize_slider.setMinimum(1)
        brushsize_slider.setMaximum(10)
        brushsize_slider.setTickInterval(1)
        brushsize_slider.setSliderPosition(3)
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
        detectionLayout.addWidget(threshold_slider)
        #minimum slider
        self.min_label = QLabel("Minimum Cell Size: {}".format(self.minSize))
        detectionLayout.addWidget(self.min_label)
        min_slider = QSlider(Qt.Horizontal)
        min_slider.setMinimum(0)
        min_slider.setMaximum(30)
        min_slider.setTickInterval(1)
        min_slider.setSliderPosition(10)
        detectionLayout.addWidget(min_slider)
        #maximum slider
        self.max_label = QLabel("Maximum Cell Size: {}".format(self.maxSize))
        detectionLayout.addWidget(self.max_label)
        max_slider = QSlider(Qt.Horizontal)
        max_slider.setMinimum(100)
        max_slider.setMaximum(400)
        max_slider.setTickInterval(20)
        max_slider.setSliderPosition(200)
        detectionLayout.addWidget(max_slider)
        #template size
        self.tempsize_label = QLabel("Template Size: {}".format(self.tempsize))
        detectionLayout.addWidget(self.tempsize_label)
        tempsize_slider = QSlider(Qt.Horizontal)
        tempsize_slider.setMinimum(1)
        tempsize_slider.setMaximum(20)
        tempsize_slider.setTickInterval(1)
        tempsize_slider.setSliderPosition(10)
        detectionLayout.addWidget(tempsize_slider)
        #template variance
        variance_label = QLabel("Template Variance:".format(self.variance))
        detectionLayout.addWidget(variance_label)
        self.variance_entry = QLineEdit()
        detectionLayout.addWidget(self.variance_entry)
        
        #remove horizontal noise checkbox
        
        #blue channel layers
        layersControlBox = QGroupBox("Add Layers")
        bottom_right_layout.addWidget(layersControlBox)
        layersControlLayout = QVBoxLayout()
        layersControlBox.setLayout(layersControlLayout)
        #add layers button 
        self.layer_button = QPushButton("Add Layers", enabled=False)
        layersControlLayout.addWidget(self.layer_button)
        
        browse_button.pressed.connect(self.browse_button_callback)
        showhide_button.pressed.connect(self.showhide_button_callback)
        opacity_slider.valueChanged.connect(self.opacity_slider_callback)
        brushsize_slider.valueChanged.connect(self.brushsize_slider_callback)
        threshold_slider.valueChanged.connect(self.threshold_slider_callback)
        min_slider.valueChanged.connect(self.min_slider_callback)    
        max_slider.valueChanged.connect(self.max_slider_callback)       
        tempsize_slider.valueChanged.connect(self.tempsize_slider_callback)
        self.variance_entry.returnPressed.connect(self.variance_entry_callback)
        self.run_button.pressed.connect(self.run_button_callback)
        count_button.pressed.connect(self.count_button_callback)
        self.layer_button.pressed.connect(self.layer_button_callback)
        tabs.currentChanged.connect(self.tab_changed_callback)
        
        self.setWindowTitle("Cell Counter 2000")
        self.setGeometry(100,100,1280,960)
        self.show()
        a,b = hlayout_bottom.sizes()
        hlayout_bottom.setSizes([.8*(a+b), .2*(a+b)])