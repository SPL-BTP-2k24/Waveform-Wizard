from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from functools import wraps

def loading_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the main window or relevant widget
        app = QApplication.instance()

        # Set loading cursor
        app.setOverrideCursor(Qt.WaitCursor)

        try:
            # Execute the blocking function
            result = func(*args, **kwargs)
        finally:
            # Restore normal cursor and re-enable the window
            app.restoreOverrideCursor()

        return result
    return wrapper
