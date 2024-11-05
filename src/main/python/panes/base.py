from threading import Thread
import matplotlib.pyplot as plt
from components.loading_decorator import loading_decorator
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QMenu, QAction)
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas

class Pane_Base(QWidget):
    def __init__(self, data, fs, resampled_data, resampled_fs, delete_callback, x_left, x_right):
        super().__init__()

        self._data = data
        self._fs = fs
        self._resampled_data = resampled_data
        self._resampled_fs = resampled_fs
        self._total_time = len(self._data)
        self.__delete_callback = delete_callback
        self.__init_x_left = x_left
        self.__init_x_right = x_right

        self._pane_name = None # to be overwritten in child.

        self.initUI()

    def initUI(self):
        self.__plot = plt.figure(facecolor='none')
        self._ax = self.__plot.add_subplot(111, facecolor='none')
        self._ax.set_facecolor('None')
        self.__plot.tight_layout()
        self._ax.margins(x=0.1, y=0.1)
        self.__canvas = FigureCanvas(self.__plot)
        self.__canvas.setStyleSheet("background: transparent;")

        layout = QVBoxLayout()
        layout.addWidget(self.__canvas)
        self.setLayout(layout)

        thread = Thread(target=self.__generate_plot)
        thread.start()
    
    def contextMenuEvent(self, event):
        '''
        Overwriting default context menu method
        '''
        context_menu = QMenu(self)

        action1 = QAction("Delete", self)
        action1.triggered.connect(self.__delete_pane)

        context_menu.addAction(action1)

        context_menu.exec_(event.globalPos())

    def update_graph_x_lims(self, x_left, x_right):
        self._ax.set_xlim((x_left, x_right))
        self.__canvas.draw()

    def __set_loading_screen_in_plot(self):
        self._ax.clear()
        self.__canvas.draw()

        self._ax.set_axis_off()
        self._ax.text(0.5, 0.5, 'Loading....', horizontalalignment='center', verticalalignment='center', fontsize=12)
        self.__canvas.draw()

        self._ax.clear()
    
    def _generate_plot(self):
        raise NotImplementedError("Subclasses should implement this!")

    @loading_decorator
    def __generate_plot(self):
        self.__set_loading_screen_in_plot()
        self._generate_plot()
        self.update_graph_x_lims(x_left=self.__init_x_left, x_right=self.__init_x_right)
        self.__canvas.draw()

    def __delete_pane(self):
        self.__delete_callback(self)
        
    def get_pane_name(self):
        return self._pane_name