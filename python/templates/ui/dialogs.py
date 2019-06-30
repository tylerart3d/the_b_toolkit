"""A starter template for a dialog window and a dockable dialog window in Maya.

This can be used as either a starter template, subclassed, or called.


"""

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance

# No longer use shiboken
import maya.OpenMayaUI as omui


class UI(QDialog):
    """A python dialog window for Maya

    """

    def __init__(self, name='UI'):
        super(UI, self).__init__(wrapInstance(long(omui.MQtUtil.mainWindow()), QWidget))

        # Set window title, upper right icons
        self.setWindowTitle(name)
        self.setWindowFlags(self.windowFlags() | Qt.WindowSystemMenuHint | Qt.WindowMinMaxButtonsHint)

        # Run main create function
        self.create_ui()
        self.show()

    def create_ui(self):
        """Method intended to be overwritten when subclassed"""
        pass


def main():
    UI()


if __name__ == '__main__':
    main()
