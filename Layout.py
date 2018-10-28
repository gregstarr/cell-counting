from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ImageItems import DrawingImage, HoverImage
from ColorChannel import Channel, DetectionChannel, ResultsChannel, LayerChannel
import pyqtgraph as pg

class Mixin:
    def setupLayout(self):
         #%% Layouts        
        toplevel_layout = QVBoxLayout()
        hlayout_top1 = QHBoxLayout()
        hlayout_top2 = QHBoxLayout()
        hlayout_top3 = QHBoxLayout()
        hlayout_bottom = QSplitter()
        bottom_right_layout = QVBoxLayout()
        bottom_right = QWidget()
        bottom_right.setLayout(bottom_right_layout)
        toplevel_layout.addLayout(hlayout_top1)
        toplevel_layout.addLayout(hlayout_top2)
        toplevel_layout.addLayout(hlayout_top3)
        toplevel_layout.addWidget(hlayout_bottom)
        tabs = QTabWidget(tabPosition=QTabWidget.East, tabShape=QTabWidget.Rounded)
        
        hlayout_bottom.addWidget(tabs)
        hlayout_bottom.addWidget(bottom_right)
        widget = QWidget()
        widget.setLayout(toplevel_layout)
        self.setCentralWidget(widget)
        
        #%% File Selection
        fname_label = QLabel('Image Path:')
        self.fname_entry = QLineEdit()
        browse_button = QPushButton('Browse')
        hlayout_top1.addWidget(fname_label)
        hlayout_top1.addWidget(self.fname_entry)
        hlayout_top1.addWidget(browse_button)
        
        export_label = QLabel('Export Directory:')
        self.export_entry = QLineEdit()
        browse_export_button = QPushButton('Browse')
        hlayout_top3.addWidget(export_label)
        hlayout_top3.addWidget(self.export_entry)
        hlayout_top3.addWidget(browse_export_button)
        
        #%% TABS        
        # red tab
        redTab = QWidget()
        tabs.addTab(redTab, "Red")
        self.redChannel = DetectionChannel(redTab, 'r', name="Red")
        self.channels.append(self.redChannel)
        # green tab
        greenTab = QWidget()
        tabs.addTab(greenTab, "Green")
        self.greenChannel = DetectionChannel(greenTab, 'g', name="Green")
        self.channels.append(self.greenChannel)
        # blue tab Layers
        blueTab = QWidget()
        tabs.addTab(blueTab, "Blue")
        self.blueChannel = LayerChannel(blueTab, 'b', name="Blue")
        self.channels.append(self.blueChannel)
        # yellow tab
        yellowTab = QWidget()
        tabs.addTab(yellowTab, "Yellow")
        self.resultChannel = ResultsChannel(yellowTab, 'y', [self.redChannel, self.greenChannel], name="Yellow")
        self.channels.append(self.resultChannel)
        
        #%% CONTROL PANEL
        # run / count buttons
        runControlBox = QGroupBox("Detect / Count / Export")
        bottom_right_layout.addWidget(runControlBox)
        runControlLayout = QVBoxLayout()
        runControlBox.setLayout(runControlLayout)
        #run button
        self.run_button = QPushButton("Detect", enabled=False)
        runControlLayout.addWidget(self.run_button)
        #count button
        count_button = QPushButton("Count Cells")
        runControlLayout.addWidget(count_button)
        #export button
        export_button = QPushButton("Export")
        runControlLayout.addWidget(export_button)
        
        # view/edit control box
        viewControlBox = QGroupBox("View / Edit Options")
        bottom_right_layout.addWidget(viewControlBox)
        viewLayout = QVBoxLayout()
        viewControlBox.setLayout(viewLayout)
        
        #show/hide
        self.showhidecells_button = QCheckBox("Show Labels")
        self.showhidecells_button.setChecked(True)
        viewLayout.addWidget(self.showhidecells_button)
        self.showhidebg_button = QCheckBox("Show Background")
        self.showhidebg_button.setChecked(True)
        viewLayout.addWidget(self.showhidebg_button)
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
        threshold_slider.setSliderPosition(20)
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
        self.variance_label = QLabel("Template Variance: {}".format(self.variance))
        detectionLayout.addWidget(self.variance_label)
        self.variance_entry = QLineEdit()
        detectionLayout.addWidget(self.variance_entry)
        
        #remove horizontal noise checkbox
        #add layers button 
        self.layer_button = QPushButton("Add Layers", enabled=False)
        detectionLayout.addWidget(self.layer_button)
        
        statusBox = QGroupBox("Status")
        bottom_right_layout.addWidget(statusBox)
        statusLayout = QVBoxLayout()
        statusBox.setLayout(statusLayout)
        #add status window 
        self.status_box = QTextEdit(readOnly=True)
        statusLayout.addWidget(self.status_box)
        
        browse_button.pressed.connect(self.browse_button_callback)
        browse_export_button.pressed.connect(self.browse_export_button_callback)
        export_button.pressed.connect(self.export_button_callback)
        self.showhidecells_button.stateChanged.connect(self.showhidecells_button_callback)
        self.showhidebg_button.stateChanged.connect(self.showhidebg_button_callback)
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