# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 11:33:45 2018

@author: gqs0108
"""

from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import tkinter as tk
import numpy as np

class ToolTip(object):
    """
    Tooltip recipe from
    http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml#e387
    """
    @staticmethod
    def createToolTip(widget, text):
        toolTip = ToolTip(widget)
        def enter(event):
            toolTip.showtip(text)
        def leave(event):
            toolTip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + self.widget.winfo_rooty()
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except tk.TclError:
            pass
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
            
class CustomToolbar(NavigationToolbar2Tk):
    
    toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Back', 'Back to  previous view', 'back', 'back'),
        ('Forward', 'Forward to next view', 'forward', 'forward'),
        (None, None, None, None),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        (None, None, None, None),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
        (None, None, None, None),
        ('Paint', 'Label cell pixels', "C:/Users/gqs0108/Desktop/cell-counting-master/cell", 'paint_tool'),
        ('Erase', 'Erase cell pixels', "C:/Users/gqs0108/Desktop/cell-counting-master/nocell", 'erase_tool')
      )
    
    def __init__(self, canvas, window, gui):
        self.gui = gui
        NavigationToolbar2Tk.__init__(self, canvas, window)
    
    def _init_toolbar(self):
        xmin, xmax = self.canvas.figure.bbox.intervalx
        height, width = 50, xmax-xmin
        tk.Frame.__init__(self, master=self.window,
                          width=int(width), height=int(height),
                          borderwidth=2)

        self.update()  # Make axes menu

        for text, tooltip_text, image_file, callback in self.toolitems:
            if text is None:
                # Add a spacer; return value is unused.
                self._Spacer()
            else:
                if text == 'Paint' or text == 'Erase':
                    button = self._Button(text=text, file=image_file,
                                          command=getattr(self, callback),
                                          extension='.png')
                else:
                    button = self._Button(text=text, file=image_file,
                                          command=getattr(self, callback))
                if tooltip_text is not None:
                    ToolTip.createToolTip(button, tooltip_text)

        self.message = tk.StringVar(master=self)
        self._message_label = tk.Label(master=self, textvariable=self.message)
        self._message_label.pack(side=tk.RIGHT)
        self.pack(side=tk.BOTTOM, fill=tk.X)
        
    def paint_tool(self, *args):
        """Activate paint mode."""
        if self._active == 'PAINT':
            self._active = None
            self._idPress = self.canvas.mpl_disconnect(self._idPress)
        else:
            self._active = 'PAINT'

        if self._idPress is not None:
            self._idPress = self.canvas.mpl_disconnect(self._idPress)
            self.mode = ''

        if self._idRelease is not None:
            self._idRelease = self.canvas.mpl_disconnect(self._idRelease)
            self.mode = ''

        if self._active:
            self._idPress = self.canvas.mpl_connect('button_press_event',
                                                    self.press_paint)
            self._idRelease = self.canvas.mpl_connect('button_release_event', 
                                                      self.release_paint)
            self.mode = 'label cells'
            self.canvas.widgetlock(self)
        else:
            self.canvas.widgetlock.release(self)

        for a in self.canvas.figure.get_axes():
            a.set_navigate_mode(self._active)

        self.set_message(self.mode)
        
        
    def press_paint(self, event):
        """Callback for mouse button press in zoom to rect mode."""

        if event.button == 1:
            self._button_pressed = 1
        elif event.button == 3:
            self._button_pressed = 3
        else:
            self._button_pressed = None
            return

        if event.xdata is not None and event.ydata is not None:
            self._xypress = set()
            x, y = int(np.round(event.xdata)), int(np.round(event.ydata))
            self._xypress.add((x,y))
            self.canvas.mpl_disconnect(self._idDrag)
            self._idDrag = self.canvas.mpl_connect('motion_notify_event',
                                                   self.drag_paint)
            
    def drag_paint(self, event):
        """Callback for dragging in paint mode."""
        if event.xdata is not None and event.ydata is not None:
            x, y = int(np.round(event.xdata)), int(np.round(event.ydata))
            self._xypress.add((x,y))
        if (len(self._xypress) % 20) == 0:
            if self._button_pressed == 1:
                for x,y in self._xypress:
                    self.gui.greenCells[y,x] = 1
            elif self._button_pressed == 3:
                for x,y in self._xypress:
                    self.gui.greenCells[y,x] = 0
            self.gui.cellImShow.set_array(self.gui.greenCells)
            self._xypress = set()
            self.canvas.draw()
            
    def release_paint(self, event):
        """Callback for mouse button release in paint mode."""

        if self._button_pressed is None:
            return
        self.canvas.mpl_disconnect(self._idDrag)
        self._idDrag = self.canvas.mpl_connect(
            'motion_notify_event', self.mouse_move)
        if not self._xypress:
            return
        if self._button_pressed == 1:
            for x,y in self._xypress:
                self.gui.greenCells[y,x] = 1
        elif self._button_pressed == 3:
            for x,y in self._xypress:
                self.gui.greenCells[y,x] = 0
        self.gui.cellImShow.set_array(self.gui.greenCells)
            
        self._xypress = []
        self._button_pressed = None
        self.push_current()
        self.release(event)
        self.draw()
    
    def erase_tool(self):
        return