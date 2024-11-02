import os
import sys
import threading
from datetime import datetime
from time import sleep
from typing import List

import matplotlib.pyplot as plt
import matplotlib.axes as mtAxes
import numpy as np
import soundfile as sf
import pickle

from dependencies.resample.main import resample

from panes.factory import Pane_Factory
from panes.base import Pane_Base

from components.draggable_box import DraggableBox
from components.loading_decorator import loading_decorator
from utils import show_message, get_file_extension,\
                    has_second_channel, process_audio
from print_window import PrintWindow

from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from ppg_runtime.application_context.PyQt5 import (ApplicationContext,
                                                   PPGLifeCycle)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QAction, QFileDialog,
                             QGroupBox, QHBoxLayout, QLabel, QMainWindow,
                             QMessageBox,
                             QToolButton, QVBoxLayout, QWidget,
                             QDialog)

from version import meta_info

class AboutInfoWindow(PPGLifeCycle,QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About This App")

        # Create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)  # Align content to the top

        # Version number
        version_label = QLabel(f"<b>Version:</b> {meta_info['version']}")
        version_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(version_label)

        # GitHub repository link
        repo_label = QLabel('<a href="https://github.com/Abhinavreddy-B/Waveform-Wizard-2">GitHub Repository</a>')
        repo_label.setOpenExternalLinks(True)
        repo_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(repo_label)

        layout.addSpacing(25)  # Add spacing after the repo link

        # "About Us" section header
        about_header = QLabel("<b>About Us</b>")
        about_header.setAlignment(Qt.AlignLeft)
        layout.addWidget(about_header)
        
        layout.addSpacing(15)  # Add spacing before logos
        
        # Logos
        logo_path = self.get_resource('images/logo.png')  # Adjust the path based on where you placed the image
        logo1 = QLabel()

        pixmap1 = QPixmap(logo_path)  # Update with actual path
        logo1.setPixmap(pixmap1)
        logo1.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo1)

        layout.addSpacing(15)  # Add spacing before logos
        
        # SPCRC description
        description_label = QLabel(
            "Signal Processing and Communication Research Center (SPCRC) is one of the highly active research centers at IIIT-H focusing on the various areas of communications and signal processing. "
            "The center provides an umbrella environment for faculty, undergraduate, and postgraduate students to carry out research in various aspects related to the respective fields."
        )
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignLeft)
        description_label.setStyleSheet("QLabel { line-height: 3; }")  # Set line height for description
        layout.addWidget(description_label)
        

        layout.addSpacing(25)  # Add spacing after the logo

        # Contact details header
        contact_header = QLabel("<b>Contact Details</b>")
        contact_header.setAlignment(Qt.AlignLeft)
        layout.addWidget(contact_header)

        # Contact information as link
        contact_link = QLabel('<a href="http://spcrc.iiit.ac.in">http://spcrc.iiit.ac.in</a>')
        contact_link.setOpenExternalLinks(True)  # Make the link clickable
        contact_link.setAlignment(Qt.AlignLeft)
        layout.addWidget(contact_link)

        layout.addSpacing(5)  # Add spacing between link and text

        # Other contact details formatted as an address
        contact_info = QLabel(
            "Signal Processing and Communication Research Centre (SPCRC)<br>"
            "IIIT Hyderabad<br>"
            "Gachibowli<br>"
            "Hyderabad, India - 500032"
        )

        contact_info.setAlignment(Qt.AlignLeft)
        contact_info.setWordWrap(True)  # Ensure text wraps properly
        contact_info.setStyleSheet("QLabel { line-height: 3; }")  # Set line height for contact info
        layout.addWidget(contact_info)

        
        # layout.addSpacing(15)  # Add spacing before the trademark
        layout.addStretch()  # Add stretchable space to push footer down


        # Footer (trademark/ownership mark)
        trademark_label = QLabel("© Signal Processing and Communication Research Center (SPCRC). All rights reserved.")
        trademark_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(trademark_label)


        # Set layout for the dialog
        self.setLayout(layout)

        # Set the size similar to the main window
        self.setGeometry(100, 100, 800, 600)  # Adjust dimensions as needed
        self.setWindowFlags(Qt.Window)  # Keep standard window decorations

class AudioComponent(QGroupBox):
    def __init__(self, file_name, delete_pane_callback):
        super().__init__(file_name)
        self.initUI()
        self.file_name = file_name
        self.data = None
        self.fs = None
        self.resampled_data = None
        self.resampled_fs = None

        self.delete_pane_parent_callback = delete_pane_callback

    def initUI(self):
        self.layout_area = QVBoxLayout()
        self.setLayout(self.layout_area)
    
    def add_waveform_plot_area(self):
        self.plot_waveform = plt.figure(facecolor='none')
        self.ax_waveform = self.plot_waveform.add_subplot(111, facecolor='none')
        self.ax_waveform.set_facecolor('None')
        self.plot_waveform.tight_layout()
        self.canvas_waveform = FigureCanvas(self.plot_waveform)
        self.canvas_waveform.setStyleSheet("background: transparent;")

        self.draggable_box = DraggableBox(self.ax_waveform, self.__update_plot_x_lims, self._time)
        self.canvas_waveform.mpl_connect('button_press_event', self.draggable_box.on_press)
        self.canvas_waveform.mpl_connect('button_release_event', self.draggable_box.on_release)
        self.canvas_waveform.mpl_connect('motion_notify_event', self.draggable_box.on_motion)

        self.action_button_layout_waveform = QHBoxLayout()
        self.zoom_in_action = QAction('Zoom  +')
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.tool_button_zoom_in = QToolButton(self)
        self.tool_button_zoom_in.setDefaultAction(self.zoom_in_action)
        self.zoom_out_action = QAction('Zoom -')
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.tool_button_zoom_out = QToolButton(self)
        self.tool_button_zoom_out.setDefaultAction(self.zoom_out_action)
        self.action_button_layout_waveform.addWidget(self.tool_button_zoom_in)
        self.action_button_layout_waveform.addWidget(self.tool_button_zoom_out)
        self.action_button_layout_waveform.addStretch()
        
        self.layout_area.addLayout(self.action_button_layout_waveform)
        self.layout_area.addWidget(self.canvas_waveform)

    def update_plot(self):
        # self.set_loading_screen_in_plot()
        # self.ax_waveform.clear()
        time = len(self.data)/self.fs

        x = np.linspace(0, time, len(self.data))
        self.ax_waveform.plot(x, self.data)
        self.canvas_waveform.draw()

    @loading_decorator
    def set_data(self, data, fs, *args, **kwargs):
        self.data = data
        self.fs = fs

        self.resampled_data = resample(self.data, 4000, self.fs)
        self.resampled_fs = 4000
        
        self._time = len(self.data)/self.fs
        
        self.add_waveform_plot_area()
        self.update_plot()


    def _add_pane(self, pane_name):
        pane_class = Pane_Factory.get_pane_class_by_name(pane_name)
        x_left, x_right = self.draggable_box.get_x_lims()
        pane = pane_class(self.data, self.fs, self.resampled_data, self.resampled_fs, self._delete_pane_callback, x_left, x_right)
        self.layout_area.addWidget(pane)

    def _delete_pane_callback(self, widget_object: QWidget):
        pane_list = self._get_pane_list()
        target_index = pane_list.index(widget_object)
        self.delete_pane_parent_callback(target_index)

    def _delete_pane(self, pane_index: int, *args, **kwargs):
        pane_list = self._get_pane_list()
        
        widget_object = pane_list[pane_index]

        self.layout_area.removeWidget(widget_object)
        self.layout_area.update()
        widget_object.deleteLater()

    def _get_pane_list(self) -> List[Pane_Base]:
        widget_list = []
        for i in range(self.layout_area.count()):
            widget = self.layout_area.itemAt(i).widget()
            if isinstance(widget, Pane_Base):
                widget_list.append(widget)
        return widget_list
    
    def get_pane_name_list(self) -> List[str]:
        pane_widgets = self._get_pane_list()
        pane_name_list = []
        for pane in pane_widgets:
            pane_name = pane.get_pane_name()
            pane_name_list.append(pane_name)
        return pane_name_list

    @loading_decorator
    def __update_plot_x_lims(self, x_left, x_right, *args, **kwargs):
        panes = self._get_pane_list()
        for pane in panes:
            pane.update_graph_x_lims(x_left, x_right)

    @loading_decorator
    def zoom_in(self, *args, **kwargs):
        xlim = self.draggable_box.get_x_lims()
        center = (xlim[0] + xlim[1])/2

        x_left = center - (center - xlim[0]) * 0.9
        x_right = center + (xlim[1] - center) * 0.9
        self.draggable_box.set_x_lims(x_left, x_right)
        self.canvas_waveform.draw()

        self.__update_plot_x_lims(x_left, x_right)

    @loading_decorator
    def zoom_out(self, *args, **kwargs):
        xlim = self.draggable_box.get_x_lims()
        center = (xlim[0] + xlim[1])/2

        x_left = center - (center - xlim[0]) * 1.1
        x_left = max(0, x_left)
        x_right = center + (xlim[1] - center) * 1.1
        x_right = min(self._time, x_right)

        self.draggable_box.set_x_lims(x_left, x_right)
        self.canvas_waveform.draw()

        self.__update_plot_x_lims(x_left, x_right)

    def export(self) -> List[mtAxes.Axes]:
        axes = []

        panes = self._get_pane_list()
        for pane in panes:
            axes.append(pane._ax)
        
        return axes

class MainWindow(PPGLifeCycle,QMainWindow):
    def __init__(self, args):
        super().__init__()
        self.initUI()
        
        if(len(args) > 0):
            self.__load_file_from_args(args[0])

    def initUI(self):
        self.createFileMenu()
        self.createPaneMenu()
        self.createMoreMenu()

        central_widget = QWidget(self)
        self.main_layout = QVBoxLayout(central_widget)

        self.audio_layouts = QHBoxLayout()

        self.main_layout.addLayout(self.audio_layouts, 9)

        footer_layout = QHBoxLayout()
        footer_layout.setAlignment(Qt.AlignCenter)

        trademark_label = QLabel("© Speech Processing Lab (SPL), IIITH. All rights reserved.")
        trademark_label.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(trademark_label)

        logo1 = QLabel()
        logo1_path=self.get_resource('images/logo1.png')
        pixmap1 = QPixmap(logo1_path)
        scaled_pixmap = pixmap1.scaled(50, 50, Qt.KeepAspectRatio)
        logo1.setPixmap(scaled_pixmap)
        logo1.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(logo1)

        self.main_layout.addLayout(footer_layout)

        self.setCentralWidget(central_widget)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Waveform-Wizard')
        self.showMaximized()

    def createFileMenu(self):
        file_menu = self.menuBar().addMenu('File')

        load_action = QAction('Load File', self)
        load_action.triggered.connect(self.__invoke_file_picker)
        file_menu.addAction(load_action)

        export_action = QAction('Export', self)
        export_action.triggered.connect(self.__invoke_export)
        file_menu.addAction(export_action)

        save_action = QAction('Save File', self)
        save_action.triggered.connect(self.__save_file)
        file_menu.addAction(save_action)
        
        new_window_action = QAction('New Window', self)
        new_window_action.triggered.connect(self.open_new_window)
        file_menu.addAction(new_window_action)
    
    @loading_decorator
    def open_new_window(self, *args, **kwargs):
        """Create and show a new instance of MainWindow."""
        self.new_window = MainWindow(args=[])
        self.new_window.show()

    def createPaneMenu(self):
        pane_menu = self.menuBar().addMenu('Panes')

        add_pane_menu = pane_menu.addMenu("Add Pane")

        graph_pane_names = [
            'Waveform', 'Spectrogram', 'ZTWS', 'Gammatonegram', 
            'SFF', 'Formant Peaks', 'VAD', 'Pitch Contour', 
            'Constant-Q', 'EGG'
        ]

        for pane_name in graph_pane_names:
            add_pane_action = QAction(pane_name, self)

            add_pane_action.triggered.connect(
                lambda checked, p=pane_name: self.__add_pane(p)
            )

            add_pane_menu.addAction(add_pane_action)

    def __get_audio_components(self) -> List[AudioComponent]:
        layout_list = []
        for i in range(self.audio_layouts.count()):
            widget = self.audio_layouts.itemAt(i).widget()
            if isinstance(widget, AudioComponent):
                layout_list.append(widget)
        return layout_list

    def __add_pane(self, pane_name):
        audio_component_list = self.__get_audio_components()

        for audio_component in audio_component_list:
            audio_component._add_pane(pane_name)

    @loading_decorator
    def __delete_pane(self, pane_index):
        audio_component_list = self.__get_audio_components()

        for audio_component in audio_component_list:
            audio_component._delete_pane(pane_index)

    def createMoreMenu(self):
        file_menu = self.menuBar().addMenu('More')

        about_action = QAction('About', self)
        about_action.triggered.connect(self.showAbout)
        file_menu.addAction(about_action)

    @loading_decorator
    def __invoke_export(self, *args, **kwargs):
        audio_component_list = self.__get_audio_components()
        
        axes_list = []
        for audio_component in audio_component_list:
            axes = audio_component.export()
            axes_list.append(axes)

        axes_grid = list(zip(*axes_list))
        axes_grid = [list(axes) for axes in axes_grid]

        self.__print_window = PrintWindow(axes_grid)
        self.__print_window.show()

    def __get_existing_pane_list(self) -> List[str]:
        audio_component_list = self.__get_audio_components()
        if(len(audio_component_list) == 0):
            return []
        else:
            pane_name_list = audio_component_list[0].get_pane_name_list()
            return pane_name_list

    def __load_audio_file(self, file_name, initial_pane_list, *args, **kwargs):
        file_path = file_name
        file_base_name = os.path.basename(file_name)

        data, samplerate = sf.read(file_path)

        first_data = process_audio(data)
        
        new_audio_component = AudioComponent(file_base_name, self.__delete_pane)
        new_audio_component.set_data(first_data, samplerate)
        self.audio_layouts.addWidget(new_audio_component)
        
        for pane in initial_pane_list:
            new_audio_component._add_pane(pane)

    def __load_wwc_file(self, file_name, initial_pane_list, *args, **kwargs):
        with open(file_name, 'rb') as file:
            config = pickle.load(file)

        for audio_component in config:
            if initial_pane_list != [] and audio_component['other_plot_config']['panes'] != initial_pane_list:
                show_message('Panes do not match', msg_type='error')
                return

            new_audio_component = AudioComponent(audio_component['file_name'], self.__delete_pane)
            new_audio_component.set_data(audio_component['data'], audio_component['fs'])
            new_audio_component.x_left = audio_component['plot_config']['x_start']
            new_audio_component.x_right = audio_component['plot_config']['x_end']
            new_audio_component.draggable_box.set_x_lims(new_audio_component.x_left, new_audio_component.x_right)
            new_audio_component.ax_waveform.set_ylim(audio_component['plot_config']['y_start'], audio_component['plot_config']['y_end'])
            for pane in audio_component['other_plot_config']['panes']:
                new_audio_component._add_pane(pane)
            self.audio_layouts.addWidget(new_audio_component)

    @loading_decorator
    def __load_file_from_file_name(self, file_name, *args, **kwargs):
        if(get_file_extension(file_name) not in ['wav', 'wwc']):
            show_message('File Format unsupported', msg_type='error')
            return

        initial_pane_list=self.__get_existing_pane_list()

        if(get_file_extension(file_name) in ['wav']):
            self.__load_audio_file(file_name, initial_pane_list)
        elif(get_file_extension(file_name) in ['wwc']):
            self.__load_wwc_file(file_name, initial_pane_list)

    def __load_file_from_args(self, arg_1):
        cwd = os.getcwd()
        resolved_path = os.path.abspath(os.path.join(cwd, arg_1))
        self.__load_file_from_file_name(resolved_path)
    
    @loading_decorator
    def __save_file(self, *args, **kwargs):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save As", "", "Custom Files (*.wwc);;All Files (*)", options=options)
        if file_path:
            if not file_path.endswith('.wwc'):
                file_path += '.wwc'
        else:
            show_message('No file saved', msg_type='error')
            return

        audio_component_list = self.__get_audio_components()
        if len(audio_component_list) == 0:
            show_message('No file loaded', msg_type='error')
            return

        all_configs = []

        # Iterate over each audio component and generate its config
        for component in audio_component_list:
            x_left, x_right = component.draggable_box.get_x_lims()
            config = {
                'file_name': component.file_name,
                'data': component.data,
                'fs': component.fs,
                'resampled_data': component.resampled_data,
                'resampled_fs': component.resampled_fs,
                'plot_config': {
                    'x_start': x_left,
                    'x_end': x_right,
                    'y_start': component.ax_waveform.get_ylim()[0],
                    'y_end': component.ax_waveform.get_ylim()[1],
                },
                'other_plot_config': {
                    'panes': [pane.get_pane_name() for pane in component._get_pane_list()],
                },
            }
            all_configs.append(config)

        # Dump all configs to the specified file as a pickle
        with open(file_path, 'wb') as f:
            pickle.dump(all_configs, f)
        
        show_message('File saved successfully', msg_type='success')

    def __invoke_file_picker(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Load Single File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            if(get_file_extension(fileName) in ['wav', 'wwc']):
                self.__load_file_from_file_name(fileName)
            else:
                show_message('File Format unsupported', msg_type='error')

    def showAbout(self):
        win = AboutInfoWindow(self)
        win.exec_()

if __name__ == '__main__':
    appctxt = ApplicationContext()
    mainWindow = MainWindow(args=sys.argv[1:])
    mainWindow.show()
    # This fixes the issue with PySide2 that the exec function is not found
    exec_func = getattr(appctxt.app, 'exec', appctxt.app.exec_)
    sys.exit(exec_func())