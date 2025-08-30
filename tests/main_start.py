from PyQt5 import QtCore, QtGui, QtWidgets
from UI.ui_frmStartUp import Ui_frmStartup
import sys
import subprocess
import os
# from .icons import sysIcons


class frmStartup(Ui_frmStartup, QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(frmStartup, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.setWindowFlags(QtCore.Qt.WindowMaximizeButtonHint |
                            QtCore.Qt.FramelessWindowHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

    def loadImg(self, pixmap=None):
        if(pixmap is not None):
            try:
                self.label.setPixmap(pixmap)
            except Exception as e:
                pass
        pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    frm_startup = frmStartup(None)


    frm_startup.show()
    mytimer = QtCore.QTimer()
    mytimer.timeout.connect(close)
    mytimer.start(15000)
    sys.exit(app.exec_())


def close():
    app = QtWidgets.QApplication.instance()
    sys.exit(app.exec_())


def run_exe(projectFile: str = ""):
    try:
        pid = os.getpid()
        args = ["mkl_mc2.dll", f"{pid}", projectFile]
        # print(args)
        myPopenObj = subprocess.Popen(args)
        print("start success.")
        # QtWidgets.QMessageBox.about(None, "run", projectFile)
    except Exception as e:
        QtWidgets.QMessageBox.about(None, "exception", str(e))
        print(e)
