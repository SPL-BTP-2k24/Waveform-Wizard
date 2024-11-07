from panes.base import Pane_Base

from panes.waveform import Pane_Waveform
from panes.spectrogram import Pane_Spectrogram
from panes.ztws import Pane_Ztws
from panes.gammatonegram import Pane_Gammatonegram
from panes.sff import Pane_Sff
from panes.formant_peaks import Pane_FormantPeaks
from panes.vad import Pane_Vad
from panes.pitch_contour import Pane_Contour
from panes.constantq import Pane_ConstantQ

class Pane_Factory():
    name_to_pane_map = {
        'Waveform': Pane_Waveform,
        'Spectrogram': Pane_Spectrogram,
        'ZTWS': Pane_Ztws,
        'Gammatonegram': Pane_Gammatonegram,
        'SFF': Pane_Sff,
        'Formant Peaks': Pane_FormantPeaks,
        'VAD': Pane_Vad,
        'Pitch Contour': Pane_Contour,
        'Constant-Q': Pane_ConstantQ,
    }

    def get_pane_class_by_name(name) -> Pane_Base:
        if(name not in Pane_Factory.name_to_pane_map):
            raise ValueError(f'No Pane with the provided name: {name}')
        
        return Pane_Factory.name_to_pane_map[name]