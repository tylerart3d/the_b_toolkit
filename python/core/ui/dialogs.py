"""A starter template for a dialog window and a dockable dialog window in Maya.

This can be used as either a starter template, subclassed, or called.


"""

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *


class UI(QDialog):
    """A python dialog window for Maya

    """

    def __init__(self, name='UI'):
        super(UI, self).__init__()

        # Set window title, upper right icons

        # Run main create function
        self.create_ui()

    def create_ui(self):
        """Method intended to be overwritten when subclassed"""
        pass

