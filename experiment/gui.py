# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 17:09:21 2018

@author: Greg
"""

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import filedialog
import CellCounting as cc
from CustomToolbar import CustomToolbar
import os.path as path

class CellCounter(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        # Set up overall GUI
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Cell Counter")        
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)
        
        # Set up container frame
        container = tk.Frame(self)
        tk.Grid.columnconfigure(container, 0, weight=100)
        tk.Grid.columnconfigure(container, 1, weight=1)
        tk.Grid.columnconfigure(container, 2, weight=1)
        tk.Grid.rowconfigure(container, 0, weight=1)
        tk.Grid.rowconfigure(container, 1, weight=100)
        tk.Grid.rowconfigure(container, 2, weight=1)
        container.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

        # Set up matplotlib stuff
        self.fig = Figure(figsize=(5,5), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, container)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky=tk.N+tk.S+tk.E+tk.W)
        
        toolbar_frame = tk.Frame(container)
        toolbar_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky=tk.N+tk.S+tk.E+tk.W)
        self.toolbar = CustomToolbar(self.canvas, toolbar_frame, self)
        self.toolbar.pack(side=tk.LEFT)
        self.toolbar.update()
        
        # Set up buttons / entries
        self.fname = tk.StringVar()
        self.fname.set("Image filename")
        self.fname_entry = tk.Entry(container, width=10, textvariable=self.fname, justify='left')
        self.fname_entry.grid(row=0, column=0, padx=10, pady=5, sticky=tk.N+tk.S+tk.E+tk.W)
        
        self.browse_button = tk.Button(container, text="Browse", command=self.selectFile)
        self.browse_button.grid(row=0, column=1, padx=10, pady=5, sticky=tk.N+tk.S+tk.E+tk.W)
        
        self.run_button = tk.Button(container, text="Run", command=self.run)
        self.run_button.grid(row=0, column=2, padx=10, pady=5, sticky=tk.N+tk.S+tk.E+tk.W)
        
        self.paint_button = tk.Button(toolbar_frame, text="Paint", command=self.paint)
        self.paint_button.pack(side=tk.RIGHT)
        
        self.erase_button = tk.Button(toolbar_frame, text="Erase", command=self.erase)
        self.erase_button.pack(side=tk.RIGHT)
        
    def run(self):
        
        imageFile = self.fname.get()
        
        if not path.isfile(imageFile):
            return
        
        self.greenImg, self.redImg, self.greenCells, self.redCells = cc.findCells(imageFile)
        
        self.ax.imshow(self.greenImg)
        self.cellImShow = self.ax.imshow(self.greenCells, alpha=.1)
        self.ax.set_position([.05,.05,.9,.9])
        self.canvas.draw()
        
    def selectFile(self):
        imageFile = filedialog.askopenfilename(title="Select Image File",
                                               filetypes = (("tif files","*.tif"),("all files","*.*")))
        self.fname.set(imageFile)
        
    def paint(self):
        return
    
    def erase(self):
        return
    
app = CellCounter()
app.mainloop()