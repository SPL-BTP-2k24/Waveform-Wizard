from matplotlib.patches import Polygon

class DraggableBox:
    def __init__(self, ax, update_callback, max_x):
        self.__ax = ax
        self.__update_callback = update_callback
        self.__max_x = max_x

        self.__line1 = self.__ax.axvline(x=0, color="red", linestyle="-")
        self.__line2 = self.__ax.axvline(x=max_x, color="red", linestyle="-")
        self.__red_bg = Polygon([(0, self.__ax.get_ylim()[0]), (0, self.__ax.get_ylim()[1]), 
                               (max_x, self.__ax.get_ylim()[1]), (max_x, self.__ax.get_ylim()[0])], 
                              closed=True, color='red', alpha=0.3)
        self.__ax.add_patch(self.__red_bg)

        self.__dragging = False
        self.__start_x = 0
        self.__start_pos = None

    def on_press(self, event):
        if event.inaxes == self.__line1.axes:
            x1 = self.__line1.get_xdata()[0]
            x2 = self.__line2.get_xdata()[0]
            x = event.xdata
            if x1 <= x <= x2:
                self.__dragging = True
                self.__start_x = event.xdata
                self.__start_pos = (self.__line1.get_xdata()[0], self.__line2.get_xdata()[0])

    def on_release(self, event):
        self.__dragging = False
        self.__update_callback(self.__line1.get_xdata()[0], self.__line2.get_xdata()[0])

    def on_motion(self, event):
        if self.__dragging:
            xdata = event.xdata
            if xdata is not None:
                delta_x = xdata - self.__start_x
                new_x_start = self.__start_pos[0] + delta_x
                new_x_start = max(0, new_x_start)
                new_x_end = self.__start_pos[1] + delta_x
                new_x_end = min(self.__max_x, new_x_end)

                self.__line1.set_xdata([new_x_start, new_x_start])
                self.__line2.set_xdata([new_x_end, new_x_end])
                
                self.__red_bg.set_xy([(new_x_start, self.__ax.get_ylim()[0]),
                                    (new_x_start, self.__ax.get_ylim()[1]),
                                    (new_x_end, self.__ax.get_ylim()[1]),
                                    (new_x_end, self.__ax.get_ylim()[0])])
                
                self.__line1.figure.canvas.draw()

                self.__line1.figure.canvas.draw()

    def set_x_lims(self, x_left, x_right):
        self.__line1.set_xdata([x_left, x_left])
        self.__line2.set_xdata([x_right, x_right])

        self.__red_bg.set_xy([(x_left, self.__ax.get_ylim()[0]),
                            (x_left, self.__ax.get_ylim()[1]),
                            (x_right, self.__ax.get_ylim()[1]),
                            (x_right, self.__ax.get_ylim()[0])])

    def get_x_lims(self):
        return self.__line1.get_xdata()[0], self.__line2.get_xdata()[0]
