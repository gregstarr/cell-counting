from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ImageItems import DrawingImage, HoverImage
from ColorChannel import Channel, DetectionChannel, ResultsChannel, LayerChannel
import pyqtgraph as pg
import json

class Mixin:
    def setup(self):        
        self.pageList = QListWidget()
        self.pageList.insertItem(0, 'set up')
        self.pageList.insertItem(1, 'detection')
        self.first_page = QWidget()
        self.detection_page = QWidget()
        
        self.one_page()
        self.d_page()
        
        self.stacked_pages = QStackedWidget(self)
        
        self.stacked_pages.addWidget(self.first_page)
        self.stacked_pages.addWidget(self.detection_page)
        
        hbox = QSplitter()
        hbox.addWidget(self.pageList)
        hbox.addWidget(self.stacked_pages)

        hbox.setCollapsible(0, False)
        hbox.setCollapsible(1, False)
        hbox.setSizes([1, 1499])

        #print(hbox.sizes())


        #widget = QWidget()
        #widget.setLayout(hbox)
        self.setCentralWidget(hbox)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10000)
        #sizePolicy.setHeightForWidth(self.pageList.sizePolicy().hasHeightForWidth())
     
        self.pageList.setSizePolicy(sizePolicy)

        self.pageList.currentRowChanged.connect(self.display)
        self.setWindowTitle("Cell Counter 2000")
        self.setGeometry(0,0,1500,self.minimumHeight())
        #self.resize(self.minimumHeight());

        self.show()
        
        #self.pageList.setSizes([10, 10])


    def one_page(self):
        one_layout = QHBoxLayout()
        right_box = QGroupBox("Settings")
        one_layout.addWidget(right_box)
        right_layout = QVBoxLayout()
        right_box.setLayout(right_layout)
        
        sub_top_box = QGroupBox("Image Description")
        right_layout.addWidget(sub_top_box)
        sub_top_layout = QVBoxLayout()
        sub_top_box.setLayout(sub_top_layout)

        sub_layout_1 = QHBoxLayout()
        sub_layout_2 = QHBoxLayout()
        
        detection_channels_label = QLabel('Choose cell detection color channels and add color channel label: ')   
        red_dc = QCheckBox("Red")
        red_dc_label = QLineEdit()
        green_dc = QCheckBox("Green")
        green_dc_label = QLineEdit()
        blue_dc = QCheckBox("Blue")
        blue_dc_label = QLineEdit()

        layers_channel_label = QLabel("Choose layers color channel: ")
        red_lc = QCheckBox("Red")
        green_lc = QCheckBox("Green")
        blue_lc = QCheckBox("Blue")
        separate_lc = QCheckBox("Separate Dapi Image")
        
        sub_layout_1.addWidget(red_dc)
        sub_layout_1.addWidget(red_dc_label)
        sub_layout_1.addWidget(green_dc)
        sub_layout_1.addWidget(green_dc_label)
        sub_layout_1.addWidget(blue_dc)
        sub_layout_1.addWidget(blue_dc_label)

        sub_layout_2.addWidget(red_lc)
        sub_layout_2.addWidget(green_lc)
        sub_layout_2.addWidget(blue_lc)
        sub_layout_2.addWidget(separate_lc)
        
        sub_top_layout.addWidget(detection_channels_label)
        sub_top_layout.addLayout(sub_layout_1)
        sub_top_layout.addWidget(layers_channel_label)
        sub_top_layout.addLayout(sub_layout_2)
        
        sub_mid_box = QGroupBox("Number of Layers")
        right_layout.addWidget(sub_mid_box)
        sub_mid_layout = QHBoxLayout()
        sub_mid_box.setLayout(sub_mid_layout)
        
        numLayers_label = QLabel("Enter Number of Layers")
        numLayers = QLineEdit()
        
        sub_mid_layout.addWidget(numLayers_label)
        sub_mid_layout.addWidget(numLayers)
        
        sub_bottom_box = QGroupBox("Colocalization")
        right_layout.addWidget(sub_bottom_box)
        sub_bottom_layout = QHBoxLayout()
        sub_bottom_box.setLayout(sub_bottom_layout)
        
        combo_label = QLabel("Check to Count All Combinations: ")
        combo_checkBox = QCheckBox('')
        
        sub_bottom_layout.addWidget(combo_label)
        sub_bottom_layout.addWidget(combo_checkBox)
        
        self.submit_button = QPushButton('submit')
        right_layout.addWidget(self.submit_button)
        
        bottom_space_box = QGroupBox(" ")
        right_layout.addWidget(bottom_space_box)
        bottom_space_layout = QHBoxLayout()
        bottom_space_box.setLayout(bottom_space_layout)
        empty_space = QLabel("                                                         ")
        bottom_space_layout.addWidget(empty_space)

        one_layout.addWidget(empty_space)
        one_layout.addWidget(empty_space)
        one_layout.addWidget(empty_space)

        self.first_page.setLayout(one_layout)
      #  self.submit_button.pressed.connect(self.openDetectionPage)
       # print(self.stacked_pages.currentIndex())
       # self.show()

    def d_page(self):
        with open('config.json') as json_data_file:
            data = json.load(json_data_file)
        if data['blue channel']== "Layers":
            self.addLayersBlue = True
        elif data['blue channel']=="Count":
            self.countBlue = True
        elif data['blue channel']=="None":
            self.addBlueChannel = False
        if data['dapi']=="Yes":
            self.addLayersTab = True
        if data['artificalLayerChannel']!="None":
            self.artificalLayerChannel = data['artificalLayerChannel']
        elif data['artificalLayerChannel']=="None":
            self.artificalLayerChannel = "None"

         #%% Layouts        
        toplevel_layout = QVBoxLayout()
        hlayout_top1 = QHBoxLayout()
        hlayout_top2 = QHBoxLayout()
        hlayout_top3 = QHBoxLayout()
        hlayout_bottom = QSplitter()
        bottom_right_layout = QVBoxLayout()
        bottom_right = QWidget()
        bottom_right.setLayout(bottom_right_layout)
        tabs = QTabWidget(tabPosition=QTabWidget.East, tabShape=QTabWidget.Rounded)

        toplevel_layout.addLayout(hlayout_top1)
        toplevel_layout.addLayout(hlayout_top2)
        toplevel_layout.addLayout(hlayout_top3)
        #hlayout_bottom.addWidget(bottom_right)
        hlayout_bottom.addWidget(tabs)
        #print(hlayout_bottom.indexOf(tabs))
        hlayout_bottom.addWidget(bottom_right)
       # print(hlayout_bottom.indexOf(bottom_right))
        hlayout_bottom.setCollapsible(0, False)
        hlayout_bottom.setCollapsible(1, False)
        hlayout_bottom.setSizes([1499, 1])
        print(hlayout_bottom.sizes())

        toplevel_layout.addWidget(hlayout_bottom)
        self.detection_page.setLayout(toplevel_layout)
        
        #%% File Selection
        fname_label = QLabel('Image Path:')
        self.fname_entry = QLineEdit()
        browse_button = QPushButton('Browse')
        hlayout_top1.addWidget(fname_label)
        hlayout_top1.addWidget(self.fname_entry)
        hlayout_top1.addWidget(browse_button)

        if self.addLayersTab:
            fname_label_dapi = QLabel('Dapi Path:')
            self.fname_entry_dapi = QLineEdit()
            browse_button_dapi = QPushButton('Browse')
            hlayout_top2.addWidget(fname_label_dapi)
            hlayout_top2.addWidget(self.fname_entry_dapi)
            hlayout_top2.addWidget(browse_button_dapi)

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
        # blue tab/Layers
        if self.addLayersBlue:
            blueTab = QWidget()
            tabs.addTab(blueTab, "Layers")
            self.blueChannel = LayerChannel(blueTab, 'b', name="Layers")
            self.channels.append(self.blueChannel)
        elif self.countBlue:
            blueTab = QWidget()
            tabs.addTab(blueTab, "Blue")
            self.blueChannel = DetectionChannel(blueTab, 'b', name="Blue")
            self.channels.append(self.blueChannel)
        #layer tab 
        if self.addLayersTab or self.artificalLayerChannel!="None":
            layersTab = QWidget()
            tabs.addTab(layersTab, "Layers")
            self.layersChannel = LayerChannel(layersTab, 'w', name = "Layers")
            self.channels.append(self.layersChannel)
        # colocalization tab
        colocTab = QWidget()
        tabs.addTab(colocTab, "Colocalization")
        if self.addLayersBlue or self.addBlueChannel == False:
            self.resultChannel = ResultsChannel(colocTab, 'y', [self.redChannel, self.greenChannel], name="Coloc")
        else:
             self.resultChannel = ResultsChannel(colocTab, 'y', [self.redChannel, self.greenChannel, self.blueChannel], name="Coloc")           
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
        brushsize_slider.setMaximum(20)
        brushsize_slider.setTickInterval(1)
        brushsize_slider.setSliderPosition(self.brushsize)
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
        min_slider.setMaximum(100)
        min_slider.setTickInterval(1)
        min_slider.setSliderPosition(10)
        detectionLayout.addWidget(min_slider)
        #maximum slider
        self.max_label = QLabel("Maximum Cell Size: {}".format(self.maxSize))
        detectionLayout.addWidget(self.max_label)
        max_slider = QSlider(Qt.Horizontal)
        max_slider.setMinimum(100)
        max_slider.setMaximum(1000)
        max_slider.setTickInterval(20)
        max_slider.setSliderPosition(200)
        detectionLayout.addWidget(max_slider)
        #template size
        self.tempsize_label = QLabel("Template Size: {}".format(self.tempsize))
        detectionLayout.addWidget(self.tempsize_label)
        tempsize_slider = QSlider(Qt.Horizontal)
        tempsize_slider.setMinimum(1)
        tempsize_slider.setMaximum(100)
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
        if self.addLayersTab:
            browse_button_dapi.pressed.connect(self.browse_button_dapi_callback)
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
        
       # self.setWindowTitle("Cell Counter 2000")
       # self.setGeometry(100,100,1280,960)
       # self.show()
        a,b = hlayout_bottom.sizes()
        hlayout_bottom.setSizes([.8*(a+b), .2*(a+b)])
        
                
    def openDetectionPage(self):
        self.stacked_pages.setCurrentWidget(self.detection_page)
    
    def display(self, i):
        self.stacked_pages.setCurrentIndex(i)
        