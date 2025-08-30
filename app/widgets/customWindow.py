from PyQt5 import QtWidgets
from ..icons import sysIcons
class CustomWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(sysIcons.windowIcon)