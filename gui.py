# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 17:09:21 2018

@author: Greg
"""

# The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# License: http://creativecommons.org/licenses/by-sa/3.0/	

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import filedialog
import numpy as np
import CellCounting as cc

class CellCounter(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Cell Counter")
        
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand = True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.run_button = tk.Button(self.container, text="Run", command=self.run)
        self.run_button.pack()

        self.fig = Figure(figsize=(5,5), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, self.container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, self.container)
        toolbar.update()
        
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
    def run(self):
        
        imageFile = filedialog.askopenfilename(title="Select Image File",
                                               filetypes = (("tif files","*.tif"),("all files","*.*")))
        if not imageFile:
            return
        
        greenImg, redImg, greenCells, redCells = cc.findCells(imageFile)
        
        self.ax.imshow(greenImg)
        self.ax.imshow(greenCells, alpha=.1)
        self.ax.set_position([.05,.05,.9,.9])
        self.canvas.draw()
        
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        
        
    def onclick(self, event):
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))
        
        
        

        

app = CellCounter()
app.mainloop()