from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from functools import wraps

class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)  # Capture mouse events
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.5);")  # Semi-transparent background
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

def loading_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the main window or relevant widget
        app = QApplication.instance()
        window = app.activeWindow()  # Assuming the main window is active

        # Set loading cursor
        app.setOverrideCursor(Qt.WaitCursor)

        # Disable the main window to block interactions
        window.setEnabled(False)

        try:
            # Execute the blocking function
            result = func(*args, **kwargs)
        finally:
            # Restore normal cursor and re-enable the window
            app.restoreOverrideCursor()
            window.setEnabled(True)

        return result
    return wrapper