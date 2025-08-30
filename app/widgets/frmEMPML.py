from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import (QToolButton, QMenu, 
                                QAction,QTableWidgetItem,QAbstractItemView,
                                QHeaderView,QItemDelegate
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from UI.ui_frmEMPML import Ui_frmEMPML
from ..icons import sysIcons
from .frmBase import frmBase


class frmEMPML(Ui_frmEMPML,frmBase):
    sigSolidSelected=QtCore.pyqtSignal(int)
  
    def __init__(self,parent=None):
        super(frmEMPML,self).__init__(parent)
        self.setWindowIcon(sysIcons.windowIcon)
        self.setupUi(self)
        self.parent=parent
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
 
        self.btnApply.clicked.connect(self.actionApply)
        self.btnOK.clicked.connect(self.actionOK)
        self.btnCancel.clicked.connect(self.close)

        self.onLoad()  
    def onLoad(self):
        super().onLoad()
        pass
    def actionApply(self):
        try:
            solidId=int(self.txtSolidId.text())-1
            self.sigSolidSelected.emit(solidId)
        except Exception as e:
            print(e)
            QtWidgets.QMessageBox.about(self,"Error","体编号不合法，请重新输入")
        pass
    def actionOK(self):
        try:
            solidId=int(self.txtSolidId.text())-1
            self.sigSolidSelected.emit(solidId)
        except Exception as e:
            QtWidgets.QMessageBox.about(self,"Error","体编号不合法，请重新输入")
        self.close()
        pass
    def sig_chooseSolid(self,solidId:int):
        self.txtSolidId.setText(str(solidId+1))
        pass