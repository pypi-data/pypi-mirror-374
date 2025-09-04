# Default imports
import sys
import warnings
import traceback
from itertools import chain
from pathlib import Path
from importlib import resources
import os

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QPushButton, QLabel, QLineEdit, QCheckBox, QGroupBox, QFileDialog,
    QGridLayout
)
from PyQt6.QtCore import QThread, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtGui import QPalette, QColor

# Import the necessary functions from the package
from numbers_and_brightness.analysis import numbers_and_brightness_analysis, numbers_and_brightness_batch
from numbers_and_brightness._gui_components._utils import wrap_text, show_error_message, show_finished_popup, gui_logger
from numbers_and_brightness import __version__
from numbers_and_brightness._defaults import (
    DEFAULT_BACKGROUND,
    DEFAULT_SEGMENT,
    DEFAULT_DIAMETER,
    DEFAULT_FLOW_THRESHOLD,
    DEFAULT_CELLPROB_THRESHOLD,
    DEFAULT_ANALYSIS,
    DEFAULT_ERODE,
    DEFAULT_BLEACH_CORR
)

import numbers_and_brightness

# Import GUI components
from numbers_and_brightness._gui_components._brightness_intensity import brightness_intensity_window

class Worker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(Exception)
    
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
            self.finished.emit()
        except Exception as e:
            traceback.print_exc()
            self.error.emit(e)

class NumbersAndBrightnessApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize instance variables
        self.file = ""
        self.folder = ""

        self.b_i_windows = []

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(f"Numbers and Brightness Analysis - Version {__version__}")

        # Main widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QGridLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # File and folder selection buttons
        self.file_select_button = QPushButton("Select file")
        self.file_select_button.clicked.connect(self.get_file)
        main_layout.addWidget(self.file_select_button, 0, 0, 1, 2)

        self.folder_select_button = QPushButton("Select folder")
        self.folder_select_button.clicked.connect(self.get_folder)
        main_layout.addWidget(self.folder_select_button, 1, 0, 1, 2)

        # Background input
        bg_label = QLabel("Background:")
        self.background_input = QLineEdit()
        self.background_input.setText(str(DEFAULT_BACKGROUND))
        main_layout.addWidget(bg_label, 2, 0)
        main_layout.addWidget(self.background_input, 2, 1)

        # Segment checkbox
        segment_label = QLabel("Segment:")
        self.segment_input = QCheckBox()
        self.segment_input.setChecked(DEFAULT_SEGMENT)
        main_layout.addWidget(segment_label, 3, 0)
        main_layout.addWidget(self.segment_input, 3, 1)

        # Cellpose settings group
        cellpose_group = QGroupBox("Cellpose settings:")
        cellpose_layout = QGridLayout(cellpose_group)

        # Diameter input
        diameter_label = QLabel("Diameter:")
        self.diameter_input = QLineEdit()
        self.diameter_input.setText(str(DEFAULT_DIAMETER))
        cellpose_layout.addWidget(diameter_label, 0, 0)
        cellpose_layout.addWidget(self.diameter_input, 0, 1)

        # Flow threshold input
        flow_label = QLabel("Flow threshold:")
        self.flow_input = QLineEdit()
        self.flow_input.setText(str(DEFAULT_FLOW_THRESHOLD))
        cellpose_layout.addWidget(flow_label, 1, 0)
        cellpose_layout.addWidget(self.flow_input, 1, 1)

        # Cellprob threshold input
        cellprob_label = QLabel("Cellprob threshold:")
        self.cellprob_input = QLineEdit()
        self.cellprob_input.setText(str(DEFAULT_CELLPROB_THRESHOLD))
        cellpose_layout.addWidget(cellprob_label, 2, 0)
        cellpose_layout.addWidget(self.cellprob_input, 2, 1)

        main_layout.addWidget(cellpose_group, 4, 0, 1, 2)

        # Analysis checkbox
        analysis_label = QLabel("Analysis:")
        self.analysis_input = QCheckBox()
        self.analysis_input.setChecked(DEFAULT_ANALYSIS)
        main_layout.addWidget(analysis_label, 5, 0)
        main_layout.addWidget(self.analysis_input, 5, 1)

        # Erode input
        erode_label = QLabel("Erode:")
        self.erode_input = QLineEdit()
        self.erode_input.setText(str(DEFAULT_ERODE))
        main_layout.addWidget(erode_label, 6, 0)
        main_layout.addWidget(self.erode_input, 6, 1)

        # Bleach correction checkbox
        bleach_corr_label = QLabel("Bleach correction:")
        self.bleach_corr_input = QCheckBox()
        self.bleach_corr_input.setChecked(DEFAULT_BLEACH_CORR)
        main_layout.addWidget(bleach_corr_label, 7, 0)
        main_layout.addWidget(self.bleach_corr_input, 7, 1)

        # Process buttons
        self.process_file_button = QPushButton("Process file")
        self.process_file_button.clicked.connect(self.process_file)
        main_layout.addWidget(self.process_file_button, 8, 0, 1, 2)

        self.process_folder_button = QPushButton("Process folder")
        self.process_folder_button.clicked.connect(self.process_folder)
        main_layout.addWidget(self.process_folder_button, 9, 0, 1, 2)

        # Store buttons for enabling/disabling
        self.select_buttons = [self.file_select_button, self.folder_select_button]
        self.process_buttons = [self.process_file_button, self.process_folder_button]

        self.create_menu()

    @pyqtSlot()
    def create_menu(self):
        # Create the menu bar
        menu_bar = self.menuBar()

        # Add a "File" menu
        file_menu = menu_bar.addMenu("Tools")

        # Create actions for the "File" menu
        new_action = QAction("Brightness - Intensity", self)
        new_action.triggered.connect(self.open_b_i)

        # Add actions to the "File" menu
        file_menu.addAction(new_action)

    @pyqtSlot()
    def open_b_i(self):
        self.b_i_window = brightness_intensity_window()
        self.b_i_window.show()
        self.b_i_windows.append(self.b_i_window)

    @pyqtSlot()
    def get_file(self):
        """Open file dialog to select a file"""
        filename, _ = QFileDialog.getOpenFileName(self, "Select File")
        if filename:
            self.file = filename
            self.file_select_button.setText(wrap_text(filename, 50))

    @pyqtSlot()
    def get_folder(self):
        """Open file dialog to select a folder"""
        foldername = QFileDialog.getExistingDirectory(self, "Select Folder")
        if foldername:
            self.folder = foldername
            self.folder_select_button.setText(wrap_text(foldername, 50))

    def _set_buttons_enabled(self, enabled: bool):
        """Helper method to enable/disable all buttons"""
        for button in chain(self.select_buttons, self.process_buttons):
            button.setEnabled(enabled)

    """File analysis functions"""
    def process_file_call(self):
        numbers_and_brightness_analysis(
            file=self.file,
            background=float(self.background_input.text()),
            segment=self.segment_input.isChecked(),
            diameter=int(self.diameter_input.text()),
            flow_threshold=float(self.flow_input.text()),
            cellprob_threshold=float(self.cellprob_input.text()),
            analysis=self.analysis_input.isChecked(),
            erode=int(self.erode_input.text()),
            bleach_corr=self.bleach_corr_input.isChecked()
        )
        print(f"Processed: {self.file}")

    def process_file_finished(self):
        show_finished_popup(parent=self, title="Finished", message=f"Finished analysis of: {self.file}")
        self._set_buttons_enabled(True)

    def process_file_error(self, error):
        show_error_message(parent=self, message=str(error))
        self._set_buttons_enabled(True)

    @pyqtSlot()
    def process_file(self):
        """Process a single file"""
        if not self.file:
            print("Select a file")
            return
            
        self._set_buttons_enabled(False)
        self.worker = Worker(fn=self.process_file_call)

        self.worker.finished.connect(self.process_file_finished)
        self.worker.error.connect(self.process_file_error)

        self.worker.start()

    """Folder analysis functions"""
    def process_folder_call(self):
        numbers_and_brightness_batch(
            folder=self.folder,
            background=float(self.background_input.text()),
            segment=self.segment_input.isChecked(),
            diameter=int(self.diameter_input.text()),
            flow_threshold=float(self.flow_input.text()),
            cellprob_threshold=float(self.cellprob_input.text()),
            analysis=self.analysis_input.isChecked(),
            erode=int(self.erode_input.text()),
            bleach_corr=self.bleach_corr_input.isChecked()
        )
        print(f"Processed: {self.folder}")

    def process_folder_finished(self):
        show_finished_popup(parent=self, title="Finished", message=f"Finished analysis of: {self.folder}")
        self._set_buttons_enabled(True)

    def process_folder_error(self, error):
        show_error_message(parent=self, message=str(error))
        self._set_buttons_enabled(True)

    @pyqtSlot()
    def process_folder(self):
        """Process a folder"""
        if not self.folder:
            print("Select a folder")
            return
            
        self._set_buttons_enabled(False)
        self.worker = Worker(fn=self.process_folder_call)

        self.worker.finished.connect(self.process_folder_finished)
        self.worker.error.connect(self.process_folder_error)

        self.worker.start()

@gui_logger()
def nb_gui():
    """Initialize and run the GUI application"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)    # Catches matplotlib plt gui warnings
        app = QApplication(sys.argv)

        app.setStyle('Fusion')

        # Set up dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))

        # Apply the palette
        app.setPalette(dark_palette)

        icon_path = os.path.join(resources.files(numbers_and_brightness), "_gui_components", "nb_icon.png")
        app.setWindowIcon(QIcon(str(icon_path)))
        window = NumbersAndBrightnessApp()
        window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    nb_gui()