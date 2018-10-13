from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from CellCounterApp import CellCounterApp

if __name__ == '__main__':

    app = QApplication([])
    window = CellCounterApp()
    app.exec_()