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
    from .icons import sysIcons
    frm_startup = frmStartup(None)
    frm_startup.loadImg(sysIcons.startupPixmap)

    args = app.arguments()
    argString = ":".join(args)
    projectFile = ""
    if(len(args) >= 2):
        projectFile = args[1] #加载工程文件，如果有的话

    # QtWidgets.QMessageBox.about(None, "args", projectFile)
    run_exe(projectFile)
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
        args = ["bin/app.exe", f"{pid}", projectFile]
        # print(args)
        myPopenObj = subprocess.Popen(args)
        print("start success.")
        # QtWidgets.QMessageBox.about(None, "run", projectFile)
    except Exception as e:
        QtWidgets.QMessageBox.about(None, "exception", str(e))
        print(e)
