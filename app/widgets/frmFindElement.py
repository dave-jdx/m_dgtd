from PyQt5 import QtCore, QtGui, QtWidgets
from UI.ui_frmFindElement import Ui_frmFindElement
from ..icons import sysIcons
class frmFindElement(Ui_frmFindElement,QtWidgets.QMainWindow):
    sigShowElement=QtCore.pyqtSignal(int)
    sigClearSelected=QtCore.pyqtSignal()
    def __init__(self,parent=None):
        super(frmFindElement,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.parent=parent
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btnClose.clicked.connect(self.close)
        self.txtElementId.textChanged.connect(self.findElement)
        self.onLoad()
    def onLoad(self):
        pass
    def findElement(self):
        try:
            if(self.txtElementId.text().strip()!=""):
                elementId=int(self.txtElementId.text())
                self.sigShowElement.emit(elementId)
            pass
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"查找网格","网格编号必须是整数"+str(e))
        pass
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.sigClearSelected.emit()
        return super().closeEvent(a0)

            