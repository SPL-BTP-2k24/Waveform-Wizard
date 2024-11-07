import numpy as np

from panes.base import Pane_Base

class Pane_Waveform(Pane_Base):
    def __init__(self, *args):
        super().__init__(*args)
        self._pane_name = 'Waveform'

    def _generate_plot(self):
        time = len(self._data)/self._fs
        x = np.linspace(0, time, len(self._data))
        self._ax.plot(x, self._data)
        self._ax.set_ylim(-1, 1)