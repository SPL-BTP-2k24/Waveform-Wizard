import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

class DraggableBox:
    def __init__(self, line1, line2):
        self.__line1 = line1
        self.__line2 = line2
        self.__dragging = False
        self.__start_x = 0
        self.__start_pos = None

    def on_press(self, event):
        if event.inaxes == self.__line1.axes:
            x1 = self.__line1.get_xdata()[0]
            x2 = self.__line2.get_xdata()[1]
            x = event.xdata
            if x1 <= x <= x2:
                self.__dragging = True
                self.__start_x = event.xdata
                self.__start_pos = (self.__line1.get_xdata()[0], self.__line2.get_xdata()[0])

    def on_release(self, event):
        self.__dragging = False

    def on_motion(self, event):
        if self.__dragging:
            xdata = event.xdata
            if xdata is not None:
                delta_x = xdata - self.__start_x
                new_x_start = self.__start_pos[0] + delta_x
                new_x_end = self.__start_pos[1] + delta_x

                self.__line1.set_xdata([new_x_start, new_x_start])
                self.__line2.set_xdata([new_x_end, new_x_end])
                
                self.__line1.figure.canvas.draw()
