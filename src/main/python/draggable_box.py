import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

class DraggableBox:
    def __init__(self, line1, line2):
        self.line1 = line1
        self.line2 = line2
        self.dragging = False
        self.start_x = 0
        self.start_pos = None

    def on_press(self, event):
        if event.inaxes == self.line1.axes:
            x1 = self.line1.get_xdata()[0]
            x2 = self.line2.get_xdata()[1]
            x = event.xdata
            if x1 <= x <= x2:
                self.dragging = True
                self.start_x = event.xdata
                self.start_pos = (self.line1.get_xdata()[0], self.line2.get_xdata()[0])

    def on_release(self, event):
        self.dragging = False

    def on_motion(self, event):
        if self.dragging:
            xdata = event.xdata
            if xdata is not None:
                # Calculate new positions
                delta_x = xdata - self.start_x
                new_x_start = self.start_pos[0] + delta_x
                new_x_end = self.start_pos[1] + delta_x

                # Update lines
                self.line1.set_xdata([new_x_start, new_x_start])
                self.line2.set_xdata([new_x_end, new_x_end])
                
                self.line1.figure.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Matplotlib in PyQt5 with Draggable Box")
        
        # Set up the main widget and layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)
        
        # Create Matplotlib figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(NavigationToolbar(self.canvas, self))
        layout.addWidget(self.canvas)
        
        # Define the initial box lines (two vertical lines)
        self.line1, = self.ax.plot([0, 0], [0, 1], 'r-')
        self.line2, = self.ax.plot([1, 1], [0, 1], 'r-')
        
        # Set the initial positions
        self.line1.set_xdata([0, 0])
        self.line2.set_xdata([1, 1])

        # Create a DraggableBox instance
        self.draggable_box = DraggableBox(self.line1, self.line2)

        # Connect Matplotlib events to the draggable box
        self.canvas.mpl_connect('button_press_event', self.draggable_box.on_press)
        self.canvas.mpl_connect('button_release_event', self.draggable_box.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.draggable_box.on_motion)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
