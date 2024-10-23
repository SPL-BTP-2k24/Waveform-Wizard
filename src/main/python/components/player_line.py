class PlayerLine():
    def __init__(self, ax, start_x):
        self.ax = ax

        self.line = self.ax.axvline(x=start_x, color="blue", linestyle="-")

    def set_x(self, x_new):
        self.line.set_xdata([x_new, x_new])

        self.line.figure.canvas.draw()
